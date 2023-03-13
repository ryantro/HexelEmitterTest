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

# GENERAL IMPORTS
import time, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import threading
import shutil

# ITC4005, RELAY, HR4000 IMPORTS
# import instruments
import spectrum_analyzer
import relay_control
import laser_driver
import purge_system
import dataanalysis

# FOR READING CONFIG FILE
import configparser

# DATA ANALYSIS IMPORTS
import dataanalysis as da


# Do we save?
SAVE = True

""" Class for managing threads and event """
class ThreadManager:
    def __init__(self):
        self.event1 = threading.Event()
        self.thread1 = threading.Thread()
        return
    
    def setAll(self):
        self.event1.set()


""" Class for controlling device addresses """
class DeviceAddrs: 
    # Config File
    cfgfile = r'device_addresses.cfg'
    
    # Device adresses
    relayAddr = 'COM3'
    purgeAddr = 'COM5'
    ldAddr = 'USB0::0x1313::0x804A::M00466376'
    
    def loadConfig(self):
        print("Loading device addresses config file...")
        
        # Creat the config parser object
        self.config = configparser.ConfigParser()
        
        # TODO: Check if file exists
        
        # Load the object with the config file
        self.config.read(self.cfgfile)
        
        # Load data from config file to temp variables
        self.relayAddr  = str(self.config['DEVICE ADDRESSES']['Relay'])
        self.purgeAddr  = str(self.config['DEVICE ADDRESSES']['Purge'])
        self.ldAddr     = str(self.config['DEVICE ADDRESSES']['ITC4005_Address'])
        
        return
    
    def saveConfig(self):
        print("Saving config file...")
        
        # Load data from config file to temp variables
        self.config.set('DEVICE ADDRESSES', 'Relay', str(self.relayAddr))
        self.config.set('DEVICE ADDRESSES', 'Purge', str(self.purgeAddr))
        self.config.set('DEVICE ADDRESSES', 'ITC4005_Address', str(self.ldAddr))
        
        f = open(self.cfgfile, 'w')
        self.config.write(f)
        
        return

""" Class for controlling device settings """
class MeasurementSettings:
    # Config File
    cfgfile = r'measurement_settings.cfg'
    
    # Measurement settings
    current = 3.3
    dutyCycles = [10, 25, 50, 75, 90, 99]
    intigrationTime = 30000
    dwellTime = 5
    coolDownTime = 5
    savePath = r'P:/AI Production Data/SETS/sets/testdata'
    
    def loadConfig(self):
        print("Loading measurement settings config file...")
        
        # TODO: Check if config file exists
        
        # Creat the config parser object
        self.config = configparser.ConfigParser()
        
        # Load the object with the config file
        self.config.read(self.cfgfile)
        
        # Load data from config file to temp variables
        self.current            = float(self.config['MEASUREMENT SETTINGS']['Laser_Current'])
        self.intigrationTime    = int(self.config['MEASUREMENT SETTINGS']['OSA_Integration_Time'])
        self.dwellTime          = float(self.config['MEASUREMENT SETTINGS']['Laser_Dwell_Time'])
        self.coolDownTime       = float(self.config['MEASUREMENT SETTINGS']['Cooldown_Time'])
        dc                      = self.config['MEASUREMENT SETTINGS']['Duty_Cycles']
        self.dutyCycles         = np.array(dc.split(","), dtype = int)
        self.savePath           = self.config['MEASUREMENT SETTINGS']['Save_Folder']
        
        pass
    
    def saveConfig(self):
        print("Saving config file...")
        

        # Load data from config file to temp variables
        self.config.set('MEASUREMENT SETTINGS', 'Laser_Current', str(self.current))
        self.config.set('MEASUREMENT SETTINGS', 'OSA_Integration_Time', str(self.intigrationTime))
        self.config.set('MEASUREMENT SETTINGS', 'Laser_Dwell_Time', str(self.dwellTime))
        self.config.set('MEASUREMENT SETTINGS', 'Cooldown_Time', str(self.coolDownTime))
        dc = ','.join(self.dutyCycles)
        self.config.set('MEASUREMENT SETTINGS', 'Duty_Cycles', str(dc))
        self.config.set('MEASUREMENT SETTINGS', 'Save_Folder', self.savePath)
        
        f = open(self.cfgfile, 'w')
        self.config.write(f)
        
        return
    
    def __str__(self):
        return ""

