#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-11-06

import subprocess, click,sys
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


menu = """
   
   ACTUALIZACION TRAS "git pull"....Continuar?
  
       """
#seguir = click.prompt(Fore.BLUE + menu, type=str, default="S/n")

if not(click.confirm(Fore.BLUE+menu)):
    print(Fore.RED+'saliendo')
    sys.exit()
print ('ejecutando')


#--- Asegurar permisos archivo crontab ---------------------
try:
    res = subprocess.run(['sudo','chown', 'root:root','/home/pi/PVControl+/etc/cron.d/pvcontrol'])
    res = subprocess.run(['sudo','ln', '-s','/home/pi/PVControl+/etc/cron.d/pvcontrol','/etc/cron.d/pvcontrol'], capture_output=True)
except:
    print (Fore.RED+'error creacion link crontab')
