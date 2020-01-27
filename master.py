import socket

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 20202
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSerSock.bind(ADDR)
    tcpSerSock.listen(5)

    while True:
        print('waiting for connection ...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('connected from ', addr)
        while True:
            print('-> receiving data ...')
            data = tcpCliSock.recv(BUFSIZE)
            if data == 'exit':
                break
            print(data)
            data = None
        tcpCliSock.close()

    tcpSerSock.close()