"""
The device manager class handles connecting and closing all devices used
in the station!
"""
class DeviceManager:
    def __init__(self):
        self.osa = None
        # self.osa.connect(integration_time = 1500)
        self.osaConnect = False
        
        self.ld = None
        self.ldConnect = False
        
        self.relay = None
        self.relayConnect = False
        
        self.purge = None
        self.purgeConnect = False
        
        self.addrs = DeviceAddrs()
    
    def connectDevices(self):
        """
        Method to connect all devices
        """            
        # Try to connect to the OSA
        print("Trying to connect to the OSA...")
        if(self.osaConnect == False):
            try:
                self.osa = spectrum_analyzer.SpectrumAnalyzer() # Create OSA object
                self.osa.connect(integration_time = 1500)       # Connect OSA object to OSA
                self.osaConnect = True
                print("...OSA connection established!5243424")
                
            except:
                self.osaConnect = False
                print("...OSA connection failed :(")
        
        # Try to connect to the relay controller
        print("Trying to connect to the Relay Control...")
        if(self.relayConnect == False):
            try:
                self.relay = relay_control.Relay(self.addrs.relayAddr) # Create OSA object
                self.relayConnect = True
                print("...Relay connection established!")
                
            except:
                self.relayConnect = False
                print("...Relay connection failed :(")
        
        # Try to connect to the relay controller
        print("Trying to connect to the purge system...")
        if(self.purgeConnect == False):
            try:
                self.purge = relay_control(self.addrs.purgeAddr) # Create OSA object
                self.purgeConnect = True
                print("...Purge system connection established!")
                
            except:
                self.purgeConnect = False
                print("...Purge system connection failed :(")
        
        # Try to connect to the laser drivers
        print("Trying to connect to the Laser Driver...")
        if(self.ldConnect == False):
            try:
                self.ld = laser_driver.CurrentSupply(self.addrs.ldAddr)
                self.ldConnect = True
                self.ld.setPresets()
                print("...Connection to laser driver established!")

                
            except:
                self.ldConnect = False
                print("...Laser driver connection failed :(")
        
        return
    
    def closeDevices(self):
        """
        Method to close all devices
        """
        # Close the laser drivers
        if(self.ldConnect == True):
            print("Trying to close laser driver")
            
            try:
                self.ld.set_current(0)
                self.ld.disable_output()
                self.ld.close()
                self.ldConnect = False
                print("...Laser driver closed!")
                
            except:
                print("...Laser driver failed to close :(")

        # Close the relay
        if(self.relayConnect == True):
            print("Trying to close relay...")
            try:
                self.relay.close()
                self.relayConnect = False
                print("...Relay closed!")
            except:
                print("...Failed to close relay :(")
        
        # Close the powermeter
        if(self.purgeConnect == True):
            print("Trying to close purge system")
            try:
                self.purge.close()
                self.purgeConnect = False
                print("...Purge system closed!")
                
            except:
                print("...Failed to close purge system :(")
        
        # Close the OSA
        if(self.osaConnect == True):
            print("Trying to close the OSA...")
            try:
                self.osa.close()
                self.osaConnect = False
                print("...OSA closed!")
                
            except:
                print("...Failed to close OSA")
        
        return
    
    def allConnected(self):
        """
        Method used to verify that all devices are connected
        """
        if(self.ldConnect and self.relayConnect and self.purgeConnect and self.osaConnect):
            return True
        else:
            return False
        
        return False


