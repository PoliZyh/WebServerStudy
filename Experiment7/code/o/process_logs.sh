#!/bin/bash

# 使用Linux系统根目录的/usr/local/log文件夹作为日志目录
log_directory="/usr/local/log"
output_file="${log_directory}/error.md"

# 检查目录是否存在，如果不存在则创建（使用sudo权限）
if [ ! -d "${log_directory}" ]; then
    sudo mkdir -p "${log_directory}"
fi

# 赋予写入权限（使用sudo权限）
sudo chmod o+w "${log_directory}"

# 获取脚本所在目录
script_directory="$(dirname "$0")"

# 切换到脚本所在目录
cd "${script_directory}"

awk_script='
BEGIN {
    types_started["sshd"] = 0;
    types_started["cron"] = 0;
    delete process_order;  # 删除数组元素

    # 为写入打开输出文件
    output_file = "'${output_file}'";
    print "" > output_file;
}

# 删除含有 systemd-login 的行
/systemd-login/ { next }

{
    sub("iZbp1amwnz2vqj9ehdtgjvZ", "", $0);

    # 提取时间戳
    match($0, /[A-Za-z]+ [0-9]+ [0-9]+:[0-9]+:[0-9]+/);
    timestamp = substr($0, RSTART, RLENGTH);

    # 将时间戳转换为所需的格式
    cmd = "date -d \"" timestamp "\" +'\''%Y-%-m-%d %T'\'' 2>/dev/null";
    cmd | getline formatted_timestamp;
    close(cmd);

    # 用格式化后的时间戳替换原始时间戳
    sub(/[A-Za-z]+ [0-9]+ [0-9]+:[0-9]+:[0-9]+/, formatted_timestamp, $0);

    # 提取进程号和错误类型
    if ($0 ~ /sshd\[[0-9]+\]:/) {
        match($0, /sshd\[[0-9]+\]:/);
        process_type = substr($0, RSTART, RLENGTH);
        error_type = "sshd";
    } else if ($0 ~ /CRON\[[0-9]+\]:/) {
        match($0, /CRON\[[0-9]+\]:/);
        process_type = substr($0, RSTART, RLENGTH);
        error_type = "cron";
    }

    # 按进程号和错误类型分类的输出行
    if (process_type != "" && error_type != "") {
        # 只处理该进程号的第一行
        if (types_started[process_type] == 0) {
            # 记录进程号的出现顺序
            process_order[++process_order_count] = process_type;

            # 处理该进程号的第一行
            types_and_titles[process_type] = "### " formatted_timestamp " " process_type;
            types_and_titles[process_type] = types_and_titles[process_type] "\n#### " error_type;
            types_started[process_type] = 1;  # 标记该进程号已经处理过
        }

        # 检查行是否包含 error: 或 pam_unix():
        if ($0 ~ /error:/ || $0 ~ /pam_unix\([^)]+\):/) {
            # 存储包含关键字的行，排除时间戳
            errors_with_markers[process_type] = errors_with_markers[process_type] "" substr($0, RSTART + RLENGTH + 1);
        } else {
            # 存储其他行，排除时间戳
            other_lines[process_type] = other_lines[process_type] "" substr($0, RSTART + RLENGTH + 1);
        }
    }
}

END {
    # 输出包含关键字的行
    # 按照进程号的出现顺序输出
    for (i = 1; i <= process_order_count; i++) {
        process_type = process_order[i];

        if (types_and_titles[process_type] != "") {
            print types_and_titles[process_type] >> output_file;
            if (errors_with_markers[process_type] != "") {
                gsub(/error:/, "**error:**", errors_with_markers[process_type]);
                match(errors_with_markers[process_type], /pam_unix\(([^)]*)\):/, arr);
                if (arr[0]) {
                    # 如果匹配到了 "pam_unix()"，arr[1] 包含括号中的内容
                    gsub(/pam_unix\([^)]*\):/, "**pam_unix(" arr[1] "):**", errors_with_markers[process_type]);
                } else {
                    # 如果未匹配到 "pam_unix()"
                    # 可以处理相应的逻辑
                }
                print errors_with_markers[process_type] >> output_file;
            }
             # 输出其他行
            if (other_lines[process_type] != "") {
                print "" >> output_file;
                print other_lines[process_type] >> output_file;
            }
            print "" >> output_file;
            print "" >> output_file;
            print "" >> output_file;
            print "" >> output_file;
        }
    }
    # 关闭输出文件
    close(output_file);
}
'

# 运行 AWK 并将输出保存到 /usr/local/log 目录中的 error.md 文件
awk "${awk_script}" auth.log > "${output_file}"

# 恢复目录的权限（使用sudo权限）
sudo chmod o-w "${log_directory}"
