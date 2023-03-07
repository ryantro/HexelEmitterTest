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
# TKINTER IMPORTS
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import serial
# GENERAL IMPORTS
import time, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import threading
import random

# ITC4005, RELAY, HR4000 IMPORTS
import instruments
import dataanalysis

# FOR READING CONFIG FILE
import configparser

# DATA ANALYSIS IMPORTS
import dataanalysis as da



class Application:
    def __init__(self, master):
        """
        Initialize the application gui.

        Parameters
        ----------
        master : tk.Frame()
            master frame object.

        Returns
        -------
        None.

        """
        self.master = master
        
        # LOAD APPLICATION ICON
        self.master.iconbitmap(r'icons\eticon.ico')
        
        # DEFINE ON CLOSING
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # DEFINE TAB PARENTS
        self.tab_parent = ttk.Notebook(self.master)
        
        # DEFINE TABS UNDER PARENT
        self.runframe = tk.Frame(self.tab_parent)
        self.settingsframe = tk.Frame(self.tab_parent)
        self.waterframe = tk.Frame(self.tab_parent)
        self.loadframe = tk.Frame(self.tab_parent)
        self.wlframe = tk.Frame(self.tab_parent)
        self.sdevframe = tk.Frame(self.tab_parent)
        self.skewframe = tk.Frame(self.tab_parent)
        self.kurtframe = tk.Frame(self.tab_parent)
        self.tab_emitter = ttk.Notebook(self.tab_parent)
        self.tab_wl = ttk.Notebook(self.tab_parent)


        # GENERATE EMITTER FRAMES
        self.emmitterframes = []
        for i in range(1,7):
            em = tk.Frame(self.tab_emitter)
            em.rowconfigure([0, 1], minsize=30, weight=1)
            em.columnconfigure([0], minsize=30, weight=1)
            self.tab_emitter.add(em, text = "Emitter {}".format(i))
            self.emmitterframes.append(em)

        # GENERATE EMITTER FRAMES for wavelength fits
        self.wlframes = []
        for i in range(1,7):
            wl = tk.Frame(self.tab_wl)
            wl.rowconfigure([0, 1], minsize=30, weight=1)
            wl.columnconfigure([0], minsize=30, weight=1)
            self.tab_wl.add(wl, text = "Emitter {}".format(i))
            self.wlframes.append(wl)

        # GENERATE TABS
        self.generate_tab_1()
        self.generate_tab_2()
        
        self.gen_settings_frame()
        self.water_settings_frame()
        
        # ADD TABS TO PARENT
        self.tab_parent.add(self.runframe, text="Run Measurement")
        self.tab_parent.add(self.settingsframe, text="Measurement Settings")
        self.tab_parent.add(self.loadframe, text="Load Measurement")
        self.tab_parent.add(self.tab_emitter, text = "Raw Emitter Data")
        self.tab_parent.add(self.tab_wl, text = "Fit Emitter Data")
        self.tab_parent.add(self.wlframe, text="Wavelength Means")
        self.tab_parent.add(self.sdevframe, text="Wavelength Sdev")
        self.tab_parent.add(self.skewframe, text="Wavelength Skew")
        self.tab_parent.add(self.kurtframe, text="Wavelength Kurtosis")
        self.tab_parent.add(self.waterframe, text="Water Flow")

        self.TempValue = tk.StringVar()
        self.FlowValue = tk.StringVar()

        # DEFINE RUNNING
        self.running = False
        self.enabled = False
        self.stopThreads = False


        # DEFINE SOFTWARE INTERLOCK
        self.enabled = False

        # RUN THREAD
        self.thread1 = threading.Thread(target = self.run_app)

        # STATION STATE THREAD
        self.thread2 = threading.Thread(target = self.stateUpdate, daemon = True)
        self.thread2.start()

        # GET DATA THREAD
        self.thread3 = threading.Thread(target = self.get_data, daemon=True)
        self.thread3.start()

        # CHANGE LABEL THREAD
        self.thread4 = threading.Thread(target = self.change_labels, daemon=True)
        self.thread4.start()

        return
        
    def gen_settings_frame(self):
        
        self.settingsframe.rowconfigure([0, 1], minsize=30, weight=1)
        self.settingsframe.columnconfigure([0, 1], minsize=30, weight=1)
        
        self.esframe = tk.Frame(self.settingsframe, borderwidth = 2,relief="groove") #, bg = '#9aedfd')
        self.esframe.rowconfigure([0,1,2,3,4,5,6,7], minsize=30, weight=1)
        self.esframe.columnconfigure([0,1], minsize=30, weight=1)
        self.esframe.grid(row = 0, column = 0, sticky = 'NEW', padx = 20, pady = 20)
        
        eslabel = tk.Label(self.esframe, text="Emitter Selection:", font = ('Ariel 15')) #, bg = '#9aedfd')
        eslabel.grid(row = 0, column = 0, columnspan = 2, sticky = "W")

        self.msframe = tk.Frame(self.settingsframe, borderwidth = 2,relief="groove") #, bg = '#9aedfd')
        self.msframe.rowconfigure([0,1,2,3,4,5,6,7], minsize=30, weight=1)
        self.msframe.columnconfigure([0,1], minsize=30, weight=1)
        self.msframe.grid(row = 0, column = 1, sticky = 'NEW', padx = (0,20), pady = 20)
        
        mslabel = tk.Label(self.msframe, text="Test Settings:", font = ('Ariel 15')) #, bg = '#9aedfd')
        mslabel.grid(row = 0, column = 0, columnspan = 2, sticky = "W")
        
        clabel = tk.Label(self.msframe, text="Laser Current (Amps):", font = ('Ariel 12')) #, bg = '#9aedfd')
        clabel.grid(row = 1, column = 0, sticky = 'W')
        
        # GENERATE CURRENT SETPOINT
        self.centry = tk.Entry(self.msframe, text = 'current', width = 5, font = ('Ariel 12'), borderwidth = 2)
        self.centry.insert(0, '2.8')
        self.centry.grid(row=1, column=1, sticky = "W", padx = 10)

        return


