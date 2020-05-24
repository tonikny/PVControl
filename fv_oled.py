#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-05-23

import time,csv,sys, subprocess
import traceback
import datetime,glob
import pickle,json

basepath = '/home/pi/PVControl+/'

print ('Arrancando_PVControl+- OLED')

#Parametros Instalacion FV
from Parametros_FV import *

#Pantalla OLED
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = 24 #parametro OLED

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print ('DEBUG=',DEBUG)


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
        draw.text((8, 0), 'SOC='+str(d_fv['SOC'])+'%', font=font16, fill=255)
        draw.rectangle((0, 20, 64, 46), outline=255, fill=0)
        draw.rectangle((64, 20, 127, 46), outline=255, fill=0)
        draw.text((4, 22),  'Vbat='+str(d_fv['Vbat']), font=font, fill=255)
        draw.text((69, 22), 'Ibat='+str(d_fv['Ibat']), font=font, fill=255)
        draw.text((4, 34),  'Vpla='+str(d_fv['Vplaca']), font=font, fill=255)
        draw.text((69, 34), 'Ipla='+str(d_fv['Iplaca']), font=font, fill=255)

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
        draw.text((8, 1), 'Vbat='+str(d_fv['Vbat']), font=font11, fill=255)
        draw.text((8, 14), 'Ibat='+str(round(d_fv['Ibat'],0)), font=font11, fill=255)
        draw.rectangle((0, 31, 90, 63), outline=255, fill=0)     
        draw.text((8, 31), 'Vpla='+str(round(d_fv['Vplaca'],1)), font=font11, fill=255)
        draw.text((8, 45), 'Ipla='+str(round(d_fv['Iplaca'],0)), font=font11, fill=255)

        draw.rectangle((90, 0, 127, 20), outline=255, fill=255)     
        draw.text((100, 0), 'SOC', font=font, fill=0)
        draw.text((93, 10), str(d_fv['SOC']), font=font, fill=0)
        
        draw.rectangle((90, 22, 127, 42), outline=255, fill=255)     
        draw.text((95, 22), 'Temp', font=font, fill=0)
        draw.text((93, 32), str(d_fv['Temp']), font=font, fill=0)
        
        
        draw.rectangle((90, 44, 127, 63), outline=255, fill=255)     
        draw.text((95, 44), 'Exced.', font=font, fill=0)
        draw.text((100, 54), str(d_fv['PWM']), font=font, fill=0)

    elif modo==3:
        lineax=0
        lineay=0
        
        for rele in d_reles:
            valor = rele[1]
            if valor > 0:
                fill1=0
                fill2=255
            else:
                fill1=255
                fill2=0
            draw.rectangle((lineax, lineay, lineax+63, lineay+10), outline=255, fill=fill2)
            draw.text((lineax+2, lineay), rele[0], font=font, fill=fill1)
            lineay +=10
            if lineay>53:
                lineax=66
                lineay=0
        
    elif modo == 4:
        if d_fv['SOC'] == 100:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=255)
            draw.rectangle((3, 3, 124, 60), outline=255, fill=0)
            draw.rectangle((10, 10, 117, 53), outline=255, fill=255)
                        
            draw.text((13, 10), '100%', font=font34, fill=0)
        else:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
            draw.text((10, 10), str(d_fv['SOC'])+'%', font=font34, fill=255)
        
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
    
    time.sleep(2) # espera para que fv.py ponga datos_fv.json
    cp = 0
    while True:
        ee=34
        nombres=(['Tiempo_sg', 'Tiempo', 'Ibat','Vbat','SOC','DS','Aux1','Aux2',
                  'Whp_bat','Whn_bat','Iplaca','Vplaca','Wplaca','Wh_placa',
                  'Temp','PWM','Consumo','Mod_bat','Tabs','Tflot','Tflot_bulk',
                  'SOC_min','SOC_max','Vbat_min','Vbat_max'])

        try:
            archivo_ram='/run/shm/datos_fv.json'
            with open(archivo_ram, 'rb') as f:
                dct = json.load(f)
            
            d_fv={}
            for i in range (len(nombres)): d_fv[nombres[i]]=dct[i]
        
            if DEBUG>=1: print(d_fv)
        
            archivo_ram='/run/shm/datos_reles.json'
            with open(archivo_ram, 'rb') as f:
                d_reles = json.load(f)
            
            nreles=len(d_reles)
            
            if DEBUG >= 1: 
                print('nreles=',len(d_reles))
                print ('reles=',d_reles)
                print('--------------------------------------------------')
            else:
                cp += 1
                print('x', end='')
                if cp > 100: cp=0;print();print(tiempo,end='')
        except:
            print ('error lectura datos.json')
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
