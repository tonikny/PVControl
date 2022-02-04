#!/usr/bin/python
# -*- coding: utf-8 -*-
#  version 25/Dic/21
#--------------------------------------------------------------------------
from pyModbusTCP.client import ModbusClient
import time
import sys
import subprocess
import MySQLdb 
import json
from Parametros_FV import *
import pickle

if usar_SB1 == 0:
    print (subprocess.getoutput('sudo systemctl stop sb'))
    sys.exit()
        
sb = ModbusClient()
host = 'sb.host(IP_'+sys.argv[1]+')'
exec(host)

sb.port(502)
sb.unit_id(3)
sb.open()

Equipo = sys.argv[1]
print('Equipo:',Equipo,'Puerto abierto',sb.open(),'IP',sb.host())
crear_pkl = 0 # poner a 1 para versiones antiguas de PVControl que no usan BD en RAM

DEBUG = False
#Comprobacion argumentos en comando
if '-p' in sys.argv: DEBUG = True # para test .... realiza print en distintos sitios

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' sb.py')
print()

time.sleep(1)

try: #inicializamos BD
    # No se crea tabla especifica de fronius              
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try:
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  (Equipo,'{}'))   
        db.commit()
    except:
        pass     
except:
    print (Fore.RED+ 'ERROR inicializando BD RAM')
    sys.exit()



def leer_datos():
	
	try:
		Vred = sb.read_holding_registers(30783, 2)
		Vred = Vred[1]
		if Vred == 65535:Vred = 230
		else: Vred = Vred*0.01
		P = sb.read_holding_registers(30775, 2)
		P = P[1]
		VP1 = sb.read_holding_registers(30771, 2)
		VP1 = round(VP1[1] * 0.01,2)
		IP1 = sb.read_holding_registers(30769, 2)
		IP1 = round(IP1[1] * 0.001,2)
		VP2 = sb.read_holding_registers(30959, 2)
		VP2 = round(VP2[1] * 0.01,2)
		IP2 = sb.read_holding_registers(30957, 2)
		IP2 = round(IP2[1] * 0.001,2)
		Wred1 = sb.read_holding_registers(30865, 2)
		Wred2 = sb.read_holding_registers(30867, 2)
		Wred = -Wred1[1] + Wred2[1]
		datos = {'Iplaca1': IP1,'Vplaca1': VP1,'Iplaca2': IP2,'Vplaca2': VP2,
			'Wplaca': P,'Wred':Wred,'Vred':Vred}
		#print(datos)

	except:
		pass
		print('err')
	if datos !=None:
		return(datos)
	else:
		print('No hay datos')
		return(None)
		
while True:
	
	try:
	
		datos = leer_datos()
		
		if DEBUG: print('datos=',datos)
	
		if datos != None:
			if crear_pkl == 0:
				try:####  ARCHIVOS RAM en BD ############
					tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
			
					salida = json.dumps(datos)
					#print(salida)
					sql = (f"UPDATE equipos SET tiempo = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{sys.argv[1]}' ") # grabacion en BD RAM
					#print(sql)	
					cursor.execute(sql)
					db.commit()
				except:
					print(Fore.RED+f'error, Grabacion tabla RAM equipos en {Equipo}')
			else:    
				# lo logico es dejar de grabar el archivo pkl
				with open('/run/shm/datos_sb.pkl', mode='wb') as f:
					pickle.dump(datos, f)      
                
	except: 
		sb.close()
		time.sleep(6)
		sb.open()
		pass
	    
	time.sleep(5)

	
	
	
        
        
	
	
	
	

