# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 11:51:49 2022

@author: ryan.robinson
"""

# FOR THORLABS ITC4005 LASER DIODE DRIVER
import pyvisa

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

