import numpy as np
import SocketServer
from Handler import Handler

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315
    ADDR = (HOST, PORT)

    Handler.A_list = [(np.arange(1, 10, 1), np.zeros((10, 10000))), (np.arange(11, 20, 1), np.zeros((10, 10000)))]
    server = SocketServer.ThreadingTCPServer(ADDR, Handler)
    server.allow_reuse_address = True
    server.serve_forever()
