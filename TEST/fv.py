#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-08-11

import time,csv
import datetime,glob
import MySQLdb 
import random # para simulacion usando random.choice

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

basepath = '/home/pi/PVControl+/'

print ('Arrancando_PVControl+')

#Parametros Instalacion FV
from Parametros_FV import *

#Pantalla OLED
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = 24

# Comprobacion numero de OLED instaladas
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
        #print ('OLED 3C y 3D')
    except:
        #print ('OLED 3C')
        pass
else:
    try:
        disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp1.begin()
        NUM_OLED += 1
        #print ('OLED 3D')
    except:
        pass
    

if NUM_OLED >= 1:
    #disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)        
    #disp1.begin()
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
    #disp2 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D)        
    #disp2.begin()
    disp2.clear()
    image2 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp2.image(image2)
    disp2.display()
    OLED_contador2 = 0 # contador del pantallazo que presenta en secuencial
    OLED_salida_opcion2 = -1

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]

bus = SMBus(1) # Bus I2C

if (Vbat_sensor + Vplaca_sensor + Vaux_sensor).find ('ADS') >=0 : 
    # Alta ADS1115_1 - pin addr a 3V3
    # A0=Vbat // A1=Vflot o Diver // A2= Vplaca// A3= Mux
    adc1 = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1) 

if (Ibat_sensor + Iplaca_sensor).find ('ADS') >=0:
    # Alta ADS1115_4 - pin addr a GND
    # A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
    adc = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1)

#---------------------------------------------------------------
DatosFV = {} #Creamos diccionario para los datos FV
OP = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,'id_rele2':7,'operacion':8,'parametro':9,'condicion':10,'valor':11}
OPH = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,'id_rele2':7,'parametro_h':8,'valor_h_ON':9,'valor_h_OFF':10}
NDIA = {'D':0,'L':1,'M':2,'X':3,'J':4,'V':5,'S':6}

#Inicializando las variables del programa
Grabar = 1

T_ejecucion_max = 0.0
hora3 = 5.0  
hora_m = time.time() #para calcular tiempo entre muestras real
dia = time.strftime("%Y-%m-%d") # para cambio de dia y reinicializar kWh
hora_actual = time.strftime("%H")
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

t_muestra = 5 # Inicializo Tiempo entre muestra real...idealmente TP[0][2]
t_muestra_1 = t_muestra_2 = t_muestra_3 = t_muestra_4 = t_muestra_5 = t_muestra_6 = 0 # muestras t ejecucion intermedias

Ibat = 0.0      # Intensidad Bateria
Vbat = vsis*12.0     # Voltaje Bateria inicial

Iplaca = 0.0    # Intensidad Placas Total
iplaca_shunt = 0.0    # Intensidad Placas (dato Shunt Iplaca)
iplaca_hibrido = 0.0    # Intensidad Placas (dato lectura Hibrido)


Vplaca = 0.0    # Volataje Placas (valor antes del regulador)
Vaux = 0.0      # Voltaje salida auxiliar Regulador
Temp = 0.0      # temperatura baterias
Mtemp = 24      # Numero de muestras para leer temperatura
sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave") # captura los DS18B20

Ctemp = 0       # Contador del numero de muestra para leer temperatura
Vflot = 0.0     # Voltaje asociado a estado de flotacion

nwifi_lectura = 0 #utilizado en secuenciacion lectura reles wifi

#---Variables calculo SOC --------------------------------
Ip = Ip1 = Ip2 = 0.0
float(CP)
float(Ip)
float(Ip1)
float(Ip2)
DS=0.0

Puerto = estado = 0

kWh_bat = kWhp_bat = kWhn_bat = 0.0

kWh_placa = kWh_consumo = 0.0

Ndiver=0
Tdiver=""

# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    #print("Connected with result code "+str(rc))
    client.subscribe("PVControl/Log")
    client.subscribe("PVControl/Opcion")
    client.subscribe("PVControl/Oled")
    
 
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global pub_diver,pub_time,OLED_salida_opcion
    
    #print(msg.topic+" "+str(msg.payload))
    if msg.topic== "PVControl/Log":
        try:
            db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor1 = db1.cursor()
            cursor1.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo, str(msg.payload)))
            db1.commit()
        except:
            db1.rollback()
        try:
            cursor1.close()
            db1.close()
        except:
            pass
    elif msg.topic== "PVControl/Opcion":
        pub_orden=str(msg.payload)
        print (pub_orden)
        if pub_orden == "PUB_DIVER_ON":
            pub_diver=1
        elif pub_orden == "PUB_DIVER_OFF":
            pub_diver=0
        elif pub_orden == "PUB_TIME_ON":
            pub_time=1
        elif pub_orden == "PUB_TIME_OFF":
            pub_time=0

    elif msg.topic== "PVControl/Oled":
        OLED_salida_opcion = int(str(msg.payload))
        #print (OLED_salida_opcion)

             
