import req
from enum import Enum, auto
import output
from functools import partial
import curses
import tran
import summarize

# 状态机
class State(Enum):
    News_List = auto()
    News_Detail = auto()
    News_Breed = auto()
    News_Option = auto()
    News_Tran = auto()
    News_Summarize = auto()

# 键盘映射
class keyboard(Enum):
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT
    KEY_CONFIRM = 10
    BACKSPACE = 127
    BACKSPACE_DB = 8
    BACKSPACE_ON_CURSES = curses.KEY_BACKSPACE


# 当前状态机的状态
current_state = State.News_List
# 位置信息
cursor_x = 0
cursor_y = 1
screen_height = 0
screen_width = 0
option_y = 1
arrow_y = 1 # 箭头的位置
breed_y = 1 # 新闻类型的箭头位置
start_row = 0 # 可视区
end_row = 0 # 可视区
# 运行状态
is_running_sys = True
is_running_news_list = True
is_running_news_detial = True
is_running_news_tran = True
is_running_news_summarize = True
is_running_news_option = True
# 新闻配置
selected_news_content = ''
selected_news_content_tran = ''
news_list = []
news_list_len = 10
page_no = 0 # 当前页号
page_size = 0 # 当前页码
rss_url = 'https://news.yahoo.co.jp/rss/categories/life.xml'
news_type = "生活"

def init(stdscr):
    global screen_height
    global screen_width
    global page_size
    global current_state
    curses.curs_set(0)

    stdscr.clear()
    stdscr.refresh()
    stdscr.scrollok(True)
    while is_running_sys:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        screen_width = width
        screen_height = height
        page_size = height - 6

        # 切换状态
        if current_state == State.News_List:
            display_news_list(stdscr)
        elif current_state == State.News_Detail:
            display_news_details(stdscr)
        elif current_state == State.News_Tran:
            display_news_tran(stdscr)
        elif current_state == State.News_Summarize:
            display_news_summarize(stdscr)
        elif current_state == State.News_Option:
            display_news_option(stdscr)
        

        stdscr.refresh()

# 展示新闻列表
def display_news_list(stdscr):
    global cursor_x, cursor_y, arrow_y
    global news_list, news_list_len
    global screen_width, screen_height
    global is_running_news_list
    global rss_url
    global start_row, end_row
    global page_no
    global news_type
    page_no = 0
    is_running_news_list = True
    news_list = req.parser_rss(rss_url, news_list_len)
    arrow_y = 1
    start_row = 0
    end_row = 0
    cursor_y = 1


    while is_running_news_list:
        stdscr.clear()
        ops_line = 0
        # 计算可见区域
        end_row = min(start_row + screen_height - 5, len(news_list))
        
        for line_index in range(start_row, end_row):
            try:
                display_text = f"{line_index + 1}. {news_list[line_index]['title'][:screen_width // 2 - 4]}"
                stdscr.addstr(line_index - start_row + 1, 2, display_text)
                ops_line = line_index
            except curses.error:
                pass

        # 添加在第一行
        add_title_to_head(stdscr, "News List" + news_type)
        # 添加在最后一行
        add_help_to_bottom(stdscr, "help ↑:上一条新闻; ↓:下一条新闻; →:新闻详情; ←: 退出程序")
        # 添加日志
        console_log(stdscr, "当前所处行: " + str(cursor_y))
        # 添加opstion
        stdscr.addstr(end_row - start_row + 2, 2, "Option")

        # 绘制"->"在前两列
        stdscr.addstr(arrow_y, 0, "->")

        news_list_choice(stdscr)

        stdscr.refresh()


        
# 在新闻列表下等待用户选择
def news_list_choice(stdscr):
    key = stdscr.getch()
   
    # 用户选择的映射
    user_choice_map = {
        keyboard.KEY_UP.value: up_cursor,
        keyboard.KEY_DOWN.value: down_cursor,
        keyboard.KEY_LEFT.value: exit_sys,
        keyboard.KEY_RIGHT.value: handle_right_on_list
    }

    if key in list(user_choice_map.keys()): 
        user_choice_map[key]()


# 处理新闻列表界面下的right操作
def handle_right_on_list():
    global cursor_y, arrow_y
    global is_running_news_list
    global news_list_len
    global start_row, end_row
    if 1 <= arrow_y <= end_row - start_row:
        # 展示新闻列表
        is_running_news_list = False
        change_state(State.News_Detail)
    elif arrow_y == end_row - start_row + 2:
        is_running_news_list = False
        change_state(State.News_Option)
        

