#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-04-02

import time,csv,sys, subprocess
import traceback
import datetime,glob
import pickle

basepath = '/home/pi/PVControl+/'
DEBUG = False #True

print ('Arrancando_PVControl+- OLED')

#Parametros Instalacion FV
from Parametros_FV import *

#Pantalla OLED
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = 24 #parametro OLED

# Comprobacion numero de OLED instaladas
NUM_OLED = 0
try:
    disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
    disp1.begin()
    NUM_OLED += 1
    #print('OLED 3C')
except:
    print('No esta la OLED 3C')
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

if NUM_OLED == 0:
    print (subprocess.getoutput('sudo systemctl stop fv_oled'))
    sys.exit()

if NUM_OLED >= 1:
    disp1.clear()
    image = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp1.image(image)
    disp1.display()

    width = disp1.width
    height = disp1.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    font34 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 34)
    font16 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 16)
    font12 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 12)
    font10 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 10)
    font11 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 15)
    font6 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 10)

    OLED_contador1=0 # contador del pantallazo que presenta en secuencial
    OLED_salida_opcion1 = -1 # para elegir entre salida fija o secuencial
                            # se controla por MQTT con PVControl/Oled
                            # -1= secuencial....0,1,2,3... fija la pantalla marcada
if NUM_OLED == 2:
    disp2.clear()
    image2 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp2.image(image2)
    disp2.display()
    OLED_contador2 = 0 # contador del pantallazo que presenta en secuencial
    OLED_salida_opcion2 = -1

#
def OLED(pantalla,modo):

    draw.rectangle((0,0,width,height), outline=0, fill=0)

    if modo == 0:
        #image1 = Image.open('pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
        image1 = Image.open(basepath+'pvcontrol_128_64.png').convert('1')
        if pantalla == 1:
            disp1.image(image1)
            disp1.display()
        else:
            disp2.image(image1)
            disp2.display()

    elif modo == 1:
        draw.rectangle((0, 0, 127, 20), outline=255, fill=0)
        draw.text((8, 0), 'SOC='+str(SOC)+'%', font=font16, fill=255)
        draw.rectangle((0, 20, 64, 46), outline=255, fill=0)
        draw.rectangle((64, 20, 127, 46), outline=255, fill=0)
        draw.text((4, 22),  'Vbat='+str(Vbat), font=font, fill=255)
        draw.text((69, 22), 'Ibat='+str(Ibat), font=font, fill=255)
        draw.text((4, 34),  'Vpla='+str(Vplaca), font=font, fill=255)
        draw.text((69, 34), 'Ipla='+str(Iplaca), font=font, fill=255)

        L4 = 'R('
        """
        for I in range(nreles): # Reles wifi
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0]-Puerto) / 10)
            if int(addr/10) == 2:
                valor = int(TR[I][3] / 10)
                if valor == 10:
                    texto ='X'
                else:
                    texto=str(valor)
                L4=L4+texto
        L4 = L4 + ')('
        for I in range(nreles): # Reles i2C
            Puerto = (TR[I][0] % 10) - 1
            addr=int((TR[I][0] - Puerto) / 10)
            if int(addr/10) == 3:
                valor = int(TR[I][3] / 10)
                if valor == 10:
                    texto ='X'
                else:
                    texto = str(valor)
                L4 = L4 + texto
        L4 = L4 + ')'
        """
        draw.text((2, 49), L4, font=font11, fill=255)

    elif modo == 2:
        draw.rectangle((0, 0, 90, 31), outline=255, fill=0)
        draw.text((8, 1), 'Vbat='+str(Vbat), font=font11, fill=255)
        draw.text((8, 14), 'Ibat='+str(round(Ibat,0)), font=font11, fill=255)
        draw.rectangle((0, 31, 90, 63), outline=255, fill=0)     
        draw.text((8, 31), 'Vpla='+str(round(Vplaca,1)), font=font11, fill=255)
        draw.text((8, 45), 'Ipla='+str(round(Iplaca,0)), font=font11, fill=255)

        draw.rectangle((90, 0, 127, 20), outline=255, fill=255)     
        draw.text((100, 0), 'SOC', font=font, fill=0)
        draw.text((93, 10), str(SOC), font=font, fill=0)
        
        draw.rectangle((90, 22, 127, 42), outline=255, fill=255)     
        draw.text((95, 22), 'Temp', font=font, fill=0)
        draw.text((93, 32), str(Temp), font=font, fill=0)
        
        
        draw.rectangle((90, 44, 127, 63), outline=255, fill=255)     
        draw.text((95, 44), 'Exced.', font=font, fill=0)
        draw.text((100, 54), str(PWM), font=font, fill=0)

    elif modo==3:
        lineax=0
        lineay=0
        for I in range(nreles):             
            valor = int(Reles_L[I][1])
            if valor > 0:
                fill1=0
                fill2=255
            else:
                fill1=255
                fill2=0
            draw.rectangle((lineax, lineay, lineax+63, lineay+10), outline=255, fill=fill2)
            draw.text((lineax+2, lineay), Reles_L[I][0], font=font, fill=fill1)
            lineay +=10
            if lineay>53:
                lineax=66
                lineay=0

    elif modo == 4:
        if SOC == 100:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=255)
            draw.rectangle((3, 3, 124, 60), outline=255, fill=0)
            draw.rectangle((10, 10, 117, 53), outline=255, fill=255)
                        
            draw.text((13, 10), '100%', font=font34, fill=0)
        else:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
            draw.text((10, 10), str(SOC)+'%', font=font34, fill=255)
        
    if modo > 0:
        if pantalla == 1:
            disp1.clear()
            disp1.image(image)
            disp1.display()
            
        if pantalla == 2:
            disp2.clear()
            disp2.image(image)
            disp2.display()

