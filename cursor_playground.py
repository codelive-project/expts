import tkinter as tk
import json

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
        "current cursor pos",
        text.index(tk.CURRENT)
    )

def move_cursor(new_pos):
    

text.bind("<KeyPress>", check, True)

root.mainloop()

# class Test:
#     def __init__(self):
#         self.attr1 = "a"
#         self.attr2 = "b"
#         self.attr3 = "c"
    
#     def to_dict(self):
#         return {
#             "attr1" : self.attr1,
#             "attr2" : self.attr2,
#             "attr3" : self.attr3
#         }

# x = Test()
# print(json.dumps(x.to_dict()))