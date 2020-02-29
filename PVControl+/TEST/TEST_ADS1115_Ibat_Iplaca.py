#!/usr/bin/python
# -*- coding: utf-8 -*-

import time 
import RPi.GPIO as GPIO
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

bus = SMBus(1) #Rpi rev.B
GPIO.setmode(GPIO.BOARD)

# ------------------------------------------
######      PARAMETROS INSTALACION 
# ------------------------------------------
SHUNT1 = 100.0/75 #Shunt Ibat
SHUNT2 = 100.0/75 #Shunt Iplaca


###### Alta ADS1115 ADC (16-bit).

  #adc con pin addr a 3V3
adc1 = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1) 

#################################################################
########     Bucle para ver Ibat, Iplaca #######
#################################################################
hora1=time.time()
iplaca=0
while True:
    print (time.time() - hora1)
    hora1=time.time()
    try:
            
        ibat_s = -0.0078127*adc1.read_adc_difference(0, gain=16, data_rate=8)
        iplaca_s = -0.0078127*adc1.read_adc_difference(3, gain=16, data_rate=8)
                        
        ibat_s=round(ibat_s,5)
        ibat=round(ibat_s*SHUNT1,2)
        
        #iplaca_s=round(iplaca_s,5)
        #iplaca=round(iplaca_s*SHUNT2,2)
        
        print ('ibat=', ibat, ' / iplaca=',iplaca)
       
    except:
        print ('Error ADS1115')

    time.sleep(0.01)

