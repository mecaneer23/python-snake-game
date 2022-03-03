#!/bin/env python3
try:
    import curses
except ImportError:
    from os import name as osname
    if osname == "nt":
        print("Curses not installed. You can install it with: `pip install windows-curses`")
    exit(1)
import time
import random

ROWS = 20
COLS = 50
CHAR_SNAKE = "#"
CHAR_FOOD = "*"
CHAR_BG = "."
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Initialize game variables
    snake = [[5, 5], [5, 4], [5, 3]]
    food = [ROWS//2, COLS//2]
    direction = 100
    paused = False

    # draw board
    for x in range(ROWS):
        for y in range(COLS):
            stdscr.addstr(x, y, CHAR_BG)

    # draw snake
    for i, _ in enumerate(snake):
        stdscr.addch(*snake[i], CHAR_SNAKE)

    # draw food
    stdscr.addch(*food, CHAR_FOOD)

    # main loop
    while True:
        # next_direction = stdscr.getkey()
        next_direction = stdscr.getch()
        direction = direction if next_direction == -1 else next_direction
        if snake[0][0] in [0, ROWS]: return "Snake out of bounds vertically"
        if snake[0][1] in [0, COLS]: return "Snake out of bounds horizontally"
        if snake[0] in snake[1:]: return "Snake can't eat itself"
        new_head = snake[0].copy()
        if direction == 119: # w
            new_head[0] -= 1
        elif direction == 97: # a
            new_head[1] -= 1
        elif direction == 115: # s
            new_head[0] += 1
        elif direction == 100: # d
            new_head[1] += 1
        elif direction == 113: # q
            return "Quit"
        else:
            continue
        if not paused:
            snake.insert(0, new_head)
            if snake[0] == food:
                food = None
                while food is None:
                    new_food = [random.randint(0, ROWS-1), random.randint(0, COLS-1)]
                    food = new_food if new_food not in snake else None
                stdscr.addch(*food, CHAR_FOOD)
            else:
                stdscr.addch(*snake.pop(-1), CHAR_BG)
            stdscr.addch(*snake[0], CHAR_SNAKE)
            stdscr.refresh()


if __name__ == "__main__":
    print(f"Game over: {curses.wrapper(main)}")
