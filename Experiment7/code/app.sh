#!/bin/bash
sudo mkdir -p /usr/local/log/ && sudo chmod +w /usr/local/log/

awk 'BEGIN {
    err_type = ""
    # 数组索引
    type_index = 1
    no_type_index = 1
    # 当前行进程号
    process_id = -1
    # 当前时间
    time = ""
    # 使用strftime函数获取当前年份
    cmd = "date +\"%Y\"";
    cmd | getline currentYear;
    close(cmd);
}

# 判断是否为有类型报错的行
function hasType(line) {
    return match(line, /[^:]*:[^:]*/)
}



# 输出
function console_log() {
    print "### " time "[" process_id "]"
    print "#### " err_type
    for (i in type_list) {
        print "**" type_list[i] "**" type_content_list[i]
    }
    printf "\n"
    for (i in no_type_content_list) {
        print no_type_content_list[i]
    }
    print "\n"
    printf "\n"
    
}

function extractProcessInfo(line) {
    if (match(line, /\[([0-9]+)\]/)) {
        return substr(line, RSTART + 1, RLENGTH - 2)
    }
    return ""
}

function extractProcessType(line) {
    if (match(line, /([^[]+)\[/)) {
        return substr(line, RSTART, RLENGTH - 1)
    }
    return ""
}

function format_date(time) {
    
    monthMap["Jan"] = "01"; monthMap["Feb"] = "02"; monthMap["Mar"] = "03";
    monthMap["Apr"] = "04"; monthMap["May"] = "05"; monthMap["Jun"] = "06";
    monthMap["Jul"] = "07"; monthMap["Aug"] = "08"; monthMap["Sep"] = "09";
    monthMap["Oct"] = "10"; monthMap["Nov"] = "11"; monthMap["Dec"] = "12";

    # 切分字符串以空格为分隔符
    split(time, arr, " ");

    # 提取月份、日期和时间部分
    month = monthMap[arr[1]];
    day = sprintf("%02d", arr[2]);
    timePart = arr[3];

    

    # 构建格式化后的日期时间字符串
    formatted_date = currentYear "-" month "-" day " " timePart

    return formatted_date
}


{
    # 截取当前行信息
    # 进程号以及出错类型
    cron_type = extractProcessType($5) # 错误类型
    cron_number = extractProcessInfo($5) # 进程号
    date_mon = $1 # 月
    date_day = $2 # 日
    date_hour = $3 
    
    
    if (cron_number != process_id && cron_type != "systemd-logind") {
        if (process_id != -1) {
            console_log()
        }
        err_type = cron_type
        # 数组索引
        type_index = 1
        no_type_index = 1
        # 当前行进程号
        process_id = cron_number
        # 当前时间
        time = format_date(date_mon " " date_day " " date_hour)
        # 数组
        delete type_list
        delete type_content_list
        delete no_type_content_list
    } 
    row_content = substr($0, index($0, $5) + length($5) + 1)
    if(hasType(row_content)) {
        if (cron_type != "systemd-logind") {
        # 有出错类型的情况下
        $0 = row_content
        type_list[type_index] = $1
        $1 = ""
        type_content_list[type_index] = $0
        type_index++
        }
        
    } else {
        # 没有出错类型的情况下
        no_type_content_list[no_type_index] = row_content  
        no_type_index++
    }

    

}
END {
    if (process_id != -1) {
        console_log()
    }
}
' ./auth.log > /usr/local/log/error.md

