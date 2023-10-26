#coding=utf-8
import json
from datetime import datetime, timedelta
import os
import req
import queue

# 序号
index = 1
# 当前已经写入的links
cur_links = []
# 当前的时间
cur_hour = -1
# log
log_index = 1
# 是否需要刷新
need_refresh = False
# 先进先出的队列，表示之前的link
last_links = queue.Queue()
# 是否为第一次写入
is_first = True

# 输出为json
def output(data): 
    data = format_data(data)
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取当前日期作为文件夹名
    current_date = datetime.now().strftime('%Y-%m-%d-%H')
    # 构建文件路径
    file_path = os.path.join(script_dir, 'data', current_date, 'index.json')
    # 构建文件夹路径
    folder_path = os.path.join(script_dir, 'data', current_date)
    # 确保文件夹存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 使用 'with' 语句打开文件，并将数据写入文件
    # with open(file_path, 'w', encoding='utf-8') as json_file:
    #     json.dump(data, json_file, ensure_ascii=False, indent=4)
    if os.path.exists(file_path):
        # 如果文件已经存在，就读取已有的 JSON 数据
        with open(file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        
        # 合并现有数据和新数据
        existing_data.extend(data)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    else:
        # 如果文件不存在，就创建一个新文件
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)



def format_data(data):
    global index

    res_list = []
    for item in data:
        # 将时间字符串解析为datetime对象
        time_obj = datetime.strptime(item['date'], "%a, %d %b %Y %H:%M:%S %Z")
        # 将datetime对象转化为中国的本地时间
        china_time = time_obj + timedelta(hours=8)
        # 将datetime对象格式化为指定的格式
        formatted_time = china_time.strftime("%Y年%m月%d日 %H:%M")

        res_obj = {
            "序号": str(index).rjust(2, '0'),
            "新闻标题": item['title'],
            "发布时间": formatted_time,
            "新闻内容": item['content']
        }

        res_list.append(res_obj)
        index += 1

    return res_list


def get_all_cur_news():
    global index
    global cur_links
    global cur_hour
    global log_index
    global need_refresh
    global last_links
    global is_first

    # 需要新增的新闻列表
    need_add_news = []

    need_refresh = False
    # 判断当前的时间 不相同则更新所有的全局变量
    now = datetime.now()
    current_hour = now.hour

    if current_hour != cur_hour:
        cur_hour = current_hour
        index = 1
        need_refresh = True
        # cur_links = []

    # 获取当前网站上的news
    data = req.parser_rss_all()

    # 对比data的link和cur_news中已有的link => 相同则不放入cur_news
    last_links_list = list(last_links.queue)
    for item in data:
        if item['link'] not in cur_links and item['link'] not in last_links_list:
            cur_links.append(item['link'])
            need_add_news.append(item)

    if need_refresh:
        # 第一次写入需要讲所有写入
        if is_first:
            for link in cur_links:
                last_links.put(link)
            is_first = False
        else:
             # 修改之前的links
            for link in cur_links:
                if last_links.qsize() > 100:
                    last_links.get()
                last_links.put(link)
        # 修改当前的links
        cur_links = []



    # 爬取所有content
    for item in need_add_news:
        # print('start' + str(log_index))
        content = req.get_text(item['link'])
        item['content'] = content
        log_index += 1


    return need_add_news

def main():
    data = get_all_cur_news()
    output(data)


