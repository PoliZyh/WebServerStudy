# WebServerStudy

记录我web服务端课程的学习心得以及源码

## 实验介绍

### 实验一：亚运会数据统计[python/node] ---- 爬虫

1. 统计亚运会关注人数最多的比赛
2. 统计亚运会票贩子的名单


### 实验二：新闻推送应用

编写新闻推送程序，具体要求如下：

1. 每隔10分钟自动从yahoo新闻的生活rss获取最新的十条新闻
2. 将获取的新闻显示到屏幕中，用户可以输入 1-10 的数字然后按回车显示新闻内容
3. 在新闻内容画面，按 t 回车可以将新闻翻译成中文。
4. 在新闻内容画面，按 q 回车返回新闻列表。

### 实验三：新闻推送进阶

编写新闻推送程序，具体要求如下：

1. 每隔10分钟自动从yahoo新闻的生活rss获取最新的十条新闻
2. 将获取的新闻显示到屏幕中，用户可以输入 1-10 的数字然后按回车显示新闻内容
3. 在新闻内容画面，按 t 回车可以将新闻翻译成中文。
4. 在新闻内容画面，按 q 回车返回新闻列表。


### 实验四：仿VIM

要求编写文字处理程序 vim.py，具体要求如下：

1. 使用 python3 vim.py hello.txt 格式能打开文件
2. 支持 hjkl 实现光标在屏幕文本上移动
3. 输入 i 可以进去编辑模式，修改文本
4. 输入 esc 可以进去普通模式
5. 在普通模式下输入 s 可以保存文本

### 实验五：Socket编程

1. 客户端连接到服务器之后，要求输入用户名和密码，格式为: `user@password`
2.  如果用户名和密码正确，则服务器返回功能菜单，如果密码错误则显示提示信息：   
   a. 客户端输入's↩︎', 然后输入消息字符串str  
   b. 客户端输入'h↩︎', 显示历史聊天记录  
   c. 客户端输入'c↩︎', 清空该客户的历史聊天记录  
   d. 客户端输入'q↩︎', 退出系统   
3. 服务器要把每个客户的历史记录保存在当前目录的 `chat.json` 文件中。  
4. 服务器每隔1小时将聊天记录压缩备份，保存在 `backup` 文件夹下面，以备份的时间进行命名。  
5. 服务器读取 `user.json` 判断用户名和密码是否正确。  

### 实验六：新闻菜单改进【python】
在实验三的基础上，要求进行功能改进：

1. 将应用的显示模式用 cursor 库改写
2. 修改每个界面的功能按钮
3. 添加系统设置功能菜单: a.设置新闻的数量 b. 选择新闻类型

### 实验七：Shell编程入门

现有 auth.log 日志文件，要求统计登录出错的记录，并以下面格式写入到 /usr/local/log/error.md 文件。请分别使用 Sed 和 Awk 编写 Shell 程序。

### 实验八：Shell改进新闻推送

编写系统数据扫描程序, 具体参数要求如下：

1. 在实验3备份的data文件夹下，统计每个子文件夹的新闻数量，以及新闻起止时间，保存到info.json
2. 将每天的24个小时的新闻合并，以YYYYMMDD.json命名，保存到result文件夹，并且以新闻时间排序
3. 通过python程序调用 awk 处理文本,提交 app.py 和 awk 程序文件
4. 使用 pm2 启动程序作为微服务运行 pm2 start app.py --name "xxx" --interpreter /usr/bin/python3

### 实验九：远程网络服务

要求实现一个类似 top 命令的网络服务，用于监控远程服务器的进程。具体要求如下：

1. web服务器使用 libmicrohttpd
2. 在浏览器中输入服务器地址 http://xxx.xxx.xxx.xxx ,显示服务器中运行进程的状态页面
3. 具体页面的格式如下图，要求分3部分显示：左边非闲置进程列表，中间占用 cpu最高的进程，右边占用内存最高的进程，每隔5秒钟刷新一次页面;
4. 非闲置进程后边有个按钮，点击后杀死该进程（不能杀死系统进程）