client = mqtt.Client("fv") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()


# --------------------- DEFINICION DE FUNCIONES --------------

def act_rele(adr,port,out) : # Activar Reles
    if simular_reles == 0:
        if int(adr/10) == 2: #Rele WIFI
            try:
                client.publish("PVControl/Reles/"+str(adr)+str(port),int(out))  # via MQTT
            except:
                if simular != 1:
                    logBD('Error rele wifi'+str(adr)+str(port)+'='+ str(out))   

        if int(adr/10) == 3: # Rele I2C
            try:
                estado = bus.read_byte(adr)  #devuelve el valor en decimal
                if out == 100 :
                    i2c_out = estado & (2**(port-1) ^ (255))
                else :
                    i2c_out = estado | 2**(port-1)
                bus.write_byte(adr,i2c_out)
            except:
                if simular != 1:
                    logBD('Error bus I2C '+str(adr)+str(port)+ '='+ str(out))
    return

def logBD(texto) : # Incluir en tabla de Log
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        #print (tiempo,' ', texto)
        db.commit()
    except:
        db.rollback()

    return

def leer_ibat(x) :  # leer Ibat
    try:
        if Ibat_sensor == 'ADS':
            y = - round(adc.read_adc_difference(0, gain=16, data_rate=8) * 0.0078125 * SHUNT1, 2)  # A0-A1

        if Ibat_sensor == 'HIBRIDO':
            
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Ibatp']) - float(d_hibrido['Ibatn'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        if Ibat_sensor == 'MONITOR':
            # SIN HACER....Trabajo para Paco
            y=x
            
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Ibat')
    if y < ibat_min or y > ibat_max:
        logBD('lectura incoherente Ibat='+str(y))
        y = x
    return y

def leer_iplaca(x) :  # leer Iplaca
    global iplaca_shunt, iplaca_hibrido
    try:
        if Iplaca_sensor == 'ADS':
            y =  leer_iplaca_shunt(x)

        if Iplaca_sensor == 'HIBRIDO':
            y =  leer_iplaca_hibrido(x)

        if Iplaca_sensor == 'ADS+HIBRIDO':
            iplaca_shunt = leer_iplaca_shunt(iplaca_shunt)
            iplaca_hibrido = leer_iplaca_hibrido(iplaca_hibrido)
            y = iplaca_shunt + iplaca_hibrido
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca')
    if y < iplaca_min or y > iplaca_max:
        logBD('lectura incoherente Iplaca='+str(y))
        y = x
    if y < 0.15:
        y = 0
    return y


def leer_iplaca_shunt(x) :  # leer Iplaca del shunt
    try:
        y =  round(adc.read_adc_difference(3, gain=16, data_rate=8) * 0.0078125 * SHUNT2, 2)  # A2-A3
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca')
    if y < iplaca_min or y > iplaca_max:
        logBD('lectura incoherente Iplaca='+str(y))
        y = x
    if y < 0.15:
        y = 0
    return y

def leer_iplaca_hibrido(x) :  # leer Iplaca del Hibrido
    try:
        dif = time.time() - float(d_hibrido['Tiempo_sg'])
 
        if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
            y = float(d_hibrido['Iplaca'])#*float(d_hibrido['Vplaca'])/float(d_hibrido['Vbat'])

        elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
            y = x

        else:
            y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca_hibrido')

    if y < iplaca_hibrido_min or y > iplaca_hibrido_max:
        logBD('lectura incoherente Iplaca_hibrido ='+str(y))
        y = x

    return y


def leer_vbat(x) :  # leer Vbat
    try:
        if Vbat_sensor == 'ADS':
            y = round(adc1.read_adc(0, gain=RES0_gain) * 0.000125/RES0_gain * RES0, 2)  # A0   4,096V/32767=0.000125 

        if Vbat_sensor == 'HIBRIDO':
            
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
 
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Vbat'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0
            
        if Vbat_sensor == 'MONITOR':
            # SIN HACER....Trabajo para Paco
            y=x
        
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Vbat')

    if y < vbat_min or y > vbat_max:
        logBD('lectura incoherente Vbat='+str(y))
        y = x
    return y


def leer_vaux(x) :  # leer Vaux
    try:
        if Vaux_sensor == 'ADS':
            y = round(adc1.read_adc(1, gain=RES1_gain) * 0.000125/RES1_gain * RES1, 2)  # A0   4,096V/32767=0.000125 
        else:
            y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Vaux')
    if y < vaux_min or y > vaux_max:
        logBD('lectura incoherente Vaux='+str(y))
        y = x
    return y

