# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 10:38:07 2022

@author: ryan.robinson
"""

import nidaqmx.system

from nidaqmx.constants import LineGrouping



def main():
    
    testDigitalWrite(val = True, port = 1)
    
    testAnalogRead()
    
    return


def testDigitalWrite(val = True, port = 0):
    
    with nidaqmx.Task() as task:
        device = '{}/port0/line0:5'.format('Dev1')
        task.do_channels.add_do_chan(device,line_grouping=LineGrouping.CHAN_PER_LINE)
        task.write([False,True,True,True,True,True])

    
    return


def testAnalogRead():
    
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        a = task.read()
    
    
    print(a)
    return




def listDevices():
    system = nidaqmx.system.System.local()
    system.driver_version
    
    for device in system.devices:
        print(device)
    
    return



if __name__ == "__main__":
    main()