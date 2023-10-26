import curses
import sys

def main(stdscr):
    # 设置终端
    curses.curs_set(0)  # 隐藏光标
    stdscr.clear()
    stdscr.refresh()
    stdscr.scrollok(True)

    # 打开文件
    if len(sys.argv) != 2:
        stdscr.addstr(0, 0, "Usage: python vim.py <filename>")
        stdscr.refresh()
        stdscr.getch()
        return

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            content = file.readlines()
    except FileNotFoundError:
        content = []

    # 初始化状态
    is_editing = False
    current_row = 0
    current_col = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if is_editing:
            # 编辑模式
            stdscr.addstr(0, 0, "EDIT MODE - Press 'Esc' to exit and 's' to save")
            for i, line in enumerate(content):
                if i == current_row:
                    stdscr.addstr(i + 1, 0, line)
                else:
                    stdscr.addstr(i + 1, 0, line.rstrip())

            stdscr.move(current_row + 1, current_col)

            key = stdscr.getch()
            if key == 27:  # 27 对应于 Esc 键
                # 退出编辑模式
                is_editing = False
            elif key == ord('s'):
                # 保存文件
                with open(filename, 'w') as file:
                    file.writelines(content)
                is_editing = False
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(content) - 1:
                current_row += 1
            elif key == curses.KEY_LEFT and current_col > 0:
                current_col -= 1
            elif key == curses.KEY_RIGHT and current_col < len(content[current_row]):
                current_col += 1
            elif key == 10:
                # 换行
                new_line = content[current_row][current_col:]
                content[current_row] = content[current_row][:current_col]
                content.insert(current_row + 1, new_line)
                current_row += 1
                current_col = 0
            elif key == 127:
                # 退格
                if current_col > 0:
                    content[current_row] = content[current_row][:current_col - 1] + content[current_row][current_col:]
                    current_col -= 1
                elif current_row > 0:
                    current_col = len(content[current_row - 1])
                    content[current_row - 1] += content.pop(current_row)
                    current_row -= 1
            elif key >= 32 and key <= 126:
                # 输入字符
                content[current_row] = content[current_row][:current_col] + chr(key) + content[current_row][current_col:]
                current_col += 1
        else:
            # 普通模式
            stdscr.addstr(0, 0, "NORMAL MODE - Press 'i' to enter edit mode")
            for i, line in enumerate(content):
                stdscr.addstr(i + 1, 0, line.rstrip())

            key = stdscr.getch()
            if key == ord('i'):
                is_editing = True
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(content) - 1:
                current_row += 1
            elif key == curses.KEY_LEFT and current_col > 0:
                current_col -= 1
            elif key == curses.KEY_RIGHT and current_col < len(content[current_row]):
                current_col += 1

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
import curses
import sys

def main(stdscr):
    # 设置终端
    curses.curs_set(0)  # 隐藏光标
    stdscr.clear()
    stdscr.refresh()
    stdscr.scrollok(True)

    # 打开文件
    if len(sys.argv) != 2:
        stdscr.addstr(0, 0, "Usage: python vim.py <filename>")
        stdscr.refresh()
        stdscr.getch()
        return

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            content = file.readlines()
    except FileNotFoundError:
        content = []

    # 初始化状态
    is_editing = False
    current_row = 0
    current_col = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if is_editing:
            # 编辑模式
            stdscr.addstr(0, 0, "EDIT MODE - Press 'Esc' to exit and 's' to save")
            for i, line in enumerate(content):
                if i == current_row:
                    stdscr.addstr(i + 1, 0, line)
                else:
                    stdscr.addstr(i + 1, 0, line.rstrip())

            stdscr.move(current_row + 1, current_col)

            key = stdscr.getch()
            if key == 27:  # 27 对应于 Esc 键
                # 退出编辑模式
                is_editing = False
            elif key == ord('s'):
                # 保存文件
                with open(filename, 'w') as file:
                    file.writelines(content)
                is_editing = False
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(content) - 1:
                current_row += 1
            elif key == curses.KEY_LEFT and current_col > 0:
                current_col -= 1
            elif key == curses.KEY_RIGHT and current_col < len(content[current_row]):
                current_col += 1
            elif key == 10:
                # 换行
                new_line = content[current_row][current_col:]
                content[current_row] = content[current_row][:current_col]
                content.insert(current_row + 1, new_line)
                current_row += 1
                current_col = 0
            elif key == 127:
                # 退格
                if current_col > 0:
                    content[current_row] = content[current_row][:current_col - 1] + content[current_row][current_col:]
                    current_col -= 1
                elif current_row > 0:
                    current_col = len(content[current_row - 1])
                    content[current_row - 1] += content.pop(current_row)
                    current_row -= 1
            elif key >= 32 and key <= 126:
                # 输入字符
                content[current_row] = content[current_row][:current_col] + chr(key) + content[current_row][current_col:]
                current_col += 1
        else:
            # 普通模式
            stdscr.addstr(0, 0, "NORMAL MODE - Press 'i' to enter edit mode")
            for i, line in enumerate(content):
                stdscr.addstr(i + 1, 0, line.rstrip())

            key = stdscr.getch()
            if key == ord('i'):
                is_editing = True
            elif key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(content) - 1:
                current_row += 1
            elif key == curses.KEY_LEFT and current_col > 0:
                current_col -= 1
            elif key == curses.KEY_RIGHT and current_col < len(content[current_row]):
                current_col += 1

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
