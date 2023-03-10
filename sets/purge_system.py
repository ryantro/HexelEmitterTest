# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 13:47:05 2023

@author: ryan.robinson
"""
import serial

class MuController():

    def __init__(self):
        self.ser = serial.Serial("COM8", 9600)
        return
        # try:
        #     self.ser = serial.Serial("COM5", 9600)
        #     self.ser.isOpen()
        #     time.sleep(2)
        #     self.ser.flush()
        #
        # except IOError:
        #     pass
        #
        # while True:
        #     text = self.ser.readline().decode()
        #     data = text.split()
        #     self.value = data[0]
        #     self.value2 = data[1]
        #     self.ser.flushInput()
        #     # print(self.value2)
        #     time.sleep(0.5)


    def purge(self):
        """
        SENDS BYTE FOR ARDUINO TO INITIALIZE THE PURGING PROCESS
        """
        self.ser.write(b'3')

        return
    