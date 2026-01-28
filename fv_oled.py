# -*- coding: utf-8 -*-

# Versión 2024-03-29


# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################
"""
#### Pantalla predefinidas:
   0 ... Logo PVControl+
   1 ... Resumen1 Bateria/Placas/Reles
   2 ... Resumen2 Bateria/Placas/Reles
   3 ... Detalles Reles
   4 ... SOC en grande
   5 ... Estado PVControl+
   El resto de pantallas que se quieran se deben definir en 'PANTALLAS' (se pone como ejemplo JK1 y JK2)
   
"""
OLED = {
  'OLED1' : {'tipo':'ssd1306',         # SSD1306 o SH1106
             'i2c_direccion' : 0x3C,   # Direccion I2C de la pantalla
             'salida':[0,1,2,3,4]},    # secuencia de pantallazos cada 5 sg
  
  'OLED2' : {'tipo':'ssd1306',
             'i2c_direccion' : 0x3D,
             'salida':['JK1', 'JK2', 5]},

  'PANTALLAS' :{
        'JK1' : ["draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                 "draw.text((8, 0), 'JK1'+' - '+str(d_['BMS_JK1']['SOC'])+'%', font=font16, fill=255)",
                 "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                 "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK1']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK1']['Ibat'])+'A', font=font, fill=255)",
                 "draw.text((4, 34), str(max(d_['BMS_JK1']['Vceldas']))+' - '+str(min(d_['BMS_JK1']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK1']['Vceldas']))-(min(d_['BMS_JK1']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                 "draw.text((4, 46), 'AH = '+str(d_['BMS_JK1']['AH_p'])+' - '+str(d_['BMS_JK1']['AH_n'])+' = '+str((d_['BMS_JK1']['AH_p'])-(d_['BMS_JK1']['AH_n'])), font=font, fill=255)",
                ],
        
        'JK2' : ["draw.rectangle((0, 0, 127, 20), outline=255, fill=0)",
                 "draw.text((8, 0), 'JK2'+' - '+str(d_['BMS_JK2']['SOC'])+'%', font=font16, fill=255)",
                 "draw.rectangle((0, 20, 127, 63), outline=255, fill=0)",
                 "draw.text((4, 22), 'Vbat='+str(d_['BMS_JK2']['Vbat'])+'V' +' / '+'Ibat='+str(d_['BMS_JK2']['Ibat'])+'A', font=font, fill=255)",
                 "draw.text((4, 34), str(max(d_['BMS_JK2']['Vceldas']))+' - '+str(min(d_['BMS_JK2']['Vceldas']))+' = '+str(int((round((max(d_['BMS_JK2']['Vceldas']))-(min(d_['BMS_JK2']['Vceldas'])),3))*1000))+'mV', font=font, fill=255)",
                 "draw.text((4, 46), 'AH = '+str(d_['BMS_JK2']['AH_p'])+' - '+str(d_['BMS_JK2']['AH_n'])+' = '+str((d_['BMS_JK2']['AH_p'])-(d_['BMS_JK2']['AH_n'])), font=font, fill=255)",
                ],
      }
}
############## FIN CONFIGURACION #######################################


import time,sys #, subprocess
import traceback
#import glob
import MySQLdb,json 

basepath = '/home/pi/PVControl+/'

print ('Arrancando_PVControl+- OLED')

#Parametros Instalacion FV
from Parametros_FV_DIST import *
from Parametros_FV import *

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, sh1106

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pathlib import Path

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

if DEBUG !=0: print ('DEBUG=',DEBUG)

# Comprobacion numero de OLED instaladas

puerto1 = 1 if 'puerto' not in OLED['OLED1'] else OLED['OLED1']['puerto'] # por si se define el bus I2C en un puerto distinto  
puerto2 = 1 if 'puerto' not in OLED['OLED2'] else OLED['OLED2']['puerto']

###### OLED1 ###########
OLED1 = False
NUM_OLED = 0
try:
    serial1 = i2c(port=puerto1, address=OLED['OLED1']['i2c_direccion'])
    
    if OLED['OLED1']['tipo'].upper() == 'SSD1306' : disp1 = ssd1306(serial1,rotate=0)
    elif OLED['OLED1']['tipo'].upper() == 'SH1106': disp1 = sh1106(serial1,rotate=0)
    else:
        print (f"Tipo de pantalla {OLED['OLED1']['tipo'] } no reconocido")
        raise ValueError("Error en tipo pantalla OLED1")
    
    OLED1 = True
    NUM_OLED = 1
    print(f"Activada OLED1 de tipo {OLED['OLED1']['tipo']} en direccion {OLED['OLED1']['i2c_direccion']} ")
    
except:
    print(f" No detectada OLED1 en direccion {OLED['OLED1']['i2c_direccion']}")
    
    time.sleep(1)
    pass

