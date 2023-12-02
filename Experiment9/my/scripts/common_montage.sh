

replacement1="$1"
replacement2="$2"
replacement3="$3"
replacement4="$4"

input=$(<./module/common.module.html)

output=$(echo "$input" | sed -e "s|<td>X</td>|<td>$replacement2</td>|g" -e "s|<td>XX</td>|<td>$replacement3</td>|g" -e "s|<td>XXX</td>|<td>$replacement4</td>|g")

echo "$output"