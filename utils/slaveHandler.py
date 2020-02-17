# coding=utf-8
import socket
import time

from utils.connection import send, receive, DELAY, DataClient, log


# 工作节点函数
class Handler:
    def __init__(self, host, port, key, signal):
        self.key = key
        self.addr = (host, port)
        self.sock = None
        self.stop = signal

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while (not self.stop[0]) and sock.connect_ex(self.addr):
            sock.close()
            time.sleep(DELAY)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            log.info('connecting to ' + str(self.addr) + ' ...')
        if self.stop[0]:
            try:
                sock.shutdown(2)
            except socket.error:
                pass
            sock.close()
            exit()
        sock.settimeout(15)
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
    def pull(self):
        while not self.stop[0]:
            self.sock = self.connect()
            if not self.verify():
                self.sock.shutdown(2)
                self.sock.close()
                time.sleep(DELAY)
                continue
            log.info(str(self.key) + ' pull verified.')
            # 开始任务传输通信
            msg = receive(self.sock)
            if msg == 'reject':
                self.sock.shutdown(2)
                self.sock.close()
                log.info(self.key + ' pull rejected.')
                time.sleep(DELAY)
                return None
            if msg == 'push':
                log.info(self.key + ' acquiring data.')
                dc = DataClient(self.stop)
                msg = dc.pullData(self.sock)
                # msg = receive(self.sock)
                if msg:
                    log.info(self.key + ' got data.')
                    self.sock.shutdown(2)
                    self.sock.close()
                    return msg
                # # 补丁，保证工作节点开始运行时刻相同
                # if send(self.sock, 'accept'):
                #     echo = receive(self.sock)
                #     print(' %s' % echo, end='')
                # print()
                # # 补丁结束
            # 已建立连接但传输计算任务失败，需要重启工作节点
            self.sock.shutdown(2)
            self.sock.close()
            time.sleep(DELAY)
        self.sock.shutdown(2)
        self.sock.close()
        exit()

    # 工作节点发送请求连接并期望得到开始运行指令
    def compute(self):
        while not self.stop[0]:
            self.sock = self.connect()
            if not self.verify():
                self.sock.shutdown(2)
                self.sock.close()
                time.sleep(DELAY)
                continue
            log.info(str(self.key) + ' compute verified.')
            # 开始任务传输通信
            if send(self.sock, 'Request Compute'):
                msg = receive(self.sock)
                if msg == 'positive':
                    time.sleep(0.1)
                    if send(self.sock, 'ack'):
                        try:
                            self.sock.shutdown(2)
                            self.sock.close()
                        except Exception:
                            break
                        log.info(self.key + ' compute start.')
                        return True
            log.info(self.key + ' compute rejected.')
            try:
                self.sock.shutdown(2)
                self.sock.close()
            except Exception:
                pass
            time.sleep(DELAY)
        self.sock.close()
        exit()

    # 工作节点向主节点发送计算结果，主节点必记录工作节点在绑定列表中
    def push(self, data):
        while not self.stop[0]:
            self.sock = self.connect()
            if not self.verify():
                self.sock.shutdown(2)
                self.sock.close()
                time.sleep(DELAY)
                continue
            log.info(str(self.key) + ' push verified.')
            # 开始任务传输通信
            dc = DataClient(self.stop)
            if dc.pushData(self.sock, data):
                self.sock.shutdown(2)
                self.sock.close()
                log.info(self.key + ' sent data.')
                time.sleep(DELAY)
                return
            self.sock.shutdown(2)
            self.sock.close()
            log.info(self.key + ' push rejected.')
            time.sleep(DELAY)
        self.sock.shutdown(2)
        self.sock.close()
        exit()

    # 终止
    def close(self):
        try:
            self.sock.shutdown(2)
            self.sock.close()
        except Exception:
            pass
        self.sock = None
