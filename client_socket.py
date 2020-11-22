import socket
import tkinter as tk
import re
import queue
import os

MSGLEN = 2048

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.queue = queue.SimpleQueue()

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        sent = self.sock.send(bytes(msg, 'ascii'))
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
    
    def receive(self, sock):
        chunk = sock.recv(MSGLEN)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        return chunk

    def makeChange(self, sock):
        active = True
        while active:
            msg = str(self.receive(sock), encoding="ascii")
            if msg == "END":
                active = False
                print("ENDING")
            else:
                codeview = text
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
        sock.shutdown(0)

    def run(self):
        print("Welcome to writer - Fromat I - line.pos - text")
        while True:
            print("Input the text to be sent: ", end="")
            msg = input()
            self.mysend(bytes(msg, 'ascii'))
            if msg == "END":
                break


sock = MySocket()
sock.connect('localhost', 8000)

root = tk.Tk()

text = tk.Text(root)
text.grid()

all_regex = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")
# (\\t)(\\r)

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
        sock.mysend(instr)

funID = text.bind("<KeyPress>", check, True)

def end():
    text.unbind("<KeyPress>", funID)
    pass

button = tk.Button(master=root,text="End", command=end)
button.grid()
root.mainloop()