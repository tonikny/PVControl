#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-25

import os, sys, time
import serial

import subprocess
import timeout_decorator

# Supresion de warning de crc16, TODO: cambiar la libreria, está obsoleta
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from crc16 import crc16xmodem

from struct import pack
from traceback import format_exc

import MySQLdb 
import telebot # Librería de la API del bot.
import token
import paho.mqtt.client as mqtt

import json
import click

#from Parametros_FV import *
from Parametros_FV import *

#Comprobacion argumentos en comando
simular = DEBUG = BORRAR = TEST = 0
narg = len(sys.argv)
if '-s' in sys.argv: simular = 1 # para desarrollo....  permite simular respuesta Hibrido a QPIGS con una captura fija
if '-p' in sys.argv: DEBUG = 1 # para desarrollo .... realiza print en distintos sitios
if '-borrar' in sys.argv: BORRAR = 1 # para desarrollo....  inicializa la tablas en BD del hibrido
if '-test' in sys.argv: TEST = 1 # para desarrollo....  inicializa la tablas en BD del hibrido

if sum(usar_hibrido)== 0 and TEST == 0:
    print (subprocess.getoutput('sudo systemctl stop hibrido'))
    sys.exit()

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
COLOR = [Fore.BLACK,Fore.RED,Fore.GREEN,Fore.YELLOW,Fore.BLUE,Fore.MAGENTA,Fore.CYAN,Fore.WHITE]
FONDO = [Back.BLACK,Back.RED,Back.GREEN,Back.YELLOW,Back.BLUE,Back.MAGENTA,Back.CYAN,Back.WHITE]
BRILLO = [Style.DIM,Style.NORMAL,Style.BRIGHT]

print (BRILLO[2] + COLOR[3] + 'Arrancando'+ COLOR[2] +' hibrido.py') #+Style.RESET_ALL)
print()

@timeout_decorator.timeout(10, use_signals=False)
def cmd_test(cmd,dev,crc):
    try:
        ee = 'c00'
        if crc == 1:
            checksum = crc16xmodem(cmd)
            cmd_crc = cmd + pack('>H', checksum)
             
        else:
            cmd_crc = cmd
        
        ee = 'c10'
        if isinstance(cmd, str):
            cmd_crc += '\r'
        else:
            cmd_crc += b'\r'
       
        ee = 'c20'
        if dev[-7:-1] == "ttyUSB": # Hibridos con puerto tipo /dev/ttyUSB         
            ser = serial.Serial(dev, 2400, timeout = 1) 
            time.sleep(.15)
            ser.write(bytes(cmd_crc)) # Envio comando al Hibrido
            r = ser.readline()  # lectura respuesta Hibrido
        
        else:   # Hibridos con puerto tipo  /dev/hidraw
            ee = 'c40'
            print(Fore.RESET+f'          dev={dev}-  cmd_crc={cmd_crc}')
            
            fd = open(dev,'rb+')    
            time.sleep(.20)
            if DEBUG == 1: print ('Byte1=',repr(cmd_crc[:8]))
            fd.write(cmd_crc[:8])
            
            ee = 'c42'
            if len(cmd_crc) > 8:
                if DEBUG == 1:print ('Byte2=',repr(cmd_crc[8:16]))
                fd.flush()
                fd.write(cmd_crc[8:16])

            ee = 'c45'
            if len(cmd_crc) > 16:
                if DEBUG == 1:print ('Byte3=',repr(cmd_crc[16:]))
                fd.flush()
                fd.write(cmd_crc[16:])
            
            ee = 50
            time.sleep(.5)                                                          
            ee = 'c50'
            r = fd.read(5)
            ee = 'c60'
            while r.find(b'\r') == -1 :
                time.sleep(.02)
                r = r + fd.read(1)
            
            #print(f'r={r}')
            
        return r
    except:
        print(Fore.RED+'Error=',ee)
        return f'ERROR {ee}'
    
