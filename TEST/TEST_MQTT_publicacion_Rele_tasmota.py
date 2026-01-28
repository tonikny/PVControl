#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt
import click


############# Conexion al Broker MQTT #####################
broker_address="localhost"

port = 1883
user = "rpi"
password = "fv"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectandose al broker")
        global Connected                           #Use global variable
        Connected = True                           #Signal connection 
    else:
        print("Fallo Conexion al Broker")

Connected = False                                  #global variable for the state of the connection

print("creando instancia MQTT")
client = mqtt.Client()
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.connect(broker_address)
client.loop_start()                                #start the loop
 
while Connected != True:                           #Wait for connection
    time.sleep(0.1)
################### Fin conexion Broker MQTT   ############################
    

try:
    rele = click.prompt(' Introduce el numero de rele=', type=int, default=531)

    topic_rele_tasmota='cmnd/PVControl/Reles/' + str(rele)[0:2]+ '/Channel'+str(rele)[-1]
    print ('topic=', topic_rele_tasmota)


    test = click.prompt(' Introduce el tipo de Test=  S= stress  / C= Calibracion SSR', type=str, default='C')

    if test == 'C':
        ini = 0
        ssr = []
        while True:    
            for pot in [5,10,15,20,30,40,50,60,70,80,85,90,95]: # lista de potencias 
                for duty in range(ini,101):  # recorrido del duty
                    client.publish(topic_rele_tasmota,duty)
                    print (f'Mandando potencia = {pot} con Duty = {duty}......',end='')
                    salir = click.prompt(' 0 = Aumentar Duty ----  1 = siguiente potencia', type=str, default='0')
                    if salir == '1': break
                if duty < 101:
                    print ('#' * 60)
                    print (f'   Guardando potencia = {pot} con Duty = {duty}')
                    print ('#' * 60)
                    ini= duty
                    ssr.append([pot,duty]) 
                    time.sleep(espera)
            print(ssr)
            salir = click.prompt(' 0 = Acabar ----  1 = Empezar de nuevo', type=str, default='0')
            if salir == '0': break
    else:
        print ()
        print ('########### TEST de STRESS ###########')
        espera = click.prompt(' introduce el tiempo en sg entre publicaciones MQTT', type=float, default=1)
        
        N = 1000
        print (f'Realizando test de {N} ciclos con espera de {espera} sg')
        
        for i in range (N): # N ciclos
            duty = random.choice([0,50,60,70,75,80,85,90,100])
            #print (i,'--', topic_rele_tasmota,'=',duty)
            print (i,'--', topic_rele_tasmota[0:-1], '(1,2,3)','=',duty)
            
            client.publish(topic_rele_tasmota,duty)
            client.publish(topic_rele_tasmota[0:-1]+'2',duty)
            client.publish(topic_rele_tasmota[0:-1]+'3',duty)
            
            
            time.sleep(espera)
            
except KeyboardInterrupt:
    print ("saliendo")
    client.disconnect()


