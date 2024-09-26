import json
import os
import requests
import numpy as np
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from scipy.spatial import ConvexHull


# -------------------- 步骤 1：解析 JSON 数据并提取所有 .bin 文件 --------------------

def extract_bin_files(node, bin_files, hierarchy=[]):
    """
    递归地从 JSON 结构中提取所有 .bin 文件的路径。
    同时记录每个文件的层级深度，以便后续绘图时分配颜色。
    """
    file_path = node['file']
    current_hierarchy = hierarchy + [file_path]
    bin_files.append({
        'file': file_path,
        'numSpecimens': node['numSpecimens'],
        'hierarchy': current_hierarchy
    })
    for child in node.get('children', []):
        extract_bin_files(child, bin_files, current_hierarchy)
    return bin_files


# -------------------- 步骤 2：下载所有 .bin 文件 --------------------

def download_bin_files(bin_files, base_url, save_dir):
    """
    下载所有 .bin 文件到指定的文件夹。
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for bin_file in bin_files:
        file_name = bin_file['file']
        file_url = f"{base_url}/{file_name}"
        file_path = os.path.join(save_dir, file_name)

        # 创建子目录结构（如果有）
        sub_dirs = os.path.dirname(file_name)
        if sub_dirs:
            os.makedirs(os.path.join(save_dir, sub_dirs), exist_ok=True)

        # 如果文件已经存在，则跳过下载
        if os.path.exists(file_path):
            print(f"{file_name} 已存在，跳过下载。")
            continue

        # 下载文件
        print(f"下载 {file_name}...")
        try:
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"{file_name} 下载完成。")
        except requests.exceptions.RequestException as e:
            print(f"下载 {file_name} 失败：{e}")


# -------------------- 步骤 3：读取并处理 .bin 文件 --------------------

def read_bin_file(filename):
    """
    读取二进制文件中的 float32 坐标数据。
    假设每个点包含 (x, y) 坐标，即每两个 float32 为一组。
    """
    data = np.fromfile(filename, dtype=np.float32)
    if len(data) % 2 != 0:
        print(f"文件 {filename} 数据长度不是 2 的倍数，去除多余的部分。")
        data = data[:-(len(data) % 2)]
    points = data.reshape(-1, 2)
    return points


# -------------------- 步骤 4：绘制并叠加所有点，添加边框和标签 --------------------

def plot_overlaid_points_with_borders(bin_files, bin_save_dir, plot_save_path, bounding_box):
    """
    在同一个画布上叠加绘制所有指定层级的 .bin 文件的点数据。
    不同的子集使用不同颜色标记，按照层级顺序绘制。
    为每个数据集添加黑色实线边框和文件名标签，确保边框和标签在最上层。
    """
    # 创建 Figure 和 Axes 对象
    fig, ax = plt.subplots(figsize=(12, 10))

    # 设置坐标轴范围
    ax.set_xlim(bounding_box['lx'], bounding_box['ux'])
    ax.set_ylim(bounding_box['ly'], bounding_box['uy'])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Overlayed Scatter Plot with Borders and Labels')

    # 获取最大层级深度
    max_depth = max(len(bin_file['hierarchy']) for bin_file in bin_files)

    # 为每个层级分配一个颜色，使用离散的 colormap
    cmap = plt.get_cmap('viridis', max_depth)

    # 按层级深度从低到高排序，确保低层级先绘制，高层级后绘制
    bin_files_sorted = sorted(bin_files, key=lambda x: len(x['hierarchy']))

    for bin_file in bin_files_sorted:
        file_name = bin_file['file']
        file_path = os.path.join(bin_save_dir, file_name)
        if not os.path.exists(file_path):
            print(f"文件 {file_name} 不存在，跳过绘图。")
            continue
        points = read_bin_file(file_path)

        # 只绘制 (x, y) 坐标
        xy_points = points[:, :2]

        # 计算当前文件的层级深度
        depth = len(bin_file['hierarchy']) - 1  # 根节点为 depth 0

        # 分配颜色
        color = cmap(depth)

        # 绘制散点
        scatter = ax.scatter(xy_points[:, 0], xy_points[:, 1], s=1, c=[color], label=file_name, alpha=0.6)

        # 计算并绘制凸包边界
        if len(xy_points) >= 3:  # ConvexHull 需要至少 3 点
            try:
                hull = ConvexHull(xy_points)
                hull_points = xy_points[hull.vertices]
                # 绘制边界线
                ax.plot(np.append(hull_points[:, 0], hull_points[0, 0]),
                        np.append(hull_points[:, 1], hull_points[0, 1]),
                        'k-', linewidth=1)

                # 计算边界的中心点用于放置标签
                center_x = np.mean(hull_points[:, 0])
                center_y = np.mean(hull_points[:, 1])
                ax.text(center_x, center_y, file_name, fontsize=8, color='black', ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))
            except Exception as e:
                print(f"计算凸包失败 for {file_name}: {e}")
        else:
            print(f"文件 {file_name} 点数不足以计算凸包，跳过边界绘制。")

    # 添加颜色条，表示层级深度
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_depth - 1))
    sm.set_array([])  # 仅用于 colorbar
    cbar = fig.colorbar(sm, ax=ax, ticks=range(0, max_depth, max(1, max_depth // 10)))
    cbar.set_label('Hierarchy Depth')

    # 可选：添加图例（如果 bin 文件较少）
    # 如果 bin 文件数量很多，图例会过于拥挤，建议省略或仅显示部分关键节点
    # ax.legend(markerscale=5, bbox_to_anchor=(1.05, 1), loc='upper left')

    # 保存绘图
    plt.savefig(plot_save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"叠加图像已保存到 {plot_save_path}")


# -------------------- 步骤 5：主流程 --------------------

def main():
    # 设置参数
    json_file = 'ScatterBrain.json'  # JSON 文件路径
    base_url = 'https://prod-sfs.brain.allentech.org/api/v1/Metadata/sb/AP8JNN5LYABGVMGKY1B/Q1NCWWPG6FZ0DNIXJBQ/v0/FS00DXV0T9R1X9FJ4QE/G4I4GFJXJB9ATZ3PTX1'
    bin_save_dir = 'bin_files'
    plot_save_dir = 'plot_images'
    overlaid_plot_path = os.path.join(plot_save_dir, 'overlaid_plot.png')

    # 边界框设置（用于绘图）
    bounding_box = {
        "lx": -13.944271999999998,
        "ly": -14.753810999999999,
        "lz": 0.0,
        "ux": 25.709905,
        "uy": 24.900365999999998,
        "uz": 39.654177
    }

    # 读取 JSON 文件
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    # 提取所有 bin 文件
    bin_files = []
    extract_bin_files(json_data['root'], bin_files)
    print(f"总共找到 {len(bin_files)} 个 .bin 文件。")

    # 下载所有 bin 文件
    download_bin_files(bin_files, base_url, bin_save_dir)

    # 创建绘图保存文件夹
    if not os.path.exists(plot_save_dir):
        os.makedirs(plot_save_dir)

    # 选择要叠加绘图的 bin 文件（从 r0 到 r020044）
    # 这里根据层级深度选择
    # 例如，选择层级深度 >= 2 的文件（r0 是 depth 1，r00 是 depth 2，等等）
    selected_bin_files = [bf for bf in bin_files if len(bf['hierarchy']) >= 2]
    print(f"选择了 {len(selected_bin_files)} 个 .bin 文件进行叠加绘图。")

    # 绘制并保存叠加图
    plot_overlaid_points_with_borders(selected_bin_files, bin_save_dir, overlaid_plot_path, bounding_box)

    # 可选：绘制树形结构图
    # 构建树形结构
    root = Node(f"{json_data['root']['file']} ({json_data['root']['numSpecimens']})")

    def build_tree(node_data, parent):
        for child_data in node_data.get('children', []):
            child = Node(f"{child_data['file']} ({child_data['numSpecimens']})", parent=parent)
            build_tree(child_data, child)

    build_tree(json_data['root'], root)

    # 导出树形结构图
    try:
        DotExporter(root).to_picture("tree.png")
        print("树形结构图已保存到 tree.png")
    except Exception as e:
        print(f"导出树形结构图失败：{e}")


if __name__ == "__main__":
    main()