# 展示新闻详情页面
def display_news_details(stdscr):
    global news_list
    global cursor_y
    global is_running_news_detial
    global page_no, page_size
    global selected_news_content
    page_no = 0
    is_running_news_detial = True
    news = news_list[cursor_y - 1]
    news_content = req.get_text(news['link'])
    selected_news_content = news_content
    pages = output.paginate_text(news_content, page_size)
    while is_running_news_detial:
        stdscr.clear()
        # 当前页内容
        page = pages[page_no]
        # 添加在第一行
        add_title_to_head(stdscr, "新闻详情页")
        # 添加在最后一行
        add_help_to_bottom(stdscr, "help ←: 新闻列表 →:新闻翻译 ↓:下一页 ↑:上一页")
        # 添加输出信息
        console_log(stdscr, "当前页号为: " + str(page_no))
        stdscr.addstr(1, 0, "新闻标题: " + news['title'])
        stdscr.addstr(2, 0, "新闻链接: " + news['link'])
        # 绘制文本内容
        lines = page.splitlines()
        for i, line in enumerate(lines):
            stdscr.addstr(i + 3, 0, line)

        news_details_choice(stdscr, len(pages))

        stdscr.refresh()


# 在新闻详情界面下等待用户的选择
def news_details_choice(stdscr, pages_len):
    key = stdscr.getch()
    # 携带默认参数的函数对象
    change_page_no_with_default = partial(change_page_no, key, pages_len)
    # 用户选择的映射
    user_choice_map = {
        keyboard.KEY_UP.value: change_page_no_with_default,
        keyboard.KEY_DOWN.value: change_page_no_with_default,
        keyboard.KEY_LEFT.value: back_to_news_list,
        keyboard.KEY_RIGHT.value: handle_tran_news
    }
    
    if key in list(user_choice_map.keys()): 
        user_choice_map[key]()

# 翻译新闻
def handle_tran_news():
    global current_state
    global is_running_news_detial
    global page_no
    page_no = 0
    is_running_news_detial = False
    change_state(State.News_Tran)

# 修改页号
def change_page_no(keyboard_key, pages_len):
    global page_no
    if keyboard_key == keyboard.KEY_DOWN.value:
        page_no = min(page_no + 1, pages_len - 1)
    elif keyboard_key == keyboard.KEY_UP.value:
        page_no = max(page_no - 1, 0)

# 返回新闻列表
def back_to_news_list():
    global is_running_news_detial
    global is_running_news_tran
    global is_running_news_summarize
    global is_running_news_option
    global page_no
    page_no = 0
    is_running_news_detial = False
    is_running_news_tran = False
    is_running_news_summarize = False
    is_running_news_option = False
    change_state(State.News_List)

# 展示新闻翻译详情界面
def display_news_tran(stdscr):
    global is_running_news_tran
    global page_no, page_size
    global cursor_y
    global news_list
    global selected_news_content, selected_news_content_tran
    page_no = 0
    is_running_news_tran = True
    news = news_list[cursor_y - 1]
    news_tran = tran.baiduTran(selected_news_content)
    selected_news_content_tran = news_tran
    news_tran = news_tran.replace("。", "。\n")
    pages = output.paginate_text(news_tran, page_size)
    while is_running_news_tran:
        stdscr.clear()
        page = pages[page_no]
        add_title_to_head(stdscr, "新闻翻译页")
        add_help_to_bottom(stdscr, "help ←: 新闻列表  ↑:新闻详情   →:新闻归纳  ↓:下一页")
        console_log(stdscr, "当前页号为: " + str(page_no))

        stdscr.addstr(1, 0, "新闻标题: " + news['title'])
        stdscr.addstr(2, 0, "新闻链接: " + news['link'])

        # 绘制文本内容
        lines = page.splitlines()
        for i, line in enumerate(lines):
            stdscr.addstr(i + 3, 0, line)
        
        news_tran_choice(stdscr, len(pages))
        stdscr.refresh()

