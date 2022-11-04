#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2022-02-10

import time, glob, sys, subprocess
import MySQLdb

# Librerias y Parametros PVControl+
from Parametros_FV import *
import json

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 100
else:
    DEBUG = 0
if DEBUG !=0: print ('DEBUG=',DEBUG)

try: #inicializamos registros en BD RAM
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  ('TEMP','{}'))
    db.commit() 
except:
    pass # registro ya creado previamente

finally:
    cursor.close()
    db.close()
    
while True:
    Temp_D= {}
    
    ## Ds18b20
    sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    if sensores: Temp_D['Ds18b20']= {}
    Ctemp = 0       # Contador del numero de sensores
    
    for sensor in sensores:
        tfile = open(sensor)
        texto = tfile.read()
        tfile.close()
        try:
            temp_datos = texto.split("\n")[1].split(" ")[9]
            temp= round(float(temp_datos[2:]) / 1000,2)
        except:
            time.sleep(1)
            continue
        if DEBUG >= 2: print (sensor, temp)
        
        Temp_D['Ds18b20']['Temp'+str(Ctemp)] = temp 
        Ctemp += 1
        time.sleep(1)

    ## RPI CPU
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_cpu = float(f.read())/1000
        Temp_D['Temp_cpu'] = temp_cpu 
    except:
        f.close()
    
    
    try:
        if DEBUG >= 1:print (Temp_D)
    
    ### Grabacion en BD
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S") 
        salida = json.dumps(Temp_D)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'TEMP'") # grabacion en BD RAM
        cursor.execute(sql)
        cursor.close()
        db.close()
        
        
        time.sleep(10)
    except:
        print ('Error grabacion BD tabla equipos')
