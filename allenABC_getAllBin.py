import json
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import requests


def extract_bin_files(node, base_path=""):
    """
    递归提取所有 .bin 文件的相对路径。

    :param node: 当前节点的字典
    :param base_path: 当前节点的路径前缀
    :return: 包含所有 .bin 文件相对路径的列表
    """
    bin_files = []
    current_file = os.path.join(base_path, node['file'])
    bin_files.append(current_file)

    for child in node.get('children', []):
        bin_files.extend(extract_bin_files(child, base_path))

    return bin_files


def download_bin_files(bin_files, base_url, download_dir):
    """
    下载所有 .bin 文件到指定的本地文件夹中。

    :param bin_files: 包含所有 .bin 文件相对路径的列表
    :param base_url: 下载文件的基 URL
    :param download_dir: 本地下载目录
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for bin_file in tqdm(bin_files, desc="Downloading .bin files"):
        # 构建完整的下载 URL
        url = os.path.join(base_url, bin_file)
        local_path = os.path.join(download_dir, bin_file)

        # 确保本地目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # 下载文件
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while downloading {url}: {http_err}")
        except Exception as err:
            print(f"Error occurred while downloading {url}: {err}")


def read_bin_file(filename):
    """
    读取二进制文件，数据类型为 float32。

    :param filename: .bin 文件路径
    :return: NumPy 数组
    """
    try:
        data = np.fromfile(filename, dtype=np.float32)
        return data
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None


def reshape_points(data):
    """
    将一维数组重塑为 Nx2 的二维数组。

    :param data: 一维 NumPy 数组
    :return: 重塑后的二维数组
    """
    if len(data) % 2 != 0:
        data = data[:-1]  # 如果不是偶数，去掉最后一个数

    points = data.reshape(-1, 2)
    return points


def plot_points(points, bounding_box, title):
    """
    绘制散点图。

    :param points: Nx2 的 NumPy 数组
    :param bounding_box: 边界框字典
    :param title: 图表标题
    """
    plt.figure(figsize=(10, 8))

    # 设置坐标轴范围
    plt.xlim(bounding_box['lx'], bounding_box['ux'])
    plt.ylim(bounding_box['ly'], bounding_box['uy'])

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)

    # 绘制散点图
    plt.scatter(points[:, 0], points[:, 1], s=1, c='blue', alpha=0.5)

    # 保存图像而不是显示，以便批量处理
    plt.savefig(title.replace('/', '_') + '.png', dpi=300)
    plt.close()


def traverse_and_plot(node, base_path, download_dir, bounding_box):
    """
    递归遍历 JSON 树，读取和绘制每个 .bin 文件。

    :param node: 当前节点的字典
    :param base_path: 当前节点的路径前缀
    :param download_dir: 本地下载目录
    :param bounding_box: 边界框字典
    """
    current_file = os.path.join(base_path, node['file'])
    local_path = os.path.join(download_dir, current_file)

    if os.path.exists(local_path):
        data = read_bin_file(local_path)
        if data is not None:
            points = reshape_points(data)

            # 验证点的范围是否在 bounding_box 内
            x_in_range = np.all((points[:, 0] >= bounding_box['lx']) & (points[:, 0] <= bounding_box['ux']))
            y_in_range = np.all((points[:, 1] >= bounding_box['ly']) & (points[:, 1] <= bounding_box['uy']))

            print(f"{current_file} - X 坐标在范围内：{x_in_range}, Y 坐标在范围内：{y_in_range}")

            # 绘图
            title = current_file.replace(os.sep, '_')
            plot_points(points, bounding_box, title)
    else:
        print(f"文件 {local_path} 不存在。")

    for child in node.get('children', []):
        traverse_and_plot(child, base_path, download_dir, bounding_box)


def main():


    # 步骤 1：提取所有 .bin 文件
    with open('ScatterBrain.json', 'r') as f:
        data = json.load(f)

    root_node = data['root']
    all_bin_files = extract_bin_files(root_node)

    # 打印所有 .bin 文件路径（可选）
    # for bin_file in all_bin_files:
    #     print(bin_file)

    # 步骤 2：下载所有 .bin 文件
    base_url = "https://prod-sfs.brain.allentech.org/api/v1/Metadata/sb/AP8JNN5LYABGVMGKY1B/Q1NCWWPG6FZ0DNIXJBQ/v0/G4I4GFJXJB9ATZ3PTX1Coordinates/G4I4GFJXJB9ATZ3PTX1/"
    download_dir = "downloaded_bins"

    # 下载文件（如果尚未下载，可以取消注释以下行）
    download_bin_files(all_bin_files, base_url, download_dir)

    # 步骤 3：读取和绘制所有 .bin 文件
    bounding_box = {
        "lx": -13.944271999999998,
        "ly": -14.753810999999999,
        "lz": 0.0,
        "ux": 25.709905,
        "uy": 24.900365999999998,
        "uz": 39.654177
    }

    traverse_and_plot(root_node, "", download_dir, bounding_box)


if __name__ == "__main__":
    main()
