#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-07-16

import time
import datetime,glob
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.


#Parametros Instalacion FV
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave") # captura los DS18B20
print()
print (Style.BRIGHT + Fore.GREEN + 'Arrancando'+ Fore.GREEN +Back.BLACK+' TEST PCB PVControl') #+Style.RESET_ALL)

print (Fore.BLUE,'Sensores DS18B20 detectados')
print('    ',sensores)
print()
print(' Pantallas OLED detectadas')

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
        print ('   OLED 3C y 3D')
    except:
        print ('   OLED 3C')
        pass
else:
    try:
        disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp1.begin()
        NUM_OLED += 1
        print ('   OLED 3D')
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

  #A0=Vbat // A1=Vflot o Diver // A2= Vplaca// A3= Mux
ads1 = 0x48
adc1 = Adafruit_ADS1x15.ADS1115(address=ads1, busnum=1) 

ads2 = 0x49
adc2 = Adafruit_ADS1x15.ADS1115(address=ads2, busnum=1) 

ads3 = 0x4a
adc3 = Adafruit_ADS1x15.ADS1115(address=ads3, busnum=1) 

  #A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
ads4 = 0x4b
adc4 = Adafruit_ADS1x15.ADS1115(address=ads4, busnum=1)

nb=1
values20 =[0]*6
while True:    

    try:#### ADS
        print(Fore.YELLOW,'*****************************************************************************')
        print (Fore.GREEN,'--------- ADS 1 (mV) en direccion=',ads1)
        ee = 10
        for n in range (4):
            values1 =[0]*6
            values1[0] = round(RES0 * 0.125/RES0_gain*adc1.read_adc(0,gain=RES0_gain),2) #valor en mV
            values1[1] = round(RES1 * 0.125/RES1_gain*adc1.read_adc(1,gain=RES1_gain),2)
            values1[2] = round(RES2 * 0.125/RES2_gain*adc1.read_adc(2,gain=RES2_gain),2)
            values1[3] = round(RES3 * 0.125/RES3_gain*adc1.read_adc(3,gain=RES3_gain),2)

            values1[4] = round(0.0078127*adc1.read_adc_difference(0,gain=16),2)
            values1[5] = round(0.0078127*adc1.read_adc_difference(3,gain=16),2)
            
            print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values1)) 
        
        try:    
            ee = 20
            print (Fore.GREEN,'--------- ADS 2 (mV) en direccion=',ads2)
            for n in range (4):
                values2 =[0]*6
                for i in range(4):
                    values2[i]=round(0.125*adc2.read_adc(i,gain=1),2) #valor en mV
                    time.sleep(0.1)
                
                values2[4]=round(0.0078125*adc2.read_adc_difference(0,gain=16),2)
                values2[5]=round(0.0078125*adc2.read_adc_difference(3,gain=16),2)
                
                print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values2)) 
        except:
            print (Fore.RED, ' NO detectado')
        
        try:    
            ee = 30
            print (Fore.GREEN,'--------- ADS 3 (mV) en direccion=',ads3)
            for n in range (4):
                values3 =[0]*6
                for i in range(4):
                    values3[i]=round(0.125*adc3.read_adc(i,gain=1),2) #valor en mV
                    time.sleep(0.1)
                
                values3[4]=round(0.0078125*adc3.read_adc_difference(0,gain=16),2)
                values3[5]=round(0.0078125*adc3.read_adc_difference(3,gain=16),2)
                
                print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values3)) 
        except:
            print (Fore.RED, ' NO detectado')
                     
        ee = 40
        #print '--------- ADS 4 -(mV) -------'
        print (Fore.GREEN,'--------- ADS 4 (mV) en direccion=',ads4)
        for n in range (4):
            values4 =[0]*6

            print ('| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values1)) 
            
            for i in range(4):
                values4[i]=round(0.125*adc4.read_adc(i,gain=1),2) #valor en mV
                time.sleep(0.1)
            
            values4[4]=round(0.0078125*adc4.read_adc_difference(0,gain=16),2)
            values4[5]=round(0.0078125*adc4.read_adc_difference(3,gain=16),2)
            
            print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values4)) 
        
        ee = 50
        print()
        print(Fore.GREEN,'################## Datos FV ##################',Fore.WHITE)
        print (' Vbat=', round(values1[0]/1000,2),
               '  Ibat=', round(values4[4]* SHUNT1,2),
               '  Iplaca=',round( values4[5]* SHUNT2,2))
        print (Fore.GREEN,'##############################################')
        
        
        # Valor Calibracion ADS
        ee = 70
        print()
        print (Fore.GREEN,' Calibracion ADS')
        values30 =[0]*6
        for n in range (4):
            #print values[n],values1[n]
            values20[n]= values20[n]+round(values4[n]/values1[n],5)
            values30[n]= round (values20[n]/nb,5)
        print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values30))

        ee=100
        # Valor en pin ADS

        values10 =[0]*6
        values10[0]= round(values1[0]/RES0,2)
        values10[1]= round(values1[1]/RES1,2)
        values10[2]= round(values1[2]/RES2,2)
        values10[3]= round(values1[3]/RES3,2)
        print (Fore.WHITE,'| {0:>7} | {1:>7} | {2:>7} | {3:>7} | {4:>7} | {5:>7} |'.format(*values10))
        
    except:
        print (Fore.RED,'Error TEST', ee)

