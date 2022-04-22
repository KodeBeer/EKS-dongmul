# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 22:24:03 2022

@author: Erwin
"""

import tkinter as tk
from tkinter import ttk

class ModalWindow(tk.Toplevel):
    def __init__(self, master, options, callback, **kwargs):
        self.callback = callback
        super().__init__(master, **kwargs)
        
        self.combo = ttk.Combobox(self, values=options)
        self.combo.pack()
        
        buttons = tk.Frame(self)
        ok = ttk.Button(buttons, text="OK", command=self._ok_pressed)
        ok.pack(side=tk.LEFT)
        cxl = ttk.Button(buttons, text="Cancel", command=self.destroy)
        cxl.pack()
        buttons.pack()
        
        # these commands make the parent window inactive
        self.transient(master) 
        self.grab_set() 
        master.wait_window(self) 
    
    def _ok_pressed(self):
        self.callback(self.combo.get()) # send the value back to the master
        self.destroy()
        
class GUI(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        btn = ttk.Button(self, text='click me', command=self.open_popup)
        btn.pack()
        
        self.lbl = tk.Label(self)
        self.lbl.pack()
        self.open_popup()

    def open_popup(self):
        ModalWindow(self, ['one', 'two', 'three'], self.update_label)
        
    def update_label(self, text):
        self.lbl.config(text=text)

def main():
    root = tk.Tk()
    root.geometry('200x200')
    win = GUI(root)
    win.pack()
    root.mainloop()

if __name__ == "__main__":
    main()