# BEGINNING OF WATER FLOW TAB IMPLEMENTATION # ------------------------------------------------------------------------

    def water_settings_frame(self):
        self.waterframe.rowconfigure([0, 4], minsize=1, weight=1)
        self.waterframe.columnconfigure([0, 1], minsize=1, weight=1)

        self.wfframe = tk.Frame(self.waterframe, borderwidth=4, relief="groove", padx=20, pady=20)  # , bg = '#9aedfd')
        self.wfframe.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7], minsize=1, weight=1)
        self.wfframe.columnconfigure([0, 1], minsize=1, weight=1)
        self.wfframe.grid(row=0, column=0, sticky='WN')

        self.wflabel = tk.Label(self.wfframe, text="Water Flow (Lpm):", font=('Ariel 15'))  # , bg = '#9aedfd')
        self.wflabel.grid(row=0, column=0, columnspan=1, padx=10, pady=10)

        self.wtlabel = tk.Label(self.wfframe, text="Water Temp (C):", font=('Ariel 15'))  # , bg = '#9aedfd')
        self.wtlabel.grid(row=1, column=0, columnspan=1, padx=10, pady=10)

#        self.wateronButton = tk.Button(self.wfframe, text='Water On', command=self.water_on, font=('Ariel 15'),
        #                                borderwidth=4)
        # self.wateronButton.grid(row=2, column=0, columnspan=1, padx=10, pady=10)

        # self.wateroffButton = tk.Button(self.wfframe, text='Water Off', command=self.water_off, font=('Ariel 15'),
        #                                 borderwidth=4)
        # self.wateroffButton.grid(row=3, column=0, columnspan=1, padx=10, pady=10)

        # self.aironButton = tk.Button(self.wfframe, text='Air On', command=self.air_on, font=('Ariel 15'), borderwidth=4)
        # self.aironButton.grid(row=2, column=1, columnspan=1, padx=10, pady=10)

        # self.airoffButton = tk.Button(self.wfframe, text='Air Off', command=self.air_off, font=('Ariel 15'),borderwidth=4)
        # self.airoffButton.grid(row=3, column=1, columnspan=1, padx=10, pady=10)

        # GENERATE PURGE BUTTON AND TIE IT TO PURGE_SYSTEM
        self.purgeButton = tk.Button(self.wfframe, text='Purge System', command=self.purge_system, font=('Ariel 15'),
                                     borderwidth=4)
        self.purgeButton.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        return

    def get_data(self):
        try:
            self.ser = serial.Serial("COM8", 9600)
            self.ser.isOpen()
            time.sleep(2)
            self.ser.flush()

        except IOError:
            self.mprint("Can't find flowmeter connection...\nPlug in flowmeter and restart software.")

        while True:
            text = self.ser.readline().decode()
            data = text.split()
            value = data[0]
            value2 = data[1]
            self.FlowValue.set(str(value))
            self.TempValue.set(str(value2))
            self.ser.flushInput()
            time.sleep(0.5)

    def change_labels(self):
        self.wfrate = tk.Label(self.wfframe, textvariable=self.FlowValue, font=('Ariel 15'))  # , bg = '#9aedfd')
        self.wfrate.grid(row=0, column=1, columnspan=1, padx=10, pady=10)
        self.wttemp = tk.Label(self.wfframe, textvariable=self.TempValue, font=('Ariel 15'))  # , bg = '#9aedfd')
        self.wttemp.grid(row=1, column=1, columnspan=1, padx=10, pady=10)
        return

    def close_serial(self):
        self.ser.close()
        return

    def purge_system(self):
        threshold = str("0.00")
        if self.FlowValue.get() == threshold:
           self.purge()
        else:
            self.purge_check()
        return

   

    def purge(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'3')

        return

    def water_on(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'4')

        return

    def water_off(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'5')

        return

    def air_on(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'1')

        return

    def air_off(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'2')

        return

    def purge_check(self):
        """
        WARNING FOR PURGE, LET USER KNOW THEY NEED TO SHUT OFF INCOMING WATER FLOW.
        """
        if tk.messagebox.showinfo("Warning", "Water must be shut off before purging."):
            return
        
    def check_for_hexel(self):
        """
        WARNING FOR PURGE, LET USER KNOW THEY NEED TO SHUT OFF INCOMING WATER FLOW.
        """
        if tk.messagebox.askokcancel("Purge!", "Are you sure you want to purge, please double check for hexel on cold plate before purging."):
            return False
        

