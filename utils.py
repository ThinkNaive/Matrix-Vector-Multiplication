import pickle
import uuid


# 编码函数，将输入的计算任务编码为字节并发送
def encode(data):
    return pickle.dumps(data)


# 解码函数，对工作节点计算结果进行解码
def decode(data):
    return pickle.loads(data)


# 主节点向工作节点发送分片矩阵数据，发送完成后最后发送EOF作为结束标志
# 发送值为编码后的字符串
def send(request, data):
    try:
        msg = encode(data)  # 将数据结构编码为bytes
        request.sendall(msg)
        msg = 'EOF'.encode('utf-8')
        request.sendall(msg)
        return True
    except Exception as e:
        print(e)
        return False


# 主节点等待工作节点返回分片计算结果，接收完成的标志为EOF
# 返回值为编码后的字符串
def receive(request):
    rec = b''
    try:
        while True:
            data = request.recv(1024)  # type:bytes
            if not data:
                print('receive data error')
                rec = None
                break
            if data.endswith(b'EOF'):
                data = data[:-3]
                rec += data
                break
            rec += data
        rec = decode(rec)
    except Exception as e:
        print(e)
        rec = None
    return rec


# 生成不重复的uuid（8位）
def UUID(table: dict):
    key = uuid.uuid1().hex[:-24]
    while table.__contains__(key):
        key = uuid.uuid1().hex[:-24]
    return key


# 日志语句输出开关
verbose = False  # type:bool

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


if __name__ == '__main__':
    pass
    # var = ([[1], [2]], np.array([[1, 2], [3, 4]]), np.array([[0.1, 0.2], [0.3, 0.4]]), ([1, 2], [3]), np.zeros(()))
    # tree = Tree(var)
    # Tree.print(tree, 0)
