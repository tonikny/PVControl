#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-09
import os,glob
import subprocess
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

carpeta= '/home/pi/PVControl+/etc/systemd/system/*.*'

print(Fore.YELLOW+'######## Parando Sevicios #########')
for f in glob.glob(carpeta):
    if os.path.isfile(f):
        print (f)
        print (Fore.RESET+'Parando Servicio '+ Fore.GREEN +f'{f}'+ Fore.RESET)
        
        res = subprocess.run(['sudo','systemctl', 'stop', f'{f[39:]}'], capture_output=True)
        print (Fore.BLUE,res.stdout[-50:])   
    else:
        print(Fore.RED+f'{f} no es un fichero')
    
print()
print(Fore.CYAN+'######## Proceso Completado #########')
