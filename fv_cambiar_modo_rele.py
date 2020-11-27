#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-10-21


import time,sys
import datetime
import MySQLdb 

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Actualizando'+ Fore.GREEN +' Reles PVControl') #+Style.RESET_ALL)

#Parametros Instalacion FV
from Parametros_FV import *

#Comprobacion argumentos en comando 
narg = len(sys.argv)

print(sys.argv)

orden = sys.argv[2]
nrele = sys.argv[1]

if narg != 3:
    print (Fore.RED + 'numero de argumentos distinto de dos  - recuerda poner Nrele y modo', narg)
    sys.exit()

try:
    i = int(nrele)
except:
    print (Fore.RED + 'no se ha indicado un mumero de rele en el primer argumento',nrele )
    sys.exit()

if orden not in ['PRG','ON','OFF']:
    print (Fore.RED + 'Modo rele no indicado', orden)
    sys.exit()
    
try:
    sql = "UPDATE reles SET modo='"+orden+"' WHERE id_rele=" + nrele
    
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

    msg='Rele '+ nrele + ' puesto a '+ orden
           
except:
    msg='No se puede actualizar la tabla reles con la orden recibida   '
    
print (sql)
print (msg)

