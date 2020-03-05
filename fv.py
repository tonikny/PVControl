#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-02-25

import time,csv,sys
import datetime,glob
import MySQLdb 
import random # para simulacion usando random.choice

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

import RPi.GPIO as GPIO # reles 4XX via GPIO
GPIO.setmode(GPIO.BOARD) #para RPi

basepath = '/home/pi/PVControl+/'

print ('Arrancando_PVControl+')

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

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]

if (Vbat_sensor + Vplaca_sensor + Aux1_sensor+ Aux2_sensor + Ibat_sensor + Iplaca_sensor).find ('ADS') >=0 : 
    bus = SMBus(1) # Bus I2C

if (Vbat_sensor + Vplaca_sensor + Aux1_sensor+ Aux2_sensor).find ('ADS') >=0 : 
    # Alta ADS1115_1 - pin addr a 3V3
    # A0=Vbat // A1=Aux1 // A2= Vplaca// A3= Aux2
    adc1 = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1) 

if (Ibat_sensor + Iplaca_sensor).find ('ADS') >=0:
    # Alta ADS1115_4 - pin addr a GND
    # A0=Ibat // A1=Ibat // // A2=Iplaca // A3=Iplaca
    adc = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1)

#---------------------------------------------------------------
DatosFV = {} #Creamos diccionario para los datos FV

OP = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,
      'id_rele2':7,'operacion':8,'parametro':9,'condicion':10,'valor':11}
OPH = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,
       'id_rele2':7,'parametro_h':8,'valor_h_ON':9,'valor_h_OFF':10}
NDIA = {'D':0,'L':1,'M':2,'X':3,'J':4,'V':5,'S':6}

nombres_datos = ['Tiempo_sg','Tiempo','Ibat', 'Vbat', 'SOC','DS','Aux1','Aux2',
                 'Whp_bat','Whn_bat','Iplaca','Vplaca','Wplaca','Wh_placa','Temp','PWM', 'Mod_bat']

#Inicializando las variables del programa
Grabar = 1 # Contador ciclo grabacion en BD

T_ejecucion_max = 0.0
#hora3 = 5.0  
hora_m = time.time() #para calcular tiempo entre muestras real
dia = time.strftime("%Y-%m-%d") # para cambio de dia y reinicializar Wh
hora_actual = time.strftime("%H")
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

t_muestra = 5 # Inicializo Tiempo entre muestra real...idealmente TP[2]
t_muestra_1 = t_muestra_2 = t_muestra_3 = t_muestra_4 = t_muestra_5 = t_muestra_6 = 0 # muestras t ejecucion intermedias
T_ejecucion = 0

Ibat = 0.0      # Intensidad Bateria
Vbat = vsis*12.0     # Voltaje Bateria inicial
Mod_bat =''

Iplaca = 0.0          # Intensidad Placas Total
iplaca_shunt = 0.0    # Intensidad Placas (dato Shunt Iplaca)
iplaca_hibrido = 0.0  # Intensidad Placas (dato lectura Hibrido)
iplaca_victron = 0.0  # Intensidad Placas (dato lectura Victron)

Vplaca = 0.0    # Voltaje Placas (valor antes del regulador)
Aux1 = Aux2 = 0.0   # Valores de captura auxiliares (salida regulador, Iplaca2, etc)
Temp = 0.0      # temperatura baterias
Mtemp = 60      # Numero de segundos para leer temperatura
sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave") # captura los DS18B20

Ctemp = 0       # Contador del numero de muestra para leer temperatura
Vflot = Vabs = Vecu = 0.0   # Voltaje asociado a estado de flotacion/Absorcion/Ecu
Tflot = Tabs = Tecu = 0.0   # Tiempo asociado a estado de flotacion/Absorcion/Ecu
Tflot_bulk = Tbulk = 0.0    # Tiempo asociado al paso de FLOT a BULK 

flag_Abs= flag_Flot = 0

Coef_Temp = 0.0             # Coeficiente de compensacion de temperatura para Vflot/Vabs 

Nlog = Nlog_max = 30 # Contador Numero de log maximos cada minuto
minuto = time.strftime("%H:%M")

nwifi_lectura = 0 #utilizado en secuenciacion lectura reles wifi

CD1 = CD2 = CD3 = CD4 = CD5 = 0.0 # contadores que se ponen a cero cada dia
C1 = C2 = C3 = C4 = C5 = 0.0      # contadores que NO se ponen a cero cada dia

#---Variables calculo SOC --------------------------------
Ip = Ip1 = Ip2 = DS = 0.0

Puerto = estado = 0
Wh_bat = Whp_bat = Whn_bat = 0.0
Wh_placa = Wh_consumo = 0.0

N = 5  # numero de muestras para PID
Lista_errores_PID = [0.0 for i in range(N)]
PWM = NDiver = IPWM_P = IPWM_I = IPWM_D = 0.0
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
    global pub_time,OLED_salida_opcion
    
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
        
        if pub_orden == "PUB_TIME_ON":
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
                #print("PVControl/Reles/"+str(adr)+str(port),int(out))
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

        if int(adr/10) == 4: # Rele GPIO
            try:
                #if DEBUG >= 2: print('rele GPIO=',(adr*10+port) % 100, int(out))
                for I in range (NGPIO):
                    if Reles_SSR[I][1] == (adr*10+port) % 100:
                        out=int(out) #por ahora resolucion maxima de 1 
                        Reles_SSR[I][0].ChangeDutyCycle(100-out)
                        if out == 0 or out == 100:
                            pass
                            #Reles_SSR[I][0].ChangeFrequency(5)
                        elif out <= 50:
                            Reles_SSR[I][0].ChangeFrequency(out)
                        else:
                            Reles_SSR[I][0].ChangeFrequency(100-out)
                        break
            except:
                print ('Error rele GPIO')
                print (I, Reles_SSR[I][0],Reles_SSR[I][1], adr,port,out)         

    return

