#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h> // 添加 bool 类型支持
#include <fcntl.h>   // 用于文件操作
#include <json-c/json.h> // JSON解析库
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <pthread.h>

#define SERV_TCP_PORT   8085
#define MAX_SIZE        256

// 定义用户结构体
typedef struct {
    char username[MAX_SIZE];
    char password[MAX_SIZE];
} User;

// 定义一个结构体来存储历史记录
struct History {
    char username[64];
    char date[64];
    char msg[256];
};

// 函数声明
User* parseUsersFromJsonFile(const char* filename, int* numUsers);
int checkCredentials(const User* users, int numUsers, const char* username, const char* password);
void *handleClient(void *arg);
void* backupThread(void* arg);
int copyFile(const char* source, const char* destination);


// 从JSON文件中解析用户数据并返回用户数组
User* parseUsersFromJsonFile(const char* filename, int* numUsers) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Unable to open JSON file");
        return NULL;
    }

    struct json_object *root = json_object_from_file(filename);

    if (root == NULL) {
        fprintf(stderr, "Error parsing JSON data.\n");
        fclose(file);
        return NULL;
    }

    struct json_object *users_array = NULL;
    if (json_object_object_get_ex(root, "users", &users_array)) {
        int numUsersInJson = json_object_array_length(users_array);
        User *userList = (User*)malloc(sizeof(User) * numUsersInJson);
        int i;
        for (i = 0; i < numUsersInJson; i++) {
            struct json_object *user_obj = json_object_array_get_idx(users_array, i);
            struct json_object *username_item = NULL;
            struct json_object *password_item = NULL;

            if (json_object_object_get_ex(user_obj, "username", &username_item) &&
                json_object_object_get_ex(user_obj, "password", &password_item)) {
                strncpy(userList[i].username, json_object_get_string(username_item), sizeof(userList[i].username));
                strncpy(userList[i].password, json_object_get_string(password_item), sizeof(userList[i].password));
            }
        }

        *numUsers = numUsersInJson;

        json_object_put(root);
        fclose(file);

        return userList;
    }

    json_object_put(root);
    fclose(file);

    return NULL;
}

// 检查用户名和密码是否存在于用户数组中
int checkCredentials(const User* users, int numUsers, const char* username, const char* password) {
    int i;
    for (i = 0; i < numUsers; i++) {
        if (strcmp(username, users[i].username) == 0 &&
            strcmp(password, users[i].password) == 0) {
            return i; // 返回用户索引
        }
    }

    return -1; // 用户未找到
}


