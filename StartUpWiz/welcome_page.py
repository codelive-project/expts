import tkinter as tk

class WelcomePage(tk.Frame):
    def __init__(self, wizard, width = 100, height = 50):
        tk.Frame.__init__(self, wizard, width = width, height = height)
        self._wizard = wizard

        text = tk.Label(self, 
                        text="Welcome to Codelive, Thonny's MQTT based collaboration plugin!")
        
        button_frame = tk.Frame(self)
        
        host_button = tk.Button(button_frame, text="Host a Session", command=self.host_callback)
        host_button.pack(side=tk.LEFT, fill=tk.X, expand = True, padx = 5)
        join_button = tk.Button(button_frame, text="Join a Session", command=self.join_callback)
        join_button.pack(side=tk.LEFT, fill=tk.X, expand = True, padx = 5)

        cancel_button = tk.Button(self,
                                  text="Cancel",
                                  command=self.cancel_callback,
                                  fg = "red")

        text.pack(expand=True, padx = 10, pady = 10)
        button_frame.pack(fill=tk.X, expand=True, pady=5)
        cancel_button.pack(side=tk.BOTTOM, fill=tk.X, expand=True)

    def host_callback(self):
        self._wizard.data["mode"] = "host"
        self._wizard.show_page("host:1")
    
    def join_callback(self):
        self._wizard.data["mode"] = "client"
        self._wizard.show_page("client:1")

    def cancel_callback(self):
        self._wizard.data["mode"] = "cancelled"
        self._wizard.destroy()

if __name__ == "__main__":

    root = tk.Tk()
    top = WelcomePage(root)
    WelcomePage.pack(self = top, fill=tk.BOTH, expand=True, padx=20, pady=20)
    root.mainloop()