###### DS18B20 
    print ()
    print (Fore.GREEN,'#######   Lectura sensores DS18B20 ######')
    for sensor in sensores:
        tfile = open(sensor)
        texto = tfile.read()
        tfile.close()
        temp_datos = texto.split("\n")[1].split(" ")[9]
        temp= round(float(temp_datos[2:]) / 1000,2)
        print (Fore.WHITE,sensor,Fore.YELLOW,' Temperatura=',temp)
        time.sleep(1)

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
                draw.text((70, 10+9*n),  'A'+str(n)+'='+str(round(values4[n]/1000,3)), font=font, fill=255)
            
            draw.text ((10,52), 'Temp='+str(temp),font=font, fill=255)
            ee=820
            disp1.clear()
            ee=830
            disp1.image(image)
            disp1.display()
            ee=840
        if NUM_OLED == 2:
            ee=850
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            for n in range (4):
                draw.text((6, 20+10*n),  'RES'+str(n)+'='+str(round(values30[n],5)), font=font, fill=255)
            disp2.clear()
            disp2.image(image)
            ee=880
            disp2.display()
    except:
        print (Fore.RED,'Error OLED',ee)

    ee = 60
    # Reles 33X I2C
    print()
    for r in (33,34):
        print (Fore.GREEN,' ##### RELES',r,'X #####',Fore.WHITE,)
        try:
            for puerto in range (8): # Rele I2C
                print ('   PCF=',r,'-',bin(bus.read_byte(r)),end='')  #devuelve el valor en decimal
                salida =(2**puerto ^ (255))
                print (' -- act_rele=',r,puerto, 'Byte=',bin(salida), end='')
                bus.write_byte(r,salida)
                
                print ('- PCF=',bin(bus.read_byte(r)))  #devuelve el valor en decimal
                time.sleep(2)
            
            print (Fore.WHITE,'  Activo Reles alternos..... 10101010', end='')
            bus.write_byte(r,170)
            time.sleep(2)
            print (Fore.WHITE,'   -   ..... 01010101')
            bus.write_byte(r,85)
            time.sleep(2)
            estado = bus.read_byte(r)  #devuelve el valor en decimal
            if estado == 85 :
                print (Fore.YELLOW,'  PCF ',r,'X OK')
            else :
                print (Fore.RED,'  PCF ',r,'X MAL')
                
            print (Fore.WHITE,'  Apago Rele..... 00000000')
            bus.write_byte(r,255) # apago
        
        except:
            print (Fore.RED,'  PCF ',r,'X ERROR')
        

    time.sleep(2)
    nb += 1
    print (Fore.WHITE, Back.GREEN)
    input("Press Enter to continue..."+Back.BLACK)
