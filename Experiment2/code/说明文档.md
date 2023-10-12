## 实验二 -- 新闻推送应用



### 实验要求

编写新闻推送程序，具体要求如下：

1. 每隔10分钟自动从yahoo新闻的生活rss获取最新的十条新闻
2. 将获取的新闻显示到屏幕中，用户可以输入 1-10 的数字然后按回车显示新闻内容
3. 在新闻内容画面，按 t 回车可以将新闻翻译成中文。
4. 在新闻内容画面，按 q 回车返回新闻列表。


### 实验所需第三方库
feedparser==6.0.10
requests==2.31.0
beautifulsoup4==4.12.2
schedule==1.2.1

### 实验环境
Linux系统 Python3.8.9

### 实验步骤

1. 对于第一步，可以通过schedule库或者通过开启一个线程进行sleep实现。
我选择在使用schedule库的基础上开启线程，核心代码如下，这样通过控制STOP_LOOP也能过方便的结束线程

``` py
# 创建一个线程用于获取和打印新闻
NEWS_THREAD = threading.Thread(target=get_news_periodically)
NEWS_THREAD.start()
# 捕获新闻列表的线程
def get_news_periodically():
    schedule.every(600).seconds.do(set_news)
    while not STOP_LOOP:
        schedule.run_pending()
        time.sleep(1)
```

2. 对于第二步，我首先使用feedparser库进行爬取，但在爬取的过程中，我发现会因为网络的问题有时候会导致链接不上，
于是进行了一次封装，超时以及报错重新尝试爬取。然后等待用户的输入，并做相应的事情即可。
``` py
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
```

3. 对于第三步，我选择使用百度翻译开放平台提供的api进行，代码是直接使用了官方文档提供的案例

4. 对于三四步，我利用了映射进行了用户操作的选择，这样或许会更优雅一些，由于有的映射值函数对象需要携带参数，所以使用了functools库

``` py
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
```

### 实验心得
通过这次实验，学习到了关于rss的知识，并且学会了如何使用第三方开放平台去协助我们的开发。对服务端编程也有了更深一步的了解。