#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-02-01

"""
Programa que sirve para publicar en cualquier Broker MQTT valores que esten en la tabla equipos de la base de datos

Este programa NO USA los datos de Parametros_FV.py por lo que se debe dar de alta los valores 
de conexion a la BD y Broker MQTT que se quiera usar

"""

###### DATOS A CONFIGURAR #########

usar_mqtt_publicaciones = 0     # 1 = Publica por MQTT los topic definidos en mqtt_publicaciones...... 0= No publica por MQTT  


# se debe reiniciar el servicio despues de realizar cambios....
# sudo systemctl restart fv_mqtt_publicar_externo

####### BD #######
servidor = "localhost" 
usuario = "rpi"
clave = "fv"
basedatos = "control_solar"

####### MQTT #######
mqtt_broker = "192.168.1.10"
mqtt_puerto  = 1883
mqtt_usuario = "rpi"
mqtt_clave   = "fv"
mqtt_cliente = "mqqt_ext" # poner cualquier nombre unico para el broker MQTT

# ---- Publicaciones -----
mqtt_topic_raiz = "PVControl/"  # Raiz del topic a publicar

#  Tuplas [Nombre Topic, Variable, frecuencia en sg (0 deshabilita, por defecto = t_muestra)]
t_muestra = 5
mqtt_publicaciones = [
                      ["Bat_Grises","d_['FV']"],
                      ["Bat_Grises/Celdas","d_['CELDAS']['Valor']"]
                     ] 

####### FIN CONFIGURACION ##########

import sys, subprocess

if usar_mqtt_publicaciones == 0:
    print (subprocess.getoutput('sudo systemctl stop fv_mqtt_publicar_externo'))
    sys.exit()

import time,MySQLdb 

import json
import paho.mqtt.client as mqtt

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' Pub.Bat.Grises ') #+Style.RESET_ALL)

basepath = '/home/pi/PVControl+/'

d_ = {} #Diccionario Equipos
    
#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
DEBUG= 0
if '-p' in sys.argv: DEBUG= 100 
 
print (Fore.RED + f'DEBUG={DEBUG}' +Fore.GREEN)

## Comprobacion inicial de que existe tabla equipos en la BD
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try:
        sql = 'SELECT * FROM equipos'
        nequipos = int(cursor.execute(sql))
        for row in cursor.fetchall():
            d_[row[0]] = json.loads(row[2])
            print('-' * 80)
            print (row[0],'=',d_[row[0]])
    except:
        print (Fore.RED+'Error lectura tabla equipos')

except:
    print (Fore.RED,'ERROR inicializando tabla equipos... abortando PVControl+')
    sys.exit()

# ------------------ INICIO BROKER MQTT MOSQUITTO ------------------------

def on_connect(cli, userdata, flags, rc):
    print(f"Conectado a Broker {mqtt_broker } codigo {rc}")
    #cli.subscribe("PVControl/Log")
    #cli.subscribe("PVControl/Opcion")
     
def on_disconnect(cli, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")
    else:
        cli.loop_stop()
        cli.disconnect()

             
client = mqtt.Client(mqtt_cliente) #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()


#########################################################################################
# -------------------------------- BUCLE PRINCIPAL --------------------------------------
#########################################################################################

try:
    while True:
        ee=10.0
        t_bucle =time.time()       
              
      ### ---------------------- LECTURA FECHA / HORA ----------------------
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
        
        ### ------------------------ CAPTURA PARAMETROS FV----------------------

        ## Capturando valores desde BD en tabla equipos
        ee=30.1
        sql = 'SELECT * FROM equipos'
        nequipos = int(cursor.execute(sql))

        d_={}
        try:
            for row in cursor.fetchall(): d_[row[0]] = json.loads(row[2])
        except:
            print ('Error Lectura Tabla equipos')
            time.sleep(5)    
                
        ###### PUBLICACION MQTT ##########
        ee = 340.0
        try:
            tm1= tiempo_sg
            if usar_mqtt_publicaciones == 1:
                ee = 340.1
                for tm in mqtt_publicaciones:
                    ee = 340.2
                    if len(tm) == 3: tm2 =tm[2]
                    else: tm2 = t_muestra
                    ee = 340.3
                    
                    if tm2 != 0:
                        if tm1 % tm2 < t_muestra:
                            ee = 340.4
                            datos = f'{eval(tm[1])}'
                            
                            if datos[0] == '{':
                                td = "json.dumps(" + tm[1] + ")" 
                            else:
                                td = tm[1]
                                
                            datos = f'{eval(td)}'
                            if DEBUG == 100:print(Fore.CYAN+f' {hora} -  topic:{mqtt_topic_raiz}{tm[0]} = {datos}'+Fore.RESET)
                            
                            client.publish(f'{mqtt_topic_raiz}{tm[0]}',f'{datos}')
                            
        except:
            print (f'Error {ee} en Publicacion MQTT')
            
        ###### ajuste fino tiempo bucle
        t_ejecucion = round(time.time() - t_bucle,2)
    
        # Repetir bucle cada t_muestra segundos
        espera = t_muestra - t_ejecucion #-0.1
        if espera > 0: time.sleep(espera)
        
except:
    print()
    print ('Error en bucle',ee)
    try:
        cursor.close()
        db.close()
    except:
        pass    
    
