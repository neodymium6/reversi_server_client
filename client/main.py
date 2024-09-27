import socket
import logging
import argparse

HOST = 'localhost'
PORT = 12345

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('color', choices=['black', 'white'])
    parser.add_argument('--log', default='client.log')
    args = parser.parse_args()
    log_format = '%(asctime)s\t[%(filename)s:%(lineno)d %(funcName)s]\t%(levelname)s\t%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S', filename=args.log, level=logging.DEBUG)
    # stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y/%m/%d %H:%M:%S'))
    logging.getLogger().addHandler(console_handler)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    logging.info('Connected to {}:{}'.format(HOST, PORT))

    # join
    sock.send('join {}\n'.format(args.color).encode())
    data = sock.recv(1024)
    logging.info('Received: {}'.format(data.decode()))
    if data == b'no':
        logging.error('Connection refused')
        sock.close()
        return
    
    # wait for game start
    logging.info('Waiting for game start')
    data = sock.recv(1024)
    logging.info('Received: {}'.format(data.decode()))
    if data != b'game_start':
        logging.error('Unexpected message')
        sock.close()
        return
    sock.send(b'ok\n')

    # game
    while True:
        sock.recv(1024)
        logging.info('Received: {}'.format(data.decode()))


    sock.close()



if __name__ == '__main__':
    main()