# 在翻译界面等待用户的选择
def news_tran_choice(stdscr, pages_len):
    key = stdscr.getch()

    change_page_no_width_default = partial(change_page_no, key, pages_len)
    # 映射
    user_choice_map = {
        keyboard.KEY_DOWN.value: change_page_no_width_default,
        keyboard.KEY_RIGHT.value: handle_news_summarize,
        keyboard.KEY_LEFT.value: back_to_news_list,
        keyboard.KEY_UP.value: back_to_news_detail
    }
    if key in list(user_choice_map.keys()): 
        user_choice_map[key]()

# 返回新闻详情界面
def back_to_news_detail():
    global is_running_news_tran
    global is_running_news_summarize
    global page_no
    page_no = 0
    is_running_news_tran = False
    is_running_news_summarize = False
    change_state(State.News_Detail)


def handle_news_summarize():
    global is_running_news_tran
    is_running_news_tran = False
    change_state(State.News_Summarize)


# 展示新闻总结界面
def display_news_summarize(stdscr):
    global is_running_news_summarize
    global cursor_y
    global selected_news_content_tran
    global page_no
    page_no = 0
    is_running_news_summarize = True
    news = news_list[cursor_y - 1]
    news_summarize = summarize.get_content_summarize(selected_news_content_tran)
    while is_running_news_summarize:
        stdscr.clear()
        add_title_to_head(stdscr, "新闻总结页")
        add_help_to_bottom(stdscr, "help ←:新闻列表;  ↑:新闻详情   ↓:新闻翻译")
        stdscr.addstr(1, 0, "新闻标题: " + news['title'])
        stdscr.addstr(2, 0, "新闻链接: " + news['link'])
        stdscr.addstr(3, 0, "新闻总结: " + news_summarize)

        news_summarize_choice(stdscr)
        stdscr.refresh()


# 新闻总结界面下的用户选择
def news_summarize_choice(stdscr):
    key = stdscr.getch()
    # 映射
    user_choice_map = {
        keyboard.KEY_DOWN.value: back_to_news_tran,
        keyboard.KEY_UP.value: back_to_news_detail,
        keyboard.KEY_LEFT.value: back_to_news_list
    }
    if key in list(user_choice_map.keys()): 
        user_choice_map[key]()

# 返回新闻翻译界面
def back_to_news_tran():
    global is_running_news_summarize
    global page_no
    page_no = 0
    is_running_news_summarize = False
    change_state(State.News_Tran)


# 展示option操作界面
def display_news_option(stdscr):
    global is_running_news_option
    global option_y
    is_running_news_option = True

    while is_running_news_option:
        stdscr.clear()

        draw_news_options(stdscr)
        
        news_option_choice(stdscr)
        stdscr.refresh()

# 在新闻设置界面等待用户选择
def news_option_choice(stdscr):
    key = stdscr.getch()
    handle_right_on_option_with_default = partial(handle_right_on_option, stdscr)
    user_choice_map = {
        keyboard.KEY_DOWN.value: down_cursor_on_option,
        keyboard.KEY_UP.value: up_cursor_on_option,
        keyboard.KEY_RIGHT.value: handle_right_on_option_with_default
    }
    if key in list(user_choice_map.keys()): 
        user_choice_map[key]()

# 绘制新闻操作下的基本内容
def draw_news_options(stdscr):
    global option_y
    add_title_to_head(stdscr, "Option")
    add_help_to_bottom(stdscr, "help ↑:上一条设置 ↓:下一条设置 →:修改设置")
    console_log(stdscr, "当前行号为: " + str(option_y))

    stdscr.addstr(1, 2, "1. Set News Count")
    stdscr.addstr(2, 2, "2. Select News Type")

    # 绘制"->"在前两列
    stdscr.addstr(option_y, 0, "->")


# 修改新闻数量
def set_news_list_len(stdscr):
    global news_list_len
    stdscr.addstr(4, 0, "Input News Count: ")
    input_str = ''
    while True:
        ops_key = stdscr.getch()
        stdscr.clear()
        draw_news_options(stdscr)

        if ops_key == keyboard.KEY_CONFIRM.value:  # 用户按下回车键
            try:
                # 尝试将用户输入的字符串转换为整数，并更新 news_list_len
                news_list_len = int(input_str)
                back_to_news_list()
                break
            except ValueError:
                # 如果无法转换为整数，显示错误信息并重置输入字符串
                console_log(stdscr, "Invalid input. Please enter a valid number.")
                input_str = ""
        elif ops_key == keyboard.BACKSPACE.value or ops_key == keyboard.BACKSPACE_DB.value or ops_key == keyboard.BACKSPACE_ON_CURSES.value:  # 用户按下退格键
            # 删除最后一个字符
            input_str = input_str[:-1]
        elif ops_key >= 48 and ops_key <= 57:  # 用户输入数字字符（ASCII码 48-57 代表数字 0-9）
            input_str += chr(ops_key)
        else:
            console_log(stdscr, "Invalid input. Please enter a valid number.")

        # 清除原有内容，显示用户输入
        stdscr.addstr(4, 0, "Input News Count: " + input_str)
        stdscr.refresh()

