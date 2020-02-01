# coding=utf-8
from SlaveHandler import Handler


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315
    handle = Handler(HOST, PORT)

    # 接收数据，若接收数据为None表明未分配计算任务，则直接退出
    A_unit = handle.poll()
    if not A_unit:
        print('shutdown please')
        exit()
    print(A_unit)

    # 发送数据
    handle.push(A_unit)