###### OLED2 ###########
OLED2 = False
try:
    serial2 = i2c(port=puerto2, address=OLED['OLED2']['i2c_direccion'])
    
    if OLED['OLED2']['tipo'].upper() == 'SSD1306' : disp2 = ssd1306(serial2,rotate=0)
    elif OLED['OLED2']['tipo'].upper() == 'SH1106': disp2 = sh1106(serial2,rotate=0)
    else:
        print (f"Tipo de pantalla {OLED['OLED2']['tipo'] } no reconocido.... se finaliza")
        raise ValueError("Error en tipo pantalla OLED2")
    
    OLED2 = True
    NUM_OLED += 1
    print (f"Activada OLED2 de tipo {OLED['OLED2']['tipo']} en direccion {OLED['OLED2']['i2c_direccion']} ")
    
except:
    print(f" No detectada OLED2 en direccion {OLED['OLED2']['i2c_direccion']}")
    
    time.sleep(1)
    pass


if NUM_OLED == 0:
    if DEBUG !=0: print ('NO detectada OLED - reintento en 1 minuto')
    sys.exit()

font34 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 34)
font16 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 16)
font12 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 12)
font10 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 10)
font11 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 15)
font6 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 10)
font = ImageFont.load_default()

#### PANTALLAZO INICIAL ######
if OLED1:
    logo1 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.LANCZOS).convert('1')    
    disp1.display(logo1.convert(disp1.mode))       
    width1 = disp1.width
    height1 = disp1.height
    image1 = Image.new('1', (width1, height1))
    draw1 = ImageDraw.Draw(image1)
    OLED_contador1 = 0 # contador del pantallazo que presenta en secuencial

if OLED2:
    logo2 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp2.width, disp2.height), Image.LANCZOS).convert('1')    
    disp2.display(logo2.convert(disp2.mode))       
    width2 = disp2.width
    height2 = disp2.height
    image2 = Image.new('1', (width2, height2))
    draw2 = ImageDraw.Draw(image2)
    OLED_contador2 = 0 # contador del pantallazo que presenta en secuencial

def salida_OLED(pantalla,modo,draw):
    print (f"{time.strftime('%Y-%m-%d %H:%M:%S')} --> Pantalla:{pantalla} - Modo:{modo}")
    
    if pantalla == 1: draw.rectangle((0,0,width1,height1), outline=0, fill=0)
    elif pantalla == 2: draw.rectangle((0,0,width2,height2), outline=0, fill=0)

    if modo == 0: #Logo PVControl+
        logo = Image.open(basepath+'pvcontrol_128_64.png').convert('1')
        if pantalla == 1:
            disp1.display(logo.convert(disp1.mode))   
        else:
            disp2.display(logo.convert(disp2.mode))
        
        return

    elif modo == 1: # Resumen1 Baterias/Placas/Reles
        draw.rectangle((0, 0, 127, 20), outline=255, fill=0)
        draw.text((8, 0), 'SOC='+str(d_['FV']['SOC'])+'%', font=font16, fill=255)
        draw.rectangle((0, 20, 64, 46), outline=255, fill=0)
        draw.rectangle((64, 20, 127, 46), outline=255, fill=0)
        draw.text((4, 22),  'Vbat='+str(d_['FV']['Vbat']), font=font, fill=255)
        draw.text((69, 22), 'Ibat='+str(d_['FV']['Ibat']), font=font, fill=255)
        draw.text((4, 34),  'Vpla='+str(d_['FV']['Vplaca']), font=font, fill=255)
        draw.text((69, 34), 'Ipla='+str(d_['FV']['Iplaca']), font=font, fill=255)

        # Rele={2:'3X', 3:'XX0X', 7:'4'}
        L4 = 'R='
        Rele={}
        
        for r in d_['RELES']:
            tipo_rele = int(int(r)/100)
            if tipo_rele not in Rele.keys(): Rele[tipo_rele] = '' # inicializo valor
            valor = f"{d_['RELES'][r]['estado']/10:1.0f}"
            if valor == '10': valor = 'X'
            Rele[tipo_rele] += valor
        
        for r in Rele: L4 +=f'{r}{Rele[r]}-'
        L4 = L4[:-1] 
        
        draw.text((2, 49), L4, font=font11, fill=255)

    elif modo == 2:# Resumen2 Baterias/Placas/Reles
        draw.rectangle((0, 0, 90, 31), outline=255, fill=0)
        draw.text((8, 1), 'Vbat='+str(d_['FV']['Vbat']), font=font11, fill=255)
        draw.text((8, 14), 'Ibat='+str(round(d_['FV']['Ibat'],0)), font=font11, fill=255)
        draw.rectangle((0, 31, 90, 63), outline=255, fill=0)     
        draw.text((8, 31), 'Vpla='+str(round(d_['FV']['Vplaca'],1)), font=font11, fill=255)
        draw.text((8, 45), 'Ipla='+str(round(d_['FV']['Iplaca'],0)), font=font11, fill=255)

        draw.rectangle((90, 0, 127, 20), outline=255, fill=255)     
        draw.text((100, 0), 'SOC', font=font, fill=0)
        draw.text((93, 10), str(d_['FV']['SOC']), font=font, fill=0)
        
        draw.rectangle((90, 22, 127, 42), outline=255, fill=255)     
        draw.text((95, 22), 'Temp', font=font, fill=0)
        draw.text((93, 32), str(d_['FV']['Temp']), font=font, fill=0)
        
        
        draw.rectangle((90, 44, 127, 63), outline=255, fill=255)     
        draw.text((95, 44), 'Exced.', font=font, fill=0)
        draw.text((100, 54), str(d_['FV']['PWM']), font=font, fill=0)

    elif modo==3: # Detalles Reles
        lineax=0
        lineay=0
        
        for r in d_['RELES']:
            valor = float(d_['RELES'][r]['estado'])
            if valor > 0:
                fill1=0
                fill2=255
            else:
                fill1=255
                fill2=0
            draw.rectangle((lineax, lineay, lineax+63, lineay+10), outline=255, fill=fill2)
            draw.text((lineax+2, lineay), d_['RELES'][r]['nombre'], font=font, fill=fill1)
            lineay +=10
            if lineay>53:
                lineax=66
                lineay=0
        
    elif modo == 4: # SOC en grande
        if d_['FV']['SOC'] == 100:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=255)
            draw.rectangle((3, 3, 124, 60), outline=255, fill=0)
            draw.rectangle((10, 10, 117, 53), outline=255, fill=255)
                        
            draw.text((13, 10), '100%', font=font34, fill=0)
        else:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
            draw.text((10, 10), str(d_['FV']['SOC'])+'%', font=font34, fill=255)
            
    elif modo == 5: # Estado PVControl+
        draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
        draw.text((4, 0), str(d_['_PVControl+']), font=font, fill=255)         
        
    elif modo in OLED['PANTALLAS']:
        try:
            for r in OLED['PANTALLAS'][modo]:
                exec(r)
        except:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
            draw.rectangle((0, 0, 127, 20), outline=255, fill=0)
            draw.text((3, 1), f'ERROR en {modo}', font=font12, fill=255)
            draw.text((4, 22), f'{r}', font=font, fill=255)
            print (f'Error en pantalla {modo} -> {r}')
        

    if pantalla == 1:  disp1.display(image1.convert(disp1.mode))     
    elif pantalla == 2:  disp2.display(image2.convert(disp2.mode))   

 
 
