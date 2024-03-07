from tqdm import tqdm
import os
def check_tags(parts, required_tags):
    """检查所需的标签是否存在于SAM行中。"""
    tags = {part.split(':', 1)[0] for part in parts}
    return all(any(part.startswith(tag) for part in parts) for tag in required_tags)
def count_total_reads(file_path):
    """估算文件中总的reads数（跳过头信息），显示进度。"""
    total = 0
    file_size = os.path.getsize(file_path)
    with tqdm(total=file_size, desc="Estimating total reads", unit="B", unit_scale=True) as pbar:
        with open(file_path, 'r') as f:
            for line in f:
                pbar.update(len(line))
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

with open("/home/sunhao/RAW/Downloda/SRR10357640.sam", "r") as sam_file, \
     open("/home/sunhao/output.fastq", "w") as fastq_file:
    for line in tqdm(sam_file, total=total_reads, desc="Converting SAM to FASTQ", unit="reads"):
        if line.startswith('@'):
            continue
        parts = line.split('\t')
        if not check_tags(parts, ['CB:Z', 'UB:Z', 'RG:Z']):
            skipped_reads += 1
            continue
        qname, seq, qual = parts[0], parts[9], parts[10]
        rg_tag = [part for part in parts if part.startswith('RG:Z:')][0].split(':')[2]
        cb_tag = [part for part in parts if part.startswith('CB:Z:')][0].split(':')[2]
        ub_tag = [part for part in parts if part.startswith('UB:Z:')][0].split(':')[2]
        # 直接使用RG标签值
        read_name = f"@{qname}_CB:{cb_tag}_UB:{ub_tag}_RG:{rg_tag}"
        fastq_file.write(f"{read_name}\n{seq}\n+\n{qual}\n")
        converted_reads += 1

print("\nConversion complete.")
print(f"Total reads processed: {total_reads}")
print(f"Reads converted: {converted_reads}")
print(f"Reads skipped due to missing information: {skipped_reads}")
