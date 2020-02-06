# coding=utf-8
import numpy as np


def repEncoder(mat, repNum, slaveNum):
    rows, cols = mat.shape
    encRows = int(rows * repNum)
    subRows = int(rows * repNum / slaveNum)
    chunkNum = int(slaveNum / repNum)  # 每个工作节点工作重叠，因此chunks记录了最小工作节点数
    repMat = (slaveNum, chunkNum)  # 记录工作节点数与最小需求节点数
    encMat = np.zeros((encRows, cols), dtype=np.int)
    for i in range(slaveNum):  # 为工作节点指派了存在相互重叠的任务
        j = int(i / repNum)
        encMat[i * subRows:(i + 1) * subRows, :] = mat[j * subRows:(j + 1) * subRows, :]
    return encMat, repMat


def repDecoder(encRes, repMat, doneList):
    slaveNum = repMat[0]
    repNum = int(repMat[0] / repMat[1])
    decRes = np.zeros(encRes.shape, dtype=np.int)
    rows = encRes.shape[0]
    subRows = int(rows * repNum / slaveNum)
    encIndex = 0
    for chunk in doneList:
        group = chunk // repNum  # 找到
        decIndex = group * subRows
        decRes[decIndex:decIndex + subRows] = encRes[encIndex:encIndex + subRows]
        encIndex += subRows
    return decRes


def mdsEncoder(mat, k, p):
    rows, cols = mat.shape
    encRows = int(p * rows / k)
    subRows = int(rows / k)
    mdsMat = np.random.normal(size=(p, k))  # (p,k) MDS编码，用于编码以及后面的逆矩阵方式解码
    encMat = np.zeros((encRows, cols), dtype=np.float32)
    for i in range(p):  # p
        for j in range(k):  # k
            # 按k个循环，放在新的A_enc上，权值为服从正态分布的随机数
            encMat[i * subRows:(i + 1) * subRows, :] += mdsMat[i][j] * mat[j * subRows:(j + 1) * subRows, :]
    return encMat, mdsMat


def mdsDecoder(encRes, mdsMat, doneList):
    # doneList是前面k个最先完成任务的工作节点
    p, k = mdsMat.shape
    matInv = np.linalg.inv(mdsMat[doneList, :])
    decRes = np.zeros(encRes.shape)
    rows = encRes.shape[0]
    subRows = int(rows / k)
    for i in range(k):
        decpos = i * subRows
        for j in range(k):
            startIndex = j * subRows
            decRes[decpos:decpos + subRows] += matInv[i, j] * encRes[startIndex:startIndex + subRows]
    return decRes
