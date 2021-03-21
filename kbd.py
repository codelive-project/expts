# # import tkinter as tk

# # root = tk.Tk()

# # text = tk.Text(root)
# # text.grid()


# # def check(event):
# #     print(
# #         "keycode:",
# #         event.keycode,
# #         "state:",
# #         event.state,
# #         "char:",
# #         repr(event.char),
# #         "\tkeysym",
# #         event.keysym,
# #         "\tcurrent cursor pos",
# #         text.index(tk.CURRENT),
# #         "\t current insert",
# #         text.index(tk.INSERT)
# #     )
# #     # return "break"


# # text.bind("<KeyRelease-Left>", check, True)
# # text.bind("<KeyRelease-Right>", check, True)
# # text.bind("<KeyRelease-Up>", check, True)
# # text.bind("<KeyRelease-Down>", check, True)
# # text.bind("<KeyRelease-Return>", check, True)

# # text.insert(tk.INSERT, "Hello, everyone!\n") 
  
# # text.insert(tk.END, "This is 2020.\n") 
  
# # text.insert(tk.END, "Pandemic has resulted in economic slowdown worldwide") 
  
# # text.pack(expand=1, fill=tk.BOTH) 
  
# # # add tag using indices for the 
# # # part of text to be highlighted 
# # text.tag_add("start", "2.8", "1.13") 
  
# # #configuring a tag called start 
# # text.tag_config("start", background="red", foreground="black") 

# # root.mainloop()

# from tkinter import *

# def onclick(event):
#     print("before:", text.tag_names())
#     if "here" in text.tag_names():
#         text.tag_delete("here")
#     else:
#         text.tag_add("here", "1.0", "1.5")
#         text.tag_config("here", background="red", foreground="blue")
#     print("after:", text.tag_names())

# root = Tk()
# text = Text(root)
# Button(root, text = "ar", command = onclick).pack()
# text.insert(INSERT, "Hello.....")
# text.insert(END, "Bye Bye.....")
# text.pack()

# text.tag_add("here", "1.0", "1.5")
# text.tag_add("start", "1.8", "1.13")
# text.tag_config("here", background="red", foreground="blue")
# text.tag_config("start", background="black", foreground="green")

# text.bind("<KeyRelease>", onclick, True)
# text.event_generate("<<Hi>>")

# root.mainloop()

import tkinter as tk

root = tk.Tk()

text = tk.Text(root)
text.grid()


def check(event):
    print(
        "keycode:",
        event.keycode,
        "state:",
        event.state,
        "char:",
        repr(event.char),
        "keysym",
        event.keysym,
        "keysym_num",
        event.keysym_num,
    )
    # return "break"
    if event.char == "r":
        root.event_generate("<<Foo>>", r = "err")

def check2(event):
    print("CHHHHHHHHHH- %s" % event.r)

text.bind("<KeyPress>", check, True)
root.bind("<<Foo>>", check2)

root.mainloop()
