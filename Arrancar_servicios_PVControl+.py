#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-10-28
import os,glob
import subprocess
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

usar_motioneye=0

from Parametros_FV import *


carpeta= '/home/pi/PVControl+/etc/systemd/system/*.*'

print(Fore.YELLOW+'######## Activando Sevicios #########')
for f in glob.glob(carpeta):
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
#Crontab
print()
print(Fore.YELLOW+'######## Activando Procesos CRONTAB #########')
res = subprocess.run(['sudo','chown', 'root','/home/pi/PVControl+/etc/cron.d/pvcontrol'])
res = subprocess.run(['sudo','ln', '-s','/home/pi/PVControl+/etc/cron.d/pvcontrol','/etc/cron.d/pvcontrol'], capture_output=True)
print (Fore.GREEN+ '  ---- OK -----')

print()
print(Fore.CYAN+'######## Proceso Completado #########')
