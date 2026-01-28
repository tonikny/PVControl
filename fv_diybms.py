#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-01
#
#

# #################### Control Ejecucion Servicio ########################################
equipo = 'diy_bms'
servicio = 'fv_diybms'
control = 'usar_diybms'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import time,datetime
import MySQLdb
import json
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

###### Parametros ############################
delay=5
diy_status=0
encoded_data={}
decoded_data={}
aux1=[0]*usar_diybms
mux1=[0]*usar_diybms
minimo=[0]*usar_diybms
maximo=[0]*usar_diybms
DatosMux= {}

equipo1='BMS_DIY'

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+"\n")

    client.subscribe("diybms/0/#")
    client.subscribe("diybms/status")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")
    else:
        client.loop_stop()
        client.disconnect()


def on_message(client, userdata, msg):
    global diy_status,decoded_data,mux1

    if msg.topic[:8] == "diybms/0":
       celda = int(msg.topic[9:])
       decoded_data[celda]=json.loads((msg.payload).decode())
       aux1[celda] = float(decoded_data[celda]['voltage'])
       if aux1[celda] != 0:
           mux1[celda] = aux1[celda]
       minimo[celda] = float(decoded_data[celda]['vMin'])
       maximo[celda] = float(decoded_data[celda]['vMax'])

    elif msg.topic == "diybms/status":
       diy_status=str(msg.payload)

    else:
       print (msg.topic,msg.payload)


# ----------------------- MOSQUITTO ------------------------
client = mqtt.Client("BMS2_mqtt") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, port=mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.5)


db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()
# Inicializo registros de los equipo en tabla ...lo logico ponerlo antes del bucle de captura
try:
    cursor.execute(f"INSERT INTO equipos (id_equipo,sensores) VALUES ('{equipo1}','{{}}')")
except:
    cursor.execute(f"UPDATE equipos SET sensores = '{{}}' WHERE id_equipo = '{equipo1}'")
db.commit()

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    Sql = """
    CREATE TABLE IF NOT EXISTS `datos_celdas` (
    `id_celda` int(11) NOT NULL AUTO_INCREMENT,
    `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
    `C1` float NOT NULL DEFAULT 0,
     PRIMARY KEY (`id_celda`),
     KEY `Tiempo` (`Tiempo`)
     )
     ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
     """
    cursor.execute (Sql)

    Sql='SELECT * FROM datos_celdas LIMIT 1' 
    nreg=cursor.execute(Sql)
    ncel = len(cursor.description) - 2 # Nº de celdas declaradas en BD

    if ncel < usar_diybms:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se crean nuevos campos en tabla datos_celdas")
        print ("-" * 50)
        for K in range(usar_diybms):
            try:
                Sql = f"ALTER TABLE `datos_celdas` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                print (Fore.RED,f'Campo de celda C{K+1} creado')
            except:
                print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
    elif ncel > usar_diybms:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        for K in range(usar_diybms,ncel):
            try:
                Sql = f"ALTER TABLE `datos_celdas` DROP `C{K+1}`"
                cursor.execute(Sql)
                db.commit()
                print (Fore.RED,f'Campo de celda C{K+1} borrado')
            except:
                print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
    cursor.close()
    db.close()


    key = [ f'C{i+1}' for i in range(usar_diybms)]
    #print (key)
    campos = ",".join(key)
    #print (campos)

except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()


client.loop_start()
try:
    while True:

        time.sleep(delay)
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")


        # Insertar Registro en BD
        try:
             db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
             cursor = db.cursor()
             valores = "','".join(str(v) for v in mux1)

             # Empezaremos a grabar cuando tengamos todas las tensiones de las celdas
             grabar = 1
             for v in range(usar_diybms):
                 if mux1[v] == 0:
                    grabar = 0

             if grabar == 1:
                 Sql= "INSERT INTO datos_celdas (Tiempo,"+ campos +") VALUES ('"+ tiempo +"','"+valores+"')"
                 cursor.execute(Sql)
                 db.commit()


        except:
             print()
             db.rollback()
             logBD('Registro MUX no grabado')


        ####  ARCHIVOS RAM en BD ############
        datos = {'Nombre' : key,'Max' : maximo,'Vceldas' : mux1,'Min' : minimo}
        salida = json.dumps(datos)
        try:
            cursor.execute(f"UPDATE equipos SET tiempo = '{tiempo}',sensores = '{salida}' WHERE id_equipo ='{equipo1}'")
            db.commit()
        except:
            print()


except:
    print("Exit")
    client.loop_stop()
    client.disconnect()