"""
Class to handle the GUI for connecting devices
"""
class DeviceManagerBox:
    def __init__(self, master, deviceManager):
        
        font = ('Ariel 12')
        
        # Save parent frame to object and configure rows/cols
        self.master = master
        self.master.rowconfigure([0], minsize=5, weight=1)
        self.master.columnconfigure([0], minsize=5, weight=1)
    
        # Frame to show device status and connect/disconnect buttons
        self.deviceFrame = tk.Frame(self.master, borderwidth = 2) # , relief = "groove")
        self.deviceFrame.grid(row = 0, column = 0, padx = 1, pady = 1, sticky = "EWN")
    
        # Link devices object to current object
        self.deviceManager = deviceManager
    
        # Button to connect all devices
        self.connectButton = tk.Button(self.deviceFrame, text = 'Connect All Devices', command = self.connect, font = font)
        self.connectButton.grid(row = 0, column = 0, sticky = "EW")
    
        # Generate str list for all devices
        self.devicesStr = ['Relay Controller', 'OSA', 'Laser Driver', 'Purge System']
    
        # Labels for device connection status
        self.deviceLabels = []
        for i in range(0, len(self.devicesStr)):
            self.deviceLabels.append(tk.Label(self.deviceFrame, text = self.devicesStr[i], bg = '#F55e65', borderwidth = 2,relief="groove", font = font))
            self.deviceLabels[-1].grid(row = i+1, sticky = "EW")
    
        # Button to connect all devices
        self.disconnectButton = tk.Button(self.deviceFrame, text = 'Disconnect All Devices', command = self.disconnect, font = font)
        self.disconnectButton.grid(row = len(self.deviceLabels)+1, column = 0, sticky = "EW")    
        self.disconnectButton.configure(state = 'disabled')
    
        # Frame to operate devices
        self.instrumentFrame = tk.Frame(self.master, borderwidth = 2, relief = "groove")
        self.instrumentFrame.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = "EWN")
        
        # Button to view spetrometer
        # self.specViewButton = tk.Button(self.instrumentFrame, text = 'View OSA', command = self.viewSpec, font = ('Ariel 8'))
        # self.specViewButton.grid(row = 0, column = 0, sticky = "EW")
        
        # Popup window for spetrometer
        # self.specWindow = None
        
        # Button to open up manual stage commands
        # self.stageMoveButton = tk.Button(self.instrumentFrame, text = "Stage Commands", command = self.stageCommands, font = ('Ariel 8'))
        # self.stageMoveButton.grid(row = 1, column = 0, sticky = "EW")
        
        # Popup window for stage
        # self.stageWindow = None
        
        # Create the event to stop the plotting
        # self.event = threading.Event()
        
        return
    
    def connect(self):
        """
        Method to connect all devices
        """
        # Color to indicate connected device
        bg = '#84e47e'
        
        # Call device manager to open all devices
        self.deviceManager.connectDevices()
        
        # Allow the disconnect button to be pressed
        self.disconnectButton.configure(state = 'normal')
        
        # ['Relay Controller', 'OSA', 'Laser Driver', 'Purge System']
        
        # Report if relay has been connected in GUI
        if(self.deviceManager.relayConnect == True):
            self.deviceLabels[0].configure(bg = bg)
        
        # Report if osa has been connected in GUI
        if(self.deviceManager.osaConnect == True):
            self.deviceLabels[1].configure(bg = bg)
        
        # Report if laser driver has been connected in GUI
        if(self.deviceManager.ldConnect == True):
            self.deviceLabels[2].configure(bg = bg)
            
        # Report if purge system has been connected in GUI
        if(self.deviceManager.purgeConnect == True):
            self.deviceLabels[3].configure(bg = bg) 
            
        return

    def disconnect(self):
        """
        Method to disconnect all devices
        """
        # Color to indicate disconnected device
        bg = '#F55e65'
        
        # Call device manager to close all devices
        self.deviceManager.closeDevices()
        
        # Allow the disconnect button to be pressed
        self.disconnectButton.configure(state = 'disabled')
        
        # Report if relay has been disconnected in GUI
        if(self.deviceManager.relayConnect == False):
            self.deviceLabels[0].configure(bg = bg)
        
        # Report if osa has been disconnected in GUI
        if(self.deviceManager.osaConnect == False):
            self.deviceLabels[1].configure(bg = bg)
        
        # Report if laser driver has been disconnected in GUI
        if(self.deviceManager.ldConnect == False):
            self.deviceLabels[2].configure(bg = bg)
            
        # Report if purge system has been disconnected in GUI
        if(self.deviceManager.purgeConnect == False):
            self.deviceLabels[3].configure(bg = bg) 
    
        return

