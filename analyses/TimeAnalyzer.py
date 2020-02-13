# coding=utf-8
import numpy as np

if __name__ == '__main__':
    rows = [500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000]
    col = 10000
    iteration = 10
    params = [{'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2},
              {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5},
              {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}]

    for param in params:
        for row in rows:
            durations = np.load('statistics/' + param['strategy'] + '_' + str(row) + '_Exp.npy')
            keys = np.load('statistics/' + param['strategy'] + '_' + str(row) + '_Key.npy')
            times = np.load('statistics/' + param['strategy'] + '_' + str(row) + '_Time.npy')
            comps = np.load('statistics/' + param['strategy'] + '_' + str(row) + '_Comp.npy')
            stops = np.load('statistics/' + param['strategy'] + '_' + str(row) + '_Stop.npy')
