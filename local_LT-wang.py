# coding: utf-8

import copy
import os
import time
from multiprocessing import Pool

import numpy as np


def multiply(source):
    slaveRows = source[0]
    slaveMat = source[1]
    vect = source[2]
    slaveTimes = []
    slaveValues = []
    slaveIndexes = []
    rowNumber = slaveMat.shape[0]
    for index in range(rowNumber):
        startTime = time.process_time()
        slaveValues.append(np.dot(slaveMat[index], vect))
        slaveIndexes.append(slaveRows[index])
        slaveTimes.append((startTime, time.process_time()))
    return os.getpid(), slaveTimes, slaveIndexes, slaveValues


def RS(m, c, delta):
    # 返回鲁棒孤子分布，即选择每一行的概率
    R = c * np.log(m / delta) * np.sqrt(m)
    left = 0.0
    right = 0.0
    pivot = round(m / R)
    rho = np.zeros(m)
    for index in range(m):
        d = float(index + 1)
        if d == 1:
            right = 1 / float(m)
        else:
            right = 1 / (d * (d - 1))
        if 1 <= d < pivot:
            left = 1 / (d * pivot)
        elif d == pivot:
            left = np.log(R / delta) / pivot
        else:
            left = 0
        rho[index] = left + right
    prob = rho / np.sum(rho)
    return prob


def ltEncoder(mat, c, delta, alpha):
    # 返回按照RS分布抽取的行累加后形成的编码行，并记录映射
    rows, cols = mat.shape
    encRows = int(alpha * rows)
    prob = RS(rows, c, delta)
    encMat = np.zeros((encRows, cols), dtype=np.int64)
    encMap = []
    for encIndex in range(encRows):
        if encIndex % 100 == 0:
            print('\r[INFO] encode line : %s' % encIndex, end='', flush=True)
        d = 1 + np.random.choice(rows, size=None, replace=True, p=prob)  # 按概率有放回抽取单条编码行的度d（即此行由d条原始行叠加形成）
        srcIndex = np.random.choice(rows, size=d, replace=False, p=None)  # 随机从[0,rows)选择d条数据索引
        encMap.append(srcIndex.tolist())
        encMat[encIndex, :] = np.sum(mat[srcIndex, :], axis=0)
    print(' ... done')
    return encMat, encMap


def ltDecoder(encRes, encMap, finishList, slaveNum, row):
    # 采用遍历图的方式解码，从少的来，如果无法解码则再扩大编码行
    # encRes是计算结果b_e
    # finishList结构为（节点，编码行索引，完成时间）的有序递增排列
    decRes = np.zeros(row, dtype=np.int64)
    decRes[:] = -1  # 设一个不可能的值为初值
    decNum = 0  # 解码行数
    soleList = []  # 度为1的编码行列表，即编码行与原始行单独对应
    srcMap = [[] for _ in range(row)]  # 创建从编码行至原始行的映射
    beginNum = 0  # 解码扩大查找的起点
    findNum = row  # 解码使用的最大编码行数

    while findNum < len(encMap):
        while (not soleList) and (findNum < len(encMap)):
            # 第一次遍历到row处，即最低可能性解码行数
            for triple in finishList[beginNum:findNum]:
                encIndex = triple[1]
                blockMap = encMap[encIndex]
                for i in reversed(range(len(blockMap))):
                    srcIndex = blockMap[i]
                    if decRes[srcIndex] >= 0:  # 此原始行已被解码
                        encRes[encIndex] -= decRes[srcIndex]
                        blockMap.__delitem__(i)  # 从中去除已解码的原始行
                    else:
                        srcMap[srcIndex].append(encIndex)
                if len(blockMap) == 1:
                    soleList.append(encIndex)
            beginNum = findNum
            findNum += 1

        # 若存在1度的行则可解码，否则失败（later：或要等待更多的计算结果）
        if not soleList:
            break
        encIndex = soleList.pop()
        if encMap[encIndex]:  # 若一度的编码行仍然需要解码（存在）
            srcIndex = encMap[encIndex][-1]  # 这里encMap[encIndex]需要清空，放在下面一起处理
            decRes[srcIndex] = encRes[encIndex]  # 原始行的最终结果
            for index in srcMap[srcIndex]:  # 对于原始映射到的各个编码行，需要将此原始行的最终解码结果减去，并减去相应的索引
                if encMap[index].__contains__(srcIndex):
                    encRes[index] -= decRes[srcIndex]
                    encMap[index].remove(srcIndex)
                if len(encMap[index]) == 1:  # 可解码行
                    soleList.append(index)
            decNum += 1
            if decNum == row:
                break
    if decNum < row:
        print('[ERROR] insufficient decode rows.')

    # 所有计算完成的时间
    stopTime = finishList[findNum - 1][2]
    # 完成计算的节点序号
    doneList = []
    # 每个节点完成时间以及完成的总数
    slaveTimes = np.zeros(slaveNum)
    slaveComps = np.zeros(slaveNum)
    for i in reversed(range(len(finishList))):
        slaveTimes[finishList[i][0]] = max(slaveTimes[finishList[i][0]], finishList[i][2])
        slaveComps[finishList[i][0]] += 1
        if not doneList.__contains__(finishList[i][0]):
            doneList.append(finishList[i][0])
    print(', threshold=%s' % findNum, end='')
    return decRes, doneList, slaveTimes, slaveComps, stopTime


