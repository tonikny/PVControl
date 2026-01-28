#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-08-16

import can
import cantools
import os
import json
import time
import re


import MySQLdb
import sys, subprocess
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)

###### a incluir en Parametros_FV.py
usar_pylontech = 0
dbcfile="/home/pi/PVControl+/pylontech_US2000B_Plus_PVControl.dbc"
caninterface="can0"
id_equipo = 'PYLON'

#############################################

basepath = '/home/pi/PVControl+/'
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
parametros_FV_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"

exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios

if usar_pylontech== 0:
    print (subprocess.getoutput('sudo systemctl stop fv_pylontech'))
    sys.exit()
    

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta 
if '-p1' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios
elif '-p' in sys.argv: DEBUG= 100

os.system('sudo ip link set '+caninterface+' type can bitrate 500000')
os.system('sudo ifconfig '+caninterface+' up')

dbcan = cantools.database.load_file(dbcfile)
can_bus = can.interface.Bus(caninterface, bustype='socketcan')

time.sleep(1)

datos= {}

try: #inicializamos registro RAM y tabla si no existe en BD 
    ee = '10'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    
    ee = '10b'
    cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  (id_equipo.upper() ,'{}'))   
    db.commit()
except:
    pass        


while True:
        try:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            message = can_bus.recv()
            id_msg = message.arbitration_id
            
            canname =  (dbcan.get_message_by_frame_id(id_msg).name)
            if DEBUG > 0: print (tiempo, f'ID:{id_msg} - {canname}')
            
            test = dbcan.decode_message(id_msg, message.data)
            
            if id_msg != 862: datos[canname] = test
            
            if canname == 'BMS_Alarma':
                if DEBUG > 0:
                    print (tiempo, datos)
                    print ('=' * 80)
                else:
                    print('G', flush= True,end='')
                ####  ARCHIVO TABLA equipos en BD ############
                try: 
                    ee2='1000'
                    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                    salida = json.dumps(datos)
                    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{id_equipo.upper()}'") # grabacion en BD RAM
                    cursor.execute(sql)
                    
                except:
                    print(Fore.RED+f'error, Grabacion tabla RAM equipos en {id_equipo.upper()}')                

                db.commit()

            
            

        except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
            os.system('sudo ifconfig '+caninterface+' down')
            break
        except:
            print(f"error no conocido en lectura ")
            time.sleep(5)
            #sys.exit()

os.system('sudo ifconfig '+caninterface+' down')
