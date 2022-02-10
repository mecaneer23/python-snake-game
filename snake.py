#!/bin/env python3
try:
    import curses
except ImportError:
    print(
        "Curses not installed, if you're on Windows, you can install it with: `pip install windows-curses`"
    )
    exit(1)
import time
import random

ROWS = 10
COLS = 10
CHAR_SNAKE = "#"
CHAR_FOOD = "*"
CHAR_BG = ". "
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def get_char_at(x, y, snake, food=None):  # int int -> char
    if (x, y) in snake:
        return CHAR_SNAKE
    elif (x, y) == food:
        return CHAR_FOOD
    else:
        return CHAR_BG


def step_point(x, y, direction):  # int int int -> int int
    if direction == UP:
        return (x, y - 1)
    elif direction == DOWN:
        return (x, y + 1)
    elif direction == LEFT:
        return (x - 1, y)
    elif direction == RIGHT:
        return (x + 1, y)
    assert 0, f"Invalid direction: {direction}"


def snake_add(x, y, snake, food=None):  # int int list -> list
    if get_char_at(x, y, snake, food) == CHAR_BG:
        if (x, y) not in snake:
            snake.append((x, y))
            return snake
        assert 0, "snake_add: snake already contains position"


def snake_del(x, y, snake, food=None):
    if get_char_at(x, y, snake, food) == CHAR_SNAKE:
        snake.remove((x, y))
        return snake


def display(stdscr, snake, food=None):
    for x in range(ROWS):
        for y in range(COLS):
            stdscr.addstr(x, y, get_char_at(x, y, snake, food))
    stdscr.addstr("\n")


def spawn_food(snake, old_food=None):
    food = (random.randint(0, ROWS), random.randint(0, COLS))
    while get_char_at(*food, snake, old_food) != CHAR_BG:
        food = (random.randint(0, ROWS), random.randint(0, COLS))
    return food


def main(stdscr):
    dead = False
    paused = False
    score = 0
    head_position = (5, 5)
    head_direction = RIGHT
    snake_length = 3
    snake = [head_position]
    for i in range(snake_length - 1):
        snake = snake_add(
            step_point(head_position[0] - i, head_position[1], LEFT)[0],
            head_position[1],
            snake
        )
    food = spawn_food(snake)
    curses.curs_set(0)
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.timeout(-1)
    stdscr.refresh()
    while not dead:
        stdscr.addstr(f"Score: {score}")
        display(stdscr, snake, food)
        stdscr.addstr("WASD to move, Q to quit, SPACE to toggle pause")
        stdscr.refresh()
        cmd = stdscr.getkey()
        if cmd == "w":
            head_direction = UP
        elif cmd == "a":
            head_direction = LEFT
        elif cmd == "s":
            head_direction = DOWN
        elif cmd == "d":
            head_direction = RIGHT
        elif cmd == "q":
            dead = True
        elif cmd == " ":
            paused = not paused
        else:
            pass # non-valid input - ignore for now

        if not paused:
            head_position = step_point(*head_position, head_direction)
            char = get_char_at(*head_position, snake, food)
            if char == CHAR_SNAKE:
                dead = True
                stdscr.addstr(f"You Died! Score: {score}")
            elif char == CHAR_FOOD:
                snake = snake_add(*head_position, snake, food)
                snake_length += 1
                if snake_length >= ROWS * COLS:
                    stdscr.addstr("You won!")
                score += 1
                food = spawn_food(snake, food)
            elif char == CHAR_BG:
                snake_del(*snake[-1], snake, food)
                snake = snake_add(*head_position, snake, food)
            snake = snake_add(*head_position, snake, food)
        time.sleep(0.2)


if __name__ == "__main__":
    curses.wrapper(main)
