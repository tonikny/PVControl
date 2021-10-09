#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt

###### Parametros ############################
servidor = '192.168.1.15'
usuario = 'rpi'
clave = 'fv'
openevse_reset="openevse/rapi/in/$FR"
openevse_ACK="openevse/rapi/out"
sleep_evse=0
delay=3

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+"\n")
    client.subscribe(openevse_ACK)


def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            client.loop_stop()
            client.disconnect()


def on_message(client, userdata, msg):
    print (msg.topic,msg.payload)


client = mqtt.Client("openevse_reset") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(usuario, password=clave)
try:
    client.connect(servidor, 1883) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.5)
client.loop_start()


try:
#    while True:
    client.publish(openevse_reset)
    time.sleep(delay)

except:
    print ("exiting")
    client.loop_stop()
    client.disconnect()