"""
Class for the spetrometer window
"""
class SpecWindow:
    def __init__(self, master, deviceManager, threadManager): #, spec, event):
        # Link device manager
        self.dm = deviceManager
        
        # Link event manager
        self.event = threadManager.event1
        
        # Link to the master window
        self.master = master
        
        # Frame for spectrometer plot        
        self.specPlot = tk.Frame(self.master, bg = 'white')
        self.specPlot.grid(row = 0, column = 0, sticky = "EWNS")
        
        # Frame for buttons
        self.buttonFrame = tk.Frame(self.master)
        self.buttonFrame.grid(row = 1, column = 0, sticky = "EW")
        
        # Create measure button
        self.measureButton = tk.Button(self.buttonFrame, text="Measure", command=self.measureAndPlot, font = ('Ariel 15'))
        self.measureButton.grid(row = 0, column = 0, sticky = "EW")
        
        # Creat continuous run button
        self.contRunButton = tk.Button(self.buttonFrame, text = "Start Realtime Plotting", command = self.contRun, font = ('Ariel 15'))
        self.contRunButton.grid(row = 0, column = 1, sticky = "EW")
        
        # Create the stop button
        self.stopButton = tk.Button(self.buttonFrame, text = "Stop Realtime Plotting", command = self.stopRun, font = ('Ariel 15'))
        self.stopButton.grid(row = 0, column = 2, sticky = "EW")
        
        # Create a figure
        self.fig = Figure(figsize = (5, 5), dpi = 100)
        
        # Create a plot
        self.plot1 = self.fig.add_subplot(111)
        
        # Plot formatting
        self.plot1.axis(ymin = 0, ymax = 16500, xmin = 400, xmax = 460)
        self.plot1.grid('on')
        self.plot1.set_title("Runtime Plots 2", fontsize = 20)
        self.plot1.set_xlabel("Wavelength (nm)", fontsize = 15)
        
        # Create the canvas and insert the figure into it
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.specPlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
        # Create the thread for the plot loop
        self.thread = threading.Thread(target = self.plotLoop, daemon = True)
        
        return

    def measureAndPlot(self):
        """
        Measure the current spectrum and plot the results
        """
        # CLEAR PLOT
        self.plot1.clear()
        
        # Measure the spectrum
        self.dm.osa.measureSpectrum()
        
        # Take a single measurement
        x, y = self.dm.osa.getData()
        
        # Plot the spetrometer data
        self.plot1.plot(x, y)
        
        # Plot formatting
        self.plot1.axis(ymin = 0, ymax = 16500, xmin = 415, xmax = 500)
        self.plot1.set_title("Runtime Plots", fontsize = 20)
        self.plot1.set_xlabel("Wavelength (nm)", fontsize = 15)
        self.plot1.grid("on")
        
        # Draw the plot
        self.canvas.draw()
        
        # Close the figure
        plt.close(self.fig)
        
        return
    
    def contRun(self):
        """
        Method to create and start the thread for realtime plotting
        """
        # Create an event for stopping the program
        self.event.clear()
        
        # Create the thread for the plot loop
        if(self.thread.is_alive() == False):
            self.thread = threading.Thread(target = self.plotLoop, daemon = True)
            self.thread.start()
        
        return

    def stopRun(self):
        """
        Stop the realtime plotting
        """
        # Set the event to stop the thread
        self.event.set()
        
        return

    def plotLoop(self):
        """
        Method for realtime plotting
        """
        while(self.event.is_set() == False):
            self.measureAndPlot()
            time.sleep(0.01)
        
        return
    
    def on_closing(self):
        """
        When closing the window
        """
        # Set event to stop thread
        self.event.set()
        
        # Wait for thread to close
        if(self.thread.is_alive()):
            self.thread.join()

        
        # Destroy window
        self.master.destroy()
        
        return



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
        
        # Create thread manager object 
        self.threadManager = ThreadManager()
        
        # Create device manager object
        self.deviceManager = DeviceManager()
        
        # Create measurement settings object
        self.measurementSettings = MeasurementSettings()
        
        # DEFINE TABS UNDER PARENT
        self.runframe = tk.Frame(self.tab_parent)
        self.settingsframe = tk.Frame(self.tab_parent)
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
        self.gen_settings_frame()
        self.generate_tab_1()
        self.generate_tab_2()
        
        
        
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

        return
        
    def gen_settings_frame(self):
        
        self.settingsframe.rowconfigure([0], minsize=30, weight=1)
        self.settingsframe.columnconfigure([0,1], minsize=30, weight=1)
        
        self.esframe = tk.Frame(self.settingsframe, borderwidth = 2, relief="groove") #, bg = '#9aedfd')
        self.esframe.rowconfigure([0,1,2,3,4,5,6,7], minsize=30, weight=1)
        self.esframe.columnconfigure([0, 1], minsize=30, weight=1)
        self.esframe.grid(row = 1, column = 0, sticky = 'NEW', padx = 20, pady = 20)
        
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
        
        # Generate device frame
        self.deviceFrame = tk.Frame(self.settingsframe, borderwidth = 2,relief="groove")
        self.deviceFrame.rowconfigure([0], minsize=30, weight=1)
        self.deviceFrame.columnconfigure([0], minsize=30, weight=1)
        self.deviceFrame.grid(row = 0, column = 0, sticky = 'NEW', padx = 20, pady = 20)
        
        
        DeviceManagerBox(self.deviceFrame, self.deviceManager)
        
        return
    
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
        # self.fig1, self.plot1, self.can1 = self.genFig(self.plotframe)
        self.specWindow = SpecWindow(self.plotframe, self.deviceManager, self.threadManager)
        # TODO: finish
        
        
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
    
    def load_dt(self): #, datapath, emitter):
        """
        Find the dT of a single measurement

        Returns
        -------
        None.

        """                
        
        # GET FOLDER NAME
        datapath = self.entry.get()        
        
        emitter = "emitter-1"
        """ Generate emitter data object """
        # CREATE EMITTER DATA OBJECTS
        EM = da.emitterData()
        
        # LOAD EMITTER DATA INTO OBJECT
        EM.loadFolder(datapath+"\\"+emitter)
        
        """ Report data calcs """            
        # REPORT DT DATA
        try:
            self.mprint("......dT-10-90 = {:.6} C".format(EM.getDT()))
        except:
            self.mprint("\n......ERROR: Missing 10% or 90% duty cycle data.")
            
        try:
            self.mprint("......dT-0-100 = {:.6} C".format(EM.getDT_New()))
            self.mprint("......CW WL = {:.6} nm".format(EM.getCWWL()))

        except:
            self.mprint("......ERROR: Failed to parse data.")
        
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
    
    def genFig2(self, frame):
        return
        event = None
        spec = self.deviceManager.osa
        SpecWindow(frame, spec, event)
        
    
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
                self.thread1 = threading.Thread(target = self.run_measurement)
                
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
            
            # Close all devices
            self.deviceManager.closeDevices()
            
            # DESTROY APPLICATION
            self.master.destroy()
            
        return
    
    def run_measurement(self):
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
                        
            # GET HEXEL TITLE
            titlemod  = self.hexel.get()
            
            # CHECK IF HEXEL NAME IS A REPEAT
            savedir = os.listdir(self.measurementSettings.savePath)
            h_name = titlemod
            if(any(h_name in savefldr for savefldr in savedir)):
                if(self.repeat_hexel(h_name) == False):
                    self.mprint("\nStopped due to repeat hexel name.\n")
                    return
            
            # Set Ocean Optics HR4000 integration time in micro seconds
            self.mprint("...OSA integration time set to {} us.".format(self.measurementSettings.integrationTime))
            
            # Sleep Time - Set time to reach steady state in seconds   
            self.mprint("...Emitter dwell time set to {} s.".format(self.measurementSettings.dwellTime))
            
            # Sleep Time between switching emitters
            self.mprint("...Cooldown time set to {} s.".format(self.measurementSettings.coolDownTime))
            
            # DUTY CYCLES TO MEASURE
            self.mprint("...Duty cycles to measure:")
            for dutycycle in self.measurementSettings.dutycycles:
                self.mprint("......{}".format(dutycycle))

            # Generate save folder
            testdata_path = os.path.abspath(self.measurementSettings.savePath)
            strtime = time.strftime("%Y%m%d-%H%M%S")  
            datafolder = "Hexel"+titlemod+"-"+strtime
            folder = "\\".join([testdata_path,datafolder])
            
            # Insert folder name into load measurement entry box
            self.entry.delete(0,"end")
            self.entry.insert(0, folder)
            
            # PRINT SAVE LOCATION
            self.mprint("...Data save location:")
            for s in folder.split("\\"):
                self.mprint("......{}/".format(s))

            # CHECK DEVICE COMMUNICATION
            self.mprint("\nChecking devices")
            
            ######################## CHECK ITC4005 ###########################            
            self.mprint("...ITC4005")
            try:
                # CS = ld.CurrentSupply(itc4005addr)
                CS = self.deviceManager.ld
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
                # RC = ra.Relay.RelayControl(usb6001dev)
                RC = self.deviceManager.relay
            except:
                self.mprint("ERROR:\n...Failed to connect to relay controller.")
                return
            self.mprint("......Connection established.")
            
            ######################## CHECK HR4000 ############################
            self.mprint("...Ocean Optics HR4000")
            try:
                # SA = sa.SpectrumAnalyzer(integration_time = integrationTime, serialnum = hr4000serial)
                SA = self.deviceManager.osa
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
                    self.mprint("......Waiting {} seconds.".format(self.measurementSettings.coolDownTime))
                    self.sleep(self.measurementSettings.coolDownTime)
                
                # Means
                means = []
                
                # DUTY CYCLE LOOP
                for dc in self.measurementSettings.dutycycles:
                    # START DUTY CYCLE MEASUREMENT
                    self.mprint("......Testing duty cycle: {}%".format(dc))
                    
                    # SET CURRENT CONTROLLER DUTY CYCLE
                    CS.setDutyCycle(dc)
                    
                    # TURN CURRENT SUPPLY ON
                    CS.switchOn()
                    
                    # WAIT FOR STEADY STATE
                    self.sleep(self.measurementSettings.dwellTime)
                    
                    # MEASURE SPECTRUM
                    SA.measureSpectrum()

                    # GET X AND Y DATA FOR REALTIME PLOT
                    # y = np.random.rand(16000)             # for testing
                    # x = np.linspace(400,500,len(y))       # for testing
                    x, y = SA.getData()
                    
                    # GENERATE REALTIME PLOTS
                    self.plot(self.plotframe, self.fig1, self.plot1, self.can1, x = x, y = y)
                    
                    # GENERATE SAVE FILE PATH
                    emittercorrection = i + 1
                    emitter_folder = "emitter-{}".format(emittercorrection)
                    dc_file = "dc-{}.csv".format(dc)
                    filename = "\\".join([folder, emitter_folder, dc_file])

                    # Save spectrum
                    SA.saveIntensityData(filename)
                    
                    # Print recent DT
                    self.load_dt(emitter_folder)
                    
                    # Find statistics
                    mean, sdev, skew, kurt = SA.findStatistics()
                    
                    # Append mean
                    means.append(mean)
                    self.mprint("\n.........mean: {:.2f} nm".format(mean))
                    
                # SET CURRENT TO 0
                CS.switchOff()
                
            # MEASUREMENT FINISHED            
            self.mprint("\nMeasurement finished!")
        
        
            ################## CALL DATA ANALYSIS PROGRAM ####################
        
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
            try:
                CS.switchOff()
            except:
                pass
            self.mprint("Program reset triggered.")
            # Delete "folder" directory 
            if tk.messagebox.askokcancel("Yes", "Delete {}?".format(folder)):
                shutil.rmtree(folder)
        
        except Exception as ex:
            # GENERAL ERROR
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            self.mprint("\nUNKNOWN ERROR:\n...Message Ryan to troubleshoot.")  
            
        finally:
            try:
                CS.switchOff()
            except:
                pass
            self.running = False
            self.enabled = False
        
        return

