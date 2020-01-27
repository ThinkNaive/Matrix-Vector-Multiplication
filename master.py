import socket

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 20202
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpSerSock.bind(ADDR)
    tcpSerSock.listen(5)

    while True:
        try:
            print('waiting for connection ...')
            tcpCliSock, addr = tcpSerSock.accept()
            print('connected from ', addr)
            while True:
                print('-> receiving data ...')
                data = tcpCliSock.recv(BUFSIZE).decode(encoding='utf-8')
                if not data or data == 'exit':
                    break
                if data == 'shutdown':
                    tcpCliSock.close()
                    raise(KeyboardInterrupt)
                print(data)
            tcpCliSock.close()
        except KeyboardInterrupt:
            break

    tcpSerSock.close()