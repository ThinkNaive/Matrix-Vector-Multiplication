import numpy as np

from MasterHandler import Handler

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315
    data = [(1, np.arange(1, 10, 1), np.ones((10, 10000))), (2, np.arange(11, 20, 1), 2*np.ones((10, 10000)))]

    Handler.run(HOST, PORT, data)

    for b in Handler.outputList:
        print(b)
