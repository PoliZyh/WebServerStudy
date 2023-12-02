#!/bin/awk -f

# 用于划分为对象,并且排序输出

BEGIN {
    news_idx = 0
    json_path = ARGV[1]
    delete ARGV[1]
}

{
    # 切割为对象形式
    n = split($0, file_lines, "\n")
    for (i = 1; i <= n; i++) {
        if (file_lines[i] ~ /^[0-9][0-9]\./) {
            # 以序号开头的行即为新闻标题
            news_idx += 1
            substring = substr(file_lines[i], 4)

            # 去除截取后字符串开头的空格
            sub(/^[[:space:]]+/, "", substring)
            news_title[news_idx] = substring
        } else if (file_lines[i] ~ /^[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日 [0-9]{2}:[0-9]{2}$/) {
            # 以时间开头的行即为新闻日期
            news_date[news_idx] = file_lines[i]
        } else {
            # 其余的则为新闻内容
            news_content[news_idx] = news_content[news_idx] file_lines[i] "\n"
        }
    }

}


END {
    # 使用快速排序对数组进行排序
    quicksort(news_date, 1, news_idx)

    # 输出排序后的结果
    
    # 输出到info.json中
    output_info_json()

    result_json_name = get_result_file_name()
    result_json_path = "./result/" result_json_name

    # 输出到result中
    output_result_json(result_json_path)
}

function quicksort(arr, left, right) {
    if (left < right) {
        pivot = partition(arr, left, right)
        quicksort(arr, left, pivot - 1)
        quicksort(arr, pivot + 1, right)
    }
}

function partition(arr, left, right) {
    pivot = arr[right]
    i = left - 1

    for (j = left; j < right; j++) {
        if (arr[j] <= pivot) {
            i++
            swap(arr, i, j)
            swap(news_title, i, j)
            swap(news_content, i, j)
        }
    }

    swap(arr, i + 1, right)
    swap(news_title, i + 1, right)
    swap(news_content, i + 1, right)
    return i + 1
}

function swap(arr, i, j) {
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp
}

function output_info_json() {
    # 输出json文件
    json_data = "{ \n \"count\":" news_idx ", \n \"from\": \"" news_date[1] "\", \n \"to\": \"" news_date[news_idx] "\" \n }"
    printf("%s\n", json_data) > (json_path "info.json")
}

function get_result_file_name() {
    year = substr(json_path, 8, 4)
    month = substr(json_path, 13, 2)
    day = substr(json_path, 16, 2)
    return year month day ".json"
}

function output_result_json(path) {
    is_first = 1  # 初始化为0

    if (news_idx == 0) {
         return
    }

    # Check if the file exists
    if ((getline < path) > 0) {
        # File exists, read the content and remove the last ']'
        file_content = $0

       

        # Remove the last ']'
        file_content = substr(file_content, 0, length(file_content) - 2)

        is_first = 0
    } else {
        # File doesn't exist, set flag for new file creation
        is_first = 1
        file_content = ""
    }

    # Move the file pointer to the end of the file for append mode
    file = path
    while (getline < file > 0) {}
    close(file)

    # Add the opening bracket if it's the first entry
    if (is_first == 1) {
        file_content = "["
    } 
    # Loop through the arrays and append JSON objects
    for (i = 1; i <= news_idx; i++) {
        # Add a comma if not the first entry
        if (i > 1) {
            file_content = file_content ","
        }
        gsub(/\n/, " ", news_content[i])
        gsub(/\"/, "'", news_content[i])  # 替换双引号为单引号
        new_json_object = "\n{\n  \"title\": \"" news_title[i] "\",\n  \"date\": \"" news_date[i] "\",\n  \"content\": \"" news_content[i] "\"\n}"
        file_content = file_content new_json_object
    }

    # Add the closing bracket
    if (news_idx > 0) {
        file_content = file_content ","
    }

    # Write the content back to the file
    printf "%s", file_content >> path
    close(path)
}






