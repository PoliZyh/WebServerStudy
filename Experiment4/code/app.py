import curses
import sys
from functools import partial
from enum import Enum

class keyboard(Enum):
    LEFT = ord('h')
    DOWN = ord('j')
    UP = ord('k')
    RIGHT = ord('l')
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT
    INSERT = ord('i')
    SAVE = ord('s')
    EXIT = ord('q')
    WRAP = 10
    OUT = 27
    BACKSPACE = 127
    BACKSPACE_DB = 8
    BACKSPACE_ON_CURSES = curses.KEY_BACKSPACE

# 是否为编辑模式
is_editing = False
# 是否退出
is_running = True
# 屏幕可见区域限制
start_row = 0
end_row = 0
screen_height = 0

# 添加文本到屏幕
def add_content_to_stdscr(stdscr, content, cur_pos):
    global start_row
    global end_row

    for line_index in range(start_row, end_row):
        try:
            stdscr.addstr(line_index - start_row, 0, content[line_index])
        except curses.error:
            pass
   
    

# 移动光标
def moving_cursor(key, cur_pos, content):
    global screen_height
    global start_row
    # 左
    if key == keyboard.LEFT.value or key == keyboard.KEY_LEFT.value:
        if cur_pos['cur_col'] == 0:
            return
        cur_pos['cur_col'] -= 1
    # 下
    elif key == keyboard.DOWN.value or key == keyboard.KEY_DOWN.value:
        if cur_pos['cur_row'] >= len(content) - 1:
            return
        cur_pos['cur_row'] += 1
        if cur_pos['cur_row'] - start_row >= screen_height - 1:
            start_row += 1
        if len(content[cur_pos['cur_row']]) <= cur_pos['cur_col']:
            cur_pos['cur_col'] = len(content[cur_pos['cur_row']]) - 1
      
    # 上
    elif key == keyboard.UP.value or key == keyboard.KEY_UP.value:
        if cur_pos['cur_row'] == 0:
            return
        cur_pos['cur_row'] -= 1
        if cur_pos['cur_row'] < start_row:
            start_row -= 1
        if len(content[cur_pos['cur_row']]) <= cur_pos['cur_col']:
            cur_pos['cur_col'] = len(content[cur_pos['cur_row']]) - 1
    # 右
    elif key == keyboard.RIGHT.value or key == keyboard.KEY_RIGHT.value:
        if cur_pos['cur_col'] >= len(content[cur_pos['cur_row']].rstrip()):
            return
        cur_pos['cur_col'] += 1

# 切换模式
def change_mode(key):
    global is_editing
    if key == keyboard.INSERT.value:
        is_editing = True
    elif key == keyboard.OUT.value:
        is_editing = False

# 输入函数
def input_character(content, cur_pos, key):
    if key < 32 or key > 126:
        return
    else:
        content[cur_pos['cur_row']] = content[cur_pos['cur_row']][:cur_pos['cur_col']] + chr(key) + content[cur_pos['cur_row']][cur_pos['cur_col']:]
        cur_pos['cur_col'] += 1

# 保存文本函数
def save_content_to_file(file_name, file_content):
    with open(file_name, 'w') as file:
        cleaned_content = [line.rstrip() for line in file_content]
        file.write('\n'.join(cleaned_content))

# 文本换行
def file_wrap(content, cur_pos):
    global screen_height
    global start_row
    content.insert(cur_pos['cur_row'] + 1, content[cur_pos['cur_row']][cur_pos['cur_col']:])
    content[cur_pos['cur_row']] = content[cur_pos['cur_row']][:cur_pos['cur_col']] + '\n'
    
    cur_pos['cur_row'] += 1
    cur_pos['cur_col'] = 0

    if cur_pos['cur_row'] - start_row >= screen_height - 1:
        start_row += 1

# 退出函数
def exit():
    global is_running
    is_running = False

