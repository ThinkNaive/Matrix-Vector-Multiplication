import numpy as np


def repAnalytics(task_times, task_keys, num_workers, num_rep):
    start_time = float('Inf')
    worker_times = np.zeros(num_workers)
    # 获取全局最先运算的节点时间作为启动时间
    # 获取每个节点最晚的结束时间作为节点完成计算的时间
    for worker in task_times:
        start_time = min(start_time,
                         task_times[worker][0][0])  # Global start time is the time at which fastest worker starts
        worker_times[worker] = task_times[worker][-1][1]  # Stop time of last task at worker
    # 取得用于解码的节点
    done_list = []  # List of done workers from each group
    done_keys = {}
    stop_time = 0

    # rep方法需要记录计算相同任务的一组工作节点集合，并找出这组的最快完成时间
    # 工作节点分配任务（rep=2）组别为0,0,1,1,2,2,...
    for worker_num in range(0, num_workers, num_rep):
        worker_group = worker_times[worker_num:worker_num + num_rep]
        fastest_worker = np.argmin(worker_group) + worker_num  # 最快完成某个chunk（组）的节点编号
        done_list.append(fastest_worker)
        stop_time = max(stop_time, worker_times[fastest_worker])  # 记录所有组的最晚完成时间作为运行终止时间
        done_keys[fastest_worker] = task_keys[fastest_worker][:]
    # 记录所有完成时间早于停止时间的计算任务，求总数
    worker_comps = np.zeros(num_workers)
    for worker in task_times:
        for worker_task in task_times[worker]:
            task_stop_time = worker_task[1]
            if task_stop_time <= stop_time:
                # Computation completed before stop time
                worker_comps[worker] += 1
            else:
                worker_times[worker] = task_stop_time  # Equivalent to cancellation after stop_time
                break
    worker_times -= start_time  # 转化为工作节点运行时间
    stop_time -= start_time
    return done_keys, done_list, worker_times, worker_comps, stop_time


def mdsAnalytics(task_times, task_keys, num_workers, mdsnum):
    start_time = float('Inf')
    worker_times = np.zeros(num_workers)
    # 获取全局最先运算的节点时间作为启动时间
    # 获取每个节点最晚的结束时间作为节点完成计算的时间
    for worker in task_times:
        start_time = min(start_time,
                         task_times[worker][0][0])  # Global start time is the time at which fastest worker starts
        worker_times[worker] = task_times[worker][-1][1]  # Stop time of last task at worker
    # 获取入选的前k个工作节点
    done_keys = {}
    worker_order = np.argsort(worker_times)
    done_list = worker_order[:mdsnum]  # fastest k workers，mds会舍去较慢节点的工作量
    stop_time = worker_times[worker_order[mdsnum - 1]]  # Time of the kth fastest worker，获取排名第k个（入选的最后一名）工作节点的完成时刻
    for worker in done_list:
        done_keys[worker] = task_keys[worker][:]
    # 分别为每个工作节点计算工作量
    worker_comps = np.zeros(num_workers)
    for worker in task_times:
        for worker_task in task_times[worker]:
            task_stop_time = worker_task[1]
            if task_stop_time <= stop_time:
                # Computation completed before stop time
                worker_comps[worker] += 1
            else:
                worker_times[worker] = task_stop_time  # Equivalent to cancellation after stop_time
                break
    worker_times -= start_time  # 转化为工作节点运行时间
    stop_time -= start_time  # 转化为工作节点运行时间
    return done_keys, done_list, worker_times, worker_comps, stop_time


def ltAnalytics(task_times, task_keys, num_workers, decthresh):
    start_time = float('Inf')
    worker_times = np.zeros(num_workers)
    comp_times_list = []
    # Logging times
    for worker in task_times:
        start_time = min(start_time,
                         task_times[worker][0][0])  # Global start time is the time at which fastest worker starts
        comp_times_list.extend([worker_task[1] for worker_task in task_times[worker]])
        worker_times[worker] = task_times[worker][-1][1]  # Stop time of last task at worker
    # Identifying stopping time
    comp_times_sorted = sorted(comp_times_list)
    stop_time = comp_times_sorted[decthresh - 1]
    # Identifying computations used in decoding
    done_list = []  # List of keys of done computations
    worker_comps = np.zeros(num_workers)
    for worker in task_times:
        for (worker_task, task_key) in zip(task_times[worker], task_keys[worker]):
            task_stop_time = worker_task[1]
            if task_stop_time <= stop_time:
                # Computation completed before stop time
                worker_comps[worker] += 1
                done_list.append(task_key)
            else:
                worker_times[worker] = task_stop_time  # Equivalent to cancellation after stop_time
                break
    worker_times -= start_time
    stop_time -= start_time
    return done_list, worker_times, worker_comps, stop_time
