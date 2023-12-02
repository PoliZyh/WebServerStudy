

replacement1="$1"
replacement2="$2"
replacement3="$3"
replacement4="$4"

input=$(<./module/del.module.html)

output=$(echo "$input" | sed -e "s|<td>X</td>|<td>$replacement2</td>|g" -e "s|<td>XXXX</td>|<td>$replacement1</td>|g" -e "s|<td>XX</td>|<td>$replacement3</td>|g" -e "s|<button class=\"btn-del\" onclick=\"killPid(XXX)\" data-user=\"XXXXX\">删除</button>|<button class=\"btn-del\" onclick=\"killPid($replacement4)\" data-user=\"$replacement1\">删除</button>|g")

echo "$output"