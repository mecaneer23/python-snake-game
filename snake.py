#!/usr/bin/env python3

try:
    import curses
except ImportError:
    from os import name as osname

    if osname == "nt":
        print(
            "Curses not installed."
            "You can install it with: `pip install windows-curses`"
        )
    exit(1)
import random
import sys
import argparse


def main():
    def end(exit_msg):
        try:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
        except curses.error:
            return "Error in exiting"
        return exit_msg

    parser = argparse.ArgumentParser(description="snake game")
    parser.add_argument("--color", action="store_true", help="enable color mode")
    parser.add_argument("-r", "--rows", type=int, help="set rows")
    parser.add_argument("-c", "--columns", type=int, help="set columns")
    parser.add_argument("--char-snake", type=int, help="set snake character")
    parser.add_argument("--char-food", type=int, help="set food character")
    parser.add_argument("--char-bg", type=int, help="set background character")
    args = parser.parse_args()

    stdscr = curses.initscr()
    curses.start_color()
    curses.cbreak()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.noecho()
    stdscr.nodelay(True)
    stdscr.timeout(100)
    stdscr.keypad(1)

    if args.color:
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
    else:
        curses.init_pair(1, -1, -1)
        curses.init_pair(2, -1, -1)
        curses.init_pair(3, -1, -1)

    ROWS = stdscr.getmaxyx()[0] - 1 or args.rows
    COLS = stdscr.getmaxyx()[1] - 1 or args.columns
    CHAR_SNAKE = "#" or args.char_snake
    CHAR_FOOD = "*" or args.char_food
    CHAR_BG = "." or args.char_bg
    IS_LARGE_ENOUGH = COLS > 50

    snake = [[5, 5], [5, 4], [5, 3]]
    score = 3
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        for i in range(int(sys.argv[1])):
            snake.append([5, 3])
        score += int(sys.argv[1])
    food = [ROWS // 2, COLS // 2]
    direction = 100
    paused = False

    for x in range(ROWS):
        for y in range(COLS):
            stdscr.addstr(x, y, CHAR_BG, curses.color_pair(1))

    for i, _ in enumerate(snake):
        stdscr.addstr(*snake[i], CHAR_SNAKE, curses.color_pair(2))

    stdscr.addstr(*food, CHAR_FOOD, curses.color_pair(3))

    stdscr.addstr(
        ROWS,
        0,
        "Controls: wasd or arrow keys, q to quit | Score: 0"
        if IS_LARGE_ENOUGH
        else "Score: 0",
        curses.color_pair(1),
    )

    while True:
        try:
            next_direction = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return end("Quit")
        direction = direction if next_direction == -1 else next_direction
        new_head = snake[0].copy()
        if direction in (119, 259):  # w | ^
            new_head[0] -= 1
        elif direction in (97, 260):  # a | <
            new_head[1] -= 1
        elif direction in (115, 258):  # s | v
            new_head[0] += 1
        elif direction in (100, 261):  # d | >
            new_head[1] += 1
        elif direction in (113, 27):  # q | esc
            return end(f"Quit, score: {score}")
        else:
            continue
        if not paused:
            snake.insert(0, new_head)
            if snake[0][0] in (ROWS, -1):
                return end(f"Snake out of bounds vertically, score: {score}")
            if snake[0][1] in (COLS, -1):
                return end(f"Snake out of bounds horizontally, score: {score}")
            if snake[0] in snake[1:]:
                return end(f"Snake can't eat itself, score: {score}")
            if snake[0] == food:
                food = None
                while food is None:
                    new_food = [
                        random.randint(0, ROWS - 1),
                        random.randint(0, COLS - 1),
                    ]
                    food = new_food if new_food not in snake else None
                stdscr.addstr(*food, CHAR_FOOD, curses.color_pair(3))
                score += 1
            else:
                stdscr.addstr(*snake.pop(-1), CHAR_BG, curses.color_pair(1))
            stdscr.addstr(*snake[0], CHAR_SNAKE, curses.color_pair(2))
        stdscr.addstr(
            ROWS, 49 if IS_LARGE_ENOUGH else 7, str(score), curses.color_pair(1)
        )
        stdscr.refresh()


if __name__ == "__main__":
    print(f"Game over: {main()}")
