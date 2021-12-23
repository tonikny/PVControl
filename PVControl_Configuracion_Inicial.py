#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-23

import time,sys,os
import MySQLdb 

import subprocess,shutil
import click

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

try:
    from Parametros_FV import *
except:
    pass


print()
print (Style.BRIGHT + Fore.YELLOW +'#' * 90)
print('  PROGRAMA DE CONFIGURACION INICIAL DE PVControl+')
print(Fore.CYAN)
print(' Este programa realiza la configuracion de PVControl+')
#print (' Para un uso mas avanzado edite y modifique el fichero Parametros_FV.py')
print (Fore.YELLOW)
print('#' * 90)

print()
#print (Fore.RED + '  ATENCION.. SE CAMBIARAN LOS PARAMETROS DEL FICHERO Parametros_FV.py')
print()
salir = click.prompt(Fore.CYAN + '  Si no esta seguro pulse 0 para salir o 1 para continuar ', type=str, default='0')

if salir == "1": pass
else: sys.exit()

print()
print('#' * 80)
print (Fore.YELLOW+' Se va a editar el archivo de configuracion Parametros_FV.py....' )
print()
print ('..... pulse 1 para usar el archivo actual de Parametros_FV.py')
print ('..... Pulse 2 si es la primera configuracion y usar el archivo patron Parametros_FV_DIST.py')
print()
print ('..... Pulse 0 para seguir sin modificar el archivo Parametros_FV.py')


s = click.prompt('    ', type=str, default='0')


if s== '1':
    archivo = 'Parametros_FV.py'
elif s == '2':
    archivo = 'Parametros_FV_DIST.py'
else:
    archivo = ''
    
