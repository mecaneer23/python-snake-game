#!/bin/env python3

try:
    import curses
except ImportError:
    from os import name as osname

    if osname == "nt":
        print(
            "Curses not installed. You can install it with: `pip install windows-curses`"
        )
    exit(1)
import time
import random
import os

ROWS = os.get_terminal_size().lines - 1
COLS = os.get_terminal_size().columns - 1
CHAR_SNAKE = "#"
CHAR_FOOD = "*"
CHAR_BG = "."


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Initialize game variables
    snake = [[5, 5], [5, 4], [5, 3]]
    food = [ROWS // 2, COLS // 2]
    direction = 100
    paused = False
    score = 0

    # draw board
    for x in range(ROWS):
        for y in range(COLS):
            stdscr.addstr(x, y, CHAR_BG)

    # draw snake
    for i, _ in enumerate(snake):
        stdscr.addstr(*snake[i], CHAR_SNAKE)

    # draw food
    stdscr.addstr(*food, CHAR_FOOD)

    stdscr.addstr(ROWS, 0, f"Controls: wasd or arrow keys, q to quit | Score: 0")

    # main loop
    while True:
        # next_direction = stdscr.getkey()
        try:
            next_direction = stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            return "Quit"
        direction = direction if next_direction == -1 else next_direction
        if snake[0][0] == ROWS:
            return f"Snake out of bounds vertically, score: {score}"
        if snake[0][1] == COLS:
            return f"Snake out of bounds horizontally, score: {score}"
        if snake[0] in snake[1:]:
            return f"Snake can't eat itself, score: {score}"
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
            return "Quit"
        else:
            continue
        if not paused:
            snake.insert(0, new_head)
            if snake[0] == food:
                food = None
                while food is None:
                    new_food = [
                        random.randint(0, ROWS - 1),
                        random.randint(0, COLS - 1),
                    ]
                    food = new_food if new_food not in snake else None
                stdscr.addstr(*food, CHAR_FOOD)
                score += 1
            else:
                stdscr.addstr(*snake.pop(-1), CHAR_BG)
            stdscr.addstr(*snake[0], CHAR_SNAKE)
        stdscr.addstr(ROWS, 49, str(score))
        stdscr.refresh()


if __name__ == "__main__":
    print(f"Game over: {curses.wrapper(main)}")