# 退格函数
def back_space(content, cur_pos):
    # 退格
    current_col = cur_pos['cur_col']
    current_row = cur_pos['cur_row']
    if current_col > 0:
        content[current_row] = content[current_row][:current_col - 1] + content[current_row][current_col:]
        cur_pos['cur_col'] -= 1
    elif current_row > 0:
        cur_pos['cur_col'] = len(content[current_row - 1].rstrip())
        content[current_row - 1] = content[current_row - 1].rstrip() + content.pop(current_row)
        cur_pos['cur_row'] -= 1
    else:
        return

def main(stdscr):
    global is_editing
    global is_running
    global start_row
    global end_row
    global screen_height
    # Clear screen
    # curses.curs_set(0) 
    stdscr.clear()
    stdscr.refresh()
    stdscr.scrollok(True)
    # 文章内容
    file_content = []
    # 光标位置
    pos = {
        'cur_row': 0,
        'cur_col': 0
    }
    

    # 打开文件
    if len(sys.argv) != 2:
        stdscr.addstr(0, 0, "Usage: python vim.py <filename>")
        stdscr.refresh()
        stdscr.getch()
        return

    filename = sys.argv[1]

    # 读取文本
    with open(filename, 'r') as file:
        for line in file:
            file_content.append(line)

    while is_running:
        stdscr.clear()
        # 获取屏幕的宽高
        height, width = stdscr.getmaxyx()
        screen_height = height - 2
        # 计算可见区域
        end_row = min(start_row + height - 2, len(file_content))

        if is_editing:
            # 编辑模式
            stdscr.addstr(height - 1, 0, "EDIT MODE - Press 'Esc' to exit")
            add_content_to_stdscr(stdscr, file_content, pos)
            # 修改光标位置
            stdscr.move(pos['cur_row'] - start_row, pos['cur_col'])

            key = stdscr.getch()
            # 携带参数的函数对象
            moving_cursor_with_default = partial(moving_cursor, key, pos, file_content)
            change_mode_with_default = partial(change_mode, key)
            file_wrap_with_default = partial(file_wrap, file_content, pos)
            back_space_with_default = partial(back_space, file_content, pos)

            edit_map = {
                keyboard.KEY_LEFT.value: moving_cursor_with_default,
                keyboard.KEY_DOWN.value: moving_cursor_with_default,
                keyboard.KEY_UP.value: moving_cursor_with_default,
                keyboard.KEY_RIGHT.value: moving_cursor_with_default,
                keyboard.OUT.value: change_mode_with_default,
                keyboard.WRAP.value: file_wrap_with_default,
                keyboard.BACKSPACE.value: back_space_with_default,
                keyboard.BACKSPACE_ON_CURSES.value: back_space_with_default,
                keyboard.BACKSPACE_DB.value: back_space_with_default
            }

            if key in list(edit_map.keys()):
                edit_map[key]()
            else:
                # 普通输入
                input_character(file_content, pos, key)
            
            
            
        else:
            # 普通模式
            stdscr.addstr(height - 1, 0, "NORMAL MODE - Press 'i' to enter edit mode and 's' to save and 'q' to exit")
            add_content_to_stdscr(stdscr, file_content, pos)
            # 修改光标
            stdscr.move(pos['cur_row'] - start_row, pos['cur_col'])

            key = stdscr.getch()
            # 携带参数的函数对象
            moving_cursor_with_default = partial(moving_cursor, key, pos, file_content)
            change_mode_with_default = partial(change_mode, key)
            save_content_to_file_with_default =partial(save_content_to_file, filename, file_content)

            normal_map = {
                keyboard.LEFT.value: moving_cursor_with_default,
                keyboard.DOWN.value: moving_cursor_with_default,
                keyboard.UP.value: moving_cursor_with_default,
                keyboard.RIGHT.value: moving_cursor_with_default,
                keyboard.INSERT.value: change_mode_with_default,
                keyboard.SAVE.value: save_content_to_file_with_default,
                keyboard.EXIT.value: exit
            }

            if key not in list(normal_map.keys()):
                continue

            normal_map[key]()



        stdscr.refresh()
        


if __name__ == '__main__':
    curses.wrapper(main)