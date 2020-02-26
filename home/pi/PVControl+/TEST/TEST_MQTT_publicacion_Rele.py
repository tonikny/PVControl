#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt

#broker_address="192.168.1.10"
broker_address="localhost"

#port = 1883
user = "rpi"
password = "fv"

topic_221="PVControl/Reles/221"
topic_Vbat="PVControl/DatosFV/Vbat"
topic_Ibat="PVControl/DatosFV/Ibat"
topic_Iplaca="PVControl/DatosFV/Iplaca"
topic_SOC="PVControl/DatosFV/SOC"
topic_Hora="PVControl/Hora"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectandose al broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Fallo Conexion al Broker")

Connected = False #global variable for the state of the connection

print("creando instancia")
client = mqtt.Client()
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect     #attach function to callback
client.connect(broker_address)
client.loop_start()         #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)

try:
    rele=0
    salto=5
    espera=0.25
    
    t = time.time()
    FV=0
    
    while True:
        #diver = random.choice([1,1,1,-1,1,-1,1,-1,1,-1,-1])
        diver = random.choice([1,1,1])
        rele = rele+diver*salto
        
        if rele > 100:
            rele = 100
        if rele < 0:
            rele = 0

        client.publish(topic_221,rele)
        
        FV+=1
        if FV%10 == 0:
            hora = time.strftime("%H:%M:%S")
            #tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            client.publish(topic_Hora,hora)
            print topic_221,diver,rele,hora
            
        if FV>= 20:
            FV=0
            Vbat = random.choice([23.8,24.1,24.4,25.2,26.1,27.3,28.3])
            Ibat = random.choice([-130,-50,-30,-10,0,5,15,25,35,120])
            Iplaca = random.choice([130,50,30,10,0,5,15,25,35,120])
            SOC = random.choice([70.3,80.3,82.2,85.5,88.8,90.8,92.9,95.5,99.9,100])

            #client.publish(topic_Vbat,Vbat)
            #client.publish(topic_Ibat,Ibat)
            #client.publish(topic_Iplaca,Iplaca)
            #client.publish(topic_SOC,SOC)
            #print topic_Vbat,Vbat,Ibat,Iplaca,SOC
        
##        t_ant = t
##        t = time.time()
##        
##        espera1 =espera - t + t_ant
##        if espera1 < 0:
##            espera1 = 0

        time.sleep(espera)

    print
        
except KeyboardInterrupt:
    print "exiting"
    client.disconnect()


