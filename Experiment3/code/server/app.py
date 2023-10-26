#coding=utf-8
import os
import functools
import threading
# import sys
import schedule
import multiprocessing
import time
# 分包
import tran
import summarize
import req
import output

# 程序停止标志符
STOP_LOOP = False

# 新闻列表
NEWS_LIST = []

# # 爬取新闻的线程
NEWS_THREAD = ''

# 更新新闻列表的间隔
REFRESH_TIME = 60 * 10

# 更新输出的间隔
OUTPUT_REFRESH_TIME = 60 * 3

# 睡眠时间间隔
SLEEP_INTERVAL = 1

# 长时间的进程
LONG_PROCESS = ''

def main():
    global STOP_LOOP
    global NEWS_LIST
    global NEWS_THREAD

    # 确保能够获取第一的新闻列表
    NEWS_LIST = get_news()

    while not STOP_LOOP:

        print_news(NEWS_LIST)
        # 用户输入
        choice = get_choice_number()
        # 根据输入进行选择
        swich_choice_list(choice, NEWS_LIST)

# 捕获新闻列表的线程
def get_news_periodically():
    # schedule.every(REFRESH_TIME).seconds.do(set_news)
    # while not STOP_LOOP:
    #     schedule.run_pending()
    #     time.sleep(1)
    global REFRESH_TIME
    global STOP_LOOP
    global SLEEP_INTERVAL

    while not STOP_LOOP:
        # 获取新闻列表
        set_news()
        slept_seconds = 0
        while not STOP_LOOP and slept_seconds < REFRESH_TIME:
            time.sleep(SLEEP_INTERVAL)
            slept_seconds += SLEEP_INTERVAL

# 输出json的列表线程
def output_data_periodically():
    global OUTPUT_REFRESH_TIME
    global STOP_LOOP
    global SLEEP_INTERVAL
    
    while not STOP_LOOP:
        # 获取新闻列表
        output.main()
        slept_seconds = 0
        while not STOP_LOOP and slept_seconds < OUTPUT_REFRESH_TIME:
            time.sleep(SLEEP_INTERVAL)
            slept_seconds += SLEEP_INTERVAL


# 设置新闻列表
def set_news():
    global NEWS_LIST
    NEWS_LIST = get_news()

# 获取新闻列表
def get_news():
    news = req.parser_rss()
    return news

# 在屏幕上打印新闻数据
def print_news(news):
    index = 1

    for new_item in news:
        print(str(index) + '. ' + new_item['title'])
        index += 1

# 清屏
def clear_screen():
    os.system('clear')

# 退出程序
def exit():
    global STOP_LOOP
    global LONG_PROCESS
    LONG_PROCESS.terminate()
    # global NEWS_THREAD
    STOP_LOOP = True
    # NEWS_THREAD.join()
    # sys.exit()

# 在文章列表界面根据用户输入进行不同操作
def swich_choice_list(choice, news):

    try: 
        # 1 - 10
        index = int(choice)
        if index <=0 or index > 10:
            print("请输入1-10")
            return
         # 获取展示的文章内容
        title = news[index - 1]['title']
        link = news[index - 1]['link']
        content = req.get_texts(link)

        # 打印文章标题、连接、内容以及操作
        atc_choice = print_article(title, link, content)

        # 选择了文章后在进行的操作
        swich_choice_article(atc_choice, title, link, content)

    except ValueError:
        # 判断是否合法
        if (choice != 'q'):
            clear_screen()
            print("请输入1-10 或者 q")
            return
        # 退出程序
        exit()

# 在文章内部根据用户输入进行不同操作
def swich_choice_article(choice, title, link, content):
    # 携带参数的函数对象
    tran_content_with_default = functools.partial(tran_content, title, link, content)
    # t / r 的映射
    option_map = {
        't': tran_content_with_default,
        'r': do_return
    }
    # 判断是否输入不合法
    if (choice not in list(option_map.keys())):
        clear_screen()
        print('请输入t或者r进行操作')
        return
    # 合法情况下
    # 清屏
    clear_screen()
    option_map[choice]()

