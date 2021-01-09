# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:44:00 2021

@author: cryst
"""

import tkinter as tk
from tkinter import filedialog

class Setting:

    def __init__(self, root):
        self.root = root
        self.root.title(' ML settings ')
        self.init_gui()
        
    def get_ss_folder(self, even=None):
        self.ss_dir = filedialog.askdirectory()
        return self.ss_dir
    
    def get_ds_folder(self, even=None):
        self.ds_dir = filedialog.askdirectory()
        return self.ds_dir
    
    def get_multiple_folder(self):
        self.c_dirs = []
        while True:
            folder = filedialog.askdirectory()
            if not folder:
                break
            self.c_dirs.append(folder)        
    
    def create_top_frame(self):
        self.top_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.top_frame.pack(side=tk.TOP)
        
    def create_inference_frame(self):
        inf_frame = tk.Frame(self.top_frame, relief=tk.SUNKEN, borderwidth=1)
        inf_frame.pack(side=tk.LEFT)
        inf_title = tk.Label(inf_frame, text='Inference setting')
        inf_title.configure(font='Arial 15')
        inf_title.grid(row=0, columnspan=7)
        ss_dir_button = tk.Button(inf_frame, text='choose test image folder', command=self.get_ss_folder)
        ss_dir_button.grid(row=1, column=3, columnspan=5)
        
        c_dirs_button = tk.Button(inf_frame, text='choose test image folders', command=self.get_multiple_folder)
        c_dirs_button.grid(row=2, column=3, columnspan=5)        
        

    def create_training_frame(self):
        pass
        
    def init_gui(self):
        self.create_top_frame()
        self.create_inference_frame()
        
    def show(self):
        print( "You entered:")
        print( "Semantic segmentation folder: ", self.ss_folder_path)
        print( '*'*20)
    
if __name__ == '__main__':
    root = tk.Tk()
    s = Setting(root)
    root.mainloop()
    print(s.c_dirs)