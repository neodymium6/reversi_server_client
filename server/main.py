import socket
import logging
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', default='server.log')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y/%m/%d %H:%M:%S', filename=args.log, level=logging.DEBUG)
    # stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
    logging.getLogger().addHandler(console_handler)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12345
    sock.bind((host, port))
    sock.listen(1)
    logging.info('Server started at {}:{}'.format(host, port))

    while True:
        conn, addr = sock.accept()
        logging.info('Connected by {}'.format(addr))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logging.info('Received: {}'.format(data.decode()))
            conn.send(data)
        conn.close()
        logging.info('Connection closed by {}'.format(addr))


if __name__ == '__main__':
    main()