def leer_vplaca(x) :  # leer Vplaca
    try:
        if Vplaca_sensor == 'ADS':
            y = round(adc1.read_adc(2, gain=RES2_gain) * 0.000125/RES2_gain * RES2, 2)  # A0   4,096V/32767=0.000125 

        if Vplaca_sensor == 'HIBRIDO':
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
 
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Vplaca'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        if Vplaca_sensor == 'MONITOR' :  # No tiene mucho sentido
            # SIN HACER....Trabajo para Paco
            y=x

    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Vplaca')
    if y < vplaca_min or y > vplaca_max:
        logBD('lectura incoherente Vplaca='+str(y))
        y = x
    return y

def leer_diver(x) :  # leer estado excedentes
    if x == "VAUX":
        Vaux = leer_vaux(0)
        if Vaux > 1:
            Diver = 1
        else:
            Diver = 0
    elif x == "VPLACA":
        Vplaca = leer_vplaca(0) # si error lectura devuelve 0
        Ibat = leer_ibat(-10)    # si error lectura devuelve -10
        if Vplaca > TP[0][5] and Ibat > -10: 
            Diver = 1
        else:
            Diver = 0
    else:
        Diver = 0
    return Diver

def leer_temp(x) :  # leer temperatura
    try:
        #tempfile= open("/sys/bus/w1/devices/28-03170107adff/w1_slave")
        tempfile= open(sensores[indice_sensortemperatura]) # chequear indice 0 si se tienen instalados mas de un DS18B20
        thetext=tempfile.read()
        tempfile.close()
        tempdata = thetext.split("\n")[1].split(" ")[9]
        y = round(float(tempdata[2:]) / 1000,2)
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Temp')
    if y < temp_min or y > temp_max:
        logBD('lectura incoherente Temp='+str(y))
        y = x
    return y


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
        draw.text((100, 54), str(Diver), font=font, fill=0)

    elif modo==3:
        lineax=0
        lineay=0
        for I in range(nreles):             
            valor = int(TR[I][3] / 10)
            if valor > 0:
                fill1=0
                fill2=255
            else:
                fill1=255
                fill2=0
            draw.rectangle((lineax, lineay, lineax+63, lineay+10), outline=255, fill=fill2)
            draw.text((lineax+2, lineay), TR[I][1], font=font, fill=fill1)
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
            
## RECUPERAR DE LA BD ALGUNOS DATOS ##

try:

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql='SELECT DS, DATE(Tiempo) FROM datos ORDER BY id DESC limit 1'
    cursor.execute(sql)
    var=cursor.fetchone()
    DS=float(var[0])
    HOY=str(var[1])

    if HOY == time.strftime("%Y-%m-%d"):
        sql='SELECT kWhp_bat FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWhp_bat=float(var[0])

        sql='SELECT kWhn_bat FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWhn_bat=float(var[0])

        sql='SELECT kWh_placa FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWh_placa=float(var[0])

    else:
         kWhp_bat=0.0
         kWhn_bat=0.0
         kWh_placa=0.0
         #print ("Nuevo dia", time.strftime("%Y-%m-%d"))

except Exception as e:
    print ("Error, la base de datos no existe")

## Definir matrices Rele_Out y Rele_Out_Ant y apagar todos los reles
    
Rele_Out = [[0] * 8 for i in range(40)] # Situacion actual
Rele_Out_Ant = [[0] * 8 for i in range(40)] # Situacion anterior
TR_D = [[0] * 3 for i in range(40)]  #Para excedentes Id_rele,Control,Timestamp

##  ------ inicializamos reles apagandolos  ------------------------
sql_reles = 'SELECT * FROM reles'
nreles = cursor.execute(sql_reles)
nreles = int(nreles)  # = numero de reles
TR = cursor.fetchall()

for I in range(nreles): #apagado fisico
    Puerto = (TR[I][0] % 10) - 1
    addr = int((TR[I][0] - Puerto)/10)
    Rele_Out[addr][Puerto] = 0
    Rele_Out_Ant[addr][Puerto] = 0
    act_rele(addr,Puerto+1,0)

if nreles > 0 : # apagado en BD
    sql = "UPDATE reles SET estado = 0"
    cursor.execute(sql)

## ------------------------------------------------------------
### Calcular voltaje sistema (12,24 o 48)
#print ('ERROR LECTURA VOLTAJE BATERIA.....SISTEMA POR DEFECTO a 24V')

if simular != 1 and Vbat_sensor != 'HIBRIDO': 
    Vbat = leer_vbat(vsis*12.0) # pongo por defecto a 24v
else:
    Vbat = vsis * 12.0
    
