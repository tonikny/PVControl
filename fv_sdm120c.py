#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-11-22

import sys, time
import MySQLdb,json
import subprocess

import minimalmodbus

from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)

#### Parametros_FV.py ##########
usar_sdm120c = [1] 
dev_sdm120c = ["/dev/ttyUSB0"]  # puerto donde reconoce la RPi al equipo
t_muestra_sdm120c = [5]         # Tiempo en segundos entre muestras
publicar_sdm120c_mqtt = [0]     # Publica o no por MQTT los datos capturados (no implementado aun)
grabar_datos_sdm120c = [1]      # 1 = Graba la tabla Hibrido... 0 = No graba
n_muestras_sdm120c = [1]        # grabar en BD cada nmuestras
# ###############################################

equipo = 'sdm120c'

if sum(eval(f'usar_{equipo}')) == 0:
    print (subprocess.getoutput(f'sudo systemctl stop {equipo}'))
    sys.exit()

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta 
if '-p' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios


# se cambiara para poner datos desde Parametros_FV.py para N equipos
if simular != 1:
    rs485 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    rs485.serial.baudrate = 2400
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
            try: #inicializamos registro RAM y tabla si no existe en BD 
                              
                Sql = f""" CREATE TABLE IF NOT EXISTS `sdm120c{N_Equipo}` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `Tiempo` datetime NOT NULL,
                  `Vac` float NOT NULL DEFAULT 0,
                  `Iac` float NOT NULL DEFAULT 0,
                  `Wac` float NOT NULL DEFAULT 0,
                  `VA` float NOT NULL DEFAULT 0,
                  `VAr` float NOT NULL DEFAULT 0,
                  `PF` float NOT NULL DEFAULT 0,
                  `AF` float NOT NULL DEFAULT 0,
                  `F` float NOT NULL DEFAULT 0,
                  `Kwhp` float NOT NULL DEFAULT 0,
                  `Kwhn` float NOT NULL DEFAULT 0,
                  `Kwhpr` float NOT NULL DEFAULT 0,
                  `Kwhnr` float NOT NULL DEFAULT 0,
                  `Kwh` float NOT NULL DEFAULT 0,
                  `Kwhr` float NOT NULL DEFAULT 0,
                  
                  PRIMARY KEY (`id`),
                  KEY `Tiempo` (`Tiempo`)
                ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci
                """                
                import warnings # quitamos el warning que da si existe la tabla equipos
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    cursor.execute(Sql)   
                db.commit()
                
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
        datos['Vac'] = round(rs485.read_float(0, 4, 2),1) # Voltaje AC
        datos['Iac'] = round(rs485.read_float(6, 4, 2),1) # Intensidad AC
        datos['Wac'] = round(rs485.read_float(12, 4, 2),1) # Watios AC
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
            
    if DEBUG == 1:
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
    

    if eval(f'grabar_datos_{equipo}[{I_Equipo}]') == 1: 
        ee = '50'
        try:
            # Insertar Registro en BD
            if n_muestras_contador[I_Equipo] == 1:
                ee = '50a'
                datos['Tiempo'] = tiempo
                
                #del Datos['Ibat'] # se quitan las claves que no estan en tabla BD
                
                campos = ",".join(datos.keys())
                valores = "','".join(str(v) for v in datos.values())
                Sql = f"INSERT INTO {equipo}{N_Equipo} ("+campos+") VALUES ('"+valores+"')"
                #print (Fore.RESET+Sql)
                cursor.execute(Sql)
                print (Fore.RED+'G'+N_Equipo,end='/',flush=True)
                db.commit()
                ee = '50d'
            
            if n_muestras_contador[I_Equipo] >= eval(f'n_muestras_{equipo}[{I_Equipo}]'):
                n_muestras_contador[I_Equipo] = 1
            else:
                n_muestras_contador[I_Equipo] +=1                   
        except:
            db.rollback()
            print (f'Error {ee} grabacion tabla {equipo}{N_Equipo}')
            
    db.commit()
    
while True:
    try:
        for i in range(len(eval(f'usar_{equipo}'))):
            if eval(f'usar_{equipo}[{i}]') == 1:
                if i==0: N_Equipo = ""
                else: N_Equipo = f'{i}'
                
                if int(time.time()) % eval(f't_muestra_{equipo}[{i}]') == 0: leer_equipo(equipo,i)
                    
    except:
        print ('Error desconocido....')
        sys.exit()
    
    time.sleep(1)
    
