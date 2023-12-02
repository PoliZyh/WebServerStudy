#!/bin/awk -f

# 用于过滤数据-->将文件空行过滤掉

BEGIN {
    file_path = ARGV[1]
    lines = "" # 用于存储所有行的变量
}

{

    # 使用 getline 读取文件中的每一行 并且过滤空行
    while ((getline line < file_path) > 0) {
        if (line == "") continue
        lines = lines line "\n"
    }

}

END {
    # 关闭文件
    close(file_path)
    # 传递参数
    print lines 
}