void *handleClient(void *arg) {
    // 收集用户列表
    int numUsers;
    char string[MAX_SIZE];
    int len;
    int session_user;
    User* users = parseUsersFromJsonFile("user.json", &numUsers);
    int newsockfd = *(int *)arg;

    // 处理客户端请求
    // 这里可以放置之前处理客户端请求的代码

    int is_running = 1;
    while(is_running) {

        /* 读取客户端的消息 */
        len = read(newsockfd, string, MAX_SIZE); 
        /* 字符串结尾处理 */
        string[len] = 0;

        // 截取字符串
        int token_count = 0;
        char *tokens[10]; // 用于存储分割后的部分
        char *token = strtok(string, "*"); // 第一次调用strtok
        while (token != NULL) {
            if (strlen(token) > 0) { // 跳过空字符串
                tokens[token_count] = token;
                token_count++;
            }
            token = strtok(NULL, "*"); // 之后的调用要传入NULL，以继续分割
        }
        printf("The event code is: %s \n", tokens[0]);
        // tokens[0] -> 事件码
        if(strcmp(tokens[0], "000") == 0) {
            // 登录
            // 检查用户名tokens[1]和密码tokens[2]
            int result = checkCredentials(users, numUsers, tokens[1], tokens[2]);
            if(result == -1) {
                send(newsockfd, "*002*登录失败账号密码不匹配*", strlen("*002*登录失败账号密码不匹配*"), 0);
            } else {
                // 成功情况下
                session_user = result;
                printf("%s Login! \n", tokens[1]);
                send(newsockfd, "*001*登录成功*", strlen("*001*登录成功*"), 0);
            }
        } else if(strcmp(tokens[0], "003") == 0) {
            // 接受消息
            // tokens[1] username; tokens[2] date; tokens[3] msg
            // 创建新消息的JSON对象
            struct json_object *newMessage = json_object_new_object();
            json_object_object_add(newMessage, "username", json_object_new_string_len(tokens[1], strlen(tokens[1])));
            json_object_object_add(newMessage, "date", json_object_new_string_len(tokens[2], strlen(tokens[2])));
            json_object_object_add(newMessage, "msg", json_object_new_string_len(tokens[3], strlen(tokens[3])));

            // 打开文件
            FILE *file = fopen("chat.json", "a+");
            if (file == NULL) {
                perror("could not open file");
                send(newsockfd, "*005*消息发送失败*", strlen("*005*消息发送失败*"), 0);
                return;
            }

            // 读取现有 JSON 数据
            fseek(file, 0, SEEK_END);
            long fileSize = ftell(file);
            fseek(file, 0, SEEK_SET);

                // 如果文件为空，创建一个新 JSON 数组
            if (fileSize == 0) {
                struct json_object *root = json_object_new_array();
                json_object_array_add(root, newMessage);
                // fprintf(file, "%s\n", json_object_to_json_string(root));
                fprintf(file, "%s\n", json_object_to_json_string_ext(root, JSON_C_TO_STRING_PRETTY));
                json_object_put(root);
            } else {
                // 读取现有 JSON 数据
                char *jsonStr = (char *)malloc(fileSize + 1);
                if (jsonStr == NULL) {
                    perror("memory allocation failed");
                    fclose(file);
                    return;
                }
                fread(jsonStr, 1, fileSize, file);
                jsonStr[fileSize] = '\0';

                // 解析现有 JSON 数据
                struct json_object *root = json_tokener_parse(jsonStr);
                free(jsonStr);

                if (json_object_get_type(root) == json_type_array) {
                    // 如果 root 是一个 JSON 数组，添加新消息到现有数组中
                    json_object_array_add(root, newMessage);

                    // 回到文件开头并清空文件内容
                    fseek(file, 0, SEEK_SET);
                    ftruncate(fileno(file), 0);

                    // 将修改后的 JSON 数组写回文件
                    // fprintf(file, "%s\n", json_object_to_json_string(root));
                    fprintf(file, "%s\n", json_object_to_json_string_ext(root, JSON_C_TO_STRING_PRETTY));
                } else {
                    fprintf(stderr, "JSON data is not an array\n");
                }

                json_object_put(root);
            }

            //
            send(newsockfd, "*004*消息发送成功*", strlen("*004*消息发送成功*"), 0);

            // 关闭文件
            fclose(file);

            // 释放资源
            json_object_put(newMessage);

        } else if(strcmp(tokens[0], "006") == 0) {
            // 退出登录
            // tokens[1] username
            printf("%s Logout!\n", tokens[1]);
            is_running = 0;
        } else if(strcmp(tokens[0], "007") == 0) {
            // 历史记录
            // tokens[1] username
            // 打开文件
            FILE *file = fopen("chat.json", "r");
            if (file == NULL) {
                perror("could not open file");
                return ;
            }

            // 读取现有 JSON 数据
            fseek(file, 0, SEEK_END);
            long fileSize = ftell(file);
            fseek(file, 0, SEEK_SET);

            // 读取文件内容到一个缓冲区
            char *jsonStr = (char *)malloc(fileSize + 1);
            if (jsonStr == NULL) {
                perror("memory allocation failed");
                fclose(file);
                return ;
            }
            fread(jsonStr, 1, fileSize, file);
            jsonStr[fileSize] = '\0';

            // 解析现有 JSON 数据
            struct json_object *root = json_tokener_parse(jsonStr);
            free(jsonStr);

            // 检查解析是否成功
            if (json_object_get_type(root) != json_type_array) {
                fprintf(stderr, "JSON data is not an array\n");
                json_object_put(root);
                fclose(file);
                return ;
            }

            // 初始化一个结构体数组来存储满足条件的数据
            struct History history[1000]; 
            int historyCount = 0;

            // 遍历 JSON 数组并筛选出符合条件的数据
            int arrayLen = json_object_array_length(root);
            int i;
            for (i = 0; i < arrayLen; i++) {
                struct json_object *item = json_object_array_get_idx(root, i);
                if (json_object_get_type(item) == json_type_object) {
                    struct json_object *usernameObj, *dateObj, *msgObj;
                    if (json_object_object_get_ex(item, "username", &usernameObj) &&
                        json_object_object_get_ex(item, "date", &dateObj) &&
                        json_object_object_get_ex(item, "msg", &msgObj)) {
                        const char *username = json_object_get_string(usernameObj);
                        const char *date = json_object_get_string(dateObj);
                        const char *msg = json_object_get_string(msgObj);

                        // 检查用户名是否匹配
                        if (strcmp(tokens[1], username) == 0) {
                            // 存储匹配的历史记录
                            strcpy(history[historyCount].username, username);
                            strcpy(history[historyCount].date, date);
                            strcpy(history[historyCount].msg, msg);
                            historyCount++;
                        }
                    }
                }
            }

            // 构建要发送给客户端的字符串
            char response_history[24080]; 
            memset(response_history, 0, sizeof(response_history));
            strcat(response_history, "*008*");
            if (historyCount == 0) {
                // 没有历史记录
                send(newsockfd, "*009*历史记录为空*", strlen("*009*历史记录为空*"), 0);
            } else {
                // 打印匹配的历史记录
                for (i = 0; i < historyCount; i++) {
                    if (i > 0) {
                        strcat(response_history, "\n");
                    }
                    strcat(response_history, "user: ");
                    strcat(response_history, history[i].username);
                    strcat(response_history, ", time: ");
                    strcat(response_history, history[i].date);
                    strcat(response_history, ", msg: ");
                    strcat(response_history, history[i].msg);
                }
                strcat(response_history, "*");

                send(newsockfd, response_history, strlen(response_history), 0);
            }
            

            // 释放资源
            json_object_put(root);
            fclose(file);

        } else if (strcmp(tokens[0], "010") == 0) {
            // 清空对应的历史记录
            // tokens[1] username
            // 打开文件
            FILE *file = fopen("chat.json", "r");
            if (file == NULL) {
                perror("could not open file");
                return;
            }

            // 读取文件内容
            fseek(file, 0, SEEK_END);
            long fileSize = ftell(file);
            fseek(file, 0, SEEK_SET);

            char *jsonStr = (char *)malloc(fileSize + 1);
            if (jsonStr == NULL) {
                perror("memory allocation failed");
                fclose(file);
                return;
            }
            fread(jsonStr, 1, fileSize, file);
            jsonStr[fileSize] = '\0';

            // 解析现有 JSON 数据
            json_object *root = json_tokener_parse(jsonStr);
            free(jsonStr);

            // 检查解析是否成功
            if (root == NULL) {
                fprintf(stderr, "JSON data parsing failed\n");
                fclose(file);
                return;
            }

            // 初始化一个新 JSON 数组，用于存储非 "tom" 的历史记录
            json_object *newRoot = json_object_new_array();
            int i, arrayLen = json_object_array_length(root);
            for (i = 0; i < arrayLen; i++) {
                json_object *item = json_object_array_get_idx(root, i);
                json_object *usernameObj = NULL;
                if (json_object_object_get_ex(item, "username", &usernameObj)) {
                    const char *username = json_object_get_string(usernameObj);
                    if (strcmp(username, tokens[1]) != 0) {
                        // 将非 "tom" 的历史记录添加到新 JSON 数组中
                        json_object_array_add(newRoot, item);
                    }
                }
            }

            // 关闭原文件
            fclose(file);

            // 打开文件以便写入
            file = fopen("chat.json", "w");
            if (file == NULL) {
                perror("could not open file");
                json_object_put(root);
                json_object_put(newRoot);
                return;
            }

            // 将新的 JSON 数据写入文件
            const char *newJsonStr = json_object_to_json_string(newRoot);
            if (newJsonStr != NULL) {
                fwrite(newJsonStr, 1, strlen(newJsonStr), file);
            }

            // 关闭文件和释放资源
            fclose(file);
            json_object_put(root);
            json_object_put(newRoot);

            send(newsockfd, "*011*历史记录清除成功*", strlen("*011*历史记录清除成功*"), 0);

        } else {
            printf("Event code does not exist\n");
        }
    }

    // 关闭客户端连接
    close(newsockfd);

    pthread_exit(NULL);
}


