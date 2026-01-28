#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2024-06-16

import sys, time
import MySQLdb,json
import subprocess

import minimalmodbus

from Parametros_FV_DIST import *
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)

"""
#### Parametros_FV.py ##########
usar_sdm230m = [0] 
dev_sdm230m = ["/dev/ttyUSB0"]  # puerto donde reconoce la RPi al equipo
              
t_muestra_sdm230m = [5]         # Tiempo en segundos entre muestras
#publicar_sdm230m_mqtt = [0]     # Publica o no por MQTT los datos capturados (no implementado aun)
# ###############################################
"""

equipo = 'sdm230m'

if sum(eval(f'usar_{equipo}')) == 0:
    print (subprocess.getoutput(f'sudo systemctl stop fv_{equipo}'))
    sys.exit()

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta 
if '-p' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios


# se cambiara para poner datos desde Parametros_FV.py para N equipos
if simular != 1:
    rs485 = minimalmodbus.Instrument(dev_sdm230m[0], 1)
    rs485.serial.baudrate =1200
    rs485.serial.bytesize = 8
    rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
    rs485.serial.stopbits = 1
    rs485.serial.timeout = 1
    rs485.debug = False
    rs485.mode = minimalmodbus.MODE_RTU
    print (rs485)


# Comprobacion BD

n_muestras_contador = [1 for i in range(len(eval(f'usar_{equipo}')))] # contadores grabacion BD

try:
    ee = '10'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    for i in range(len(eval(f'usar_{equipo}'))):
        ee = '10a'    
        if eval(f'usar_{equipo}[{i}]') == 1:
            if i==0: N_Equipo = ""
            else: N_Equipo = f"{i}"
            try: #inicializamos registro RAM 
                              
                
                ee = '10b'
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                              (equipo.upper()+ N_Equipo ,'{}'))   
                db.commit()
            except:
                pass             
                                
except:
    print (Fore.RED,f'ERROR {ee} - inicializando BD RAM')
    sys.exit()


def leer_equipo(equipo,I_Equipo):
    global n_muestras_contador
    
    if I_Equipo == 0: N_Equipo = ""
    else: N_Equipo = f"{I_Equipo}"

    datos= {} # Diccionarios datos
    
    if simular == 1:
     datos = {'Vac': 220,'Iac': 2,'Wac': 440,'VA': 460,'VAr': 22,'PF': 0.8,'AF': 20,'F': 50.1,
              'Kwhp':3.3,'Kwhn':5.5,'Kwhpr':1.1,'Kwhnr':2.2,'Kwh':-2.2,'Kwhr':-1.1}
    else:
        try:
            ee = 0
            datos['Vac'] = round(rs485.read_float(0x0, 4, 2),1) # Voltaje AC
            ee = 1
            datos['Iac'] = round(rs485.read_float(0x06, 4, 2),1) # Intensidad AC
            ee = 2
            datos['Wac'] = -round(rs485.read_float(0x0C, 4, 2),1) # Watios AC
            ee = 3
            datos['PF'] = round(rs485.read_float(0x1E, 4, 2),1)  # Factor de Potencia
            ee = 4
            datos['Fase'] = round(rs485.read_float(0x24, 4, 2),1)  # Factor de Potencia
            ee = 5
            datos['F'] = round(rs485.read_float(0x46, 4, 2),1)  #Frecuencia
            ee = 6
            datos['Kwh_import'] = round(rs485.read_float(0x48, 4, 2),1)
            ee = 7
            datos['Kwh_export'] = round(rs485.read_float(0x4A, 4, 2),1)
            ee = 8
            datos['W_import'] = round(rs485.read_float(0x58, 4, 2),1)
            ee = 9
            datos['W_export'] = round(rs485.read_float(0x5C, 4, 2),1)
        
            datos['Wred'] = int(datos['W_export'] - datos['W_import'])
        
        
            """
            datos['VA'] = round(rs485.read_float(18, 4, 2),1)  # Potencia aparente
            datos['VAr'] = round(rs485.read_float(24, 4, 2),1) # Potencia reactiva
            datos['PF'] = round(rs485.read_float(30, 4, 2),1)  # Factor de Potencia
            datos['AF'] = round(rs485.read_float(36, 4, 2),1) # Angulo de fase
            datos['F'] = round(rs485.read_float(70, 4, 2),1)  #Frecuencia
            datos['Kwhp'] = round(rs485.read_float(72, 4, 2),3) # Kwh importados
            datos['Kwhn'] = round(rs485.read_float(74, 4, 2),3) # Kwh exportados
            datos['Kwhpr'] = round(rs485.read_float(76, 4, 2),3) # Kwh importados reactiva
            datos['Kwhnr'] = round(rs485.read_float(78, 4, 2),3) # Kwh exportados reactiva
            datos['Kwh'] = round(rs485.read_float(342, 4, 2),3)  # Kwh netos
            datos['Kwhr'] = round(rs485.read_float(344, 4, 2),3) # Kwh netos reactiva
            """
            #print(datos)
        except:
            print (f'Error {ee} en captura de datos')
            datos['Wac'] = 0 # Watios AC a cero si no responde
            
    if DEBUG == 1:
        print (f'{time.strftime("%H:%M:%S")}','=' * 70)
        for i in datos: print(f'{i}= {datos[i]}')    

    
    try:####  ARCHIVOS RAM en BD ############ 
        ee = '40'
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        salida = json.dumps(datos)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo.upper()}{N_Equipo}'") # grabacion en BD RAM
        #print (Fore.RED+sql)
        cursor.execute(sql)
        #db.commit()
    except:
        print(Fore.RED+f'error, Grabacion tabla RAM equipos en {equipo.upper()}{N_Equipo}')


t_captura = time.time()-100

while True:
    try:
        for i in range(len(eval(f'usar_{equipo}'))):
            if eval(f'usar_{equipo}[{i}]') == 1:
                if i==0: N_Equipo = ""
                else: N_Equipo = f'{i}'
                
                if time.time() - t_captura > t_muestra_sdm230m[i]:
                    
                    leer_equipo(equipo,i)
                    t_captura = time.time()
    except:
        print ('Error desconocido....')
        sys.exit()
    
    time.sleep(1)
    
