#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-01-02

# ########################   Control Ejecucion Servicio ##################################
servicio = 'daikin'
control = 'usar_daikin'
exec(open("fv_control_servicio.py").read())
# ########################################################################################

archivo_ram='/run/shm/datos_fv.json' # se lee... no se escribe archivo
Nodo = 'PVControl/Reles/27'  #el rele virtual sera el '27'+'1', ver mas abajo de donde sale el 1
DEBUG = False

import requests
from requests.exceptions import HTTPError
import json
import time
import pickle

from csvFv import CsvFv
import csv
import datetime
#import broadlink
import paho.mqtt.client as mqtt

estado = 0
estado_ant = 0
cmd_off = 'pydaikin -m off '+ IP_DAIKIN
time.sleep(2)

# ----------------------- MOSQUITTO ------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(Nodo+str(1))   #aqui vemos el 1 que decia antes, entonces 27+1=> 271  

def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Unexpected MQTT disconnection. Will auto-reconnect")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global ultimo_msg, duty
    duty = int(msg.payload)
    if DEBUG: print(msg.topic+" estado="+str(duty))
    ultimo_msg = time.time()


client = mqtt.Client("AA1") #crear nueva instancia, de nombre AA1 = Aire Acondicionado 1
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(usuario, password=clave)
try:
    client.connect(servidor, 1883) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()
temp_apagado = 0
ultimo_msg = time.time()
duty = 0
contador = 0 #para ver si llevo mucho tiempo al mínimo o máximo, si no hay excendentes apagar el AA
#temp = 20
#print('Temperatura objetivo inicial',temp,'ºC')
#print (subprocess.getoutput('pydaikin -t 20 192.168.1.54'))

def leer_pot_int():

    
    archivo_ram='/run/shm/datos_fv.json'
    try:
        with open(archivo_ram, 'rb') as f:
            d_fv = json.load(f)
    except:
        print('error lectura '+archivo_ram)
        return (-POT_AA) #si no leo el fichero, simulo un consumo alto para parar el AA por si acaso
        #continue       
        
    time.sleep(1)
    if (time.time()-d_fv[0][0]) > 20: return (-POT_AA)
    if DEBUG: print('Potencia instantánea',round(float(d_fv[5][1]),2))    
    return(round(float(d_fv[5][1]),2))
    
def leer_pot_med(X):
    y = 0
    for i in range(0,X):
        pot = leer_pot_int()
        y = y + int(pot)
        time.sleep(1)
    y = y / X 
    return(y)

class daikin:

    def __init__(self):
    
        self.dct = {}
        self.cmd_sensor = 'http://' + IP_DAIKIN + '/aircon/get_control_info?'
        self.cmd_control = 'http://' + IP_DAIKIN + '/aircon/get_sensor_info?'

    def read_data_sensor(self):
    
        try:
            response = requests.get(self.cmd_sensor)
            Encendido = (response.text.split(",")[1]).split("=")[1]
            Modo = (response.text.split(",")[2]).split("=")[1]
            if DEBUG: print('Encendido',Encendido,'Modo',Modo)
            
            self.dct['Encendido'] = Encendido
            self.dct['Modo'] = Modo
            return self.dct
            
        except:
            
            if DEBUG: print('Error lectura sensor')
            return None
            
            
    def read_data_control(self):
    
        try:
            response = requests.get(self.cmd_control)
            Temp_externa = (response.text.split(",")[3]).split("=")[1]
            Temp_interna = (response.text.split(",")[1]).split("=")[1]
            if DEBUG: print('Temp_externa',Temp_externa,'Temp_interna',Temp_interna)
            
            self.dct['Temp_externa'] = Temp_externa
            self.dct['Temp_interna'] = Temp_interna
            return self.dct
            
        except:
            
            if DEBUG: print('Error lectura control')
            return None

while True:    
    try:
        if (time.time()- ultimo_msg) > 60 and duty > 0: #si el relé esta encendido pero hace mas de 1 minuto del ultimo mensaje, apago el AA
            contador = 0
            print("Apagando rele virtual...")
            subprocess.getoutput(cmd_off)
            time.sleep(300) #despues de apagar por cualquier motivo el AA, espero 5 minutos antes de encenderlo
        if duty == 100: #si el relé está encendido
            aa = daikin()
            datos_sensor = aa.read_data_sensor()
            datos_control = aa.read_data_control()
            if DEBUG: print('sensor',datos_sensor,'control',datos_control)
            if int(datos_sensor['Encendido']) == 0: #si el AA estába apagado y hay al menos 500W de excendentes, lo enciendo para ver el modo de funcionamiento
                pot_inst = leer_pot_med(3)
                if int(pot_inst) > POT_AA:
                    cmd = 'pydaikin -t ' + str(int(float(datos_control['Temp_interna']))) + ' ' + IP_DAIKIN #arranco en el modo en el que esté a la temperatura de la habitación
                    subprocess.getoutput(cmd)
                    datos_sensor = aa.read_data_sensor()
                    temp = int(float(datos_control['Temp_interna'])) #temperatura inicial
            else:
                contador += 1
                pot_ac = leer_pot_med(30)
                var_temp = round(pot_ac/POT_AA)
                if DEBUG: print ('variación temp:',var_temp)
                estado = estado + var_temp
                if DEBUG: print ('estado:',estado)
                if estado >= 5: estado = 5
                if estado <= 0: estado = 0
                if DEBUG: print ('contador:',contador)
                if contador > 20 and var_temp < 0: #si ha estado en el mismo estado 10 minutos (20 vueltas x 30 segudos por vuelta) y no hay excedentes, apago. 
                    subprocess.getoutput(cmd_off)
                    time.sleep(300) #despues de apagar por cualquier motivo el AA, espero 5 minutos antes de encenderlo
                    contador = 0
                if estado_ant != estado: #si cambia el estado, hay que actualizar la temperatura
                    if int(datos_sensor['Modo']) == 4:
                        temp = temp + var_temp
                        if temp > TEMP_MAX_CALOR: temp =TEMP_MAX_CALOR
                        if temp < TEMP_MIN_CALOR: temp =TEMP_MIN_CALOR
                    elif int(datos_sensor['Modo']) == 3:
                        temp = temp - var_temp
                        if temp > TEMP_MAX_FRIO: temp =TEMP_MAX_FRIO
                        if temp < TEMP_MIN_FRIO: temp =TEMP_MIN_FRIO
                    else:
                        temp = temp
                    if DEBUG: print('Potencia media',pot_ac,'Nueva temperatura objetivo',temp,'ºC')
                    cmd = 'pydaikin -t '+str(temp)+' ' + IP_DAIKIN
                    if DEBUG: print('cmd',cmd)
                    subprocess.getoutput(cmd)
                    contador = 0
                estado_ant = estado
        if duty == 0 and int(datos_sensor['Encendido']) == 1 and contador > -1: #Si el relé está a cero, y el AA está encendido apago el AA, si se vuelve a encender desde el mando, ya lo no apaga
            estado = 0
            estado_ant = 0
            contador = -1
            print("Apagando aire acondicionado...")
            subprocess.getoutput(cmd_off)
            time.sleep(300) #despues de apagar por cualquier motivo el AA, espero 5 minutos antes de encenderlo
    except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
        break
    except:
        #print("error no conocido")
        time.sleep(5)
        #sys.exit()