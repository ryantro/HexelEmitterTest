# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:46:44 2022

@author: ryan.robinson
"""


import instruments
import time, os, sys

def main():
    try:
        # DEFINE AND CREATE FOULDER STRUCTURE
        foulder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
        strtime = time.strftime("%Y%m%d-%H%M%S")
        foulder = foulder + "\\" + strtime + "\\"
        
        # CREATE INSTRUMENT OBJECTS
        SA = instruments.SpectrumAnalyzer()        
        CS = instruments.CurrentSupply()
        RC = instruments.RelayControl()
        
        # SAVE WAVELENGTH AXIS
        wlfilename = foulder + "wavelengths.csv"
        SA.saveWavelengthData(wlfilename)
        
        # PARAMETERS
        dutycycles = [20, 40, 50, 60, 80, 100]
        current = "2.8" # Amphere
        sleepT = 1 # second
        
        # EMITTER SELECTION LOOP
        for i in range(0,6):
            
            print("Testing emitter #: {}".format(i))
            
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
                
                # WAIT FOR STEADY STATE - TODO: FIND WAIT TIME
                time.sleep(sleepT)
                
                # MEASURE SPECTRUM
                SA.measureSpectrum()
                
                # SAVE SPECTRUM
                filename = "emitter-{}\\dc-{}.csv".format(i,dc)
                filename = foulder + filename
                SA.saveIntensityData(filename)
                
            # SET CURRENT TO 0
            CS.switchOff()
    
    except Exception as e:
        print(e)  
    
    finally:
        # CLOSE DEVICES
        SA.close()
        CS.close()
        
    return
        
        




if __name__ == "__main__":
    main()
    