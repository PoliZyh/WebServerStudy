#coding=utf-8
import feedparser
import http.client
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


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


def parser_rss(rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml', num = 10):
    # rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml'
    parsed_data = parse_rss_with_retry(rss_url)

    # 避免超过五十条
    num = min(50, num)

    if parsed_data:
        items = []
        # num = 10

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
    
def parser_rss_all(rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml'):
    # rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml'
    parsed_data = parse_rss_with_retry(rss_url)

    if parsed_data:
        items = []

        for item in parsed_data:
            if 'title' in item and 'link' in item and 'published' in item:
                title = item.title
                link = item.link
                date = item.published
                items.append({
                    'title': title,
                    'link': link,
                    'date': date
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

            # elements = soup.find_all(class_="sc-juNJA-d hRaqMf yjSlinkDirectlink highLightSearchTarget")
            element = soup.find('div', class_='article_body')

            if not element:
                return text


            # for element in elements:
            text += element.get_text()

        else:
            return text

# 仅获取第一页的text
def get_text(url):
    text = ''
    response = requests.get(url)
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.find_all(class_="sc-juNJA-d hRaqMf yjSlinkDirectlink highLightSearchTarget")
        for element in elements:
                text += element.text
        return text
    else:
        return ''

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

# 爬取rss的所有分类和url
# def get_all_breed():
#     url = "https://news.yahoo.co.jp/rss"

#     # 发送GET请求并获取网页内容
#     response = requests.get(url)
#     html_content = response.text

#     # 使用BeautifulSoup解析HTML
#     soup = BeautifulSoup(html_content, "html.parser")

#     # 查找第二个 class 名为 "sc-iVsyfh MnZEn" 的 ul 标签
#     ul_tags = soup.find_all("ul", class_="sc-iVsyfh MnZEn")
#     second_ul = ul_tags[1]  # 第二个 ul 标签

#     # 查找ul标签下的所有li标签
#     li_tags = second_ul.find_all("li")

#     res_breed = []
#     # 遍历每个li标签，提取a标签的href属性和内容
#     for li in li_tags:
#         a_tag = li.find("a")
#         if a_tag:
#             href = a_tag.get("href")
#             content = a_tag.get_text()
#             res_breed.append({
#                 'url': 'https://news.yahoo.co.jp' + href,
#                 'name': content
#             })
#     return res_breed

def get_all_breed():
    res_breed = []
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/domestic.xml',
        'name': '国内'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/world.xml',
        'name': '国際'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/business.xml',
        'name': '経済'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/entertainment.xml',
        'name': 'エンタメ'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/sports.xml',
        'name': 'スポーツ'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/it.xml',
        'name': 'IT'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/science.xml',
        'name': '科学'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/life.xml',
        'name': 'ライフ'
    })
    res_breed.append({
        'url': 'https://news.yahoo.co.jp/rss/categories/local.xml',
        'name': '地域'
    })
    return res_breed