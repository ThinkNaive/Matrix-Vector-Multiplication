import numpy as np


# 副本策略的时间和计算性能分析
def repAnalytics(taskTimes, slaveNum, repNum):
    startTime = float('Inf')
    slaveTimes = np.zeros(slaveNum)
    # 获取全局最先运算的节点时间作为启动时间
    # 获取每个节点最晚的结束时间作为节点完成计算的时间
    for slave in taskTimes:
        startTime = min(startTime, taskTimes[slave][0][0])  # 全局最早运行计算任务的时间
        slaveTimes[slave] = taskTimes[slave][-1][1]  # 每个工作节点的停止计算时间
    # 取得用于解码的节点
    doneList = []
    stopTime = 0

    # rep方法需要记录计算相同任务的一组工作节点集合，并找出这组的最快完成时间
    # 工作节点分配任务（rep=2）组别为0,0,1,1,2,2,...
    for slave in range(0, slaveNum, repNum):
        group = slaveTimes[slave:slave + repNum]
        fastest = np.argmin(group) + slave  # 最快完成某个chunk（组）的节点编号
        doneList.append(fastest)
        stopTime = max(stopTime, slaveTimes[fastest])  # 记录所有组的最晚完成时间作为运行终止时间
    # 记录所有完成时间早于停止时间的计算任务，求总数
    slaveComps = np.zeros(slaveNum)
    for slave in taskTimes:
        for task in taskTimes[slave]:
            taskStopTime = task[1]
            if taskStopTime <= stopTime:
                # 统计在stopTime前的计算数
                slaveComps[slave] += 1
            else:
                slaveTimes[slave] = taskStopTime
                break
    slaveTimes -= startTime  # 转化为工作节点运行时间
    stopTime -= startTime  # 转化为工作节点运行时间
    return doneList, slaveTimes, slaveComps, stopTime


# MDS策略的时间和计算性能分析
def mdsAnalytics(taskTimes, p, k):
    startTime = float('Inf')
    slaveTimes = np.zeros(p)
    # 获取全局最先运算的节点时间作为启动时间
    # 获取每个节点最晚的结束时间作为节点完成计算的时间
    for slave in taskTimes:
        startTime = min(startTime, taskTimes[slave][0][0])
        slaveTimes[slave] = taskTimes[slave][-1][1]
    # 获取入选的前k个工作节点
    order = np.argsort(slaveTimes)
    doneList = order[:k]  # 前k个最快工作节点，mds会舍去较慢节点的工作量
    stopTime = slaveTimes[order[k - 1]]  # 获取排名第k个（入选的最后一名）工作节点的完成时刻
    # 分别为每个工作节点计算工作量
    slaveComps = np.zeros(p)
    for slave in taskTimes:
        for task in taskTimes[slave]:
            taskStopTime = task[1]
            if taskStopTime <= stopTime:
                slaveComps[slave] += 1
            else:
                slaveTimes[slave] = taskStopTime
                break
    slaveTimes -= startTime  # 转化为工作节点运行时间
    stopTime -= startTime  # 转化为工作节点运行时间
    return doneList, slaveTimes, slaveComps, stopTime


# LT策略的时间排序算法，分析需要与解码同时进行
def ltAnalytics(taskTimes, taskIndexes):
    startTime = float('Inf')
    for slave in taskTimes:
        startTime = min(startTime, taskTimes[slave][0][0])
    # 将所有任务按（节点，索引，完成时间）排序（排序目标为完成时间升序）
    # 完成时间为从节点开始计算至完成本行计算的时间
    finishList = []
    for slave in taskTimes:
        finishList.extend([(slave, taskIndexes[slave][index], taskTimes[slave][index][1] - startTime)
                           for index in range(len(taskIndexes[slave]))])  # 每行计算的完成时间
    finishList = sorted(finishList, key=lambda x: x[2])
    return finishList
