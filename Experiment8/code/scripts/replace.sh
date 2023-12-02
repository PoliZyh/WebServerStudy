# 进入目标文件夹
folder_path=./result

# 进入目标文件夹
folder_path=./result

# 迭代文件夹中的每个文件
for file in "$folder_path"/*; do
  if [ -f "$file" ]; then
    # 使用 awk 处理文件内容并写回源文件
    sudo awk 'NR>1 {print prev} {prev=$0} END {print "}]" }' "$file" > temp && sudo mv temp "$file"
  fi
done

