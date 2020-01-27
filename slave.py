import socket
import time

def tryConnect(addr):
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while tcpCliSock.connect_ex(ADDR):
        time.sleep(1)
        tcpCliSock.close()
        tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('try connecting ...')
    return tcpCliSock

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 20202
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    tcpCliSock = tryConnect(ADDR)
        
    while True:
        try:
            data = input('> ')
            tcpCliSock.send(data.encode(encoding='utf-8'))
            if data == 'shutdown' or data == 'exit':
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            tcpCliSock = tryConnect(ADDR)

    tcpCliSock.close()