void* backupThread(void* arg) {

    while (1) {
        // 获取当前日期和时间
        time_t current_time;
        struct tm *time_info;
        time(&current_time);
        time_info = localtime(&current_time);

        char backup_filename[64];
        strftime(backup_filename, sizeof(backup_filename), "%Y-%m-%d_%H-%M-%S", time_info);

        // 构建备份命令
        char command[256];
        sprintf(command, "zip -r backup/%s.zip chat.json", backup_filename);

        // 执行备份命令
        int result = system(command);

        if (result == 0) {
            printf("Chat history backup completed: %s.zip\n", backup_filename);
        } else {
            fprintf(stderr, "Backup failed.\n");
        }

        // 等待1小时
        sleep(3600); 
    }

    return NULL;
}

int copyFile(const char* source, const char* destination) {
    FILE* sourceFile = fopen(source, "rb");
    FILE* destinationFile = fopen(destination, "wb");

    if (sourceFile == NULL || destinationFile == NULL) {
        return -1; // 打开文件失败
    }

    char buffer[1024];
    size_t bytesRead;

    while ((bytesRead = fread(buffer, 1, sizeof(buffer), sourceFile)) > 0) {
        fwrite(buffer, 1, bytesRead, destinationFile);
    }

    fclose(sourceFile);
    fclose(destinationFile);

    return 0;
}





int main(int argc, char *argv[]) {
    int port = SERV_TCP_PORT;
    if (argc == 2) {
        sscanf(argv[1], "%d", &port);
    }

    int sockfd, newsockfd;
    struct sockaddr_in serv_addr, cli_addr;
    socklen_t clilen;

    // 创建套接字
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("无法打开套接字");
        exit(1);
    }

    // 设置服务器地址结构
    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(port);

    // 绑定服务器地址
    if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) {
        perror("无法绑定本地地址");
        exit(1);
    }

    // 监听端口，允许最多5个等待连接
    listen(sockfd, 5);

    /* 备份的线程 */
    pthread_t thread_backup;
    // 创建线程
    pthread_create(&thread_backup, NULL, backupThread, NULL);

    for(;;) {
        clilen = sizeof(cli_addr);
        newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
        if(newsockfd < 0) {
            perror("can't bind local address");
            continue;
        }   
        // 创建新线程处理客户端连接
        pthread_t tid;
        if (pthread_create(&tid, NULL, handleClient, &newsockfd) != 0) {
            perror("无法创建线程");
        }
    }  
    pthread_cancel(thread_backup);
    close(sockfd);
}
