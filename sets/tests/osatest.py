# -*- coding: utf-8 -*-
"""
Spyder Editor

Test osa functionality

Ocean Optics HR4000

Uses the seabreeze package to communicate

IMPORTANT NOTE:
    
    MUST HAVE THE WINUSB DRIVERS FOR THE HR4000 INSTALLED!!!
    NI DRIVERS WILL NOT WORK WITH SEABREEZE
"""

#import pyvisa
from seabreeze.spectrometers import Spectrometer, list_devices

import matplotlib.pyplot as plt


def main():
    
    # GET A LIST OF ALL THE OCEAN OPTICS SPECTRUM DEVICES
    devices = list_devices()
    
    # PRINT A LIST OF ALL THE DEVICES
    print(devices)
    
    it = 200000 # integration time in microseconds
    
    
    print("test1")
    # CONNECT TO THE FIRST OCEAN OPTICS DEVICE IT SEES (MAY CAUSE ISSUES)
    # spec = Spectrometer.from_first_available()
    
    serialnum = "HR4D1482"
    
    spec = Spectrometer.from_serial_number(serialnum)
    
    
    spec.integration_time_micros(it)
    
    print(spec.serial_number)
    
    x = spec.wavelengths()
    y = spec.intensities()
    
    
    plt.figure(1)
    plt.plot(x,y)
    plt.xlabel("wavelength (nm)")
    plt.ylabel("Intensity")
    plt.title("Spectrum Plot")
    
    print("test2")
    #spec.integration_time_micros(10)
    #x = spec.wavelengths()
    y2 = spec.intensities()
    
    plt.figure(2)
    plt.plot(x,y2-y)
    plt.xlabel("wavelength (nm)")
    plt.ylabel("Intensity")
    plt.title("Spectrum Plot")
    
    spec.close()
    
    return




if __name__ == "__main__":
    main()