#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-10-17

import os, sys, time
import serial

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

import pickle,json

from Parametros_FV import *

if usar_hibrido == 0:
    print (subprocess.getoutput('sudo systemctl stop hibrido'))
    sys.exit()

#Comprobacion argumentos en comando
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-s': simular= 1 # para desarrollo permite simular respuesta Hibrido a QPIGS con una captura fija
else: simular = 0
    
if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
    bot.send_message(cid, 'Arrancando Programa Control Hibrido')


# Comprobacion BD
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    try: #inicializamos registro en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('HIBRIDO','{}'))
        db.commit()
    except:
        pass
except:
    print (Fore.RED,'ERROR inicializando BD RAM')
    sys.exit()


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
    ee = '0'
    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        hora_ant= hora
        hora = time.time()
        print (int(hora-hora_ant), end = '')
        if nbucle > 0:
            nbucle -= 1
        
        #print(msg.topic+" "+str(msg.payload))
        ee = '10'
        if msg.topic== "PVControl/Hibrido":
            ee = '10a'
            #print ('payload=',msg.payload)
            cmd=msg.payload#.decode()#.upper()
            #print ('cmd en message=',cmd)
            
            if simular == 1:
                ee = '10b'
                r= ['2021-09-23', '20:39:33', 'QPIGS', '000.0', '00.0', '230.1', '50.0', '0069', '0006',
                    '001', '407', '25.20', '000', '082', '0031', '0000', '000.0', '00.00', '00000',
                    '00010000', '00', '00', '00000', '010']
            else:
                ee = '10c'
                r= comando(cmd)
                ee = '10d'
                #print(r)
                r = [i.decode() for i in r]
            #print (r)
            #print ('cmd=',cmd)
            
            if cmd == b'QPIGSBD' and len(r) >= 24:
                ##########################################################################
                #            CAMBIAR INDICES  DE r[] DEPENDIENDO DEL MODELO DE HIBRIDO
                ##########################################################################
                #print ('Respuesta Hibrido=',r)
                ee = '20'
                Vgen = float(r[3]) # Voltaje AC entrada Linea
                Fgen = float(r[4]) # Frecuencia AC entrada Linea
                
                PACW = float(r[8])  # W consumo activo
                PACVA = float(r[7]) # VA consumo aparente
                
                Vbus = float(r[10]) # V 
                Vbat = float(r[11]) # Voltaje bateria
                
                Ibatp = float(r[12]) # A carga Bateria
                
                Temp = float(r[14])  # Grados
                #Iplaca = r[15]
                                
                Vplaca = float(r[16]) # Voltaje placas
                                
                Ibatn = float(r[18])  # A descarga bateria
                
                Wplaca = float(r[22]) # W produccion placas
                
                Flot = int(r[23][0]) # estado bit flotacion
                OnOff = int(r[23][1]) # estado pulsador OnOff Hibrido
                
                Iplaca = float(Wplaca)/float(Vbat)  # Intensidad producida por placas en relacion a Vbat
                Ibat  = float(Ibatp) - float(Ibatn) # Intensidad de bateria             
                ee = '30'
                ##########################################################################
                if publicar_hibrido_mqtt == 1:
                    client.publish("PVControl/Hibrido/Iplaca",Iplaca)
                    client.publish("PVControl/Hibrido/Vplaca",Vplaca)
                    client.publish("PVControl/Hibrido/Wplaca",Wplaca)

                    client.publish("PVControl/Hibrido/Vbat",Vbat)
                    client.publish("PVControl/Hibrido/Vbus",Vbus)
                    
                    client.publish("PVControl/Hibrido/Ibatp",Ibatp)
                    client.publish("PVControl/Hibrido/Ibatn",Ibatn)
                    client.publish("PVControl/Hibrido/Ibat",Ibat)
                    

                    client.publish("PVControl/Hibrido/PACW",PACW)
                    client.publish("PVControl/Hibrido/PACVA",PACVA)
                    
                    client.publish("PVControl/Hibrido/Temp",Temp)
                                 
                    client.publish("PVControl/Hibrido/Flot",Flot)
                    client.publish("PVControl/Hibrido/OnOff",OnOff)
                
                if grabar_datos_hibrido == 1:
                    ee = '50'
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
                    ee = '60'
                    datos = {'Vbat': Vbat,'Ibat':Ibat,'Ibatp':Ibatp,'Ibatn':Ibatn,'Iplaca': Iplaca,
                             'Vplaca': Vplaca,'Wplaca': Wplaca,'Vbus':Vbus,'PACW':PACW,'PACVA':PACVA,
                             'Temp':Temp,'Flot':Flot,'OnOff':OnOff,'Ibat':Ibat }

                    ####  ARCHIVOS RAM en BD ############ 
                
                    salida = json.dumps(datos)
                    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'HIBRIDO'") # grabacion en BD RAM
                    cursor.execute(sql)            
                except:
                    print(Fore.RED+'error, Grabacion tabla RAM equipos')
                
                db.commit()
                    
            elif cmd == b'QPIGSBD':
                ee = '70'
                print ('X', end = '')
                pass

            else:
                ee = '80'
                print (r, len(r)) 
                client.publish("PVControl/Hibrido/Respuesta",str(r))
                if usar_telegram == 1: 
                    L1 = 'Comando Recibido ='+ str(cmd)
                    L2 = str(r)
                    tg_msg = L1+'\n'+L2
                    print (tg_msg) 
                    bot.send_message(cid, tg_msg)
            
    except:
        print (f' -- error {ee} en on_message ')

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
            if dev_hibrido[-7:-1] == "ttyUSB": # Hibridos con puerto tipo /dev/ttyUSB         
                err=21
                ser = serial.Serial(dev_hibrido, 2400, timeout = 1) 
                err=22
                time.sleep(.15)
                ser.write(bytes(cmd_crc)) # Envio comando al Hibrido
                err=30
                r = ser.readline()  # lectura respuesta Hibrido
            else:   # Hibridos con puerto tipo  /dev/hidraw
                err=21
                fd = open(dev_hibrido,'rb+')
                err=22
                
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
        print('Error Comando ',err,sys.exc_info([0]))
        
        t_muestra=12
        s = 'Error Hibrido'+str(err)
        
        
    finally:
        #print ('finally')
        if dev_hibrido[-7:-1] == "ttyUSB":
            ser.flush() #limpia el buffer
        else:
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

