# -*- coding: utf-8 -*-
#
#Version 5/Dic/23
#

"""
## USO desde ventana terminal

python3 fv_victron_mk2.py        # funcionamiento normal
   
python3 fv_victron_mk2.py -p     # saca por pantalla las distintas capturas

python3 fv_victron_mk2.py -test  # realiza un test de forma autonoma sin estar integrado en PVControl+ con lo especificado en la variable BMS_JK

"""

########## NO TOCAR SALVO QUE SE QUIERA USAR FUERA DE PVControl+ con la opcion -test 
######### LA CONFIGURACION para PVControl+ SE DEBE HACER EN Parametros_FV_py con la siguiente estructura ##############
VICTRON_MK2 = {
    'MULTIPLUS1': {'usar': 0,
           'dev' : 'dev/ttyUSB0',
           'tiempo_captura': 5,
           'ciclos_grabacion' : 1, # 0 para NO grabar en BD
          },
          
    'MULTIPLUS2': {'usar':0,
            'dev' : 'dev/ttyUSB1',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 5,
          },
    }

import sys
import serial
import time
import struct
import math

import json,sys
import MySQLdb 
import multiprocessing

flag = True
for s in ['-scan','-test']:
    if s in sys.argv:
        flag = False
        break

simula = 0
if '-sim' in sys.argv: simula = 1


#if flag:
# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'VICTRON_MK2'
servicio = 'fv_victron_mk2'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO}])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################
#else:
import sys,subprocess

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


DEBUG= 0
if '-p1' in sys.argv: DEBUG= 1 
elif '-p' in sys.argv: DEBUG= 100
elif '-test' in sys.argv: DEBUG= 100



# Comprobacion que la tabla en BD tiene los campos necesarios
def comprobar_bd(equipo):
    ee = 100
    if '-test' not in sys.argv:
        try:
            ee = 110   
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            
            # Comprobacion si tabla equipos existe y si no se crea
            sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                          `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                          `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                          `sensores` varchar(3000) COLLATE latin1_spanish_ci NOT NULL,
                           PRIMARY KEY (`id_equipo`)
                         ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

            import warnings # quitamos el warning que da si existe la tabla equipos
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cursor.execute(sql_create)
            ee = 120
            
            if VICTRON_MK2[equipo]['usar'] == 1: # solo se chequea si se activa el equipo
                ee = 130
                try:#inicializamos registro en BD RAM
                    cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                                      (f"{equipo}","{}"))
                except:
                    pass   
                
            db.commit()
            cursor.close()
            db.close()

        except:
            print(f'ERROR {ee} en creacion/comprobacion de la Base de datos.....se detiene programa')
            sys.exit()

def grabar_bd(equipo,datos):
    
    print_c(equipo)
    if DEBUG == 100:
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {equipo}...Grabando en BD...')
        #print(datos)
      
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
    except:
        print('Error conexion BD')
        sys.exit()
           
    try:
        ####  ARCHIVOS RAM en BD ############ 
        ee = 100
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        salida = json.dumps(datos)
        ee = 110
        
        #print(salida)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo}'")
        
        
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
        
    except:
        print(f'error {ee}, Grabacion tabla RAM equipo {equipo}')
        print(sql)


def print_c(eq):
    #print()
    if eq[-1] =='1' : print(Fore.GREEN, end='')
    elif eq[-1] =='2' : print(Fore.YELLOW, end='')
    elif eq[-1] =='3' : print(Fore.BLUE, end='')
    elif eq[-1] =='4' : print(Fore.MAGENTA, end='')

