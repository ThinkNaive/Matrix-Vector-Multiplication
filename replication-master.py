import numpy as np

from MasterHandler import Handler
from timeAnalytics import repTimeAnalytics


def repEncoder(mat, repNum, slaveNum):
    rows, cols = mat.shape
    encRows = int(rows * repNum)
    subRows = int(rows * repNum / slaveNum)
    chunkNum = int(slaveNum / repNum)  # 每个工作节点工作重叠，因此chunks记录了最小工作节点数
    repMat = np.zeros((slaveNum, chunkNum))  # Mapping at client corresponding to r-Repetition code
    encMat = np.zeros((encRows, cols), dtype=np.int)
    for i in range(slaveNum):  # 为工作节点指派了存在相互重叠的任务
        j = int(i / repNum)
        encMat[i * subRows:(i + 1) * subRows, :] = mat[j * subRows:(j + 1) * subRows, :]
    return encMat, repMat


def repDecoder(encRes, repMat, doneList):
    slaveNum = int(repMat.shape[0])
    repNum = int(repMat.shape[0] / repMat.shape[1])
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


if __name__ == "__main__":
    np.random.seed(0)

    HOST = "127.0.0.1"
    PORT = 12315

    slaveNum = 10
    repNum = 2
    row = 1000
    col = 1000
    iteration = 10
    A = np.random.randint(256, size=(row, col))
    Ae, repMat = repEncoder(A, repNum, slaveNum)

    # 正确值，用于对比
    x = np.random.randint(256, size=(col, 1))
    trueResult = np.ravel(np.dot(A, x))

    subMatList = []
    subMatSize = int(row * repNum / slaveNum)
    for slave in range(slaveNum):
        startIndex = slave * subMatSize
        endIndex = startIndex + subMatSize
        subMatList.append((np.arange(startIndex, endIndex, 1), Ae[startIndex:endIndex, :], x))

    slaveTimes = np.zeros((iteration, slaveNum))
    slaveComps = np.zeros((iteration, slaveNum))
    stopTime = np.zeros(iteration)
    for i in range(iteration):
        print('iteration %s, error = ' % i, end='')
        results = Handler.run(HOST, PORT, subMatList)

        taskTimes = {}
        taskIndexes = {}
        taskValues = {}
        for slave in range(slaveNum):
            taskTimes[slave] = results[slave][1]
            taskIndexes[slave] = results[slave][2]
            taskValues[slave] = results[slave][3]
        doneIndexes, doneList, slaveTimes[i, :], slaveComps[i, :], stopTime[i] = repTimeAnalytics(
            taskTimes,
            taskIndexes,
            slaveNum,
            repNum)
        encodeResult = np.zeros(row, dtype=np.int)
        startIndex = 0
        for slave in doneList:
            encodeResult[startIndex:startIndex + subMatSize] = taskValues[slave]
            startIndex += subMatSize
        decodeResult = repDecoder(encodeResult, repMat, doneList)
        err = np.linalg.norm(decodeResult - trueResult) / np.linalg.norm(trueResult)
        print('%s%%' % (err * 100))
        np.save('statistics/repError_' + str(i) + '.npy', decodeResult - trueResult)

    # 保存性能分析数据
    np.save('statistics/repSlaveTimes_' + str(repNum) + '.npy', slaveTimes)
    np.save('statistics/repSlaveComps_' + str(repNum) + '.npy', slaveComps)
    np.save('statistics/repSlaveStopTime_' + str(repNum) + '.npy', stopTime)

    print('Average Latency = ' + str(np.mean(stopTime)))