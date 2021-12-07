#!/usr/bin/python
# -*- coding: utf-8 -*-

# 19/Nov/2021

import sys,time
import paho.mqtt.client as mqtt


#from Parametros_FV import *


# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    pass
    #print("Connected with result code "+str(rc))
    #client.subscribe("PVControl/Hibrido")
    #client.subscribe("PVControl/Hibrido/Opcion") # Ya vere para que
    
 
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            #print "Desconexion MQTT"
            client.loop_stop()
            client.disconnect()


tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
print (tiempo,end='-')


###### MQTT
mqtt_broker ='localhost'
mqtt_puerto = 1883
mqtt_usuario = 'rpi'
mqtt_clave = 'fv'

client = mqtt.Client("crontabhibrido") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()

# -------------------------------- BUCLE PRINCIPAL --------------------------------------
#print "10"

salir=False
N=1
Nmax=3
narg = len(sys.argv)
print ('Nº de Argumentos = ',sys.argv)
time.sleep(1)
               
while salir!=True and N<Nmax:
    try:
        for i in range (1,narg):
            msg =  str(sys.argv[i])
            print (f' Comando enviado {msg}', end='-- ')
            if msg[0].isnumeric():
                print('publico PVControl/Hibrido'+msg[0],msg[1:])
                client.publish('PVControl/Hibrido'+msg[0],msg[1:])
            else:
                print('publico PVControl/Hibrido',msg)
                client.publish('PVControl/Hibrido',msg)
           
            #print "20"
            #client.publish('PVControl/Hibrido',msg)
            #print "21"
            time.sleep(5)

        salir=True
    except:
        print ('error')
        salir=False
        time.sleep(60)
        N=N+1
        print ('N=',N)

#print "30"
client.disconnect()
#print "31"
print()
time.sleep(3)
