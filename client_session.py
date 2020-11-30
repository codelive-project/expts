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
        self.receiver_thread = threading.Thread(target=self.receive, args=(self.socket_lock, ), daemon=True)
        
    def broadcast_keypress(self, event):
        instr = get_instruction(event, self._text_widget)

        if instr != None:
            self.send(self._sock, self.socket_lock, instr)
    
    def receive(self, lock):
        partial_msg = None
        full_msg_len = 0

        while True:
            #lock.acquire()
            chunk = self._sock.recv(MSGLEN)
            #lock.release()

            if chunk == b'':
                raise RuntimeError("socket connection broken")
            
            msg = str(chunk, encoding="ascii")

            if partial_msg == None and len(msg) >= 5 and msg[0 : 5] == "FIRST":
                full_msg_len = int(msg[msg.find("[") + 1 : msg.find("]")])
                partial_msg = msg[msg.find("]") + 1:]
                print("First msg\nlen:", full_msg_len, "\t part:", partial_msg)
                
            if partial_msg == None:
                self._instruction_queue.put(msg)
            else:
                partial_msg += msg
                if len(partial_msg) == full_msg_len:
                    self._instruction_queue.put("I[0.0]" + partial_msg)
                    print("I[0.0]" + partial_msg)
                    partial_msg = None
                    full_msg_len = 0

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