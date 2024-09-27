# reversi_server_client

## internal command

### server -> client

- `game_start`
    - send `game_start` to client to indicate that the game has started.


### client -> server

- `join "color"` -> `yes` or `no`

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
