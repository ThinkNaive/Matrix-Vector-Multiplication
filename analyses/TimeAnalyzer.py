# coding=utf-8
import numpy as np

if __name__ == '__main__':
    params = {'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2}
    params = {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5}
    params = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}

    keys = np.load('statistics/' + params['strategy'] + 'Keys_' + params['id'] + '.npy')
    times = np.load('statistics/' + params['strategy'] + 'Times_' + params['id'] + '.npy')
    comps = np.load('statistics/' + params['strategy'] + 'Comps_' + params['id'] + '.npy')
    stops = np.load('statistics/' + params['strategy'] + 'StopTime_' + params['id'] + '.npy')