if TEST == 1:
    for i in range(4):
        for j in ('hidraw','ttyUSB'):
            dev = f'/dev/{j}{i}'
            print()
            print (Fore.GREEN+f'Probando puerto {dev}....')
            if os.path.exists(dev):
                for cmd in (b'QPIGS',b'^P005GS'):
                    for crc in (0,1):
                        try:
                            print (Fore.YELLOW+ f'  .... Test en {dev} comando={cmd} crc={crc}....')
                            r = cmd_test(cmd,dev,crc)
                            print (Fore.GREEN+'             Respuesta=', r)
                        except:
                            print (Fore.RED+'       ..... No hay respuesta del Hibrido')
                        print(Fore.BLUE, '#'*80)           
            else:
                print (Fore.RED + f'No existe equipo detectado en {i}')
    print (Fore.YELLOW+'#'*80)
    print (Fore.GREEN+'      ----- Test finalizado -------')
    print (Fore.YELLOW+'#'*80+Fore.RESET)
    sys.exit()

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
                r = [i.decode() for i in r]
                if DEBUG == 1:print('Respuesta Hibrido',r)
             
            if cmd == b'QPIGSBD' and len(r) >= 24:
            
                if protocolo_hibrido[I_Hibrido]==30:
                    ee = '10e'
                    if DEBUG == 1:print('Hibrido con protocolo 30')
                
                    ##########################################################################
                    #            CAMBIAR INDICES  DE r[] DEPENDIENDO DEL MODELO DE HIBRIDO
                    ##########################################################################
                    #print ('Respuesta Hibrido=',r)
                    ee = '20'
                    Datos = {} # inicializo diccionario
                    
                    Datos['Vgen'] = float(r[3]) # Voltaje AC entrada Linea
                    Datos['Fgen'] = float(r[4]) # Frecuencia AC entrada Linea
                    
                    Datos['PACW'] = float(r[8])  # W consumo activo
                    Datos['PACVA'] = float(r[7]) # VA consumo aparente
                    ee = '22'
                    Datos['Vbus'] = float(r[10]) # V 
                    Datos['Vbat'] = float(r[11]) # Voltaje bateria
                    
                    Datos['Ibatp'] = float(r[12]) # A carga Bateria
                    ee = '24'
                    Datos['Temp'] = float(r[14])  # Grados
                    #Iplaca = r[15]
                                    
                    Datos['Vplaca'] = float(r[16]) # Voltaje placas
                                    
                    Datos['Ibatn'] = float(r[18])  # A descarga bateria
                    
                    Datos['Wplaca'] = float(r[22]) # W produccion placas
                    ee = '26'
                    Datos['Flot'] = int(r[23][0]) # estado bit flotacion
                    Datos['OnOff'] = int(r[23][1]) # estado pulsador OnOff Hibrido
                    
                    Datos['Iplaca'] = round(float(Datos['Wplaca'])/float(Datos['Vbat']),1)  # Intensidad producida por placas en relacion a Vbat
                    Datos['Ibat']  = round(float(Datos['Ibatp']) - float(Datos['Ibatn']),2) # Intensidad de bateria             
                    
                    ee = '28'
                    """
                    Datos = {'Vbat': Vbat,'Ibat':Ibat,'Ibatp':Ibatp,'Ibatn':Ibatn,'Iplaca': Iplaca,
                                 'Vplaca': Vplaca,'Wplaca': Wplaca,'Vbus':Vbus,'PACW':PACW,'PACVA':PACVA,
                                 'Temp':Temp,'Flot':Flot,'OnOff':OnOff }
                    """
                    Datos_BD = Datos.copy()
                    
                    Datos['Iplaca_PV'] = float(r[15])  # Intensidad de PV1
                    Datos['Vac'] = float(r[5])  # Voltaje AC
                    Datos['Fac'] = float(r[6])  # Frecuencia AC
                    
                    Datos['Carga'] = int(r[19][5]) # estado carga
                    Datos['Carga_SCC'] = int(r[19][6]) # estado carga SCC
                    Datos['Carga_AC'] = int(r[19][7]) # estado carga AC
                    
                    
                elif protocolo_hibrido[I_Hibrido]==18:
                    ee = '10f'
                    Vgrid = float(r[3])/10
                    Fgrid = float(r[4])/10
                    Vac = float(r[5])/10
                    Fac = float(r[6])/10
                    
                    ee = '10f1'
                    PACVA = float(r[7]) # VA salida AC
                    PACW = float(r[8]) # W salida AC
                    Carga = float(r[9]) # % carga
                    
                    Vbat = float(r[10])/10 # Vbat
                    Vbus = float(r[11])/10 # Vbat
                    Vbat_scc2 = float(r[12])/10 # Vbat
                    
                    ee = '10f2'
                    Ibatn = float(r[13]) # Ibat descarga
                    Ibatp = float(r[14]) # Ibat carga
                    Ibat  = round(Ibatp - Ibatn,2) # Intensidad de bateria             
                      
                    soc = float(r[15]) # SOC bateria
                    ee = '10f2a'
                    Temp = float(r[16])  # Temperatura Heat sink
                    Temp_mppt1 = float(r[17])  # Temperatura MPPT1
                    Temp_mppt2 = float(r[18])  # Temperatura MPPT2
                    
                    ee = '10f3'
                    Wplaca1 = int(r[19]) # W PV1
                    Wplaca2 = int(r[20]) # W PV2 
                    Wplaca = Wplaca1 +Wplaca2 #W PV1 + PV2
                    
                    Vplaca1 = float(r[21])/10 # V PV1
                    Vplaca2 = float(r[22])/10  # V PV2
                    Vplaca = Vplaca1 # podria ser la media, maximo etc
                   
                    ee = '10f4'
                    if Vbat==0:
                        if Vplaca > 0:
                            Iplaca = round (Wplaca / Vplaca, 2)
                        else:
                            Iplaca = 0
                    else:
                        Iplaca = round(float(Wplaca)/float(Vbat),1)  # Intensidad producida por placas en relacion a Vbat

                    ee = '10f5'
                    Change = int(r[23])  # 
                    Mppt1 = int(r[24])  # 
                    Mppt2 = int(r[25])  # 
                    Conexion = int(r[26])  #
                    Bat_status = int(r[27]) # 0: donothing, 1: charge, 2: discharge
                    Bat_Power_Direction= int(r[28])#0: donothing, 1: AC-DC, 2: DC-AC
                    Line_Power_Direction= int(r[29])#0: donothing, 1: input, 2: output
                    
                    Flot = Bat_status  #
                    OnOff = Line_Power_Direction #
                    
                    ee = '10f6'
                    
                    Datos = {'Vbat': Vbat,'Ibat':Ibat,'Ibatp':Ibatp,'Ibatn':Ibatn,'Iplaca': Iplaca,
                                 'Vplaca': Vplaca,'Wplaca': Wplaca,'Vbus':Vbus,'PACW':PACW,'PACVA':PACVA,
                                 'Temp':Temp,'Flot':Flot,'OnOff':OnOff,
                                 'Change':Change,'Mppt1':Mppt1,'Mppt2':Mppt2,'Conexion':Conexion,
                                 'Bat_status':Bat_status,'Bat_Power_Direction':Bat_Power_Direction,
                                 'Line_Power_Direction':Line_Power_Direction}

                    Datos_BD = Datos.copy()
                    
                if DEBUG == 1:print(Fore.GREEN+'Datos=',Datos,Fore.RESET)
                
                ee = '30'
                ##########################################################################
                if publicar_hibrido_mqtt[I_Hibrido] == 1:  
                    for i in Datos:
                        client.publish("PVControl/Hibrido"+ N_Hibrido+"/"+i,Datos[i])
                
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
                            Datos_BD['Tiempo'] = tiempo
                            ee = '50b'
                            
                            del Datos_BD['Ibat'] # se quita la clave que no esta en tabla BD
                            if protocolo_hibrido[I_Hibrido]==18:
                                del Datos_BD['Change']
                                del Datos_BD['Mppt1']
                                del Datos_BD['Mppt2']
                                del Datos_BD['Conexion']
                                del Datos_BD['Bat_status']
                                del Datos_BD['Bat_Power_Direction']
                                del Datos_BD['Line_Power_Direction']
                            
                            print ('Datos_BD=',Datos_BD)
                            campos = ",".join(Datos_BD.keys())
                            valores = "','".join(str(v) for v in Datos_BD.values())
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
            if protocolo_hibrido[I_Hibrido]==30: cmd1 = b'QPIGS'
            elif protocolo_hibrido[I_Hibrido]==18: cmd1 = b'^P005GS'
            

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
            if DEBUG == 1:
                    print(f'Mandando comando {cmd_crc} al Hibrido {dev_hibrido[I_Hibrido]}')
            if dev_hibrido[I_Hibrido][-7:-1] == "ttyUSB": # Hibridos con puerto tipo /dev/ttyUSB         
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
            if protocolo_hibrido[I_Hibrido]==30:            
                r = time.strftime("%Y-%m-%d %H:%M:%S").encode()+ b" " + cmd1 + b" " + r 
                # Creo lista separando por espacio
                s = r.split(b" ")
                
                err=50
                s[3]=s[3][1:] #quito el parentesis inicial de la respuesta

            elif protocolo_hibrido[I_Hibrido]==18:
                r = time.strftime("%Y-%m-%d,%H:%M:%S").encode()+ b"," + cmd1 + b"," + r 
                # Creo lista separando por coma
                s = r.split(b",")
                
                err=50
                s[3]=s[3][5:] #quito la D106 inicial de la respuesta

            
            
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

