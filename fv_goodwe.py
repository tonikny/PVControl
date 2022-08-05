# -*- coding: utf-8 -*-
#"""
#Version 02/Ago/22


import asyncio
import goodwe

import json
import time
import subprocess, sys
import MySQLdb 

DEBUG = 0
#Comprobacion argumentos en comando
if '-p1' in sys.argv: DEBUG = 1    # ...  print diccionario datos
elif '-p2' in sys.argv: DEBUG = 2  # ...  print tiempo captura
elif '-p' in sys.argv: DEBUG = 100 # ...  print detalle de cada campo de captura

from Parametros_FV import *
#if usar_goodwe == 0:
#    print (subprocess.getoutput('sudo systemctl stop goodwe'))
#    sys.exit()


import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_goodwe.py') #+Style.RESET_ALL)
print()


async def get_runtime_data():

    inverter = await goodwe.connect(IP_GOODWE)
    runtime_data = await inverter.read_runtime_data()
        
    if DEBUG == 1:
        print (runtime_data)
        print('=' * 80)
        
    if DEBUG == 100:
        for sensor in inverter.sensors():
            if sensor.id_ in runtime_data:
                print(Fore.GREEN+f"{sensor.id_}:"+ Fore.RESET + f"{sensor.name}" + Fore.CYAN + f" = {runtime_data[sensor.id_]} {sensor.unit}")
            else:
                print (Fore.YELLOW+f"{sensor.id_}: \t\t {sensor.name} =  NO HAY sensor" )
        print('=' * 80)
        
    return runtime_data


if usar_goodwe == 1:
    try: #inicializamos BD
        # No se crea tabla especifica de fronius              
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()

        Sql = f""" CREATE TABLE IF NOT EXISTS `goodwe` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `Tiempo` datetime NOT NULL,
          `xxxx` float NOT NULL DEFAULT 0,
          `yyyy` float NOT NULL DEFAULT 0,
          PRIMARY KEY (`id`),
          KEY `Tiempo` (`Tiempo`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci
        """                
        """
        import warnings # quitamos el warning que da si existe la tabla equipos
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            cursor.execute(Sql)   
        db.commit()
        """
        try:
            cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('GOODWE','{}'))   
            db.commit()
        except:
            pass     
    except:
        print (Fore.RED+ 'ERROR inicializando BD RAM')
        sys.exit()

while True:
    try:
        ee = 0
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        t1= time.time()
        ee = 10
        datos = asyncio.run(get_runtime_data())
        t2= time.time()
        
        
        if DEBUG == 2: 
          print(Fore.YELLOW +f"{tiempo}: Tiempo de captura = {(t2-t1):.0f} sg")
        
        ee = 20
        if datos != None :
            try:####  ARCHIVOS RAM en BD ############ 
                salida = json.dumps(datos)
                ee = 30
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'GOODWE'") # grabacion en BD RAM
                cursor.execute(sql)
                db.commit()
            except:
                print(Fore.RED+f'error, Grabacion tabla RAM equipos en FRONIUS')

        time.sleep(max (t_muestra_goodwe-(time.time()-t1),0))    
        
        
    except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
        break
    except:
        print(f"{tiempo} - error {ee}")
        time.sleep(5)
        #sys.exit()
