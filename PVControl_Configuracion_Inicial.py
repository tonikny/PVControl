#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-11-20

import time,sys,os
import MySQLdb 

import subprocess,shutil
import click

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""

from Parametros_FV import * # para conexion a la BD

print()
print (Style.BRIGHT + Fore.YELLOW +'#' * 90)
print('  PROGRAMA DE CONFIGURACION INICIAL DE PVControl+')
print(Fore.CYAN)
print(' Este programa realiza una configuracion BASICA del archivo Parametros_FV.py')
print (' Para un uso mas avanzado edite y modifique el fichero Parametros_FV.py')
print (Fore.YELLOW)
print('#' * 90)

print()
print (Fore.RED + '  ATENCION.. SE CAMBIARAN LOS PARAMETROS DEL FICHERO Parametros_FV.py')
#salir = input(Fore.CYAN +'Si no esta seguro pulse 0 para salir o 1 para continuar ')
print()
salir = click.prompt(Fore.CYAN + '  Si no esta seguro pulse 0 para salir o 1 para continuar ', type=str, default='0')

if salir == "1": pass
else: sys.exit()

parametros_comunes = ['AH','CP','EC','vsis']
parametros_mezcla = ['_sensor',
                     'usar_hibrido', 'grabar_datos_hibrido',
                     '_victron',
                     '_bmv',
                     'usar_sma','usar_si','usar_sb1','usar_sb2','IP_SI','IP_SB1','IP_SB2','grabar_datos_sma',
                     '_srne', 
                     ]

parametros_hibrido = ['dev_hibrido','t_muestra_hibrido']

parametros_ads = ['RES','SHUNT','Temperatura_sensor',
                  'usar_mux','pin_ADS_mux1'   
                     ]

f_salida = open("/home/pi/PVControl+/Parametros_FV.aux", "w")

print()

print (Fore.CYAN + ' Menu seleccion del tipo de dispositivo de captura'+Fore.GREEN)
print ('   0 = Usar archivo Parametros_FV.py actual')
print ('   1 = PCB de PVControl+   (copia el archivo Parametros_FV_ADS.py en Parametros_FV.py y continua)')
print ('   2 = HIBRIDO tipo Axpert (copia el archivo Parametros_FV_HIBRIDO.py en Parametros_FV.py y continua)')

print ('   99 = Mezcla u otras instalaciones')

print ()
print (Fore.CYAN + ' Elije el dispositivo de captura'+Fore.GREEN)


Tipo_instalacion = click.prompt('    ', type=str, default='0')

if Tipo_instalacion == '1':
    parametros = parametros_comunes + parametros_ads
    shutil.copy('/home/pi/PVControl+/Parametros_FV_ADS.py', '/home/pi/PVControl+/Parametros_FV.py')
    
    print()
    print (Fore.CYAN +' Configuracion para PCB')
    
elif Tipo_instalacion == '2':
    parametros = parametros_comunes + parametros_hibrido
    shutil.copy('/home/pi/PVControl+/Parametros_FV_HIBRIDO.py', '/home/pi/PVControl+/Parametros_FV.py')
    print()
    print (Fore.CYAN +' Configuracion para HIBRIDO')
    
elif Tipo_instalacion == '99' or Tipo_instalacion == '0':
    parametros = parametros_comunes + parametros_ads + parametros_hibrido + parametros_mezcla

#print (parametros)    
print()
print (Fore.YELLOW +'#' * 90)
print('  INTRODUCCION DE PARAMETROS DE PVControl+')
print(Fore.CYAN)
print(' Introduzca los datos de los parametros y pulse "INTRO"')
print (' Pulsar "INTRO" sin incluir el dato selecciona el valor que aparece por defecto')
print (Fore.YELLOW)
print('#' * 90)

print()


