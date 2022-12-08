# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 14:52:12 2022

@author: ryan.robinson

For the single emitter testing.  Summary data should include

The weighted mean of the peak          
    OUTPUT: Peak mean for each emitter (to get peak location)
                                
The standard deviation of the peak   
    OUTPUT:  Standard Deviation of each emitter spectrum
                                  
The skew of the peak              
    OUTPUT:  Skew of each emitter spectrum
                                       
The kurtosis of the peak            
    OUTPUT:  Kurtosis of each emitter spectrum
                                               
A linear regression fit to the data – Wavelength vs Duty Cycle for each emitter  
    OUTPUT:  Slope, Intercept, and Rsquare.


"""

# from scipy import stats as sts
import numpy as np # for data manipulation
import os # for directory navigating
import math # for math
import matplotlib.pyplot as plt # for plotting
from operator import attrgetter # for sortings


# CONSTANTS
FH = 6.35
FW = 8.9

def main():
    """
    For testing

    Returns
    -------
    None.

    """
    # DATA FOLDER TO ANALYZE
    #data = r'Hexel1002570 Test-20220207-125243'
    data = r'Hexel1002570-20220208-102829'

    # EMITTERS TO IGNORE
    ignores = ["emitter-6"]
    
    # GENERATE MAIN FILE PATHS
    path = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
    datapath = path + "\\" + data +"\\"
    
    # GENERATE WL DATA FILENAME AND PATH
    wlfilename = datapath + "wavelengths.csv"
    
    # GENERATE EMITTER FOLDER NAMES
    folders = os.listdir(datapath)
    emitters = []
    for folder in folders:
        if("emitter" in folder):
            #foldername = "emitter-{}".format(en)
            #print(foldername)
            emitters.append(folder)
    
    # OPEN FILES AND RUN DATA ANALYSIS
    for em in emitters:
        
        # CREATE EMITTER DATA OBJECTS
        EM = emitterData()
        EM.loadFoler(datapath+em)

        # IGNORE BROKEN EMITTERS
        if(EM.title in ignores):
            break
        
        # if(EM.findDC(10).reliable == False):
        #     break
        # if(EM.findDC(90).reliable == False):
        #     break
        
        
        # PRINT OUT PARAMETERS
        print("emitter: {}".format(EM.getEmitterNum()))
        print("...dt: {}".format(EM.getDT()))
        
        # GENERATE PLOTS
        # em.plotIntensity()
        EM.plotIntensityNorm()
        EM.plotPeak()
        EM.plotSdev()
        EM.plotSkew()
        EM.plotKurt()
    
    return


# OBJECT FOR DUTY CYCLE DATA
class dutyCycleData:
    def __init__(self, dutyCycle = 0, x = [], y = []):
        """
        Init method

        Parameters
        ----------
        dutyCycle : TYPE, optional
            DESCRIPTION. The default is 0.
        x : TYPE, optional
            DESCRIPTION. The default is [].
        y : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        None.

        """
        # SAVE INPUTS TO OBJECT
        self.dutyCycle = dutyCycle
        self.x = x
        self.y = y
        
        # ANALYZE DATA IF DATA HAS BEEN ENTERED
        if(dutyCycle != 0 and len(x) > 0 and len(y) > 0):
            self.analyzeData()
        
        return
    
    
    def loadFile(self,filename):
        """
        Load a duty cycle .csv file into the object.

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # PARSE THE INTENSITY DATA
        data = np.genfromtxt(filename, delimiter = ",")
        self.x = data[:,0]
        self.y = data[:,1]
        
        # Parse duty cycle from filename
        self.dutyCycle = float(filename.split("\\")[-1].strip('.csv').strip('dc-'))
        
        self.analyzeData()
        
        return
    
    def analyzeData(self):
        """
        Perform data analyzing metrics on object.

        Returns
        -------
        bool
            indicator if dataset is reliable.

        """
        # LIMIT THE RANGE OF THE DATA
        index_start = np.where(self.x > 425)[0][0] #'''#changed on 11/16/2022 riley 435 to 455'''
        index_end = np.where(self.x > 460)[0][0]        
        self.x = self.x[index_start:index_end]
        self.y = self.y[index_start:index_end]
        
        
        
        # DETERMINE DATA RELIABILITY
        self.reliable = True
        if(np.max(self.y) - np.min(self.y) < 200):
            self.reliable = False
            return self.reliable
            
        
        # GENERATE DATA
        self.getNorm()
        self.getMean()
        self.getSdev()
        self.getSkew()
        self.getKurt()
        
        return self.reliable
    
    def getDutyCycle(self):
        """
        Get current duty cycle.

        Returns
        -------
        int
            duty cycle for emitter object.

        """
        return self.dutyCycle
    
    def getNorm(self):
        """
        Calculates the peak based on the weighted mean.

        Parameters
        ----------
        wavelengths : numpy array
            list of wavelengths.

        Returns
        -------
        numpy array
            normalized intensity distribution.

        """
        # CHECK IF RELIABLE
        if(self.reliable == False):
            
            # IF DATA IS JUST NOISE, SET NORMALIZE Y TO 0
            self.yf = np.zeros(len(self.x))
            
            return self.yf
        
        # FIND THE INDEX OF THE MAX PEAK
        index = np.argmax(self.y)
        
        # DETERMINE WAVELENGHT SPACING
        wavelength_spacing = self.x[index] - self.x[index - 1]
        
        # OVER ESTIMATE PEAK WIDTH IN TERMS OF INDEX NUMBERS
        halfwidth = 10.0
        d_index = int(halfwidth / wavelength_spacing)
        
        # DEFINE UPPER INDEX AND ENSURE IT IS WITHIN BOUNDS
        dplus_index = d_index + index
        if(dplus_index > len(self.x)):
            dplus_index = len(self.x)
        
        # DEFINE LOWER INDEX AND ENSURE IT IS WITHIN BOUNDS
        dminus_index = index - d_index
        if(dminus_index < 0):
            dminus_index = 0
        
        # DEFINE DATA WITHOUT PEAKS AKA FLOOR
        ynoise = np.concatenate((self.y[:dminus_index],self.y[dplus_index:]), axis = None)
        
        # SUBTRACT THE FLOOR
        self.yf = self.y - np.average(ynoise)
        
        # SET ANY VALUE BELOW THE FLOOR TO 0
        floor = 50
        for i in range(0,len(self.yf)):
            if(self.yf[i] < floor):
                self.yf[i] = 0       
        
        # NORMALIZE
        self.yf = self.yf / np.sum(self.yf)                
    
        return self.yf
    
    def getMean(self):
        """
        Generate the weighted mean.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # FIND WEIGHTED MEAN PEAK
        if(self.reliable):        
            self.wMean = np.dot(self.x, self.yf)
        else:
            self.wMean = None
        
        return self.wMean
    
    def getSdev(self):
        """
        Generate the standard deviation.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # CALCULATE THE VARIANCE
        n = 2
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE STANDARD DEVIATION
        self.sdev = math.sqrt(abs(moment))
        
        return self.sdev

    def getSkew(self):
        """
        Generate the skew.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # CALCULATE THIRD CENTRAL MOMENT
        n = 3
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE KURTOSIS
        self.skew = moment / (self.sdev**n)
        
        return self.skew
    
    def getKurt(self):
        """
        Generate the kurtosis

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # CALCULATE FOURTH CENTRAL MOMENT
        n = 4
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE KURTOSIS
        self.kurt = moment / (self.sdev**n)
        
        return self.kurt