def ltAnalytics(taskTimes, taskIndexes):
    startTime = float('Inf')
    for slave in taskTimes:
        startTime = min(startTime, taskTimes[slave][0][0])
    # 将所有任务按（节点，索引，完成时间）排序（排序目标为完成时间升序）
    # 完成时间为从节点开始计算至完成本行计算的时间
    finishList = []
    for slave in taskTimes:
        finishList.extend([(slave, taskIndexes[slave][index], taskTimes[slave][index][1] - taskTimes[slave][0][0])
                           for index in range(len(taskIndexes[slave]))])  # 每行计算的完成时间
    finishList = sorted(finishList, key=lambda x: x[2])
    return finishList


if __name__ == '__main__':
    np.random.seed(0)
    slaveNum = 10
    row = 10000
    col = 1000
    c = 0.03
    delta = 0.5
    alpha = 2.0
    decThresh = 11057
    iteration = 10

    A = np.random.randint(256, size=(row, col))
    Ae, encMapAll = ltEncoder(A, c, delta, alpha)

    x = np.random.randint(256, size=(col, 1))
    trueRes = np.ravel(np.dot(A, x))

    subMatList = []
    subMatSize = int(alpha * row / slaveNum)
    for slave in range(slaveNum):
        startIndex = slave * subMatSize
        endIndex = startIndex + subMatSize
        subMatList.append((np.arange(startIndex, endIndex, 1), Ae[startIndex:endIndex, :], x))

    pool = Pool(slaveNum, maxtasksperchild=1)

    # In[11]:

    slaveKeys = [[] for _ in range(iteration)]
    slaveTimes = np.zeros((iteration, slaveNum))  # 每个工作节点的计算完成时间
    slaveComps = np.zeros((iteration, slaveNum))  # 每个工作节点的计算完成量
    stopTime = np.zeros(iteration)  # 每次迭代完成时间
    for i in range(iteration):
        print('iteration %s' % i, end='')
        results = pool.map(multiply, subMatList)

        taskKeys = {}
        taskTimes = {}
        taskIndexes = {}
        taskValues = {}
        encRes = np.zeros(int(alpha * row))
        encMap = copy.deepcopy(encMapAll)

        for slave in range(slaveNum):
            taskKeys[slave] = results[slave][0]
            taskTimes[slave] = results[slave][1]
            taskIndexes[slave] = results[slave][2]
            taskValues[slave] = results[slave][3]
            encRes[taskIndexes[slave]] = np.asarray(taskValues[slave])[:, 0]
        finishList = ltAnalytics(taskTimes, taskIndexes)

        # 根据finishList进行解码
        decRes, doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = ltDecoder(
            encRes,
            encMap,
            finishList,
            slaveNum,
            row)

        for slave in doneList:
            slaveKeys[i].append(taskKeys[slave])

        err = np.linalg.norm(decRes - trueRes) / np.linalg.norm(trueRes)
        print(', error=%s%%' % (err * 100))

    # print some slaveKeys, slaveTimes, slaveComps, stopTime
    print('Average Latency = ' + str(np.mean(stopTime)))
