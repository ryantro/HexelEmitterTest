# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:46:44 2022

@author: ryan.robinson
"""


import instruments
import time, os, sys

def main():
    try:

        
 
        RC = instruments.RelayControl()
        # TURN ON SPECIFIC EMITTER 
        RC.turnOn(5)
          
    
    except Exception as e:
        print(e)  
    
    finally:
        print("done")
        
    return
        
        




if __name__ == "__main__":
    main()
    