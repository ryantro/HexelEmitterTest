# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:46:44 2022

@author: ryan.robinson
"""

import numpy as np
import instruments
import time, os, sys
import matplotlib.pyplot

# Import data analysis
sys.path.append('../dataanalysis/')
import dataanalysis

def main():
    try:
        # Note: Click the terminal and press 
        #       "CTRL + C" to cancel a measurement 
        
        # Edit this to change folder name
        titlemod = "Hexel1002485-"
        
        # Set Ocean Optics HR4000 integration time in micro seconds
        integrationTime = 40000 # 
        
        # Sleep Time - Set time to reach steady state in seconds
        sleepT = 5 # second        
        
        # Sleep Time between switching emitters
        sleepT2 = 20 # seconds
        
        # DUTY CYCLES TO MEASURE
        # dutycycles = [10, 20, 40, 50, 60, 80, 90, 99]
        dutycycles = [10, 50, 90, 99]
        
        
        # FOR OVERNIGHT MEASUREMENT
        #dutycycles = np.linspace(10,95,18)
        
        #####################################################################
        #####################################################################
        
        # DEFINE AND CREATE folder STRUCTURE
        folder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
        strtime = time.strftime("%Y%m%d-%H%M%S")  
        datafolder = titlemod+strtime
        folder = folder + "\\" + datafolder + "\\"
        
        # CREATE INSTRUMENT OBJECTS
        SA = instruments.SpectrumAnalyzer(integrationTime)        
        CS = instruments.CurrentSupply()
        RC = instruments.RelayControl()
        
        # SAVE WAVELENGTH AXIS
        wlfilename = folder + "wavelengths.csv"
        SA.saveWavelengthData(wlfilename)
        
        # SET PRESETS FOR LASER DRIVER
        CS.setPresets()
        
        # EMITTER SELECTION LOOP
        for i in range(0,6):
            
            print("Testing emitter #: {}".format(6-i))
            
            # SET CURRENT TO 0
            CS.switchOff()
            
            # TURN ON SPECIFIC EMITTER 
            RC.turnOn(i)
            
            # Wait to turn on new emitter
            if(i != 0):
                print("Waiting {} seconds...".format(sleepT2))
                time.sleep(sleepT2)
            
            # DUTY CYCLE LOOP
            for dc in dutycycles:
                
                print("...Testing duty cycle: {}%".format(dc))
                
                
                
                # SET CURRENT CONTROLLER DUTY CYCLE
                CS.setDutyCycle(dc)
                
               
                
                # TURN CURRENT SUPPLY ON
                CS.switchOn()
                
                # GET RUNNING DATA
                print("......Laser State: {}".format(CS.getState()))
                print("......Laser Current: {}".format(CS.getCurrent()))
                # print("......ITC4005 Voltage: {}".format(CS.getVoltage()))
                # print("......ITC4005 Mode: {}".format(CS.getMode()))
                print("......Laser Duty Cycle: {}".format(CS.getDutyCycle()))
                
                
                # WAIT FOR STEADY STATE - TODO: FIND WAIT TIME
                time.sleep(sleepT)
                
                # MEASURE SPECTRUM
                SA.measureSpectrum()
                SA.plotSpectrum("Emitter: {}\nDuty Cycle: {}".format(6-i,dc))
                
                # SAVE SPECTRUM
                emittercorrection = 6 - i
                filename = "emitter-{}\\dc-{}.csv".format(emittercorrection,dc)
                filename = folder + filename
                SA.saveIntensityData(filename)
                
            # SET CURRENT TO 0
            CS.switchOff()
            
        # CALL DATA ANALYSIS PROGRAM
        print("Running data analysis.")
        dataanalysis.mainCall(datafolder)
        
        print("\nProgram finished!")
    except Exception as e:
        print(e)  
    
    finally:
        # CLOSE DEVICES
        SA.close()
        CS.close()
        
    return
        
        




if __name__ == "__main__":
    main()
    