log=''
if Vbat > 11 and Vbat < 15.5 :
    vsis = 1
elif Vbat > 22 and Vbat < 31 :
    vsis = 2
elif Vbat > 44 and Vbat < 62 :
    vsis = 4
else :
    log='Error: Imposible reconocer el voltaje del sistema'
    

vflotacion = 13.7 * vsis

print('Pulsa Ctrl-C para salir...')

log = ' Arrancando programa fv.py \nBateria = ' + str(Vbat) + 'v' + log
logBD(log) # incluyo mensaje en el log
if usar_telegram == 1:
    try:        
        pass
        #bot.send_message( cid, log)
    except:
        logBD("Error en Msg Telegram") # incluyo mensaje en el log
        
# -------------------------------- BUCLE PRINCIPAL --------------------------------------

while True:
    #print ('Bucle',)
    cursor.close()
    db.close()

    t_muestra_7=time.time()-hora_m

    hora1=time.time()
    
    ### ------------ Cargar tablas parametros, reles , reles_c, reles_h ---------------------

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql_reles='SELECT * FROM parametros'
    nparametros=cursor.execute(sql_reles)
    nparametros=int(nparametros)  # = numero de filas de parametros.---- debe ser 1
    TP=cursor.fetchall()
    
    sql_reles='SELECT * FROM reles'
    nreles=cursor.execute(sql_reles)
    nreles=int(nreles)  # = numero de reles
    TR=cursor.fetchall()

    sql_reles='SELECT * FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele'
    ncon=cursor.execute(sql_reles)
    ncon=int(ncon)  # = numero de condiciones
    R=cursor.fetchall()

    sql_reloj='SELECT * FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele'
    hcon=cursor.execute(sql_reloj)
    hcon=int(hcon)  # = numero de condiciones horarias
    H=cursor.fetchall()

    t_muestra_8=time.time()-hora_m
    # ------------------------ LECTURA FECHA / HORA ----------------------

    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    tiempo_sg = time.time()
    diasemana = time.strftime("%w")
    hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
    
    # ------------------------ LECTURA PARAMETROS FV----------------------

    t_muestra_ant=t_muestra
    t_muestra=time.time()-hora_m
    hora_m=time.time()

    if t_muestra > t_muestra_max:
        #logBD('Tmuestra elevado='+str(round(t_muestra,1))+'sg DIVER='+str(int(Ndiver))+'/'+Tdiver)
        logBD('TmuestraX='+str(round(t_muestra_1,1))+'/'+str(round(t_muestra_2,1))+'/'+str(round(t_muestra_3,1))+'/'+str(round(t_muestra_4,1))+'/'+str(round(t_muestra_5,1))+'/'+str(round(t_muestra_6,1))+'/'+str(round(t_muestra_7,1))+'/'+str(round(t_muestra_8,1)))

    if pub_time == 1:
        client.publish("PVControl/Opcion/Time",str(round(t_muestra_1,1))+'/'+str(round(t_muestra_2,1))+'/'+str(round(t_muestra_3,1))+'/'+str(round(t_muestra_4,1))+'/'+str(round(t_muestra_5,1))+'/'+str(round(t_muestra_6,1))+'/'+str(round(t_muestra_7,1))+'/'+str(round(t_muestra_8,1)))  # via MQTT

    if simular == 1:
        Ibat=random.choice([0,12,22,33,46,56,65,78,101,
                            -10,-20,-30,-40,-50,-60,-70,-80,-90])
        Iplaca=random.choice([0,10,20,30,45,57,67,77,88,99,102,110])
        Vbat=random.choice([22.5,23.7,24.0,24.4,25.5,26.3,27,27.5,28.2,29.1])
        Vplaca=random.choice([60,59.4,61,59.9,52,60.1,61.6,58.7,62,57.3])
        Diver=random.choice([1,1,1,0,1,0,1,1])  
        Temp=random.choice([10,12,14,16,18,20,22,24,26,28,30,32,34])
    else:
        if usar_hibrido == 1:
            with open('/run/shm/datos_hibrido.csv', mode='r') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    d_hibrido = row # Capturo los valores del fichero datos_hibrido.csv

        Ibat = leer_ibat(Ibat)
        Vbat = leer_vbat(Vbat)

        Iplaca = leer_iplaca(Iplaca)
        Vplaca = leer_vplaca(Vplaca)

        Vaux = leer_vaux(Vaux)

        TIPO_DIVER = TP[0][6].upper() # VAUX o VPLACA
        Diver = leer_diver(TIPO_DIVER)
        
        Vflot = 0
        
        # pongo 0, 1 ,2 o 3 en Vflot dependiendo de estado Vplaca/salida aux
        if Vaux > 1: # por ahora utilizare campo Vflot para ver Diver en la BD 
            Vflot = 1
        if Diver == 1:
            Vflot += 2
            
        if sensortemperatura == 1 and Ctemp <= 0:
            Temp = leer_temp(Temp)
            Ctemp=Mtemp # reinicio contador
            client.publish("PVControl/DatosFV/Temp",Temp)
        else:
            Ctemp -=1

    client.publish("PVControl/DatosFV/Ibat",Ibat)
    client.publish("PVControl/DatosFV/Iplaca",Iplaca)
    client.publish("PVControl/DatosFV/Vbat",Vbat)
    client.publish("PVControl/DatosFV/Vplaca",Vplaca)
    client.publish("PVControl/Reles/Diver", Diver)  # publico salida Diver


    ######## VALORES DEL MULTIPLEXOR ----PCF en Direccion 39---#########
    if mux == 1: 
        ###### Asegurar que el PCF del mux esta en la direccion 39 ==> A0=A1=A2=1
        for K in range(16):
            act_rele(39,1,int(not(K%2)))       #Pin S0 74HC4067
            act_rele(39,2,int(not((K//2)%2)))  #Pin S1 74HC4067
            act_rele(39,3,int(not((K//4)%2)))  #Pin S2 74HC4067
            act_rele(39,4,int(not((K//8)%2)))  #Pin S3 74HC4067

            #print ('direcc=',int(not(K%2)),)
            #print (int(not((K//2)%2)),)
            #print (int(not((K//4)%2)),)
            #print (int(not((K//8)%2)),)
            try:

                ###### pin del ADS1115 para mux
                mux1 = adc.read_adc(1, gain=1)
                #print (' Mux1=',mux1)

            #### FALTA INCORPORAR A BD ######

            except:
                logBD('-ERROR MEDIDA MUX1-'+ str(K))

    ##################################################################
    t_muestra_1=time.time()-hora_m


    ### CALCULO KWH_BAT y KWH_PLACA
    hora_anterior=hora_actual
    hora_actual=time.strftime("%H")

    dia_anterior = dia
    dia = time.strftime("%Y-%m-%d")

    #if (hora_anterior== "23" and hora_actual=="00"): #cambio de dia
    if dia_anterior != dia: #cambio de dia
        kWh_bat = 0.0
        kWhp_bat = 0.0
        kWhn_bat = 0.0
        kWh_placa = 0.0
    else:
        if Ibat < 0:
            kWhn_bat = round(kWhn_bat - (Ibat * Vbat * t_muestra/3600),2)
        else:
            kWhp_bat = round(kWhp_bat + (Ibat * Vbat * t_muestra/3600),2)

        kWh_placa = round(kWh_placa + (Iplaca * Vbat * t_muestra/3600),2)
        ###para kWh dividir por 1000

    ### CALCULO SOC% A C20
    if Ibat < 0 :
        Ip1 = -Ibat 
        Ip1 = Ip1**CP 
        Ip1 = AH*Ip1

        Ip2 = AH / 20
        Ip2 = (Ip2**CP)*20
        Ip= -Ip1/Ip2
    else :
        Ip = Ibat * EC

    if (Ibat>0 and Ibat<1 and abs(Vbat-vflotacion)<0.2) :
        DS = DS + (AH-DS)/50
    else :
        DS = DS + (Ip * t_muestra/3600)
    
    if DS > AH :
        DS = AH
    if DS < 0 :
        DS = 0

    if TP[0][4] != 0: # Actualizo SOC si en la BD es distinto de 0
        DS = AH*TP[0][4]/100
        cursor.execute("UPDATE parametros SET nuevo_soc=0 WHERE id_parametros=1")
        db.commit()                
    SOC = round(DS/AH*100,2)
    client.publish("PVControl/DatosFV/SOC",SOC)
    
    ### FIN CALCULO SOC%

    ### Salida por pantalla OLED
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


    #------------- Asignamos valores al diccionario para parametros condiciones ...

    DatosFV['Vbat'] = Vbat
    DatosFV['Ibat'] = Ibat
    DatosFV['SOC'] = SOC
    DatosFV['Iplaca'] = Iplaca
    DatosFV['Vflot'] = Vflot
    DatosFV['Temp'] = Temp
    DatosFV['Vplaca'] = Vplaca
    DatosFV['Diver'] = Diver

    # ----------------- Guardamos datos_fv.csv ------

    with open('/run/shm/datos_fv.csv', mode='w') as f:
        nombres = ['Tiempo_sg','Tiempo','Ibat', 'Vbat', 'SOC','DS','Vflot','kWhp_bat','kWhn_bat','Iplaca','Vplaca','kWh_placa','Temp']
        datos = csv.DictWriter(f, fieldnames=nombres)

        datos.writeheader()
        datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Ibat': Ibat,'Vbat': Vbat,'SOC': SOC,'DS':DS,'Vflot':Vflot,
                        'kWhp_bat': kWhp_bat,'kWhn_bat':kWhn_bat,'Iplaca':Iplaca,'Vplaca':Vplaca,
                        'kWh_placa':kWh_placa,'Temp':Temp})


    #------------------------ ALGORITMO CONDICIONES RELES -----------------------------

    #### Cargamos los valores actuales de los reles  en Rele_Out_Ant####
    nwifi = 0
    for I in range(nreles): # Calculo Numero reles wifi y Rele_Out_Ant por defecto
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)
        Rele_Out_Ant[addr][Puerto] = Rele_Out[addr][Puerto]
        if int(addr/10) == 2:
            nwifi = nwifi + 1

    nwifi_lectura = nwifi_lectura + 1 # lectura de un unico rele wifi por ciclo
    if nwifi_lectura > nwifi:       # para evitar colapsar al NodeMCU
        nwifi_lectura = 0

    nwifi_lectura1 = 0

    if simular_reles == 0: #Captura de los valores reales que estan en los reles
        for I in range(nreles):
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
                
            if int(addr/10) == 3: # Reles I2C
                try:
                    estado = bus.read_byte(addr)
                    estado = bin(estado ^ 255)[2:10].zfill(8)
                    Rele_Out_Ant[addr][Puerto] = int(estado[7-Puerto]) * 100
                except:
                    logBD('Error lectura I2C en direccion/ '+str(addr)+str(Puerto))

            if int(addr/10) == 2: # Reles Wifi re-escritura un solo rele por ciclo
                nwifi_lectura1 = nwifi_lectura1 + 1
                if nwifi_lectura == nwifi_lectura1:
                    try:
                        client.publish("PVControl/Reles/"+str(addr)+str(Puerto+1),int(Rele_Out[addr][Puerto]))  # via MQTT
                    except:
                        logBD('Rele ' + str(Puerto + 1) + ' en NodeMCU de direccion '+str(addr)+' NO ENCONTRADO')

    #### Apagamos virtualmente y encendemos SI condiciones FV o HORARIAS por defecto####
    
    for I in range(ncon): # enciendo reles con condiciones FV
        Puerto = (R[I][0] % 10) - 1
        addr = int((R[I][0]-Puerto) / 10)
        Rele_Out[addr][Puerto] = R[I][5] # pongo valor del salto

    for I in range(hcon): # enciendo reles con condiciones horario
        Puerto = (H[I][0] % 10)-1
        addr = int((H[I][0] - Puerto)/10)
        Rele_Out[addr][Puerto] = H[I][5] # pongo valor del salto

    for I in range(nreles): # reles Diver se ponen a situacion anterior
        if TR[I][6] != 0:
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto]

 # -------------------- Bucle de condiciones de horario --------------------------

    Rele_Out_H = [[0] * 8 for i in range(40)] # Inicializo variable a 0

    for I in range(hcon):
        Puerto = (H[I][0] % 10) - 1
        addr = int((H[I][0] - Puerto) / 10) 

        diaok = 0 # variables de control para ver si esta dentro de horario
        horaok = 0
        
        if H[I][OPH['parametro_h']] == 'T': #Todos los dias de la semana
            diaok = 1
        elif str(NDIA[H[I][OPH['parametro_h']]]) == diasemana:
            diaok = 1

        if str(H[I][OPH['valor_h_ON']]).zfill(8) > str(H[I][OPH['valor_h_OFF']]).zfill(8): #True si periodo pasa por 0:00
            if (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= "23:59:59"): 
                horaok = 1                                                       
            if (hora >= "00:00:00" and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)): 
                horaok = 1

        elif (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)):
            horaok = 1

        if diaok == 1 and horaok == 1:
            Rele_Out_H[addr][Puerto]+= 1

    for I in range(hcon):
        Puerto = (H[I][0] % 10)-1
        addr = int((H[I][0] - Puerto) / 10) 
                
        if Rele_Out_H[addr][Puerto] == 0:
            Rele_Out[addr][Puerto] = 0 #apago rele
            Rele_Out_H[addr][Puerto] = -1 # para quitar posibilidad de ser rele Diver en el ciclo

 # -------------------- Bucle de condiciones de parametros FV --------------------------

    for I in range(ncon):
        Puerto = (R[I][0] % 10) - 1   
        addr = int((R[I][0] - Puerto) / 10)

        if R[I][OP['condicion']] == '<':
            if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] > R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                Rele_Out[addr][Puerto] = 0
            if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] <= R[I][OP['valor']] :
                Rele_Out[addr][Puerto] = 0

        if R[I][OP['condicion']] == '>':
            if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] < R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                Rele_Out[addr][Puerto] = 0
            if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] >= R[I][OP['valor']] :
                Rele_Out[addr][Puerto] = 0

    #-------------------- Bucle encendido/apagado reles ------------------------------------

    Flag_Rele_Encendido = 0

    for I in range(nreles):
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)

        ### forzado ON/OFF
        if TR[I][OP['modo']] == 'ON' :
            Rele_Out[addr][Puerto] = 100
        if TR[I][OP['modo']] == 'OFF' :
            Rele_Out[addr][Puerto] = 0

        ### dejar rele como esta     
        if Rele_Out[addr][Puerto] == 100 and Rele_Out_Ant[addr][Puerto] < 100 and Flag_Rele_Encendido == 1 : 
            Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto]      #dejar rele en el estado anterior

        ### encender rele
        if Rele_Out[addr][Puerto] == 100 and Rele_Out_Ant[addr][Puerto] < 100 and Flag_Rele_Encendido == 0:
            Flag_Rele_Encendido = 1
            act_rele(addr,Puerto+1,100)

        ### apagar rele
        if Rele_Out[addr][Puerto] == 0 and Rele_Out_Ant[addr][Puerto] > 0 :
            act_rele(addr,Puerto+1,0) #apagar rele

    ### CONTROL DE EXCEDENTES -- DIVER
    t_muestra_2=time.time()-hora_m

    Ndiver = 1 # Numero de ciclos Diver por muestra
    Tdiver = str(Diver) # Almacena secuencia Diver
    while True:
        if simular == 1:
            Diver = random.choice([1,0,1,0,1,0,1,0,1])
        else:
            Diver = leer_diver(TIPO_DIVER)

        Tdiver = Tdiver + str(Diver)
        #client.publish("PVControl/Reles/Diver", Diver)  # publico salida Diver
        
        if Diver == 1 :  #hay excedentes
            # Pongo 1 en TR_D[P][1] en reles candidatos a Diver
            # y busco prioridad_actual
            prioridad_actual = 100
            for P in range(nreles):
                Puerto = (TR[P][0] % 10) - 1
                addr = int((TR[P][0] - Puerto) / 10)

                TR_D[P][0] = TR[P][0]
                TR_D[P][1] = 0
                if TR[P][2] == 'PRG' and Rele_Out[addr][Puerto] < 100 and TR[P][6]!= 0 and Rele_Out_H[addr][Puerto] != -1:
                    TR_D[P][1] = 1
                    if TR[P][6] < prioridad_actual :
                        prioridad_actual = TR[P][6]
                    else:
                        TR_D[P][1] = 0

            if prioridad_actual != 100:
                # Pongo 2 en TR_D[P][1] si coincide prioridad actual
                # y busco rele con la marca temporal mas antigua
                timerele = 9999999999
                id_rele_diver = 0
                for P in range(nreles):
                    if TR[P][6] == prioridad_actual and TR_D[P][1] == 1 and TR_D[P][2] < timerele:
                        timerele = TR_D[P][2]
                        id_rele_diver = TR_D[P][0]

                for P in range(nreles):
                    if TR[P][0] == id_rele_diver:
                        Puerto = (TR[P][0] % 10) - 1
                        addr = int((TR[P][0] - Puerto) / 10)
                        Rele_Out[addr][Puerto] = Rele_Out[addr][Puerto] + TR[P][5]

                        if Rele_Out[addr][Puerto] > 100:
                            Rele_Out[addr][Puerto] = 100
                        act_rele(addr,Puerto+1,Rele_Out[addr][Puerto])
                        timerele = time.process_time() #time.clock()
                        TR_D[P][2] = timerele

            #break

        else:  # NO hay excedentes  Diver==0
            prioridad_actual = 0
            for P in range(nreles):
                Puerto = (TR[P][0] % 10) - 1
                addr = int((TR[P][0] - Puerto) / 10)
                TR_D[P][0] = TR[P][0]
                if TR[P][2] == 'PRG' and Rele_Out[addr][Puerto] > 0 and TR[P][6]!= 0 :
                    TR_D[P][1] = 1
                    if TR[P][6] > prioridad_actual :
                        prioridad_actual = TR[P][6]
                else:
                    TR_D[P][1] = 0

            if prioridad_actual != 0:
                timerele = 9999999999
                id_rele_diver = 0
                for P in range(nreles):
                    if TR[P][6] == prioridad_actual and TR_D[P][1] == 1 and TR_D[P][2] < timerele:
                        timerele = TR_D[P][2]
                        id_rele_diver = TR_D[P][0]

                for P in range(nreles):
                    if TR[P][0] == id_rele_diver:
                        Puerto = (TR[P][0] % 10) - 1
                        addr = int((TR[P][0] - Puerto) / 10)
                        Rele_Out[addr][Puerto] = Rele_Out[addr][Puerto] - TR[P][5]

                        if Rele_Out[addr][Puerto] < 0:
                            Rele_Out[addr][Puerto] = 0
                        act_rele(addr,Puerto+1,Rele_Out[addr][Puerto])
                        timerele = time.process_time() #time.clock()
                        TR_D[P][2] = timerele

        Ndiver += 1
        time.sleep(0.2)
        if time.time() - hora1 > TP[0][2] - 0.5: #Tmuestra menos 0.5 segundos
            break

    t_muestra_3=time.time()-hora_m

    #if int(hora_actual) < 21 and int(hora_actual) > 8:
    #    print (hora, round(t_muestra_3 - t_muestra_2,1), Ndiver, Tdiver)

    if pub_diver==1:
        client.publish("PVControl/Opcion/Diver",str(round((t_muestra_3 - t_muestra_2),1))+'/'+str(Ndiver)+'/'+Tdiver)  # via MQTT
    

    # -------------------------- Escribir en la BD Tabla Reles el Estado RELES -------------------------
    for I in range(nreles):
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)
        id = TR[I][0]
        estado = Rele_Out[addr][Puerto]
        sql = "UPDATE reles SET estado =" +str(estado)+ " WHERE id_rele = " + str(id)
        sql_reles = 'SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha='+'"'+time.strftime("%Y-%m-%d")+'" and id_rele =' + str(id)

        try:
            nreles_on = cursor.execute(sql_reles)
            nreles_on = int(nreles_on)
            if estado > 0 :
                segundos_on = TP[0][2]
                nconmutaciones = 1

                if nreles_on >= 1:
                    TS = cursor.fetchall()
                    
                    segundos_on = TS[0][1] + round((t_muestra*estado/100),2)  # calculo funcionamiento real reles PWM
                    if TR[I][3] == 0:
                        nconmutaciones = TS[0][2] + 1
                    else:
                        nconmutaciones = TS[0][2]

                    #UPDATE
                    sql_reles = ("UPDATE reles_segundos_on SET segundos_on =" +str(segundos_on)+
                                 ",nconmutaciones =" + str(nconmutaciones)+ " WHERE id_rele = " +
                                 str(id) + ' and fecha = "' + time.strftime("%Y-%m-%d") +'"')
                    cursor.execute(sql_reles)
                else :
                    #INSERT
                    cursor.execute("""INSERT INTO reles_segundos_on
                                    (id_rele,fecha,segundos_on,nconmutaciones)
                                    VALUES (%s,%s,%s,%s)""",
                                    (id,time.strftime("%Y-%m-%d"),segundos_on,1))

            if Rele_Out[addr][Puerto] != TR[I][3]:
                cursor.execute(sql)

    ##            db.commit()

        except:
            db.rollback()
            logBD('Error grabacion Reles_segundos_on')
            
        if TP[0][1] == "S" and Grabar == 1 and TR[I][4] == "S" and Rele_Out[addr][Puerto] != TR[I][3]:
            try:
                cursor.execute("""INSERT INTO reles_grab (Tiempo,id_rele,valor_rele)
                               VALUES(%s,%s,%s)""",(tiempo,TR[I][0],estado))
    ##            db.commit()
            except:
                db.rollback()
                logBD('tabla reles_grab NO grabados por fallo')

    t_muestra_4=time.time()-hora_m
    #------------------------Escribir en la tabla valores FV  ---------------------------

    if TP[0][0] == "S" and Grabar == 1:
        try:
            cursor.execute("""INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Vflot,kWhp_bat,kWhn_bat,Iplaca,Vplaca,kWh_placa,Temp) 
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
               (tiempo,Ibat,Vbat,SOC,DS,Vflot,kWhp_bat,kWhn_bat,Iplaca,Vplaca,kWh_placa,Temp))
            db.commit()

        except:
            db.rollback()
            logBD('Registro DATOS no grabado')
    else :
        db.commit()
        #print ("registro DATOS NO grabado")

    t_muestra_5=time.time()-hora_m

    Grabar += 1
    if Grabar >= TP[0][3] + 1:
        Grabar = 1

    hora2 = time.time()
    ###### ajuste fino tiempo bucle=0.10
    T_ejecucion = hora2 - hora1 + 0.10
    if T_ejecucion_max < T_ejecucion:
        T_ejecucion_max = T_ejecucion


    # Repetir bucle cada X segundos
    espera = TP[0][2] - T_ejecucion
    if espera > 0:
        time.sleep(espera)
    t_muestra_6=time.time()-hora_m

