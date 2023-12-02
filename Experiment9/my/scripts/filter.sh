awk 'NR > 7 {print $1, $9, $10, $12}' ./log/index.log

