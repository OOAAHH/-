from tqdm import tqdm
rg_info = {}
def check_tags(parts, required_tags):
    """检查所需的标签是否存在于SAM行中。"""
    tags = {part.split(':', 1)[0] for part in parts}
    return all(any(part.startswith(tag) for part in parts) for tag in required_tags)

def count_total_reads(file_path):
    """计算文件中总的reads数（跳过头信息）。"""
    total = 0
    with open(file_path, 'r') as f:
        for line in f:
            if not line.startswith('@'):
                total += 1
    return total

# 首先计算总reads数
total_reads = count_total_reads("/home/sunhao/RAW/Downloda/SRR10357640.sam")
print('total_reads',total_reads,sep='\t')

# 初始化计数器
current_read = 0
converted_reads = 0
skipped_reads = 0
from tqdm import tqdm
with open("/home/sunhao/RAW/Downloda/SRR10357640.sam", "r") as header_file:
    for line in header_file:
        if line.startswith('@RG'):
            parts = line.strip().split('\t')
            rg_id = [part.split(':', 1)[1] for part in parts if part.startswith('ID')][0]
            sm = [part.split(':', 1)[1] for part in parts if part.startswith('SM')][0]
            pl = [part.split(':', 1)[1] for part in parts if part.startswith('PL')][0]
            rg_info[rg_id] = {'SM': sm, 'PL': pl}
with open("/home/sunhao/RAW/Downloda/SRR10357640.sam", "r") as sam_file, \
     open("/home/sunhao/output.fastq", "w") as fastq_file:
    # 使用tqdm直接封装sam_file，避免先加载所有行到内存
    for line in tqdm(sam_file, total=total_reads, desc="Converting SAM to FASTQ", unit="reads"):
        if line.startswith('@'):
            continue
        current_read += 1    
        parts = line.split('\t')
        if not check_tags(parts, ['CB', 'UB', 'RG']):
            skipped_reads += 1
            continue
        qname, seq, qual = parts[0], parts[9], parts[10]
        rg_tag = [part for part in parts if part.startswith('RG:Z:')][0].split(':')[2]
        cb_tag = [part for part in parts if part.startswith('CB:Z:')][0].split(':')[2]
        ub_tag = [part for part in parts if part.startswith('UB:Z:')][0].split(':')[2]
        if rg_tag in rg_info:
            sm, pl = rg_info[rg_tag]['SM'], rg_info[rg_tag]['PL']
            read_name = f"@{qname}_CB:{cb_tag}_UB:{ub_tag}_RG:{rg_tag}_SM:{sm}_PL:{pl}"
            fastq_file.write(f"{read_name}\n{seq}\n+\n{qual}\n")
            converted_reads += 1
        else:
            skipped_reads += 1

#update_progress(100)  # 完成后更新进度到100%
print("\nConversion complete.")
print(f"Total reads processed: {total_reads}")
print(f"Reads converted: {converted_reads}")
print(f"Reads skipped due to missing information: {skipped_reads}")
