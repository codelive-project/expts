import socket
import socketserver
from multiprocessing import Process

MSGLEN = 2048

def myreceive(sock):
        chunk = sock.recv(MSGLEN)
        if chunk == b'':
                raise RuntimeError("socket connection broken")
        return chunk

def showReceived(sock):
        active = True
        while active:
                msg = str(myreceive(sock), encoding="ascii")
                if msg == "END":
                        active = False
                        print("ENDING")
                else:
                        print("message: %s\t command: %s\tposition: %s\tsrting: %s" % (msg, msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
                
        sock.shutdown(0)

if __name__ == "__main__":
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 8000))
        server.listen(1)

        while True:
                client, add = server.accept()
                print("new connection at:", add)
                showReceived(client)

