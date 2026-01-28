#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-12
import os,glob
import subprocess, sys
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

usar_motioneye=0

from Parametros_FV import *

#sudo ln -s /home/pi/PVControl+/etc/systemd/system/fv_crontab.service /etc/systemd/system/fv_crontab.service

carpeta= '/home/pi/PVControl+/etc/systemd/system/'

print(Fore.YELLOW+'######## Activando Sevicios #########')

if len (sys.argv) > 1:
    servicios = glob.glob(carpeta+sys.argv[1]+'.service')
else:
    servicios = glob.glob(carpeta+'*.*')


for f in servicios:
    if os.path.isfile(f):
        print (Fore.RESET+'Procesando archivo.... '+ Fore.GREEN+f'{f}'+ Fore.RESET)
        res = subprocess.run(['sudo','ln', '-s',f'{f}',f'/etc/systemd/system/{f[39:]}'], capture_output=True)
        res = subprocess.run(['sudo','systemctl', 'enable', f'{f[39:]}'], capture_output=True)
        res = subprocess.run(['sudo','systemctl', 'restart', f'{f[39:]}'], capture_output=True)
        res = subprocess.run(['sudo','systemctl', 'status', f'{f[39:]}'], capture_output=True)
        print (Fore.BLUE,res.stdout[-50:])   
    else:
        print(Fore.RED+f'{f} no es un fichero')
        
if usar_motioneye == 0: 
        res = subprocess.run(['sudo','systemctl', 'stop', 'motioneye'], capture_output=True)
        res = subprocess.run(['sudo','systemctl', 'disable', 'motioneye'], capture_output=True)
    
#Paginas web
print()
print(Fore.YELLOW+'######## Activando WEB PVControl+ #########')
res = subprocess.run(['sudo','rm', '-R','/var/www/html'])
res = subprocess.run(['sudo','ln', '-s','/home/pi/PVControl+/html','/var/www'])
print (Fore.GREEN+ '  ---- OK -----')

print()
print(Fore.CYAN+'######## Proceso Completado #########')
