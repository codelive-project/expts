import tkinter as tk

class StartUpWizard(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self._data = dict()

        self._current_page = None
        self._wizardPages = {"welcome": None,
                             "host:1": None,
                             "client:1": None}

    
    def show_step(self, page):
        if self._current_page:
            current = self._wizardPages[self._current_page]
            current.forget_pack()
        
        self._current_page = page
        self._wizardPages[page].pack(fill = "both", expand = True)