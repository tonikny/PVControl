#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-29-12

import time,sys
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
import json

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p1':    DEBUG = 1
elif str(sys.argv[narg-1]) == '-p2':  DEBUG = 2
elif str(sys.argv[narg-1]) == '-p3':  DEBUG = 3
elif str(sys.argv[narg-1]) == '-p':   DEBUG = 100
else:    DEBUG = 0

print (Fore.RED + 'DEBUG=',DEBUG,Fore.CYAN)

usar_mux = 1

while True:
    if usar_mux > 0:
        archivo_ram='10.147.17.10:/run/shm/datos_mux.json'
        try:
            with open(archivo_ram, 'r') as f:
                d_mux = json.load(f)
                #print(d_mux)
        except:
            print('error lectura '+archivo_ram)
            time.sleep(3)
            continue
    
    hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
    Vbat = 0
    for x in d_mux[2]: Vbat += x
    print(hora,round(Vbat,2), round(Vbat/12,3),d_mux[2])
    time.sleep(5)
    
