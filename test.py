# import tkinter as tk
# from tkinter import ttk
# from datetime import datetime

# root = tk.Tk()
# frame = ttk.Frame(root)

# def down(event):
#     if event.widget.tag_ranges("sel"):
#         print(event.widget.index("sel.first"))
#     print(
#         "keycode:",
#         event.keycode,
#         "state:",
#         event.state,
#         # "char:",
#         # repr(event.char),
#         "keysym",
#         event.keysym,
#         # "keysym_num",
#         #event.keysym_num,
#     )

# def up(event):
#     def x(sym):
#         print("After a second", sym)
#     #root.after(1000, x, event.keysym)

# def t():
#     print("Ping at ", datetime.now())
#     root.after(1000, t)

# text = tk.Text(frame)
# im = tk.PhotoImage(file = "bug.png")
# button = tk.Button(frame, text = "Ping", image = im, command = t, bg = "red")

# text.bind("<KeyPress>", down, True)

# text.bind("<KeyRelease-Meta_R>", up, True)
# text.bind("<KeyRelease-Super_L>", up, True)
# text.bind("<KeyRelease-Control_L>", up, True)
# text.bind("<KeyRelease-Alt_L>", up, True)


# text.pack()
# button.pack()
# frame.pack()
# root.mainloop()

import os

print(os.path.dirname(__file__))