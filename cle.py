import socket
import tkinter as tk
import re
import queue
import os
import threading
import sys

MSGLEN = 2048
all_regex = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")
IP = "localhost"
PORT = 8000

class MyEditor(tk.Tk):

    def __init__(self, mode, cons=5, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.mode = mode
        self.cons = cons
        self.queue = queue.SimpleQueue()
        
        self.connections = {}

        self.host_thread = None
        self.receiver_thread = None
        self.writer_thread = None

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        sent = self.sock.send(bytes(msg, 'ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def receive(self):
        # if self.mode == "Host":
        #     while True:
        #         for i in self.connections:
        #             chunk = self.connections[i]["sock"].recv(MSGLEN)
        #             if chunk == b'':
        #                 print("host: empty")

        #             msg = str(chunk, encoding="ascii")
        #             self.queue.put(msg)
        # else:
        while True:
            chunk = self.sock.recv(MSGLEN)
            if chunk == b'':
                print("client: empty")
            else:
                msg = str(chunk, encoding="ascii")
                self.queue.put(msg)

    def makeChange(self, codeview):
        active = True
        while active:
            msg = self.queue.get()
            print("command: %s\tposition: %s\tsrting: %s" % (msg[0], msg[2:msg.find("]")], msg[msg.find("]") + 1:]))
            if msg[0] == "I":
                position = msg[2 : msg.find("]")]
                new_text = msg[msg.find("]") + 1 : ]
                codeview.insert(position, new_text)
            elif msg[0] == "D":
                codeview.delete(msg[2:msg.find("]")])
            elif msg[0] == "R":
                codeview.insert(position, '')
                codeview.insert(position, '\r')
            elif msg[0] == "T":
                codeview.insert(position, '\t')
            elif len(msg) >= 5 and msg[0 : 5] == "FIRST":
                # insert_cursor(codeview, msg[6 : msg.find("]")])
                pass

    def start_host(self):
        self.sock.bind((IP, PORT))
        self.sock.listen(self.cons)
        while True:
            print("Listening...")
            client, add = self.sock.accept()
            print("new connection at:", add)
            new_user = threading.Thread(target=self.receive)
            self.connections[add] = {"thread": new_user,
                                     "sock": client}
            new_user.start()

    def start_client(self):
        self.sock.connect((IP, PORT))

    def start_editor(self):
        root = tk.Tk()

        text = tk.Text(root)
        text.grid()

        def check(event):
            print(
                "keysym: ",
                event.keysym,
                "\tkeysym_num",
                event.keysym_num,
                "\tmatch:",
                event.keysym == "BackSpace", # all_regex.match(event.char),
                "\tcurrent:",
                text.index(tk.CURRENT),
                "- c:",
                repr(text.get(text.index(tk.CURRENT))),
                "\tinsert:",
                text.index(tk.INSERT),
                "- c:",
                repr(text.get(text.index(tk.INSERT)))
            )
            
            if all_regex.match(event.char):
                instr = "I[" + text.index(tk.INSERT) + "]" + event.char
            elif event.keysym == "BackSpace":
                pos = text.index(tk.INSERT)

                if pos[pos.find('.') + 1 :] == '0':
                    return

                try:
                    col = int(pos[pos.find('.') + 1 :])
                    pos = pos[ : pos.find('.') + 1] + str(col - 1)
                except:
                    pass

                instr = "D[" + pos + "]"
            elif event.keysym == "Return":
                pos = text.index(tk.INSERT)
                # try:
                #     col = int(pos[pos.find('.') + 1 :])
                #     pos = pos[ : pos.find('.') + 1] + str(col + 1)
                # except:
                #     pass
                instr = "R[" + pos + "]"
            elif event.keysym == "Tab":
                instr = "T[" + text.index(tk.INSERT) + "]"
            elif event.keysym == "Delete":
                print("Right Delete")
            
            if event.keysym != "Delete":
                self.send(instr)
        
        funID = text.bind("<KeyPress>", check, True)

        def end():
            text.unbind("<KeyPress>", funID)

        if self.mode == "Host":
            self.host_thread = threading.Thread(target=self.start_host)
            self.host_thread.start()
        else:
            self.start_client()
            self.receiver_thread = threading.Thread(target=self.receive)
            self.receiver_thread.start()
        
        self.writer_thread = threading.Thread(target=self.makeChange, args=(text, ))
        self.writer_thread.start()

        button = tk.Button(master=root,text="End", command=end)
        button.grid()
        root.mainloop()

if __name__ == "__main__":
    editor = MyEditor(sys.argv[1])
    editor.start_editor()