class Error(Exception):
    
    pass

class ProgramReset(Exception):
    
    pass

class InterlockError(Exception):
    
    pass



"""
Holds data for a single duty cycle.
"""
class DutyCycle:
    def __init__(self, dutyCycle):
        self.dutyCycle = dutyCycle
        self.CWL = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
        self.FWHM = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
        pass
    
"""
Holds data for all duty cycles.
"""
class DutyCycles:
    def __init__(self):
        self.dutyCycles = []
    
    def store(self, dutyCycle, emitter, cwl, fwhm):
        """
        Method to store data
        """
        
        # TODO: check for NaN
        
        # Check if a duty  entry already exists
        for dc in self.dutyCycles:
            if(dutyCycle == dc.dutyCycle):
                dc.CWL[emitter - 1] = cwl
                dc.FWHM[emitter - 1] = fwhm
                return
        
        # Create a new object
        tmp = DutyCycle(dutyCycle)
        tmp.CWL[emitter-1] = cwl
        tmp.FWHM[emitter-1] = fwhm
        
        # Append object to self
        self.dutyCycles.append(tmp)
        
        return
        
    def write(self, hexelSn):
        
        for dc in self.dutyCycles:
            writeToDb(hexelSn, dc.dutyCycle, dc.CWL, dc.FWHM)
        
        return
                
        

