#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-05-26

import time
import datetime,glob
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.


#Parametros Instalacion FV
from Parametros_FV import *

sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave") # captura los DS18B20

print (sensores)

import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = 24
NUM_OLED = 0
try:
    disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
    disp1.begin()
    NUM_OLED += 1
except:
    pass
if NUM_OLED == 1:
    try:
        disp2 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp2.begin()
        NUM_OLED += 1
        print ('OLED 3C y 3D')
    except:
        print ('OLED 3C')
        pass
else:
    try:
        disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp1.begin()
        NUM_OLED += 1
        print ('OLED 3D')
    except:
        pass
    
if NUM_OLED >= 1:
    disp1.clear()
    image = Image.open('/home/pi/PVControl+/pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp1.image(image)
    disp1.display()

    width = disp1.width
    height = disp1.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    font34 = ImageFont.truetype('/home/pi/PVControl+/Minecraftia-Regular.ttf', 34)
    font16 = ImageFont.truetype('/home/pi/PVControl+/Minecraftia-Regular.ttf', 16)
    font12 = ImageFont.truetype('/home/pi/PVControl+/Minecraftia-Regular.ttf', 12)
    font10 = ImageFont.truetype('/home/pi/PVControl+/Minecraftia-Regular.ttf', 10)
    font11 = ImageFont.truetype('/home/pi/PVControl+/SmallTypeWriting.ttf', 15)
    font6 = ImageFont.truetype('/home/pi/PVControl+/SmallTypeWriting.ttf', 10)

if NUM_OLED == 2:
    disp2.clear()
    image2 = Image.open('/home/pi/PVControl+/pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp2.image(image2)
    disp2.display()

bus = SMBus(1) # Bus I2C

###### Alta ADS1115 ADC (16-bit).
  #adc con pin addr a GND
  #A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
ad = 0x4b
adc = Adafruit_ADS1x15.ADS1115(address=ad, busnum=1)

  #adc con pin addr a 3V3
  #A0=Vbat // A1=Vflot o Diver // A2= Vplaca// A3= Mux
ad1 = 0x48
adc1 = Adafruit_ADS1x15.ADS1115(address=ad1, busnum=1) 

nb=1
values2 =[0]*6
while True:    
    try:
        print()
        print('*****************************************************************************')
        print ('--------- ADS 1 - 4 (mV)--------')
        print ('ADS en direccion=',ad1)
        ee = 10
        for n in range (4):
            values1 =[0]*6
            values1[0] = round(RES0 * 0.125/RES0_gain*adc1.read_adc(0,gain=RES0_gain),2) #valor en mV
            values1[1] = round(RES1 * 0.125/RES1_gain*adc1.read_adc(1,gain=RES1_gain),2)
            values1[2] = round(RES2 * 0.125/RES2_gain*adc1.read_adc(2,gain=RES2_gain),2)
            values1[3] = round(RES3 * 0.125/RES3_gain*adc1.read_adc(3,gain=RES3_gain),2)

            values1[4] = round(0.0078127*adc1.read_adc_difference(0,gain=16),2)
            values1[5] = round(0.0078127*adc1.read_adc_difference(3,gain=16),2)
            
            print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values1)) 
            
        ee = 20
        print()
        #print '--------- ADS 4 -(mV) -------'
        print ('ADS en direccion=',ad)
        for n in range (4):
            values =[0]*6
            for i in range(4):
                values[i]=round(0.125*adc.read_adc(i,gain=1),2) #valor en mV
                time.sleep(0.1)
            
            values[4]=round(0.0078125*adc.read_adc_difference(0,gain=16),2)
            values[5]=round(0.0078125*adc.read_adc_difference(3,gain=16),2)
            
            print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values)) 
        ee = 30
        print()
        print('################## Datos FV ##################')
        print ('Vbat=', round(values1[0]/1000,2),
               '  Ibat=', round(values[4]* SHUNT1,2),
               '  Iplaca=',round( values[5]* SHUNT2,2))
        print ('##############################################')
        
        
        # Valor Calibracion
        ee = 40
        print()
        print ('Calibracion')
        values3 =[0]*6
        for n in range (4):
            #print values[n],values1[n]
            values2[n]= values2[n]+round(values[n]/values1[n],5)
            values3[n]= round (values2[n]/nb,5)
        print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values3))

        # Valor en pin ADS
        values4 =[0]*6
        values4[0]= round(values1[0]/RES0,2)
        values4[1]= round(values1[1]/RES1,2)
        values4[2]= round(values1[2]/RES2,2)
        values4[3]= round(values1[3]/RES3,2)
        print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values4))

    except:
        print ('Error ADS1115', ee)

###### DS18B20 
    print ()
    print ('#######   Lectura sensores DS18B20 ######')
    for sensor in sensores:
        tfile = open(sensor)
        texto = tfile.read()
        tfile.close()
        temp_datos = texto.split("\n")[1].split(" ")[9]
        temp= round(float(temp_datos[2:]) / 1000,2)
        print (sensor,' Temperatura=', temp)
        time.sleep(1)
    print()

###### OLED
    print ('Numero de OLED detectadas =', NUM_OLED)
    try:   
        if NUM_OLED >= 1:
            ee=800
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.rectangle((0, 0, 127, 50), outline=255, fill=0)
            draw.rectangle((0, 0, 64, 50), outline=255, fill=0)
            ee=810
            draw.text ((10,2), 'ADS 1',font=font, fill=255)
            draw.text ((76,2), 'ADS 4',font=font, fill=255)
            for n in range (4):
                draw.text((6, 10+9*n),  'A'+str(n)+'='+str(round(values1[n]/1000,3)), font=font, fill=255)
                draw.text((70, 10+9*n),  'A'+str(n)+'='+str(round(values[n]/1000,3)), font=font, fill=255)
            
            draw.text ((10,52), 'Temp='+str(temp),font=font, fill=255)
            ee=820
            disp1.clear()
            ee=830
            disp1.image(image)
            disp1.display()
            
        if NUM_OLED == 2:
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            for n in range (4):
                draw.text((6, 20+10*n),  'RES'+str(n)+'='+str(round(values3[n],5)), font=font, fill=255)
            disp2.clear()
            disp2.image(image)
            disp2.display()
    except:
        print ('Error OLED',ee)
        
    time.sleep(2)
    nb += 1
