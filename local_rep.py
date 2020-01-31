# coding: utf-8

# In[1]:


import os
import time
from multiprocessing import Pool

import numpy as np

from time_analytics_local import time_analytics_rep


# In[2]:


def vect_mult(workerdata):
    pid = os.getpid()
    np.random.seed(0)
    # vect = np.random.randint(256, size=(10000, 1))
    vect = workerdata[2]
    worker_rows = workerdata[0]
    worker_mat = workerdata[1]
    task_times = []
    task_values = []
    task_keys = []
    num_rows = worker_mat.shape[0]
    for row in range(num_rows):
        start_time = time.process_time()
        task_values.append(np.dot(worker_mat[row], vect))
        task_keys.append(worker_rows[row])
        task_times.append((start_time, time.process_time()))
    return pid, task_times, task_keys, task_values


# In[3]:


def rep_encoder(mat, num_rep, num_workers):
    rows, cols = mat.shape
    encrows = int(rows * num_rep)
    subrows = int(rows * num_rep / num_workers)
    num_chunks = int(num_workers / num_rep)  # 每个工作节点工作重叠，因此chunks记录了最小工作节点数
    repmat = np.zeros((num_workers, num_chunks))  # Mapping at client corresponding to r-Repetition code
    encmat = np.zeros((encrows, cols), dtype=np.int)
    for i in range(num_workers):  # 为工作节点指派了存在相互重叠的任务
        j = int(i / num_rep)
        encmat[i * subrows:(i + 1) * subrows, :] = mat[j * subrows:(j + 1) * subrows, :]
    return encmat, repmat


# In[4]:


def rep_decoder(encres, repmat, done_list):
    # done_list is the list of groups
    # num_workers is the total number of workers
    num_workers = int(repmat.shape[0])
    num_rep = int(repmat.shape[0] / repmat.shape[1])
    decres = np.zeros(encres.shape, dtype=np.int)
    rows = encres.shape[0]
    subrows = int(rows * num_rep / num_workers)
    encpos = 0
    for chunk_num in done_list:
        group_num = chunk_num // num_rep
        decpos = group_num * subrows
        decres[decpos:decpos + subrows] = encres[encpos:encpos + subrows]
        encpos += subrows
    return decres


if __name__ == '__main__':
    # In[5]:

    num_workers = 10
    num_rep = 1
    num_rows = 10000
    num_cols = 10000
    A = np.random.randint(256, size=(num_rows, num_cols))
    A_enc, repmat = rep_encoder(A, num_rep, num_workers)

    # In[6]:

    # True Result
    np.random.seed(0)
    x = np.random.randint(256, size=(10000, 1))
    res = np.ravel(np.dot(A, x))

    # In[7]:

    A_list = []
    blocksize = int(num_rows * num_rep / num_workers)
    for worker_num in range(num_workers):
        start_pos = worker_num * blocksize
        end_pos = start_pos + blocksize
        A_list.append((np.arange(start_pos, end_pos, 1), A_enc[start_pos:end_pos, :], x))

    # In[8]:

    pool = Pool(num_workers, maxtasksperchild=1)
    # start_time = time.time()

    # In[9]:

    num_iters = 10
    worker_times = np.zeros((num_iters, num_workers))
    worker_comps = np.zeros((num_iters, num_workers))
    stop_time = np.zeros(num_iters)
    for iter in range(num_iters):
        print('iteration %s, error=' % iter, end='')
        results = pool.map(vect_mult, A_list)
        #     pool.close()
        #     pool.join()
        task_times = {}
        task_keys = {}
        task_values = {}
        for worker_num in range(num_workers):
            task_times[worker_num] = results[worker_num][1]
            task_keys[worker_num] = results[worker_num][2]
            task_values[worker_num] = results[worker_num][3]
        done_keys, done_list, worker_times[iter, :], worker_comps[iter, :], stop_time[iter] = time_analytics_rep(
            task_times,
            task_keys,
            num_workers,
            num_rep)
        encres = np.zeros(num_rows, dtype=np.int)
        startpos = 0
        for worker_num in done_list:
            encres[startpos:startpos + blocksize] = task_values[worker_num]
            startpos += blocksize
        decres = rep_decoder(encres, repmat, done_list)
        err = np.linalg.norm(decres - res) / np.linalg.norm(res)
        print('%s%%' % (err * 100))
    # Saving
    np.save('statistics/worker_times_rep_' + str(num_rep) + '.npy', worker_times)
    np.save('statistics/worker_comps_rep_' + str(num_rep) + '.npy', worker_comps)
    np.save('statistics/stop_time_rep_' + str(num_rep) + '.npy', stop_time)

    # In[10]:

    print('Average Latency = ' + str(np.mean(stop_time)))

    # In[ ]:
