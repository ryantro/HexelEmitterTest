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
import sys, time, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# import instruments

# FOR READING CONFIG FILE
import configparser


# Import data analysis
sys.path.append('../dataanalysis/')
import dataanalysisV2 as da

class Application:
    def __init__(self, master):
        self.master = master
        # self.master.configure(bg = "#808080")
        
        # SET THEMES
        # s = ttk.Style()
        # print(s.theme_names())
        # s.theme_use("clam")
        # self.master.iconphoto(False, 'icons/eticon.png')
        
        # 
        self.master.iconbitmap(r'icons\eticon.ico')
        # pyinstaller --onefile -w -F --add-binary "my.ico;." my.py
        
        # DEFINE TAB PARENTS
        self.tab_parent = ttk.Notebook(self.master)
        
        # DEFINE TABS
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

        self.generate_tab_1()
        self.generate_tab_2()

        self.tab_parent.add(self.runframe, text="Run Measurement")
        self.tab_parent.add(self.loadframe, text="Load Measurement")
        self.tab_parent.add(self.tab_emitter, text = "Emitter Data")
        self.tab_parent.add(self.wlframe, text="Wavelength Means")
        self.tab_parent.add(self.sdevframe, text="Wavelength Sdev")
        self.tab_parent.add(self.skewframe, text="Wavelength Skew")
        self.tab_parent.add(self.kurtframe, text="Wavelength Kurtosis")
        
        
    def generate_tab_1(self):

        minw = 25
        # GRID CONFIGURE
        self.runframe.rowconfigure([0, 1, 2], minsize=30, weight=1)
        self.runframe.columnconfigure([0, 1], minsize=minw, weight=1)
        
        # BOX CONFIGURE
        self.master.title('Hexel Emitter Test')
        w = 80
        

        
        ##################### HEXEL ENTRY BOX #################################
        r = 0
        
        self.hexelframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove") #, highlightbackground="black", highlightthickness=1)
        self.hexelframe.columnconfigure([0, 1], minsize=50, weight=1)
        self.hexelframe.rowconfigure([0], minsize=50, weight=1)
        self.hexelframe.grid(row = 0, column = 0, padx = 20, pady = (20,0), sticky = "EW")
        
        
        # GENERATE HEXEL NAME BOX LABEL
        pxs = tk.Label(self.hexelframe, text="Hexel Serial Number:", font = ('Ariel 15'))
        pxs.grid(row = r, column = 0, sticky = "w", padx = 10)
        
        # GENERATE HEXEL NUMBER ENTRY BOX
        self.hexel = tk.Entry(self.hexelframe, text = 'hexel', width = minw, font = ('Ariel 15'), borderwidth = 2)
        self.hexel.insert(0, '100XXXX')
        self.hexel.grid(row=r, column=1, sticky = "WE", padx = 10)
        
        
        
        ############################ PLOT FRAME ##############################
        r = 3
        
        self.plotframe = tk.Frame(self.runframe, borderwidth = 2,relief="groove")#, highlightbackground="black", highlightthickness=1)
        self.plotframe.grid(row = 1, column = 0, padx = 20, pady = 20)
        
        self.fig1, self.plot1, self.can1 = self.genFig(self.plotframe)
        self.plot(self.plotframe, self.fig1, self.plot1, self.can1)
    
        
        ########################### TEXT BOX #################################
        r = 0
        
        self.text_box = tk.Text(self.runframe, height = 30, width = 40, borderwidth = 2, relief = "groove")
        self.text_box.grid(row = r, column = 1, rowspan = 2, sticky = "NS", padx = (0,20), pady = 20)
        self.text_box.insert("end","")
        self.text_box.config(state = 'disabled')
        
        ############################## ROW 6 #################################
        r = 2
        
        # RUN BUTTON
        self.getButton = tk.Button(self.runframe, text = 'Run Automated Test!', command = self.run_app, font = ('Ariel 15'), borderwidth = 4)
        self.getButton.grid(row=r, column=0, columnspan = 2, pady = (0,20), padx = 20, sticky = "EW")

        # FINALLY
        self.tab_parent.pack()
        return
    
    def mprint(self, text, append = True):
        self.text_box.config(state = 'normal')
        if(append == False):
            self.text_box.delete("1.0","end")
        self.text_box.insert("end", text+"\n")
        self.text_box.config(state = 'disabled')
        self.text_box.update()
        self.text_box.see("end")
        
        self.text_box2.config(state = 'normal')
        if(append == False):
            self.text_box2.delete("1.0","end")
        self.text_box2.insert("end", text+"\n")
        self.text_box2.config(state = 'disabled')
        self.text_box2.update()
        self.text_box2.see("end")
        
        return
    
    def generate_tab_2(self):
        minw = 25
        
        span = 6
        r = 0
        
        # GRID CONFIGURE
        self.loadframe.rowconfigure([0, 1, 2], minsize=10, weight=1)
        self.loadframe.columnconfigure([0], minsize=10, weight=1)
        
        # FILE SELECTION FRAME
        self.loadbox = tk.Frame(self.loadframe)
        self.loadbox = tk.Frame(self.loadframe, borderwidth = 2,relief="groove") #, highlightbackground="black", highlightthickness=1)
        self.loadbox.columnconfigure([0, 1, 2], minsize=50, weight=1)
        self.loadbox.rowconfigure([0], minsize=50, weight=1)
        self.loadbox.grid(row = 0, column = 0, padx = 20, pady = (20,0), sticky = "NEW")
        
        # FILENAME LABEL
        self.entryLabel = tk.Label(self.loadbox,text="Foldername:")
        self.entryLabel.grid(row=0, column=0, sticky = "w")

        
        # FILENAME ENTRY BOX
        self.entry = tk.Entry(self.loadbox, text = 'Entry', width = minw*4)
        self.entry.insert(0, r'testdata\Hexel1002570-20220208-102829')
        self.entry.grid(row=0, column=1)

        # BROWS FOR FILE
        self.browsButton = tk.Button(self.loadbox, text = 'Browse', command = self.brows)
        self.browsButton.grid(row = 0, column = 2)
        
        
        ######################################################################
        
        self.text_box2 = tk.Text(self.loadframe, height = 33, width = 40, borderwidth = 2, relief = "groove")
        self.text_box2.grid(row = 1, column = 0, sticky = "NSEW", padx = 20, pady = 20)
        self.text_box2.insert("end","")
        self.text_box2.config(state = 'disabled')
        
        
        
        r = 5
        
        # RUN BUTTON
        self.getButton = tk.Button(self.loadframe, text = 'Load Folder and Analyze Data!', command = self.load_folder, font = ('Ariel 15'), borderwidth = 4)
        self.getButton.grid(row=2, column=0, padx = 20, pady = (0,20), sticky = "ews")
        
        return
    
    def brows(self):
        filename = fd.askdirectory()
        filename = filename
        self.entry.delete(0,'end')
        self.entry.insert(0,filename)
        
        return
    
    def load_folder(self):
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
            
            self.genEmitterPlot(self.emmitterframes[i], emfig)
            
            self.mprint("...{}".format(emitters[i]))
            
            self.mprint("......dT = {}".format(EM.getDT()))
            
            wMeanFigure, wMeanPlot = EM.getPeakFigure(wMeanFigure, wMeanPlot)
            sdevFigure, sdevPlot = EM.getSdevFigure(sdevFigure, sdevPlot)
            skewFigure, skewPlot = EM.getSkewFigure(skewFigure, skewPlot)
            kurtFigure, kurtPlot = EM.getKurtFigure(kurtFigure, kurtPlot)

        self.genEmitterPlot(self.wlframe, wMeanFigure)
        self.genEmitterPlot(self.sdevframe, sdevFigure)
        
        self.genEmitterPlot(self.skewframe, skewFigure)
        
        self.genEmitterPlot(self.kurtframe, kurtFigure)
        
        
        # GET PLOT FIGURES
        # emfig, emplot = EMS[1].getIntensityFigure()
        # self.genEmitterPlot(self.e1, emfig, emplot)
        
        
        return
    
    def plotEmitters(self):
        
        return
    
    def plotWl(self):
        
        return
    
    
    def plotSdev(self):
        
        return
    
    def plotSkew(self):
        
        return
    
    def plotKurt(self):
        
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
        
        # the figure that will contain the plot
        fig = plt.figure(figsize = (5, 5), dpi = 100)
        # adding the subplot
        plot1 = fig.add_subplot(111)
        
        
        canvas = FigureCanvasTkAgg(fig, master = frame)  
        canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20)
        canvas.draw()

        return fig, plot1, canvas
    
    def plot(self, frame, fig, plot1, canvas, x = [], y = []):
        

       
        # plotting the graph
        y = np.random.rand(100)
        # plot1.set_figure(fignum)
        plot1.clear()
        plot1.plot(y)
        
        plot1.set_title("Runtime Plots")
        plot1.set_xlabel("Wavelength (nm)")
        plot1.set_ylabel("Intensity")
        
        
        # DRAW THE PLOT
        canvas.draw()
        
            
        # creating the Matplotlib toolbar
        # toolbarFrame = tk.Frame(master=window)
        # toolbarFrame.grid(row=3, column=1, columnspan = 3, sticky = "w")
        # toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        # plt.show()
        plt.close(fig)

        return
    
    def runTimePlot(self, frame, fig, plot1, canvas, x = [], y = []):
        

       
        # plotting the graph
        y = np.random.rand(100)
        # plot1.set_figure(fignum)
        plot1.clear()
        plot1.plot(y)
        
        
        plot1.set_title("Runtime Plots")
        plot1.set_xlabel("Wavelength (nm)")
        plot1.set_ylabel("Intensity")
        
        # creating the Tkinter canvas
        # containing the Matplotlib figure
        
        
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, ipadx=40, ipady=20, columnspan = 4)
        
            
        # creating the Matplotlib toolbar
        # toolbarFrame = tk.Frame(master=window)
        # toolbarFrame.grid(row=3, column=1, columnspan = 3, sticky = "w")
        # toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        # plt.show()
        plt.close(fig)

        return
    
    def plotemitter(self, frame, emitter):
        
        
        return
    
    def run_app(self):
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
            configfile = 'hexelemittertest.cfg'
            file_exists = os.path.exists(configfile)
            
            # CHECK IF CONFIG FILE EXISTS
            if(file_exists == False):
                raise FileNotFoundError(configfile)
                
            # LOAD DATA INTO CONFIGPARSER OBJECT
            config.read(configfile)
            
            # LOAD HR4000 INTEGRATION TIME
            integrationTime = config['SETTINGS']['HR4000_Integration_Time']
            
            # LOAD DUTY CYCLES
            dutycyclesstr = config['SETTINGS']['Duty_Cycles']
            dutycycles = np.array(dutycyclesstr.split(","), dtype = int)
            
            # LOAD SLEEP TIMES
            sleepT = float(config['SETTINGS']['Laser_Dwell_Time'])
            sleepT2 = float(config['SETTINGS']['Laser_Dwell_Time'])
            
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
            
            testdata_path = os.path.abspath(testdata_folder)
            # DEFINE AND CREATE folder STRUCTURE
            # folder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
            strtime = time.strftime("%Y%m%d-%H%M%S")  
            datafolder = "Hexel"+titlemod+"-"+strtime
            folder = "\\".join([testdata_path,datafolder])
            # self.mprint("...Save folder: {}".format(folder))
            
            # SAVE LOCATION
            self.mprint("...Data save location:")
            for s in folder.split("\\"):
                self.mprint("......{}/".format(s))

            
            # CREATE INSTRUMENT OBJECTS
            # SA = instruments.SpectrumAnalyzer(integrationTime)        
            # CS = instruments.CurrentSupply()
            # RC = instruments.RelayControl()
            
            # CHECK DEVICE COMMUNICATION
            self.mprint("\nChecking devices")
            
            ######################## CHECK ITC4005 ###########################
            self.mprint("...ITC4005")
            self.mprint("......Connection established.")
            
            # CHECK INTERLOCK
            intrlck = 0 # TODO: REPLACE WITH METHOD
            self.mprint("......Interlock state: {}".format(intrlck))
            if(intrlck == 1):
                raise InterlockError()
            
            # SET PRESETS FOR LASER DRIVER
            self.mprint("......Setting device presets.")
            # CS.setPresets()
            
            ###################### CHECK NI USB6001 ##########################
            self.mprint("...NI USB-6001")
            self.mprint("......Connection established.")
            
            ######################## CHECK HR4000 ############################
            self.mprint("...Ocean Optics HR4000")
            self.mprint("......Connection established.")
            
            self.mprint("\nRunning measurement for {}.".format(titlemod))
            
            # EMITTER SELECTION LOOP
            for i in range(0,6):
                
                self.mprint("...Testing emitter {}.".format(6-i))
                
                # SET CURRENT TO 0
                # CS.switchOff()
                
                # TURN ON SPECIFIC EMITTER 
                # RC.turnOn(i)
                
                # Wait to turn on new emitter
                if(i != 0):
                    self.mprint("......Waiting {} seconds.".format(sleepT2))
                    time.sleep(sleepT2)
                
                # DUTY CYCLE LOOP
                for dc in dutycycles:
                    
                    self.mprint("......Testing duty cycle: {}%".format(dc))
                    
                    self.plot(self.plotframe, self.fig1, self.plot1, self.can1)
                    
                    # SET CURRENT CONTROLLER DUTY CYCLE
                    # CS.setDutyCycle(dc)
                    
                   
                    
                    # TURN CURRENT SUPPLY ON
                    # CS.switchOn()
                    
                    # GET RUNNING DATA
                    # print("......Laser State: {}".format(CS.getState()))
                    # print("......Laser Current: {}".format(CS.getCurrent()))
                    # print("......Laser Duty Cycle: {}".format(CS.getDutyCycle()))
                    
                    
                    # WAIT FOR STEADY STATE - TODO: FIND WAIT TIME
                    time.sleep(sleepT)
                    
                    # MEASURE SPECTRUM
                    # SA.measureSpectrum()
                    # SA.plotSpectrum("Emitter: {}\nDuty Cycle: {}".format(6-i,dc))
                    
                    # self.plot(self.plotframe, self.fig1, self.plot1, self.can1)
                    
                    # GENERATE SAVE FILE PATH
                    emittercorrection = 6 - i
                    emitter_folder = "emitter-{}".format(emittercorrection)
                    dc_file = "dc-{}.csv".format(dc)
                    filename = "\\".join([folder, emitter_folder, dc_file])

                    # SAVE SPECTRUM
                    # SA.saveIntensityData(filename)
                    
                # SET CURRENT TO 0
                # CS.switchOff()
                
                # self.plot(self.wlframe, fignum = 6)
                
            # CALL DATA ANALYSIS PROGRAM
            self.mprint("\nRunning data analysis.")
            # dataanalysis.mainCall(datafolder)
            
            self.mprint("\nProgram finished!")
        
        except FileNotFoundError as ex:
            print(ex)
            self.mprint("\nFILE NOT FOUND ERROR")
            self.mprint("...'{}' not found.".format(str(ex)))
        
        except InterlockError:
            self.mprint("\nINTERLOCK ERROR:")
            self.mprint("...ITC4005 interlock is on.")
        
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            self.mprint("\nUNKNOWN ERROR:\n...Message Ryan to troubleshoot.")  
            
        finally:
            
            
            
            # CLOSE DEVICES
            self.mprint("\nClosing devices.\n")
            # SA.close()
            # CS.close()
        
        return

class Error(Exception):
    
    pass

class InterlockError(Exception):
    
    pass

def main():
   
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

    return


    
if __name__=="__main__":
    main()