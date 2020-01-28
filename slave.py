import socket
import time
from socket import socket


def tryConnect(addr):
    cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while cliSock.connect_ex(ADDR):
        time.sleep(1)
        cliSock.close()
        cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('try connecting ...')
    return cliSock


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315
    ADDR = (HOST, PORT)

    sock = tryConnect(ADDR)

    while True:
        try:
            data = input('> ')
            sock.send(data.encode(encoding='utf-8'))
            if data == 'shutdown' or data == 'exit':
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e.message)
            sock = tryConnect(ADDR)

    sock.close()
