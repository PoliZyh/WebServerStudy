#include <microhttpd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>


#define HTML_PATH "./index.html"
#define CSS_PATH "./index.css"

char *global_html = NULL;

// 读取文件内容的函数
char *readFile(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        return NULL;
    }

    // 获取文件大小
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    // 检查文件大小是否为非负值
    if (file_size < 0) {
        perror("Error getting file size");
        fclose(file);
        return NULL;
    }

    // 分配足够的内存来存储文件内容
    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        perror("Error allocating memory");
        fclose(file);
        return NULL;
    }

    // 读取文件内容
    size_t read_size = fread(content, 1, file_size, file);

    // 检查实际读取的字节数是否和预期相同
    if (read_size != (size_t)file_size) {
        perror("Error reading file");
        free(content);
        fclose(file);
        return NULL;
    }

    content[file_size] = '\0';

    fclose(file);

    return content;
}

// 插入CSS
char *insertCss(char *html, const char *cssContent) {
    // 在 HTML 内容中插入 CSS 内容
    char *cbC = (char *)malloc(strlen(html) + strlen(cssContent) + 20);
    sprintf(cbC, "%s\n<style>%s</style>", html, cssContent);

    return cbC;
}

// 封装的函数，接收一个shell命令，返回执行结果
char* executeShellCommand(const char* command) {
    FILE* fp;
    char buffer[1024];
    char* result = NULL;
    size_t result_size = 0;

    // 打开一个shell进程，执行命令
    fp = popen(command, "r");
    if (fp == NULL) {
        fprintf(stderr, "Error opening pipe for command '%s'\n", command);
        exit(EXIT_FAILURE);
    }

    // 读取输出并动态分配内存保存
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        result_size += strlen(buffer);
        result = realloc(result, result_size + 1);
        if (result == NULL) {
            fprintf(stderr, "Memory allocation error\n");
            exit(EXIT_FAILURE);
        }
        strcat(result, buffer);
    }

    // 关闭文件指针
    pclose(fp);

    return result;
}


static int ahc_echo(void *cls,
                    struct MHD_Connection *connection,
                    const char *url,
                    const char *method,
                    const char *version,
                    const char *upload_data,
                    size_t *upload_data_size,
                    void **ptr) {
    static int dummy;
    struct MHD_Response *response;
    int ret;

    if (0 != strcmp(method, "GET")) {
        return MHD_NO; /* 非正常模式 */
    }

    if (&dummy != *ptr) {
        /* 第一次只有 head 是合法的，因此第一次不返回响应数据 */
        *ptr = &dummy;
        return MHD_YES;
    }

    if (0 != *upload_data_size) {
        return MHD_NO; /* GET模式不支持上传 */
    }

    *ptr = NULL; /* 清空内存指针 */

    

    // 处理请求
    if (strcmp(url, "/") == 0) {
        // 提取query参数
        const char *pid_str = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "pid");
        
        if (pid_str != NULL) {
            // 这里可以对query_params进行处理，比如打印或者使用
            printf("Query parameters: %s\n", pid_str);
            // 将字符串转换为整数
            pid_t process_id_to_kill = atoi(pid_str);

            // 发送终止信号给指定的进程
            if (kill(process_id_to_kill, SIGTERM) == 0) {
                printf("进程 %d 已被成功终止。\n", process_id_to_kill);
            } else {
                perror("终止进程失败");
            }
            
        }
        const char* command = "bash main.sh"; 
        global_html = executeShellCommand(command);
    }

    char *css_content = readFile(CSS_PATH);
    global_html = insertCss(global_html, css_content);
    free(css_content);

    response = MHD_create_response_from_buffer(strlen(global_html), (void *)global_html, MHD_RESPMEM_PERSISTENT);
    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response);

    return ret;
}






int main(int argc, char **argv) {
    const char* command = "bash main.sh"; 
    char *html_content = executeShellCommand(command);
    
    global_html = html_content;
    
    struct MHD_Daemon *daemon = NULL;  // 保存MHD_Daemon指针

    if (argc != 2) {
        printf("%s PORT\n", argv[0]);
        return 1;
    }

    do {

        if (html_content == NULL) {
            fprintf(stderr, "Error reading HTML file\n");
            return 1;
        }
        daemon = MHD_start_daemon(MHD_USE_THREAD_PER_CONNECTION,
                                  atoi(argv[1]),
                                  NULL,
                                  NULL,
                                  &ahc_echo,
                                  html_content,
                                  MHD_OPTION_END);

        if (daemon == NULL) {
            fprintf(stderr, "Error starting server\n");
            free(html_content);
            return 1;
        }

        printf("Press Enter to stop the server...\n");
        getchar(); // 等待用户输入

        free(html_content);
    } while (0);

    // 停止最终的MHD_Daemon
    if (daemon != NULL) {
        MHD_stop_daemon(daemon);
        printf("Stopped the final MHD_Daemon.\n");
    }

    return 0;
}
