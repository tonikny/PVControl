#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-03-28

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

parametros_bateria = ['AH','CP','EC','vsis']
parametros_ads     = ['RES','SHUNT','Temperatura_sensor',
                      'usar_mux','pin_ADS_mux1' ]
parametros_mezcla =  ['_sensor',
                      'usar_', '_hibrido', '_victron', '_bmv','_sma','_si','_sb1','_sb2',
                      'IP_','_srne']

parametros_simular = ['simular =','simular_reles']

parametros_hibrido = ['dev_hibrido','t_muestra_hibrido']
parametros_fronius = ['_sensor','_fronius','IP_FRONIUS']
parametros_huawei = ['_sensor','_huawei','IP_HUAWEI']
parametros_goodwe = ['_sensor','_goodwe','IP_GOODWE']

f_salida = open("/home/pi/PVControl+/Parametros_FV.aux", "w") # Fichero auxiliar


print()
print (Fore.CYAN + ' MENU SELECCION DEL TIPO DE INSTALACION FV'+Fore.GREEN)
print()
print ('     0 = Usar archivo Parametros_FV.py actual')
print()
print ( Fore.CYAN +'   ########## SISTEMAS CON BATERIA ##############'+Fore.GREEN)
print ('     1 = PCB de PVControl+   (copia el archivo Parametros_FV_ADS.py en Parametros_FV.py y continua)')
print ('     2 = HIBRIDO tipo Axpert (copia el archivo Parametros_FV_HIBRIDO.py en Parametros_FV.py y continua)')
print()
print ( Fore.CYAN +'   ########## SISTEMAS SIN BATERIA ##############'+Fore.GREEN)
print ('     11 = FRONIUS SIN BATERIA (copia el archivo Parametros_FV_FRONIUS.py en Parametros_FV.py y continua)')
print ('     12 = HUAWEI SIN BATERIA (copia el archivo Parametros_FV_HUAWEI.py en Parametros_FV.py y continua)')
print ('     13 = GOODWE SIN BATERIA (copia el archivo Parametros_FV_GOODWE.py en Parametros_FV.py y continua)')

print()
print ( Fore.CYAN +'   ########## OTROS SISTEMAS ##############'+Fore.GREEN)
print ('     99 = Mezcla u otras instalaciones (SRNE, SMA, ...)')
print ('          copia el archivo "patron" Parametros_FV_DIST.py en Parametros_FV.py y continua)')

print ()
print (Fore.CYAN + ' Elije Tipo Instalacion FV'+Fore.GREEN)

Tipo_instalacion = click.prompt('    ', type=str, default='0')

fichero2 = '/home/pi/PVControl+/Parametros_FV.py'
if Tipo_instalacion == '1': # ADS
    parametros = parametros_bateria + parametros_ads
    texto = ' Configuracion para PCB'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_ADS.py'
    shutil.copy(fichero1, fichero2)
    
elif Tipo_instalacion == '2': # Hibrido
    parametros = parametros_bateria + parametros_hibrido
    texto = ' Configuracion para HIBRIDO'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_HIBRIDO.py'
    shutil.copy(fichero1, fichero2)
    
elif Tipo_instalacion == '11': # Fronius
    parametros = parametros_fronius
    texto = ' Configuracion para FRONIUS'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_FRONIUS.py'
    shutil.copy(fichero1, fichero2)

elif Tipo_instalacion == '12': # Huawei
    parametros = parametros_huawei
    texto = ' Configuracion para HUAWEI'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_HUAWEI.py'
    shutil.copy(fichero1, fichero2)

elif Tipo_instalacion == '13': # goodwe
    parametros = parametros_goodwe
    texto = ' Configuracion para GOODWE'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_GOODWE.py'
    shutil.copy(fichero1, fichero2)

    
elif Tipo_instalacion == '99': # Otros
    parametros = parametros_bateria + parametros_ads + parametros_hibrido + parametros_mezcla
    texto = ' Configuracion para OTROS SISTEMAS'
    fichero1 ='/home/pi/PVControl+/Parametros_FV_DIST.py'
    shutil.copy(fichero1, fichero2)
    
elif Tipo_instalacion == '0': # Fichero actual
    parametros = parametros_bateria + parametros_ads + parametros_hibrido + parametros_mezcla
    texto = ' Configuracion usando Parametros_FV.py actual'
    
print (Fore.CYAN + texto)

narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-sim':    parametros += parametros_simular

try:
    from Parametros_FV import * # para conexion a la BD
