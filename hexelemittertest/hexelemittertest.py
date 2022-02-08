# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:46:44 2022

@author: ryan.robinson
"""


import instruments
import time, os, sys
import matplotlib.pyplot

def main():
    try:
        # Edit this to change folder name
        titlemod = "Hexel1002570-Broken Emiiter 6-Long Sleep Time-"
        
        # Set Ocean Optics HR4000 integration time in micro seconds
        integrationTime = 40000
        
        # Sleep Time - Set time to reach steady state in seconds
        sleepT = 20 # second        
        
        # DUTY CYCLES TO MEASURE
        dutycycles = [10, 20, 40, 50, 60, 80, 90, 99]
        
        #####################################################################
        #####################################################################
        
        # DEFINE AND CREATE folder STRUCTURE
        folder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
        strtime = time.strftime("%Y%m%d-%H%M%S")        
        folder = folder + "\\" + titlemod+strtime + "\\"
        
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
            
            # DUTY CYCLE LOOP
            for dc in dutycycles:
                
                print("...Testing duty cycle: {}%".format(dc))
                
                
                
                # SET CURRENT CONTROLLER DUTY CYCLE
                CS.setDutyCycle(dc)
                
               
                
                # TURN CURRENT SUPPLY ON
                CS.switchOn()
                
                # GET RUNNING DATA
                print("......ITC4005 State: {}".format(CS.getState()))
                print("......ITC4005 Current: {}".format(CS.getCurrent()))
                print("......ITC4005 Mode: {}".format(CS.getMode()))
                print("......ITC4005 Duty Cycle: {}".format(CS.getDutyCycle()))
                
                
                # WAIT FOR STEADY STATE - TODO: FIND WAIT TIME
                time.sleep(sleepT)
                
                # MEASURE SPECTRUM
                SA.measureSpectrum()
                SA.plotSpectrum("Duty Cylce: {}\nEmitter: {}".format(dc,6-i))
                
                # SAVE SPECTRUM
                emittercorrection = 6 - i
                filename = "emitter-{}\\dc-{}.csv".format(emittercorrection,dc)
                filename = folder + filename
                SA.saveIntensityData(filename)
                
            # SET CURRENT TO 0
            CS.switchOff()
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
    