def logBD(texto) : # Incluir en tabla de Log
    global Nlog, minuto

    Nlog -=1
    if time.strftime("%H:%M") != minuto:
        minuto = time.strftime("%H:%M")
        Nlog = Nlog_max

    if Nlog > 0:
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
            y = round(adc.read_adc_difference(0, gain=16, data_rate=128) * 0.0078125 * SHUNT1, 2)  # A0-A1

        elif Ibat_sensor == 'HIBRIDO':
            
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Ibatp']) - float(d_hibrido['Ibatn'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        elif Ibat_sensor == 'VICTRON':
            dif = time.time()- float(d_victron['Tiempo_sg'])
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_victron['Iplaca'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        elif Ibat_sensor == 'VICTRON+HIBRIDO':
            dif1 = time.time()- float(d_hibrido['Tiempo_sg'])
            if dif1 < 10: # maximo 10 seg de diferencia para considerar dato valido
                y1 = float(d_hibrido['Ibatp']) - float(d_hibrido['Ibatn'])
            elif dif1 < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y1 = float(d_hibrido['Ibatp']) - float(d_hibrido['Ibatn'])
                logBD('lectura desfasada Ibat_hibrido='+str(y1))
            else:
                y1=0
                logBD('lectura MUY desfasada Ibat_hibrido=0')

            dif2 = time.time()- float(d_victron['Tiempo_sg'])
            if dif2 < 10: # maximo 10 seg de diferencia para considerar dato valido
                y2 = float(d_victron['Iplaca'])
            elif dif2 < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y2 = float(d_victron['Iplaca'])
                logBD('lectura desfasada Ibat_victron='+str(y2))
            else:
                y2=0
                logBD('lectura MUY desfasada Ibat_victron=0')
            y =y1+y2

    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Ibat')
    if y < ibat_min or y > ibat_max:
        logBD('lectura incoherente Ibat='+str(y))
        y = x
    return y

def leer_iplaca(x) :  # leer Iplaca
    global iplaca_shunt, iplaca_hibrido,iplaca_victron
    try:
        if Iplaca_sensor == 'ADS':
            y =  leer_iplaca_shunt(x)
            
        elif Iplaca_sensor == 'HIBRIDO':
            y =  leer_iplaca_hibrido(x)

        elif Iplaca_sensor == 'VICTRON':
            y =  leer_iplaca_victron(x)

        elif Iplaca_sensor == 'ADS+HIBRIDO':
            iplaca_shunt = leer_iplaca_shunt(iplaca_shunt)
            iplaca_hibrido = leer_iplaca_hibrido(iplaca_hibrido)
            y = iplaca_shunt + iplaca_hibrido

        elif Iplaca_sensor == 'VICTRON+HIBRIDO':
            iplaca_victron = leer_iplaca_victron(iplaca_victron)
            iplaca_hibrido = leer_iplaca_hibrido(iplaca_hibrido)
            y = iplaca_victron + iplaca_hibrido

    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca')
    if y < iplaca_min or y > iplaca_max:
        logBD('lectura incoherente Iplaca='+str(y))
        y = x
    if abs(y) < iplaca_error: y = 0.0
    
    return y

def leer_iplaca_shunt(x) :  # leer Iplaca del shunt
    try:
        y =  round(adc.read_adc_difference(3, gain=16, data_rate=128) * 0.0078125 * SHUNT2, 2)  # A2-A3
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca')
    if y < iplaca_min or y > iplaca_max:
        logBD('lectura incoherente Iplaca_ADS='+str(y))
        y = x
    #if abs(y) < iplaca_error: y = 0.0
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

def leer_iplaca_victron(x) :  # leer Iplaca del Victron
    try:
        dif = time.time() - float(d_victron['Tiempo_sg'])
        if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
            y = float(d_victron['Iplaca'])
        elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
            y = x
        else:
            y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Iplaca_victron')

    if y < iplaca_victron_min or y > iplaca_victron_max:
        logBD('lectura incoherente Iplaca_victron ='+str(y))
        y = x

    return y

def leer_vbat(x) :  # leer Vbat
    try:
        if Vbat_sensor == 'ADS':
            y = round(adc1.read_adc(0, gain=RES0_gain,data_rate=128) * 0.000125/RES0_gain * RES0, 2)  # A0   4,096V/32767=0.000125 

        elif Vbat_sensor == 'HIBRIDO':
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Vbat'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        elif Vbat_sensor == 'VICTRON':
            dif = time.time()- float(d_victron['Tiempo_sg'])
            if dif < 10: # maximo 5 seg de diferencia para considerar dato valido
                y = float(d_victron['Vbat'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Vbat')

    if y < vbat_min or y > vbat_max:
        logBD('lectura incoherente Vbat='+str(y))
        y = x
    return y

def leer_aux1(x) :  # leer Aux1
    try:
        if Aux1_sensor == 'ADS':
            y = round(adc1.read_adc(1, gain=RES1_gain,data_rate=128) * 0.000125/RES1_gain * RES1, 2)  # A0   4,096V/32767=0.000125 
        else:
            y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Aux1')
    if y < aux1_min or y > aux1_max:
        logBD('lectura incoherente Aux1='+str(y))
        y = x
    return y

def leer_aux2(x) :  # leer Aux2
    try:
        if Aux2_sensor == 'ADS':
            y = round(adc1.read_adc(3, gain=RES1_gain,data_rate=128) * 0.000125/RES1_gain * RES1, 2)  # A3   4,096V/32767=0.000125 
        else:
            y=0
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Aux2')
    if y < aux1_min or y > aux1_max:
        logBD('lectura incoherente Aux2='+str(y))
        y = x
    return y

def leer_vplaca(x) :  # leer Vplaca
    try:
        if Vplaca_sensor == 'ADS':
            y = round(adc1.read_adc(2, gain=RES2_gain,data_rate=128) * 0.000125/RES2_gain * RES2, 2)  # A0   4,096V/32767=0.000125 

        elif Vplaca_sensor == 'HIBRIDO':
            dif = time.time()- float(d_hibrido['Tiempo_sg'])
            if dif < 10: # maximo 10 seg de diferencia para considerar dato valido
                y = float(d_hibrido['Vplaca'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

        elif Vplaca_sensor == 'VICTRON':
            dif = time.time()- float(d_victron['Tiempo_sg'])
            if dif < 10: # maximo 5 seg de diferencia para considerar dato valido
                y = float(d_victron['Vplaca'])
            elif dif < 20: # maximo 20 seg de diferencia para considerar dato anterior
                y = x
            else:
                y=0

    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor Vplaca')
    if y < vplaca_min or y > vplaca_max:
        logBD('lectura incoherente Vplaca='+str(y))
        y = x
    return y

def leer_diver(x) :  # ANTIGUO.....leer estado excedentes
    if x == "AUX1":
        Aux1 = leer_aux1(0)
        if Aux1 > 1:
            Diver = 1
        else:
            Diver = 0
    elif x == "AUX2":
        Aux2 = leer_aux2(0)
        if Aux2 > 1:
            Diver = 1
        else:
            Diver = 0
    elif x == "VPLACA":
        Vplaca = leer_vplaca(0) # si error lectura devuelve 0
        Ibat = leer_ibat(-10)    # si error lectura devuelve -10
        if Vplaca > TP[5] and Ibat > -10: 
            Diver = 1
        else:
            Diver = 0
    else:
        Diver = 0
    return Diver

def leer_temp(x) :  # leer temperatura
    try:
        """
        tempfile= open(sensores[indice_sensortemperatura]) # chequear indice si se tienen instalados mas de un DS18B20
        thetext=tempfile.read()
        tempfile.close()
        tempdata = thetext.split("\n")[1].split(" ")[9]
        y = round(float(tempdata[2:]) / 1000,2)
        """
        with open('/run/shm/datos_temp.csv', mode='r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                d_temp = row # Capturo los valores del fichero datos_temp.csv
                
        y= float(d_temp['Temp'+str(indice_sensortemperatura)])
        
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

def Calcular_PID (sensor,objetivo,P,I,D):
    global Lista_errores_PID, IPWM_P, IPWM_I, IPWM_D
    
    valor = eval(sensor)
        
    # Desplazamos un elemento en la Lista de errores
    Lista_errores_PID = Lista_errores_PID[-1:] + Lista_errores_PID[:-1] 

    # Calculo Termino Proporcional PID
    if valor >= 0:
        error_actual = Lista_errores_PID[0] = valor - objetivo
    else:
        error_actual = Lista_errores_PID[0] = objetivo + valor


    # Calculo Termino Integral PID
    error_integral = 0
    for i in range(N-1):
        error_integral += (Lista_errores_PID[i]+Lista_errores_PID[i+1])/2/N
 
    # Calculo Termino Diferencial PID
    error_diferencial = Lista_errores_PID[0]-Lista_errores_PID[1]

    IPWM_P = P * error_actual
    IPWM_I = I * error_integral
    IPWM_D = D * error_diferencial

    #IPWM = P * error_actual + I * error_integral + D * error_diferencial
    IPWM = IPWM_P + IPWM_I + IPWM_D
    
    return IPWM
       
def Calcular_PWM(PWM):
    global Diver #,PWM
    
    Objetivo_PID= TP[5]   # Variable sensora de PID
    Diver = Calcular_PID (TP[6],Objetivo_PID,TP[7],TP[8],TP[9]) # 'sensor', objetivo, P,I,D 
    
    Diver_Max = 200 # Ya veremos si lo pongo en Parametros_FV.py
    if Diver > Diver_Max: Diver = Diver_Max
    elif Diver < -Diver_Max : Diver=-Diver_Max
    
    PWM += Diver
    
    if PWM >= PWM_Max: PWM = PWM_Max
    if PWM <= 0: PWM = 0

    #print ('Vbat={0:>5}'.format(Vbat) ,TP[6]+'={0:>5}'.format(round(eval(TP[6]),1)),
    #       ' -- PWM={0:>3} -- Incr={1:>4} -- Ibat={2:>6}'.format(round(PWM,0),round(Diver,1), round(Ibat,1)))
    return PWM

## RECUPERAR DE LA BD ALGUNOS DATOS ##
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql='SELECT DS, DATE(Tiempo),Whp_bat,Whn_bat,Wh_placa FROM datos ORDER BY id DESC limit 1'
    cursor.execute(sql)
    var=cursor.fetchone()
    DS=float(var[0])
    HOY=str(var[1])
    if HOY == time.strftime("%Y-%m-%d"): #Comprueba que es el mismo dia
        Whp_bat=float(var[2])
        Whn_bat=float(var[3])
        Wh_placa=float(var[4])
    else:
         Whp_bat = Whn_bat = Wh_placa = 0.0
except Exception as e:
    print ("Error, la base de datos no existe")

## Definir matrices Rele_Out y Rele_Out_Ant
Rele_Out = [[0] * 8 for i in range(50)]
Rele_Out_Ant = [[0] * 8 for i in range(50)] # Situacion actual y anterior de los reles

##  ------ inicializamos reles apagandolos  ------------------------
sql = 'SELECT * FROM reles'
nreles = cursor.execute(sql)
nreles = int(nreles)  # = numero de reles
TR = cursor.fetchall()

Reles_SSR = [ ]
NGPIO =0 # Num Reles GPIO

for I in range(nreles): #apagado fisico solo en Reles wifi
    Puerto = (TR[I][0] % 10) - 1
    addr = int((TR[I][0] - Puerto)/10)
    Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto] = 0
    if True: #int(addr/10) == 2: 
        act_rele(addr,Puerto+1,0)

    if int(TR[I][0]/100) == 4:
            NGPIO_PIN = TR[I][0] % 100
            print (NGPIO_PIN , TR[I][0] % 100)
      
            GPIO.setup(NGPIO_PIN, GPIO.OUT)
            Reles_SSR.append ([GPIO.PWM(NGPIO_PIN, 5),NGPIO_PIN])# 5hz
            
            print  ('NGPIO=',NGPIO, '- NGPIO_PIN=',NGPIO_PIN)
            Reles_SSR[NGPIO][0].start(0)
            NGPIO +=1


if nreles > 0 : # apagado reles en BD
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
if Vbat > 11 and Vbat < 15.5 : vsis = 1
elif Vbat > 22 and Vbat < 31 : vsis = 2
elif Vbat > 44 and Vbat < 62 : vsis = 4
else : log='Error: Imposible reconocer el voltaje del sistema'

Vflot = 13.7 * vsis
Vabs = 14.4 * vsis
Objetivo_PID = 15.2 * vsis #pongo un valor alto no alcanzable

print('Pulsa Ctrl-C para salir...')

log = ' Arrancando programa fv.py \nBateria = ' + str(Vbat) + 'v' + log
logBD(log) # incluyo mensaje en el log
if usar_telegram == 1:
    try:        
        pass
        #bot.send_message( cid, log)
    except:
        logBD("Error en Msg Telegram") # incluyo mensaje en el log


# Inicializo lista reles diver
Reles_D = [ ] 
for P in range(nreles):
    if TR[P][2] == 'PRG' and TR[P][6]!= 0:
       Reles_D.append([TR[P][0],TR[P][6],TR[P][5]]) #id_rele, prioridad, salto
Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1])
Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
PWM_Max = Nreles_Diver * 100

if DEBUG >= 100: print ('PWM_Max=',PWM_Max)

#########################################################################################
# -------------------------------- BUCLE PRINCIPAL --------------------------------------
#########################################################################################

#nbucle = consumo = 0
try:
    while True:
        #print ('Bucle',)
        cursor.close()
        db.close()
        ee=10

        t_muestra_7=time.time()-hora_m

        hora1=time.time()
        
      ### B1 ---------- Cargar tablas parametros, reles , reles_c, reles_h ---------------------
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()

        sql='SELECT * FROM parametros'
        nparametros=cursor.execute(sql)
        nparametros=int(nparametros)  # = numero de filas de parametros.---- debe ser 1
        TP=cursor.fetchone()
        
        Mod_bat = TP[10]
        Vflot = float(TP[11])
        Vabs = float(TP[12])
        Tabs_max = float(TP[13])
        Vequ = float(TP[14])
        Tequ_max = float(TP[15])
        
        
        sql='SELECT * FROM reles'
        nreles=cursor.execute(sql)
        nreles=int(nreles)  # = numero de reles
        TR=cursor.fetchall()

        sql='SELECT * FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele'
        fvcon=cursor.execute(sql)
        fvcon=int(fvcon)  # = numero de condiciones
        R=cursor.fetchall()


        sql='SELECT * FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele'
        hcon=cursor.execute(sql)
        hcon=int(hcon)  # = numero de condiciones horarias
        H=cursor.fetchall()

        sql='SELECT * FROM condiciones'
        ncon=cursor.execute(sql)
        ncon=int(ncon)  # = numero de condiciones
        TC=cursor.fetchall()
        
        ee=20
        t_muestra_8=time.time()-hora_m
      
      ### B2---------------------- LECTURA FECHA / HORA ----------------------
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        tiempo_us = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        diasemana = time.strftime("%w")
        hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
        
      ### ------------------------ CAPTURA PARAMETROS FV----------------------

        t_muestra_ant=t_muestra
        t_muestra=time.time()-hora_m
        hora_m=time.time()

        if t_muestra > t_muestra_max:
            #logBD('Tmuestra elevado='+str(round(t_muestra,1))+'sg DIVER='+str(int(Ndiver))+'/'+Tdiver)
            logBD('TmuestraX='+str(round(t_muestra_1,1))+'/'+str(round(t_muestra_2,1))+'/'+str(round(t_muestra_3,1))+'/'+str(round(t_muestra_4,1))+'/'+str(round(t_muestra_5,1))+'/'+str(round(t_muestra_6,1))+'/'+str(round(t_muestra_7,1))+'/'+str(round(t_muestra_8,1)))
       
        if DEBUG >= 2:
            print('T='+str(round(t_muestra_1,1))+'/'+str(round(t_muestra_2,1))+
              '/'+str(round(t_muestra_3,1))+'/'+str(round(t_muestra_4,1))+'/'+
              str(round(t_muestra_5,1))+'/'+str(round(t_muestra_6,1))+'/'+
              str(round(t_muestra_7,1))+'/'+str(round(t_muestra_8,1)),end='')
              
        if pub_time == 1:
            client.publish("PVControl/Opcion/Time",str(round(t_muestra_1,1))+'/'+str(round(t_muestra_2,1))+'/'+str(round(t_muestra_3,1))+'/'+str(round(t_muestra_4,1))+'/'+str(round(t_muestra_5,1))+'/'+str(round(t_muestra_6,1))+'/'+str(round(t_muestra_7,1))+'/'+str(round(t_muestra_8,1)))  # via MQTT

        if simular == 1:
            Ibat = random.choice([0,12,22,33,46,56,65,78,101,
                                -10,-20,-30,-40,-50,-60,-70,-80,-90])
            Iplaca = random.choice([0,10,20,30,45,57,67,77,88,99,102,110])
            Vbat = random.choice([22.5,23.7,24.0,24.4,25.5,26.3,27,27.5,28.2,29.1])
            Vplaca = random.choice([60,59.4,61,59.9,52,60.1,61.6,58.7,62,57.3])
            Wplaca = random.choice([600,590.40,610,590.90,520,600.10,610.60,580.70,620,570.30])
            Diver = random.choice([10,-10,11,20,-7,5,8,-8])  
            Temp = random.choice([10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux1 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Aux2 = random.choice([0,10,12,14,16,18,20,22,24,26,28,30,32,34])
            Consumo = Vbat * (Iplaca-Ibat)
            
        else:
            ee=30
            if usar_hibrido == 1:
                try:
                    with open('/run/shm/datos_hibrido.csv', mode='r') as f:
                        csv_reader = csv.DictReader(f)
                        for row in csv_reader:
                            d_hibrido = row # Capturo los valores del fichero datos_hibrido.csv
                except:
                    print ('Error, datos Hibrido no encontrados')
                    
            ee=32
            if usar_victron == 1:
                try:
                    with open('/run/shm/datos_victron.csv', mode='r') as f:
                        csv_reader = csv.DictReader(f)
                        for row in csv_reader:
                            d_victron = row # Capturo los valores del fichero datos_victron2.csv
                except:
                    print ('Error, datos victron no encontrados')
                    
            ee=34
            Ibat = leer_ibat(Ibat)
            Vbat = leer_vbat(Vbat)
            Iplaca = leer_iplaca(Iplaca)
            Vplaca = leer_vplaca(Vplaca)
            Aux1 = leer_aux1(Aux1)
            Aux2 = leer_aux2(Aux2)

            try:
                # evalua las expresiones definidas en Parametros_FV.py
                Consumo = float(eval (Consumo_sensor)) 
                Wplaca = float(eval(Wplaca_sensor))
            except:
                Consumo = 0
                Wplaca = 0

            if sensortemperatura == 1 and Ctemp <= 0:
                Temp = leer_temp(Temp)
                Ctemp=Mtemp # reinicio contador
                client.publish("PVControl/DatosFV/Temp",Temp)
                if DEBUG >= 100: print('Temp=',Temp,end='')
            else:
                Ctemp -= t_muestra # resto t_muestra

      ### ------------------ Control Excedentes...Cálculo salida PWM ----------
        ee=36
        PWM = Calcular_PWM(PWM)
        
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

        ### CALCULO Wh_BAT y Wh_PLACA
        hora_anterior=hora_actual
        hora_actual=time.strftime("%H")

        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        if dia_anterior != dia: #cambio de dia
            Wh_bat = Whp_bat = Whn_bat = Wh_placa = 0.0
            CD1 = CD2 = CD3 = CD4 = CD5 = 0.0
            Tbulk = Tflot = Tabs = Tflot_bulk= 0  #Tecu ??

        else:
            if Ibat < 0:
                Whn_bat = round(Whn_bat - (Ibat * Vbat * t_muestra/3600),2)
            else:
                Whp_bat = round(Whp_bat + (Ibat * Vbat * t_muestra/3600),2)

            Wh_placa = round(Wh_placa + (Wplaca * t_muestra/3600),2)

        ## -------- CALCULO SOC% A C20 ----------
        if Ibat < 0 :
            Ip1 = -Ibat 
            Ip1 = Ip1**CP 
            Ip1 = AH*Ip1

            Ip2 = AH / 20
            Ip2 = (Ip2**CP)*20
            Ip= -Ip1/Ip2
        else :
            Ip = Ibat * EC

        if (Ibat>0 and Ibat<0.005*AH and abs(Vbat-Vflot)<0.2) : DS = DS + (AH-DS)/50
        else : DS = DS + (Ip * t_muestra/3600)
        
        if DS > AH : DS = AH
        if DS < 0 :  DS = 0

        if TP[4] != 0: # Actualizo SOC si en la BD es distinto de 0
            DS = AH*TP[4]/100
            cursor.execute("UPDATE parametros SET nuevo_soc=0 WHERE id_parametros=1")
            db.commit()                
        SOC = round(DS/AH*100,2)
        
        ###########   Calculo Algoritmo de carga #############
        ee=38
        try:
            if Mod_bat == 'BULK':
                ee=38.1
                if Iplaca > 0: Tbulk += t_muestra
                
                if Vbat >= Vabs:# paso de Bulk a Abs
                    cursor.execute("UPDATE parametros SET Mod_bat='ABS'")
                    db.commit()
                    try:
                        if flag_Abs == 0 and usar_telegram == 1:
                            flag_Abs =1
                            logBD('Inicio ABS')
                            bot.send_message( cid, 'Inicio Absorcion')
                    except:
                        pass

            elif Mod_bat == 'FLOT': 
                ee=38.2
                if Vbat >= Vflot-0.2: Tflot += t_muestra
            
                # paso de Flot a Bulk
                if Vbat <= Vflot-4: Tflot_bulk += 1000
                elif Vbat <= Vflot-3: Tflot_bulk += 4 * t_muestra
                elif Vbat <= Vflot-2: Tflot_bulk += 2 * t_muestra
                elif Vbat <= Vflot-0.1: Tflot_bulk += t_muestra

                if Tflot_bulk > 10000: # Ver que tiempo se pone o si se pone como parametro
                    Tflot_bulk = Tabs = flag_Abs= 0
                    cursor.execute("UPDATE parametros SET Mod_bat='BULK'")
                    cursor.execute("UPDATE parametros SET objetivo_PID='"+str(Vabs)+"'")
                    db.commit()
                    try:
                        if flag_Flot == 1 and usar_telegram == 1:
                            flag_Flot = 0
                            logBD('Inicio BULK')
                            bot.send_message( cid, 'Inicio BULK')
                    except:
                        pass
            
            elif Mod_bat == 'ABS':
                ee=38.3
                if Vbat >= Vabs-0.1:Tabs += t_muestra
                
                elif Vbat < Vabs-0.2:# paso de Abs a Bulk
                    cursor.execute("UPDATE parametros SET Mod_bat='BULK'")
                    db.commit() 
                
                if Tabs >= Tabs_max: # paso de Abs a Flot
                    cursor.execute("UPDATE parametros SET Mod_bat='FLOT'")
                    cursor.execute("UPDATE parametros SET objetivo_PID='"+str(Vflot)+"'")
                    db.commit()
                    try:
                        if flag_Flot == 0 and usar_telegram == 1:
                            flag_Flot = 1
                            logBD('Inicio FLOT')
                            bot.send_message( cid, 'Inicio Flotacion')
                    except:
                        pass

            elif Mod_bat == 'EQU':
                ee=38.4
                if Vbat >= Vequ-0.2:
                    Tequ += t_muestra
                if Tequ >= Tequ_max:    
                    Tequ=0 
                    cursor.execute("UPDATE parametros SET Mod_bat='FLOT'")
                    db.commit() 
            ee=39
            if DEBUG >=3:
                print(' Tbulk={0:.2f} - Tabs={1:.2f} - Tflot={2:.2f}- Tflot_bulk={3:.2f}'.format(Tbulk,Tabs,Tflot,Tflot_bulk),end='')
                print (' Carga= {0}'.format(Mod_bat))
        except:
            print (tiempo,' Error algoritomo carga ',ee) 
            print(' Tbulk={0:.2f} - Tabs={1:.2f} - Tflot={2:.2f}- Tflot_bulk={3:.2f}'.format(Tbulk,Tabs,Tflot,Tflot_bulk),end='')
            print (' Carga= {0}'.format(Mod_bat))
            logBD('Err.Alg.Carga='+ str(ee)+ '==' + Mod_bat + '=' + str(Tabs) + '/' + str(Tflot) + '/' + str(Tflot_bulk))            
            
        
        ee=40
        if Grabar == 1: #publico cada t_muestra*N_muestras
            client.publish("PVControl/DatosFV/Ibat",Ibat)
            client.publish("PVControl/DatosFV/Iplaca",Iplaca)
            client.publish("PVControl/DatosFV/Vbat",Vbat)
            client.publish("PVControl/DatosFV/Vplaca",Vplaca)
            client.publish("PVControl/DatosFV/Wplaca",Wplaca)
            client.publish("PVControl/DatosFV/Aux1",Aux1)
            client.publish("PVControl/DatosFV/Aux2",Aux2)
            client.publish("PVControl/Reles/PWM", PWM)  # publico salida PWM
            client.publish("PVControl/DatosFV/SOC",SOC)
        
        t_muestra_2=time.time()-hora_m
        
      ## ------- Salida por pantalla OLED -------
        
        if NUM_OLED >= 1 and Grabar == 1: #OLED numero 1
            if OLED_salida_opcion1 < 0: # <0 es salida secuencial
                OLED(1,OLED_salida1[OLED_contador1])
                OLED_contador1 += 1
                if OLED_contador1 >= len(OLED_salida1):
                    OLED_contador1=0
            else:
                 OLED(1,OLED_salida_opcion1)

        if NUM_OLED == 2 and Grabar == 1: #OLED numero 2
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
        DatosFV['Aux1'] = Aux1
        DatosFV['Aux2'] = Aux2
        DatosFV['Temp'] = Temp
        DatosFV['Vplaca'] = Vplaca
        DatosFV['Wplaca'] = Wplaca
        DatosFV['Diver'] = Diver
        DatosFV['PWM'] = PWM

        # ----------------- Guardamos datos_fv.csv ------
        ee=42        
        with open('/run/shm/datos_fv.csv', mode='w') as f:
            """
            datos = csv.DictWriter(f, fieldnames=nombres_datos)
            datos.writeheader()
            datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Ibat': Ibat,'Vbat': Vbat,'SOC': SOC,
                            'DS':DS,'Aux1':Aux1,'Aux2':Aux2,'Whp_bat': Whp_bat,'Whn_bat':Whn_bat,
                            'Iplaca':Iplaca,'Vplaca':Vplaca,'Wplaca':Wplaca,'Wh_placa':Wh_placa,
                            'Temp':Temp,'PWM':PWM,'Mod_bat':Mod_bat})
            """
            f_writer = csv.writer(f,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)

            f_writer.writerow([round(tiempo_sg,2), tiempo,Ibat,Vbat,SOC,round(DS,2),Aux1,Aux2,
                               int(Whp_bat),int(Whn_bat),Iplaca,Vplaca,Wplaca,round(Wh_placa),
                               Temp,PWM,Mod_bat])
        ee=43
        with open('/run/shm/datos_reles.csv', mode='w') as f:
            f_writer = csv.writer(f,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
            for I in range(nreles):
                #print (TR[I][1],'-',TR[I][3])
                f_writer.writerow([TR[I][1],TR[I][3]])
            

      ## ------------------ ALGORITMO CONDICIONES RELES -----------------------------
        ee=50
        #### Cargamos los valores actuales de los reles  en Rele_Out_Ant####
        nwifi = 0
        for I in range(nreles): # Calculo Numero reles wifi y actualizo Rele_Out_Ant
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            Rele_Out_Ant[addr][Puerto] = Rele_Out[addr][Puerto]
            if int(addr/10) == 2: nwifi += 1
        
        if Grabar ==1 : #Cada t_muestra*n_muestras
            nwifi_lectura += 1 # Escritura de un unico rele wifi por ciclo
            if nwifi_lectura > nwifi: nwifi_lectura = 0    # para evitar colapsar al NodeMCU
            nwifi_lectura1 = 0
        
            if simular_reles == 0: #Lectura o Captura de los valores reales que estan en los reles
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
                    
                    elif int(addr/10) == 2: # Reles Wifi re-escritura un solo rele por ciclo
                        nwifi_lectura1 += 1
                        if nwifi_lectura == nwifi_lectura1:
                            try:
                                pass
                                client.publish("PVControl/Reles/"+str(addr)+str(Puerto+1),int(Rele_Out[addr][Puerto]))  # via MQTT
                                #print("--PVControl/Reles/"+str(addr)+str(Puerto+1),int(Rele_Out[addr][Puerto]))
                            except:
                                logBD('Rele ' + str(Puerto + 1) + ' en NodeMCU de direccion '+str(addr)+' NO ENCONTRADO')
                    
                    elif int(addr/10) == 4: pass

        #### Encendemos virtualmente y apagamos SI condiciones FV o HORARIAS no se cumplen####
        
        ee=52
        for I in range(fvcon): # enciendo reles con condiciones FV
            if R[I][6] == 0: # no actuo en reles de excedentes
                Puerto = (R[I][0] % 10) - 1
                addr = int((R[I][0]-Puerto) / 10)
                Rele_Out[addr][Puerto] = R[I][5] # pongo valor del salto
                #print ('enciendo condiciones FV - Rele',addr,Puerto+1,'=',Rele_Out[addr][Puerto])
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        ee=54
        for I in range(hcon): # enciendo reles con condiciones horario
            if H[I][6] == 0: # no actuo en reles de excedentes
                Puerto = (H[I][0] % 10)-1
                addr = int((H[I][0] - Puerto)/10)
                Rele_Out[addr][Puerto] = H[I][5] # pongo valor del salto
                #print ('enciendo condiciones Horario - Rele',addr,Puerto+1,'=',Rele_Out[addr][Puerto])
                
                # no me gusta... deberia ser al valor ant + salto y ver si no me paso de 100

        """
        for I in range(nreles): # Apago reles Diver
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            if TR[I][6] != 0: Rele_Out[addr][Puerto] = 0 #Rele_Out_Ant[addr][Puerto]
           
        for I in range(nreles):   
            # Situacion reles antes de condiciones
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
                    
            print ('Antes condiciones - Rele',addr,Puerto+1,'=',Rele_Out[addr][Puerto])
        """
        # -------------------- Bucle de condiciones de horario --------------------------
        ee=56
        Rele_Out_H = [[0] * 8 for i in range(50)] # Inicializo variable a 0

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
                # deberia ser quitar salto y ver que no me paso de 0
                
                Rele_Out_H[addr][Puerto] = -1 # para quitar posibilidad de ser rele Diver en el ciclo

        """
        for I in range(nreles): # ver reles tras Condiciones Hora 
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            
            #print ('Despues Condiciones Hora- Rele',addr,Puerto+1,'=',Rele_Out[addr][Puerto], 'Out_H=',Rele_Out_H[addr][Puerto])
        """

        # -------------------- Bucle de condiciones de parametros FV --------------------------
        ee=58
        for I in range(fvcon):
            Puerto = (R[I][0] % 10) - 1   
            addr = int((R[I][0] - Puerto) / 10)

            if R[I][OP['condicion']] == '<':
                if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] > R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                    Rele_Out[addr][Puerto] = 0
                    # deberia ser quitar salto y ver que no me paso de 0
                    
                if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] <= R[I][OP['valor']] :
                    Rele_Out[addr][Puerto] = 0

            if R[I][OP['condicion']] == '>':
                if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] < R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                    Rele_Out[addr][Puerto] = 0
                if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] >= R[I][OP['valor']] :
                    Rele_Out[addr][Puerto] = 0

        # -------------------- Bucle de condiciones  --------------------------
        ee=60
        for I in range(ncon):
            try:
                #print (I,CD1,TC[I][0],TC[I][1],TC[I][2],(eval(TC[I][0])and eval(TC[I][1])))
                if (eval(TC[I][0])and eval(TC[I][1])):
                    #print( 'Ejecutando ',TC[I][2])                
                    exec(TC[I][2]) 
            except:
                logBD('Error en id_condicion='+str(TC[I][3]))

        #-------------------- Bucle encendido/apagado reles ------------------------------------
        ee=62
        Flag_Rele_Encendido = 0
        for I in range(nreles):
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)

            ### forzado ON/OFF
            if TR[I][OP['modo']] == 'ON' :
                Rele_Out[addr][Puerto] = 100
                
            if TR[I][OP['modo']] == 'OFF' :
                Rele_Out[addr][Puerto] = 0

            #print ('Despues Condiciones FV - Rele',addr,Puerto+1,'=',Rele_Out[addr][Puerto], 'Ant=',Rele_Out_Ant[addr][Puerto], ' Flag=',Flag_Rele_Encendido)
            

            ### dejar rele como esta     
            if Rele_Out[addr][Puerto] == 100 and Rele_Out_Ant[addr][Puerto] < 100 and Flag_Rele_Encendido == 1 : 
                Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto]      #dejar rele en el estado anterior


            ### encender rele
            if Rele_Out[addr][Puerto] == 100 and Flag_Rele_Encendido == 0 and Rele_Out_Ant[addr][Puerto] < 100 :
                Flag_Rele_Encendido = 1
                print (tiempo,' - Enciendo rele ',addr,Puerto+1)
                act_rele(addr,Puerto+1,100)

            ### apagar rele
            if Rele_Out[addr][Puerto] == 0 and Rele_Out_Ant[addr][Puerto]>0: # and TR[I][6]== 0:
                print (tiempo,' - Apago rele ',addr,Puerto+1)
                act_rele(addr,Puerto+1,0) #apagar rele
        
      ## --------- BUCLE DIVER + ACTIVACION RELES CONTROL DE EXCEDENTES -------------
        t_muestra_3=time.time()-hora_m
        
        ee=100
        if PWM >=0: # esto siempre se debe cumplir
            Reles_D = [ ] # inicializo lista reles diver
            for P in range(nreles):
                Puerto = (TR[P][0] % 10) - 1
                addr = int((TR[P][0] - Puerto) / 10)

                if TR[P][2] == 'PRG' and TR[P][6]!= 0 and Rele_Out_H[addr][Puerto] != -1 and Flag_Rele_Encendido != 1:
                   Reles_D.append([TR[P][0],TR[P][6],TR[P][5]]) #id_rele, prioridad, salto

            Reles_D_Ord = sorted(Reles_D, key=lambda rr: rr[1]) # Ordeno lista reles por prioridad
            
            Nreles_Diver = len(Reles_D_Ord) # Nº de reles Diver a considerar para reparto excedentes
            PWM_Max= Nreles_Diver * 100
            
            #print ('Reles diver=',Nreles_Diver)
            #print (Reles_D_Ord)
            
            if Nreles_Diver > 0:
                # Repartimos PWM entre los reles
                PWM_R = PWM
                for P in range(Nreles_Diver):
                    Puerto = (Reles_D_Ord[P][0] % 10) - 1
                    addr = int((Reles_D_Ord[P][0] - Puerto) / 10)
                    
                    valor = min(100,PWM_R)
                    salto = Reles_D_Ord[P][2]
                    
                    Rele_Out[addr][Puerto] =  int(salto * round(valor/salto))
                    
                    if Rele_Out[addr][Puerto] != Rele_Out_Ant[addr][Puerto]:
                        act_rele(addr,Puerto+1,Rele_Out[addr][Puerto])
                        #Rele_Out_Ant[addr][Puerto]=Rele_Out[addr][Puerto]
                    
                    PWM_R -= Rele_Out[addr][Puerto]
                    PWM_R = max(0,PWM_R)
                    #print('Rele',Reles_D_Ord [P][0],Rele_Out[addr][Puerto],int(PWM_R))
                #print('.....................')
                


      ## --------- Escribir en la BD Tabla Reles el Estado RELES -------------------------
        t_muestra_4=time.time()-hora_m
        ee=200
        if TP[1] == "S" and Grabar == 1 and nreles > 0:
            for I in range(nreles):
                Puerto = (TR[I][0] % 10) - 1
                addr = int((TR[I][0] - Puerto) / 10)
                id_rele = TR[I][0]
                estado = Rele_Out[addr][Puerto]
                sql = ('SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha='+
                      '"'+time.strftime("%Y-%m-%d")+'" and id_rele =' + str(id_rele))
                try:
                    nreles_on = cursor.execute(sql)
                    nreles_on = int(nreles_on)
                    if estado > 0 :
                        segundos_on = float(TP[2] * TP[3])
                        nconmutaciones = 1

                        if nreles_on >= 1:
                            TS = cursor.fetchall()
                            
                            segundos_on = TS[0][1] + round((t_muestra*TP[3]*estado/100),2)  # calculo funcionamiento real reles PWM
                            if TR[I][3] == 0:
                                nconmutaciones = TS[0][2] + 1
                            else:
                                nconmutaciones = TS[0][2]
                            sql = ("UPDATE reles_segundos_on SET segundos_on =" +str(segundos_on)+
                                   ",nconmutaciones =" + str(nconmutaciones)+ " WHERE id_rele = " +
                                   str(id_rele) + ' and fecha = "' + time.strftime("%Y-%m-%d") +'"')
                            cursor.execute(sql)
                        else :
                            cursor.execute("""INSERT INTO reles_segundos_on
                                            (id_rele,fecha,segundos_on,nconmutaciones)
                                            VALUES (%s,%s,%s,%s)""",
                                            (id_rele,time.strftime("%Y-%m-%d"),segundos_on,1))

                    
                    if Rele_Out[addr][Puerto] != TR[I][3]:
                        #print ('estado rele',addr,Puerto,'==',TR[I][3],Rele_Out[addr][Puerto],str(estado))
                        sql = "UPDATE reles SET estado =" +str(estado)+ " WHERE id_rele = " + str(id_rele)
                        cursor.execute(sql)
                        #db.commit()

                except:
                    db.rollback()
                    print ('Error grabacion Reles_segundos_on',ee)
                    logBD('Error grabacion Reles_segundos_on')
                    
                if TP[1] == "S" and Grabar == 1 and TR[I][4] == "S" and Rele_Out[addr][Puerto] != TR[I][3]:
                    try:
                        cursor.execute("""INSERT INTO reles_grab (Tiempo,id_rele,valor_rele)
                                       VALUES(%s,%s,%s)""",(tiempo,TR[I][0],estado))
                        #db.commit()
                    except:
                        db.rollback()
                        logBD('tabla reles_grab NO grabados por fallo')


        #------------------------Escribir en la tabla valores FV  ---------------------------
        
        if TP[0] == "S" and Grabar == 1:
            if DEBUG >=2: print ('G',end='')
            try:
                cursor.execute("""INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat))
                #db.commit()
            except:
                db.rollback()
                logBD('Registro DATOS no grabado')
        #else :
            #db.commit()
            #print ("registro DATOS NO grabado")

        if TP[0] == "S" and eval(grabar_datos_s): #grabar datos_s 
            if DEBUG >=2: print ('S',end='')
            try:
                cursor.execute("""INSERT INTO datos_s (Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,
                   Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,
                   IPWM_P,IPWM_I,IPWM_D,Kp, Ki,Kd) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (tiempo_us,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,
                   Wplaca,Wh_placa,Temp,PWM,IPWM_P,IPWM_I,IPWM_D,TP[7],TP[8],TP[9]))
                db.commit()
            except:
                db.rollback()
                logBD('Registro datos_s no grabado')
        else :
            db.commit()

      ## ------------------------------------------------
        
        t_muestra_5=time.time()-hora_m

        Grabar += 1
        if Grabar >= TP[3] + 1: Grabar = 1

        #hora2 = time.time()
        ###### ajuste fino tiempo bucle=0.10
        T_ejecucion = round(time.time() - hora1,2)

        if T_ejecucion_max < T_ejecucion: T_ejecucion_max = T_ejecucion

        if DEBUG >= 1:
            #print (tiempo,'-',end='')
            print(' {0:.2f}sg - Sensor={1}={2:.2f}'.format(T_ejecucion,TP[6],TP[5]),end='')
            print (' / Vbat={0:.2f}- Iplaca={1:.2f}- Ibat={2:.2f}- Wcon={3:.2f}- PWM={4:.0f}'.format(Vbat,Iplaca,Ibat,Consumo,PWM))

        # Repetir bucle cada X segundos
        espera = TP[2] - T_ejecucion #-0.1
        if espera > 0: time.sleep(espera)
        t_muestra_6=time.time()-hora_m


except:
    print()
    print ('Error en bucle fv',ee)
    for I in range (NGPIO):
        print (I)
        Reles_SSR[I][0].stop()
finally:
    GPIO.cleanup()    
