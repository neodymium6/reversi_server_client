import socket
import logging
import argparse
import threading
import creversi

HOST = 'localhost'
PORT = 12345

connections = [None, None]
connections_lock = threading.Lock()

def log_setup():
    # logging
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', default='server.log')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y/%m/%d %H:%M:%S', filename=args.log, level=logging.DEBUG)
    # stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
    logging.getLogger().addHandler(console_handler)

def handle_command(command, conn):
    if command.startswith('join '):
        color = command.split()[1]
        with connections_lock:
            if color == 'black' and connections[0] is None:
                connections[0] = conn
                conn.send(b'yes')
                logging.info('connection 0: {}'.format(conn))
            elif color == 'white' and connections[1] is None:
                connections[1] = conn
                conn.send(b'yes')
                logging.info('connection 1: {}'.format(conn))
            else:
                conn.send(b'no')
                logging.info('connection refused (the color is used): {}'.format(conn))
    else:
        conn.send(b'unknown command')
        logging.info('unknown command: {}'.format(conn))


def handle_client(conn, addr):
    logging.info('Connected by {}'.format(addr))
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # no data -> connection closed
                break
            logging.info('Received: {}'.format(data.decode()))
            handle_command(data.decode(), conn)
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()
        logging.info('Connection closed by {}'.format(addr))
        with connections_lock:
            for i in range(len(connections)):
                if connections[i] == conn:
                    connections[i] = None

def main():
    log_setup()

    # prepare socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen()
    logging.info('Server started at {}:{}'.format(HOST, PORT))

    # prepare game
    board = creversi.Board()

    # accept connection
    while True:
        conn, addr = sock.accept()
        with connections_lock:
            if connections[0] is not None and connections[1] is not None:
                conn.send(b'Server is full')
                conn.close()
                logging.info('Connection refused: Server is full')
                continue
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
