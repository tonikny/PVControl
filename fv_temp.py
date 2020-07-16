#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-05-29

import time, glob, sys, subprocess

# Librerias y Parametros PVControl+
from Parametros_FV import *
import pickle

"""
#if Temperatura_sensor.find ('d_ds18b20') == -1:
if usar_ds18b20 == 0:
    print ('sensor ds18b20 no seleccionado')
    print (subprocess.getoutput('sudo systemctl stop fv_temp'))
    sys.exit()
"""

archivo_ram = '/run/shm/datos_ds18b20.pkl'

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

while True:
    Temp_D= {}
    sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
    Ctemp = 0       # Contador del numero de sensores
    
    for sensor in sensores:
        tfile = open(sensor)
        texto = tfile.read()
        tfile.close()
        temp_datos = texto.split("\n")[1].split(" ")[9]
        temp= round(float(temp_datos[2:]) / 1000,2)
        if DEBUG >= 2: print (sensor, temp)
        
        Temp_D['Temp'+str(Ctemp)] = temp 
        Ctemp += 1
        time.sleep(1)

    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_cpu = float(f.read())/1000
        Temp_D['Temp_cpu'] = temp_cpu 
    except:
        f.close()
    
    
    try:
        Temp_D['Tiempo'] = '_'+time.strftime("%Y-%m-%d %H:%M:%S")
        Temp_D['Tiempo_sg'] =  time.time()
        if DEBUG >= 1:print (Temp_D)
        
        with open(archivo_ram, 'wb') as f:
            pickle.dump(Temp_D, f)
            
        time.sleep(10)
    except:
        print ('Error grabacion fichero datos_ds18b20')
