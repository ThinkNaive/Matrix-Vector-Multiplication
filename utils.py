import numpy as np


class Tree(object):
    def __init__(self, data):
        self.type = None  # 自身类型
        self.shape = None  # 内部尺寸
        self.data = None  # 子数据或若干子树，由type和shape决定

        if isinstance(data, int):
            self.type = int
            self.data = data
        elif isinstance(data, float):
            self.type = float
            self.data = data
        elif isinstance(data, np.ndarray):
            self.type = np.ndarray
            if len(data.shape) != 0 and np.prod(data.shape) != 0:
                self.shape = data.shape
                self.data = np.reshape(data, np.prod(data.shape))  # 将数据转换为一维数组存放
        elif isinstance(data, list):
            self.type = list
            if len(data) > 0:
                self.shape = len(data)
                self.data = []
            for unit in data:  # unit可能类型为tuple, int, float, list, array
                self.data.append(Tree(unit))
        elif isinstance(data, tuple):
            self.type = tuple
            if len(data) > 0:
                self.shape = len(data)
                self.data = []
            for unit in data:  # unit可能类型为tuple, int, float, list, array
                self.data.append(Tree(unit))

    @staticmethod
    def print(node, depth):
        for i in range(depth):
            print('  ', end='')
        print(node.type, end=' ')
        if node.type == int or node.type == float:
            print(node.data)
        elif node.type == np.ndarray:
            if not node.shape:
                print('None')
            else:
                print('shape=' + str(node.shape), end=' ')
                print('dtype=' + str(node.data.dtype), end=' ')
                print(node.data)
        elif node.type == list or node.type == tuple:
            if node.shape > 0:
                print()
                for data in node.data:
                    node.print(data, depth+1)
            else:
                print('None')


if __name__ == '__main__':
    var = ([[1], [2]], np.array([[1, 2], [3, 4]]), np.array([[0.1, 0.2], [0.3, 0.4]]), ([1, 2], [3]), np.zeros(()))
    tree = Tree(var)
    Tree.print(tree, 0)
