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
        
    def uploadAction(self, even=None):
        self.ss_folder_path = filedialog.askdirectory()
        return self.ss_folder_path
    
    def create_top_frame(self):
        self.top_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.top_frame.pack(side=tk.TOP)
        
    def create_inference_frame(self):
        inf_frame = tk.Frame(self.top_frame, relief=tk.SUNKEN, borderwidth=1)
        inf_frame.pack(side=tk.LEFT)
        inf_title = tk.Label(inf_frame, text='Inference setting')
        inf_title.configure(font='Arial 15')
        inf_title.grid(row=0, columnspan=7)
        ss_upload_button = tk.Button(inf_frame, text='choose test image folder', command=self.uploadAction)
        ss_upload_button.grid(row=1, column=3, columnspan=5)

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
    #print(s.ss_folder_path)