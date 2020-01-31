# coding=utf-8
import socketserver
import threading
from utils import send, receive


# 主节点函数，用于替换程序中的Pool
# 此类需要进行初始化，Handler.inputList\Handler.srvHandle需要赋初值
class Handler(socketserver.BaseRequestHandler):
    # 此处为静态变量
    srvHandle = None  # 服务句柄，用于控制服务端开关流程
    bindings = []  # 工作节点-计算任务绑定列表
    slaveNum = 0  # 工作节点数量
    inputList = []  # 总计算任务
    semInput = threading.Semaphore(1)  # 用于输入值冲突的信号量
    outputList = []  # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        # 此处为成员变量
        self.binding = None  # 工作节点-计算任务绑定
        self.input = None  # 单片计算任务

    def handle(self):
        print('new connection coming: %s' % str(self.client_address))
        Handler.semInput.acquire()
        if len(Handler.inputList):
            self.input = Handler.inputList.pop()
            self.binding = (self.client_address, self.input)
            Handler.bindings.append(self.binding)
            Handler.slaveNum += 1
            Handler.semInput.release()
        else:
            Handler.semInput.release()
            return

        print('new connection assigned: %s' % str(self.client_address))
        while len(Handler.inputList):  # 当所有计算任务分配完毕，则所有线程开始运行
            pass

        # 向slave发送所有数据
        send(self.request, self.input)
        print('data have sent to: %s' % str(self.client_address))

        # 等待slave返回计算结果
        b = receive(self.request)
        if not b:
            print("receiving data fail: %s" % str(self.client_address))
        else:
            Handler.semOutput.acquire()
            Handler.outputList.append(b)
            Handler.slaveNum -= 1
            print('data have been received from: %s' % str(self.client_address))
            Handler.semOutput.release()

        # 当所有线程执行完毕时，关闭服务
        if not Handler.slaveNum:
            Handler.srvHandle.shutdown()
