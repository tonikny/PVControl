#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-08-29

import os, sys, time
import subprocess
import timeout_decorator

from crc16 import crc16xmodem
from struct import pack
from traceback import format_exc

import MySQLdb 
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

import csv

from Parametros_FV import *

if usar_hibrido == 0:
    print (subprocess.getoutput('sudo systemctl stop hibrido'))
    sys.exit()

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
    bot.send_message(cid, 'Arrancando Programa Control Hibrido')


# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("PVControl/Hibrido")
    client.subscribe("PVControl/Hibrido/Opcion") # Ya vere para que
    
 
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Desconexion MQTT.... intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global hora,t_muestra,nbucle

    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        hora_ant= hora
        hora = time.time()
        print (int(hora-hora_ant), end = '')
        if nbucle > 0:
            nbucle -= 1
        
        #print(msg.topic+" "+str(msg.payload))
        
        if msg.topic== "PVControl/Hibrido":
            #print ('payload=',msg.payload)
            cmd=msg.payload#.decode()#.upper()
            #print ('cmd en message=',cmd)
            
            r= comando(cmd)
            
            #print(r)
            
            r = [i.decode() for i in r]
            #print (r)
            print ('cmd=',cmd)
            
            if cmd == b'QPIGSBD' and len(r) >= 24:
                ##########################################################################
                #            CAMBIAR INDICES  DE r[] DEPENDIENDO DEL MODELO DE HIBRIDO
                ##########################################################################
                #print ('Respuesta Hibrido=',r)
                
                Vgen = r[3] # Voltaje AC entrada Linea
                Fgen = r[4] # Frecuencia AC entrada Linea
                
                PACW = r[8]  # W consumo activo
                PACVA = r[7] # VA consumo aparente
                
                Vbus = r[10] # V 
                Vbat = r[11] # Voltaje bateria
                
                Ibatp = r[12] # A carga Bateria
                
                Temp = r[14]  # Grados
                #Iplaca = r[15]
                                
                Vplaca = r[16] # Voltaje placas
                                
                Ibatn = r[18]  # A descarga bateria
                
                Wplaca = r[22] # W produccion placas
                
                Flot = r[23][0] # estado bit flotacion
                OnOff = r[23][1] # estado pulsador OnOff Hibrido
                
                Iplaca = float(Wplaca)/float(Vbat) # Intensidad producida por placas en relacion a Vbat
                
                
                ##########################################################################
                
                client.publish("PVControl/Hibrido/Iplaca",Iplaca)
                client.publish("PVControl/Hibrido/Vplaca",Vplaca)
                client.publish("PVControl/Hibrido/Wplaca",Wplaca)

                client.publish("PVControl/Hibrido/Vbat",Vbat)
                client.publish("PVControl/Hibrido/Vbus",Vbus)
                
                client.publish("PVControl/Hibrido/Ibatp",Ibatp)
                client.publish("PVControl/Hibrido/Ibatn",Ibatn)

                client.publish("PVControl/Hibrido/PACW",PACW)
                client.publish("PVControl/Hibrido/PACVA",PACVA)
                
                client.publish("PVControl/Hibrido/Temp",Temp)
                             
                client.publish("PVControl/Hibrido/Flot",Flot)
                client.publish("PVControl/Hibrido/OnOff",OnOff)
                
                if grabar_datos_hibrido == 1:
                    try:
                        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor1 = db1.cursor()
                        cursor1.execute("""INSERT INTO hibrido (Tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,
                                                                PACW,PACVA,Temp,Flot,OnOff)
                                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                        (tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,PACW,PACVA,Temp,Flot,OnOff))
                        db1.commit()
                    except:
                        db1.rollback()
                        print ('error grabacion tabla hibrido')
                        print (tiempo, r)
                    try:
                        cursor1.close()
                        db1.close()
                    except:
                        pass

                try:
                    with open('/run/shm/datos_hibrido.csv', mode='w') as f:
                        nombres = ['Tiempo_sg','Tiempo','Iplaca', 'Vplaca', 'Wplaca','Vbat','Vbus','Ibatp','Ibatn','PACW','PACVA','Temp','Flot','OnOff']
                        datos = csv.DictWriter(f, fieldnames=nombres)
                        datos.writeheader()
                        datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Iplaca': Iplaca,'Vplaca': Vplaca,'Wplaca': Wplaca,
                         'Vbat': Vbat,'Vbus':Vbus,'Ibatp':Ibatp,'Ibatn':Ibatn,
                         'PACW':PACW,'PACVA':PACVA,'Temp':Temp,'Flot':Flot,'OnOff':OnOff})
                except:
                    print ('Error grabacion fichero datos_hibrido.csv')

                    
            elif cmd == b'QPIGSBD':
                print ('X', end = '')
                pass

            else:
                print (r, len(r)) 
                client.publish("PVControl/Hibrido/Respuesta",str(r))
                if usar_telegram == 1: 
                    L1 = 'Comando Recibido ='+ str(cmd)
                    L2 = str(r)
                    tg_msg = L1+'\n'+L2
                    print (tg_msg) 
                    bot.send_message(cid, tg_msg)
            
    except:
        print ('error en on_message')

client = mqtt.Client("hibrido") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()

# ---- Comandos HIBRIDO

@timeout_decorator.timeout(15, use_signals=False)
def comando(cmd):
    global t_muestra
    
    #print ('cmd=',cmd, '  cmd.decode()=',cmd.decode())
    cmd1 = cmd
    
    try:
        err=10
        #print ('Comando')
        if cmd1 == b"ERROR":
            while True:
                time.sleep(1)

        if cmd1 == b'QPIGSBD':
            cmd1 = b'QPIGS'

        #print('cmd1==',cmd1)
        
        if usar_crc == 1:
            if cmd1 == b"POP02":   # ERROR firmware - CRC correcto es: 0xE2 0x0A
                cmd_crc = b'\x50\x4f\x50\x30\x32\xe2\x0b\x0d'
            elif cmd1[:9] == b'^S007POP1':
                cmd1 = b'^S007POP1\x0e\x10\r'    
            elif cmd1[:9] == b'^S007LON0':
                cmd1 = b'^S007LON0\x69\xd8\r'
            else:
                checksum = crc16xmodem(cmd1)
                cmd_crc = cmd1 + pack('>H', checksum) + b'\r'
        else:
            cmd_crc = cmd1 + b'\r'

        #print ('Comando=',cmd_crc)
        err=20
        if os.path.exists(dev_hibrido):
            fd = open(dev_hibrido,'rb+')
            time.sleep(.15)
            
            fd.write(cmd_crc[:8])
            
            if len(cmd_crc) > 8:
                fd.flush()
                fd.write(cmd_crc[8:16])
                err=21
                if (cmd1 == b"PBEQA1") or (cmd1 == b"PBEQA0"):
                    fd.write(cmd_crc[8:16]) ######
                    err = 22

            if len(cmd_crc) > 16:
                fd.flush()
                fd.write(cmd_crc[16:])      
                
            time.sleep(.5)
            
            err=30
            r = fd.read(5)

            while r.find(b'\r') == -1 :
                time.sleep(.02)
                r = r + fd.read(1)

            err=40
            r = r[0:len(r)-3] # quita CRC
            #print (r)
            
            #Añado a la respuesta fecha hora y comando enviado
            r = time.strftime("%Y-%m-%d %H:%M:%S").encode()+ b" " + cmd1 + b" " + r 
            #print('Sin CRC=',r)
            # Creo lista separando por espacio
            s = r.split(b" ")
            
            err=50
            s[3]=s[3][1:] #quito el parentesis inicial de la respuesta
            
            t_muestra=5
        else:
            print('No se conecta Hibrido')
            """
            s = [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9',
                 b'10',b'11',b'12',b'13',b'14',b'15',b'16',b'17',b'18',b'19',
                 b'20',b'21',b'22',b'23',b'24',b'25',b'26',b'27',b'28']
            """       
    except:
        #print('Error Comando ',err)
        t_muestra=12
        s = 'Error Hibrido'+str(err)
        
    finally:
        #print ('finally')
        try:
            fd.close()
        except:
            pass
        #print (s)
        return s

        
##### Bucle infinito  ######################
hora = time.time()

client.publish('PVControl/Hibrido/Respuesta','Arrancando Control Hibrido')
t_muestra = 5
nbucle=0

while True:
    nbucle += 1
    time.sleep(t_muestra)
    if nbucle < 6:
        client.publish('PVControl/Hibrido',"QPIGSBD")       
    else:
        sys.exit()

