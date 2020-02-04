# coding=utf-8
import copy
import socketserver
import threading

import numpy as np

from utils import send, receive, UUID, verbose


# 主节点函数
class Handler(socketserver.BaseRequestHandler):
    # 此处为静态变量
    server = None  # 服务句柄，用于控制服务端开关流程
    slaveRec = {}  # 工作节点状态记录器，状态有：1.不存在键值 2.register 3.bind 4.push 5.poll 6.reject
    taskBinds = {}  # 记录节点key绑定的任务
    seqBinds = {}  # 记录key绑定的任务顺序，与inputList相同，保证输入输出的一致性
    inputList = []  # 总计算任务
    semInput = threading.Semaphore(1)  # 用于输入值冲突的信号量
    outputList = {}  # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        # 此处为成员变量
        self.key = None  # 工作节点的唯一标志

    def handle(self):
        # 必须考虑断线重连情况
        # 下面的判断将poll注释掉，这是因为在push后客户端主动与服务端解除握手，等计算完成后再尝试连接
        self.key = None
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
                # 当工作节点发送完成后进入工作节点自身的下一轮循环，但主节点仍处于poll状态，这时需要处理冲突，
                # 即主节点需要向等待连接的工作节点发送拒绝信号
                self.reject()
                Handler.close()
            else:  # reject
                self.reject()
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
        elif msg == 'blank':
            return 'applicant'
        else:  # 节点发送的是未知的key（可能之前的循环中持有并使用过）
            if self.register(msg):  # 需要将之前的key值复用
                return 'member'
        return None

    # 注册函数先发送key:xxx给客户端，并期望收到accept消息，注册函数将返回成功或失败两种状态
    def register(self, key=None):
        if not key:
            key = UUID(Handler.slaveRec)
            if not send(self.request, 'key:' + key):
                return False
            msg = receive(self.request)
            if msg == 'accept':
                self.key = key
                Handler.slaveRec[key] = 'register'
                return True
        else:
            if send(self.request, 'pass'):
                self.key = key
                Handler.slaveRec[self.key] = 'register'
                return True
        return False

    # 将工作节点key与数据绑定，若绑定列表已满则向客户端发送reject，并在工作节点状态记录器中添加拒绝
    def bind(self):
        if verbose:
            print('new connection coming: %s' % str(self.key))
        Handler.semInput.acquire()
        if len(Handler.inputList):
            Handler.taskBinds[self.key] = Handler.inputList.pop()
            Handler.seqBinds[self.key] = len(Handler.inputList)
            Handler.slaveRec[self.key] = 'bind'
            if verbose:
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
        if not send(self.request, Handler.taskBinds[self.key]):
            return False
        Handler.slaveRec[self.key] = 'push'
        if verbose:
            print('data have sent to: %s' % str(self.key))
        return True

    # 等待slave返回计算结果
    def poll(self):
        data = receive(self.request)
        if not data:
            if verbose:
                print("receiving data fail: %s" % str(self.key))
            return False
        else:
            Handler.semOutput.acquire()
            Handler.outputList[Handler.seqBinds[self.key]] = data
            Handler.slaveRec[self.key] = 'poll'
            if verbose:
                print('data have been received from: %s' % str(self.key))
            Handler.semOutput.release()
            return True

    def reject(self):
        if send(self.request, 'reject'):
            Handler.slaveRec[self.key] = 'reject'
            return True
        return False

    # 当所有线程执行完毕时，关闭服务（尝试关闭socket server），增加reject情况
    @staticmethod
    def close():
        status = np.array(list(Handler.slaveRec.values()))
        if np.logical_or(status == 'poll', status == 'reject').all():
            Handler.server.shutdown()

    # 在主节点程序中调用以执行分布式任务
    @staticmethod
    def run(host, port, inputList):
        Handler.reset()
        ADDR = (host, port)
        Handler.server = socketserver.ThreadingTCPServer(ADDR, Handler)
        Handler.inputList = copy.deepcopy(inputList)
        Handler.server.allow_reuse_address = True
        Handler.server.serve_forever()
        Handler.server.server_close()
        return Handler.outputList

    # 重置静态变量
    @staticmethod
    def reset():
        Handler.server = None
        Handler.slaveRec = {}
        Handler.taskBinds = {}
        Handler.seqBinds = {}
        Handler.inputList = []
        Handler.outputList = {}
