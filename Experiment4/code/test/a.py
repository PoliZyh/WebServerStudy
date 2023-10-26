import curses

def main(stdscr):
    # 初始化终端窗口
    curses.initscr()
    stdscr.clear()

    # 创建一个新窗口
    win = curses.newwin(10, 20, 0, 0)

    # 启用窗口滚动
    win.scrollok(True)

    content = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6", "Line 7", "Line 8", "Line 9", "Line 10"]

    while True:
        win.clear()

        # 显示文本
        for i, line in enumerate(content):
            win.addstr(i, 0, line)

        win.refresh()

        key = win.getch()

        if key == ord('q'):
            break
        elif key == ord('s'):
            # 向上滚动一行
            win.scroll(1)

    # 清理终端窗口
    curses.endwin()

if __name__ == '__main__':
    curses.wrapper(main)