#########################################################################################
# -------------------------------- BUCLE PRINCIPAL OLED --------------------------------------
#########################################################################################
try:
    time.sleep(20) # espera para que fv.py ponga datos_fv.csv
    cp = 0
    while True:
        ee=34
        
        with open('/run/shm/datos_fv.csv', mode='r') as f:
            d=f.read()
        d_fv = d.split(",")
    
        if DEBUG: print(d_fv)
        try:
            tiempo_sg = float(d_fv[0])
            tiempo = d_fv[1]
            Ibat = float(d_fv[2])
            Vbat = float(d_fv[3])
            SOC = float(d_fv[4])
            DS = float(d_fv[5])
            Aux1 = float(d_fv[6])
            Aux2 = float(d_fv[7])
            Whp_bat = float(d_fv[8])
            Whn_bat = float(d_fv[9])
            Iplaca = float(d_fv[10])
            Vplaca = float(d_fv[11])
            Wplaca = float(d_fv[12])
            Wh_placa = float(d_fv[13])
            Temp = float(d_fv[14])
            PWM = float(d_fv[15])
            Consumo = float(d_fv[16])
            Mod_bat = d_fv[17]
            Tabs = float(d_fv[18])
            Tflot = float(d_fv[19])
            Tflot_bulk = float(d_fv[20])
            SOC_min = float(d_fv[21])
            SOC_max = float(d_fv[22])
            Vbat_min = float(d_fv[23])
            Vbat_max = float(d_fv[24]) 
        except:
            print ('error datos_fv.csv')
            print (d_fv)
            time.sleep(0.3)
            continue
        
        try:
            with open('/run/shm/datos_reles.csv', mode='r',newline='\r\n') as f:
                d_reles=f.read().splitlines()
            if DEBUG: 
                print('nreles=',len(d_reles))
                print ('reles=',d_reles)
            nreles=len(d_reles)
            
            Reles_L = [ ] # inicializo lista reles
            
            for rele in d_reles:
                Reles_L.append(rele.split(','))  
            
            if DEBUG: 
                print (Reles_L)
                print('--------------------------------------------------')
            else:
                cp += 1
                print('x', end='')
                if cp > 100: cp=0;print();print(tiempo,end='')
        except:
            print ('error datos_reles.csv')
            print (Reles_L)
            time.sleep(0.3)
            continue
            
      ## ------- Salida por pantalla OLED -------
        
        if NUM_OLED >= 1: #OLED numero 1
            if OLED_salida_opcion1 < 0: # <0 es salida secuencial
                OLED(1,OLED_salida1[OLED_contador1])
                OLED_contador1 += 1
                if OLED_contador1 >= len(OLED_salida1):
                    OLED_contador1=0
            else:
                 OLED(1,OLED_salida_opcion1)

        if NUM_OLED == 2: #OLED numero 2
            if OLED_salida_opcion2 < 0: # <0 es salida secuencial
                OLED(2,OLED_salida2[OLED_contador2])
                OLED_contador2 += 1
                if OLED_contador2 >= len(OLED_salida2):
                    OLED_contador2=0
            else:
                 OLED(2,OLED_salida_opcion2)
        
        time.sleep(5)
        

except:
    print()
    print ('Error en bucle Oled',ee)
    traceback.print_exc()
finally:
    pass    
