# coding=utf-8
import random
import time

import numpy as np

from master import run

if __name__ == '__main__':
    rows = [10000]
    col = 10000
    iteration = 10
    params = [
        {'id': '01', 'strategy': 'rep', 'p': 10, 'repNum': 1},
        {'id': '02', 'strategy': 'rep', 'p': 10, 'repNum': 2},
        {'id': '03', 'strategy': 'mds', 'p': 10, 'k': 4},
        {'id': '04', 'strategy': 'mds', 'p': 10, 'k': 5},
        {'id': '05', 'strategy': 'mds', 'p': 10, 'k': 8},
        {'id': '06', 'strategy': 'mds', 'p': 10, 'k': 10},
        {'id': '07', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 1.25},
        {'id': '08', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 1.5},
        {'id': '09', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0},
        {'id': '10', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 3.0}
    ]

    for param in params:
        for row in rows:
            # time.sleep(DELAY)
            print('--- Param Experiment - ' + param['strategy'] + ' - ' + param['id'] + ' ---')
            startTime = time.time()
            np.random.seed(0)
            random.seed(0)

            A = np.random.randint(256, size=(row, col))
            x = np.random.randint(256, size=(col, 1))

            keys, times, comps, stops, ideals = run(A, x, iteration, param)

            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Exp.npy', time.time() - startTime)
            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Key.npy', keys)
            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Time.npy', times)
            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Comp.npy', comps)
            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Stop.npy', stops)
            np.save('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Ideal.npy', ideals)

            print('Average Latency = ' + str(np.mean(stops)))
            print('Run Time = ', str(time.time() - startTime), sep='')
