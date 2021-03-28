#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-03-08

from datetime import datetime
import requests, time, sys
import MySQLdb

from Parametros_FV import *
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' pvoutput_live.py') #+Style.RESET_ALL)

#Comprobacion argumentos en comando
arg = [x.upper() for x in sys.argv]
arg= arg[1:] # quito argumento con nombre del archivo

print(Fore.BLUE+'Comandos='+Fore.GREEN,arg)

DEBUG = 0 
for x in arg:
    if x[0]=='-': x= x[1:]
    exec(x)

print (Fore.RED + 'DEBUG=',DEBUG)

def update_pvoutput():
    attempt = 0
    
    while(attempt < 5):
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)    
        cursor = db.cursor()
        sql='SELECT  Wh_placa, Whp_bat, Whn_bat, Vbat, Temp, Whp_red, Whn_red FROM datos ORDER BY id DESC LIMIT 1'
        cursor.execute(sql)
        datos = cursor.fetchone()
        
        Wh_placa = int(datos[0])
        Whp_bat = int(datos[1])
        Whn_bat = int(datos[2])
        Vbat = float(datos[3])
        Temp = float(datos[4])
        Whp_red = int(datos[5])
        Whn_red = int(datos[6])
        
        Wh_consumo = Wh_placa - (Whp_bat-Whn_bat) - (Whp_red-Whn_red)
        
        if DEBUG >= 1:
            print (Fore.GREEN+f'Wh_placa={Wh_placa} - Wh_bat={Whp_bat-Whn_bat} - Wh_red={Whp_red-Whn_red}- Wh_con={Wh_consumo}')

        cursor.close()
        db.close()

        dia = datetime.today().strftime('%Y%m%d')
        hora = time.strftime("%H:%M")
 
        PV_OUTPUT_URL = ('https://pvoutput.org/service/r2/addstatus.jsp?'
                          f'key={pvoutput_key}&sid={pvoutput_id}'
                          f'&d={dia}&t={hora}&v1={Wh_placa}&v3={Wh_consumo}&v5={Vbat}&v6={Temp}'
                        )

        if DEBUG >=2: 
            print (Fore.GREEN+PV_OUTPUT_URL)
            print (Fore.YELLOW,'#' * 60)    
  
        r = requests.get(PV_OUTPUT_URL)
##        print (r,r.status_code,requests.codes.ok)
        attempt += 1
        if (r.status_code != requests.codes.ok):
            time.sleep(3)
            print (Fore.RED, "ERROR")
        else:
            break

if __name__ == '__main__':
    if usar_pvoutput == 1:
        update_pvoutput()
    else:
        print (Fore.RED+"Registro PVoutput no actualizado -- Variable usar_pvoutput esta a 0 en Parametros_FV.py")
