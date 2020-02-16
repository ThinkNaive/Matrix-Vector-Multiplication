# coding=utf-8
import random
import time

import numpy as np

from master import run

if __name__ == '__main__':
    rows = [500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000]
    col = 10000
    iteration = 10
    params = [
        # {'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 1},
        # {'id': '2', 'strategy': 'rep', 'p': 10, 'repNum': 2},
        {'id': '3', 'strategy': 'mds', 'p': 10, 'k': 5},
        {'id': '4', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}
    ]

    for param in params:
        for row in rows:
            # time.sleep(DELAY)
            print('--- Scale Experiment - ' + param['strategy'] + ' - ' + str(row) + ' ---')
            startTime = time.time()
            np.random.seed(0)
            random.seed(0)

            A = np.random.randint(256, size=(row, col))
            x = np.random.randint(256, size=(col, 1))

            keys, times, comps, stops, ideals = run(A, x, iteration, param)

            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Exp.npy', time.time() - startTime)
            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Key.npy', keys)
            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Time.npy', times)
            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Comp.npy', comps)
            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Stop.npy', stops)
            np.save('statistics/Scale_' + param['strategy'] + '_' + param['id'] + '_' + str(row) + '_Ideal.npy', ideals)

            print('Average Latency = ' + str(np.mean(stops)))
            print('Run Time = ', str(time.time() - startTime), sep='')
