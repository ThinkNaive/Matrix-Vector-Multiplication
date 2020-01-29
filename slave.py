# coding=utf-8
import os
import socket
import time
import numpy as np
from numpy import array


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
    A_unit = None

    sock = tryConnect(ADDR)

    # 接收数据
    rec = ''
    try:
        while True:
            data = sock.recv(1024)  # type:bytes
            if not data:
                print('receive data error')
                sock.close()
                exit()
            data = data.decode('utf-8')  # type:str
            if data.endswith('EOF'):
                data = data[:-3]
                rec += data
                break
            rec += data
    except Exception as e:
        print(e)

    # 处理数据
    A_unit = tuple(eval(rec))
    print(A_unit)
    # cal = np.sum(A_unit[1], None, int)

    # 发送数据
    while True:
        try:
            # 目前需要先确定发送的数据格式，并写编码解码方法
            # sock.sendall(str((A_unit[0], cal)).encode('utf-8'))
            data = "!@#$%^&*()"  # type:str
            for i in range(8):
                data += data
            sock.sendall(data.encode('utf-8'))
            sock.sendall('EOF'.encode('utf-8'))
            break
        except Exception as e:
            print(e)
            break

    sock.close()
