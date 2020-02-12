# coding=utf-8
from utils.codecs import RS


if __name__ == '__main__':
    params = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}
    prob = RS(10000, params['c'], params['delta'])

    with open('statistics/RobustSolitonDistribution.txt', 'w') as f:
        for index in range(len(prob)):
            f.write(str(index) + '\t' + str(prob[index]) + '\n')
