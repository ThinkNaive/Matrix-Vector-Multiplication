import numpy as np


def time_analytics_rep(task_times, task_keys, num_workers, num_rep):
    start_time = float('Inf')
    worker_times = np.zeros(num_workers)
    # Logging times
    for worker in task_times:
        start_time = min(start_time,
                         task_times[worker][0][0])  # Global start time is the time at which fastest worker starts
        worker_times[worker] = task_times[worker][-1][1]  # Stop time of last task at worker
    # Identifying workers used in decoding
    done_list = []  # List of done workers from each group
    done_keys = {}
    stop_time = 0
    for worker_num in range(0, num_workers, num_rep):
        worker_group = worker_times[worker_num:worker_num + num_rep]
        fastest_worker = np.argmin(worker_group) + worker_num
        done_list.append(fastest_worker)
        stop_time = max(stop_time, worker_times[fastest_worker])  # Slowest fastest worker
        done_keys[fastest_worker] = task_keys[fastest_worker][:]
    # Logging computations by each worker
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
    worker_times -= start_time
    stop_time -= start_time
    return done_keys, done_list, worker_times, worker_comps, stop_time


def time_analytics_mds(task_times, task_keys, num_workers, mdsnum):
    start_time = float('Inf')
    worker_times = np.zeros(num_workers)
    # Logging times
    for worker in task_times:
        start_time = min(start_time,
                         task_times[worker][0][0])  # Global start time is the time at which fastest worker starts
        worker_times[worker] = task_times[worker][-1][1]  # Stop time of last task at worker
    # Identifying workers used in decoding
    done_list = []  # List of done workers from each group
    done_keys = {}
    stop_time = 0
    worker_order = np.argsort(worker_times)
    done_list = worker_order[:mdsnum]  # fastest k workers
    stop_time = worker_times[worker_order[mdsnum - 1]]  # Time of the kth fastest worker
    for worker in done_list:
        done_keys[worker] = task_keys[worker][:]
    # Count computations by each worker
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
    worker_times -= start_time
    stop_time -= start_time
    return done_keys, done_list, worker_times, worker_comps, stop_time


def time_analytics_lt(task_times, task_keys, num_workers, decthresh):
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
