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
RES= (68+1.5)/1.5 # Divisor tension Vbat --Suma REAL de las Resistencias en Ks 
RES_gain=1

#Vbat
RES0 = (68+1.5)/1.5 * 12.63/12.33     # Divisor tension Vbat
RES0_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#Vaux
RES1 = (68+1.5)/1.5 * 12/12     # Divisor tension Vaux
RES1_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#Vplaca
RES2 = (68+1.5)/1.5 * 48/48     # Divisor tension Vplaca
RES2_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#V...
RES3 = (68+1.5)/1.5 * 48/48     # Divisor tension ....
RES3_gain = 2                   # Fondo escala 1=4,096 - 2=2.048

###### Alta ADS1115 ADC (16-bit).
  #adc con pin addr a GND
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

  #adc con pin addr a 3V3
adc1 = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1) 

#################################################################
######## Bucle para ajustar Parametros vbat, Ibat, Iplaca #######
#################################################################
MODO=1

if MODO==0:
    print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*range(6)))
    print ('-' * 57)
    while True:
        #adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
        #adc1 = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1) 
    
        try:
            """
            print ('--------- ADS 1 (mV)--------')
            for n in range (5):
                values =[0]*6
                for i in range(4):
                    values[i]=round(0.125/RES_gain*adc.read_adc(i,gain=RES_gain),2) #valor en mV
                values[4]=round(0.0078127*adc.read_adc_difference(0,gain=16),2)
                values[5]=round(0.0078127*adc.read_adc_difference(3,gain=16),2)
                
                print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values))    

            print ('--------- ADS 4 -(mV) -------')
            """
            for n in range (5):
                values =[0]*6
                for i in range(4):
                    values[i]=round(0.125/RES_gain*adc1.read_adc(i,gain=RES_gain,data_rate=8),2) #valor en mV
                    time.sleep(0.3)
                #values[4]=round(0.0078127*adc1.read_adc_difference(0,gain=16),2)
                #values[5]=round(0.0078127*adc1.read_adc_difference(3,gain=16),2)
                
                print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values)) 
            print
            
            
        except:
            print ('Error ADS1115')

        time.sleep(2)
else:

    while True:
        try:
            vbat_s = 0.000125*adc.read_adc(0, gain=1)
            vplaca_s = 0.000125*adc.read_adc(2, gain=1)
                
            ibat_s = -0.0078127*adc1.read_adc_difference(0, gain=16, data_rate=8)
            iplaca_s = -0.0078127*adc1.read_adc_difference(3, gain=16, data_rate=8)
                            
            vbat_s=round(vbat_s,5)
            vbat=round(vbat_s*RES0,2)

            vplaca_s=round(vplaca_s,5)
            vplaca=round(vplaca_s*RES2,2)

            ibat_s=round(ibat_s,5)
            ibat=round(ibat_s*SHUNT1,2)
            
            iplaca_s=round(iplaca_s,5)
            iplaca=round(iplaca_s*SHUNT2,2)
            
            #print ('vbat_s=',vbat_s,' / ibat_s=', ibat_s, ' / iplaca_s=',iplaca_s)
            print ('vbat=',vbat,' / vplaca=', vplaca,' / ibat=', ibat, ' / iplaca=',iplaca)
           
        except:
            print ('Error ADS1115')

        time.sleep(2)

