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
        self.host_thread = threading.Thread(target=self.start_host, daemon=True)
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
            handler_thread = threading.Thread(target=self.handler, args=(add, ))
            self.connections[add] = {"handler_thread" : handler_thread,
                                     "lock" : handler_lock,
                                     "socket": client}
            handler_thread.start()

    def handler(self, conn):
        sock = self.connections[conn]["socket"]
        #self.send_current_state(conn)

        while True:
            chunk = sock.recv(MSGLEN)

            if chunk == b'':
                print("Connection with", conn, "end")
                break
            else:
                msg = str(chunk, encoding="ascii")
                self._instruction_queue.put(msg)

    def send_current_state(self, conn):
        sock = self.connections[conn]["socket"]
        lock = self.connections[conn]["lock"]

        full_text = self._text_widget.get("0.0", tk.END)

        header = "FIRST[" + str(len(full_text)) + "]"
        packet = full_text[:MSGLEN - len(header)]
        self.send(sock, lock, packet)

        last_end = MSGLEN - len(header)
        for _ in range(0, (len(full_text) - len(header)) // MSGLEN):
            packet = full_text[last_end : last_end + MSGLEN]
            self.send(sock, lock, packet)
            last_end = last_end + MSGLEN

    def start(self):
        self.host_thread.start()
        self.start_session()

if __name__ == "__main__":
    sess = HostSession()
    sess.start()