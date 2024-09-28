import socket
import logging
import argparse
import threading
import time
import creversi

HOST = "localhost"
PORT = 12345

connections = [None, None]
connections_lock = threading.Lock()
game_started = False
handle_client_threads = []


def conn2idx(conn):
    with connections_lock:
        for i in range(len(connections)):
            if connections[i] == conn:
                return i
    return None


def log_setup():
    # logging
    log_format = "%(asctime)s\t[%(filename)s:%(lineno)d %(funcName)s]\t%(levelname)s\t%(message)s"
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="server.log")
    args = parser.parse_args()
    logging.basicConfig(
        format=log_format,
        datefmt="%Y/%m/%d %H:%M:%S",
        filename=args.log,
        level=logging.DEBUG,
    )
    # stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter(log_format, datefmt="%Y/%m/%d %H:%M:%S")
    )
    logging.getLogger().addHandler(console_handler)


def handle_command(command, conn):
    if command.startswith("join "):
        color = command.split()[1]
        with connections_lock:
            if color == "black" and connections[0] is None:
                connections[0] = conn
                conn.sendall(b"yes")
                logging.info("connection 0: {}".format(conn))
            elif color == "white" and connections[1] is None:
                connections[1] = conn
                conn.sendall(b"yes")
                logging.info("connection 1: {}".format(conn))
            else:
                conn.sendall(b"no")
                logging.info("connection refused (the color is used): {}".format(conn))
    else:
        conn.sendall(b"unknown command")
        logging.info("unknown command: {}".format(command[0:-1]))


def handle_client(conn, addr):
    # return after adding connection to connections
    global game_started
    logging.info("Connected by {}".format(addr))
    try:
        while True:
            buffer = b""
            try:
                while True:
                    data = conn.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
            except BlockingIOError:
                time.sleep(0.01)
                continue
            logging.info("Received: {}".format(buffer.decode()[0:-1]))
            handle_command(buffer.decode(), conn)
            if conn2idx(conn) is not None:
                return
    except Exception as e:
        logging.error(e)
        conn.close()
        logging.info("Connection closed by {}".format(addr))
        with connections_lock:
            for i in range(len(connections)):
                if connections[i] == conn:
                    connections[i] = None


def game_thread(conn_black, conn_white):
    try:
        global game_started
        logging.info("Game started")
        handle_client_threads[0].join()
        handle_client_threads[1].join()
        for thread in handle_client_threads:
            thread.join()
        handle_client_threads.clear()
        conn_black.sendall(b"game_start")
        conn_white.sendall(b"game_start")
        logging.info("Check if both clients are ready")
        # check if black is ok
        while True:
            buffer = b""
            try:
                while True:
                    data = conn_black.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
            except BlockingIOError:
                time.sleep(0.01)
                continue
            logging.info("Received (black): {}".format(buffer.decode()[0:-1]))
            if buffer == b"ok\n":
                break
            else:
                conn_black.sendall(b"game_end error")
                conn_white.sendall(b"game_end error")
                return
        # check if white is ok
        while True:
            buffer = b""
            try:
                while True:
                    data = conn_white.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
            except BlockingIOError:
                time.sleep(0.01)
                continue
            logging.info("Received (white): {}".format(buffer.decode()[0:-1]))
            if buffer == b"ok\n":
                break
            else:
                conn_black.sendall(b"game_end error")
                conn_white.sendall(b"game_end error")
                return
        logging.info("Both clients are ready")

        def parse_move(move_command):
            move_command = move_command.decode().strip()
            if move_command.split()[0] == "move":
                return int(move_command.split()[1])
            else:
                raise ValueError("Invalid move command")

        # game start
        board = creversi.Board()
        while not board.is_game_over():
            logging.info("\nBoard: {}".format(board))
            if board.turn == creversi.BLACK_TURN:
                conn_black.sendall(b"your_turn")
                buffer = b""
                while True:
                    data = conn_black.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
                logging.info("Received (black): {}".format(buffer.decode()[0:-1]))
                move = parse_move(buffer)
                if not board.is_legal(move):
                    raise ValueError("Illegal move")
                board.move(move)
                conn_white.sendall("move {}".format(move).encode())
                buffer = b""
                while True:
                    data = conn_white.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
                logging.info("Received (white): {}".format(buffer.decode()[0:-1]))
                if buffer != b"ok\n":
                    raise ValueError("Invalid response from white")
            else:
                conn_white.sendall(b"your_turn")
                buffer = b""
                while True:
                    data = conn_white.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
                logging.info("Received (white): {}".format(buffer.decode()[0:-1]))
                move = parse_move(buffer)
                if not board.is_legal(move):
                    raise ValueError("Illegal move")
                board.move(move)
                conn_black.sendall("move {}".format(move).encode())
                buffer = b""
                while True:
                    data = conn_black.recv(1024)
                    buffer += data
                    if data.endswith(b"\n"):
                        break
                logging.info("Received (black): {}".format(buffer.decode()[0:-1]))
                if buffer != b"ok\n":
                    raise ValueError("Invalid response from black")
        logging.info("Game over")
        if board.turn == creversi.BLACK_TURN:
            black_pieces = board.piece_num()
            white_pieces = board.opponent_piece_num()
        else:
            black_pieces = board.opponent_piece_num()
            white_pieces = board.piece_num()
        if black_pieces > white_pieces:
            conn_black.sendall(
                "game_end win {} {}".format(black_pieces, white_pieces).encode()
            )
            conn_white.sendall(
                "game_end lose {} {}".format(white_pieces, black_pieces).encode()
            )
        elif black_pieces < white_pieces:
            conn_black.sendall(
                "game_end lose {} {}".format(black_pieces, white_pieces).encode()
            )
            conn_white.sendall(
                "game_end win {} {}".format(white_pieces, black_pieces).encode()
            )
        else:
            conn_black.sendall(
                "game_end draw {} {}".format(black_pieces, white_pieces).encode()
            )
            conn_white.sendall(
                "game_end draw {} {}".format(black_pieces, white_pieces).encode()
            )
        logging.info("Sent game result")
        logging.info("Connection closed by game")
        conn_black.close()
        conn_white.close()
        with connections_lock:
            connections[0] = None
            connections[1] = None
        game_started = False

    except Exception as e:
        logging.error(e)
        conn_black.close()
        conn_white.close()
        logging.info("Connection closed by game")
        with connections_lock:
            connections[0] = None
            connections[1] = None
        game_started = False


def main():
    global game_started
    log_setup()

    # prepare socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    sock.setblocking(False)
    logging.info("Server started at {}:{}".format(HOST, PORT))

    # accept connection
    while True:
        try:
            conn, addr = sock.accept()
            logging.info("Accepted connection from {}".format(addr))
            with connections_lock:
                if connections[0] is not None and connections[1] is not None:
                    conn.sendall(b"Server is full")
                    conn.close()
                    logging.info("Connection refused: Server is full")
                    continue
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            handle_client_threads.append(thread)
        except BlockingIOError:
            time.sleep(0.01)
        finally:
            with connections_lock:
                if (
                    connections[0] is not None
                    and connections[1] is not None
                    and not game_started
                ):
                    threading.Thread(
                        target=game_thread, args=(connections[0], connections[1])
                    ).start()
                    game_started = True


if __name__ == "__main__":
    main()
