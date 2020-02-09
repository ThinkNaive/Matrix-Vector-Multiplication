# coding=utf-8
import socket
import time

from utils.connection import send, receive, DELAY


# 工作节点函数
class Handler:
    def __init__(self, host, port, signal):
        self.key = None
        self.addr = (host, port)
        self.sock = None
        self.stop = signal

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while (not self.stop[0]) and sock.connect_ex(self.addr):
            time.sleep(DELAY)
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('connecting to ' + str(self.addr) + ' ...')
        if self.stop[0]:
            sock.close()
            exit()
        return sock

    # 工作节点在进行认证过程中若有必要则进行注册，因此在主方法中无需调用register
    def verify(self):
        msg = receive(self.sock)
        if msg == 'verify':
            if not self.key:
                if send(self.sock, 'blank'):
                    return self.register()
            else:
                if send(self.sock, self.key):
                    if receive(self.sock) == 'pass':
                        return True
        return False

    def register(self):
        msg = receive(self.sock)  # type:str
        if msg.startswith('key:'):
            if send(self.sock, 'accept'):
                self.key = msg[4:]
                return True
        return False

    # 工作节点向主节点获取计算任务，若未能分配则返回None
    def poll(self):
        while not self.stop[0]:
            self.sock = self.connect()
            if not self.verify():
                self.sock.close()
                time.sleep(DELAY)
                continue
            print(str(self.key) + ' poll verified.')
            # 开始任务传输通信
            msg = receive(self.sock)
            if msg == 'reject':
                self.sock.close()
                print(self.key + ' poll rejected.')
                return None
            if msg:
                self.sock.close()
                print(self.key + ' got data.')
                return msg
            # 已建立连接但传输计算任务失败，需要重启工作节点
            self.sock.close()
            time.sleep(DELAY)
        if self.stop[0]:
            self.sock.close()
            exit()

    # 工作节点向主节点发送计算结果，主节点必记录工作节点在绑定列表中
    def push(self, data):
        while not self.stop[0]:
            self.sock = self.connect()
            if not self.verify():
                self.sock.close()
                time.sleep(DELAY)
                continue
            print(str(self.key) + ' push verified.')
            # 开始任务传输通信
            if send(self.sock, data):
                self.sock.close()
                print(self.key + ' sent data.')
                return
            time.sleep(DELAY)
        if self.stop[0]:
            self.sock.close()
            exit()

    # 终止
    def close(self):
        self.sock.close()
        self.sock = None
