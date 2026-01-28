#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from timeloop import Timeloop
from datetime import timedelta

import random # para simulacion usando random.choice
import json
import paho.mqtt.client as mqtt
import MySQLdb
from Parametros_FV import *

###### Parametros ############################
openevse_current="openevse/rapi/in/$SC"
openevse_disable="openevse/rapi/in/$FD"
openevse_enable="openevse/rapi/in/$FE"
mode="Auto"
max_current=25
max_current_diver0=13
min_current=6
current=13
ibat=0.0
diver=0
sleep_evse=0
delay=3
count_excedentes=0
TR={}
nreles=0
Connected = False #global variable for the state of the connection



tl = Timeloop()
@tl.job(interval=timedelta(seconds=5))
def sample_job_every_5s():
    global current,sleep_evse,mode,ibat,diver,nreles,TR

    print("Mode: ",mode,"Sleep_evse: ",sleep_evse,"Current: ",current)

    try:
        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor1 = db1.cursor()
        d_={}
        sql1 = "SELECT * FROM equipos where id_equipo = 'FV'"
        nequipos = int(cursor1.execute(sql1))
        for row in cursor1.fetchall(): d_[row[0]] = json.loads(row[2])
        ibat=float(d_['FV']['Ibat'])
        diver=int(d_['FV']['Aux1'])
        cursor1.close()
        db1.close()
    except Exception as e:
        pass


    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        sql="""SELECT valor FROM parametros1 WHERE id_parametro = 100"""
        cursor.execute(sql)
        var=cursor.fetchone()

        # Guardo en memoria los relés
        if int(var[0]) == 0:
            ##  ------ Nos guardamos el valor de los reles ------------------------
            sql = 'SELECT * FROM reles'
            nreles = cursor.execute(sql)
            nreles = int(nreles)  # = numero de reles
            columns = [column[0] for column in cursor.description] # creacion diccionario Tabla Reles
            TR=[]
            for row in cursor.fetchall(): TR.append(dict(zip(columns, row)))
            #print("Memoria reles:")
            #for i in range(nreles):
            #    print(TR[i]['id_rele']," ",TR[i]['modo'])

        if int(var[0]) > 5: #contador tiempo, desactivacion reles
            count_excedentes = int(var[0]) + 1
            cursor.execute("""UPDATE parametros1 SET valor=%s WHERE id_parametro =%s""",(str(count_excedentes),100))
            db.commit()
            client.publish(openevse_disable)
            sleep_evse=2

            #Paramos todos los reles
            cursor.execute('UPDATE reles SET modo="OFF"')
            db.commit()

        # Si han pasado 10 minutos sin resetear el contador, vuelvo a activar excedentes y recupero los valores originales en los reles
        if int(var[0]) > 200:
            #Recupero los valores originales en los relés
            for i in range(nreles):
                #print(TR[i]['id_rele']," ",TR[i]['modo'])
                cursor.execute("""UPDATE reles SET modo=%s WHERE id_rele=%s""",(TR[i]['modo'],TR[i]['id_rele']))
                db.commit()

            cursor.execute("""UPDATE parametros1 SET valor=%s WHERE id_parametro =%s""",('0',100))
            db.commit()
            client.publish(openevse_enable)
            sleep_evse=0

        cursor.close()
        db.close()

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
                    #if current == min_current:
                    #    client.publish(openevse_disable)
                    #    sleep_evse=1
                    #else:
                    if current > min_current:
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
        #print "Mode:",mode,"\n","Amps:",current,"\n","Ibat:",ibat,"\n","Diver:",diver,"\n","\n","Sleep:",sleep_evse,"\n"
        time.sleep(delay)

    except Exception as e:
        print ("exiting",e)
        client.loop_stop()
        client.disconnect()

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection
    else:
        print("Connection failed")

    client.subscribe("PVControl/Reles/PWM")
    client.subscribe("PVControl/Reles/EvseMode")


def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            client.loop_stop()
            client.disconnect()


def on_message(client, userdata, msg):
    global PWM,mode

    if msg.topic == "PVControl/Reles/PWM":
       PWM=(msg.payload).decode()
       PWM=float(PWM)
    elif msg.topic == "PVControl/Reles/EvseMode":
       mode=(msg.payload).decode()
    else :
       print (msg.topic,msg.payload)


client = mqtt.Client("openevse_mqtt") #crear nueva instancia
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, port=mqtt_puerto)          #connect to broker


client.loop_start()        #start the loop
while Connected != True:    #Wait for connection
    time.sleep(0.1)
if __name__ == "__main__":  #main loop
    tl.start(block=True)
client.disconnect()
client.loop_stop()
#tl.stop()
