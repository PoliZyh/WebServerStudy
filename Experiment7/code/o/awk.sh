sudo mkdir -p /usr/local/log/ && sudo chmod +w /usr/local/log/

sudo awk -v year=$(date +'%Y') '
BEGIN {
  first_line_processed = 0; # 设置一个标志，表示是否已处理过第一行
  block_count = 1; # 记录块的数量
}
{
  line = $0; # 保存当前行的内容
  colon_count = 0; # 记录冒号出现的次数
  threeth_colon_position = 0
  while (match(line, /:/)) 
  { # 循环匹配冒号
    colon_count++;
    threeth_colon_position += RSTART; # 记录冒号的位置
    if (colon_count == 3) { # 找到第三个冒号
      break; # 退出循环
    }
    line = substr(line, RSTART + RLENGTH);
  }
  threeth_colon_position += RLENGTH
  first_part = substr($0, 1, threeth_colon_position); # 获取从开头到第三次出现":"的部分
  second_part = substr($0, threeth_colon_position);

  split(first_part, arr, " ");
  month = (index("JanFebMarAprMayJunJulAugSepOctNovDec", arr[1]) + 2) / 3;
  date_str = sprintf("%d-%d-%d ", year, month, arr[2]);
  time_str = arr[3]
  split(arr[5], parts, /\[/); 

  combination = date_str SUBSEP parts[2]; # 组合作为唯一标识

  if (!(combination in seen_combinations) && parts[1] != "systemd-logind") {
  # if (parts[1] != "systemd-logind") {
    if (first_line_processed) {
      block_count++;
    }
    
    if (parts[2]==""){
      head[block_count] = "### " date_str time_str "\n#### " parts[1];
    }
    else{
      head[block_count] = "### " date_str time_str " [" parts[2] "\n#### " parts[1];
    }
    
    seen_combinations[combination] = block_count; # 将组合标记为已见过
    first_line_processed = 1; # 将标志设置为已处理过第一行
  }

  message = substr(second_part, 2);  # 截取掉第一个字符

  if(combination in seen_combinations){
    if(parts[1] != "systemd-logind"){
      if (index(message, ":") > 0) {
        split(message, fails, /\:/); 
        count = seen_combinations[combination];
        first[count] = first[count] "\n" "**" fails[1] ":" fails[2] ":**" fails[3]; # 存储带有 * 的消息
      }
      else {
        second[count] = second[count] "\n" message; # 存储普通消息
      }
    }
  }
  else{
    if(parts[1] != "systemd-logind"){
      if (index(message, ":") > 0) {
        split(message, fails, /\:/); 
        first[block_count] = first[block_count] "\n" "**" fails[1] ":" fails[2] ":**" fails[3]; # 存储带有 * 的消息
      }
      else {
        second[block_count] = second[block_count] "\n" message; # 存储普通消息
      }
    }
  }
}
END {
  # 输出块内容
  for (i = 1; i <= block_count; i++) {
    printf head[i]
    if (first[i] && second[i]) {
      print first[i] "\n" second[i] "\n\n\n\n"
    } else if (first[i]) {
      print first[i] "\n\n\n\n"
    } else {
      print second[i] "\n\n\n\n"
    }
  }
}
' auth.log | sudo tee /usr/local/log/error.md > /dev/null
