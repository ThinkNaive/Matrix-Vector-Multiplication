# coding=utf-8
import numpy as np
from utils.connection import log


def repEncoder(mat, repNum, slaveNum):
    rows, cols = mat.shape
    encRows = int(rows * repNum)
    subRows = int(rows * repNum / slaveNum)
    chunkNum = int(slaveNum / repNum)  # 每个工作节点工作重叠，因此chunks记录了最小工作节点数
    encMap = (slaveNum, chunkNum)  # 记录工作节点数与最小需求节点数
    encMat = np.zeros((encRows, cols), dtype=np.float64)
    for i in range(slaveNum):  # 为工作节点指派了存在相互重叠的任务
        j = int(i / repNum)
        encMat[i * subRows:(i + 1) * subRows, :] = mat[j * subRows:(j + 1) * subRows, :]
    return encMat, encMap


def repDecoder(encRes, repMat, doneList):
    slaveNum = repMat[0]
    repNum = int(repMat[0] / repMat[1])
    decRes = np.zeros(encRes.shape, dtype=np.float64)
    rows = encRes.shape[0]
    subRows = int(rows * repNum / slaveNum)
    encIndex = 0
    for chunk in doneList:
        group = chunk // repNum  # 找到一个chunk对应的组号
        decIndex = group * subRows
        decRes[decIndex:decIndex + subRows] = encRes[encIndex:encIndex + subRows]
        encIndex += subRows
    return decRes


def mdsEncoder(mat, k, p):
    rows, cols = mat.shape
    encRows = int(p * rows / k)
    subRows = int(rows / k)
    encMap = np.random.normal(size=(p, k))  # (p,k) MDS编码，用于编码以及后面的逆矩阵方式解码
    encMat = np.zeros((encRows, cols), dtype=np.float64)
    for i in range(p):  # p
        for j in range(k):  # k
            # 按k个循环，放在新的A_enc上，权值为服从正态分布的随机数
            encMat[i * subRows:(i + 1) * subRows, :] += encMap[i][j] * mat[j * subRows:(j + 1) * subRows, :]
    return encMat, encMap


def mdsDecoder(encRes, mdsMat, doneList):
    # doneList是前面k个最先完成任务的工作节点
    p, k = mdsMat.shape
    matInv = np.linalg.inv(mdsMat[doneList, :])
    decRes = np.zeros(encRes.shape)
    rows = encRes.shape[0]
    subRows = int(rows / k)
    for i in range(k):
        decIndex = i * subRows
        for j in range(k):
            startIndex = j * subRows
            decRes[decIndex:decIndex + subRows] += matInv[i, j] * encRes[startIndex:startIndex + subRows]
    return decRes


def RS(m, c, delta):
    # 返回鲁棒孤子分布，即选择每一行的概率
    R = c * np.log(m / delta) * np.sqrt(m)
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
    encMat = np.zeros((encRows, cols), dtype=np.float64)
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
    decRes = np.zeros(row, dtype=np.float64)
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
                if encMap[index].__contains__(srcIndex):  # 对于新加入的编码行，可能是冗余的，需要判断是否已处理srcIndex
                    encRes[index] -= decRes[srcIndex]
                    encMap[index].remove(srcIndex)
                if len(encMap[index]) == 1:  # 可解码行
                    soleList.append(index)
            decNum += 1
            if decNum == row:
                break
    if decNum < row:
        print('[ERROR] insufficient decode rows.')

    # 理想节点的计算完成时间
    idealTime = finishList[row - 1][2]
    # 所有计算完成的时间
    stopTime = finishList[findNum - 1][2]
    # 完成计算的节点序号
    doneList = []
    # 每个节点完成时间以及完成的总数
    slaveTimes = np.zeros(slaveNum)
    slaveComps = np.zeros(slaveNum)
    for i in reversed(range(findNum)):
        slaveTimes[finishList[i][0]] = max(slaveTimes[finishList[i][0]], finishList[i][2])
        slaveComps[finishList[i][0]] += 1
        if not doneList.__contains__(finishList[i][0]):
            doneList.append(finishList[i][0])
    print(', threshold=%s' % findNum, end='', flush=True)
    return decRes, doneList, slaveTimes, slaveComps, stopTime, idealTime
