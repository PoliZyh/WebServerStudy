

# 读入文件
HTML_PATH='./index.html'
COMMON_TEMPLATE='./module/common.module.html'
DEL_TEMPLATE='./module/del.module.html'

COMMON_SH='bash ./scripts/common_montage.sh'
DEL_SH='bash ./scripts/del_montage.sh'

awk -v common_template="$COMMON_TEMPLATE" -v del_template="$DEL_TEMPLATE" -v common_sh="$COMMON_SH" -v del_sh="$DEL_SH" '
{
    if (NR <= 3) {
        # 占用CPU最高的进程(前3)
        # 将 $1 2 3 传入COMMON_SH并得到结果
        command = common_sh " " $1 " " $2 " " $3 " " $5
        system(command)
    } else if (NR <= 6) {
        # 占用内存最高的进程(前3)
        # 将 $1 2 3 传入DEL_SH并得到结果
        command = common_sh " " $1 " " $2 " " $4 " " $5
        system(command)
    } else {
        # 非闲置进程列表
        command = del_sh " " $1 " " $2 " " $5 " " $2
        system(command)
    }
}
' 