# top日志
top -b -n 1 > ./log/index.log
# ps aux日志
ps aux > ./log/ps.log

{
    # 根据 CPU 排序前三
    bash ./scripts/filter_ps.sh |
    sort -k2,2nr | 
    head -n 3

    # 根据占用内存的前三
    bash ./scripts/filter_ps.sh |
    sort -k3,3nr | 
    head -n 3

    # 选出非闲置进程列表
    bash ./scripts/non_idle_ps.sh
} | bash ./scripts/all_montage.sh | bash ./scripts/cb.sh
