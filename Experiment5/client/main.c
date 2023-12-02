#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>



#define SERV_TCP_PORT 8085
#define MAX_SIZE        256

// 全局变量
char global_username[256];
int global_isrunning = 1;

// 定义状态机
enum State {
    STATE_1_INIT,
    STATE_1_MENU
};
enum State_Menu {
    STATE_1_MENU_2_SEND,
    STATE_1_MENU_2_HISTORY,
    STATE_1_MENU_2_CLEAR,
    STATE_1_MENU_2_QUIT,
};

// 状态机结构
struct StateMachine {
    enum State current_state;
};
struct StateMenuMachine {
    enum State_Menu current_state_menu;
};

// 全局变量
struct StateMachine state_machine;

// 函数声明
void handleUserLogin(int sockfd, struct StateMachine* sm);
void handleSendMsgToServer(int sockfd);
void handleStateMenuMachine(struct StateMenuMachine* smm, int sockfd, struct StateMachine* sm);
void handleUserLogout(int sockfd);
void handleGetHistory(int sockfd);
void handleClearHistory(int sockfd);

// 初始化状态机
void initStateMachine(struct StateMachine* sm) {
    sm->current_state = STATE_1_INIT;
}

// 处理状态
void handleStateMachine(struct StateMachine* sm, int sockfd) {
    struct StateMenuMachine state_menu_machine;
    switch(sm->current_state) {
        case STATE_1_INIT:
            handleUserLogin(sockfd, sm);
            break;
        case STATE_1_MENU:
            // 初始化子状态机 
            handleStateMenuMachine(&state_menu_machine, sockfd, sm);
            break;
    }
}

// 发送消息
void handleSendMsgToServer(int sockfd) {
    time_t currentTime;
    struct tm *timeInfo;
    char timeString[50];
    // 获取当前时间
    time(&currentTime);
    // 格式化时间
    timeInfo = localtime(&currentTime);
    strftime(timeString, sizeof(timeString), "%Y年%m月%d日%H:%M", timeInfo);
    // 等待输入
    char user_msg[1024];
    char send_msg[1280];
    printf("Enter a message to send: ");
    scanf(" %s", user_msg); // 注意这里的格式化字符串
    snprintf(send_msg, sizeof(send_msg), "*003*%s*%s*%s", global_username, timeString, user_msg);
    write(sockfd, send_msg, strlen(send_msg));
    // 等待响应
    char response_message[200];
    int bytes_received = read(sockfd, response_message, sizeof(response_message));
    
    if (bytes_received > 0) {
        // 在响应消息中查找登录结果
        if (strstr(response_message, "*004*") != NULL) {
            printf("Successfully sent message!\n");
        } else if (strstr(response_message, "*005*") != NULL) {
            printf("Sending message failed!\n");
        } else {
            printf("Unexpected response: %s\n", response_message);
        }
    } else {
        printf("Failed to receive server response\n");
    }
}

// 展示菜单
void handleStateMenuMachine(struct StateMenuMachine* smm, int sockfd, struct StateMachine* sm) {
    int is_running = 1;
    while (is_running) {
        char user_choice;
        printf("Enter a command \n's' to send msg \n'h' for history \n'c' to clear history \n'q' to quit: ");
    
        // scanf("%c", &user_choice);
        user_choice = getchar();  // 使用 getchar() 读取单个字符

        // 切换状态机
        if (user_choice == 's') {
            smm->current_state_menu = STATE_1_MENU_2_SEND;
        } else if (user_choice == 'h') {
            smm->current_state_menu = STATE_1_MENU_2_HISTORY;
        } else if (user_choice == 'c') {
            smm->current_state_menu = STATE_1_MENU_2_CLEAR;
        } else if (user_choice == 'q') {
            smm->current_state_menu = STATE_1_MENU_2_QUIT;
        }

        // 执行状态
        switch(smm->current_state_menu) {
            case STATE_1_MENU_2_SEND:
                // 发送消息
                handleSendMsgToServer(sockfd);
                break;
            case STATE_1_MENU_2_HISTORY:
                // 处理历史记录
                handleGetHistory(sockfd);
                break;
            case STATE_1_MENU_2_QUIT:
                // 退出登录
                handleUserLogout(sockfd);
                is_running = 0;
                global_isrunning = 0;
                break;
            case STATE_1_MENU_2_CLEAR:
                // 清空记录
                handleClearHistory(sockfd);
                break;
            default:
                printf("Invalid input. Please try again.\n");
                break;
        }
        while (getchar() != '\n');
    }
}

