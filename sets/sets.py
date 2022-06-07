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
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import threading

# ITC4005, RELAY, HR4000 IMPORTS
import instruments

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
        
        # DEFINE TAB PARENTS
        self.tab_parent = ttk.Notebook(self.master)
        
        # DEFINE TABS UNDER PARENT
        self.runframe = tk.Frame(self.tab_parent)
        self.loadframe = tk.Frame(self.tab_parent)
        self.wlframe = tk.Frame(self.tab_parent)
        self.sdevframe = tk.Frame(self.tab_parent)
        self.skewframe = tk.Frame(self.tab_parent)
        self.kurtframe = tk.Frame(self.tab_parent)
        self.tab_emitter = ttk.Notebook(self.tab_parent)
        
        # GENERATE EMITTER FRAMES
        self.emmitterframes = []
        for i in range(1,7):
            em = tk.Frame(self.tab_emitter)
            em.rowconfigure([0, 1], minsize=30, weight=1)
            em.columnconfigure([0], minsize=30, weight=1)
            self.tab_emitter.add(em, text = "Emitter {}".format(i))
            self.emmitterframes.append(em)

        # GENERATE TABS
        self.generate_tab_1()
        self.generate_tab_2()
        
        # ADD TABS TO PARENT
        self.tab_parent.add(self.runframe, text="Run Measurement")
        self.tab_parent.add(self.loadframe, text="Load Measurement")
        self.tab_parent.add(self.tab_emitter, text = "Emitter Data")
        self.tab_parent.add(self.wlframe, text="Wavelength Means")
        self.tab_parent.add(self.sdevframe, text="Wavelength Sdev")
        self.tab_parent.add(self.skewframe, text="Wavelength Skew")
        self.tab_parent.add(self.kurtframe, text="Wavelength Kurtosis")
        
        # DEFINE THREADS
        self.thread1 = None
        self.thread1 = threading.Thread(target = self.run_app)

        # DEFINE RUNNING
        self.running = False        

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
        
        ############################ PLOT FRAME ##############################
        r = 3
        
        # GENERATE PLOT FRAME
        self.plotframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove")#, highlightbackground="black", highlightthickness=1)
        self.plotframe.grid(row = 1, column = 0, padx = 20, pady = 20)
        
        # GENERATE FIGURE FOR RUNTIME PLOTS
        self.fig1, self.plot1, self.can1 = self.genFig(self.plotframe)
        
        ########################### TEXT BOX #################################
        r = 0
        
        # GENERATE TEXT BOX FOR REPORTING RESULTS
        self.text_box = tk.Text(self.runframe, height = 30, width = 40, borderwidth = 2, relief = "groove")
        self.text_box.grid(row = r, column = 1, rowspan = 2, sticky = "NS", padx = (0,20), pady = 20)
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
            
            # CREATE EMITTER DATA OBJECTS
            EM = da.emitterData()
            
            # LOAD EMITTER DATA INTO OBJECT
            EM.loadFolder(datapath+"\\"+emitters[i])
            
            # GENERATE FIGURES AND PLOTS
            emfig = EM.getIntensityFigure()
            
            # GENERATE INTENSITY PLOTS
            self.genEmitterPlot(self.emmitterframes[i], emfig)
            
            # REPORT DT DATA
            self.mprint("...{}".format(emitters[i]))
            self.mprint("......dT = {} nm/C".format(EM.getDT()))
            self.mprint("......CW WL = {} nm".format(EM.getCWWL()))
            
            # GENERATE FIGURES
            wMeanFigure, wMeanPlot = EM.getPeakFigure(wMeanFigure, wMeanPlot)
            sdevFigure, sdevPlot = EM.getSdevFigure(sdevFigure, sdevPlot)
            skewFigure, skewPlot = EM.getSkewFigure(skewFigure, skewPlot)
            kurtFigure, kurtPlot = EM.getKurtFigure(kurtFigure, kurtPlot)

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
            self.mprint("\n")
 
        return
    
    def run_app(self):
        """
        Create a new thread and run the test.

        Returns
        -------
        None.

        """
        # CHECK IF PROGRAM IS ALREADY RUNNING
        if(self.running == False):
            
            # MARK AS RUNNING
            self.running = True
            
            # CHECK IF THREAD IS ALIVE
            if(self.thread1.is_alive() ==  False):
                
                # CREATE THREAD OBJECT TARGETTING THE PROGRAM
                self.thread1 = threading.Thread(target = self.run_app2)
                
                # START THREAD
                self.thread1.start()
        
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
            
            CS = instruments.CurrentSupply(itc4005addr)
            
            self.mprint("......Connection established.")
            
            # CHECK INTERLOCK
            intrlck = CS.protectionQuery()
            self.mprint("......Interlock state: {}".format(intrlck))
            if(intrlck == 1):
                raise InterlockError()
            
            # SET PRESETS FOR LASER DRIVER
            self.mprint("......Setting device presets.")
            CS.setPresets()
            
            ###################### CHECK NI USB6001 ##########################
            self.mprint("...NI USB-6001")
            
            RC = instruments.RelayControl(usb6001dev)

            self.mprint("......Connection established.")
            
            ######################## CHECK HR4000 ############################
            self.mprint("...Ocean Optics HR4000")
            
            SA = instruments.SpectrumAnalyzer(integration_time = integrationTime, serialnum = hr4000serial)
            
            self.mprint("......Connection established.")
            
            
            ####################### START MEASUREMENT ########################            
            self.mprint("\nRunning measurement for {}.".format(titlemod))
            
            # EMITTER SELECTION LOOP
            for i in range(0,6):
                
                self.mprint("...Testing emitter {}.".format(6-i))
                
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
                    emittercorrection = 6 - i
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
            SA.close()
            CS.close()
            self.running = False
        
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
