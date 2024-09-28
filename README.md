# reversi_server_client

## server

### usage

```sh
cd server
python -m venv server_env
source server_env/bin/activate
pip install -r requirements.txt
python main.py
```

### command line options

- `--host`
    - host to bind to
    - default: `localhost`

- `--port`
    - port to bind to
    - default: `12345`

- `--log`
    - log file to write to
    - default: `server.log`


## client

### usage

```sh
cd client
python -m venv client_env
source client_env/bin/activate
pip install -r requirements.txt
python main.py black
```

### command line options

- `--host`
    - host to connect to
    - default: `localhost`

- `--port`
    - port to connect to
    - default: `12345`

- `engine`
    - engine to use
    - default: `python random_player.py`

- `--log`
    - log file to write to
    - default: `client.log`


### how to use your own engine

- engine is a command that can be executed in the shell.
- arg 1 of the command is the color of the client.
- engine should read board state from stdin and write the move to stdout.
- engine have to loop until receiving SIGTERM.
- board state format is as follows:
    - 1 lines of 64 characters.
    - each character is either `O`, `X`, or `-`.
    - `X` is a black piece.
    - `O` is a white piece.
    - `-` is an empty space.
    - the board is read from the top left to the bottom right.
    - ex: `------------------OOO------OXX----OOXX----OX--------------------`
- move format is as follows:
    - 1 line of a number.
    - the number is the position to place a piece.
    - the position is from 0 to 64.
    - the position is read from the top left to the bottom right.
    - 64 means pass.
    - ex: `34`

## internal command

### server -> client

commands do not end with a newline character.

- `game_start`
    - send `game_start` to client to indicate that the game has started.

- `your_turn`
    - send `your_turn` to client to indicate that it is the client's turn.
    - client should respond with `move [number]` where number is the position to place a piece.
    - example: `move 34`

- `move [number]`
    - send `move [number]` to client to indicate the opponent's move.
    - client should respond with `ok` to acknowledge the move.
    - number is the position where the opponent placed a piece.
    - example: `move 34`

- `game_end [description] [my_pieces] [opponent_pieces]`
    - send `game_end [description]` to client to indicate that the game has ended.
    - description can be `win`, `draw`, `lose`, or `error`.
    - except for `error`, the description is followed by pieces.
    - pieces are separated by a space.
    - pieces are the number of my pieces and the number of opponent pieces.
    - example: `game_end win 34 30`


### client -> server

commands end with a newline character.

- `join [color]`

    - send `join [color]` to server to join a game.
    - The server will respond with `yes` or `no` to indicate whether the request is accepted.
    - color can be `black` or `white`.
    - example: `join black`
        
## connection flow

1. client connects to server
1. client sends `join [color]` to server
1. server responds with `yes` or `no`
1. if `yes`, client waits for the game to start
1. when the game starts, server sends `game_start` to client
1. client receives `game_start` and starts the game. black goes first.
    1. if the client receives `your_turn`, the client should respond with `move [number]`
    1. if the client receives `move [number]`, the client should respond with `ok`
    1. repeat until the game ends
1. when the game ends, server sends `game_end [description] [my_pieces] [opponent_pieces]` to client
1. client receives `game_end` and ends the game
1. client disconnects from the server
