#!/usr/bin/env python3
"""Python snake game"""

import curses
from argparse import SUPPRESS, ArgumentParser, Namespace
from collections import deque
from enum import Enum
from random import randint
from typing import Iterable, Iterator

from working_initscr import wrapper

# from os.path import exists, expanduser

# CHARACTER_ASPECT_RATIO = 19 / 9
# FILENAME = expanduser("~/.config/snake-best-score.txt")

COLORS = {
    "black": curses.COLOR_BLACK,
    "white": curses.COLOR_WHITE,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
}


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

    def init(
        self,
        stdscr: curses.window,
        bg_color: int,
        long_text: str,
        short_text: str,
    ) -> None:
        """Initialize the board by outputting the background and bottom text."""
        for y in range(self._rows):
            for x in range(self._cols):
                stdscr.addch(y, x, self._background_char, bg_color)

        stdscr.addstr(
            self._rows,
            0,
            long_text if self.is_large_enough(len(long_text)) else short_text,
            bg_color,
        )

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
        yield self._x
        yield self._y

    def __repr__(self) -> str:
        return f"({self._x}, {self._y})"


class Snake:
    """Represent a snake for the game"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        body_char: str,
        head_char: str,
        # max_speed: int,
        cheat: int,
        color: int,
    ) -> None:
        self._body_char = body_char
        self._head_char = head_char
        # self._max_speed = max_speed
        self._head = Location(5, 5)
        self._body: deque[Location] = deque((Location(4, 5),))
        for _ in range(cheat + 1):
            self._body.append(Location(3, 5))
        self._color = color

    def display_head(self, stdscr: curses.window) -> None:
        """Render the head of the snake"""
        stdscr.addch(
            self._head.get_y(),
            self._head.get_x(),
            self._head_char,
            self._color,
        )

    def display(self, stdscr: curses.window) -> None:
        """Render the snake"""
        self.display_head(stdscr)
        for x, y in self._body:
            stdscr.addch(
                y,
                x,
                self._body_char,
                self._color,
            )

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


class Direction(Enum):
    """
    Represent the state the snake is currently in.
    Includes paused, direction snake is heading/facing/moving, and gameover
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PAUSED = "paused"
    GAMEOVER = "gameover"


class Food:
    """Represent the food the snake is currently trying to eat"""

    def __init__(
        self,
        char: str,
        rows: int,
        cols: int,
        color: int,
    ) -> None:
        self._char = char
        self._rows = rows
        self._cols = cols
        self._location = Location(cols // 2, rows // 2)
        self._color = color

    def get_location(self) -> Location:
        """Return the food's current location"""
        return self._location

    def reroll(self, snake: Snake) -> None:
        """Randomly update the location of the food"""
        while True:
            loc = Location(
                randint(0, self._cols - 1),
                randint(0, self._rows - 1),
            )
            if loc in snake:
                continue
            self._location = loc
            break

    def display(self, stdscr: curses.window) -> None:
        """Render the food"""
        stdscr.addch(
            self._location.get_y(),
            self._location.get_x(),
            self._char,
            self._color,
        )


class Game:  # pylint: disable=too-many-instance-attributes
    """Runnable game object"""

    _LONG_TEXT = "Controls: wasd or arrow keys, q to quit | Score: 0"
    _SHORT_TEXT = "Score: 0"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        stdscr: curses.window,
        snake: Snake,
        board: Board,
        food_char: str,
        bg_color: int,
        food_color: int,
    ) -> None:
        self._stdscr = stdscr
        self._snake = snake
        self._board = board
        self._food = Food(
            food_char,
            self._board.get_rows(),
            self._board.get_cols(),
            food_color,
        )
        self._paused = Direction.PAUSED
        self._direction = Direction.RIGHT
        self._score = len(snake)
        self._bg_color = bg_color
        # best_score = update_best_score(score)
        self._board.init(
            self._stdscr,
            self._bg_color,
            self._LONG_TEXT,
            self._SHORT_TEXT,
        )
        self._food.display(self._stdscr)
        self._snake.display(self._stdscr)

    def _ensure_valid(self, new: Direction) -> Direction:
        """Disallow moving in the opposite direction from current"""
        if self._direction == Direction.PAUSED:
            unpause_heading = self._paused
            self._paused = Direction.PAUSED
            return unpause_heading

        if new == Direction.PAUSED:
            self._paused = self._direction
            return Direction.PAUSED

        opposites: dict[Direction, Direction] = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if new == opposites[self._direction]:
            return self._direction
        return new

    def _get_new_direction(self) -> Direction:
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
            return Direction.GAMEOVER
        if key in (113, 27):  # q, esc
            return Direction.GAMEOVER
        if key == -1:  # no key provided
            return self._direction
        return self._ensure_valid(keys.get(key, Direction.PAUSED))

    def _get_new_head(self) -> Location:
        """Return the location of the snake's new head"""
        self._direction = self._get_new_direction()
        if self._direction == Direction.PAUSED:
            return Location(-1, -1)  # pause
        addend = 1 if self._direction in (Direction.DOWN, Direction.RIGHT) else -1
        head = self._snake.get_head()
        new_x = head.get_x()
        new_y = head.get_y()
        if self._direction in (Direction.LEFT, Direction.RIGHT):
            return Location(new_x + addend, new_y)
        return Location(new_x, new_y + addend)

    def _display_score(self) -> None:
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
            self._bg_color,
        )

    def run(self) -> str:
        """Main loop for game. Returns why game ended."""
        while True:
            new_head = self._get_new_head()
            if self._direction == Direction.GAMEOVER:
                return "Quit"
            if self._direction == Direction.PAUSED:
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
                    self._bg_color,
                )
            self._snake.add_head(new_head)
            self._snake.display_head(self._stdscr)
            self._food.display(self._stdscr)
            self._display_score()
            self._stdscr.refresh()

    def get_score(self) -> int:
        """Return the current score"""
        return self._score


def get_args(color_choices: Iterable[str]) -> Namespace:
    """Parse the command line arguments using argparse"""
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


def main(stdscr: curses.window, args: Namespace) -> str:
    """Entry point for snake game"""

    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(True)
    stdscr.timeout(1000 // args.speed)

    curses.init_pair(1, -1 if args.black_white else COLORS[args.color_bg], -1)
    curses.init_pair(2, -1 if args.black_white else COLORS[args.color_snake], -1)
    curses.init_pair(3, -1 if args.black_white else COLORS[args.color_food], -1)

    game = Game(
        stdscr,
        Snake(
            args.char_snake,
            args.char_head,
            # args.speed,
            args.cheat,
            curses.color_pair(2),
        ),
        Board(
            args.rows or stdscr.getmaxyx()[0] - 1,
            args.columns or stdscr.getmaxyx()[1] - 1,
            args.char_bg,
        ),
        args.char_food,
        curses.color_pair(1),
        curses.color_pair(3),
    )

    return f"Game over: {game.run()}\nScore: {game.get_score()}"


if __name__ == "__main__":
    print(wrapper(main, get_args(COLORS.keys())))
