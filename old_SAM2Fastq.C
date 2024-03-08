#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define LINE_SIZE 1024
#define TAG_SIZE 256

// 函数：检查所需标签是否存在于行中
bool check_tags(char *line, char required_tags[3][5]) {
    bool found[3] = {false, false, false};
    for (int i = 0; i < 3; i++) {
        if (strstr(line, required_tags[i])) {
            found[i] = true;
        }
    }
    return found[0] && found[1] && found[2];
}

// 函数：从行中提取特定标签的值
void extract_tag_value(char *line, const char *tag, char *value) {
    char *part = strstr(line, tag);
    if (part) {
        sscanf(part, "%*[^:]:%*[^:]:%s", value);
    } else {
        strcpy(value, "N/A"); // 如果未找到标签，则设为 N/A
    }
}

int main() {
    char *input_path = "/home/sunhao/RAW/Downloda/SRR10357640.sam";
    char *output_path = "/home/sunhao/output_new&RG&_CB_UMI_2.fastq";
    FILE *sam_file = fopen(input_path, "r");
    FILE *fastq_file = fopen(output_path, "w");
    char line[LINE_SIZE];
    char qname[TAG_SIZE], seq[TAG_SIZE], qual[TAG_SIZE];
    char rg_tag[TAG_SIZE], cb_tag[TAG_SIZE], ub_tag[TAG_SIZE];
    char required_tags[3][5] = {"RG:Z", "CB:Z", "UB:Z"};
    int total_reads = 0, converted_reads = 0, skipped_reads = 0;

    if (!sam_file || !fastq_file) {
        perror("Error opening file");
        return 1;
    }

    while (fgets(line, sizeof(line), sam_file)) {
        if (line[0] == '@') {
            skipped_reads++;
            continue;
        }
        total_reads++;
        if (!check_tags(line, required_tags)) {
            skipped_reads++;
            continue;
        }
        sscanf(line, "%s\t%*s\t%*s\t%*s\t%*s\t%*s\t%*s\t%*s\t%*s\t%s\t%s", qname, seq, qual);
        extract_tag_value(line, "RG:Z:", rg_tag);
        extract_tag_value(line, "CB:Z:", cb_tag);
        extract_tag_value(line, "UB:Z:", ub_tag);
        fprintf(fastq_file, "@%s&RG:%s&_%s_%s\n%s\n+\n%s\n", qname, rg_tag, cb_tag, ub_tag, seq, qual);
        converted_reads++;
    }

    fclose(sam_file);
    fclose(fastq_file);

    printf("\nConversion complete.\n");
    printf("Total reads processed (excluding headers): %d\n", total_reads);
    printf("Reads converted: %d\n", converted_reads);
    printf("Reads skipped due to missing information: %d\n", skipped_reads);

    return 0;
}