except:
    print (Fore.RED, '#' * 80)
    print (Fore.CYAN,'NO EXISTE EL FICHERO Parametros_FV.py - Ejecute de nuevo y elija otra opcion')
    print (Fore.RED, '#' * 80)
    sys.exit()

# ######## ACTUALIZACION BD (CAMPOS,..) 
try:
    print ()
    print(' Actualizaciones en BD pendientes desde imagen')
    
    import Actualizar_BD # lo pongo en programa aparte para poder ejecutarse por separado
    
    print (Fore.GREEN+ 'OK')     
except:
    print( ' ERROR EN BD ')


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
                
                if 'vsis' in p: # Adaptacion tabla parametros en BD
                    print()
                    print (Fore.RED + '  ATENCION.. SE ADAPTARA LA BASE DE DATOS PARA EL VOLTAJE SELECCIONADO')
                    print ('  Para una adaptacion optima :')
                    print ('   - Adaptar la tabla paramemtros de la Base de Datos')
                    
                    print()
                    bd_act = click.prompt(Fore.GREEN + ' 1= Actualiza BD  --  0: No Actualiza', type=str, default='1')
                    if bd_act == '1':
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
        
                        if '2' in ip:
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '28.8',Vabs = '28.8',Vflot = '27.2',Vequ = '29.6'"
                            print (Fore.CYAN +'tabla parametros configurada a 24V')
                            
                        elif '4' in ip:
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '57.6', Vabs = '57.6',Vflot = '54.4', Vequ = '59.2'"
                            print (Fore.CYAN +'tabla parametros configurada a 48V')
                            
                        elif '1' in ip:
                            Sql = "sensor_PID = 'Vbat',objetivo_PID = '14.4', Vabs = '14.4',Vflot = '13.6', Vequ = '14.8'"
                            print (Fore.CYAN +'tabla parametros configurada a 12V')
                        
                        Sql = "UPDATE parametros SET nuevo_soc = '100',"+Sql # Ponemos SOC a 100%
                        print(Sql)
                        cursor.execute(Sql)
                        db.commit()
                        cursor.close()
                        db.close()
                
                elif 'AH' in p: # Valores PID en tabla parametros dependiendo de si se usa bateria o no
                    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                    cursor = db.cursor()
                    
                    if float(Valor) < 1.0:
                        AH_valor = 'SIN BATERIA'
                        Sql = """sensor_PID = 'Wred',objetivo_PID = '0', Vabs = '0',Vflot = '0', Vequ = '0' ,
                                 Kp = '0.1',Ki = '0', Kd = '0'"""
                    else:
                        AH_valor = 'CON BATERIA'
                        Sql = """sensor_PID = 'Vbat', Kp = '10',Ki = '0', Kd = '0'"""
                    
                    print (Fore.CYAN +'Instalacion ',AH_valor,' se adapta PID en tabla parametros....')
                    Sql = "UPDATE parametros SET " + Sql
                    print(Sql)
                    print()
                    print (Fore.CYAN +' ...Valores PID en tabla parametros configurada a sistemas ',AH_valor)
                    
                    cursor.execute(Sql)
                    db.commit()
                    cursor.close()
                    db.close()
              
                break # siguiente parametro
                
            else:
                linea_s = linea
                
        f_salida.write(linea_s)  # Grabamos linea en fichero temporal 

f_salida.close()

print()
print (Fore.RED + '  --- CONFIGURACION Parametros_FV.py FINALIZADA --- ') 
print()
confirmacion = click.prompt(Fore.GREEN + '    Pulsa 1 para grabar o 0 para cancelar', type=str, default='1')

if confirmacion == '1':
    os.rename('/home/pi/PVControl+/Parametros_FV.py', '/home/pi/PVControl+/Parametros_FV.back')
    os.rename('/home/pi/PVControl+/Parametros_FV.aux', '/home/pi/PVControl+/Parametros_FV.py')
    
    print (Fore.RED + '  --- NUEVO FICHERO Parametros_FV.py CREADO... ')
    print()
    
    # ############# Adaptacion Web #########################################
    exec(open("/home/pi/PVControl+/PVControl_Configuracion_Web.py").read()) # adaptacion Web segun Parametros_FV.py
    # #######################################################################
    
    print (Fore.CYAN +'#' * 50)
    print ('#' * 50)
    print (Fore.RED + '  --- SI HA MODIFICADO EL FICHERO Parametros_FV.py ES NECESARIO REINICIAR PVControl+.. ')
    print (Fore.CYAN +'#' * 50)
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

