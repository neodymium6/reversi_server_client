import socket
import logging
import argparse
import threading
import creversi

HOST = 'localhost'
PORT = 12345

connections = []
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

def handle_client(conn, addr):
    logging.info('Connected by {}'.format(addr))
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logging.info('Received: {}'.format(data.decode()))
            conn.send(data)
            logging.info('Sent: {}'.format(data.decode()))
    except Exception as e:
        logging.error(e)
    finally:
        conn.close()
        logging.info('Connection closed by {}'.format(addr))
        with connections_lock:
            connections.remove(conn)

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
            assert len(connections) <= 2
            if len(connections) == 2:
                conn.send(b'Server is full')
                conn.close()
                logging.info('Connection refused: Server is full')
                continue
            connections.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
