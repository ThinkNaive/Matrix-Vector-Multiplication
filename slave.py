# coding=utf-8
import threading
import time

import numpy as np

from utils.connection import HOST, PORT
from utils.slaveHandler import Handler


def multiply(source):
    slaveRows = source[0]
    slaveMat = source[1]
    vect = source[2]
    taskTime = []
    taskValue = []
    taskIndex = []
    rowNumber = slaveMat.shape[0]
    for index in range(rowNumber):
        startTime = time.process_time()
        taskValue.append(np.dot(slaveMat[index], vect))
        taskIndex.append(slaveRows[index])
        taskTime.append((startTime, time.process_time()))
    return taskTime, taskIndex, taskValue


def delaySimulate(data, initDelay, ratioDelay):
    taskTime = []
    taskIndex = data[1]
    taskValue = data[2]
    for (start, end) in data[0]:
        taskTime.append((start + initDelay, start + initDelay + ratioDelay * (end - start)))
    return taskTime, taskIndex, taskValue


class Work:
    def __init__(self, param):
        self.key = param['key']
        self.initDelay = param['init']
        self.ratioDelay = param['ratio']
        self.stop = [False]

    def end(self):
        self.stop[0] = True

    def run(self):
        handle = Handler(HOST, PORT, self.key, self.stop)  # 传入引用变量

        while not self.stop[0]:
            # 接收数据，若接收数据为None表明未分配计算任务，则直接退出
            data = handle.pull()
            if data:
                # 询问是否可计算
                handle.compute()
                # 计算任务
                result = (handle.key,) + delaySimulate(multiply(data), self.initDelay, self.ratioDelay)
                # 发送数据
                handle.push(result)
            handle.close()


if __name__ == "__main__":
    threadNum = 1  # 一台物理机上最多运行几个工作节点
    params = [{'key': 'client-a', 'init': 0.0, 'ratio': 1.0},
              {'key': 'client-b', 'init': 1.0, 'ratio': 2.0},
              {'key': 'client-c', 'init': 0.0, 'ratio': 1.0},
              {'key': 'client-d', 'init': 0.5, 'ratio': 2.0},
              {'key': 'client-e', 'init': 0.0, 'ratio': 1.0},
              {'key': 'client-f', 'init': 1.0, 'ratio': 1.5},
              {'key': 'client-g', 'init': 0.0, 'ratio': 1.0},
              {'key': 'client-h', 'init': 0.5, 'ratio': 1.5},
              {'key': 'client-i', 'init': 0.0, 'ratio': 1.0},
              {'key': 'client-j', 'init': 0.0, 'ratio': 1.0}]
    works = []
    try:
        for i in range(threadNum):
            work = Work(params[i])
            t = threading.Thread(target=work.run)
            works.append(work)
            t.start()

        while True:
            pass

    except KeyboardInterrupt:
        for work in works:
            work.end()
