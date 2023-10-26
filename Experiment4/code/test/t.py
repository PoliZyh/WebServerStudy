import curses
import sys
import logging

# 配置日志
logging.basicConfig(filename='vim.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main(stdscr):
    curses.curs_set(1)
    stdscr.refresh()

    if len(sys.argv) < 2:
        stdscr.addstr("Usage: python3 vim.py <filename>\n")
        stdscr.refresh()
        stdscr.getch()
        return

    filename = sys.argv[1]

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.readlines()

    cursor_x, cursor_y = 0, 0
    in_insert_mode = False
    start_row = 0  # 当前可见区域的第一行
    screen_height, screen_width = stdscr.getmaxyx()

    while True:
        stdscr.clear()

        # 计算可见区域
        end_row = min(start_row + screen_height, len(content))

        for i in range(start_row, end_row):
            try:
                stdscr.addstr(i - start_row, 0, content[i])
            except curses.error:
                pass

        stdscr.move(cursor_y - start_row, cursor_x)

        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord('i'):
            in_insert_mode = True
        elif key == 27:  # Escape key
            in_insert_mode = False
        elif in_insert_mode:
            if key == 10:  # Enter key
                content.insert(cursor_y + 1, content[cursor_y][cursor_x:])
                content[cursor_y] = content[cursor_y][:cursor_x] + "\n"
                cursor_y += 1
                cursor_x = 0
            elif key == curses.KEY_LEFT and cursor_x > 0:  # Left arrow
                cursor_x -= 1
            elif key == curses.KEY_DOWN and cursor_y < len(content) - 1:  # Down arrow
                cursor_y += 1
                if cursor_y - start_row >= screen_height - 1:
                    start_row += 1
                if cursor_x >= len(content[cursor_y]):
                    cursor_x = len(content[cursor_y]) - 1
            elif key == curses.KEY_UP and cursor_y > 0:  # Up arrow
                cursor_y -= 1
                if cursor_y < start_row:
                    start_row -= 1
                if cursor_x >= len(content[cursor_y]):
                    cursor_x = len(content[cursor_y]) - 1
            elif key == curses.KEY_RIGHT and cursor_x < len(content[cursor_y]) - 1:  # Right arrow
                cursor_x += 1
            elif key == curses.KEY_BACKSPACE:  # Backspace key
                if cursor_x > 0:
                    content[cursor_y] = content[cursor_y][:cursor_x - 1] + content[cursor_y][cursor_x:]
                    cursor_x -= 1
            elif key != curses.KEY_RIGHT:
                # Handle Chinese characters using UTF-8 encoding
                ch = chr(key)
                if len(ch.encode('utf-8')) == 1:
                    content[cursor_y] = content[cursor_y][:cursor_x] + ch + content[cursor_y][cursor_x:]
                    cursor_x += 1
        elif key == ord('s'):
            logging.info("Content saved to file: %s", content)
            with open(filename, 'w', encoding='utf-8') as file:
                file.writelines(content)
        elif key == ord('h') and not in_insert_mode and cursor_x > 0:  # 'h' key
            cursor_x -= 1
        elif key == ord('j') and not in_insert_mode and cursor_y < len(content) - 1:  # 'j' key
            cursor_y += 1
            if cursor_y - start_row >= screen_height - 1:
                start_row += 1
            if cursor_x >= len(content[cursor_y]):
                cursor_x = len(content[cursor_y]) - 1
        elif key == ord('k') and not in_insert_mode and cursor_y > 0:  # 'k' key
            cursor_y -= 1
            if cursor_y < start_row:
                start_row -= 1
            if cursor_x >= len(content[cursor_y]):
                cursor_x = len(content[cursor_y]) - 1
        elif key == ord('l') and not in_insert_mode and cursor_x < len(content[cursor_y]) - 1:  # 'l' key
            cursor_x += 1

if __name__ == '__main__':
    curses.wrapper(main)
