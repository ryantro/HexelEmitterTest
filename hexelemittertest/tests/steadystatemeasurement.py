# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 10:56:06 2022

@author: ryan.robinson
"""

import sys
sys.path.append('../')
import instruments

import time, os

def main():
    try:
        # DEFINE AND CREATE folder STRUCTURE
        folder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
        strtime = time.strftime("steady-state-test-%Y%m%d-%H%M%S")
        folder = folder + "\\" + strtime + "\\"
        
        # CREATE INSTRUMENT OBJECTS
        SA = instruments.SpectrumAnalyzer()        
        CS = instruments.CurrentSupply()
        RC = instruments.RelayControl()
        
        # SAVE WAVELENGTH AXIS
        wlfilename = folder + "wavelengths.csv"
        SA.saveWavelengthData(wlfilename)
        
        # PARAMETERS        
        dc = 20
        sleepT = 1 # second
        emitter = 0

        print("Testing emitter #: {}".format(emitter))
        
        # SET CURRENT TO 0
        CS.switchOff()
        
        CS.setDutyCycle(dc)
        
        i = 0
        # TURN ON SPECIFIC EMITTER 
        RC.turnOn(i)
        
        # TURN CURRENT SUPPLY ON
        CS.switchOn()
        CS.setPresets()
        
        starttime = time.time()
        mnum = 20
        # DUTY CYCLE LOOP
        for j in range(0,mnum):
            
            print("...Measurement {} of {}.".format(j,mnum-1))
            
            # WAIT FOR STEADY STATE - TODO: FIND WAIT TIME
            time.sleep(sleepT)
            
            t = time.time() - starttime
            print("Time: {}".format(t))
            
            # MEASURE SPECTRUM
            SA.measureSpectrum()
            
            # SAVE SPECTRUM
            filename = "{}.csv".format(t)
            filename = folder + filename
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