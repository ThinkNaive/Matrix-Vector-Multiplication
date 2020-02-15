# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionStyle

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

    latency = []
    computation = []

    for i, param in enumerate(params):
        comps = np.load('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Comp.npy')
        stops = np.load('statistics/Param_' + param['strategy'] + '_' + param['id'] + '_Stop.npy')
        latency.append(np.mean(stops))
        computation.append(np.sum(comps) / rows[0] / 10)  # comp/m，平均每次迭代

    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    marker = ['o', '^', 's', 'D', 'x', '*', '+']

    # 计算节点总次数
    fig = plt.figure(num=1, figsize=(6, 4), dpi=150)
    plt.title('Computation vs Latency')
    plt.xlabel('latency (s)')
    plt.ylabel('computation/$m$ (ratio)')

    plt.plot(latency[0:2], computation[0:2], color=color[0], label=params[0]['strategy'].upper(), marker=marker[0])
    plt.plot(latency[2:6], computation[2:6], color=color[1], label=params[2]['strategy'].upper(), marker=marker[1])
    plt.plot(latency[6:12], computation[6:12], color=color[2], label=params[6]['strategy'].upper(), marker=marker[2])
    plt.legend()

    for i, (x, y) in enumerate(zip(latency[0:2], computation[0:2])):
        plt.annotate(r'$r$=%s' % params[i]['repNum'], xy=(x, y), xytext=(0, 5), textcoords='offset points')
    for i, (x, y) in enumerate(zip(latency[2:6], computation[2:6])):
        plt.annotate(r'$k$=%s' % params[i + 2]['k'], xy=(x, y), xytext=(0, 5), textcoords='offset points')

    plt.annotate('',
                 xy=(3.6, 1.28),
                 xytext=(3.45, 1.07),
                 arrowprops=dict(arrowstyle='fancy',
                                 color='#1E90FF',
                                 connectionstyle=ConnectionStyle("Angle3, angleA=45, angleB=-100")))

    sub = fig.add_axes([0.25, 0.4, 0.25, 0.25])
    sub.plot(latency[6:12], computation[6:12], color=color[2], label=params[6]['strategy'].upper(), marker=marker[2])
    for i, (x, y) in enumerate(zip(latency[6:12], computation[6:12])):
        sub.annotate(r'$\alpha$=%s' % params[i + 6]['alpha'], xy=(x, y), xytext=(0, 5), textcoords='offset points')
    # for i, (x, y) in enumerate(zip(latency[6:12], computation[6:12])):
    #     plt.annotate(r'$\alpha$=%s' % params[i + 6]['alpha'], xy=(x, y), xytext=(0, 5), textcoords='offset points')

    plt.savefig('figures/Param_ComputationVsLatency.svg', dpi=150, bbox_inches='tight')
    plt.show()
