# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 09:37:33 2021

@author: ryan.robinson

tkinter layout:
    https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
    
Purpose:
    The purpose of this code is to be used as a tutorial for learning how to
    create a GUI with tkinter.
    
    You don't need a class structure to do it, but class structure helps with
    organization.
"""

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import sys

class Demo1:
    def __init__(self, master):
        self.master = master
        
        # SET THEMES
        s = ttk.Style()
        print(s.theme_names())
        s.theme_use("clam")
        
        # DEFINE TAB PARENTS
        self.tab_parent = ttk.Notebook(self.master)
        
        # DEFINE TABS
        self.frame = tk.Frame(self.tab_parent)
        self.frame2 = tk.Frame(self.tab_parent)

        self.generate_tab_2()

        self.tab_parent.add(self.frame, text="Tab1")
        self.tab_parent.add(self.frame2, text="Tab2")

        minw = 25
        # GRID CONFIGURE
        self.frame.rowconfigure([0, 1, 2, 3, 4, 5], minsize=30, weight=1)
        self.frame.columnconfigure([0, 1, 2, 3], minsize=minw, weight=1)

        
        # BOX CONFIGURE
        self.master.title('Beam Profiler ASCII Analyzer')
        w = 100
        

        
        ############################## ROW 1 #################################
        r = 1
        
        # PIXEL SIZE
        pxs = tk.Label(self.frame, text="Hexel Name:")
        pxs.grid(row = r, column = 0, sticky = "w")
        self.pixel = tk.Entry(self.frame, text = 'Pixel Size', width = minw)
        self.pixel.insert(0, 'Hexel100XXXX-')
        self.pixel.grid(row=r, column=1, sticky = "w")
        
        
        
        
        ############################## ROW 2 #################################
        r = 2
        
        
        # ROW LABEL
        entryLabel = tk.Label(self.frame,text="Emitters:")
        entryLabel.grid(row=r, column=0, sticky = "w")
        
        # CHECK BOX VARIABLE
        self.E = [tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar(),tk.BooleanVar()]
        self.listE = ["emitter-1","emitter-2","emitter-3","emitter-4","emitter-5","emitter-6"]
        
        # NEAR FIELD CHECK BOX
        j = 0
        for e in self.E:
            box1 = tk.Checkbutton(self.frame, text = self.listE[j], variable = e, onvalue = True, offvalue = False)
            box1.grid(row=r, column = j + 1, sticky = "w")
            e.set(True)
            j = j + 1
        
        ############################## ROW 3 #################################
        r = 3
        
        # PIXEL SIZE
        pxs = tk.Label(self.frame, text="Pixel Size (um):")
        pxs.grid(row = r, column = 0, sticky = "w")
        self.pixel = tk.Entry(self.frame, text = 'Pixel Size', width = minw)
        self.pixel.grid(row=r, column=1, sticky = "w")
        
        # PLOT AXIS LIMIT
        self.XL = tk.BooleanVar()
        xl = tk.Checkbutton(self.frame, text = 'Axis Limit (um):', variable = self.XL, onvalue = True, offvalue = False)
        xl.grid(row = r, column = 4, sticky = "w")
        
        self.XLB = tk.Entry(self.frame, text = 'Axis Limit:', width = minw)
        self.XLB.insert(0,'600')
        self.XLB.grid(row = r, column = 5, sticky = "w")
        
        ############################## ROW 4 #################################
        r = 4
        
        # PLOT SELECTION
        pts = tk.Label(self.frame, text="Plots:")
        pts.grid(row = r, column = 0, sticky = "w")
        
        self.CP = tk.BooleanVar() # COLOR PLOT
        self.KP = tk.BooleanVar() # KNIFE EDGE PLOT
        self.SP = tk.BooleanVar() # SINGLE AXIS PLOT
        self.CP.set(True)
        self.KP.set(True)
        self.SP.set(True)
        
        cp = tk.Checkbutton(self.frame, text = 'Color Plot', variable = self.CP, onvalue = True, offvalue = False)
        kp = tk.Checkbutton(self.frame, text = 'Knife Edge Plot', variable = self.KP, onvalue = True, offvalue = False)
        sp = tk.Checkbutton(self.frame, text = 'Single Axis Plot', variable = self.SP, onvalue = True, offvalue = False)
        
        cp.grid(row = r, column = 1, sticky = "w")
        kp.grid(row = r, column = 3, sticky = "w")
        sp.grid(row = r, column = 5, sticky = "w")
        
        ############################## ROW 5 #################################
        r = 5
        
        # PLOT TITLES
        label = tk.Label(self.frame, text="Plot Title: ")
        label.grid(row = r, column = 0, sticky = "w")
        
        self.PLTT = tk.Entry(self.frame, text = 'Plot title', width = minw*4)
        self.PLTT.insert(0,'Module 19 Collimator Far Field')
        self.PLTT.grid(row = r, column = 1, columnspan = 6, sticky = "w")
        
        ############################## ROW 6 #################################
        r = 6
        
        # REMOVE NOISE
        label = tk.Label(self.frame, text="Noise Settings:")
        label.grid(row = r, column = 0, sticky = "w")
        
        self.RN = tk.BooleanVar()
        self.RN.set(True)
        
        rn = tk.Checkbutton(self.frame, text = 'Remove Noise?', variable = self.RN, onvalue = True, offvalue = False)
        rn.grid(row = r, column = 1, sticky = "w")
        
        
        
        ############################## ROW 6 #################################
        r = 7
        
        # RUN BUTTON
        self.getButton = tk.Button(self.frame, text = 'Run!', command = self.get_entry, width = minw*4)
        self.getButton.grid(row=r, column=0, columnspan = 7)

        # FINALLY
        # self.frame.pack()
        self.tab_parent.pack()
        return
    
    def generate_tab_2(self):
        minw = 25
        
        r = 0
        
        # FILENAME LABEL
        self.entryLabel = tk.Label(self.frame2,text="Foldername:")
        self.entryLabel.grid(row=r, column=0, sticky = "w")

        
        # FILENAME ENTRY BOX
        self.entry = tk.Entry(self.frame2, text = 'Entry', width = minw*5)
        self.entry.insert(0, r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata\Hexel1002570-20220208-102829')
        self.entry.grid(row=r, column=1, columnspan = 5, sticky = 'w')

        # BROWS FOR FILE
        self.browsButton = tk.Button(self.frame2, text = 'Browse', command = self.brows, width = minw)
        self.browsButton.grid(row = r, column = 6)
        return
    
    def brows(self):
        filename = fd.askdirectory()
        filename = filename
        self.entry.delete(0,'end')
        self.entry.insert(0,filename)
        

  
        
        
        return
    
    
    def get_entry(self):
        
        filename = self.entry.get()
        px = float(self.pixel.get())
        mult = float(self.mag.get())
        zoom = float(self.XLB.get())
        FF = not self.NF.get()
        flen = float(self.fl.get())
        zoomed = self.XL.get()
        
        titleMod = self.PLTT.get()+" "
        #titleMod = 'GUI Test'
        

        return



def main():
   
    root = tk.Tk()
    app = Demo1(root)
    root.mainloop()

    return


    
if __name__=="__main__":
    main()