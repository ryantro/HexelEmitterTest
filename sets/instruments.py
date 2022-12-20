# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 11:51:49 2022

@author: ryan.robinson
"""

import numpy, os
import matplotlib.pyplot as plt
import time

# FOR DAQ
import nidaqmx.system
from nidaqmx.constants import LineGrouping


# FOR OCEAN OPTICS HR4000
from seabreeze.spectrometers import Spectrometer

# FOR THORLABS ITC4005 LASER DIODE DRIVER
import pyvisa

# CONTROLS THE OCEAN OPTICS HR4000 OSA
# REQUIRES SEABREEZE TO BE INSTALLED
class SpectrumAnalyzer():
    def __init__(self, integration_time = 2000, serialnum = "HR4D1482"):
        """
        Connect to Ocean Optics HR4000.
        Generate wavelength axis.

        Returns
        -------
        None.

        """
        
        
        # SET OSA INTEGRATION TIME
        self.integration_time = integration_time
        
        # SET OSA DEVICE
        # SERIAL NUMBER: HR4D1482
        self.spec = Spectrometer.from_serial_number(serialnum)
        
        self.spec.integration_time_micros(self.integration_time)
        
        # GET WAVELENGTH X AXIS
        self.wavelengths = self.spec.wavelengths()
        
        return
    
    def close(self):
        """
        Close the device.

        Returns
        -------
        None.

        """
        
        self.spec.close()
        
        return
    
    
    def measureSpectrum(self):
        """
        Measure data from the OSA.

        Returns
        -------
        None.

        """
        # READ INTENSITIES
        self.intensities = self.spec.intensities()
        
        return
    
    def getData(self):
        """
        Get the data in the buffer.

        Returns
        -------
        numpy array
            wavelength data.
        numpy array
            intensity data.

        """
        return self.wavelengths, self.intensities
    
    def plotSpectrum(self,title = ""):
        plt.plot(self.wavelengths,self.intensities)
        plt.xlim([435,455])
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")
        plt.grid("On")
        plt.title(title)
        plt.pause(0.05)
        return
    
    def saveWavelengthData(self, filename):
        """
        Save the wavelength data to a csv.

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Create directories for file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save data
        numpy.savetxt(filename, self.wavelengths, delimiter = ",")
        
        return
    
    def saveIntensityData(self, filename):
        """
        Save the intensity data to a csv

        Parameters
        ----------
        filename : str
            filename and foulders to save data in.

        Returns
        -------
        None.

        """
        # Create directories for file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Generate save data
        savedata = numpy.column_stack((self.wavelengths,self.intensities))
        
        # Save data
        numpy.savetxt(filename, savedata, delimiter = ",")
        
        return

