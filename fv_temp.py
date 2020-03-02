#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-01-11

import time,csv,sys
import datetime,glob

#Parametros Instalacion FV
from Parametros_FV import *

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':
    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':
    DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':
    DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':
    DEBUG = 10
else:
    DEBUG = 0
print ('DEBUG=',DEBUG)

Temp_D = ([0] * 8)

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
        if DEBUG >=2: print (sensor, temp)
        
        Temp_D[Ctemp]=temp 
        Ctemp +=1
        time.sleep(1)
        
     
         
    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        
        if DEBUG >=1:print (tiempo,tiempo_sg,Temp_D)
        
        with open('/run/shm/datos_temp.csv', mode='w') as f:
            nombres = ['Tiempo_sg','Tiempo','Temp0', 'Temp1', 'Temp2','Temp3', 'Temp4', 'Temp5']
            datos = csv.DictWriter(f, fieldnames=nombres)
            datos.writeheader()
            datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,
                'Temp0': Temp_D[0],'Temp1': Temp_D[1],'Temp2':Temp_D[2],
                'Temp3': Temp_D[3],'Temp4': Temp_D[4],'Temp5':Temp_D[5]})
            
        
        with open('/run/shm/datos_temp.csv', mode='r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                d_temp = row # Capturo los valores del fichero datos_temp.csv
        
        
        if DEBUG >=1: print (d_temp['Temp'+str(indice_sensortemperatura)])
        
        
        
        time.sleep(10)
        
    except:
        print ('Error grabacion fichero datos_temp.csv')