if archivo != '':  
    hora =   time.strftime("%Y-%m-%d_%H:%M")
    fichero1 ='/home/pi/PVControl+/Parametros_FV.py'
    fichero2 = f'/home/pi/PVControl+/Parametros_FV_{hora}.back'
    fichero3 = f'/home/pi/PVControl+/Parametros_FV_DIST.py'
    
    print ()
    try:
        shutil.copy(fichero1, fichero2)
        print (Fore.RED+f'Se crea copia de seguridad de Parametros_FV.py anterior con el nombre...Parametros_FV_{hora}.back') 
    except:
        print ('ERROR.... No existe fichero Parametros_FV.py....se usa el archivo Parametros_FV_DIST como modelo')
        archivo = '2'    
    
    if archivo =='2': shutil.copy(fichero3, fichero1)
        
    print()
    print('#' * 80)
    print (Fore.YELLOW+'Como primer paso se abrira en el editor de textos "geany" el archivo Parametros_FV.py.....')
    print ()
    print(Fore.RED+'ES MUY IMPORTANTE RELLENAR BIEN ESTE ARCHIVO SIN ERRORES DE SINTAXIS')
    print ('LEA EL MANUAL SI TIENE DUDAS DE COMO RELLENAR EL ARCHIVO')
    print(Fore.YELLOW+' MODIFIQUE LO NECESARIO SEGUN SU INSTALACION, ...GUARDE el archivo..... y SALGA de geany para continuar')
    print('#' * 80)

    continuar = click.prompt('pulsa una tecla para seguir.....    ', type=str, default=' ')

    comando = f"geany {fichero1}"
    print ("Comando: ", comando)
    proceso = subprocess.run(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proceso.returncode==0:
        msg = proceso.stdout
    else:
        msg = proceso.stderr
    print (msg)

    continuar = click.prompt('pulsa un tecla para seguir una vez finalizada la edicion de Parametros_FV.py.....    ', type=str, default=' ')



# ######## ACTUALIZACION BD (CAMPOS,..) 
try:
    print ()
    print(' Actualizaciones en BD pendientes desde imagen')
    
    import Actualizar_BD # lo pongo en programa aparte para poder ejecutarse por separado
    
    print (Fore.GREEN+ 'OK')     
except:
    print( ' ERROR EN BD ')

from Parametros_FV import *


db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()

print()
print('#' * 80)
print (Fore.YELLOW+'  Actualización de la tabla parametros para el Control de Excedentes')
print ()
print(Fore.RED+'ES MUY IMPORTANTE DEFINIR LOS CAMPOS DE CONTROL DE EXCEDENTES ACORDES A LA INSTALACION FV')
print ('LEA EL MANUAL SI TIENE DUDAS DE LO QUE TIENE QUE PONER')
#print(Fore.YELLOW+' iNTRODMODIFIQUE LO NECESARIO SEGUN SU INSTALACION, ...GUARDE el archivo..... y SALGA de geany para continuar')
print('#' * 80)
        
sensor_PID = click.prompt(Fore.YELLOW+'Introduce la variable de control de excedentes ', type=str, default='Vbat')
if sensor_PID == 'Vbat':
    Vabs = 14.4 * vsis
    Vflot = 13.2 * vsis
    Vequ = 14.8 * vsis
    Tabs= 3600
    Objetivo_PID = Vabs
    
    Vabs = click.prompt('Introduce valor de Vabs.. ', type=float, default=Vabs)
    Vflot = click.prompt('Introduce valor de Vflot.. ', type=float, default=Vflot)
    Vequ = click.prompt('Introduce valor de Vequ.. ', type=float, default=Vequ)
    Tabs = click.prompt('Introduce valor de Tabs.. ', type=float, default=Tabs)
    
else:
    Vabs = Vflot = Vequ = Objetivo_PID =0
    Objetivo_PID = click.prompt('Introduce el valor objetivo de la variable de control de excedentes ', type=float, default=Objetivo_PID)


Sql = f"UPDATE parametros SET sensor_PID = '{sensor_PID}', objetivo_PID = '{Objetivo_PID}', Vabs = '{Vabs}', Vflot = '{Vflot}', Vequ = '{Vequ}'"
print(Fore.MAGENTA+Sql)
cursor.execute(Sql)
db.commit()

Kd= Ki = 0
if AH > 0: Kp= 10
else: Kp = 0.1

print(Fore.YELLOW)

Kp = click.prompt('Introduce el valor del parametro Kp del control de excedentes ', type=float, default=Kp)
Kd = click.prompt('Introduce el valor del parametro Kd del control de excedentes ', type=float, default=Kd)
Ki = click.prompt('Introduce el valor del parametro Ki del control de excedentes ', type=float, default=Ki)

Sql = f"UPDATE parametros SET Kp = {Kp}, Kd = {Kd}, Ki = {Ki}"
print(Fore.MAGENTA+Sql)
cursor.execute(Sql)
db.commit()


print (Fore.CYAN +'tabla parametros configurada....')
print ('... Recuerda adaptar los parametros del control PID ....Kp, Ki, Kd  para un control mas preciso')

if AH > 0:
    
    SOC = click.prompt(Fore.YELLOW+'Introduce valor del SOC actual de la Bateria.. ', type=float, default=100)
    
    Sql = f"UPDATE parametros SET nuevo_soc = {SOC}" # Ponemos SOC a 100%
    print(Fore.MAGENTA+Sql)
    cursor.execute(Sql)
    db.commit

print (Fore.CYAN +'tabla parametros configurada')

cursor.close()
db.close()

    
# ############# Adaptacion Web #########################################
try:
    exec(open("/home/pi/PVControl+/PVControl_Configuracion_Web.py").read()) # adaptacion Web segun Parametros_FV.py
except:
    print (Fore.BLUE+ '#' * 60)
    print (Fore.RED+ '--------- ERROR en configuracion WEB ---------')
    print (Fore.BLUE+ '#' * 60)
# #######################################################################

    
print (Fore.CYAN +'#' * 50)
print ('#' * 50)
print (Fore.RED + '  --- SI HA MODIFICADO EL FICHERO Parametros_FV.py ES NECESARIO REINICIAR PVControl+.. ')
print (Fore.CYAN +'#' * 50)
print()

r_servicios = click.prompt(Fore.GREEN + '    Pulsa 1 para reiniciar PVControl+ o 0 para reinicio manual', type=str, default='1')
print(r_servicios)
    
if r_servicios == '1':
    subprocess.run(['python3','Arrancar_servicios_PVControl+.py'], check=True)
    print()
    print (Fore.RED + '  --- SERVICIOS PVControl+ REINICIADOS --- ')
else:
    print()
    print (Fore.RED + '  --- SERVICIOS PVControl+ NO REINICIADOS --- ')
    print ( ' Recuerde reiniciar manualmente los servicios afectados con '+ Fore.CYAN +
            '\n sudo systemctl enable nombre_servicio'+
            '\n sudo systemctl restart nombre_servicio\n')
    

salir = click.prompt(Fore.GREEN + '    Pulsa INTRO para salir', type=str, default='')