def Equipo_lectura(equipo):
    contador_ciclos = 0
    print_c(equipo)
    print (f"Iniciando lectura VICTRON_MK2.... equipo= {equipo}... dev= {VICTRON_MK2[equipo]['dev']}")
    
    print (f'DEBUG= {DEBUG} -- simula={simula}')
    
    comprobar_bd(equipo)
    
    if simula == 1:
        d_= {}
        d_['Vred'] = 0
        d_['Ired'] = 0
        d_['Vinv'] = 0
        d_['Iinv'] = 0
        d_['Frec_red'] = 0
        
        d_['Vbat'] = 0
        d_['Ibatn'] =  0
        d_['Ibatp'] = 0
        d_['Frec_inv'] = 0
        
        while True:
            contador_ciclos += 1
            
            if DEBUG == 100 :
                print_c(equipo)
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} -- {equipo}: {d_}')
                
            if contador_ciclos == VICTRON_MK2[equipo]['ciclos_grabacion']: 
                grabar_bd(equipo, d_)
                contador_ciclos = 0         
            
            d_['Ired'] = 0  if d_['Ired'] > 9 else d_['Ired']+1
            time.sleep(5)
            

    else:
        
        ser = serial.Serial()
        ser.baudrate = 2400
        ser.parity = 'N'
        ser.port= VICTRON_MK2[equipo]['dev']
        ser.timeout = 4
        ser.open()
        time.sleep(1)
            
        read_ac_info = [0x03,0xFF,0x46,0x01,0xB7]
        read_dc_info = [0x03,0xFF,0x46,0x00,0xB8]
        
        
        while True:
        
            t1 = time.time()
            
            # Captura datos AC 
            ser.reset_input_buffer()
            ser.write(serial.to_bytes(read_ac_info))
            rcv = ser.read(17)
            datos = struct.unpack(">17B",rcv)
            d_={}   
            if datos[0]==15:
                d_['Vred'] = round((datos[7]+datos[8]*256)/100,1)
                d_['Ired'] = round((datos[9]+datos[10]*256)/100,2)
                d_['Vinv'] = round((datos[11]+datos[12]*256)/100,1)
                d_['Iinv'] = round((datos[13]+datos[14]*256)/100,2)     
                #Cuando hay Ibatp, Iinv lee mal por eso linea 245 
                # Cuando se pierde AC-IN, el período es 0xFF ya que se pierde el bloqueo.
                if (datos[15] == [0xFF]):
                    d_['Frec_red'] = 0
                else:
                    #d_['Frec_red'] = round((10000.0/datos[15]), 1)    
                   d_['Frec_red'] = datos[15]

            else:
                if DEBUG > 0: print('Error lectura AC')
                ser.reset_input_buffer()             
                
            
            # Captura datos DC 
            ser.reset_input_buffer()
            ser.write(serial.to_bytes(read_dc_info))   
            rcv = ser.read(17)    
            datos = struct.unpack(">17B",rcv)
            if datos[0]==15:
                d_['Vbat'] = (datos[7]+datos[8]*256)/100
                d_['Ibatn'] = round((datos[9]+datos[10]*256+datos[11]*256*256)/10,2)  #he anadiso datos 11
                d_['Ibatp'] = round((datos[12]+datos[13]*256+datos[14]*256*256)/10,2) #he añadido datos14   
                if d_['Ibatp'] > 0:
                    d_['Iinv'] = 0
                d_['Frec_inv'] = round(100000.0/datos[15], 1)#datos[15]
                
            else:
                if DEBUG > 0 : print('Error lectura DC')
                ser.reset_input_buffer()
            t2 = time.time()
            
            contador_ciclos += 1
                    
            if DEBUG == 100 :
                print_c(equipo)
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} -- {equipo}: {d_}')
            
            if '-test' not in sys.argv: 

                if contador_ciclos == VICTRON_MK2[equipo]['ciclos_grabacion']: 
                    
                    grabar_bd(equipo, d_)
                    
                    contador_ciclos = 0         
                
            
            #print(round(time.time(),2),round(t2-t1,3),a)
            t3 = time.time()       
            time.sleep(4-(t3-t1)) # ya veremos si se pone parametrizable# original 5 he puesto 4 para mas rapido
            

equipo = VICTRON_MK2

if __name__ == '__main__':  

    # Arrancar procesos inicial
    print (Fore.RESET+'=' * 50)
    for h in equipo:
        print(Fore.YELLOW + f' {h}:')
        if equipo[h]['usar'] == 1:
            print(Fore.GREEN, end='')
            multiprocessing.Process(target = Equipo_lectura,args=(h,),name = f'{h}').start() # arranco proceso
        else:
            print(Fore.RED, end='')
        print(f"          {equipo[h]}")
        print()
    print (Fore.RESET+'=' * 50)

    Procesos= multiprocessing.active_children() # lista procesos
    print ('Procesos activos=',Procesos)
    
    Nprocesos = [p.name for p in Procesos]
    
    
    ####### BUCLE ####################################
    t_control1 = t_control2 = time.time()
    
    while True:
        try:
            if time.time()-t_control1 > 60: #cada 60 sg
                t_control1 = time.time()
                try:
                    # Arrancar procesos ...por si se cambia Parametros_FV.py
                    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
                    equipo = equipos[eq]
                    
                    for h in equipo: 
                        if equipo[h]['usar'] == 1 and h not in Nprocesos: # se ha activado un hilo nuevo
                            multiprocessing.Process(target = Equipo_lectura,args=(h,),name = f'{h}').start() # arranco proceso
                        
                        if equipo[h]['usar'] == 0 and h in Nprocesos: # se ha desactivado un hilo
                            for p in Procesos:
                                if p.name == h:
                                    print()
                                    print(Fore.RED + f'     ....Terminando hilo..{p}')
                                    print()
                                    p.terminate()
                                    time.sleep(1)
                          
                    Procesos= multiprocessing.active_children() # lista procesos
                    Nprocesos = [p.name for p in Procesos] # lista de Nombre de procesos
                    if DEBUG > 0:
                        print()
                        print(Fore.YELLOW + f'Nprocesos = {Nprocesos}....Procesos = {Procesos}')
                        print()
                        
                except:
                    print ('Error en bucle control Parametros')
                
            
            if time.time()-t_control2 > 10: #cada 10 sg
                t_control2 = time.time()
                        
                try:
                    for p in Procesos:
                        if not p.is_alive():
                            print('=' * 50)
                            print (Fore.RED + f'Proceso {p.name} KO.... se reinicia')
                            time.sleep(1)
                            multiprocessing.Process(target = Equipo_lectura,args=(p.name,),name = p.name).start()
                            Procesos= multiprocessing.active_children()
                            print (Procesos)
                            print('=' * 50)
                        else:
                            #print (Fore.GREEN + f'Proceso {p.name}..... OK') 
                            pass
                except:
                    print ('Error en bucle control procesos activos')
                    
                    break        
            
                time.sleep(2)
        except:        
            print()
            print(Fore.RED + '=' * 50)
            print ('Finalizando .......')
            for p in Procesos:
                print(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()

