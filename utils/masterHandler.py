# coding=utf-8
import copy
import socket
import socketserver
import threading
import time

import numpy as np

from utils.connection import send, receive, UUID, log, DataServer, DELAY


# 主节点函数
class Handler(socketserver.BaseRequestHandler):
    # 此处为静态变量
    server = None  # 服务句柄，用于控制服务端开关流程
    slaveRec = {}  # 工作节点状态记录器，状态有：1.不存在键值 2.register 3.bind 4.push 5.compute 6.pull 7.reject
    # 1.客户端首次连接或之前验证失败需要重新取得许可（applicant）
    # 2.register 已注册状态，主节点未对工作节点分配任务
    # 3.bind 已分配任务，未发送给工作节点
    # 4.push 已发送任务，工作节点未收到启动命令
    # 5.compute 工作节点已启动并计算完成，尝试连接主节点传送计算结果
    # 6.pull 计算结果已完成传输，但仍寻求连接，应主动拒绝连接信号
    # 7.reject 主节点暂时不需要工作节点，主动拒绝连接信号
    taskBinds = {}  # 记录节点key绑定的任务
    seqBinds = {}  # 记录key绑定的任务顺序，与inputList相同，保证输入输出的一致性
    inputList = []  # 总计算任务
    semInput = threading.Semaphore(1)  # 用于输入值冲突的信号量
    outputList = {}  # 工作节点的输出值列表
    semOutput = threading.Semaphore(1)  # 用于输入值冲突的信号量

    def __init__(self, request, client_address, server):
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        self.key = None  # 工作节点的唯一标志

    def setup(self):
        self.key = None

    def handle(self):
        # 必须考虑断线重连情况
        # 下面的判断将poll注释掉，这是因为在push后客户端主动与服务端解除握手，等计算完成后再尝试连接
        if self.verify() == 'member':  # 客户端通过验证，已分配key
            if not Handler.slaveRec.__contains__(self.key):
                return
            else:
                status = Handler.slaveRec[self.key]
            if status == 'verify':
                if self.bind():
                    self.push()
            elif status == 'bind':
                self.push()
            elif status == 'push':
                self.compute()
            elif status == 'compute':
                if self.pull():
                    self.reject()
                    Handler.close()
            elif status == 'pull':
                # 当工作节点发送完成后进入工作节点自身的下一轮循环，但主节点仍处于pull状态，这时需要处理冲突，
                # 即主节点需要向等待连接的工作节点发送拒绝信号
                self.reject()
                Handler.close()
            else:  # reject
                self.reject()

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
        elif self.register(msg):
            # 节点发送的是未知的key（可能之前的循环中持有并使用过）或为新
            # 需要将之前的key值复用，若为blank则注册新的key
            return 'member'
        return None

    # 注册函数先发送key:xxx给客户端，并期望收到accept消息，注册函数将返回成功或失败两种状态
    def register(self, key):
        if key == 'blank':
            key = UUID(Handler.slaveRec)
            if not send(self.request, 'key:' + key):
                return False
            msg = receive(self.request)
            if msg == 'accept':
                self.key = key
                Handler.slaveRec[self.key] = 'verify'
                log.debug('%s are verified.' % str(self.key))
                return True
        else:
            if send(self.request, 'pass'):
                self.key = key
                Handler.slaveRec[self.key] = 'verify'
                log.debug('%s are verified.' % str(self.key))
                return True
        return False

    # 将工作节点key与数据绑定，若绑定列表已满则向客户端发送reject，并在工作节点状态记录器中添加拒绝
    def bind(self):
        log.debug('new connection coming: %s' % str(self.key))
        Handler.semInput.acquire()
        if len(Handler.inputList):
            Handler.taskBinds[self.key] = Handler.inputList.pop()
            Handler.seqBinds[self.key] = len(Handler.inputList)
            Handler.slaveRec[self.key] = 'bind'
            log.debug('<tasks remain = %s>' % len(Handler.inputList))
            Handler.semInput.release()
            log.debug('new connection are bound: %s' % str(self.key))
            return True
        else:
            log.debug('<tasks remain = %s> : %s' % (len(Handler.inputList), str(self.key)))
            Handler.slaveRec[self.key] = 'reject'
            Handler.semInput.release()
            log.debug('new connection are rejected: %s' % str(self.key))
            send(self.request, 'reject')
            return False

    # 为工作节点发送计算任务
    def push(self):
        # while len(Handler.inputList):  # 等待：当所有计算任务分配完毕，则所有线程开始运行
        time.sleep(DELAY)
        if not send(self.request, 'push'):
            return False
        ds = DataServer()
        if not ds.pushData(self.request, Handler.taskBinds[self.key]):
            return False
        # if not send(self.request, Handler.taskBinds[self.key]):
        #     return False
        Handler.slaveRec[self.key] = 'push'
        log.debug('data have sent to: %s' % str(self.key))
        # # 补丁，保证工作节点开始运行时刻相同
        # flag = False
        # if receive(self.request):
        #     flag = True
        # status = np.array(list(Handler.slaveRec.values()))
        # while not (status == 'push').all():
        #     pass
        # send(self.request, 'accept')
        # # 补丁结束
        return True

    # 计划启动工作节点
    def compute(self):
        if receive(self.request) == 'Request Compute':
            # status = np.array(list(Handler.slaveRec.values()))
            # status = np.logical_or(
            #     np.logical_or(status == 'push', status == 'compute'),
            #     np.logical_or(status == 'pull', status == 'reject'))
            # if not status.all():
            #     send(self.request, 'negative')
            # elif send(self.request, 'positive'):
            #     Handler.slaveRec[self.key] = 'compute'
            #     return True
            time.sleep(0.1)
            status = np.array(list(Handler.slaveRec.values()))
            status = np.logical_or(
                np.logical_or(status == 'push', status == 'compute'),
                np.logical_or(status == 'pull', status == 'reject'))
            while not status.all():
                status = np.array(list(Handler.slaveRec.values()))
                status = np.logical_or(
                    np.logical_or(status == 'push', status == 'compute'),
                    np.logical_or(status == 'pull', status == 'reject'))
            if send(self.request, 'positive'):
                if receive(self.request) == 'ack':
                    Handler.slaveRec[self.key] = 'compute'
                    log.debug('computing: %s' % str(self.key))
                    return True
        return False

    # 等待slave返回计算结果
    def pull(self):
        ds = DataServer()
        data = ds.pullData(self.request)
        # data = receive(self.request)
        if not data:
            log.debug("receiving data fail: %s" % str(self.key))
            return False
        else:
            Handler.semOutput.acquire()
            Handler.outputList[Handler.seqBinds[self.key]] = data
            Handler.slaveRec[self.key] = 'pull'
            log.debug('data have been received from: %s' % str(self.key))
            Handler.semOutput.release()
            return True

    def reject(self):
        if Handler.slaveRec[self.key] != 'reject':
            Handler.slaveRec[self.key] = 'reject'
        time.sleep(DELAY)
        send(self.request, 'reject')

    # 当所有线程执行完毕时，关闭服务（尝试关闭socket server），增加reject情况
    @staticmethod
    def close():
        status = np.array(list(Handler.slaveRec.values()))
        try:
            if np.logical_or(status == 'pull', status == 'reject').all():
                Handler.server.shutdown()
                Handler.server.__shutdown_request = False
        except Warning as w:
            log.debug('status = %s' % status)
            log.debug(w)
        except Exception:
            pass

    # 在主节点程序中调用以执行分布式任务
    @staticmethod
    def run(port, inputList):
        # 心态崩了
        Handler.semInput.acquire()
        Handler.reset()
        Handler.inputList = copy.deepcopy(inputList)
        Handler.semInput.release()

        Handler.server = ThrTCPSrv(('', port), Handler)
        # while not Handler.inputList:
        #     time.sleep(0.1)
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
        Handler.outputList = {}


class ThrTCPSrv(socketserver.ThreadingTCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
