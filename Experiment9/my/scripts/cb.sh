#!/bin/bash

your_html_file="./index.html"

awk -v tbody1="<tbody id=\"tbody1\">" -v tbody2="<tbody id=\"tbody2\">" -v tbody3="<tbody id=\"tbody3\">" -v start_tbody2="<tbody id=\"tbody2\">" -v end_tbody2="</tbody>" '
BEGIN {
    # 读入整个 HTML 文件
    while (getline line < "'"$your_html_file"'") {
        html_content = html_content line "\n"
    }
    close("'"$your_html_file"'")

    # 初始化标志
    in_tbody2 = 0
    in_tbody1 = 0
    in_tbody3 = 0
}

NR <= 3 {
    in_tbody2 = 1
    tbody2_content = tbody2_content $0
}

NR > 3 && NR <= 6 {
    in_tbody3 = 1
    tbody3_content = tbody3_content $0
}

NR > 6 {
    in_tbody1 = 1
    tbody1_content = tbody1_content $0
}

END {
    if (in_tbody2) {
        html_content = gensub(start_tbody2 end_tbody2, start_tbody2 "\n" tbody2_content end_tbody2, "1", html_content)
    }
    if (in_tbody1) {
        html_content = gensub(tbody1 end_tbody2, tbody1 "\n" tbody1_content end_tbody2, "1", html_content)
    }
    if (in_tbody3) {
        html_content = gensub(tbody3 end_tbody2, tbody3 "\n" tbody3_content end_tbody2, "1", html_content)
    }

    # 输出修改后的 HTML 到输出文件
    print html_content 
}
' 
