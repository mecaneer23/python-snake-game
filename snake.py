#!/usr/bin/env python3
"""Python snake game"""

import curses
from argparse import SUPPRESS, ArgumentParser, Namespace
from collections import deque
from enum import Enum
from os.path import exists, expanduser
from random import randint
from typing import Iterator

from working_initscr import wrapper

CHARACTER_ASPECT_RATIO = 19 / 9
FILENAME = expanduser("~/.config/snake-best-score.txt")


class DisplayableInterface:
    """Specify a class with a display function"""

    def display(self, stdscr: curses.window) -> None:
        """Output some sort of representation of this object to stdscr"""
        _ = stdscr
        raise NotImplementedError("display must be implemented by child")


class Board:
    """Represent a board for the snake to move on"""

    def __init__(
        self,
        rows: int,
        cols: int,
        background_char: str,
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._background_char = background_char

    def get_rows(self) -> int:
        """Get the number of rows"""
        return self._rows

    def get_cols(self) -> int:
        """Get the number of columns"""
        return self._cols

    def get_background_char(self) -> str:
        """Get the background character"""
        return self._background_char

    def is_large_enough(self, long_text_length: int) -> bool:
        """
        Return whether the board is wide
        enough to display the instructions
        """
        return self._cols > long_text_length


class Location:
    """Represent a location with an x and y coordinate"""

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def get_x(self):
        """Get the x coordinate"""
        return self._x

    def get_y(self):
        """Get the y coordinate"""
        return self._y

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Location) and self._x == other._x and self._y == other._y
        )

    def __iter__(self) -> Iterator[int]:
        return iter({self._x, self._y})

    def __repr__(self) -> str:
        return f"({self._x}, {self._y})"


class Snake(DisplayableInterface):
    """Represent a snake for the game"""

    def __init__(
        self,
        body_char: str,
        head_char: str,
        max_speed: int,
        cheat: int,
    ) -> None:
        self._body_char = body_char
        self._head_char = head_char
        self._max_speed = max_speed
        self._head = Location(5, 5)
        self._body: deque[Location] = deque((Location(4, 5),))
        for _ in range(cheat + 1):
            self._body.append(Location(3, 5))

    def display(self, stdscr: curses.window) -> None:
        stdscr.addch(
            self._head.get_y(),
            self._head.get_x(),
            self._head_char,
            curses.color_pair(2),
        )
        for x, y in self:
            stdscr.addch(y, x, self._body_char, curses.color_pair(2))

    def get_head(self) -> Location:
        """Returns the head of the snake"""
        return self._head

    def add_head(self, head: Location) -> None:
        """Display a new head of the snake"""
        self._body.appendleft(self._head)
        self._head = head

    def __contains__(self, item: Location) -> bool:
        return item in self._body

    def pop(self) -> Location:
        """Remove the last bit of the tail of the snake"""
        return self._body.pop()

    def __len__(self) -> int:
        return len(self._body) + 1

    def __iter__(self) -> Iterator[tuple[int, int]]:
        for loc in self._body:
            yield loc.get_x(), loc.get_y()


