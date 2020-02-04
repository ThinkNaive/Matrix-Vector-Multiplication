# coding=utf-8
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


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315

    while True:
        handle = Handler(HOST, PORT)

        # 接收数据，若接收数据为None表明未分配计算任务，则直接退出
        data = handle.poll()
        if not data:
            print('shutdown please')
            time.sleep(1)
        else:
            print('obtain key = ' + handle.key)

            # 计算任务
            result = (handle.key,) + multiply(data)

            # 发送数据
            handle.push(result)

            # 终止并等待下一次任务
            handle.close()
