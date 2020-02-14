# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    rows = [500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000]
    col = 10000
    iteration = 10
    params = [{'id': '1', 'strategy': 'rep', 'p': 10, 'repNum': 2},
              {'id': '2', 'strategy': 'mds', 'p': 10, 'k': 5},
              {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}]

    durationList = {}
    latencyList = {}
    computationList = {}

    for param in params:
        durations = []
        latency = []
        computation = []

        for row in rows:
            total = np.load('statistics/Scale_' + param['strategy'] + '_' + str(row) + '_Exp.npy')
            keys = np.load('statistics/Scale_' + param['strategy'] + '_' + str(row) + '_Key.npy')
            times = np.load('statistics/Scale_' + param['strategy'] + '_' + str(row) + '_Time.npy')
            comps = np.load('statistics/Scale_' + param['strategy'] + '_' + str(row) + '_Comp.npy')
            stops = np.load('statistics/Scale_' + param['strategy'] + '_' + str(row) + '_Stop.npy')

            durations.append(total)
            latency.append(np.mean(stops))
            computation.append(np.sum(comps))

        durationList[param['strategy']] = durations
        latencyList[param['strategy']] = latency
        computationList[param['strategy']] = computation

    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    marker = ['o', '^', 's', 'D', 'x', '*', '+']

    # 整个实验耗时
    plt.figure(num=1, figsize=(6, 4), dpi=150)
    plt.title('Total Time Comparison')
    plt.xlabel('m (row)')
    plt.ylabel('time (s)')
    # plt.axis([0, 12000, 0, 550])

    for i, (label, durations) in enumerate(durationList.items()):
        plt.plot(rows, durations, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()
    plt.savefig('figures/Scale_TotalTimeComparison.svg', bbox_inches='tight')
    plt.show()

    # 计算节点总耗时
    plt.figure(num=2, figsize=(10, 4), dpi=150)
    # 121
    plt.subplot(121)
    plt.title('Latency Comparison')
    plt.xlabel('m (row)')
    plt.ylabel('time (s)')
    # plt.axis([0, 12000, 0, 1000])

    for i, (label, latency) in enumerate(latencyList.items()):
        plt.plot(rows, latency, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()

    # 122
    plt.subplot(122)
    plt.title('Latency Comparison')
    plt.xlabel('m (row)')
    plt.ylabel('time (s)')
    # plt.axis([0, 12000, 0, 25])

    for i, (label, latency) in enumerate(latencyList.items()):
        if label != 'mds':
            plt.plot(rows, latency, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()
    plt.savefig('figures/Scale_LatencyComparison.svg', bbox_inches='tight')
    plt.show()

    # 计算节点总次数
    plt.figure(num=1, figsize=(6, 4), dpi=150)
    plt.title('Computation Comparison')
    plt.xlabel('m (row)')
    plt.ylabel('computation (row)')
    # plt.axis([0, 12000, 0, 550])

    for i, (label, computation) in enumerate(computationList.items()):
        plt.plot(rows, computation, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()
    plt.savefig('figures/Scale_ComputationComparison.svg', bbox_inches='tight')
    plt.show()

    # 计算量与耗时对比
    plt.figure(num=2, figsize=(10, 4), dpi=150)
    # 121
    plt.subplot(121)
    plt.title('Computation vs Latency')
    plt.xlabel('Latency (s)')
    plt.ylabel('computation (row)')
    # plt.axis([0, 12000, 0, 550])

    for i, param in enumerate(params):
        label = param['strategy']
        latency = latencyList[label]
        computation = computationList[label]
        plt.plot(latency, computation, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()

    # 122
    plt.subplot(122)
    plt.title('Computation vs Latency')
    plt.xlabel('Latency (s)')
    plt.ylabel('computation (row)')
    # plt.axis([0, 12000, 0, 550])

    for i, param in enumerate(params):
        label = param['strategy']
        if label != 'mds':
            latency = latencyList[label]
            computation = computationList[label]
            plt.plot(latency, computation, color=color[i], label=label.upper(), marker=marker[i])

    plt.legend()
    plt.savefig('figures/Scale_ComputationVsLatency.svg', bbox_inches='tight')
    plt.show()