# END OF WATER FLOW TAB IMPLEMENTATION # -----------------------------------------------------------------------------------------


    def generate_tab_1(self):
        """
        Create the run measurement and realtime plots tab.

        Returns
        -------
        None.

        """

        minw = 25
        # GRID CONFIGURE
        self.runframe.rowconfigure([0, 1, 2], minsize=30, weight=1)
        self.runframe.columnconfigure([0, 1], minsize=25, weight=1)
        
        # BOX CONFIGURE
        self.master.title('SETS - Single Emitter Test Station')
        
        ##################### HEXEL ENTRY BOX #################################
        r = 0
        # GENERATE HEXEL FRAME FRAME
        self.hexelframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove", bg = '#9aedfd') #, highlightbackground="black", highlightthickness=1)
        self.hexelframe.columnconfigure([0, 1], minsize=50, weight=1)
        self.hexelframe.rowconfigure([0], minsize=50, weight=1)
        self.hexelframe.grid(row = 0, column = 0, padx = 20, pady = (20,0), sticky = "EW")
        
        # GENERATE HEXEL NAME BOX LABEL
        pxs = tk.Label(self.hexelframe, text="Hexel Serial Number:", font = ('Ariel 15'), bg = '#9aedfd')
        pxs.grid(row = r, column = 0, sticky = "w", padx = 10)
        
        # GENERATE HEXEL NUMBER ENTRY BOX
        self.hexel = tk.Entry(self.hexelframe, text = 'hexel', width = minw, font = ('Ariel 15'), borderwidth = 2)
        self.hexel.insert(0, '100XXXX')
        self.hexel.grid(row=r, column=1, sticky = "WE", padx = 10)
        
        """New Addition"""
        ################### STATION ENABLE BOX ###############################
        r = 0
        # GENERATE STATION ENABLE BOX
        self.stateframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove")
        self.stateframe.columnconfigure([0, 1], minsize=50, weight=1)
        self.stateframe.rowconfigure([0], minsize=50, weight=1)
        self.stateframe.grid(row = 0, column = 1, padx = (0, 20), pady = (20,0), sticky = "EW")
        
        # GENERATE ENABLE/DISABLE BUTTON
        self.stateButton = tk.Button(self.stateframe, text="Enable", command=self.stateToggle, font = ('Ariel 15'))
        self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
        
        # GENERATE STATION STATUS BOX
        self.statelabel = tk.Label(self.stateframe, text=" STATION DISABLED ", bg = '#84e47e', font = ('Ariel 15'))
        self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
        """End of new Addition"""
        
        ############################ PLOT FRAME ##############################
        r = 3
        
        # GENERATE PLOT FRAME
        self.plotframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove")#, highlightbackground="black", highlightthickness=1)
        self.plotframe.grid(row = 1, column = 0, padx = 20, pady = 20)
        
        # GENERATE FIGURE FOR RUNTIME PLOTS
        self.fig1, self.plot1, self.can1 = self.genFig(self.plotframe)
        
        ########################### TEXT BOX #################################
        r = 1
        
        # GENERATE TEXT BOX FOR REPORTING RESULTS
        self.text_box = tk.Text(self.runframe, height = 30, width = 40, borderwidth = 2, relief = "groove")
        self.text_box.grid(row = r, column = 1, rowspan = 1, sticky = "NS", padx = (0,20), pady = 20)
        self.text_box.insert("end","")
        self.text_box.config(state = 'disabled')
        
        ###################### RUN & STOP BUTTONS ############################
        r = 2
        
        # GENERATE RUN BUTTON AND TIE IT TO RUN_APP       
        self.getButton = tk.Button(self.runframe, text = 'Run Automated Test!', command = self.run_app, font = ('Ariel 15'), borderwidth = 4, bg = '#84e47e')
        self.getButton.grid(row=r, column=0, columnspan = 1, pady = (0,20), padx = 20, sticky = "EW")
        
        # GENERATE FORCE STOP BUTTON
        self.stopButton = tk.Button(self.runframe, text = "Force Stop", command = self.stop_app, font = ('Ariel 15'), borderwidth = 4, bg = '#F55e65')
        self.stopButton.grid(row=r, column=1, columnspan = 1, pady = (0,20), padx = (0, 20), sticky = "EW")
        
        ##################### FINALLY IT ALL TOGETHER ########################
        self.tab_parent.pack()
        
        return
    
    def stateToggle(self):
        """
        CHANGE THE STATE FOR THE STATION
        """
        if(self.enabled == False):
            
            # ENABLE THE STATION
            self.enabled = True
            
            self.mprint("Station state set to enabled.")
            
            # GRID LOCATION
            self.statelabel.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
            self.stateButton.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
            
            # COLOR AND LABEL
            self.stateButton.configure(text = "Disable")
            self.statelabel.configure(text = "STATION ENABLED", bg = '#F55e65')
            
        elif(self.enabled == True):
            
            # DISABLE THE STATION
            self.enabled = False
            
            if(self.running == True):
                self.running = False
                self.mprint("\n")
                self.mprint("Software Interlock Triggered.")
            
            self.mprint("Station state set to disabled.")
            
            # GRID LOCATION
            self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
            self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
            
            # COLOR AND LABEL
            self.stateButton.configure(text = "Enable")
            self.statelabel.configure(text = "STATION DISABLED", bg = '#84e47e')
            
        return
    
    def stateUpdate(self):
        """
        MONITORS STATION STATE
        """
        while(self.stopThreads == False):
            if(self.enabled == True and self.running == True):
                
                # GRID LOCATION
                self.statelabel.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
                self.stateButton.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
                
                # COLOR AND LABEL
                self.stateButton.configure(text = "Disable")
                self.statelabel.configure(text = "TEST RUNNING", bg = '#F55e65')
                time.sleep(0.2)
                self.statelabel.configure(bg = "White")
                
            elif(self.enabled == True and self.running == False):
                
                # GRID LOCATION
                self.statelabel.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
                self.stateButton.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
                
                # COLOR AND LABEL
                self.stateButton.configure(text = "Disable")
                self.statelabel.configure(text = "STATION ENABLED", bg = '#F55e65')
            elif(self.enabled == False and self.running == False):
                
                # GRID LOCATION
                self.statelabel.grid(row = 0, column = 1, padx = 0, pady = 0, sticky = "NSEW")
                self.stateButton.grid(row = 0, column = 0, padx = 0, pady = 0, sticky = "NSEW")
                
                # COLOR AND LABEL
                self.stateButton.configure(text = "Enable")
                self.statelabel.configure(text = "STATION DISABLED", bg = '#84e47e')
            else:
                self.running = False
            time.sleep(0.2)    
        
        return
    
    def mprint(self, text, append = True, newline = True):
        """
        Write message into text boxes.

        Parameters
        ----------
        text : TYPE
            DESCRIPTION.
        append : TYPE, optional
            DESCRIPTION. The default is True.
        newline : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        ############################# TEXT BOX 1 #############################
        
        # WRITE IN FIRST TEXT BOX
        self.text_box.config(state = 'normal')
        if(append == False):
            self.text_box.delete("1.0","end")
        self.text_box.insert("end", text)
        
        # CHECK FOR NEWLINE
        if(newline):
            self.text_box.insert("end","\n")
        
        # UPDATE TEXT BOX
        self.text_box.config(state = 'disabled')
        self.text_box.update()
        self.text_box.see("end")
        
        ############################# TEXT BOX 2 #############################
        
        # WRITE IN SECOND TEXT BOX
        self.text_box2.config(state = 'normal')
        if(append == False):
            self.text_box2.delete("1.0","end")
        self.text_box2.insert("end", text)
        
        # CHECK FOR NEWLINE
        if(newline):
            self.text_box2.insert("end","\n")
        
        # UPDATE TEXT BOX
        self.text_box2.config(state = 'disabled')
        self.text_box2.update()
        self.text_box2.see("end")
        
        return
    
    def generate_tab_2(self):
        """
        Generate the data analysis tab.

        Returns
        -------
        None.

        """
        # GRID CONFIGURE
        self.loadframe.rowconfigure([0, 1, 2], minsize=10, weight=1)
        self.loadframe.columnconfigure([0], minsize=10, weight=1)
        
        # FILE SELECTION FRAME
        self.loadbox = tk.Frame(self.loadframe)
        self.loadbox = tk.Frame(self.loadframe, borderwidth = 2,relief="groove", bg = '#9aedfd')
        self.loadbox.columnconfigure([0, 1, 2], minsize=50, weight=1)
        self.loadbox.rowconfigure([0], minsize=50, weight=1)
        self.loadbox.grid(row = 0, column = 0, padx = 20, pady = (20,0), sticky = "NEW")
        
        # FILENAME LABEL
        self.entryLabel = tk.Label(self.loadbox,text="Foldername:", font = ('Ariel 15'), bg = '#9aedfd')
        self.entryLabel.grid(row=0, column=0, sticky = "W", padx = 10)
        
        # FILENAME ENTRY BOX
        self.entry = tk.Entry(self.loadbox, text = 'Entry', width = 60, font = ('Ariel 15'))
        self.entry.insert(0, r'testdata\Hexel1002596-20220216-123108')
        self.entry.grid(row=0, column=1, sticky = "EW", padx = (0,20))

        # BROWS FOR FILE
        self.browsButton = tk.Button(self.loadbox, text = 'Browse', command = self.brows, font = ('Ariel 15'), bg = '#84e47e')
        self.browsButton.grid(row = 0, column = 2, sticky = "EW", padx = (0,10))
        
        # GENERATE 2ND TEXT BOX FOR DATA ANALYSIS TAB
        self.text_box2 = tk.Text(self.loadframe, height = 33, width = 40, borderwidth = 2, relief = "groove")
        self.text_box2.grid(row = 1, column = 0, sticky = "NSEW", padx = 20, pady = 20)
        self.text_box2.insert("end","")
        self.text_box2.config(state = 'disabled')

        # RUN BUTTON
        self.getButton = tk.Button(self.loadframe, text = 'Load Folder and Analyze Data!', command = self.load_folder, font = ('Ariel 15'), borderwidth = 4, bg = '#84e47e')
        self.getButton.grid(row=2, column=0, padx = 20, pady = (0,20), sticky = "ews")
        
        return
    
    def brows(self):
        """
        Browes for file to run.

        Returns
        -------
        None.

        """
        filename = fd.askdirectory()
        filename = filename
        self.entry.delete(0,'end')
        self.entry.insert(0,filename)
        
        return
    
    def load_folder(self):
        """
        Load folder and perform data analysis.

        Returns
        -------
        None.

        """        
        if(self.running):
            return
        
        # CLOSE ALL PLOTS TO SLEDGE HAMMER ANY POTENTIAL MEMORY LEAKS
        plt.close('all')
        
        # START DATA ANALYSIS
        self.mprint("\nRunning data analysis.")
        
        # GET FOLDER NAME
        datapath = self.entry.get()
        self.mprint("\nLoading data from:")
        self.mprint("{}\n".format(datapath))
        
        hexelfolder = datapath.split("\\")[-1]
        hexelfolder = hexelfolder.split("/")[-1]
        self.mprint("{}".format(hexelfolder))
        
        # GENERATE EMITTER FOLDER NAMES
        folders = os.listdir(datapath)
        emitters = []
        for folder in folders:
            if("emitter" in folder):
                emitters.append(folder)
        
        # TODO: CHECK IF EMITTERS [] IS EMPTY
        wMeanFigure = None
        wMeanPlot = None
        
        sdevFigure = None
        sdevPlot = None
        
        skewFigure = None
        skewPlot = None
        
        kurtFigure = None
        kurtPlot = None
        
        # OPEN EMITTER DATA FOLDERS
        for i in range(0,len(emitters)):
            
            """ Generate emitter data object """
            # CREATE EMITTER DATA OBJECTS
            EM = da.emitterData()
            
            # LOAD EMITTER DATA INTO OBJECT
            EM.loadFolder(datapath+"\\"+emitters[i])
            
            """ Generate raw intensity plots """
            # GENERATE FIGURES AND PLOTS
            emfig = EM.getIntensityFigure()
            
            # GENERATE INTENSITY PLOTS
            self.genEmitterPlot(self.emmitterframes[i], emfig)
            
            """ Generate wl fit plots """
            # TODO
            # GENERATE FIGURES AND PLOTS
            wlfig = EM.getWlFitFigure()
            self.genEmitterPlot(self.wlframes[i], wlfig)
            
            """ Report data calcs """            
            # REPORT DT DATA
            self.mprint("...{}".format(emitters[i]))
            try:
                self.mprint("......dT-10-90 = {:.6} C".format(EM.getDT()))
            except:
                self.mprint("\n......ERROR: Missing 10% or 90% duty cycle data.")
                
            try:
                self.mprint("......dT-0-100 = {:.6} C".format(EM.getDT_New()))
                self.mprint("......CW WL = {:.6} nm".format(EM.getCWWL()))
            
                # GENERATE FIGURES
                wMeanFigure, wMeanPlot = EM.getPeakFigure(wMeanFigure, wMeanPlot)
                sdevFigure, sdevPlot = EM.getSdevFigure(sdevFigure, sdevPlot)
                skewFigure, skewPlot = EM.getSkewFigure(skewFigure, skewPlot)
                kurtFigure, kurtPlot = EM.getKurtFigure(kurtFigure, kurtPlot)
            except:
                self.mprint("......ERROR: Failed to parse data.")

        # GENERATE WEIGHTED MEAN PLOTS
        self.genEmitterPlot(self.wlframe, wMeanFigure)
        
        # GENERATE STANDARD DEVIATION PLOTS
        self.genEmitterPlot(self.sdevframe, sdevFigure)
        
        # GENERATE SKEW PLOTS
        self.genEmitterPlot(self.skewframe, skewFigure)
        
        # GENERATE KURTOSIS PLOTS
        self.genEmitterPlot(self.kurtframe, kurtFigure)
        
        # DATA ANALYSIS FINISHED
        self.mprint("\nData analysis finished!\n")
        
        return
        
    def genEmitterPlot(self, frame, fig):
        """
        Insert emitter intensity plots into emitter tabs

        Parameters
        ----------
        frame : tk.Frame()
            tk frame to inject figure in.
        fig : pyplot.figure object
            figure plot.

        Returns
        -------
        None.

        """
        # GENERATE AND INSERT CANVAS
        canvas = FigureCanvasTkAgg(fig, master = frame)  
        canvas.get_tk_widget().grid(row=0, column=0, ipadx=40, ipady=20, sticky = "ewns")
        canvas.draw()
            
        # GENERATE AND INSERT TOOLBAR
        toolbarFrame = tk.Frame(frame)
        toolbarFrame.grid(row=1, column=0, sticky = "w", padx = 40)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        # CLOSE FIGURE (TO PREVENT MEMORY LEAKS)
        plt.close(fig)
        
        return
    
    def genFig(self, frame):
        """
        Generate the figure for the runtime plot.

        Parameters
        ----------
        frame : tk.Frame()
            frame object that the plot in placed in.

        Returns
        -------
        fig : plt.figure()
            figure for runtime plots.
        plot1 : subplot
            subplot for runtime plots.
        canvas : FigureCanvasTkAgg()
            canvas object that the plot is drawn into.

        """
        # CREATE FIGURE
        fig = plt.figure(figsize = (5, 5), dpi = 100)
        
        # GENERATE PLOT OBJECT
        plot1 = fig.add_subplot(111)
        
        # FORMAT PLOT
        plot1.set_title("Runtime Plots", fontsize = 20)
        plot1.set_xlabel("Wavelength (nm)", fontsize = 15)
        plot1.set_ylabel("Intensity", fontsize = 15)
        plot1.grid("on")
        plot1.set_xlim([435.0, 455.0])
        plot1.set_ylim([0.0, 16000.0])
        
        # GENERATE CANVAS OBJECT
        canvas = FigureCanvasTkAgg(fig, master = frame)  
        canvas.get_tk_widget().grid(row=1, column=0, ipadx=60, ipady=20)
        canvas.draw()

        plt.close(fig)

        return fig, plot1, canvas
    
    def plot(self, frame, fig, plot1, canvas, x = [], y = []):
        """
        Generate runtime plots.

        Parameters
        ----------
        frame : TYPE
            DESCRIPTION.
        fig : TYPE
            DESCRIPTION.
        plot1 : TYPE
            DESCRIPTION.
        canvas : TYPE
            DESCRIPTION.
        x : TYPE, optional
            DESCRIPTION. The default is [].
        y : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """
        # CLEAR PLOT
        plot1.clear()
        
        # GENERATE PLOT
        plot1.plot(x, y)
        
        # FORMAT PLOT
        plot1.set_title("Runtime Plots", fontsize = 20)
        plot1.set_xlabel("Wavelength (nm)", fontsize = 15)
        plot1.set_ylabel("Intensity", fontsize = 15)
        plot1.grid("on")
        
        # DRAW THE PLOT
        canvas.draw()
        
        # CLOSE FIGURE
        plt.close(fig)

        return
    
    def sleep(self, t):
        """
        Sleep for a duration of time and print the status in the gui text box.

        Parameters
        ----------
        t : float/int
            time to wait.

        Returns
        -------
        None.

        """        

        dots = 30
        text = "("
        for i in range(0,dots):
            text = text + " "
        text = text + ")"
        
        self.text_box.config(state = 'normal')
        self.text_box.insert("end", text)
        
        for i in range(0,dots):
            
            # CHECK IF STOP BUTTON HAS BEEN PRESSED
            if(self.running == False):
                raise ProgramReset()
                
            # PRINT DOTS
            self.text_box.config(state = 'normal')        
            self.text_box.insert("end-{}c".format(dots - i + 2), ".")
            self.text_box.delete("end-{}c".format(dots - i + 2),"end-{}c".format(dots - i + 1))
            self.text_box.config(state = 'disabled')
            self.text_box.update()
            time.sleep(t/dots)
        
        self.text_box.config(state = 'normal')
        self.text_box.delete("end-{}c".format(dots+3),"end")
        self.mprint("")
                
        return

    def stop_app(self):
        """
        Ran when reset button is pressed! Marks running flag to false.

        Returns
        -------
        None.

        """
        if(self.running == True):
            self.running = False
            self.enabled = False
            self.mprint("\n")
 
        return
    
    def run_app(self):
        """
        Create a new thread and run the test.

        Returns
        -------
        None.

        """


        # uncomment for testing
        # return
        
        # CHECK IF PROGRAM IS ALREADY RUNNING
        if(self.enabled == False):
            self.mprint("Station is disabled.")
            return
        
        # CHECK IF ENTRY SETTINGS ARE VALID
        current = self.centry.get()
        if(current.replace('.','',1).isdigit() == False):
            self.mprint("ERROR:\n...Invalid current input.")
            return
        currentnum = float(current)
        if(currentnum > 3.5):
            self.mprint("ERROR:\n...Current exceeds maximum value.")
            return
        
        # CHECK IF IT IS OKAY TO START THE TEST
        if(self.running == False and self.enabled == True):
            
            # CHECK IF HEXEL NAME IS A REPEAT
            # savedir = os.listdir("testdata")
            # h_name = self.hexel.get()
            # if(any(h_name in savefldr for savefldr in savedir)):
            #     if(self.repeat_hexel(h_name) == False):
            #         return
            
            # MARK AS RUNNING
            self.running = True
            
            # CHECK IF THREAD IS ALIVE
            if(self.thread1.is_alive() ==  False):
                
                # CREATE THREAD OBJECT TARGETTING THE PROGRAM
                # self.thread1 = threading.Thread(target = self.run_app2)
                
                # FOR TESTING
                self.thread1 = threading.Thread(target = self.run_app2)
                
                # START THREAD
                self.thread1.start()
        
        return
    
    def run_test(self):
        """
        FOR TESTING ONLY
        """
        try:
            self.sleep(10)
        except ProgramReset:
            self.mprint("Program reset triggered.")
        finally:
            self.running = False
            self.enabled = False
        return
    
    def repeat_hexel(self, hexel = "100XXXX"):
        """
        CHECK IF DATA FOR HEXEL ALREADY EXISTS.
        """
        if tk.messagebox.askokcancel("Yes", "Data for Hexel {} already exists, continue?".format(hexel)):
            return True
        return False
    
    def on_closing(self):
        """
        EXIT THE APPLICATION
        """
        # PROMPT DIALOG BOX
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            # SET RUNNING TO FALSE
            self.running = False
            
            self.stopThreads = True
            
            # JOIN THREAD
            if(self.thread1.is_alive() ==  True):
                self.thread1.join(2)
            
            if(self.thread2.is_alive() == True):
                self.thread2.join(2)

            if (self.thread3.is_alive() == True):
                self.thread3.join(2)

            # self.ser.flush()
            # self.ser.close()
            
            # DESTROY APPLICATION
            self.master.destroy()
            
        return
    
    def run_app2(self):
        """
        Method to run the single emitter measurements.

        Raises
        ------
        FileNotFoundError
            DESCRIPTION.
        InterlockError
            DESCRIPTION.

        Returns
        -------
        None.

        """        
        try:
            
            
            ############ LOAD CONFIG FILE INTO LOCAL VARIABLES ##############
            self.mprint("Reading config file.", append = False)
            config = configparser.ConfigParser(inline_comment_prefixes="#")
            configfile = 'sets_config.cfg'
            file_exists = os.path.exists(configfile)
            
            # CHECK IF CONFIG FILE EXISTS
            if(file_exists == False):
                raise FileNotFoundError(configfile)
                
            # LOAD DATA INTO CONFIGPARSER OBJECT
            config.read(configfile)
            
            # LOAD HR4000 INTEGRATION TIME
            integrationTime = int(config['SETTINGS']['HR4000_Integration_Time'])
            
            # LOAD DUTY CYCLES
            dutycyclesstr = config['SETTINGS']['Duty_Cycles']
            dutycycles = np.array(dutycyclesstr.split(","), dtype = int)
            
            # LOAD SLEEP TIMES
            sleepT = float(config['SETTINGS']['Laser_Dwell_Time'])
            sleepT2 = float(config['SETTINGS']['Cooldown_Time'])
            
            # LOAD DATA SAVE LOCATION
            testdata_folder = str(config['SETTINGS']['Folder'])
            
            # GET HEXEL TITLE
            titlemod  = self.hexel.get()
            
            
            # CHECK IF HEXEL NAME IS A REPEAT
            savedir = os.listdir(testdata_folder)
            h_name = titlemod
            if(any(h_name in savefldr for savefldr in savedir)):
                if(self.repeat_hexel(h_name) == False):
                    self.mprint("\nStopped due to repeat hexel name.\n")
                    return
            
            
            # Set Ocean Optics HR4000 integration time in micro seconds
            self.mprint("...OSA integration time set to {} us.".format(integrationTime))
            
            # Sleep Time - Set time to reach steady state in seconds   
            self.mprint("...Emitter dwell time set to {} s.".format(sleepT))
            
            # Sleep Time between switching emitters
            self.mprint("...Cooldown time set to {} s.".format(sleepT2))
            
            # DUTY CYCLES TO MEASURE
            self.mprint("...Duty cycles to measure:")
            for dutycycle in dutycycles:
                self.mprint("......{}".format(dutycycle))

            # SAVE FOLDER LOCATION
            testdata_path = os.path.abspath(testdata_folder)
            strtime = time.strftime("%Y%m%d-%H%M%S")  
            datafolder = "Hexel"+titlemod+"-"+strtime
            folder = "\\".join([testdata_path,datafolder])
            
            # PRINT SAVE LOCATION
            self.mprint("...Data save location:")
            for s in folder.split("\\"):
                self.mprint("......{}/".format(s))

            # CHECK DEVICE COMMUNICATION
            self.mprint("\nChecking devices")
            
            # LOAD DEVICES
            itc4005addr = config['INSTRUMENTS']['ITC4005_Address']
            usb6001dev = config['INSTRUMENTS']['USB_6001']
            hr4000serial = config['INSTRUMENTS']['HR4000_SERIAL']
            
            ######################## CHECK ITC4005 ###########################            
            self.mprint("...ITC4005")
            try:
                CS = instruments.CurrentSupply(itc4005addr)
            except:
                self.mprint("ERROR:\n...Failed to connect to current supply.")
                return
                
            self.mprint("......Connection established.")
            
            # CHECK INTERLOCK
            intrlck = CS.protectionQuery()
            self.mprint("......Interlock state: {}".format(intrlck))
            if(intrlck == 1):
                raise InterlockError()
            
            # SET PRESETS FOR LASER DRIVER
            self.mprint("......Setting device presets.")
            current = float(self.centry.get())
            self.mprint("......Current set to {} A.".format(current))
            CS.setPresets(current = current)
            
            ###################### CHECK NI USB6001 ##########################
            self.mprint("...NI USB-6001")
            try:
                RC = instruments.RelayControl(usb6001dev)
            except:
                self.mprint("ERROR:\n...Failed to connect to relay controller.")
                return
            self.mprint("......Connection established.")
            
            ######################## CHECK HR4000 ############################
            self.mprint("...Ocean Optics HR4000")
            try:
                SA = instruments.SpectrumAnalyzer(integration_time = integrationTime, serialnum = hr4000serial)
            except:
                self.mprint("ERROR:\n...Failed to connect to spectrum analyzer.")
                return
            
            self.mprint("......Connection established.")
            
            
            ####################### START MEASUREMENT ########################            
            self.mprint("\nRunning measurement for {}.".format(titlemod))
            
            # EMITTER SELECTION LOOP
            for i in range(0,6):
                
                self.mprint("...Testing emitter {}.".format(i + 1))
                
                # SET CURRENT TO 0
                CS.switchOff()
                
                # TURN ON SPECIFIC EMITTER 
                RC.turnOn(i)
                
                # Wait to turn on new emitter
                if(i != 0):
                    # WAIT FOR EMITTER TO COOL DOWN
                    self.mprint("......Waiting {} seconds.".format(sleepT2))
                    self.sleep(sleepT2)
                
                # DUTY CYCLE LOOP
                for dc in dutycycles:
                    # START DUTY CYCLE MEASUREMENT
                    self.mprint("......Testing duty cycle: {}%".format(dc))
                    
                    # SET CURRENT CONTROLLER DUTY CYCLE
                    CS.setDutyCycle(dc)
                    
                    # TURN CURRENT SUPPLY ON
                    CS.switchOn()
                    
                    # GET RUNNING DATA
                    # print("......Laser State: {}".format(CS.getState()))
                    # print("......Laser Current: {}".format(CS.getCurrent()))
                    # print("......Laser Duty Cycle: {}".format(CS.getDutyCycle()))
                    
                    # WAIT FOR STEADY STATE
                    self.sleep(sleepT)
                    
                    # MEASURE SPECTRUM
                    SA.measureSpectrum()

                    # GET X AND Y DATA FOR REALTIME PLOT
                    # y = np.random.rand(100)             # for testing
                    # x = np.linspace(400,500,len(y))     # for testing
                    x, y = SA.getData()
                    
                    # GENERATE REALTIME PLOTS
                    self.plot(self.plotframe, self.fig1, self.plot1, self.can1, x = x, y = y)
                    
                    # GENERATE SAVE FILE PATH
                    emittercorrection = i + 1
                    emitter_folder = "emitter-{}".format(emittercorrection)
                    dc_file = "dc-{}.csv".format(dc)
                    filename = "\\".join([folder, emitter_folder, dc_file])

                    # SAVE SPECTRUM
                    SA.saveIntensityData(filename)
                    
                # SET CURRENT TO 0
                CS.switchOff()
                
            # MEASUREMENT FINISHED            
            self.mprint("\nMeasurement finished!")
        
        
            ################## CALL DATA ANALYSIS PROGRAM ####################
        
            # folder INSERT FOLDER INTO LOAD MEASUREMENT BOX
            self.entry.delete(0,"end")
            self.entry.insert(0, folder)
        
            # ANALYZE JUST COLLECTED DATA
            self.running = False
            self.load_folder()
        
        ############################ EXCEPTIONS ##############################
        except FileNotFoundError as ex:
            # ERROR FOR NOT FINDING A FILE
            print(ex)
            self.mprint("\nFILE NOT FOUND ERROR")
            self.mprint("...'{}' not found.".format(str(ex)))
        
        except InterlockError:
            # ERROR FOR TRIGGERED LASER INTERLOCK
            self.mprint("\nINTERLOCK ERROR:")
            self.mprint("...ITC4005 interlock is on.")
        
        except ProgramReset:
            # EXCEPTION FOR PROGRAM RESET
            self.mprint("Program reset triggered.")
        
        except Exception as ex:
            # GENERAL ERROR
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            self.mprint("\nUNKNOWN ERROR:\n...Message Ryan to troubleshoot.")  
            
        finally:
            # CLOSE DEVICES
            self.mprint("Closing devices.\n")
            try:
                SA.close()
            except NameError:
                self.mprint("ERROR:\n...No spectrum analyzer object to close.")
            try:
                CS.close()
            except NameError:
                self.mprint("ERROR:\n...No current source object to close.")
            self.running = False
            self.enabled = False
        
        return

class Error(Exception):
    
    pass

class ProgramReset(Exception):
    
    pass

class InterlockError(Exception):
    
    pass

def main():
    # CREATE ROOT TKINTER OBJECT
    root = tk.Tk()
    
    # CREATE APPLICATION
    app = Application(root)
    
    # RUN MAINLOOP
    root.mainloop()
    return


    
if __name__=="__main__":
    main()
