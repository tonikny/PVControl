#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-09-22

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_mqtt'
control = 'usar_mqtt'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import MySQLdb,json,time
import paho.mqtt.client as mqtt

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_mqtt') #+Style.RESET_ALL)


#Comprobacion argumentos en comando 
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
print (Fore.RED + 'DEBUG=',DEBUG)

# -----------------------MQTT MOSQUITTO ------------------------
Nmensajes= 0

def on_connect(client, userdata, flags, rc):
    for i in mqtt_suscripciones:
        print ('Topic =',i)
        client.subscribe(i)
    
     
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Desconexion MQTT - Intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global DATOS_MQTT, Nmensajes
    
    #print(msg.topic+" "+str(msg.payload))
    Nmensajes += 1
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    #print (Fore.BLUE,tiempo, ' - Mensajes=',Nmensajes)
    
    try:
        DATOS_MQTT[msg.topic] = json.loads(msg.payload)
    except:
        pass
    
    if DEBUG == 100: print (Fore.BLUE+'DATOS_MQTT=',DATOS_MQTT)
    
    #### REGISTRO EN BD ############
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
    except:
        print(Fore.RED+'error, BD', Sql)
    
    ####  ARCHIVOS RAM en BD ############ 
    try:
            
        salida = json.dumps(DATOS_MQTT)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'MQTT'") # grabacion en BD RAM
        cursor.execute(sql)            
    except:
        print(Fore.RED+'error, Grabacion tabla RAM equipos')
    
    db.commit()
    cursor.close()
    db.close()
    
client = mqtt.Client("fv_mqtt") #crear nueva instancia
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


DATOS_MQTT = {} # Diccionario de los datos recibidos por MQTT
dia = time.strftime("%Y-%m-%d")

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try: #inicializamos registro en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('MQTT','{}'))
        db.commit()
    except:
        pass
except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()

# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================

while True:
    print (Fore.GREEN,time.strftime("%Y-%m-%d %H:%M:%S"), ' - Mensajes=',Nmensajes)
    time.sleep(60)  