// 查找历史记录
void handleGetHistory(int sockfd) {
    char history_message[1024];
    snprintf(history_message, sizeof(history_message), "*007*%s*", global_username);

    // 向服务器发送登录请求消息
    write(sockfd, history_message, strlen(history_message));
    // 接收数据
    char response_message[24080];
    memset(response_message, 0, sizeof(response_message));
    int bytesRead = read(sockfd, response_message, sizeof(response_message));
    if (bytesRead <= 0) {
        perror("Data reception failed!");
    } else {
        // 打印接收到的数据
        // 在响应消息中查找登录结果
        if (strstr(response_message, "*008*") != NULL) {
            // 在 response_message 中查找 *004*
            char *found = strstr(response_message, "*008*");
            if (found != NULL) {
                // 找到 *008* 子字符串，计算数字部分的起始位置
                found += strlen("*008*");

                // 查找下一个 *
                char *end = strstr(found, "*");
                if (end != NULL) {
                    // 计算数字部分的长度
                    size_t length = end - found;

                    // 截取数字部分并打印
                    char msg[24080]; // 假设数字部分不超过256个字符
                    strncpy(msg, found, length);
                    msg[length] = '\0';
                    printf("History is:\n %s\n", msg);
                }
            }
        } else if (strstr(response_message, "*009*") != NULL) {
            printf("History is empty!\n");
        } else {
            printf("Unexpected response: %s\n", response_message);
        }
    }

}

// 清空历史记录
void handleClearHistory(int sockfd) {
    char clear_message[200];
    snprintf(clear_message, sizeof(clear_message), "*010*%s*", global_username);

    // 向服务器发送登录请求消息
    write(sockfd, clear_message, strlen(clear_message));
    // 等待响应
    char response_message[200];
    int bytes_received = read(sockfd, response_message, sizeof(response_message));
    
    if (bytes_received > 0) {
        // 在响应消息中查找登录结果
        if (strstr(response_message, "*011*") != NULL) {
            printf("History cleared successfully!\n");
        } else if (strstr(response_message, "*012*") != NULL) {
            printf("History clearing failed!\n");
        } else {
            printf("Unexpected response: %s\n", response_message);
        }
    } else {
        printf("Failed to receive server response\n");
    }
}

// 退出登录函数
void handleUserLogout(int sockfd) {
    char logout_message[200];
    snprintf(logout_message, sizeof(logout_message), "*006*%s*", global_username);

    // 向服务器发送登录请求消息
    write(sockfd, logout_message, strlen(logout_message));
}

// 用户登录函数
void handleUserLogin(int sockfd, struct StateMachine* sm) {

    char input[200];  // 存储用户输入
    char username[100];  // 存储用户名
    char password[100];  // 存储密码

    printf("Please enter your username and password (format: user@password): ");
    fgets(input, sizeof(input), stdin);  // 从用户输入读取一行

    // 使用 sscanf 从输入中提取用户名和密码
    if (sscanf(input, "%99[^@]@%99s", username, password) == 2) {
        strcpy(global_username, username);
    } else {
        printf("Invalid input format. Please use 'user@password' format.\n");
        // exit(1);
        return;
    }

    // 构建登录请求消息，这里假设使用字符串格式
    char login_message[200];
    snprintf(login_message, sizeof(login_message), "*000*%s*%s*", username, password);

    // 向服务器发送登录请求消息
    write(sockfd, login_message, strlen(login_message));

    char response_message[200];
    int bytes_received = read(sockfd, response_message, sizeof(response_message));
    
    if (bytes_received > 0) {
        // 在响应消息中查找登录结果
        if (strstr(response_message, "*001*") != NULL) {
            printf("Login successful!\n");
            sm->current_state = STATE_1_MENU;
        } else if (strstr(response_message, "*002*") != NULL) {
            printf("Login failed!\n");
        } else {
            printf("Unexpected response: %s\n", response_message);
        }
    } else {
        printf("Failed to receive server response\n");
    }
}

int main(int argc, char *argv[]) {
  int sockfd;
    int port = SERV_TCP_PORT;
    char *serv_host = "localhost";

    if (argc >= 2)
        serv_host = argv[1];

    if (argc == 3)
        port = atoi(argv[2]);

    // 创建套接字
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("无法打开套接字");
        exit(1);
    }

    struct hostent *host_ptr = gethostbyname(serv_host);
    if (host_ptr == NULL) {
        perror("获取主机信息失败");
        exit(1);
    }

    struct sockaddr_in serv_addr;
    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = ((struct in_addr *)host_ptr->h_addr_list[0])->s_addr;
    serv_addr.sin_port = htons(port);

    // 连接到远程服务器
    if (connect(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
        perror("无法连接到服务器");
        exit(1);
    }


  // 初始化状态机
  initStateMachine(&state_machine);

  /* 发送数据到服务器 */
  while(global_isrunning) {
    handleStateMachine(&state_machine, sockfd);
  }
  

  close(sockfd);
}