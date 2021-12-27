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

DEBUG= 0
if '-p1' in sys.argv: DEBUG= 1 
elif '-p' in sys.argv: DEBUG= 100 

print (Fore.RED + 'DEBUG=',DEBUG)


ser = serial.Serial()
ser.baudrate = 9600
ser.parity = 'N'
if dev_daly == "": 
    dev_daly = "/dev/ttyUSB0"
    print ('No esta especificado el puerto de comuniaciones del daly en Parametros_FV.py...se activa por defecto en /dev/ttyUSB0')

ser.port = dev_daly 
ser.timeout = 1
ser.open()
time.sleep(1)


#variables
Daly_indice_datos = [5,6,7,14,15,16,23,24,0,0,0,0,0,0,0] # posicion de los datos de Vceldas en la respuesta

#read_meter = [0xA5,0x40,0x59,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x46]

leer_estado =    [0xA5,0x40,0x90,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7D]
leer_maxmin = [0xA5,0x40,0x91,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7E]
leer_max_temperaturas = [0xA5,0x40,0x92,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7F]
leer_ciclos_celdas = [0xA5,0x40,0x94,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x81] #ok
leer_tensiones = [0xA5,0x40,0x95,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x82] #ok
leer_temp = [0xA5,0x40,0x96,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x83]
leer_todo = [0xA5,0x40,0x98,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x85]


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
espera = 0.4 # tiempo sg entre mandar comando y lectura

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
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

    try: #inicializamos registro en BD RAM
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      ('CELDAS','"{}"'))
        db.commit()
    except:
        pass
        
    try: #inicializamos registro en BD RAM
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      ('DALY','"{}"'))
        db.commit()
    except:
        pass    
    Sql = """    
    CREATE TABLE IF NOT EXISTS `datos_celdas` (
    `id_celda` int(11) NOT NULL AUTO_INCREMENT,
    `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
    `C1` float NOT NULL DEFAULT 0,
     PRIMARY KEY (`id_celda`),
     KEY `Tiempo` (`Tiempo`)
     ) 
     ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
     """
    if DEBUG >= 100: cursor.execute (Sql)
    
    Sql='SELECT * FROM datos_celdas LIMIT 1' 
    nreg=cursor.execute(Sql)
    ncel = len(cursor.description) - 2 # Nº de celdas declaradas en BD
    
    if ncel < usar_daly:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se crean nuevos campos en tabla datos_celdas")
        print ("-" * 50)
        for K in range(usar_daly):
            try:
                Sql = f"ALTER TABLE `datos_celdas` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
    elif ncel > usar_daly:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas declaradas en Parametros_FV.py")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        for K in range(usar_daly,ncel):
            try:
                Sql = f"ALTER TABLE `datos_celdas` DROP `C{K+1}`"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} borrado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
    cursor.close()
    db.close()        
except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()
# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================

try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    try: #inicializamos registro en BD RAM --- 
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
            
            #leemos vceldas desde daly
            ser.write(serial.to_bytes(leer_tensiones)) 
            time.sleep(espera)
            rcv = ser.read(39) 
            datos = struct.unpack(">5B 4H 5B 4H 5B 3H 2B",rcv)  
            if DEBUG != 0: print('datos_vceldas=',datos)  
            ee = '40'
            
            #reseteamos valor de vcelda_max y min a 0 para ver el valor max y min de cada lectura
            Vcelda_max['Valor'] = 0
            Vcelda_min['Valor'] = 100
          
            for i in range(usar_daly):
                ee = '41'
                
                Valor_real[i] = datos[Daly_indice_datos[i]]/1000
                ee='42'
                Valor_Max[i] = max(Valor_real[i], Valor_Max[i])
                Valor_Min[i] = min(Valor_real[i], Valor_Min[i])
    
            
                #verificamos el valor max y min 
                if Valor_real[i] > Vcelda_max['Valor']:
                    Vcelda_max['Celda'] = f'C{i+1}'
                    Valor_Max_real = round(Valor_real[i],2)
                    Vcelda_max['Valor'] = Valor_Max_real
                    
                if Valor_real[i] < Vcelda_min['Valor']:
                    Vcelda_min['Celda'] = f'C{i+1}'
                    Valor_Min_real = round(Valor_real[i],2)
                    Vcelda_min['Valor'] = Valor_Min_real
                   

            #asignamos valor max y min de la lectura actual
            Valores['Vceldamax'] = Vcelda_max 
            Valores['Vceldamin'] = Vcelda_min 
            
            ee = '50'      
            #leemos estado de vbat soc y ibat
            ser.write(serial.to_bytes(leer_estado)) 
            time.sleep(espera)
            rcv = ser.read(13)  
            datos = struct.unpack(">4B 4H B",rcv)  
            #print(Fore.GREEN+'datos_celdas_estado=',datos) 
            
            
            #asignamos los valores recibidos
            Valores['Vbat'] = datos[4]/10
            Valores['Ibat'] = (30000-datos[6])/10
            Valores['SOC'] = datos[7]/10
            
##########################################################################
### sacamos ciclos y numero de celdas
########################################################################## 
            ser.write(serial.to_bytes(leer_ciclos_celdas)) 
            time.sleep(espera)
            rcv = ser.read(13) 
            datos = struct.unpack(">13B",rcv)  
            if DEBUG != 0: print(Fore.GREEN+'datos_ciclos_celdas=',datos) 
            
            #asginamos valores nceldas y ciclos
            Valores['Nceldas'] = datos[4]
            Valores['Ciclos'] = datos[10]
           
           
##########################################################################
##########################################################################  

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
                
                #time.sleep(t_muestra_daly- 3 * espera)
                time.sleep(t_muestra_daly * espera)
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
                #comprobamos si el valor es mayor o menor al programado en parametros para darlo como error de lectura
                # y asi no desvirtualizar la realidad.
                if Valor_error_max > Valores['Vceldamax']['Valor'] and Valor_error_min < Valores['Vceldamin']['Valor']:
                    
                
                    if grabar_datos_daly == 1 and n_muestras_daly_contador == n_muestras_daly-1:
                        n_muestras_daly_contador = 0         
                        # Insertar Registro en BD
                        campos = ",".join(Nombre_celdas)
                        valores = "','".join(str(v) for v in Valor_real)
                        Sql = "INSERT INTO datos_celdas ("+campos+") VALUES ('"+valores+"')"
                        cursor.execute(Sql)
                        if DEBUG == 0:print (Fore.RED+'G', end = '',flush=True)
                        
                    else:
                        n_muestras_daly_contador+=1
                        if DEBUG == 0: print (Fore.BLUE+'D', end = '',flush=True)
                    
                    ee='75'    
                    db.commit()

                    contador -= 1
                    if contador== 0:
                        contador = nveces
                        if DEBUG == 0:
                            print ()
                            print(Fore.GREEN+time.strftime("%Y-%m-%d %H:%M:%S") ,'- ', end='')
                            
               
                else: 
                    texto = "Error en lectura max o min"
                    time.strftime("%H:%M")                    
                    try: 
                        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
                        #print (tiempo,' ', texto)
                        db.commit()
                        print(texto)
                    except:
                        db.rollback()
                
                              
                
            except:
                print('error, BD', Sql)
                db.rollback()
                pass    
            
    except:
        print ('Error en bucle ',ee)
        pass

