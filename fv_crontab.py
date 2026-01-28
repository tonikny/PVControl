#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-13

import time,sys
from datetime import datetime

import subprocess
import MySQLdb

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

basepath = '/home/pi/PVControl+/'
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
parametros_FV_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"

DEBUG = 100 if '-p' in sys.argv else 0

def logBD(texto) : # Incluir en tabla de Log
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(time.strftime("%Y-%m-%d %H:%M:%S"),texto[:49]))
        
        db.commit()
    except:
        db.rollback()
    
    finally:
        cursor.close()
        db.close()
            
    return


print('Iniciando fv_crontab.py.....')
try:
    #Parametros Instalacion FV
    exec(open(parametros_FV_DIST).read(),globals()) #cargo Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
    exec(open(parametros_FV).read(),globals()) #cargo Parametros_FV.py
except:
    print (f'Error .... NO se pueden cargar Parametros_FV.py')
    sys.exit()

comandos = {}

for c in crontab:
    comandos[c] = crontab[c]
    comandos[c]['tiempo'] = time.time()

#print(comandos)

while True:
    ee = 10
    t1 = time.time()
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    minuto = time.strftime("%H:%M")
    procesos = {}
    try:
        ee = 20
        for c in comandos:
            ee = 30
            if comandos[c]['activo'] > 0:
                ee = 40
                if comandos[c]['periodo'] > 0 and (time.time() - comandos[c]['tiempo'])/60 > comandos[c]['periodo']:                
                    ee = 42
                    if DEBUG > 0:
                        print(Fore.RED+f"{tiempo} - {Fore.CYAN}Periodo {Fore.GREEN}{comandos[c]['comando']}")    
                    try:
                        procesos[c] = subprocess.Popen(comandos[c]['comando'])
                        
                        if DEBUG > 0:
                            out, err = procesos[c].communicate()
                            print ('out=', out)
                            print ('err=', err)
                        
                        if comandos[c]['log'] == 1:  logBD(f"CRON_PER:{c}")
                    except:
                        if DEBUG > 0: print(f"Error en ejecucion comando {c} ")
                        logBD(f"CRON_PER ERROR-{c}")
                        
                    comandos[c]['tiempo'] = time.time()
            
                if minuto in comandos[c]['horas']:
                    if DEBUG > 0:
                        print(Fore.RED+f"{tiempo} - {Fore.CYAN}Hora {Fore.GREEN}{comandos[c]['comando']}")    
                    try:
                        procesos[c] = subprocess.Popen(comandos[c]['comando'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        if comandos[c]['log'] == 1: logBD(f"CRON_HOR-{c}")
                    
                    except:
                        if DEBUG > 0: print(f"Error en ejecucion comando {c} ")
                        logBD(f"CRON_HOR ERROR - {c}")
                        
                    comandos[c]['tiempo'] = time.time()
    except:
        if DEBUG > 0: print ('Error no controlado')
        logBD(f"CRONTAB ERROR - {c}")
        
    # Espera hasta comienzo minuto siguiente
    espera = 60 - datetime.utcnow().second
    time.sleep(espera)
    #print (tiempo, espera, procesos)
    #print()
    
    exec(open(parametros_FV_DIST).read(),globals()) #recargo Parametros_FV_DIST.py por si hay cambios
    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
    
    for c in crontab:
        tc = comandos[c]['tiempo'] if 'tiempo' in comandos[c] else time.time()
        comandos[c] = crontab[c]
        comandos[c]['tiempo'] = tc
    
    
