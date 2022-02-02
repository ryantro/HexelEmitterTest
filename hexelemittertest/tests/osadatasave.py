# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:46:44 2022

@author: ryan.robinson
"""


import instruments
import time, os, sys

def main():
    try:
        foulder = r'N:\SOFTWARE\Python\hexelemittertest\hexelemittertest\testdata'
        strtime = time.strftime("%Y%m%d-%H%M%S")
        
        foulder = foulder + "\\" + strtime
        os.mkdir(foulder)
        
        SA = instruments.SpectrumAnalyzer()
        CS = instruments.CurrentSupply()
        #RC = instruments.RelayControl()
        
     
        
        # PLACE HOLDERS
        dutycycles = [0, 1, 2, 3]
        current = "3A"
        zeroCurr = "0A"
        sleepT = 1 # second
        
    
        
        # Emitter selection loop
        for i in range(0,6):
            
            # Turn current off before switching emitters
            CS.setZero()
            # Turn on specific emitter
            #RC.turnOn(i)
            
            for dc in dutycycles:
                
                # Switch current on
                CS.setCurrent(current)
                
                # Set duty cycle
                CS.setDutyCycle(dc)
                
                # Wait for steady state
                time.sleep(sleepT)
                
                # Measure Spectrum
                SA.measureSpectrum()
                
                # Create foulder/filename
                filename = "emitter{}-dc{}.csv".format(i,dc)
                
                filename = foulder + "\\" + filename
                
                # Save spectrum
                
                SA.saveIntensityData(filename)
                
            # Turn current off
            CS.setZero()
    
    except Exception as e:
        print(e)  
    
    finally:
        SA.close()
        
        
    return
        
        




if __name__ == "__main__":
    main()
    