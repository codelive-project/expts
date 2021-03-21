import socket
import tkinter as tk
import re
import queue
import os
import time
import threading
import json
import random
import copy
import sys

from utils import get_instruction, get_new_id, free_id
from remote_user import RemoteUser, USER_COLORS

MIN_FREE_ID = 0
FREE_IDS = []

MSGLEN = 2048
SOCK_ADDR = ('localhost', 8000)

class Session(tk.Event):
    def __init__(self, is_host = False, is_cohost = False):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._window, self._text_widget = self.create_window(is_host)
        self._instruction_queue = queue.SimpleQueue()
        self._text_callback = None
        
        self._change_thread = threading.Thread(target=self.apply_remote_changes, daemon=True)
        self._cursor_blink_thread = threading.Thread(target=self._cursor_blink, daemon=True)
        self.socket_lock = threading.Lock()

        self._remote_users = dict()

        self.is_host = is_host
        self.is_cohost = is_cohost
        
        # For hosts
        self._text_callback = self._text_widget.bind("<KeyPress>", self.broadcast_keypress, True)
        self._cursor_callback = self.bind_curosr_callbacks()

        self.host_thread = threading.Thread(target=self.accept_connections, daemon=True)
        
        self._max_connections = 5
        self.connections = dict()

        # For clients
        self.receiver_thread = threading.Thread(target=self.receive, args=(self.socket_lock, ), daemon=True)
        self.my_id = get_new_id()
        self.initialized = False


    # For all
    def _cursor_blink(self):
        while True:
            time.sleep(0.5)
            for i in self._text_widget.tag_names():
                if i != str(self.my_id) and i in self._remote_users:
                    if self._remote_users[i].cursor_colored:
                        self._text_widget.tag_config(i, background="white")
                        self._remote_users[i].cursor_colored = False
                    else:
                        self._text_widget.tag_config(i, background=self._remote_users[i].color)
                        self._remote_users[i].cursor_colored = True

    def send(self, sock, lock = None, msg = None):
        # lock.aquire()
        sent = sock.sendall(bytes(msg, "utf-8"))
        if sent != None:
            raise RuntimeError("socket connection broken")
        # lock.release()
    
    def receive(self, conn):
        sock = self.connections[conn]["socket"] if self.is_host else self._sock

        partial_msg = None
        full_msg_len = 0

        while True:
            chunk = sock.recv(MSGLEN)

            if chunk == b'':
                print("Connection with", conn, "ended")
                break
            else:
                msg = str(chunk, encoding="utf-8")
                print("received:", msg)
                 
                if partial_msg == None and len(msg) >= 5 and msg[0 : 5] == "FIRST" and self.initialized == False:
                    full_msg_len = int(msg[msg.find("[") + 1 : msg.find("]")])
                    self.my_id = int(msg[msg.find("(") + 1 : msg.find(")")])
                    partial_msg = msg[msg.find(")") + 1:]
                    print("First msg\nlen:", full_msg_len, "\t id:,", self.my_id, "\n part:\n", partial_msg)
                    
                    if len(partial_msg) == full_msg_len:
                        if len(partial_msg) > 0:
                            self._instruction_queue.put("I[0.0]" + partial_msg)
                            print("I[0.0]" + partial_msg)
                        partial_msg = None
                        full_msg_len = 0
                        self.initialized = True
                
                if partial_msg == None:
                    self._instruction_queue.put(msg)
                    print("Pushed -%s- to queue" % msg)
                else:
                    partial_msg += msg
                    print("part:\n", partial_msg)
                    if len(partial_msg) == full_msg_len:
                        self._instruction_queue.put("I[0.0]" + partial_msg)
                        print("I[0.0]" + partial_msg)
                        partial_msg = None
                        full_msg_len = 0
                        self.initialized = True
    
    def boradcast_cursor_motion(self, event):
        instr = "M(" + str(self.my_id) + "|" + self._text_widget.index(tk.INSERT) + ")"

        if self.is_host:
            self.broadcast_host(instr)
        else:
            self.broadcast_client(instr)

    def broadcast_keypress(self, event):
        instr = get_instruction(event, self._text_widget, self.my_id, 
                                self._text_widget.index(tk.INSERT))

        if self.is_host:
            self.broadcast_host(instr)
        else:
            self.broadcast_client(instr)
    
    def bind_curosr_callbacks(self):
        bind_hash = dict()

        bind_hash["<KeyRelease-Left>"] = self._text_widget.bind("<KeyRelease-Left>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>"] = self._text_widget.bind("<KeyRelease-Right>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>"] = self._text_widget.bind("<KeyRelease-Up>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>"] = self._text_widget.bind("<KeyRelease-Down>", self.boradcast_cursor_motion, True)
        bind_hash["<KeyRelease-Left>"] = self._text_widget.bind("<KeyRelease-Return>", self.boradcast_cursor_motion, True)
        bind_hash["<ButtonRelease-1>"] = self._text_widget.bind("<ButtonRelease-1>", self.boradcast_cursor_motion, True)

        return bind_hash

    def end_broadcast(self):
        self._text_widget.unbind("<KeyPress>", self._text_callback)

        for i in self._cursor_callback:
            self._text_widget.unbind(i, self._cursor_callback[i])
    
    def create_window(self, is_host):
        root = tk.Tk()

        text = tk.Text(root)
        text.grid()

        button = tk.Button(master=root,text="End", command=self.end_broadcast)
        button.grid()

        root.title("Host" if is_host else "Client")

        return root, text
    
    def apply_remote_changes(self):
        while True:
            msg = self._instruction_queue.get()
            
            codeview = self._text_widget
            print("command: %s" % msg)
            
            if msg[0] in ("I", "D", "R", "T", "M"):
                position = msg[2 : msg.find("]")]

            if msg[0] == "I":
                new_text = msg[msg.find(")") + 1 : ]
                codeview.insert(position, new_text)
            
            elif msg[0] == "D":
                codeview.delete(msg[2:msg.find("]")])
            
            elif msg[0] == "R":
                if self._text_widget.index(position) == \
                    self._text_widget.index(position[:position.find(".")] + ".end"):
                    idx = int(position[position.find(".") + 1: ]) + 1
                    codeview.insert(position[:position.find(".") + 1] + str(idx), '\n')
                else:
                    codeview.insert(position, '\n')
            
            elif msg[0] == "T":
                codeview.insert(position, '\t')
            
            if msg[0] in ("I", "D", "R", "T", "M"):
                user_id = msg[msg.find("(") + 1 : msg.find("|")]
                cur_position = msg[msg.find("|") + 1: msg.find(")")]
                self.update_remote_cursor(user_id, cur_position, is_keypress= msg[0] != "M")

    def update_remote_cursor(self, user_id, index, is_keypress = False):
        color = self._remote_users[user_id].color
        self._text_widget.mark_set(user_id, index)

        if user_id in self._text_widget.tag_names():
            self._text_widget.tag_delete(user_id)
        
        col = int(index[index.find(".") + 1 : ])
        if col != 0:
            real_index = index[: index.find(".") + 1] + \
                         str(col if is_keypress else col - 1)
            self._text_widget.tag_add(user_id, real_index)
            self._text_widget.tag_configure(user_id, background=color)

    def start_session(self):
        if self.is_host:
            self.host_thread.start()
        else:
            while True:
                try:
                    self._sock.connect(SOCK_ADDR)
                    break
                except:
                    print("connection failed... pinging again in 2 secs")
                    time.sleep(2)
            
            self.receiver_thread.start()

        self._change_thread.start()
        self._cursor_blink_thread.start()
        self._window.mainloop()

    # for host
    def broadcast_host(self, instr):
        if instr:
            for conn in self.connections:
                sock = self.connections[conn]["socket"]
                lock = self.connections[conn]["lock"]
                self.send(sock, lock, instr)
    
    def accept_connections(self):
        self._sock.bind(SOCK_ADDR)
        self._sock.listen(self._max_connections)
        
        while True:
            client, add = self._sock.accept()
            print("New connection at:", add)

            handler_lock = threading.Lock()
            handler_thread = threading.Thread(target=self.receive, args=(add, ))
            author_id = get_new_id()

            new_user = RemoteUser(author_id, "", random.sample(USER_COLORS, 1))

            self.connections[add] = {"author_id": author_id,
                                     "handler_thread" : handler_thread,
                                     "lock" : handler_lock,
                                     "socket": client}

            self.send_current_state(author_id, add)
            self._remote_users[str(author_id)] = new_user
            handler_thread.start()
            
            print("Users:\n", self._remote_users)
        
    def send_current_state(self, user_id, conn):
        sock = self.connections[conn]["socket"]
        lock = self.connections[conn]["lock"]

        full_text = self._text_widget.get("0.0", tk.END)
        if full_text == "\n":
            full_text = ""
        msg = "FIRST[" + str(len(full_text)) + "]" + \
                   "(" + str(user_id) + ")" + full_text

        lock.acquire()
        sock.sendall(bytes(msg, encoding="utf-8"))
        lock.release()
    
    def send_active_users(self, user_list, lock, sock):
        list_json = json.dumps(user_list)
        self.send(sock, lock, list_json)

    # for client
    def broadcast_client(self, instr):
        if instr:
            self.send(self._sock, self.socket_lock, instr)

if __name__ == "__main__":
    sess = Session(sys.argv[1] == "host" if len(sys.argv) > 1 else False)
    sess.start_session()