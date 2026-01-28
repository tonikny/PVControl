#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
## Este servicio se ejecutará como openevse_partial_kWh.service para    ##
## recoger periodicamente las lecturas parciales del openEVSE.          ##
## Dos veces por hora, el proceso openevse_kWh_diario contará los       ##
## parciales y los guardará en la tabla diario 2.                       ##
##########################################################################
import time
import MySQLdb
import paho.mqtt.client as mqtt
from Parametros_FV import *

###### Parametros ############################
openevse_energy_usage="openevse/rapi/in/$GU"
openevse_ACK="openevse/rapi/out"
openevse_Amp="openevse/amp"
kWh_openevse=-1.0
kW_openevse=0
delay=1
update=0

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+"\n")
    client.subscribe(openevse_ACK)
    client.subscribe(openevse_Amp)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print ("Unexpected MQTT disconnection. Will auto-reconnect")
    else:
        client.loop_stop()
        client.disconnect()


def on_message(client, userdata, msg):
    global kWh_openevse,kW_openevse

    #print (msg.topic,msg.payload)
    if msg.topic == openevse_ACK:
        payload=(msg.payload).decode() 
        response=payload[:3]

        #print ("resp:",response,"six:",payload[5:6],"seven:",payload[6:7])

        if (response == "$OK" and payload[5:6] != "^" and payload[6:7] != "^"):
            i=4
            while payload[i] != " ":
                i += 1
            kWh_openevse=(float(payload[4:i])/3600)/1000
    
    elif msg.topic == openevse_Amp:
        payload=(msg.payload).decode()
        kW_openevse=(float(payload) / 1000) * 230
        #print(kW_openevse)
        
        

def logBD() :
    try:
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,log))
        print (tiempo,' ', log)
        db.commit()
    except:
        db.rollback()
        print (tiempo,'Error en logBD()')

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

db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()

try:
    while (kWh_openevse == -1.0 or update==0):
        client.publish(openevse_energy_usage)
        time.sleep(delay)

        try:
            if kWh_openevse != -1.0:
                
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                try:
                    cursor.execute("""INSERT INTO open_evse_partial (Fecha,kWh_evse,kW_evse) VALUES(%s,%s,%s)""",(tiempo,kWh_openevse,kW_openevse))  
                    db.commit()
                    #update=1

                except:
                    db.rollback()
                    log='Error en la creacion del registro Evse'
                    logBD()
                
                kWh_openevse = -1
                time.sleep(300)
                #cursor.close()    
                #db.close()
                #client.disconnect()

        except:
            log='Error en tabla Evse(partial_kWh)'
            logBD()

except:
    print ("exiting")
    client.loop_stop()
    client.disconnect()

