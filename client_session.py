import socket
import tkinter as tk
import re
import queue
import os
import time
import threading

from session import Session, SOCK_ADDR, MSGLEN
from utils import get_instruction

class ClientSession(Session):
    def __init__(self):
        Session.__init__(self)
        self._text_callback = self._text_widget.bind("<KeyPress>", self.broadcast_keypress, True)
        self.socket_lock = threading.Lock()
        self.receiver_thread = threading.Thread(target=self.receive, args=(self.socket_lock, ))
        
    def broadcast_keypress(self, event):
        instr = get_instruction(event, self._text_widget)

        if instr:
            self.send(self._sock, self.socket_lock, instr)
    
    def receive(self, lock):
        while True:
            #lock.acquire()
            chunk = self._sock.recv(MSGLEN)
            #lock.release()

            if chunk == b'':
                raise RuntimeError("socket connection broken")
            else:
                msg = str(chunk, encoding="ascii")
                self._instruction_queue.put(msg)

    def start(self):
        while True:
            try:
                self._sock.connect(SOCK_ADDR)
                break
            except:
                print("connection failed... pinging again in 2 secs")
                time.sleep(2)

        self.receiver_thread.start()
        self.start_session()

if __name__ == "__main__":
    sess = ClientSession()
    sess.start()