# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 13:28:47 2022

@author: ryan.robinson

Just a jumbled mess of code to quickly figure out how long it takes an emitter
to reach steady sate.
"""


import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    
    # GENERATE MAIN FILE PATHS
    path = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
    data = r'steady-state-test-20220207-111750'
    datapath = path + "\\" + data +"\\"
    
    # GENERATE WL DATA FILENAME AND PATH
    wlfilename = datapath + "wavelengths.csv"
    
    files = os.listdir(datapath)
    
    rfiles = []
    for file in files:
        if('.csv' in file and 'wavelengths.csv' not in file):
            rfiles.append(file)
    

    # PARSE WL DATA TO A NUMPY ARRAY
    wls = np.genfromtxt(wlfilename)
    

    
    e0 = emitterTimeData(datapath,wls)
    
    e0.plot()
    
    return


class dutyCycleData:
    def __init__(self,filename):
        self.data = np.genfromtxt(filename)         
        return
    
    def setTime(self,time):
        self.time = float(time)
        return

class emitterTimeData:
    def __init__(self,datapath,wavelengths):

        self.title = "Time Data"
        self.wavelengths = wavelengths
        self.files = os.listdir(datapath)
        
        self.rfiles = []
        for file in self.files:
            if('.csv' in file and 'wavelengths.csv' not in file):
                self.rfiles.append(file)
        
        print(self.rfiles.sort(key = self.sortFunc))

        self.dutyCycles = []
        
        for file in self.rfiles:
            filewithpath = datapath + "\\" + file
            self.dutyCycles.append(dutyCycleData(filewithpath))
        
        self.times = []
        
        for file in self.rfiles:
            a = file.strip('.csv')
            a = "{:.4f}".format(float(a))
            self.times.append(a)
            
        for i in range(0,len(self.dutyCycles)):
            self.dutyCycles[i].setTime(self.times[i])
            
        return
    
    def sortFunc(self,a):
        a = a.strip('.csv')
        a = float(a)
        return a
    
    def plot(self):
        
        legend = []
        for dutyCycle in self.dutyCycles:
            plt.figure(0)
            plt.plot(self.wavelengths, dutyCycle.data)
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Intensity")
            plt.title(self.title)
            legend.append(dutyCycle.time)
        
        plt.legend(legend)
        plt.grid()
        return





if __name__=="__main__":
    main()