# CONTROLS THE THORLABS ITC4005    
class CurrentSupply():
    def __init__(self, usbaddr = "USB::4883::32842::M00466376"):
        """
        Connects to the current supply device.

        Returns
        -------
        None.

        """
        usbaddr = "USB::4883::32842::M00466376"
        
        self.itc = USBDevice(usbaddr)
        
        return
    
    def protectionQuery(self):
        """
        Tests if any protection queries are tripped.

        Returns
        -------
        test : int
            returns a value of 1 if a protection query is tripped.

        """
        vQ = "OUTPut:PROTection:VOLTage:TRIPped?"
        eQ = "OUTPut:PROTection:EXTernal:TRIPped?"
        # wQ = "OUTPut:PROTection:INTernal:TRIPped?" # Not used
        iQ = "OUTPut:PROTection:INTLock:TRIPped?"
        kQ = "OUTPut:PROTection:KEYLock:TRIPped?"
        tQ = "OUTPut:PROTection:OTEMp:TRIPped?"
        
        listQ = [vQ, eQ, iQ, kQ, tQ]
        
        test = 0
        for Q in listQ:
            response = self.itc.send(Q)
            if(response == "1"):
                print("Unable to start laser driver:\n"+Q+"\nreturned 1.")
                test = 1
        
        return test
    
    def setPresets(self, current = 2.8):
        """
        Sets the defaults for the ITC4005 current driver.

        Returns
        -------
        None.

        """
        
        # Laser Driver Settings
        limitSet    = "SOURce:CURRent:LIMit {}".format(3.5) # Set current limit
        currentSet  = "SOURce:CURRent {}".format(current)       # Set current
        periodSet   = "SOURce:PULse:PERiod {}".format(0.002) # Set pulse period
        modeSet     = "SOURce:FUNCtion:MODE CURRent"        # Set mode to current
        shapeSet    = "SOURce:FUNCtion:SHAPe PULSE"         # Set to pulsed
        modSet      = "SOURce:AM 0"                         # Turn modulation off
        
        # Send all preset commands relating to the laser driver
        commands = [limitSet, currentSet, periodSet, modeSet, shapeSet, modSet]
        for command in commands:
            self.itc.write(command)
        
        return
    
    def setCurrent(self, curr):
        """
        Set the current output.

        Parameters
        ----------
        curr : float
            current setting in Amphere.

        Returns
        -------
        None.

        """
        command = "SOURce:CURRent {}".format(curr)
        
        self.itc.write(command)
        
        return
    
    def getVoltage(self):
        command = "MEAS:VOLT?"
        return self.itc.send(command)
    
    def getCurrent(self):
        """
        Reads out the current.

        Returns
        -------
        str
            current setting in Amphere.

        """
        command = "SOURce:CURRent?"
        
        return self.itc.send(command)
    
    def setDutyCycle(self, dutyCycle):
        """
        Set duty cycle in terms of percent, 0 to 100.

        Parameters
        ----------
        duty : int
            percentage duty cycle.

        Returns
        -------
        None.

        """
        if(dutyCycle == 100):
            self.setCW()
        else:
            self.setPulsed()
            command = "SOURce:PULSe:DCYCle {}".format(dutyCycle)
            self.itc.write(command)
        
        return
    
    def getState(self):
        command = ":OUTPut:STATe?"
        return self.itc.send(command)
    
    def switchOn(self):
        """
        Switches the laser diode on.

        Returns
        -------
        None.

        """
        command = ":OUTPut:STATe ON"
    
        self.itc.write(command)    
    
        return
    
    def switchOff(self):
        """
        Switches the laser diode off.

        Returns
        -------
        None.

        """
        command = ":OUTPut:STATe OFF"
        
        self.itc.write(command) 
        
        return
    
    def setPulsePeriod(self, period):
        """
        Sets the pulse period in microseconds.

        Parameters
        ----------
        period : float
            pulse period in microseconds.

        Returns
        -------
        None.

        """
        command = "SOURce:PULse:PERiod {}".format(period)
        
        self.itc.write(command)
        
        return
    
    def setCW(self):
        """
        Switches mode to CW operation.

        Returns
        -------
        None.

        """
        command = "SOURce:FUNC:MODE CURR;SHAP DC"
        
        self.itc.write(command)
        
        return
    
    def setPulsed(self):
        """
        Switches mode to pulsed operation.

        Returns
        -------
        None.

        """
        
        command = "SOURce:FUNCtion:SHAPe PULSE"
        
        self.itc.write(command)
        
        return
    
    def getMode(self):
        """
        Switches mode to pulsed operation.

        Returns
        -------
        None.

        """
        
        command = "SOURce:FUNCtion:SHAPe?"
        
        return self.itc.send(command)
    
    def getDutyCycle(self):
        
        return self.itc.send("SOURce:PULSe:DCYCle?")
    
    def close(self):
        """
        Closes the device.

        Returns
        -------
        None.

        """
        try:
            # SHUT OFF CURRENT OUTPUT
            self.switchOff()
        finally:
            # CLOSE THE DEVICE
            self.itc.close()
        
        return

# GENERIC USB DEVICE CLASS
# USED TO COMMUNICATE WITH THE THORLABS ITC40005    
class USBDevice:
    def __init__(self,rname):
        self.inst = pyvisa.ResourceManager().open_resource(rname)
        return None
    
    def settimeout(self,timeout):
        """
        Sets the timeout.

        Parameters
        ----------
        timeout : int
            time before an exception is thrown.

        Returns
        -------
        None.

        """
        self.inst.timeout = timeout+1000
        
        return
    
    def write(self,command):
        """
        Sends a command that requires no response. 

        Parameters
        ----------
        command : str
            command string.

        Returns
        -------
        None.

        """
        self.inst.write(command)
        
        return
    
    def send(self,command):
        """
        Sends a command that gives a response.

        Parameters
        ----------
        command : str
            command string.

        Returns
        -------
        str
            command response.

        """
        return self.inst.query(command).strip('\r\n')
    
    def close(self):
        """
        Closes the device.

        Returns
        -------
        None.

        """
        self.inst.close()
        
        return
    
# Controls for a NI USB-6001 DAQ
# May have to edit Dev1 depending on how PC recognizes device
class RelayControl():
    
    def __init__(self,device = "Dev1"):
        """
        Initialize device.
        Can use NI Max to find the 'device' name.

        Parameters
        ----------
        device : TYPE, optional
            DESCRIPTION. Device name.

        Returns
        -------
        None.

        """
        self.target = '{}/port0/line0:5'.format(device)
        
        # Initialize all relays to be on, shorts across all emitters
        self.relays = [True, True, True, True, True, True]
        
        # Setup Daq
        self.sendToDaq()
        
        return
    
    def turnOn(self,num):
        """
        Turns on the specified emitter by switching off the respective relay
        and turning on all other relays.

        Parameters
        ----------
        num : TYPE
            DESCRIPTION. Can be any value from 0 to 5, specifies the emitter.

        Returns
        -------
        None.

        """
        # Check if a valid emitter num is entered
        if(num > 5):
            print("Invalid emitter specified")
        
        # Turn on the specified emitter
        else:
            self.relays = [True, True, True, True, True, True]
            self.relays[num] = False
            self.sendToDaq()
            
        return
    
    def sendToDaq(self):
        """
        Sends the command to the DAQ

        Returns
        -------
        None.

        """
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(self.target, line_grouping=LineGrouping.CHAN_PER_LINE)
            task.write(self.relays)
            
        return
    