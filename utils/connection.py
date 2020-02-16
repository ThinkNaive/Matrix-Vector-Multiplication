import logging
import pickle
import random
import socket
import threading
import time
import uuid

# 日志语句输出等级开关
level = logging.INFO
logging.basicConfig(level=level, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
log = logging.getLogger()

# 失败等待延迟
DELAY = 1
# 服务器地址
HOST = "127.0.0.1"
PORT = 12315

# 缓冲区修改标记信号量
sem = threading.Semaphore(1)


# 编码函数，将输入的计算任务编码为字节并发送
def encode(data):
    return pickle.dumps(data)


# 解码函数，对工作节点计算结果进行解码
def decode(data):
    return pickle.loads(data)


# 主节点向工作节点发送分片矩阵数据，发送完成后最后发送EOF作为结束标志
# 发送值为编码后的字符串
# lock为线程同步锁，保证单个端口缓冲不抢占
def send(request, data, lock=True):
    msg = encode(data) + 'EOF'.encode('utf-8')  # 将数据结构编码为bytes
    status = trySend(request, msg, lock)
    time.sleep(0.1)  # 解决粘包问题
    return status


# 判断发送缓冲区大小并发送数据
def trySend(request, msg, lock):
    pt = 0
    while pt < len(msg):
        if lock:
            sem.acquire()
        try:
            bufSize = request.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            if bufSize > 0:
                request.send(msg[pt:pt + bufSize])
                pt += bufSize
        except Exception as e:
            log.debug(e)
            if lock:
                sem.release()
            return False
        if lock:
            sem.release()
    return True


# 主节点等待工作节点返回分片计算结果，接收完成的标志为EOF
# 返回值为编码后的字符串
def receive(request):
    rec = b''
    try:
        while True:
            bufSize = request.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            if bufSize == 0:
                log.debug('receive buffer empty')
                rec = None
                break
            data = request.recv(bufSize)  # type:bytes
            if not data:
                log.debug('receive data empty')
                rec = None
                break
            if data.endswith(b'EOF'):
                data = data[:-3]
                rec += data
                break
            rec += data
        rec = decode(rec)
    except Exception as e:
        log.debug(e)
        rec = None
    return rec


# 生成不重复的uuid（8位）
def UUID(table: dict):
    key = uuid.uuid1().hex[:-24]
    while table.__contains__(key):
        key = uuid.uuid1().hex[:-24]
    return key


# 新建随机端口sock，用于大量数据传输
class DataServer:
    def __init__(self):
        self.host = HOST
        self.port = None
        self.server = None
        self.sock = None

    def assignPort(self, request):
        # 申请端口
        while self.port is None:
            self.port = random.randint(5001, 65535)
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server.bind((self.host, self.port))
                self.server.listen(1)
            except socket.error:
                self.port = None
                self.server.close()
                time.sleep(DELAY)
        # 向工作节点发送端口信息
        if send(request, self.port):
            self.sock, _ = self.server.accept()
            if receive(request) != 'ready':
                time.sleep(DELAY)
                self.server.close()
                return False
        return True

    def pushData(self, request, data):
        # 向工作节点协议端口
        if not self.assignPort(request):
            return False

        # 向工作节点发送数据
        if send(self.sock, data, lock=False):
            self.server.close()
            return True

        self.server.close()
        return False

    def pullData(self, request):
        # 向工作节点协议端口
        if not self.assignPort(request):
            return None

        # 从工作节点接收数据
        return receive(self.sock)


class DataClient:
    def __init__(self, stop):
        self.host = HOST
        self.port = None
        self.sock = None
        self.stop = stop

    def queryPort(self, request):
        # 请求数据传输端口信息
        self.port = receive(request)
        if self.port and 5001 <= self.port <= 65535:
            # 建立主节点通信端口
            try:
                time.sleep(DELAY)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                if not send(request, 'ready'):
                    self.sock.close()
                    return False
            except socket.error:
                send(request, 'error')
                self.sock.close()
                return False
        return True

    def pullData(self, request):
        # 请求数据传输端口信息
        if not self.queryPort(request) or self.stop[0]:
            return None

        # 从主节点接收数据
        return receive(self.sock)

    def pushData(self, request, data):
        # 请求数据传输端口信息
        if not self.queryPort(request) or self.stop[0]:
            return False

        # 向主节点发送数据
        log.info('dataSize=%s' % len(pickle.dumps(data)))
        if send(self.sock, data, lock=False):
            self.sock.close()
            return True

        try:
            self.sock.close()
        except Exception:
            pass
        return False


# class Tree(object):
#     def __init__(self, data):
#         self.type = None  # 自身类型
#         self.shape = None  # 内部尺寸
#         self.data = None  # 子数据或若干子树，由type和shape决定
#         self.dtype = None  # 当类型为array时的内部数据类型，如int32，float64
#
#         if isinstance(data, int):
#             self.type = 'int'
#             self.data = data
#         elif isinstance(data, float):
#             self.type = 'float'
#             self.data = data
#         elif isinstance(data, np.ndarray):
#             self.type = 'array'
#             if len(data.shape) != 0 and np.prod(data.shape) != 0:
#                 self.shape = data.shape
#                 self.dtype = str(data.dtype)
#                 self.data = np.reshape(data, np.prod(data.shape))  # 将数据转换为一维数组存放
#         elif isinstance(data, list):
#             self.type = 'list'
#             if len(data) > 0:
#                 self.shape = len(data)
#                 self.data = []
#             for unit in data:  # unit可能类型为tuple, int, float, list, array
#                 self.data.append(Tree(unit))
#         elif isinstance(data, tuple):
#             self.type = 'tuple'
#             if len(data) > 0:
#                 self.shape = len(data)
#                 self.data = []
#             for unit in data:  # unit可能类型为tuple, int, float, list, array
#                 self.data.append(Tree(unit))
#
#     @staticmethod
#     def print(node, depth):
#         for i in range(depth):
#             print('  ', end='')
#         print(node.type, end=' ')
#         if node.type == 'int' or node.type == 'float':
#             print(node.data)
#         elif node.type == 'array':
#             if not node.shape:
#                 print('None')
#             else:
#                 print('shape=' + str(node.shape), end=' ')
#                 print('dtype=' + node.dtype, end=' ')
#                 print(node.data)
#         elif node.type == 'list' or node.type == 'tuple':
#             if node.shape > 0:
#                 print()
#                 for data in node.data:
#                     node.print(data, depth + 1)
#             else:
#                 print('None')
#
#     @staticmethod
#     def encode(node):
#         pass
