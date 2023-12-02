#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

void init_daemon(void);

int main(){
    int hour, min;
time_t timep;
struct tm *p;
time(&timep);
p = localtime(&timep);

printf("这是一个闹钟程序,输入你想要设定的时间:\n");
if (scanf("%d:%d", &hour, &min) != 2){
    fprintf(stderr, "输入格式错误，应为小时:分钟\n");
    exit(EXIT_FAILURE);
}

    init_daemon();

    while (1){
        sleep(20);
        time(&timep);
        p = localtime(&timep);

        if (p->tm_hour == hour && p->tm_min == min){
            // 将到达设定时间时的系统时间写入日志文件
            FILE *log_file = fopen("./alarm_log.txt", "a");
            if (log_file != NULL)
            {
                fprintf(log_file, "Alarm triggered at %02d:%02d\n", p->tm_hour, p->tm_min);
                fclose(log_file);
            }
            else
            {
                fprintf(stderr, "无法打开日志文件: %s\n", strerror(errno));
            }

            exit(EXIT_SUCCESS);
        }
    }
}

void init_daemon(void){
    pid_t child1, child2;
    int i;

    child1 = fork();

    if (child1 > 0){
        exit(EXIT_SUCCESS);
    }
    else if (child1 < 0){
    perror("创建子进程失败");
    exit(EXIT_FAILURE);
    }

    setsid();

    child2 = fork();

    if (child2 > 0){
        exit(EXIT_SUCCESS);
    }
    else if (child2 < 0){
        perror("创建子进程失败");
        exit(EXIT_FAILURE);
    }

    umask(0);

    chdir("/");

    for (i = 0; i < NOFILE; ++i){
        close(i);
    }

    open("/dev/null", O_RDWR);
    dup(0);
    dup(0);

    return;
}