"""
arguments are; 
    the serial number of the hexel being tested
    the % DC of the test
    the center wavelength readings for each emitter (array of 6)
    the spectrum width readings for each emitter (array of 6)
"""
import pyodbc
def writeToDb(HexelSn, DC, CWL, FWHM):
    cnxn = pyodbc.connect(("Driver={SQL Server}; Server=NSQL\LASERPRODUCTION; Database=CosModules; Trusted_Connection=yes;"))
    cursor = cnxn.cursor()     
    command = ("INSERT INTO [CosModules].[dbo].[SETS] ([Date_Time],[HexelSN],[DC],"
      "[CentralWL_1],[CentralWL_2],[CentralWL_3],[CentralWL_4],[CentralWL_5],[CentralWL_6],"
      "[FWHM_1], [FWHM_2], [FWHM_3], [FWHM_4], [FWHM_5], [FWHM_6]"
      " ) VALUES (GETDATE(), "+ str(HexelSn) + ", " + str(DC) + ", ")
    command = command + str(CWL[0])+", "+str(CWL[1])+", "+str(CWL[2])+", " +str(CWL[3])+", " +str(CWL[4])+", " +str(CWL[5])+", "  
    command = command + str(FWHM[0])+", +"+str(FWHM[1])+", " +str(FWHM[2])+", "+str(FWHM[3])+", "+str(FWHM[4])+", "+str(FWHM[5])+");"
    cursor.execute(command) 
    cnxn.commit() 
    cursor.close()
    cnxn.close()  


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
