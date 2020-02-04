# coding=utf-8
import threading
import time

import numpy as np

from SlaveHandler import Handler


def multiply(source):
    vect = source[2]
    slaveRows = source[0]
    slaveMat = source[1]
    slaveTimes = []
    slaveValues = []
    slaveIndexes = []
    rowNumber = slaveMat.shape[0]
    for index in range(rowNumber):
        startTime = time.process_time()
        slaveValues.append(np.dot(slaveMat[index], vect))
        slaveIndexes.append(slaveRows[index])
        slaveTimes.append((startTime, time.process_time()))
    return slaveTimes, slaveIndexes, slaveValues


class Work:
    def __init__(self):
        self.stop = [False]

    def end(self):
        self.stop[0] = True

    def run(self):
        HOST = "127.0.0.1"
        PORT = 12315
        handle = Handler(HOST, PORT, self.stop)  # 传入引用变量

        while not self.stop[0]:
            # 接收数据，若接收数据为None表明未分配计算任务，则直接退出
            data = handle.poll()
            if not data:
                print(handle.key + ' is rejected.')
                time.sleep(1)
            else:
                print(handle.key + ' is obtained.')
                # 计算任务
                result = (handle.key,) + multiply(data)
                # 发送数据
                handle.push(result)
            handle.close()


if __name__ == "__main__":
    works = []
    try:
        for i in range(10):
            work = Work()
            t = threading.Thread(target=work.run)
            works.append(work)
            t.start()

        while True:
            pass

    except KeyboardInterrupt:
        for work in works:
            work.end()
