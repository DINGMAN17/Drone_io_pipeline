# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 17:44:00 2021

@author: cryst
"""

import tkinter as tk
from tkinter import filedialog
#from tkinter.ttk import *


class Setting:

    def __init__(self, root):
        self.root = root
        self.root.title(' ML settings ')
        self.init_gui()
        self.ds_dir, self.ss_dir, self.c_dirs = None, None, []
        #TODO: find default output folder
        self.ds_out_dir = self.ss_out_dir = self.dc_out_dir = None
        
    def get_mode(self):
        return self.mode.get()
    
    def get_model(self):
        return self.ss.get(), self.dc.get(), self.ds.get()
        
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
            
    def get_ds_out_folder(self, even=None):
        self.ds_out_dir = filedialog.askdirectory()
        return self.ds_out_dir
    
    def get_ss_out_folder(self, even=None):
        self.ss_out_dir = filedialog.askdirectory()
        return self.ss_out_dir
    
    def get_dc_out_folder(self, even=None):
        self.dc_out_dir = filedialog.askdirectory()
        return self.dc_out_dir
    
    def create_top_frame(self):
        self.top_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.top_frame.pack(side=tk.TOP)
        
    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.bottom_frame.pack(side=tk.BOTTOM)
        
    def create_basic_frame(self):
        mode_frame = tk.Frame(self.top_frame, relief=tk.SUNKEN, borderwidth=1)
        mode_frame.pack(side=tk.LEFT)
        mode_title = tk.Label(mode_frame, text='Basic setting')
        mode_title.configure(font=("Times New Roman", 18, "bold"))
        mode_title.grid(row=0, columnspan=10)
        tk.Label(mode_frame, text='Please select training or inference:').grid(row=1, column=0)
        self.mode = tk.StringVar()
        tk.OptionMenu(mode_frame, self.mode, "Training", "Inference").grid(row=1, column=1)
 
        model_title = tk.Label(mode_frame, text='Please indicate which model/models to run:')
        model_title.configure(font='Arial 11')
        model_title.grid(row=2, column=0, columnspan=10)
        
        ss = tk.Label(mode_frame, text='Semantic segmentation: ')
        ss.configure(font=("Times New Roman", 11, "bold"))
        ss.grid(row=3, column=0)
        self.ss = tk.StringVar()
        tk.OptionMenu(mode_frame, self.ss, "Yes", "No").grid(row=3, column=1)
        dc = tk.Label(mode_frame, text='Defect classification: ')
        dc.configure(font=("Times New Roman", 11, "bold"))
        dc.grid(row=4, column=0)
        self.dc = tk.StringVar()
        tk.OptionMenu(mode_frame, self.dc, "Yes", "No").grid(row=4, column=1)
        ds = tk.Label(mode_frame, text='Defect segmentation: ')
        ds.configure(font=("Times New Roman", 11, "bold"))
        ds.grid(row=5, column=0)
        self.ds = tk.StringVar()
        tk.OptionMenu(mode_frame, self.ds, "Yes", "No").grid(row=5, column=1)
        
    def create_inference_frame(self):
        self.inf_frame = tk.Frame(self.bottom_frame, relief=tk.SUNKEN, borderwidth=1)
        self.inf_frame.pack(side=tk.TOP)
        inf_title = tk.Label(self.inf_frame, text='Inference setting')
        inf_title.configure(font=("Times New Roman", 18, "bold"))
        inf_title.grid(row=0, columnspan=7)
        
        ss_title = tk.Label(self.inf_frame, text=' Semantic segmentation ')
        ss_title.configure(font=("Times New Roman", 13, "bold"))
        ss_title.grid(row=1, column=1)
        dc_title = tk.Label(self.inf_frame, text=' Defect classification ')
        dc_title.configure(font=("Times New Roman", 13, "bold"))
        dc_title.grid(row=1, column=2)
        ds_title = tk.Label(self.inf_frame, text=' Defect segmentation ')
        ds_title.configure(font=("Times New Roman", 13, "bold"))
        ds_title.grid(row=1, column=3)
        
        input_label = tk.Label(self.inf_frame, text='Input:')
        input_label.configure(font=("Times New Roman", 11, "bold"))
        input_label.grid(row=2, column=0)
        ss_dir_button = tk.Button(self.inf_frame, text='choose test image folder', command=self.get_ss_folder)
        ss_dir_button.grid(row=2, column=1)
        dc_dirs_button = tk.Button(self.inf_frame, text='choose test image folders', command=self.get_multiple_folder)
        dc_dirs_button.grid(row=2, column=2)
        ds_dir_button = tk.Button(self.inf_frame, text='choose test image folder', command=self.get_ds_folder)
        ds_dir_button.grid(row=2, column=3)
        
        input_label = tk.Label(self.inf_frame, text='Output:')
        input_label.configure(font=("Times New Roman", 11, "bold"))
        input_label.grid(row=3, column=0)
        ss_out_dir_button = tk.Button(self.inf_frame, text='choose output folder', command=self.get_ss_out_folder)
        ss_out_dir_button.grid(row=3, column=1)
        dc_out_dir_button = tk.Button(self.inf_frame, text='choose output folder', command=self.get_dc_out_folder)
        dc_out_dir_button.grid(row=3, column=2)
        ds_out_dir_button = tk.Button(self.inf_frame, text='choose output folder', command=self.get_ds_out_folder)
        ds_out_dir_button.grid(row=3, column=3)
        
        confirm_label = tk.Label(self.inf_frame, text='To confirm: ')
        confirm_label.configure(font=("Times New Roman", 11, "bold"))
        confirm_label.grid(row=4, column=1)
        #set style for confirm button
        #sto = tk.ttk.Style()
        #sto.configure('W.TButton', font= ('Arial', 10, 'underline'), foreground='Green')
        confirm_button = tk.Button(self.inf_frame, text="Confirm",
                                   command=self.show, height=2, width=15)
        confirm_button.grid(row=4, column=2)
        
    def create_training_frame(self):
        self.inf_frame = tk.Frame(self.bottom_frame, relief=tk.SUNKEN, borderwidth=1)
        self.inf_frame.pack()
        inf_title = tk.Label(self.inf_frame, text='Training setting')
        inf_title.configure(font='Arial 15')
        inf_title.grid(row=0, columnspan=7)
        
    def init_gui(self):
        self.create_top_frame()
        self.create_bottom_frame()
        self.create_basic_frame()
        self.create_inference_frame()
        #self.create_training_frame()
        
    def show(self):
        print( "You entered:")
        print('-'*20)
        print('-Run: ', self.get_mode())
        print('-Chosen model(s): Semantic segmentation/Defect classification/Defect segmentation', self.get_model())
        print('Input folders:')
        print("-Semantic segmentation image list: ", self.ss_dir)
        print('-Defect segmentation image list: ', self.ds_dir)
        print('-Defect classification folders list: ', self.c_dirs)
        print('Output folders:')
        print("-Semantic segmentation output: ", self.ss_out_dir)
        print('-Defect segmentation output: ', self.ds_out_dir)
        print('-Defect classification output: ', self.dc_out_dir)
        
        
        print( '*'*20)
    
if __name__ == '__main__':
    root = tk.Tk()
    s = Setting(root)
    root.mainloop()
    