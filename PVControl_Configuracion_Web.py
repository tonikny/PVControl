#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-24

import time,sys,os
import MySQLdb 

import subprocess,shutil
import click

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

usar_diybms = 0 # para futuro
from Parametros_FV import * # para ver valores usar_mux  y AH

print()
print (Style.BRIGHT + Fore.YELLOW +'#' * 90)
print('  PROGRAMA DE CONFIGURACION PAGINA PRINCIPAL WEB DE PVControl+')
print(Fore.CYAN)
print(' Este programa realiza una adaptacion de la WEB segun archivo Parametros_FV.py')
print (Fore.YELLOW)
print('#' * 90)

print()
print (Fore.RED + '  ATENCION.. SE CAMBIARAN LOS ARCHIVOS '+ Fore.YELLOW + '(version.inc y Parametros_Web.js')
print()
salir = click.prompt(Fore.CYAN + '  Si no esta seguro pulse 0 para salir o 1 para continuar ', type=str, default='1')

if salir == "1": pass
else: sys.exit()

print ()
version="";
if AH <1 :
    print ('NO se ha dado de alta una BATERIA,por lo que se configura la WEb como.. ', end='')
    print(Fore.RED+' ---- FV SIN BATERIA ----')
    version="RD";
    fichero2 ='/home/pi/PVControl+/html/Parametros_Web_red.js'
                        
else:
    print (Fore.CYAN + 'Dada de alta BATERIA de ' + Fore.RED, AH, 'AH'+ Fore.CYAN,
           ' se configura la Web como', end='')
    print(Fore.RED+' --------- FV CON BATERIA a ', end='')
    if vsis == 1:
        print (' 12V -------')
        fichero2 ='/home/pi/PVControl+/html/Parametros_Web_12V.js'
    elif vsis == 2:
        print (' 24V -------')
        fichero2 ='/home/pi/PVControl+/html/Parametros_Web_24V.js'
    elif vsis == 4:
        print (' 48V -------')
        fichero2 ='/home/pi/PVControl+/html/Parametros_Web_48V.js'
    print()
    
    if usar_mux+ usar_daly + usar_diybms > 0:
        print (Fore.CYAN + 'Se ha dado de alta control de ' + Fore.RED, usar_mux, 'Celdas'+ Fore.CYAN,
           ' por lo que se configura la WEb como')
        print (Fore.RED+' ------ FV CON BATERIA y CONTROL CELDAS -------')
        version="CC";
    else:
        print (Fore.CYAN + 'NO se ha dado de alta control de Celdas',
           ' por lo que se configura la WEb como ')
        print (Fore.RED+' ------ FV CON BATERIA y SIN CONTROL CELDAS --------')
        version="SC";
        
print()

web_act = click.prompt(Fore.GREEN + ' 1= Actualiza Web  --  0: No Actualiza', type=str, default='1')

if web_act == '1':
    # tipo de instalacion
    with open('/home/pi/PVControl+/html/version.inc','w') as f:
        f.write('<?php\n'
                '// Version de la web\n'
                '// SC = bat sin celdas, CC = bat con celdas, RD = sin bat\n'
               f'$version = "{version}";\n'
                '?>')
    # valores web
    shutil.copy(fichero2, '/home/pi/PVControl+/html/Parametros_Web.js')
    
    print ()
    print ('WEB ACTUALIZADA')

