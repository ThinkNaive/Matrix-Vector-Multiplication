# coding=utf-8
import SocketServer
import threading
import sys
import numpy as np


# 主节点函数，用于替换程序中的Pool
# 此类需要进行初始化，Handler.A_list需要赋初值
class Handler(SocketServer.BaseRequestHandler):
    # 此处为静态变量
    bindings = []           # 工作节点-计算任务绑定列表
    A_list = []             # 总计算任务
    semInput = threading.Semaphore(1)    # 用于输入值冲突的信号量
    b_list = []             # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        # 此处为成员变量
        self.binding = None     # 工作节点-计算任务绑定
        self.A_unit = None      # 单片计算任务

    def handle(self):
        print('new connection coming: %s' % str(self.client_address))
        Handler.semInput.acquire()
        if len(Handler.A_list):
            self.A_unit = Handler.A_list.pop()
            self.binding = (self.client_address, self.A_unit)
            Handler.bindings.append(self.binding)
            Handler.semInput.release()
        else:
            Handler.semInput.release()
            return

        print('new connection assigned: %s' % str(self.client_address))
        while len(Handler.A_list):    # 当所有计算任务分配完毕，则所有线程开始运行
            pass

        # 向slave发送所有数据
        # 如何解码数据？见如下例子：
        #   from numpy import array
        #   data = (get data from receive).decode('utf-8')
        #   A_unit = tuple(eval(data))
        self.send(self.request, self.A_unit)

        # 等待slave返回计算结果
        b = self.receive(self.request)
        if not b:
            print("receiving data fail: %s" % str(self.client_address))
        else:
            Handler.semOutput.acquire()
            Handler.b_list.append(b)
            Handler.semOutput.release()

    # 主节点向工作节点发送分片矩阵数据，发送完成后最后发送EOF作为结束标志
    @classmethod
    def send(cls, request, data):
        try:
            dat = str(data).encode('utf-8')
            request.sendall(dat)
            dat = 'EOF'.encode('utf-8')
            request.sendall(dat)
        except Exception as e:
            print(e.message)

    # 主节点等待工作节点返回分片计算结果，接收完成的标志为EOF
    @classmethod
    def receive(cls, request):
        b = ''
        try:
            while True:
                rec = request.recv(1024).decode('utf-8')
                if not rec:
                    b = None
                    break
                if rec == 'EOF':
                    break
                b += rec
        except Exception as e:
            print(e.message)
            b = None
        return b