# 在opstion界面下右击
def handle_right_on_option(stdscr):
    global option_y
    if option_y == 1:
        set_news_list_len(stdscr)
    elif option_y == 2:
        change_news_breed(stdscr)

# 选择新闻类型
def change_news_breed(stdscr):
    global rss_url
    global breed_y
    global screen_height
    global start_row, end_row
    global news_type
    breeds = req.get_all_breed()
    breed_y = 1
    arrow_breed_y = 1
    start_row = 0
    
    while True:
        stdscr.clear()
        end_row = min(start_row + screen_height - 3, 9)
        add_title_to_head(stdscr, "新闻类型选择")
        add_help_to_bottom(stdscr, "help →:选择当前类型")
        for breed_index in range(min(len(breeds), screen_height - 2)):
            stdscr.addstr(breed_index + 1, 2, str(breed_index + start_row + 1).zfill(2) + ". " + breeds[breed_index + start_row - 1]['name'])
        stdscr.addstr(arrow_breed_y, 0, "->")
        console_log(stdscr, "当前的新闻序号为: " + str(breed_y))
        key = stdscr.getch()

        if key == keyboard.KEY_UP.value:
            if breed_y > 1:
                if 1 < arrow_breed_y <= end_row - start_row:
                    arrow_breed_y -= 1
                breed_y -= 1
                if breed_y <= start_row:
                    start_row -= 1
                
        elif key == keyboard.KEY_DOWN.value:
            if breed_y < len(breeds):
                if arrow_breed_y == end_row - start_row:
                    start_row += 1
                if arrow_breed_y < end_row - start_row:
                    arrow_breed_y += 1
                breed_y += 1
        elif key == keyboard.KEY_RIGHT.value:
            rss_url = breeds[breed_y - 2]['url']
            news_type = breeds[breed_y - 2]['name']
            back_to_news_list()
            break

# 上移动 -> 操作界面
def up_cursor_on_option():
    global option_y
    if option_y > 1:
        option_y -= 1

# 下移动 -> 操作界面
def down_cursor_on_option():
    global option_y
    if option_y < 2:
        option_y += 1

# 上移 -> 新闻列表
def up_cursor():
    global cursor_y, arrow_y
    global start_row, end_row
    global screen_height
    if cursor_y > 1:
        if 1 < arrow_y <= end_row - start_row:
            arrow_y -= 1
        elif arrow_y == end_row - start_row + 2:
            arrow_y -= 2
            cursor_y -= 1

        cursor_y -= 1
        if cursor_y <= start_row:
            start_row -= 1
    
        
# 下移 -> 新闻列表
def down_cursor():
    global cursor_y, arrow_y
    global news_list
    global start_row, end_row
    global screen_height
    if cursor_y <= len(news_list) + 1:
        if end_row - start_row + 2 == arrow_y:
            start_row += 1
        if arrow_y < end_row - start_row:
            arrow_y += 1
        elif arrow_y == end_row - start_row:
            arrow_y += 2
            cursor_y += 1
        
        cursor_y += 1
        


# 添加到最后一行
def add_help_to_bottom(stdscr, str):
    global screen_height
    stdscr.addstr(screen_height - 1, 0, str)


# 添加到第一行
def add_title_to_head(stdscr, str):
    stdscr.addstr(0, 0, str)

# 输出日志
def console_log(stdscr, str):
    global screen_height
    stdscr.addstr(screen_height - 2, 0, "输出日志: " + str)


# 退出程序
def exit_sys():
    global is_running_news_list
    global is_running_sys
    is_running_sys = False
    is_running_news_list = False

# 切换状态
def change_state(new_state):
    global current_state
    current_state = new_state