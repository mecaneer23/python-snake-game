# Python Snake Game

![Snake game in action!](res/snake.png)

This is a snake game in python. The default characters are as below.

- Snake: `#`
- Food: `*`
- Background: `.`

[GitHub](https://github.com/mecaneer23/python-snake-game)

## How to play

wasd or arrow keys or Vim hjkl for snake movement. q to quit. Any other key to pause. Press one of the movement keys to resume.

## Running the game

```bash
python3 snake.py [flags]
```

### Flags

See `snake.py --help`

### Example configurations

```bash
python3 snake.py --char-head='☺' --char-snake='+' --char-bg=' '
python3 snake.py --color-snake blue --color-food red
```

## Todo

- [ ] Make horizontal and vertical speeds equal (see commit history for details)
- [ ] Add support for best score saving/loading (tentative)