class Direction(Enum):
    """Represent the direction the snake is currently facing/moving"""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class Food(DisplayableInterface):
    """Represent the food the snake is currently trying to eat"""

    def __init__(self, char: str, rows: int, cols: int) -> None:
        self._char = char
        self._rows = rows
        self._cols = cols
        self._location = Location(rows // 2, cols // 2)

    def get_location(self) -> Location:
        """Return the food's current location"""
        return self._location

    def reroll(self, snake: Snake) -> None:
        """Randomly update the location of the food"""
        while True:
            loc = Location(
                randint(0, self._rows - 1),
                randint(0, self._cols - 1),
            )
            if loc in snake:
                continue
            self._location = loc
            break

    def display(self, stdscr: curses.window) -> None:
        stdscr.addch(
            self._location.get_y(),
            self._location.get_x(),
            self._char,
            curses.color_pair(3),
        )


class Game:
    """Runnable game object"""

    _LONG_TEXT = "Controls: wasd or arrow keys, q to quit | Score: 0"
    _SHORT_TEXT = "Score: 0"

    def _init_board(self) -> None:
        for y in range(self._board.get_rows()):
            for x in range(self._board.get_cols()):
                self._stdscr.addch(
                    y, x, self._board.get_background_char(), curses.color_pair(1)
                )

        self._stdscr.addstr(
            self._board.get_rows(),
            0,
            self._LONG_TEXT
            if self._board.is_large_enough(len(self._LONG_TEXT))
            else self._SHORT_TEXT,
            curses.color_pair(1),
        )

    def __init__(
        self,
        stdscr: curses.window,
        snake: Snake,
        board: Board,
        food_char: str,
    ) -> None:
        self._stdscr = stdscr
        self._snake = snake
        self._board = board
        self._food = Food(
            food_char,
            self._board.get_rows(),
            self._board.get_cols(),
        )
        self._paused = False
        self._direction = Direction.RIGHT
        self._running = True
        self._score = len(snake)
        # best_score = update_best_score(score)
        self._init_board()
        for obj in (self._food, self._snake):
            obj.display(self._stdscr)

    def get_input(self) -> Direction:
        """
        If a key has been pressed, change the
        direction or pause the game
        """
        keys: dict[int, Direction] = {
            119: Direction.UP,
            259: Direction.UP,
            107: Direction.UP,
            97: Direction.LEFT,
            260: Direction.LEFT,
            104: Direction.LEFT,
            115: Direction.DOWN,
            258: Direction.DOWN,
            106: Direction.DOWN,
            100: Direction.RIGHT,
            261: Direction.RIGHT,
            108: Direction.RIGHT,
        }
        try:
            key = self._stdscr.getch()
        except KeyboardInterrupt:  # exit on ^C
            self._running = False
            return Direction.NONE
        if key in (113, 27):  # q, esc
            self._running = False
            return Direction.NONE
        if key == -1:  # no key provided
            return self._direction
        try:
            return keys[key]
        except KeyError:
            return Direction.NONE

    def get_new_head(self) -> Location:
        """Return the location of the snake's new head"""
        self._direction = self.get_input()
        self._paused = False
        if self._direction == Direction.NONE:
            self._paused = True
            return Location(-1, -1)  # pause
        addend = 1 if self._direction in (Direction.DOWN, Direction.RIGHT) else -1
        head = self._snake.get_head()
        new_x = head.get_x()
        new_y = head.get_y()
        if self._direction in (Direction.LEFT, Direction.RIGHT):
            return Location(new_x + addend, new_y)
        return Location(new_x, new_y + addend)

    def display_score(self) -> None:
        """Output the current score at the correct location"""
        self._stdscr.addstr(
            self._board.get_rows(),
            (
                len(self._LONG_TEXT)
                if self._board.is_large_enough(len(self._LONG_TEXT))
                else len(self._SHORT_TEXT)
            )
            - 1,
            str(self._score),
            curses.color_pair(1),
        )

    def run(self) -> str:
        """Main loop for game"""
        while True:
            if not self._running:
                return "Quit"
            new_head = self.get_new_head()
            if self._paused:
                continue
            if new_head.get_y() in (self._board.get_rows(), -1):
                return "Snake out of bounds vertically"
            if new_head.get_x() in (self._board.get_cols(), -1):
                return "Snake out of bounds horizontally"
            if new_head in self._snake:
                return "Snake can't eat itself"
            if new_head == self._food.get_location():
                self._food.reroll(self._snake)
                self._score += 1
                # best_score = update_best_score(score)
            else:
                new_bg = self._snake.pop()
                self._stdscr.addch(
                    new_bg.get_y(),
                    new_bg.get_x(),
                    self._board.get_background_char(),
                    curses.color_pair(1),
                )
            self._snake.add_head(new_head)
            for obj in (self._food, self._snake):
                obj.display(self._stdscr)
            self.display_score()
            self._stdscr.refresh()

    def get_score(self) -> int:
        """Return the current score"""
        return self._score


def get_args() -> Namespace:
    """Parse the command line arguments using argparse"""
    color_choices = [
        "black",
        "white",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
    ]
    parser = ArgumentParser(
        description="snake game",
        add_help=False,
    )
    parser.add_argument(
        "--help",
        "-h",
        action="help",
        help="show this help message and exit",
    )
    parser.add_argument(
        "--cheat",
        default=0,
        type=int,
        help=SUPPRESS,
    )
    parser.add_argument(
        "--black-white",
        "--bw",
        action="store_true",
        help="disable colors (black and white only)",
    )
    parser.add_argument(
        "--rows",
        "-r",
        type=int,
        help="set rows",
    )
    parser.add_argument(
        "--columns",
        "-c",
        type=int,
        help="set columns",
    )
    parser.add_argument(
        "--color-snake",
        choices=color_choices,
        default="green",
        help="set snake color",
    )
    parser.add_argument(
        "--color-food",
        choices=color_choices,
        default="yellow",
        help="set food color",
    )
    parser.add_argument(
        "--color-bg",
        choices=color_choices,
        default="white",
        help="set background color",
    )
    parser.add_argument(
        "--char-snake",
        type=str,
        default="#",
        help="set snake character",
    )
    parser.add_argument(
        "--char-head",
        type=str,
        default="#",
        help="set head character",
    )
    parser.add_argument(
        "--char-food",
        type=str,
        default="*",
        help="set food character",
    )
    parser.add_argument(
        "--char-bg",
        type=str,
        default=".",
        help="set background character",
    )
    parser.add_argument(
        "--speed",
        "-s",
        type=int,
        default=10,
        help="set speed",
    )
    return parser.parse_args()


# def end(stdscr: curses.window, exit_msg: str, **kwargs):
#     try:
#         curses.nocbreak()
#         stdscr.keypad(False)
#         curses.echo()
#         curses.endwin()
#     except curses.error:
#         return "Error in exiting"
#     return (
#         exit_msg
#         + "\n"
#         + ", ".join(
#             f"{k.capitalize().replace('_', ' ')}: {v}" for k, v in kwargs.items()
#         )
#     )


# def update_best_score(score: int, best_score: int = -1) -> int:
#     if best_score == -1:
#         fetch_best_score(score)
#     if score > best_score:
#         with open(FILENAME, "w", encoding="utf-8") as f:
#             f.write(str(score))
#     return max(score, best_score)


# def fetch_best_score(score: int = 0) -> int:
#     if not exists(FILENAME):
#         with open(FILENAME, "w", encoding="utf-8") as f:
#             f.write(str(score))
#         return score
#     with open(FILENAME, "r", encoding="utf-8") as f:
#         return int(f.read().split("\n")[0])


def main(stdscr: curses.window) -> str:
    """Entry point for snake game"""
    args = get_args()
    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)
    stdscr.timeout(1000 // args.speed)

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

    game = Game(
        stdscr,
        Snake(
            args.char_snake,
            args.char_head,
            args.speed,
            args.cheat,
        ),
        Board(
            args.rows or stdscr.getmaxyx()[0] - 1,
            args.columns or stdscr.getmaxyx()[1] - 1,
            args.char_bg,
        ),
        args.char_food,
    )

    return f"Game over: {game.run()}\nScore: {game.get_score()}"


if __name__ == "__main__":
    print(wrapper(main))
