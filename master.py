# coding=utf-8
import copy
import random
import time

import numpy as np

from utils.codecs import repEncoder, repDecoder, mdsEncoder, mdsDecoder, ltEncoder, ltDecoder
from utils.connection import PORT
from utils.masterHandler import Handler
from utils.performanceHandler import repAnalytics, mdsAnalytics, ltAnalytics


# 输入：工作节点数slaveNum，矩阵A，向量x，迭代次数iteration，（方法名（rep，mds，lt），参数1，参数2...）如下
# params = {'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2}
# params = {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5}
# params = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}
def run(A, x, iteration, params):
    # 解析params
    strategy = params['strategy']
    slaveNum = params['p']

    row, col = A.shape
    # Ae = None
    # castMap = None
    if strategy == 'rep':
        repNum = params['repNum']
        Ae, castMap = repEncoder(A, repNum, slaveNum)
    elif strategy == 'mds':
        p = params['p']
        k = params['k']
        Ae, castMap = mdsEncoder(A, k, p)
    else:  # 'lt'
        c = params['c']
        delta = params['delta']
        alpha = params['alpha']
        Ae, castMap = ltEncoder(A, c, delta, alpha)

    # 正确值，用于对比
    trueRes = np.ravel(np.dot(A, x))

    subMatList = []
    # subMatSize = None
    if strategy == 'rep':
        repNum = params['repNum']
        subMatSize = int(row * repNum / slaveNum)
    elif strategy == 'mds':
        k = params['k']
        subMatSize = int(row / k)
    else:  # 'lt'
        alpha = params['alpha']
        subMatSize = int(alpha * row / slaveNum)

    for slave in range(slaveNum):
        startIndex = slave * subMatSize
        endIndex = startIndex + subMatSize
        subMatList.append((np.arange(startIndex, endIndex, 1), Ae[startIndex:endIndex, :], x))

    slaveKeys = [[] for _ in range(iteration)]
    slaveTimes = np.zeros((iteration, slaveNum))
    slaveComps = np.zeros((iteration, slaveNum))
    stopTime = np.zeros(iteration)
    for i in range(iteration):
        print('iteration %s' % i, end='')
        results = None
        while not results:
            results = Handler.run(PORT, subMatList)
        taskKeys = {}
        taskTimes = {}
        taskIndexes = {}
        taskValues = {}
        # encRes = None

        if strategy == 'lt':
            alpha = params['alpha']
            encRes = np.zeros(int(alpha * row))
        else:
            encRes = np.zeros(row, dtype=np.int)

        for slave in range(slaveNum):
            taskKeys[slave] = results[slave][0]
            taskTimes[slave] = results[slave][1]
            taskIndexes[slave] = results[slave][2]
            taskValues[slave] = results[slave][3]
            if strategy == 'lt':
                encRes[taskIndexes[slave]] = np.asarray(taskValues[slave])[:, 0]

        if strategy == 'rep':
            repNum = params['repNum']
            doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = repAnalytics(
                taskTimes,
                slaveNum,
                repNum)
            startIndex = 0
            for slave in doneList:
                slaveKeys[i].append(taskKeys[slave])
                encRes[startIndex:startIndex + subMatSize] = taskValues[slave]
                startIndex += subMatSize
            decRes = repDecoder(encRes, castMap, doneList)
        elif strategy == 'mds':
            p = params['p']
            k = params['k']
            doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = mdsAnalytics(
                taskTimes,
                p,
                k)
            startIndex = 0
            for slave in doneList:
                slaveKeys[i].append(taskKeys[slave])
                encRes[startIndex:startIndex + subMatSize] = taskValues[slave]
                startIndex += subMatSize
            decRes = mdsDecoder(encRes, castMap, doneList)
        else:  # 'lt'
            finishList = ltAnalytics(taskTimes, taskIndexes)
            ltMap = copy.deepcopy(castMap)
            decRes, doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = ltDecoder(
                encRes,
                ltMap,
                finishList,
                slaveNum,
                row)
            for slave in doneList:
                slaveKeys[i].append(taskKeys[slave])

        err = np.linalg.norm(decRes - trueRes) / np.linalg.norm(trueRes)
        print(', error=%s%%' % (err * 100))
    return slaveKeys, slaveTimes, slaveComps, stopTime


if __name__ == "__main__":
    startTime = time.time()
    np.random.seed(0)
    random.seed(0)

    row = 10000
    col = 1000
    iteration = 10

    # 测试使用，数据分析请见analyses目录
    params = {'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2}
    # params = {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5}
    # params = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}

    A = np.random.randint(256, size=(row, col))
    x = np.random.randint(256, size=(col, 1))

    keys, times, comps, stops = run(A, x, iteration, params)

    np.save('statistics/Test_' + params['strategy'] + 'Keys_' + params['id'] + '.npy', keys)
    np.save('statistics/Test' + params['strategy'] + 'Times_' + params['id'] + '.npy', times)
    np.save('statistics/Test' + params['strategy'] + 'Comps_' + params['id'] + '.npy', comps)
    np.save('statistics/Test' + params['strategy'] + 'StopTime_' + params['id'] + '.npy', stops)

    print('Average Latency = ' + str(np.mean(stops)))
    print('Run Time = ', str(time.time() - startTime), sep='')
