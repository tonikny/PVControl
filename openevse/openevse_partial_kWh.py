#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
## Este servicio se ejecutará en el crontab para recoger periodicamente ##
## las lecturas parciales del openEVSE. A final del dia el proceso      ##
## xxxxxxxxxxx contará los parciales y los guardará en la tabla master  ##
##########################################################################


import MySQLdb
import time
import random # para simulacion usando random.choice

import paho.mqtt.client as mqtt

###### Parametros ############################
servidor = '192.168.1.15'
servidor2 = 'localhost'
usuario = 'rpi'
clave = 'fv'
basedatos = 'control_solar'

openevse_energy_usage="openevse/rapi/in/$GU"
openevse_ACK="openevse/rapi/out"
kWh_openevse=-1
delay=1
update=0

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+"\n")
    client.subscribe(openevse_ACK)


def on_disconnect(client, userdata, rc):
        if rc != 0:
            print "Unexpected MQTT disconnection. Will auto-reconnect"
        else:
            client.loop_stop()
            client.disconnect()


def on_message(client, userdata, msg):
    global kWh_openevse

    print msg.topic,msg.payload
    if msg.topic == openevse_ACK:
        payload=str(msg.payload)    
        response=payload[:3]

        #print "resp:",response,"six:",payload[5:6],"seven:",payload[6:7]

        if (response == "$OK" and payload[5:6] <> "^" and payload[6:7] <> "^"):
            i=4
            while payload[i] <> " ":
                i += 1
            kWh_openevse=(float(payload[4:i])/3600)/1000


tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
date = time.strftime("%Y-%m-%d")


def logBD() :
    try:
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,log))
        print tiempo,' ', log
        db.commit()
    except:
        db.rollback()
        print tiempo,'Error en logBD()'

    return


client = mqtt.Client("openevse_kWh") #crear nueva instancia
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
    while (kWh_openevse == -1 or update==0):
        client.publish(openevse_energy_usage)
        time.sleep(delay)

        try:
            db = MySQLdb.connect(host = servidor2, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            if kWh_openevse <> -1:
                try:
                    cursor.execute("""INSERT INTO open_evse_partial (Fecha,kWh_evse) VALUES(%s,%s)""",(tiempo,kWh_openevse))  
                    db.commit()
                    update=1

                except:
                    db.rollback()
                    log='Error en la creacion del registro Evse'
                    logBD()


        except:
            log='Error en tabla Evse'
            logBD()



except:
    print "exiting"
    client.loop_stop()
    client.disconnect()

