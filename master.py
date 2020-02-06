# coding=utf-8
import numpy as np

from analyses.codecs import repEncoder, repDecoder, mdsEncoder, mdsDecoder
from analyses.timeAnalytics import repAnalytics, mdsAnalytics
from utils.MasterHandler import Handler
from utils.connection import HOST, PORT


# 输入：工作节点数slaveNum，矩阵A，向量x，迭代次数iteration，（方法名（rep，mds，lt），参数1，参数2...）如下
# ('rep', p, repNum)
# ('mds', p, k)
# ('lt', p, c, delta, alpha)
def run(A, x, iteration, params):
    # 解析params
    strategy = params[0]
    slaveNum = params[1]

    row, col = A.shape
    Ae = None
    castMat = None
    if strategy == 'rep':
        repNum = params[2]
        Ae, castMat = repEncoder(A, repNum, slaveNum)
    elif strategy == 'mds':
        p = params[1]
        k = params[2]
        Ae, castMat = mdsEncoder(A, k, p)

    # 正确值，用于对比
    trueResult = np.ravel(np.dot(A, x))

    subMatList = []
    subMatSize = None
    if strategy == 'rep':
        repNum = params[2]
        subMatSize = int(row * repNum / slaveNum)
    elif strategy == 'mds':
        k = params[2]
        subMatSize = int(row / k)

    for slave in range(slaveNum):
        startIndex = slave * subMatSize
        endIndex = startIndex + subMatSize
        subMatList.append((np.arange(startIndex, endIndex, 1), Ae[startIndex:endIndex, :], x))

    slaveKeys = [[] for _ in range(iteration)]
    slaveTimes = np.zeros((iteration, slaveNum))
    slaveComps = np.zeros((iteration, slaveNum))
    stopTime = np.zeros(iteration)
    for i in range(iteration):
        print('iteration %s, error = ' % i, end='')
        results = Handler.run(HOST, PORT, subMatList)

        taskKeys = {}
        taskTimes = {}
        taskIndexes = {}
        taskValues = {}
        for slave in range(slaveNum):
            taskKeys[slave] = results[slave][0]
            taskTimes[slave] = results[slave][1]
            taskIndexes[slave] = results[slave][2]
            taskValues[slave] = results[slave][3]
        # doneIndexes = None
        doneList = None
        if strategy == 'rep':
            repNum = params[2]
            doneIndexes, doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = repAnalytics(
                taskTimes,
                taskIndexes,
                slaveNum,
                repNum)
        elif strategy == 'mds':
            p = params[1]
            k = params[2]
            doneIndexes, doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = mdsAnalytics(
                taskTimes,
                taskIndexes,
                p,
                k)

        encodeResult = np.zeros(row, dtype=np.int)
        startIndex = 0
        for slave in doneList:
            slaveKeys[i].append(taskKeys[slave])
            encodeResult[startIndex:startIndex + subMatSize] = taskValues[slave]
            startIndex += subMatSize
        decodeResult = None
        if strategy == 'rep':
            decodeResult = repDecoder(encodeResult, castMat, doneList)
        elif strategy == 'mds':
            decodeResult = mdsDecoder(encodeResult, castMat, doneList)
        err = np.linalg.norm(decodeResult - trueResult) / np.linalg.norm(trueResult)
        print('%s%%' % (err * 100))
    return slaveKeys, slaveTimes, slaveComps, stopTime


if __name__ == "__main__":
    np.random.seed(0)

    row = 1000
    col = 1000
    iteration = 10

    # index = 2
    # params = ('rep', 10, 2)

    index = 1
    params = ('mds', 10, 5)

    A = np.random.randint(256, size=(row, col))
    x = np.random.randint(256, size=(col, 1))

    keys, times, comps, stops = run(A, x, iteration, params)

    np.save('statistics/' + params[0] + 'Times_' + str(index) + '.npy', times)
    np.save('statistics/' + params[0] + 'Comps_' + str(index) + '.npy', comps)
    np.save('statistics/' + params[0] + 'StopTime_' + str(index) + '.npy', stops)

    print('Average Latency = ' + str(np.mean(stops)))
