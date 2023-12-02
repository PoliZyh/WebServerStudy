result=$(awk 'NR > 1 && substr($11, 1, 1) == "/" {print $1, $2, $3, $4, $11}' ./log/ps.log)

# 使用循环处理每一行
while read -r line; do
    # 获取每行的最后一列
    last_column=$(basename "${line##* }")

    # 替换每行的最后一列
    modified_line="${line% *} $last_column"

    # 输出替换后的行
    echo "$modified_line"
done <<< "$result"
