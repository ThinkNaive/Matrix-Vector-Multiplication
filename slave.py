# coding=utf-8
import socket
import time
from utils import send, receive


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

    # 接收数据
    A_unit = receive(sock)
    print(A_unit)
    # cal = np.sum(A_unit[1], None, int)

    # 发送数据
    send(sock, id(sock))

    sock.close()
