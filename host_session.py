import socket
import tkinter as tk
import re
import queue
import os
import time
import threading
import json
import random

from session import Session, SOCK_ADDR, MSGLEN
from utils import get_instruction
from remote_user import *

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
    
    def boradcast_cursor_motion(self, event):
        instr = "M[" + self._text_widget.index(tk.CURRENT) + "]"
        for conn in self.connections:
            sock = self.connections[conn]["socket"]
            lock = self.connections[conn]["lock"]
            self.send(sock, lock, instr)
    
    def start_host(self):
        self._sock.bind(SOCK_ADDR)
        self._sock.listen(self._max_connections)
        
        while True:
            client, add = self._sock.accept()
            print("New connection at", add)
            handler_lock = threading.Lock()
            handler_thread = threading.Thread(target=self.handler, args=(add, ))
            author_id = self.get_new_id()

            self.connections[add] = {"author_id": author_id,
                                     "handler_thread" : handler_thread,
                                     "lock" : handler_lock,
                                     "socket": client}

            self._remote_users[author_id] = RemoteUser(author_id, "", random.sample(USER_COLORS, 1))
        
            self.send_active_users()
            handler_thread.start()

    def handler(self, conn):
        sock = self.connections[conn]["socket"]

        while True:
            chunk = sock.recv(MSGLEN)

            if chunk == b'':
                print("Connection with", conn, "ended")
                break
            else:
                msg = str(chunk, encoding="ascii")
                print("received:", msg)
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