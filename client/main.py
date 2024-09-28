import socket
import logging
import argparse
import creversi
import subprocess

HOST = "localhost"
PORT = 12345


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("color", choices=["black", "white"])
    parser.add_argument("--engine", default="python random_player.py")
    parser.add_argument("--log", default="client.log")
    args = parser.parse_args()
    log_format = "%(asctime)s\t[%(filename)s:%(lineno)d %(funcName)s]\t%(levelname)s\t%(message)s"
    logging.basicConfig(
        format=log_format,
        datefmt="%Y/%m/%d %H:%M:%S",
        filename=args.log,
        level=logging.DEBUG,
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    logging.info("Connected to {}:{}".format(HOST, PORT))

    # join
    sock.sendall("join {}\n".format(args.color).encode())
    data = sock.recv(1024)
    logging.info("Received: {}".format(data.decode()))
    if data == b"no":
        logging.error("Connection refused")
        sock.close()
        return

    # wait for game start
    logging.info("Waiting for game start")

    engine_args = []
    for arg in args.engine.split():
        engine_args.append(arg)
    engine_args.append(args.color)
    # prepare game engine
    engine = subprocess.Popen(
        engine_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    data = sock.recv(1024)
    logging.info("Received: {}".format(data.decode()))
    if data != b"game_start":
        logging.error("Unexpected message")
        sock.close()
        return
    sock.sendall(b"ok\n")

    # game
    board = creversi.Board()
    while True:
        data = sock.recv(1024)
        logging.info("Received: {}".format(data.decode()))
        if data == b"your_turn":
            if len([move for move in range(64) if board.is_legal(move)]) == 0:
                board.move(64)
                sock.sendall(b"move 64\n")
                logging.info("Sent: pass")
                continue
            # make a move
            board_str = board.to_line()
            logging.info("Board: {}".format(board_str))
            engine.stdin.write(board_str + "\n")
            engine.stdin.flush()
            move = int(engine.stdout.readline())
            board.move(move)
            sock.sendall("move {}\n".format(move).encode())
            logging.info("Sent: {}".format(move))
        elif data.decode().startswith("move "):
            # opponent's move
            move = int(data.decode().split()[1])
            board.move(move)
            sock.sendall(b"ok\n")
            logging.info("Sent: ok")
        elif data.decode().startswith("game_end "):
            if data.decode().split()[1] == "error":
                raise ValueError("Game end with error")
            result = data.decode().split()[1]
            my_pieces = int(data.decode().split()[2])
            opponent_pieces = int(data.decode().split()[3])
            break
        else:
            logging.error("Unexpected message {}".format(data.decode()))
            raise Exception("Unexpected message")

    print(result)
    print("My pieces: {}".format(my_pieces))
    print("Opponent pieces: {}".format(opponent_pieces))
    sock.close()


if __name__ == "__main__":
    main()
