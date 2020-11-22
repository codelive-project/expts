import socket
import tkinter as tk
import re
import queue
import os
import time
import threading

from session import Session, SOCK_ADDR, MSGLEN
from utils import get_instruction

class HostSession(Session):
    def __init__(self):
        Session.__init__(self)
        self._text_callback = self._text_widget.bind("<KeyPress>", self.broadcast_keypress, True)
        self.host_thread = threading.Thread(target=self.start_host)
        self.receiver_thread = threading.Thread(target=self.receive)
        self.socket_lock = threading.Lock()
        self._max_connections = 5
        self.connections = dict()

    def broadcast_keypress(self, event):
        instr = get_instruction(event, self._text_widget)

        if instr:
            for conn in self.connections:
                sock = self.connections[conn]["socket"]
                lock = self.connections[conn]["lock"]
                self.send(sock, lock, instr)
    
    def start_host(self):
        self._sock.bind(SOCK_ADDR)
        self._sock.listen(self._max_connections)
        
        while True:
            client, add = self._sock.accept()
            handler_lock = threading.Lock()
            handler_thread = threading.Thread(target=self.receive, args=(add, ))
            self.connections[add] = {"receiver_thread" : handler_thread,
                                     "lock" : handler_lock,
                                     "socket": client}
            handler_thread.start()

    def receive(self, conn_key):
        while True:
            #lock.acquire()
            chunk = self.connections[conn_key]["socket"].recv(MSGLEN)
            #lock.release()

            if chunk == b'':
                raise RuntimeError("socket connection broken")
            else:
                msg = str(chunk, encoding="ascii")
                self._instruction_queue.put(msg)

    def start(self):
        self.host_thread.start()
        self.start_session()

if __name__ == "__main__":
    sess = HostSession()
    sess.start()