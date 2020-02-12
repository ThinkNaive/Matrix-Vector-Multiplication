# coding=utf-8
import random
import time

import numpy as np

from master import run

if __name__ == '__main__':
    rows = [500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    col = 10000
    iteration = 10
    params = [{'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2},
              {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5},
              {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}]
    for param in params:
        for row in rows:
            print('--- Scale Experiment - ' + param['strategy'] + ' - ' + str(row) + ' ---')
            startTime = time.time()
            np.random.seed(0)
            random.seed(0)

            A = np.random.randint(256, size=(row, col))
            x = np.random.randint(256, size=(col, 1))

            keys, times, comps, stops = run(A, x, iteration, param)

            np.save('statistics/' + param['strategy'] + 'Keys_' + str(row) + '.npy', keys)
            np.save('statistics/' + param['strategy'] + 'Times_' + str(row) + '.npy', times)
            np.save('statistics/' + param['strategy'] + 'Comps_' + str(row) + '.npy', comps)
            np.save('statistics/' + param['strategy'] + 'StopTime_' + str(row) + '.npy', stops)

            print('Average Latency = ' + str(np.mean(stops)))
            print('Run Time = ', str(time.time() - startTime))
