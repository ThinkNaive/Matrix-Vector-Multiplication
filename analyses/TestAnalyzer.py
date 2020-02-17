# coding=utf-8
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    # 由master生成的测试参数
    row = 10000
    col = 10000
    iteration = 10
    param = {'id': '3', 'strategy': 'lt', 'p': 10, 'c': 0.03, 'delta': 0.5, 'alpha': 2.0}
    params = [{'key': 'client-a'},
             {'key': 'client-b'},
             {'key': 'client-c'},
             {'key': 'client-d'},
             {'key': 'client-e'},
             {'key': 'client-f'},
             {'key': 'client-g'},
             {'key': 'client-h'},
             {'key': 'client-i'},
             {'key': 'client-j'}]

    keys = np.load('statistics/Test_' + param['strategy'] + '_' + param['id'] + '_Key' + '.npy', allow_pickle=True)
    times = np.load('statistics/Test_' + param['strategy'] + '_' + param['id'] + '_Time' + '.npy')
    comps = np.load('statistics/Test_' + param['strategy'] + '_' + param['id'] + '_Comp' + '.npy')
    stops = np.load('statistics/Test_' + param['strategy'] + '_' + param['id'] + '_Stop' + '.npy')
    ideals = np.load('statistics/Test_' + param['strategy'] + '_' + param['id'] + '_Ideal' + '.npy')

    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    marker = ['o', '^', 's', 'D', 'x', '*', '+']

    slave = [e['key'] for e in params]

    for key, time, comp, stop, ideal in zip(keys, times, comps, stops, ideals):  # 单个循环
        group = {}
        for i, s in enumerate(slave):
            group[s] = {}
            group[s]['time'] = time[i]
            group[s]['comp'] = comp[i]
            if key.__contains__(s):
                group[s]['valid'] = True
            else:
                group[s]['valid'] = False

        print('--- iteration ---')
        print(group)

    # # 计算节点总次数
    # fig = plt.figure(num=1, figsize=(6, 4), dpi=150)
    # plt.title('Computation vs Latency')
    # plt.xlabel('latency (s)')
    # plt.ylabel('computation/$m$ (ratio)')
    #
    # plt.plot(latency[0:2], computation[0:2], color=color[0], label=params[0]['strategy'].upper(), marker=marker[0])
    # plt.plot(latency[2:6], computation[2:6], color=color[1], label=params[2]['strategy'].upper(), marker=marker[1])
    # plt.plot(latency[6:12], computation[6:12], color=color[2], label=params[6]['strategy'].upper(), marker=marker[2])
    #
    # for i, (x, y) in enumerate(zip(latency[0:2], computation[0:2])):
    #     plt.annotate(r'$r$=%s' % params[i]['repNum'], xy=(x, y), xytext=(0, 5), textcoords='offset points')
    #
    # plt.legend(loc='upper left')
    # plt.savefig('figures/Param_ComputationVsLatency.svg', dpi=150, bbox_inches='tight')
    # plt.show()
