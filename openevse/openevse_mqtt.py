#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt

###### Parametros ############################
servidor = '192.168.1.15'
usuario = 'rpi'
clave = 'fv'
openevse_current="openevse/rapi/in/$SC"
openevse_disable="openevse/rapi/in/$FD"
openevse_enable="openevse/rapi/in/$FE"
mode="Auto"
max_current=25
max_current_diver0=13
min_current=6
current=13
ibat=0.0
soc=0.0
diver=0
sleep_evse=0
delay=3

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+"\n")
    client.subscribe("PVControl/DatosFV/Ibat")
    client.subscribe("PVControl/DatosFV/SOC")
    client.subscribe("PVControl/Reles/Diver")
    client.subscribe("PVControl/Reles/EvseMode")


def on_disconnect(client, userdata, rc):
        if rc != 0:
            print "Unexpected MQTT disconnection. Will auto-reconnect"
        else:
            client.loop_stop()
            client.disconnect()


def on_message(client, userdata, msg):
    global diver,ibat,soc,mode

    if msg.topic == "PVControl/Reles/Diver":
       diver=str(msg.payload)
       diver=int(diver)
    elif msg.topic == "PVControl/DatosFV/Ibat":
       ibat=str(msg.payload)
       ibat=float(ibat)
    elif msg.topic == "PVControl/DatosFV/SOC":
       soc=str(msg.payload)
       soc=float(soc)
    elif msg.topic == "PVControl/Reles/EvseMode":
       mode=str(msg.payload)
    else :
       print msg.topic,msg.payload


client = mqtt.Client("openevse_mqtt") #crear nueva instancia
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
    while True:
#        current = random.choice([13,6,10,7,9,11,8,12,15,14,16])
#        ibat = random.choice([-13,-6,-10,-7,9,11,-8,12,-15,14,16])
#        diver = random.choice([1,1,1,0,1,1,0])

#        year, month, day, hour, minute = time.strftime("%Y,%m,%d,%H,%M").split(',')
#        print year, month, day, hour, minute

        if mode == "Auto":
            if diver == 0:  #Sin Excedentes
            
	        if ibat < 0: #Bajo intensidad un nivel. Si he llegado al mínimo, desactivo cargador
                     #if current == min_current:
                     #    client.publish(openevse_disable)
                     #    sleep_evse=1
                     #else:
                     if current > min_current:
                         current -= 1
                else: #Subo intensidad un nivel (hasta 13A). Si la intensidad es superior, bajo un nivel.Habilito cargador si no lo está.
                     if current > max_current_diver0:
                         current -= 1
                     elif current < max_current_diver0:
                         if sleep_evse == 1:
                             client.publish(openevse_enable)
                             sleep_evse=0
                         else:
                             current += 1
            else: #Con Excedentes
                if ibat < 0:  #Bajo intensidad un nivel. Si he llegado al mínimo, desactivo cargador
                     if current == min_current:
                         client.publish(openevse_disable)
                         sleep_evse=1
                     else:
                         current -= 1
                else: #Subo intensidad un nivel. Habilito cargador si no lo está.
                     if current < max_current:
                         if sleep_evse == 1:
                             client.publish(openevse_enable)
                             sleep_evse=0
                         else:
                             current += 1
        else: #En modo manual, envío la intensidad de entrada. Habilito cargador si no lo está
            current=int(mode)   
            if sleep_evse==1:
                client.publish(openevse_enable)
                sleep_evse=0 

        client.publish(openevse_current,current)
        #print "Mode:",mode,"\n","Amps:",current,"\n","Ibat:",ibat,"\n","Diver:",diver,"\n","SOC:",soc,"\n","Sleep:",sleep_evse,"\n"
        time.sleep(delay)

except:
    print "exiting"
    client.loop_stop()
    client.disconnect()

