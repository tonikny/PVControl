#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-11-23

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

import json
import click

#from Parametros_FV import *
from Parametros_FV import *

if sum(usar_hibrido) == 0:
    print (subprocess.getoutput('sudo systemctl stop hibrido'))
    sys.exit()

#Comprobacion argumentos en comando
simular = DEBUG = BORRAR = 0
narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo....  permite simular respuesta Hibrido a QPIGS con una captura fija
if '-p' in sys.argv: DEBUG= 1 # para desarrollo .... realiza print en distintos sitios
if '-borrar' in sys.argv: BORRAR= 1 # para desarrollo....  inicializa la tablas en BD del hibrido


import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
COLOR = [Fore.BLACK,Fore.RED,Fore.GREEN,Fore.YELLOW,Fore.BLUE,Fore.MAGENTA,Fore.CYAN,Fore.WHITE]
FONDO = [Back.BLACK,Back.RED,Back.GREEN,Back.YELLOW,Back.BLUE,Back.MAGENTA,Back.CYAN,Back.WHITE]
BRILLO = [Style.DIM,Style.NORMAL,Style.BRIGHT]

print (BRILLO[2] + COLOR[3] + 'Arrancando'+ COLOR[2] +' hibrido.py') #+Style.RESET_ALL)

n_muestras_contador = [1 for i in range(len(usar_hibrido))] # contadores grabacion BD


if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
    bot.send_message(cid, 'Arrancando Programa Control Hibrido')


# Comprobacion BD

try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    for i in range(len(usar_hibrido)):
        if usar_hibrido[i] == 1:
            if i==0: N_Hibrido = ""
            else: N_Hibrido = f"{i}"
            
            try: # Borramos la tabla hibridoX si la opcion BORRAR esta activa
                if BORRAR == 1:
                    print (Fore.RED + Back.YELLOW+ f'  ATENCION.. SE BORRARAN LOS DATOS DE LA TABLA hibrido{N_Hibrido}')
                    print()
                    salir = click.prompt(Fore.CYAN + '  Si no esta seguro pulse 0 para salir o 1 para borrar ', type=str, default='0')
                    if salir == "1":
                        cursor.execute('DROP TABLE `hibrido{N_Hibrido}` ')   
                        db.commit()
                        print (Fore.CYAN+' Tabla hibrido{N_Hibrido} borrada'+Style.RESET_ALL)
            except:
                pass
            
            
            try: #inicializamos registro RAM y tabla si no existe en BD 
                              
                Sql = f""" CREATE TABLE IF NOT EXISTS `hibrido{N_Hibrido}` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `Tiempo` datetime NOT NULL,
                  `Vgen` float NOT NULL DEFAULT 0,
                  `Fgen` float NOT NULL DEFAULT 0,
                  `Iplaca` float NOT NULL DEFAULT 0,
                  `Vplaca` float NOT NULL DEFAULT 0,
                  `Wplaca` smallint(5) NOT NULL DEFAULT 0,
                  `Vbat` float NOT NULL DEFAULT 0,
                  `Vbus` smallint(3) NOT NULL DEFAULT 0,
                  `Ibatp` float NOT NULL DEFAULT 0,
                  `Ibatn` float NOT NULL DEFAULT 0,
                  `temp` float NOT NULL DEFAULT 0,
                  `PACW` smallint(5) NOT NULL DEFAULT 0,
                  `PACVA` smallint(5) NOT NULL DEFAULT 0,
                  `Flot` tinyint(1) NOT NULL DEFAULT 0,
                  `OnOff` tinyint(1) NOT NULL DEFAULT 0,
                  PRIMARY KEY (`id`),
                  KEY `Tiempo` (`Tiempo`)
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci
                """                
                import warnings # quitamos el warning que da si existe la tabla equipos
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    cursor.execute(Sql)   
                db.commit()
                
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                              ('HIBRIDO'+ N_Hibrido ,'{}'))   
                db.commit()
            except:
                pass             
                
                
except:
    print (Fore.RED,'ERROR inicializando BD RAM')
    sys.exit()


# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for i in range(len(usar_hibrido)):
        if i==0: N_Hibrido = ""
        else: N_Hibrido = f"{i}"
        client.subscribe("PVControl/Hibrido" + N_Hibrido)
        client.subscribe("PVControl/Hibrido"+ N_Hibrido + "/Opcion") # Ya vere para que
        
 
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print ("Desconexion MQTT.... intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global hora,t_muestra_hibrido,nbucle,n_muestras_contador
    ee = '0'
    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        hora_ant= hora
        hora = time.time()
        #print (int(hora-hora_ant), end = '')
        if nbucle > 0:
            nbucle -= 1
        
        #print(Fore.CYAN+msg.topic+" "+str(msg.payload))
        ee = '10'
        if msg.topic[:17]== "PVControl/Hibrido":
            ee = '10a'
            try:
                if msg.topic[-1].isnumeric():
                    N_Hibrido = msg.topic[-1]
                    I_Hibrido = int(N_Hibrido)
                else: # caso primer hibrido
                    N_Hibrido = ''
                    I_Hibrido = 0
            except: 
                print ('Error ', ee)
                
            #print (Fore.BLUE+f'{msg.topic} -- N_Hibrido={N_Hibrido} - I_Hibrido={I_Hibrido}')
            #print ('payload=',msg.payload)
            cmd=msg.payload#.decode()#.upper()
            #print ('cmd en message=',cmd)
            
            if simular == 1:
                ee = '10b'
                r= ['2021-11-15', '20:39:33', 'QPIGS', '000.0', '00.0', '230.1', '50.0', '0069', '0006',
                    '001', '407', '25.20', '000', '082', '0031', '0000', '000.0', '00.00', '00000',
                    '00010000', '00', '00', '00000', '010']
            else:
                ee = '10c'
                r= comando(cmd,I_Hibrido)
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
                
                Iplaca = round(float(Wplaca)/float(Vbat),1)  # Intensidad producida por placas en relacion a Vbat
                Ibat  = round(float(Ibatp) - float(Ibatn),2) # Intensidad de bateria             

                Datos = {'Vbat': Vbat,'Ibat':Ibat,'Ibatp':Ibatp,'Ibatn':Ibatn,'Iplaca': Iplaca,
                             'Vplaca': Vplaca,'Wplaca': Wplaca,'Vbus':Vbus,'PACW':PACW,'PACVA':PACVA,
                             'Temp':Temp,'Flot':Flot,'OnOff':OnOff,'Ibat':Ibat }

                
                ee = '30'
                ##########################################################################
                if publicar_hibrido_mqtt[I_Hibrido] == 1:  
                    for i in datos:
                        client.publish("PVControl/Hibrido"+ N_Hibrido+"/"+i,datos[i])
                
                try:####  ARCHIVOS RAM en BD ############ 
                    ee = '40'
                    salida = json.dumps(Datos)
                    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'HIBRIDO{N_Hibrido}'") # grabacion en BD RAM
                    #print (Fore.RED+sql)
                    cursor.execute(sql)
                    #db.commit()
                except:
                    print(Fore.RED+f'error, Grabacion tabla RAM equipos en HIBRIDO{N_Hibrido}')
                        
                #print (Fore.RESET+'grabar_datos_hibrido=',grabar_datos_hibrido,I_Hibrido,grabar_datos_hibrido[I_Hibrido])         
                if grabar_datos_hibrido[I_Hibrido] == 1: 
                    ee = '50'
                    try:
                        # Insertar Registro en BD
                        if n_muestras_contador[I_Hibrido] == 1:
                            ee = '50a'
                            Datos['Tiempo'] = tiempo
                            del Datos['Ibat'] # se quita la clave que no esta en tabla BD
                            campos = ",".join(Datos.keys())
                            valores = "','".join(str(v) for v in Datos.values())
                            Sql = f"INSERT INTO hibrido{N_Hibrido} ("+campos+") VALUES ('"+valores+"')"
                            #print (Fore.RESET+Sql)
                            cursor.execute(Sql)
                            print (COLOR[I_Hibrido+1]+'G'+N_Hibrido,end='/',flush=True)
                            db.commit()
                            ee = '50d'
                        
                        if n_muestras_contador[I_Hibrido] >= n_muestras_hibrido[I_Hibrido]:
                            n_muestras_contador[I_Hibrido] = 1
                        else:
                            n_muestras_contador[I_Hibrido] +=1                   
                    except:
                        db.rollback()
                        print (f'Error {ee} grabacion tabla hibrido{N_Hibrido}')
                        print (tiempo, r)
                    
                db.commit()
                    
            elif cmd == b'QPIGSBD':
                ee = '70'
                print ('X', end = '')
                pass

            else:
                ee = '80'
                print (Fore.CYAN,r, len(r)) 
                client.publish(f"PVControl/Hibrido{N_Hibrido}/Respuesta",str(r))
                if usar_telegram == 1: 
                    L1 = f'Comando Hibrido{N_Hibrido}= '+ str(cmd)[2:-1]
                    L2 = str(r)
                    tg_msg = L1+'\n'+L2
                    print (tg_msg) 
                    bot.send_message(cid, tg_msg)
            
    except:
        print (tiempo,f' -- error {ee} en on_message ')

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
def comando(cmd,I_Hibrido):
    
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
        
        if usar_crc[I_Hibrido] == 1:
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
        if os.path.exists(dev_hibrido[I_Hibrido]):
            if dev_hibrido[-7:-1] == "ttyUSB": # Hibridos con puerto tipo /dev/ttyUSB         
                err=21
                ser = serial.Serial(dev_hibrido[I_Hibrido], 2400, timeout = 1) 
                err=22
                time.sleep(.15)
                ser.write(bytes(cmd_crc)) # Envio comando al Hibrido
                err=30
                r = ser.readline()  # lectura respuesta Hibrido
            else:   # Hibridos con puerto tipo  /dev/hidraw
                err=21
                fd = open(dev_hibrido[I_Hibrido],'rb+')
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
            
            
        else:
            print(f'No se conecta Hibrido{I_Hibrido}')
            """
            s = [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9',
                 b'10',b'11',b'12',b'13',b'14',b'15',b'16',b'17',b'18',b'19',
                 b'20',b'21',b'22',b'23',b'24',b'25',b'26',b'27',b'28']
            """       
    except:
        print('Error Comando ',err,sys.exc_info([0]))
        
        s = f'Error Hibrido{I_Hibrido}'+str(err)
        time.sleep(12)
        
    finally:
        #print ('finally')
        if dev_hibrido[I_Hibrido][-7:-1] == "ttyUSB":
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

nbucle=0
tiempo_sg = time.time()

while True:
    if nbucle < 60:
        for i in range(len(usar_hibrido)):
            if usar_hibrido[i] == 1:
                if i==0: N_Hibrido = ""
                else: N_Hibrido = f"{i}"
                if int(time.time())%t_muestra_hibrido[i] == 0:
                    nbucle += 1
                    client.publish(f'PVControl/Hibrido{N_Hibrido}',"QPIGSBD")
                    if DEBUG == 1:
                        print (Fore.RESET,time.strftime("%Y-%m-%d %H:%M:%S"),f'-- Publico PVControl/Hibrido{N_Hibrido} QPIGSBD')
    else:
        sys.exit()
    time.sleep(1)

