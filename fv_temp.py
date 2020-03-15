#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-03-15

import time,sys
import datetime,glob

#Parametros Instalacion FV
from Parametros_FV import *

from csvFv import CsvFv

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
print ('DEBUG=',DEBUG)

Temp_D ={}

while True:
    sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    tiempo_sg = time.time()
    Ctemp = 0       # Contador del numero de sensores
    
    for sensor in sensores:
        tfile = open(sensor)
        texto = tfile.read()
        tfile.close()
        
        temp_datos = texto.split("\n")[1].split(" ")[9]
        #temp_datos = segundalinea.split(" ")[9]
        
        temp= round(float(temp_datos[2:]) / 1000,2)
        if DEBUG >= 2: print (sensor, temp)
        
        Temp_D['Temp'+str(Ctemp)] = temp 
        Ctemp += 1
        time.sleep(1)

    
    try:
        Temp_D['Tiempo'] = time.strftime("%Y-%m-%d %H:%M:%S")
        Temp_D['Tiempo_sg'] =  time.time()
        
        if DEBUG >= 1:print (Temp_D)
        
        
        if tipo_sensortemperatura == 'DS18B20':
            fichero = '/run/shm/datos_temp.csv'
        else:
            fichero = '/run/shm/datos_temp_DS18B20.csv'

        c = CsvFv(fichero)
        c.escribirCsv(Temp_D)
        
        time.sleep(10)
        
    except:
        print ('Error grabacion fichero datos_temp.csv')
