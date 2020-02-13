# coding=utf-8
import matplotlib.pyplot as plt

from utils.codecs import RS

if __name__ == '__main__':
    params = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}
    probs = RS(10000, params['c'], params['delta'])

    x = []
    y = []
    for index, prob in enumerate(probs):
        x.append(index)
        y.append(prob)

    # 鲁棒孤子分布曲线
    plt.figure(num=2, figsize=(10, 4), dpi=150)
    # 121
    plt.subplot(121)
    plt.title('Robust Soliton Distribution')
    plt.xlabel('m (row)')
    plt.ylabel('probability')
    # plt.axis([0, 12000, 0, 550])
    plt.plot(x[:400], y[:400])

    # 122
    plt.subplot(122)
    plt.title('Robust Soliton Distribution')
    plt.xlabel('m (row)')
    plt.ylabel('probability')
    # plt.axis([0, 12000, 0, 550])
    plt.plot(x[400:], y[400:])

    plt.savefig('figures/RobustSolitonDistribution.svg')
    plt.show()