# CLASS FOR EMITTER DATA OBJECT
class emitterData:
    def __init__(self,title = ""):
        """
        Init method.

        Parameters
        ----------
        title : TYPE, optional
            DESCRIPTION. The default is "".

        Returns
        -------
        None.

        """
        # GENERATE TITLE BASED ON FOULDER NAME
        self.title = title
        self.hexel = ""
        
        # GENERATE FULL FILEPATH TO DUTY CYCLE CSV FILES
        self.dutyCycles = []
        
        return
    
    def loadFolder(self, filepath):
        """
        Load the emitter folder.

        Parameters
        ----------
        filepath : str
            path to the folder to load.

        Returns
        -------
        None.

        """
        # GET EMITTER NUMBER FROM FOLDER NAME
        tlist = filepath.split("\\")
        self.title = tlist[-1]
        
        # GET HEXEL SERIAL NUMBER FROM FOLDER NAME
        h1 = tlist[-2]
        h1 = h1.split("/")[-1]
        self.hexel = h1
        
        # LIST ALL DUTY CYCLE FILES FOR THIS EMITTER
        self.files = os.listdir(filepath)
        
        # GENERATE FULL FILEPATH TO DUTY CYCLE CSV FILES
        self.dutyCycles = []
        for file in self.files:
            filewithpath = filepath + "\\" + file
            
            # GENERATE DUTY CYCLE DATA OBJECT
            DC = dutyCycleData()
            
            # LOAD IN DATA
            DC.loadFile(filewithpath)
            
            # APPEND DUTY CYCLE DATA OBJECT TO EMITTER DATA OBJECT
            # if(DC.reliable == True):
            self.dutyCycles.append(DC)
        
        # SORT DUTY CYCLE OBJECTS BY DUTY CYCLE
        self.dutyCycles.sort(key = attrgetter('dutyCycle'))
        
        return
    
    def addDutyCycle(self, dutyCycle, x, y):
        """
        Add a duty cycle data set manually.

        Parameters
        ----------
        dutyCycle : TYPE
            DESCRIPTION.
        x : TYPE
            DESCRIPTION.
        y : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Add duty cycle object
        DC = dutyCycleData(dutyCycle = dutyCycle, x = x, y = y)
        self.dutyCycles.append(DC)
        self.dutyCycles.sort(key = attrgetter('dutyCycle'))
        
        return
                
    
    def getEmitterNum(self):
        """
        Get the current emitter number.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.title.split("-")[-1]
    
    def findDC(self, dc):
        """
        Get specific duty cycle object given the duty cycle

        Parameters
        ----------
        dc : int
            duty cycle to measure.

        Returns
        -------
        DC : dutyCycleData
            dutyCycleData object for specific given dc.

        """
        # FIND THE CORRESPONDING DUTY CYCLE
        for DC in self.dutyCycles:
            if(DC.dutyCycle == dc):
                return DC
        print("Error: Duty cycle {} not found".format(dc))
        
        return None
    
    def getDT(self):
        """
        Get the dT for the emitter.

        Returns
        -------
        float
            dT measurement.

        """
        # s2 = None
        # s1 = None
        # for dc in self.dutyCycles:
        #     if(dc.dutyCycle == 10):
        #         if(dc.reliable):
        #             s1 = dc.wMean
        #     elif(dc.dutyCycle == 90):
        #         if(dc.reliable):
        #             s2 = dc.wMean
        # if(s1 == None or s2 == None):
        #     return "N/A"
        
        # GET WEIGHTED MEAN FOR 10% DUTY CYCLE
        s1 = self.findDC(10).getMean()
        
        # GET WEIGHTED MEAN FOR 50% DUTY CYCLE
        s2 = self.findDC(90).getMean()
            
        # RETURN N/A IF DATA IS UNRELIABLE
        if(s1 == None or s2 == None):
            return "N/A"
        
        # CALCULATE DT
        dt = (s2 - s1) / 0.06
        
        return dt
    
    def getCWWL(self):
        """
        Get the mean wavelength at 99% duty cycle.

        Returns
        -------
        float
            Wavelength at `CW current

        """
        # Find the mean wavelength at 99% duty cycle
        wl = self.findDC(99).getMean()
        
        # Check if data exists
        if(wl == None):
            return "N/A"
        
        # Return wavelength
        return wl
    
    def plotIntensity(self):
        """
        Overlay the intensity plots for each duty cycle

        Returns
        -------
        None.

        """
        # Generate blank legend
        legend = []
        
        # Plot each duty cycle and append legend
        plt.figure(self.title+"norm")
        for dutyCycle in self.dutyCycles:
            plt.plot(dutyCycle.x, dutyCycle.y)
            legend.append("{:.1f}%".format(dutyCycle.dutyCycle))
        
        # Plot formatting
        #plt.xlim([440,445])
        plt.title(self.title)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")
        plt.legend(legend)
        plt.grid()
        
        return
    
    def getIntensityFigure(self):
        """
        Generates plot figures for intensity vs wavelength

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        plot1 : TYPE
            DESCRIPTION.

        """
        # CREATE FIGURE
        fig = plt.figure(figsize = (8, 6), dpi = 100)
        
        # GENERATE SUBPLOT
        plot1 = fig.add_subplot(111)
  
        # FILL OUT PLOTS
        for dutyCycle in self.dutyCycles:
            plot1.plot(dutyCycle.x, dutyCycle.y, label = "{:.1f}%".format(dutyCycle.dutyCycle))
                
        # PLOT FORMATTING
        if(len(self.dutyCycles) > 0):
            plot1.legend(loc='upper right', shadow=True, title = "Duty Cycle")
        plot1.set_title("Spectrum Plot\n"+self.hexel+"/"+self.title, fontsize = 20)
        plot1.set_xlabel("Wavelength (nm)", fontsize = 20)
        plot1.set_ylabel("Intensity", fontsize = 20)
        plot1.grid("on")
        
        return fig
        
    def plotIntensityNorm(self):
        """
        Overlay the intensity plots for each duty cycle

        Returns
        -------
        None.

        """
        # Generate blank legend
        legend = []
        
        # Plot each duty cycle and append legend
        plt.figure(self.title)
        for dutyCycle in self.dutyCycles:
            plt.plot(dutyCycle.x, dutyCycle.yf)
            legend.append("{:.1f}%".format(dutyCycle.dutyCycle))
        
        # Plot formatting
        # plt.xlim([440,445])
        # plt.ylim([-100,100])
        plt.title(self.title+" Normalized")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Normalized Intensity")
        plt.legend(legend)
        plt.grid()
        return

    def plotPeak(self):
        """
        Plot the peak wavelength vs duty cycle.

        Returns
        -------
        None.

        """
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            x.append(dutyCycle.dutyCycle)
            y.append(dutyCycle.getMean())
        
        # Plotting and formatting
        plt.figure(5)
        plt.plot(x,y,label = self.title)
        plt.xlabel('Duty Cycle (%)')
        plt.ylabel('Wavelength (nm)')
        plt.title('Wavelength Shift')
        plt.grid("on")
        plt.legend()
        
        return

    def getPeakFigure(self, fig = None, plot1 = None):
        """
        Generates plot figures for weighted mean vs wavelength

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        plot1 : TYPE
            DESCRIPTION.

        """
        # CREATE FIGURE
        if(fig == None):
            
            # CREATE FIGURE AND PLOT
            fig = plt.figure(figsize = (FW, FH), dpi = 100)
            plot1 = fig.add_subplot(111)
            
            # PLOT FORMATTING
            plot1.set_title("Wavelength Shifts\n"+self.hexel, fontsize = 20)
            plot1.set_xlabel("Duty Cycle (%)", fontsize = 20)
            plot1.set_ylabel("Wavelength (nm)", fontsize = 20)
  
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            if(dutyCycle.reliable):
                x.append(dutyCycle.dutyCycle)
                y.append(dutyCycle.getMean())
        
        # ADD PLOT DATA TO FIGURE
        plot1.plot(x, y, label = self.title, marker = 'o')
        plot1.grid("on")
        
        # ADD LEGEND
        if(len(x) > 0):
            plot1.legend(loc='upper left', shadow=True)
        
        return fig, plot1

    def plotSdev(self):
        """
        Plot the peak wavelength vs duty cycle.

        Returns
        -------
        None.

        """
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            x.append(dutyCycle.dutyCycle)
            y.append(dutyCycle.getSdev())
        
        # Plotting and formatting
        plt.figure(6)
        plt.plot(x,y,label = self.title)
        plt.xlabel('Duty Cycle (%)')
        plt.ylabel('Standard Deviation (nm)')
        plt.title('Peak Standard Deviation')
        plt.grid("on")
        plt.legend()
        
        return

    def getSdevFigure(self, fig = None, plot1 = None):
        """
        Generates plot figures for weighted mean vs wavelength

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        plot1 : TYPE
            DESCRIPTION.

        """
        # CREATE FIGURE
        if(fig == None):
            
            # CREATE FIGURE AND PLOT
            fig = plt.figure(figsize = (FW, FH), dpi = 100)
            plot1 = fig.add_subplot(111)
            
            # PLOT FORMATTING
            plot1.set_title("Wavelength Standard Deviation\n"+self.hexel, fontsize = 20)
            plot1.set_xlabel("Duty Cycle (%)", fontsize = 20)
            plot1.set_ylabel("Wavelength Sdev (nm)", fontsize = 20)
  
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            if(dutyCycle.reliable):
                x.append(dutyCycle.dutyCycle)
                y.append(dutyCycle.sdev)
        
        # ADD PLOT DATA TO FIGURE
        plot1.plot(x, y, label = self.title, marker = 'o')
        plot1.grid("on")        
        
        # ADD LEGEND
        if(len(x) > 0):
            plot1.legend(loc='upper left', shadow=True)
            
        return fig, plot1

    def plotSkew(self):
        """
        Plot the peak wavelength vs duty cycle.

        Returns
        -------
        None.

        """
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            x.append(dutyCycle.dutyCycle)
            y.append(dutyCycle.getSkew())
        
        # Plotting and formatting
        plt.figure(7)
        plt.plot(x,y,label = self.title)
        plt.xlabel('Duty Cycle (%)')
        plt.ylabel('Skewness')
        plt.title('Skewness')
        plt.grid("on")
        plt.legend()
        
        return

    def getSkewFigure(self, fig = None, plot1 = None):
        """
        Generates plot figures for skew vs duty cycle

        Returns
        -------
        fig : TYPE
            DESCRIPTION.
        plot1 : TYPE
            DESCRIPTION.

        """
        # CREATE FIGURE
        if(fig == None):
            
            # CREATE FIGURE AND PLOT
            fig = plt.figure(figsize = (FW, FH), dpi = 100)
            plot1 = fig.add_subplot(111)
            
            # PLOT FORMATTING
            plot1.set_title("Wavelength Skew\n"+self.hexel, fontsize = 20)
            plot1.set_xlabel("Duty Cycle (%)", fontsize = 20)
            plot1.set_ylabel("Skew", fontsize = 20)
  
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            if(dutyCycle.reliable):
                x.append(dutyCycle.dutyCycle)
                y.append(dutyCycle.skew)
        
        # ADD PLOT DATA TO FIGURE
        plot1.plot(x, y, label = self.title, marker = 'o')
        plot1.grid("on")        
        
        # ADD LEGEND
        if(len(x) > 0):
            plot1.legend(loc='upper left', shadow=True)
            
        return fig, plot1

    def plotKurt(self):
        """
        Plot the peak wavelength vs duty cycle.

        Returns
        -------
        None.

        """
        # Generate blank X and Y axis
        x = []
        y = []
        
        # Fill X and Y axis
        for dutyCycle in self.dutyCycles:
            x.append(dutyCycle.dutyCycle)
            y.append(dutyCycle.getKurt())
        
        # Plotting and formatting
        plt.figure(8)
        plt.plot(x,y,label = self.title)
        plt.xlabel('Duty Cycle (%)')
        plt.ylabel('Kurtosis')
        plt.title('Kurtosis')
        plt.grid("on")
        plt.legend()
        
        return

    def getKurtFigure(self, fig = None, plot1 = None):
            """
            Generates plot figures for skew vs duty cycle
    
            Returns
            -------
            fig : TYPE
                DESCRIPTION.
            plot1 : TYPE
                DESCRIPTION.
    
            """
            # CREATE FIGURE
            if(fig == None):
                
                # CREATE FIGURE AND PLOT
                fig = plt.figure(figsize = (FW, FH), dpi = 100)
                plot1 = fig.add_subplot(111)
                
                # PLOT FORMATTING
                plot1.set_title("Wavelength Kurtosis\n"+self.hexel, fontsize = 20)
                plot1.set_xlabel("Duty Cycle (%)", fontsize = 20)
                plot1.set_ylabel("Kurtosis", fontsize = 20)
      
            # Generate blank X and Y axis
            x = []
            y = []
            
            # Fill X and Y axis
            for dutyCycle in self.dutyCycles:
                if(dutyCycle.reliable):
                    x.append(dutyCycle.dutyCycle)
                    y.append(dutyCycle.kurt)
            
            # ADD PLOT DATA TO FIGURE
            plot1.plot(x, y, label = self.title, marker = 'o')
            plot1.grid("on")       
            
            # ADD LEGEND
            if(len(x) > 0):
                plot1.legend(loc='upper left', shadow=True)
                
            return fig, plot1

if __name__ == "__main__":
    main()