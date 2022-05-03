#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2022-05-01


# Programa de instalacion de Home Assistant en docker
#

import os
import time
import subprocess #,commands
import sys
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()
import click

time.sleep(1)

lista = [# HA
         
         
         # Home Assistant
         'docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Europe/Madrid -v /home/pi/PVControl+/HA:/config --network=host  ghcr.io/home-assistant/home-assistant:stable',
           ]



for i in lista:
    print (Style.BRIGHT + Fore.YELLOW + '#' * 60)
    print (i)
    print ('#' * 60 + Fore.RESET)
    res = subprocess.run(i, shell=True)
    if res.returncode == 0:
        print (Style.BRIGHT + Fore.GREEN + '-' * 60)
        print('returncode:', res.returncode)
        print ('-' * 60)
    else:
        print (Style.BRIGHT + Fore.RED + '-' * 60)
        print('returncode:', res.returncode)
        print ('-' * 60)
        print ()
        salir = click.prompt(Fore.CYAN + '  Error detectado.... pulse una 0 para seguir o 1 para abortar ', type=str, default='0')
        if salir == '1': sys.exit()
        
    print(Fore.RESET)
    print()
    time.sleep(1)
    print(' ')
    
print()

print(Fore.YELLOW+'######## Instalado HA  #########')
print(Fore.YELLOW+'######## ponga en un navegador web la http://IP_raspberry:8123    y siga las instrucciones de configuracion')



print()
print(Fore.CYAN+'######## Proceso Completado #########')

