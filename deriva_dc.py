#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2024-04-19

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

########## Valores por defecto si no hay nada en Parametros_FV.py  ###########
usar_deriva_dc = 0
#rele_deriva_dc = 209

baudrate_deriva_dc = 9600
parity_deriva_dc = 'N'
port_deriva_dc ='/dev/ttyACM0'
timeout_deriva_dc = 1



simular_deriva_dc = 0    

##############################################  
EQUIPO = 'DERIVA_DC'

# #################### Control Ejecucion Servicio ########################################
servicio = 'deriva_dc'
control = 'usar_deriva_dc'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


import MySQLdb,json,time
import paho.mqtt.client as mqtt
import json
import telebot # Librería de la API del bot.

import serial
import struct

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_deriva_dc') #+Style.RESET_ALL)

# Se abre el puerto serie al principio antes de conexion MQTT
P_res=0
Nmensajes= 0

if simular_deriva_dc == 0:
    
    try:
        ser = serial.Serial()
        ser.baudrate = baudrate_deriva_dc
        ser.parity = parity_deriva_dc
        ser.port = port_deriva_dc
        ser.timeout = timeout_deriva_dc
        ser.open()
        
        while ser.isOpen() == False:
            time,sleep(0.01)
        ser.flushInput()
        ser.flushOutput()   
        ser.write(b'\t\x00\t7') #'\X09\X0\X09\X37'
        rcv = ser.read(2) #?? no, deriva_dc no va a contestar, algo real 09 0 09 55
        print('lactura inicial=',rcv)
        time.sleep(0.3)
        
    except:
        print(Fore.RED+f'ERROR en apertura puerto serie {port_deriva_dc}')
    
else:
    print(Fore.YELLOW + '=' * 50)
    print (Fore.BLUE +'      Simulando comunicacion deriva_dc...')
    print (Fore.YELLOW + '=' * 50 + Fore.RESET)


#Comprobacion argumentos en comando
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print (Fore.RED + 'DEBUG=',DEBUG)

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try: #inicializamos registro en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      (EQUIPO,'{}'))
        db.commit()
    except:
        pass
    cursor.close()
    db.close()    

except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()

# -----------------------MQTT MOSQUITTO ------------------------

DATOS = {} # Diccionario de los datos recibidos por MQTT

def on_connect(client, userdata, flags, rc):
    # TOPIC a los que se suscribe
    for t in  range (202, 214): 
        client.subscribe(f"PVControl/Reles/{t}")
    
     
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Desconexion MQTT - Intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

##################################################################
########  Funcion que se ejecuta al recibir un mensaje MQTT  #####
##################################################################
def on_message(client, userdata, msg): # 
    global DATOS, Nmensajes #,ser
    
    topic = msg.topic
    
    nrele = int(topic[-3:]) 
    
    mensaje = msg.payload.decode() # pasa de byte a texto
    
    if DEBUG == 100: client.publish(f'PVControl/Reles/{nrele}/Rec',int(mensaje)) #publico mensaje recibido
    
    #print(topic+" --"+ mensaje)
    
    Nmensajes += 1
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        DATOS[nrele] = json.loads(mensaje) # por si en un futuro se pasa un diccionario
    except:
        pass
    
    if DEBUG == 100:
        print (Fore.RESET + '=' * 80 )
        print (tiempo+ Fore.YELLOW +' - Nuevo Mensaje para rele: '+Fore.RED+f' {nrele} ' + Fore.YELLOW + f'duty:{mensaje}')
  
  
    # Calculo de valores a pasar al deriva_dc
    try:
        data = [0,0,0,0]
        data[0] = nrele-200  # Pin digital en deriva_dc?       
        data[1] = int(mensaje) # Valor duty 
        data[2] = data[0]+data[1]  # Check 
        data[3]=  55               # Check 
    except:
        print('error en data')
        return
        
    Iplaca = 0 # inicializo variable
    
    # Gestionar comunicacion serie
    if ser.isOpen() == True:
        ee = 5
        dat = serial.to_bytes(data)
        
        if DEBUG == 100: print(Fore.RESET + f'data={data} ==> dat={dat} ')
        #for i in range(0,4): print(f'dat{i}= {dat[i]} : {type(dat[i])} ---', end='')
        
        ser.write(dat)
        
        time.sleep(0.5)

        try:
            ee= 10
            rcv = ser.read(2)
            time.sleep(0.1)
            
            if DEBUG == 100: print (f'rcv={rcv}')
            ee= 15
            resp = struct.unpack(">H",rcv)
            ee=20
            intensidad = resp[0]/64*5/1023 
            intensidad = (2494 - intensidad * 1000)/66
            ee=30
            Iplaca = round(intensidad,1)     
            if Iplaca < 0 : Iplaca = 0
            
            
            if DEBUG == 100: print(f'Iplaca= {Iplaca}')
        except:
            print(f'error lectura {ee}')
                
    else:
        print('puerto serie cerrado... esperando apertura...')          
    
    
    if Nmensajes < 2 : 
        print(Fore.YELLOW + 'Primera lectura...no se considera'+Fore.RESET)
        return
    
    DATOS['Iplaca'] = Iplaca
  
    ####  ARCHIVOS RAM en BD ############ 
    try:            
        if DEBUG == 100: print (DATOS)
    
        salida = json.dumps(DATOS)
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{EQUIPO}'") # grabacion en BD RAM
        cursor.execute(sql)
        
    except:
        print(Fore.RED+f'error, Grabacion tabla RAM equipos -- {DATOS}')
        sys.exit()
    db.commit()
    cursor.close()
    db.close()
    

## MOSQUITTO
client = mqtt.Client("fv_deriva_dc") #crear nueva instancia
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

"""
# TELEGRAM
bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages
"""

# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================

while True:
    if simular_deriva_dc == 0 and ser.isOpen()==False:
        try:
            print('Reconectando puerto serie...')
            ser.close()
            ser.flushInput()
            ser.flushOutput()
            
            time.sleep(1)
            ser.open()
            time.sleep(1)
        except:
            print('Error en conexion puerto serie')
            
    print (Fore.GREEN,time.strftime("%Y-%m-%d %H:%M:%S"), ' - Mensajes=',Nmensajes)

    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios

    time.sleep(60)   # cada 60sg vemos ser.isOpen