# 在翻译界面根据用户的输入进行不同的操作
def swich_choice_tran_article(choice, title, link, content, tran_content):
    # 携带参数的函数对象
    print_article_with_default = functools.partial(print_article, title, link, content)
    sum_content_width_default = functools.partial(summarize_content, title, link, content, tran_content)
    # o / s 的映射
    option_map = {
        'o': print_article_with_default,
        's': sum_content_width_default
    }
    # 判断是否输入不合法
    if (choice not in list(option_map.keys())):
        clear_screen()
        print('请输入o或者s进行操作')
        return
    # 合法情况下
    # 清屏
    clear_screen()
    option_map[choice]()

# 翻译
def tran_content(title, link, content):
    res_tran = tran.baiduTran(content)
    # 在翻译界面下等待选择
    new_choice = print_tran_article(title, link, res_tran)
    swich_choice_tran_article(new_choice, title, link, content, res_tran)

# 总结
def summarize_content(title, link, content, tran_content):
    res_sum = summarize.get_content_summarize(tran_content)
    # 在总结界面下等待选择
    new_choice = print_sum_article(title, link, res_sum)
    swich_choice_tran_article(new_choice, title, link, content, tran_content)

# 获取用户的输入
def get_choice_number():
    print("                                          ")
    print("        ---------------操作----------------")
    print("        请选择：                           ")
    print("        1.  显示文章内容[1-10]")
    print("        2.  退出程序[q]")
    print('        ----------------------------------')
    print("                                           ")
    choice = input("请输入选项：")
    # 输入后清屏
    clear_screen()
    return choice

# 打印文章信息
def print_article(title, link, content):
    print("文章标题：" + title)
    print("文章链接：" + link)
    print("                                          ")
    print("文章内容：" + content)
    print("                                          ")
    print("        ---------------操作----------------")
    print("        请选择：                           ")
    print("        1.  翻译成中文[t]")
    print("        2.  返回新闻列表[r]")
    print('        ----------------------------------')
    print("                                           ")
    choice = input("请输入：")
    clear_screen()
    return choice

# 翻译文章时
def print_tran_article(title, link, content):
    print("文章标题：" + title)
    print("文章链接：" + link)
    print("                                          ")
    print("文章翻译内容：" + content)
    print("                                          ")
    print("        ---------------操作----------------")
    print("        请选择：                           ")
    print("        1.  返回原文[o]")
    print("        2.  总结新闻[s]")
    print('        ----------------------------------')
    print("                                           ")
    choice = input("请输入：")
    # 输入后清屏
    clear_screen()
    return choice

# 总结新闻时
def print_sum_article(title, link, content):
    print("文章标题：" + title)
    print("文章链接：" + link)
    print("                                          ")
    print("总结为：" + content)
    print("                                          ")
    print("        ---------------操作----------------")
    print("        请选择：                           ")
    print("        1.  返回原文[o]")
    print("        2.  总结新闻[s]")
    print('        ----------------------------------')
    print("                                           ")
    choice = input("请输入：")
    clear_screen()
    return choice


# 空执行函数
def do_return():
    return




# if __name__ == "__main__":
#     main()


if __name__ == "__main__":
    # 创建一个线程用于获取和打印新闻
    # NEWS_THREAD = threading.Thread(target=get_news_periodically)
    # 创建一个线程用于主函数
    # MAIN_THREAD = threading.Thread(target=main)
    # 创建一个线程用于输出
    # OUTPUT_THREAD = threading.Thread(target=output_data_periodically)
    LONG_PROCESS = multiprocessing.Process(target=output_data_periodically)

    # 将线程设置为守护线程
    # OUTPUT_THREAD.setDaemon(True)

    # NEWS_THREAD.start()
    # MAIN_THREAD.start()
    # OUTPUT_THREAD.start()
    LONG_PROCESS.start()

    # NEWS_THREAD.join()
    # MAIN_THREAD.join()
    # OUTPUT_THREAD.join()
    LONG_PROCESS.join()



    