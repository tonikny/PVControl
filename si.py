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

if usar_SI1 == 0:
    print (subprocess.getoutput('sudo systemctl stop sb'))
    sys.exit()
        
si = ModbusClient()
host = 'si.host(IP_'+sys.argv[1]+')'
exec(host)
print(si.host())
si.port(502)
si.unit_id(3)
si.open()

Equipo = sys.argv[1]

crear_pkl = 0 # poner a 1 para versiones antiguas de PVControl que no usan BD en RAM

DEBUG = False
#Comprobacion argumentos en comando
if '-p' in sys.argv: DEBUG = True # para test .... realiza print en distintos sitios

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' si.py')
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
		
		Vbat = si.read_holding_registers(30851, 2)
		Vbat = round(Vbat[1]*0.01,2)     
		Ibat = si.read_holding_registers(30843, 2)
		p_desc = si.read_holding_registers(31395, 2)
		p_desc = p_desc[1]
		p_carg = si.read_holding_registers(31393, 2)
		p_carg = p_carg[1]
		Aux1=   si.read_holding_registers(30803, 2)
		Aux1 = round(Aux1[1]*0.01,2)
		   
		if Ibat[0]<=32768:
		    Ibat = -(Ibat[1]+Ibat[0]*65535)*0.001
	
		else:
		    Ibat =  (65535-Ibat[1]+(65535-Ibat[0])*65536)*0.001
			    
		
		    
		datos = {'Vbat': Vbat,'Ibat': Ibat,'Pdesc': p_desc,'Pcarg': p_carg,'Aux1': Aux1}
		if DEBUG:print(datos)
		
	except:
		if DEBUG: print ('error de lectura SI')
		logBD('Error de Lectura SI Vbat,Ibat...')
		si.close()
		time.sleep(3)
		si.open()
		pass

	
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
		si.close()
		time.sleep(6)
		si.open()
		pass
	    
	time.sleep(5)

	
	
	
        
        
	
	
	
	

