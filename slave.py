import socket

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 20202
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.connect(ADDR)

    while True:
        data = input('> ')
        if data == 'quit':
            break
        tcpCliSock.send(data)

    tcpCliSock.close()