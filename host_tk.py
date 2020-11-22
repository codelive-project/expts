import re
import os
import socket
import socketserver
from threading import Thread, Lock
from queue import SimpleQueue

import tkinter as tk

MSGLEN = 2048

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connections = {}
instruction_queue = SimpleQueue()
all_regex = re.compile("[a-zA-Z0-9 ./<>?;:\"\'`!@#$%^&*()\[\]{}_+=|(\\)-,~]")

root = tk.Tk()
text = tk.Text(root)
text.grid()

def receive(sock):
    chunk = sock.recv(MSGLEN)
    if chunk == b'':
        raise RuntimeError("socket connection broken")
    return chunk

def makeChange(sock):
    active = True
    while active:
        msg = str(receive(sock), encoding="ascii")
        
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

def mysend(msg):
    for i in connections:
        sent = 0
        sent = connections[i]["sock"].send(bytes(msg, 'ascii'))
        if sent == 0:
            print("Nothing sent for:", i)

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
        mysend(instr)

funID = text.bind("<KeyPress>", check, True)

def run(self):
    server.listen(5)

    while True:
        client, add = server.accept()
        print("new connection at:", add)
        new_client = Thread(target=makeChange, args=(client, ))
        connections["add"] = {"process" : new_client,
                              "sock" : client,
                              "name" : add[0], 
                              }
        new_client.start()
    
    for connection in connections:
        print("Connection %s ending..." % (connection))
        if connections[connection].isalive():
            connections[connection].stop()
    print("-------------------------------------------")
    for connection in connections:
        connections[connection].join()
        print("Connection %s joined..." % (connection))
        del connections[connection]

def end():
    text.unbind("<KeyPress>", funID)
    pass

button = tk.Button(master=root,text="End", command=end)
button.grid()

serverThread = Thread(target=run)
serverThread.start()
root.mainloop()