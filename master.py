import numpy as np
import socketserver
from Handler import Handler

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 12315
    ADDR = (HOST, PORT)

    server = socketserver.ThreadingTCPServer(ADDR, Handler)
    Handler.srvHandle = server
    Handler.inputList = [(np.arange(1, 10, 1), np.ones((10, 10000))), (np.arange(11, 20, 1), 2*np.ones((10, 10000)))]
    server.allow_reuse_address = True
    server.serve_forever()
    server.server_close()

    for b in Handler.outputList:
        print(b)
