import os
import functools
import threading
import feedparser
import http.client
import requests
from bs4 import BeautifulSoup
import random
from hashlib import md5
import sys
import schedule
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# 程序停止标志符
STOP_LOOP = False

# 新闻列表
NEWS_LIST = []

# 爬取新闻的线程
NEWS_THREAD = ''

def main():
    global STOP_LOOP
    global NEWS_LIST
    global NEWS_THREAD

    # 确保能够获取第一的新闻列表
    NEWS_LIST = get_news()

    # 创建一个线程用于获取和打印新闻
    NEWS_THREAD = threading.Thread(target=get_news_periodically)
    NEWS_THREAD.start()

    while not STOP_LOOP:

        print_news(NEWS_LIST)
        # 用户输入
        choice = get_choice_number()
        # 根据输入进行选择
        swich_choice_list(choice, NEWS_LIST)

# 捕获新闻列表的线程
def get_news_periodically():
    schedule.every(600).seconds.do(set_news)
    while not STOP_LOOP:
        schedule.run_pending()
        time.sleep(1)

# 设置新闻列表
def set_news():
    global NEWS_LIST
    NEWS_LIST = get_news()

# 获取新闻列表
def get_news():
    news = parser_rss()
    return news

# 在屏幕上打印新闻数据
def print_news(news):
    index = 1
    for new_item in news:
        print(str(index) + '. ' + new_item['title'])
        index += 1



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


# 清屏
def clear_screen():
    os.system('clear')

# 退出程序
def exit():
    global STOP_LOOP
    global NEWS_THREAD
    STOP_LOOP = True
    NEWS_THREAD.join()
    sys.exit()

# 在文章列表界面根据用户输入进行不同操作
def swich_choice_list(choice, news):

    try: 
        # 1 - 10
        index = int(choice)
         # 获取展示的文章内容
        title = news[index - 1]['title']
        link = news[index - 1]['link']
        content = get_texts(link)

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


# 翻译
def tran_content(title, link, content):
    res_tran = baiduTran(content)
    new_choice = print_article(title, link, res_tran)
    swich_choice_article(new_choice, title, link, content)

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
    return choice


# 空执行函数
def do_return():
    return


# 防止连接报错
def parse_rss_with_retry(rss_url, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            d = feedparser.parse(rss_url)
            return d.entries  # 返回解析后的数据条目
        except http.client.IncompleteRead:
            print("IncompleteRead error. Retrying...")
            retries += 1
    print(f"Failed to parse RSS after {max_retries} retries.")
    return None  # 如果多次重试后仍然失败，返回None或采取其他处理方式


def parser_rss():
    rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml'
    parsed_data = parse_rss_with_retry(rss_url)

    if parsed_data:
        items = []
        num = 10

        for item in parsed_data[:num]:
            if 'title' in item and 'link' in item:
                title = item.title
                link = item.link
                items.append({
                    'title': title,
                    'link': link,
                })
        return items
    else:
        return []  # 或者采取其他适当的处理方式


# 爬取内容
def get_texts(url):

    text = ''
    for i in range(1, 100):
        new_url = reset_url(url, i)
        # 发送 GET 请求
        response = requests.get(new_url)

        # 检查响应状态码
        if response.status_code == 200:
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")

            elements = soup.find_all(class_='sc-fVnRWS bfa-dbI')

            for element in elements:
                text += element.text

        else:
            return text


# 重写url，为了在多页情况下爬取到完整的内容
def reset_url(url, index):
    # 解析URL
    parsed_url = urlparse(url)

    # 解析查询参数
    query_params = parse_qs(parsed_url.query)

    # 修改参数值为index
    query_params['page'] = [index]

    # 移除source参数
    if 'source' in query_params:
        del query_params['source']

    # 构建新的查询字符串
    new_query_string = urlencode(query_params, doseq=True)

    # 用新的查询字符串替换原始URL中的查询部分
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query_string, parsed_url.fragment))

    return new_url


# 调用百度翻译
def baiduTran(strs):
    appid = '' # 填写你的哦
    appkey = '' # 填写你的哦

    from_lang = 'jp'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    query = strs

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    res = r.json()

    res_str = ''

    for str_item in res['trans_result']:
        res_str += str_item['dst']

    return res_str



if __name__ == "__main__":
    main()