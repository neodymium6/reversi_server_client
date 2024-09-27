import socket
import logging
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', default='client.log')
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

    sock.connect((host, port))
    logging.info('Connected to {}:{}'.format(host, port))

    sock.send(b'Hello, world!')
    logging.info('Sent: Hello, world!')

    data = sock.recv(1024)
    logging.info('Received: {}'.format(data.decode()))
    
    sock.close()



if __name__ == '__main__':
    main()
