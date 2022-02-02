#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-10-24

import time,sys,os,glob
import MySQLdb 

import subprocess,shutil
import click

#Parametros Instalacion FV
from Parametros_FV import *

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

from datetime import datetime

###### UBICACION DE LA CARPETA DE BACKUP ###########

carpeta = '/home/pi/PVControl+/backBD/'
comodin_borrado = 'PV*.*'

if not os.path.exists(carpeta):
    os.makedirs(carpeta)
    print (f'Creada carpeta {carpeta}')    

####################################################
#instalar pv (barra progreso) si no esta instalado
res = subprocess.run('dpkg -s pv', shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
if res.returncode == 1:
    res = subprocess.run('sudo apt-get install pv ', shell=True) 
####################################################
    
def borrar_ficheros(carpeta, dias=10): # borra ficheros mas antiguos de X dias en la carpeta definida que cumplan el comodin_borrado
    limite = time.time() - dias * 86400
    nborrados = 0
 
    for f in glob.glob(carpeta):
        if os.path.isfile(f) and os.stat(f).st_mtime < limite:
            try:
                os.remove(f)
                nborrados+=1
                print (f,'---- Borrado fichero ')
            except:
                pass
        else: pass
    return nborrados

def vaciar_tablas():
    try: # tuplas de [nombre tabla, dias maximos de antiguedad de registros]
        # tablas con campo tiempo (fecha/hora)
        tablas=[
                ['datos_s',10],
                ['datos',366],
                ['reles_grab',366],
                ['log',30],
                ['hibrido',366]
               ]
               
        # tablas con campo fecha
        tablas_d=[
                  ['reles_segundos_on',366],
                 ]      
               
        error='conexion BD'
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        for t in tablas:
            error = f'borrando tabla {t[0]}'
            sql = f"DELETE FROM {t[0]} WHERE Tiempo < SUBDATE(NOW(),INTERVAL {t[1]} DAY)"
            try:
                cursor.execute(sql)
            except:
                print(f'Error en borrado de tabla {t}')
            db.commit()
        
        for t in tablas_d:
            error = f'borrando tabla {t[0]}'
            sql = f"DELETE FROM {t[0]} WHERE fecha < SUBDATE(NOW(),INTERVAL {t[1]} DAY)"
            try:
                cursor.execute(sql)
            except:
                print(f'Error en borrado de tabla {t}')
            db.commit()
            
            
            #print (error)        
        #print ('vaciado de tablas ejecutado correctamente')
       
        

    except Exception as e:
        log='Error en limpieza de tablas'+error
        try: 
            cursor.execute("""INSERT INTO log (fecha,log) VALUES(%s,%s)""",(tiempo,log))
            print (tiempo,' ', log)
            db.commit()
        except:
            db.rollback()
            print ("Error en limpieza de tablas, sin acceso a la base de datos")


#Comprobacion argumentos en comando
fichero = time.strftime("PVControl_%Y-%m-%d.sql")
salir= False
    
if '-c' in sys.argv: # copia completa  
    fichero = '' + fichero
    opc = '--opt'
    cmd = f'mysqldump -u {usuario} -p{clave} --single-transaction --quick {opc} control_solar  | gzip > /home/pi/PVControl+/backBD/{fichero}.gz'
    res = subprocess.run(cmd, shell=True)
    salir= True
    
if '-e' in sys.argv:  #copia estructura
    fichero = 'E_' + fichero
    opc = '--no-data'
    cmd = f'mysqldump -u {usuario} -p{clave} --single-transaction --quick {opc} control_solar  | gzip > /home/pi/PVControl+/backBD/{fichero}.gz'
    res = subprocess.run(cmd, shell=True)
    salir= True
    
if '-d' in sys.argv:  # copia solo datos
    fichero = 'D_' + fichero
    opc = '--no-create-info --disable-keys --complete-insert --extended-insert'
    cmd = f'mysqldump -u {usuario} -p{clave} --single-transaction --quick {opc} control_solar  | gzip > /home/pi/PVControl+/backBD/{fichero}.gz'
    res = subprocess.run(cmd, shell=True)
    salir= True

if '-b' in sys.argv:  # borrado ficheros antiguos
    borrar_ficheros(carpeta + comodin_borrado)
    salir= True

if '-v' in sys.argv:  # vaciado de registros antiguos
    vaciar_tablas()
    salir= True
    
if salir: sys.exit()

print()
print (Style.BRIGHT + Fore.YELLOW +'#' * 90)
print('  PROGRAMA DE GESTION DE COPIAS DE SEGURIDAD DE LA BD DE PVControl+')
print(Fore.CYAN)
print(' Este programa permite:')
print('   Copias de seguridad de la BD de PVControl a un fichero en la carpeta BackBD')
print('   Restaura la BD de PVControl+ desde un fichero en la carpeta BackBD ')
print (Fore.YELLOW)
print('#' * 90)
print()


menu = """
   
   Elige la carpeta de destino u origen de los ficheros de backup
  
       """
carpeta = click.prompt(Fore.BLUE + menu, type=str, default=carpeta)

print()

menu = """
  Elige Opcion pulsando
      
      - 1 Crea fichero SQL comprimido de backup de la Base de datos
      
      - 2 Restaura la Base de datos desde un fichero SQL comprimido
      
       """
salir = click.prompt(Fore.CYAN + menu, type=str, default='1')

print()
print (Fore.BLUE + f'  -- Listado de Archivos en la carpeta {carpeta} -- ')
print (Fore.RESET)
f=[] # lista ficheros
i= 0
with os.scandir(carpeta) as ficheros:
    for fic in ficheros:
        i += 1
        l= int(fic.stat().st_size/1024)
        d= fic.stat().st_mtime
        date_time = datetime.fromtimestamp(d)
        d = date_time.strftime("%d/%m/%Y-%H:%M:%S")        
        print(Style.BRIGHT+ f'  {i} = {fic.name:35} {l:>7} kB   {d}')
        f.append(fic.name)
print()

if salir == "1":
    msg = """
            ----- BACKUP DE LA BD DE PVControl+ -----
            
            Permite realizar el backup de cualquier tabla o conjunto de tablas de PVControl+
            datos, datos_c, diario, reles, etc a un un fichero
            """    
    print (msg)
    fichero = click.prompt(Fore.CYAN + '  introduce el nombre del fichero a crear', type=str, default=fichero)
    
    print()
    bd= click.prompt(Fore.CYAN + '  introduce el nombre de la Base de datos  ', type=str, default='control_solar')
    
    print()
    
    tabla = click.prompt(Fore.CYAN + '  introduce los nombres de las tablas separadas por espacio - dejar en blanco para backup de todas las tablas', type=str, default='')
   
    print()
    td = click.prompt(Fore.CYAN + """
        1 = Backup solo estructura 
        2 = Backup solo datos
        3 = Backup datos y estructura 
        """, type=str, default='1')
    
    if td== '1': 
        td='--no-data '
        fichero = 'E_' + fichero  # empieza por E para diferenciar solo estructura
    elif td== '2': 
        fichero = 'D_' + fichero  # empieza por D para diferenciar solo datos
        td='--no-create-info --disable-keys --complete-insert --extended-insert'
    else:
        fichero = 'C_' + fichero  # empieza por C para diferenciar completa
        td='--opt'
    
    
    cmd = f'mysqldump -u {usuario} -p{clave} --single-transaction --quick {td} {bd} {tabla} | gzip > /home/pi/PVControl+/backBD/{fichero}.gz'
    #print(cmd)
    
    res = subprocess.run(cmd, shell=True)
    
elif salir == "2":
    msg = """
            ----- RESTAURACION DE LA BD DE PVControl+ -----
            
            Permite realizar la restauracion de la BD completa o cualquier tabla o conjunto de tablas de PVControl+
            datos, datos_c, diario, reles, etc desde un fichero SQL de backup
            
            El nivel de restauracion dependera de lo que contenga el archivo SQL que se utilice por lo que es posible
            que se borren los datos que actualmente contenga la BD seleccionada            
            """    
    print (msg)
    nfichero = click.prompt(Fore.CYAN + '  introduce el NUMERO del fichero a usar para la restauracion ', type=str, default='')
    fichero = f[int(nfichero)-1]
    print()
    print(Fore.RED+'ATENCION si introduce el nombre de la Base de Datos', Fore.CYAN+'control_solar')
    print(Fore.RED+' se actualizaran o borraran los datos actuales que contenga actualmente PVControl+')
    
    print()
    bd= click.prompt(Fore.CYAN + '  introduce el nombre de la Base de datos ', type=str, default='control_solar')
    
    #db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = bd)
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave)
    
    cursor = db.cursor()
    sql_create = f'create database {bd} character set utf8;'
    try:
        cursor.execute(sql_create)
    except:
       print()
       print (Fore.RED+f' La base de datos elegida {bd} ya existe ')
       r= click.prompt(Fore.CYAN + '  introduce 0 para continuar u otra tecla para cancelar ', type=str, default='0')
       if r != '0': sys.exit()
    
    db.commit()
    cursor.close()
    db.close()
    
    fichero = carpeta + '/' + fichero
    print()
    print (f'Restaurando copia de seguridad del archivo {fichero} en base de datos {bd}')
    print ( ' esta operacion puede tardar bastante dependiendo del tamaño del fichero')
    print()
    cmd = f'pv {fichero} | gunzip | mysql -u {usuario} -p{clave} {bd}'
    #cmd = f'gunzip < {fichero} | mysql -u {usuario} -p{clave} {bd}'
    
    res = subprocess.run(cmd, shell=True)
