# coding=utf-8
import socketserver
import threading

import numpy as np

from utils import send, receive, UUID


# 主节点函数
class Handler(socketserver.BaseRequestHandler):
    # 此处为静态变量
    server = None  # 服务句柄，用于控制服务端开关流程
    bindings = []  # 工作节点-计算任务绑定列表
    slaveRec = {}  # 工作节点状态记录器，状态有：1.不存在键值 2.register 3.bind 4.push 5.poll 6.reject
    inputList = []  # 总计算任务
    semInput = threading.Semaphore(1)  # 用于输入值冲突的信号量
    outputList = []  # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        # 此处为成员变量
        self.binding = None  # 工作节点-计算任务绑定
        self.input = None  # 单片计算任务
        self.key = None  # 工作节点的唯一标志

    def handle(self):
        # 必须考虑断线重连情况
        # 下面的判断将poll注释掉，这是因为在push后客户端主动与服务端解除握手，等计算完成后再尝试连接
        status = self.verify()
        if not status:  # 验证失败
            return
        elif status == 'member':  # 客户端通过验证，已分配key
            if Handler.slaveRec[self.key] == 'register':
                if not self.bind():
                    return
                if not self.push():
                    return
                # if not self.poll():
                #     return
                Handler.close()
            elif Handler.slaveRec[self.key] == 'bind':
                if not self.push():
                    return
                # if not self.poll():
                #     return
                Handler.close()
            elif Handler.slaveRec[self.key] == 'push':
                if not self.poll():
                    return
                Handler.close()
            elif Handler.slaveRec[self.key] == 'poll':
                Handler.close()
        else:  # 客户端首次连接或之前验证失败需要重新取得许可（applicant）
            if not self.register():
                return
            if not self.bind():
                return
            if not self.push():
                return
            # if not self.poll():
            #     return
            Handler.close()

    # 验证函数发起验证请求，将返回三种状态，member：客户端已在绑定列表，或applicant：新客户端等待分配，或None：连接错误
    def verify(self):
        if not send(self.request, "verify"):
            return None
        msg = receive(self.request)  # 若首次连接，客户端需要发送'blank'作为验证信息
        if not msg:
            return None
        if Handler.slaveRec.__contains__(msg):
            self.key = msg
            if send(self.request, "pass"):
                return 'member'
        else:
            return 'applicant'
        return None

    # 注册函数先发送key:xxx给客户端，并期望收到accept消息，注册函数将返回成功或失败两种状态
    def register(self):
        key = UUID(Handler.slaveRec)
        if not send(self.request, 'key:'+key):
            return False
        msg = receive(self.request)
        if msg == 'accept':
            self.key = key
            Handler.slaveRec[key] = 'register'
            return True
        return False

    # 将工作节点key与数据绑定，若绑定列表已满则向客户端发送reject，并在工作节点状态记录器中添加拒绝
    def bind(self):
        print('new connection coming: %s' % str(self.key))
        Handler.semInput.acquire()
        if len(Handler.inputList):
            self.input = Handler.inputList.pop()
            self.binding = (self.key, self.input)
            Handler.bindings.append(self.binding)
            Handler.slaveRec[self.key] = 'bind'
            print('new connection are bound: %s' % str(self.key))
            Handler.semInput.release()
            return True
        else:
            Handler.semInput.release()
            Handler.slaveRec[self.key] = 'reject'
            send(self.request, 'reject')
            return False

    # 为工作节点发送计算任务
    def push(self):
        while len(Handler.inputList):  # 等待：当所有计算任务分配完毕，则所有线程开始运行
            pass
        if not send(self.request, self.input):
            return False
        Handler.slaveRec[self.key] = 'push'
        print('data have sent to: %s' % str(self.key))
        return True

    # 等待slave返回计算结果
    def poll(self):
        data = receive(self.request)
        if not data:
            print("receiving data fail: %s" % str(self.key))
            return False
        else:
            Handler.semOutput.acquire()
            Handler.outputList.append(data)
            Handler.slaveRec[self.key] = 'poll'
            print('data have been received from: %s' % str(self.key))
            Handler.semOutput.release()
            return True

    # 当所有线程执行完毕时，关闭服务（尝试关闭socket server），增加reject情况
    @staticmethod
    def close():
        status = np.array(list(Handler.slaveRec.values()))
        if np.logical_or(status == 'poll', status == 'reject').all():
            Handler.server.shutdown()

    # 在主节点程序中调用以执行分布式任务
    @staticmethod
    def run(host, port, inputList):
        ADDR = (host, port)
        Handler.server = socketserver.ThreadingTCPServer(ADDR, Handler)
        Handler.inputList = inputList
        Handler.server.allow_reuse_address = True
        Handler.server.serve_forever()
        Handler.server.server_close()
