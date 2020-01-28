# coding=utf-8
import SocketServer
import threading
import sys
import numpy as np


# 主节点函数，用于替换程序中的Pool
# 此类需要进行初始化，Handler.A_list、Handler.count、Handler.sem需要赋初值
class Handler(SocketServer.BaseRequestHandler):
    bindings = []           # 工作节点-计算任务绑定列表
    A_list = []             # 总计算任务
    count = sys.maxint      # 总计算任务分片数
    semInput = threading.Semaphore(1)    # 用于输入值冲突的信号量
    b_list = []             # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        self.binding = None     # 工作节点-计算任务绑定
        self.A_unit = None      # 单片计算任务

    def handle(self):
        print('new connection coming: %s' % str(self.client_address))
        Handler.semInput.acquire()
        if len(Handler.A_list):
            self.A_unit = Handler.A_list.pop()
            self.binding = (self.client_address, self.A_unit)
            Handler.bindings.append(self.binding)
            Handler.count -= 1
            Handler.semInput.release()
        else:
            Handler.semInput.release()
            return

        print('new connection assigned: %s' % str(self.client_address))
        while Handler.count:    # 当所有计算任务分配完毕，则所有线程开始运行
            pass

        # 向slave发送所有数据
        # 如何解码数据？见如下例子：
        #   from numpy import array
        #   data = (get data from receive).decode('utf-8')
        #   A_unit = tuple(eval(data))
        data = str(self.A_unit)
        self.request.sendall(data.encode('utf-8'))
        # 等待slave返回计算结果
        # b = receive(self.request, semOutput)      # 这是要补充的函数
        # Handler.semOutput.acquire()
        # Handler.b_list.append(b)
        # Handler.semOutput.release()