#########################################################################################
# -------------------------------- BUCLE PRINCIPAL OLED --------------------------------------
#########################################################################################
try:
    
    time.sleep(10) # espera para que fv.py ponga en tabla equipos
    cp = 0
    while True:
        ee=10
        
        try:
            ## Capturando valores desde BD en tabla equipos
            ee=10.1
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
  
            sql = 'SELECT * FROM equipos' # WHERE id_equipo IN' ('FV','RELES')'# capturo todo...quizas lo logico solo FV y RELES
            nequipos = int(cursor.execute(sql))
           
            d_={}
            for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])
            if DEBUG == 100:
                print ('#'*40)
                print ('Equipos =',d_)
            cursor.close()
            db.close()
            
            ee=10.2    
            d_reles = d_['RELES']
            ee = 10.3
            nreles=len(d_['RELES'])
            ee = 10.4
            
            if DEBUG >= 1: 
                print('nreles=',nreles)
                print ('reles=',d_['RELES'])
                print('--------------------------------------------------')
            else:
                cp += 1
                print('x', end='',flush=True)
                if cp > 100: cp=0;print();print(time.strftime("%Y-%m-%d %H:%M:%S"),end='')
            
        except:
            print (f'error {ee} en lectura tabla equipos')
            time.sleep(0.3)
            break
            continue
            
      ## ------- Salida por pantalla OLED -------
        OLED_salida1 = OLED['OLED1']['salida']
        OLED_salida2 = OLED['OLED2']['salida']
        
        if OLED1: #OLED numero 1
            salida_OLED(1,OLED_salida1[OLED_contador1],draw1)
            OLED_contador1 += 1
            if OLED_contador1 >= len(OLED_salida1): OLED_contador1=0

        if OLED2: #OLED numero 2
            salida_OLED(2,OLED_salida2[OLED_contador2],draw2)
            OLED_contador2 += 1
            if OLED_contador2 >= len(OLED_salida2): OLED_contador2=0
        
        time.sleep(5)
        

except:
    print()
    print ('Error en bucle OLED',ee)
    traceback.print_exc()
finally:
    pass    
