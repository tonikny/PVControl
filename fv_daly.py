import serial
import time
import struct
from struct import pack
import os, sys, time
import serial
import subprocess
import MySQLdb 
import json
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

from Parametros_FV import *

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_daly'
control = 'usar_daly'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_daly.py') #+Style.RESET_ALL)

ser = serial.Serial()
ser.baudrate = 9600
ser.parity = 'N'
if dev_daly = "": 
    ser.port = "/dev/ttyUSB0"
    print ('No esta especificado el puerto de comuniaciones del daly en Parametros_FV.py...se activa por defecto en /dev/ttyUSB0')
ser.timeout = 1
ser.open()
time.sleep(1)

#variables
Daly_indice_datos = [5,6,7,14,15,16,23,0,0,0,0,0,0,0,0] # posicion de los datos de Vceldas en la respuesta

#read_meter = [0xA5,0x40,0x59,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x46]
leer_tensiones = [0xA5,0x40,0x95,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x82]
leer_estado =    [0xA5,0x40,0x90,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7D]
leer_temperaturas = [0xA5,0x40,0x92,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7F]

try:
    print (Fore.RED,f'Nº celdas activas = {usar_daly}')
except:
    print (Fore.RED,'No hay dado de alta el numero de celdas activas en Parametros_FV.py')
    print ('Se introduce por defecto 7 celdas..... usar_daly = 7')
    usar_daly = 7
    
Nombre_celdas = [ f'C{i+1}' for i in range(usar_daly)]

Valor_Max = [0] * usar_daly
Valor_real = [0] * usar_daly
Valor_Min = [100] * usar_daly
Valores = {} # diccionario global datos capturados

Vcelda_max = {'Celda': 'Cx', 'Valor': 0} # lo explicas :)
Vcelda_min = {'Celda': 'Cx', 'Valor': 100} #

contador = nveces = 80    # print de control
n_muestras_daly_contador= 0 # contador para grabacion en BD
espera = 0.1 # tiempo sg entre mandar comando y lectura

try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    try: #inicializamos registro en BD RAM --- por ahora MUX dado que es lo que usa la web...cambiar a VCELDAS
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('CELDAS','{}'))
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('DALY','{}'))
        
        db.commit()
    except:
        pass
except:
    print (Fore.RED,'ERROR inicializando BD RAM')
    sys.exit()

#print(Fore.CYAN,"Empieza el monitoreo de celdas desde daly hay :", Fore.RED,usar_daly , Fore.CYAN,"que monitorizar")
dia = time.strftime("%Y-%m-%d")
print(time.strftime(Fore.GREEN+"%Y-%m-%d %H:%M:%S") ,'- ', end='')

if usar_daly in range(1,17): # poner el Nº de celdas maxima que admita
    
    try:
            
        while True:
            ## Inicializacion valores diario a las 00:00
            dia_anterior = dia
            dia = time.strftime("%Y-%m-%d")

            if dia_anterior != dia: #cambio de dia
                Vcelda_max = {'Celda': 'Cx', 'Valor': 0} 
                Vcelda_min = {'Celda': 'Cx', 'Valor': 100} 
                Valor_Max = [0] * usar_daly
                Valor_Min = [100] * usar_daly
            
            ser.write(serial.to_bytes(leer_tensiones)) 
            time.sleep(espera)
            rcv = ser.read(39)  
            datos = struct.unpack(">5B 4H 5B 4H 5B 3H 2B",rcv)  
            #print(datos)  
            ee = '40'
            
            for i in range(usar_daly):
                ee = '41'
                
                Valor_real[i] = datos[Daly_indice_datos[i]]/1000
                ee='42'
                Valor_Max[i] = max(Valor_real[i], Valor_Max[i])
                Valor_Min[i] = min(Valor_real[i], Valor_Min[i])
            
                Valores[f'C{i+1}'] = Valor_real[i]
                Valores[f'C{i+1}max'] = Valor_Max[i]
                Valores[f'C{i+1}min'] = Valor_Min[i]
                
                if Valor_Max[i] > Vcelda_max['Valor']:
                    Vcelda_max['Celda'] =  f'C{i}'
                    Vcelda_max['Valor'] =  Valor_Max[i]
                    
                if Valor_Min[i] < Vcelda_min['Valor']:
                    Vcelda_min['Celda'] =  f'C{i}'
                    Vcelda_min['Valor'] =  Valor_Min[i]
                
                Valores['Vceldamax'] = Vcelda_max # pon la clave que mas te guste
                Valores['Vceldamin'] = Vcelda_min # pon la clave que mas te guste
                
            #print ('Celda Maxima=',Valores['Vceldamax'])
            #print ('Celda Minima=',Valores['Vceldamin'])
                
            ee = '50'      

            ser.write(serial.to_bytes(leer_estado)) 
            time.sleep(espera)
            rcv = ser.read(13)  
            datos = struct.unpack(">4B 4H B",rcv)  
            #print(datos) 

            Valores['Vbat'] = datos[4]/10
            Valores['Ibat'] = (30000-datos[6])/10
            Valores['SOC'] = datos[7]/10

            
            ser.write(serial.to_bytes(leer_temperaturas)) 
            time.sleep(espera)
            rcv = ser.read(13)  
            datos = struct.unpack(">13B",rcv)  
            #print(datos) 
            ee='58'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            ee='59'
                        
                 #### REGISTRO EN BD ############
            try:
                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                cursor = db.cursor()
            except:
                print(Fore.RED+'error, BD', Sql)
                
            try:
                ee = '60'
                time.sleep(t_muestra_daly- 3 * espera)
                
                datos = {'Nombre' : Nombre_celdas, 'Max': Valor_Max,'Valor' : Valor_real,'Min' : Valor_Min}
                ####  ARCHIVOS RAM en BD ############ 
                salida = json.dumps(datos)
                ee='61'
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'CELDAS'")
                ee='62'
                
                cursor.execute(sql)
                ee='65'
                salida = json.dumps(Valores)
                ee='66'
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'DALY'")
                cursor.execute(sql)
                ee='67'
                
                #print("Datos actualizados")
                
            except:
                print(Fore.RED+'error, Grabacion tabla RAM equipos')
            #db.commit()
  
            try:
                ee='70'
                if grabar_datos_daly == 1 and n_muestras_daly_contador == n_muestras_daly-1:
                    n_muestras_daly_contador = 0         
                    # Insertar Registro en BD
                    campos = ",".join(Nombre_celdas)
                    valores = "','".join(str(v) for v in Valor_real)
                    Sql = "INSERT INTO datos_celdas ("+campos+") VALUES ('"+valores+"')"
                    cursor.execute(Sql)
                    print (Fore.RED+'G', end = '',flush=True)
                    
                else:
                    n_muestras_daly_contador+=1
                    print (Fore.BLUE+'D', end = '',flush=True)
                
                ee='75'    
                db.commit()

                contador -= 1
                if contador== 0:
                    contador = nveces
                    print ()
                    print(Fore.GREEN+time.strftime("%Y-%m-%d %H:%M:%S") ,'- ', end='')
                
            except:
                print('error, BD', Sql)
                db.rollback()
                pass    
            
    except:
        print ('Error en bucle ',ee)
        pass

