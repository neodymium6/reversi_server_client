# reversi_server_client

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
