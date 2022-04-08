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

    parser = argparse.ArgumentParser(description="snake game", add_help=False)
    parser.add_argument(
        "--help", "-h", action="help", help="show this help message and exit"
    )
    parser.add_argument("--cheat", type=int, help=argparse.SUPPRESS)
    parser.add_argument(
        "--black-white",
        "--bw",
        action="store_true",
        help="disable colors (black and white only)",
    )
    parser.add_argument("--rows", "-r", type=int, help="set rows")
    parser.add_argument("--columns", "-c", type=int, help="set columns")
    parser.add_argument(
        "--color-snake",
        choices=["black", "white", "red", "green", "yellow", "blue", "magenta", "cyan"],
        default="green",
        help="set snake color",
    )
    parser.add_argument(
        "--color-food",
        choices=["black", "white", "red", "green", "yellow", "blue", "magenta", "cyan"],
        default="yellow",
        help="set food color",
    )
    parser.add_argument(
        "--color-bg",
        choices=["black", "white", "red", "green", "yellow", "blue", "magenta", "cyan"],
        default="white",
        help="set background color",
    )
    parser.add_argument(
        "--char-snake", type=str, default="#", help="set snake character"
    )
    parser.add_argument(
        "--char-head", type=str, default="#", help="set head character"
    )
    parser.add_argument("--char-food", type=str, default="*", help="set food character")
    parser.add_argument(
        "--char-bg", type=str, default=".", help="set background character"
    )
    parser.add_argument("--speed", "-s", type=int, default=10, help="set speed")
    args = parser.parse_args()

    stdscr = curses.initscr()
    curses.start_color()
    curses.cbreak()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.noecho()
    stdscr.nodelay(True)
    stdscr.timeout(1000 // args.speed)
    stdscr.keypad(1)

    colors = {
        "black": curses.COLOR_BLACK,
        "white": curses.COLOR_WHITE,
        "red": curses.COLOR_RED,
        "green": curses.COLOR_GREEN,
        "yellow": curses.COLOR_YELLOW,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA,
        "cyan": curses.COLOR_CYAN,
    }

    curses.init_pair(1, -1 if args.black_white else colors[args.color_bg], -1)
    curses.init_pair(2, -1 if args.black_white else colors[args.color_snake], -1)
    curses.init_pair(3, -1 if args.black_white else colors[args.color_food], -1)

    ROWS = args.rows or stdscr.getmaxyx()[0] - 1
    COLS = args.columns or stdscr.getmaxyx()[1] - 1
    CHAR_SNAKE = args.char_snake
    CHAR_HEAD = args.char_head
    CHAR_FOOD = args.char_food
    CHAR_BG = args.char_bg
    IS_LARGE_ENOUGH = COLS > 50

    snake = [[5, 5], [5, 4], [5, 3]]
    score = len(snake)
    if args.cheat:
        for i in range(args.cheat):
            snake.append([5, 3])
        score += args.cheat
    food = [ROWS // 2, COLS // 2]
    direction = 100
    paused = False
    body = [*snake[0]]

    for x in range(ROWS):
        for y in range(COLS):
            stdscr.addstr(x, y, CHAR_BG, curses.color_pair(1))

    for i, _ in enumerate(snake):
        stdscr.addstr(*snake[i], CHAR_HEAD, curses.color_pair(2))

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
            stdscr.addstr(*body, CHAR_SNAKE, curses.color_pair(2))
            body = [*snake[0]]
            stdscr.addstr(*snake[0], CHAR_HEAD, curses.color_pair(2))
        stdscr.addstr(
            ROWS, 49 if IS_LARGE_ENOUGH else 7, str(score), curses.color_pair(1)
        )
        stdscr.refresh()


if __name__ == "__main__":
    print(f"Game over: {main()}")