with open('/home/pi/PVControl+/Parametros_FV.py') as f:
    for linea in f:
        #print (Fore.BLUE + linea)
        for p in parametros:
            p1 = linea.find(p)
            
            if p1 >= 0:
                print('-' * 70)
                p2 = linea.find('=')
                p = linea[:p2] # pongo el p el nombre completo del parametro y sus espacios 
                p3 = linea.find('#')
                Valor = linea[p2 + 1:p3].rstrip()
                Valor = Valor.lstrip()
                comillas = Valor.find('"') # Compruebo si el parametro debe llevar comillas
                if comillas >= 0:
                    Valor = Valor[1:-1]
                                        
                Descripcion = linea[p3 + 1:]
                
                print (Fore.BLUE + 'Parametro = '+ p,Fore.RED,' Valor actual = '+ Valor)
                print (Fore.YELLOW+'    Descripcion : '+Descripcion) 
                
                ip = click.prompt(Fore.GREEN + '    Nuevo valor para '+ p +'?', type=str, default=Valor)
                
                if comillas >= 0: ip = '"' + ip + '"'        # Añado comillas
                ip = ip + " " * (p3 - p2 - len(ip) - 2)      # Añados espacios
                linea_s = p +  "= " + ip + "#" + Descripcion # Completo la nueva linea
                
                print ('original: ', linea, end='')
                print ('final   : ', linea_s)
                
                if 'vsis' in p: # Adaptacion de escalas de la Web y tabla parametros en BD
                    print()
                    print (Fore.RED + '  ATENCION.. SE ADAPTARA LA WEB y BASE DE DATOS PARA EL VOLTAJE SELECCIONADO')
                    print ('  Para una adaptacion optima :')
                    print ('   - Editar el archivo ubicado en ..PVControl+/html/Parametros_Web.js')
                    print ('   - Adaptar la tabla paramemtros de la Base de Datos')
                    
                    print()
                    web_act = click.prompt(Fore.GREEN + ' 1= Actualiza Web  --  0: No Actualiza', type=str, default='1')
                    if web_act == '1':
                        shutil.copy('/home/pi/PVControl+/html/Parametros_Web.js', '/home/pi/PVControl+/html/Parametros_Web_back.js')
                        # Para actualizacion Tabla Parametros de la BD
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
        
                        if '2' in ip:
                            shutil.copy('/home/pi/PVControl+/html/Parametros_Web_24V.js', '/home/pi/PVControl+/html/Parametros_Web.js')
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '28.8',Vabs = '28.8',Vflot = '27.2',Vequ = '29.6'"
                            print (Fore.CYAN +'Web configurada a 24V')
                            
                        elif '4' in ip:
                            shutil.copy('/home/pi/PVControl+/html/Parametros_Web_48V.js', '/home/pi/PVControl+/html/Parametros_Web.js')
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '57.6', Vabs = '57.6',Vflot = '54.4', Vequ = '59.2'"
                            print (Fore.CYAN +'Web configurada a 48V')
                            
                        elif '1' in ip:
                            shutil.copy('/home/pi/PVControl+/html/Parametros_Web_12V.js', '/home/pi/PVControl+/html/Parametros_Web.js')
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '14.4', Vabs = '14.4',Vflot = '13.6', Vequ = '14.8'"
                            print (Fore.CYAN +'Web configurada a 12V')
                        
                        Sql = "UPDATE parametros SET nuevo_soc = '100', "+Sql
                        print(Sql)
                        cursor.execute(Sql)
                        db.commit()
                        cursor.close()
                        db.close()
                
                elif 'usar_mux' in p: # adaptacion inicio.php e index.php dependiendo de si se usa mux o no
                    if int(ip) > 0:
                        shutil.copy('/home/pi/PVControl+/html/inicio_con_celdas.php', '/home/pi/PVControl+/html/inicio.php')
                        shutil.copy('/home/pi/PVControl+/html/index_con_celdas.php', '/home/pi/PVControl+/html/index.php')
                        print (Fore.CYAN +'Pagina de inicio.php y index.php configuradas CON celdas')
                    else:
                        shutil.copy('/home/pi/PVControl+/html/inicio_sin_celdas.php', '/home/pi/PVControl+/html/inicio.php')
                        shutil.copy('/home/pi/PVControl+/html/index_sin_celdas.php', '/home/pi/PVControl+/html/index.php')
                        print (Fore.CYAN +'Pagina de inicio.php y index.php configuradas SIN celdas')
                    
                break
            else:
                linea_s = linea
                
        f_salida.write(linea_s)  # Grabamos linea en fichero temporal 

f_salida.close()

print()
print (Fore.RED + '  --- CONFIGURACION FINALIZADA --- ') 
print()
confirmacion = click.prompt(Fore.GREEN + '    Pulsa 1 para grabar o 0 para cancelar', type=str, default='0')

if confirmacion == '1':
    os.rename('/home/pi/PVControl+/Parametros_FV.py', '/home/pi/PVControl+/Parametros_FV.back')
    os.rename('/home/pi/PVControl+/Parametros_FV.aux', '/home/pi/PVControl+/Parametros_FV.py')
    
    print (Fore.RED + '  --- NUEVO FICHERO Parametros_FV.py CREADO... ')
    print()
    
    print (Fore.RED + '  --- SI HA MODIFICADO EL FICHERO Parametros_FV.py ES NECESARIO REINICIAR PVControl+.. ')
    print()
    
    r_servicios = click.prompt(Fore.GREEN + '    Pulsa 1 para reiniciar PVControl+ o 0 para reinicio manual', type=str, default='1')
    print(r_servicios)
    
    if r_servicios == '1':
        subprocess.run(['bash','./Arrancar_Servicios_PVControl+.sh'], check=True)
        print()
        print (Fore.RED + '  --- SERVICIOS PVControl+ REINICIADOS --- ')
    else:
        print()
        print (Fore.RED + '  --- SERVICIOS PVControl+ NO REINICIADOS --- ')
        print ( ' Recuerde reiniciar manualmente los servicios afectados con '+ Fore.CYAN +
                '\n sudo systemctl enable nombre_servicio'+
                '\n sudo systemctl restart nombre_servicio\n')
        
else:
    print()
    print (Fore.RED + '  --- CANCELADA MODIFICACION DEL ARCHIVO Parametros_FV.py --- ')

salir = click.prompt(Fore.GREEN + '    Pulsa INTRO para salir', type=str, default='')

