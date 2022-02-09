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

from scipy import stats as sts
import numpy as np # for data manipulation
import os # for directory navigating
import math # for math
import matplotlib.pyplot as plt # for plotting
from operator import attrgetter # for sortings

def main():
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
        em = emitterData(datapath+em)

        # IGNORE BROKEN EMITTERS
        if(em.title in ignores):
            break
        
        # PRINT OUT PARAMETERS
        print("emitter: {}".format(em.getEmitterNum()))
        print("...dt: {}".format(em.getDT()))
        
        # GENERATE PLOTS
        # em.plotIntensity()
        em.plotIntensityNorm()
        em.plotPeak()
        em.plotSdev()
        em.plotSkew()
        em.plotKurt()
    
    return

def mainCall(data):
    # DATA FOLDER TO ANALYZE
    #data = r'Hexel1002570 Test-20220207-125243'
    #data = r'Hexel1002570-Broken Emiiter 6-Long Sleep Time-20220207-190556'

    
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
    
    # PARSE WL DATA TO A NUMPY ARRAY
    # wls = np.genfromtxt(wlfilename)
    
    for em in emitters:
        
        em = emitterData(datapath+em)
        
        em.plotIntensity()
    
        em.plotPeak()
        
        em.getDT()        
        
    
    return

class dutyCycleData:
    def __init__(self,filename):
        
        # PARSE THE INTENSITY DATA
        data = np.genfromtxt(filename, delimiter = ",")
        self.x = data[:,0]
        self.y = data[:,1]
        
        # LIMIT THE RANGE OF THE DATA
        index_start = np.where(self.x > 435)[0][0]
        index_end = np.where(self.x > 455)[0][0]        
        self.x = self.x[index_start:index_end]
        self.y = self.y[index_start:index_end]
        
        # Parse duty cycle from filename
        self.dutyCycle = float(filename.split("\\")[-1].strip('.csv').strip('dc-'))
        
        # DETERMINE DATA RELIABILITY
        self.reliable = True
        if(np.max(self.y) - np.min(self.y) < 200):
            self.reliable = False
            return
        
        # GENERATE DATA
        self.getNorm()
        self.getMean()
        self.getSdev()
        self.getSkew()
        self.getKurt()
        
        return
    
    def getDutyCycle(self):
        
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
        
        floor = 50
        for i in range(0,len(self.yf)):
            if(self.yf[i] < floor):
                self.yf[i] = 0
        
        # self.yf = self.yf - np.min(self.yf)
        
        
        
        # NORMALIZE
        self.yf = self.yf / np.sum(self.yf)                
    
        return self.yf
    
    def getMean(self):

        # FIND WEIGHTED MEAN PEAK        
        self.wMean = np.dot(self.x, self.yf)
        
        return self.wMean
    
    def getSdev(self):
        
        # CALCULATE THE VARIANCE
        n = 2
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE STANDARD DEVIATION
        self.sdev = math.sqrt(abs(moment))
        
        return self.sdev

    def getSkew(self):
        
        # CALCULATE THIRD CENTRAL MOMENT
        n = 3
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE KURTOSIS
        self.skew = moment / (self.sdev**n)
        
        return self.skew
    
    def getKurt(self):
        
        # CALCULATE FOURTH CENTRAL MOMENT
        n = 4
        moment = np.dot((self.x - self.wMean)**n, self.yf)
        
        # CALCULATE KURTOSIS
        self.kurt = moment / (self.sdev**n)
        
        return self.kurt

class emitterData:
    def __init__(self,filepath):
        # GENERATE TITLE BASED ON FOULDER NAME
        self.title = filepath.split("\\")[-1]
        
        # ADD WAVELENGTHS TO OBJECT
        #self.wavelengths = wavelengths
        
        # LIST ALL DUTY CYCLE FILES FOR THIS EMITTER
        self.files = os.listdir(filepath)
        
        # GENERATE FULL FILEPATH TO DUTY CYCLE CSV FILES
        # print(self.title)
        self.dutyCycles = []
        for file in self.files:
            filewithpath = filepath + "\\" + file
            self.dutyCycles.append(dutyCycleData(filewithpath))
        
        
        self.dutyCycles.sort(key = attrgetter('dutyCycle'))
        
        return
    
    def getEmitterNum(self):
        
        return self.title.split("-")[-1]
    
    def getDT(self):
        
        for dc in self.dutyCycles:
            if(dc.dutyCycle == 10):
                s1 = dc.wMean
            elif(dc.dutyCycle == 90):
                s2 = dc.wMean
        dt = (s2 - s1) / 0.06
        
        return dt
    
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

if __name__ == "__main__":
    main()