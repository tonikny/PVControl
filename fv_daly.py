#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 10-1-22



import serial
import time
import struct
import math
import logging
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

##########################################################################
####   VARIABLES
##########################################################################

#Daly_indice_datos = [5,6,7,14,15,16,23,24,0,0,0,0,0,0,0] # posicion de los datos de Vceldas en la respuesta

#read_meter = [0xA5,0x40,0x59,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x46]

leer_estado =    [0xA5,0x40,0x90,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7D]
leer_maxmin = [0xA5,0x40,0x91,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7E] #ok
leer_max_temperaturas = [0xA5,0x40,0x92,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7F] #ok
leer_ciclos_celdas = [0xA5,0x40,0x94,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x81] #ok
leer_tensiones = [0xA5,0x40,0x95,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x82] #ok
leer_temp_bms = [0xA5,0x40,0x96,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x83]
leer_todo = [0xA5,0x40,0x98,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x85] # ok saca errores no lo usamos


DALY = {} # diccionario global datos capturados


##########################################################################
### LEEMOS NUMERO DE CELDAS
########################################################################## 
ser.write(serial.to_bytes(leer_ciclos_celdas)) 
time.sleep(0.4)
rcv = ser.read(13) 
datos = struct.unpack(">13B",rcv)  
if DEBUG != 0: print(Fore.GREEN+'datos_ciclos_celdas=',datos) 
           
#asginamos valores nceldas y ciclos
DALY['N_celdas'] = datos[4] # asignamos a Valores el numero de celdas
N_celdas = DALY['N_celdas'] # lo mismo pero abajo si no es asi no me lo coge
print (Fore.RED,f'Nº celdas activas = {N_celdas}')
           
           
##########################################################################
##########################################################################  

##########################################################################
######  DECLARAMOS LAS VARIABLES A UTILIZAR
##########################################################################    
Nombre_celdas = [ f'C{i+1}' for i in range(N_celdas)]  # esto crea el nombre de las celdas C1,C2....

Valor_Max_dia = [0] * N_celdas  # Valores max del dia segun  cantidad de celdas
Valor_real = [0] * N_celdas  # Valores reales segun cantidad de  celdas
Valor_Min_dia = [100] * N_celdas # Valores min del dia segun cantidad de celdas
Vcelda_max_actual = {'Celda': 'Cx', 'Valor': 0} # valor celda max de la lectura en ese momento  Cx X.XX 
Vcelda_min_actual = {'Celda': 'Cx', 'Valor': 100} # valor de la celda min de la lectura de ese momento Cx X.XX

contador = nveces = 80    # print de control
n_muestras_daly_contador= n_muestras_daly - 1 # contador para grabacion en BD lo pongo asi para que grabe en la primera vuelta
espera = 0.4 # tiempo sg entre mandar comando y lectura
############################################################################
max_responses = 1
logger=None
################################################

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
    
    if ncel < N_celdas:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas detectado en la BMS")
        print ( " se crean nuevos campos en tabla datos_celdas")
        print ("-" * 50)
        for K in range(N_celdas):
            try:
                Sql = f"ALTER TABLE `datos_celdas` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
    elif ncel > N_celdas:
        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas detectado en la BMS")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        for K in range(N_celdas,ncel):
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


#print(Fore.CYAN,"Empieza el monitoreo de celdas desde daly hay :", Fore.RED,N_celdas , Fore.CYAN,"que monitorizar")
dia = time.strftime("%Y-%m-%d")
print(time.strftime(Fore.GREEN+"%Y-%m-%d %H:%M:%S") ,'- ', end='')
######################
### CREAMOS FUNCIONES PARA LEER EL DALY SOLO LO NECESARIO 
###################
def leer_soc_bms():
   
    contenedor_datos = []
    ser.write(serial.to_bytes(leer_estado))
    time.sleep(espera) 
    b = ser.read(13)
    data = b[4:-1]
    contenedor_datos.append(data)   
    if len(contenedor_datos) > 1:
        respuesta = contenedor_datos
    elif len(contenedor_datos) == 1:
        respuesta = contenedor_datos[0]

    partes = struct.unpack('>h h h h', respuesta)
    DALY['Vbat'] = partes[0] / 10
    #DALY['x_voltage'] partes[1] / 10, # always 0
    DALY['Ibat'] = (30000 - partes[2] ) / 10  # negativo descargando positivo cargando (30000-datos[6])/10
    DALY['SOC'] = partes[3] / 10
    
def leer_temp_bms():
   
    ser.write(serial.to_bytes(leer_max_temperaturas))
    time.sleep(espera) 
    contenedor_datos = []
    b = ser.read(13)
    data = b[4:-1]
    contenedor_datos.append(data)
       
    if len(contenedor_datos) > 1:
        respuesta = contenedor_datos
    elif len(contenedor_datos) == 1:
        respuesta = contenedor_datos[0]


    partes = struct.unpack('>b b b b 4x', respuesta)
    
    DALY['Temp_Max'] = partes[0] - 40
    DALY['Sensor_Max'] = partes[1]
    DALY['Temp_Min'] = partes[2] - 40
    DALY['Sensor_min'] = partes[3]

    
def leer_ciclos_bms():
   
    ser.write(serial.to_bytes(leer_ciclos_celdas))
    time.sleep(espera) 
    contenedor_datos = []
    b = ser.read(13)
    data = b[4:-1]
    contenedor_datos.append(data)
           
    if len(contenedor_datos) > 1:
        respuesta = contenedor_datos
    elif len(contenedor_datos) == 1:
        respuesta = contenedor_datos[0]

    partes = struct.unpack('>b b ? ? b h x', respuesta)
    state_bits = bin(partes[4])[2:]
    state_names = ["DI1", "DI2", "DI3", "DI4", "DO1", "DO2", "DO3", "DO4"]
    states = {}
    state_index = 0
    for bit in reversed(state_bits):
        if len(state_bits) == state_index:
            break
        states[state_names[state_index]] = bool(int(bit))
        state_index += 1
        
        
    DALY['N_celdas'] = partes[0]
    DALY['Ciclos'] = partes[5]
    #DALY['Sendores_temp'] = partes[1]
    #DALY['cargador_corriendo'] = partes[2]
    #DALY['carga en funcionamiento'] = partes[3]
    #DALY['state_bits'] = state_bits
    DALY['estados'] = states
    
    
    
      

def leer_Vceldas_bms():
## leemos desde la DALY los valores
    contenedor_datos = []
    if not contenedor_datos:
        max_responses = math.ceil(N_celdas / 3)
        if not max_responses:
            return
    
    ser.write(serial.to_bytes(leer_tensiones))
    time.sleep(espera)
    x = 0
###### partimos las repuesta     
    while True:
        b = ser.read(13)
        x += 1
        data = b[4:-1]
        contenedor_datos.append(data)
        if x == max_responses:
            break
   
    if len(contenedor_datos) > 1:
        respuesta = contenedor_datos
    elif len(contenedor_datos) == 1:
        respuesta = contenedor_datos[0]
    else:
        return False
###### leemos la respuesta y la pasamos legible
    values = {}
    pepe ={}
    x = 1
    i = 1
        
    for response_bytes in respuesta:
        
        partes = struct.unpack(">b 3h x", respuesta[x-1])
        if partes[0] != x:
            logger.warning("frame out of order, expected %i, got %i" % (x, response_bytes[0]))
            continue
        for value in partes[1:]:
            values[i] = value /1000
            Valor_real[i-1] = value /1000
            Valor_Max_dia[i-1] = max(Valor_real[i-1], Valor_Max_dia[i-1])
            Valor_Min_dia[i-1] = min(Valor_real[i-1], Valor_Min_dia[i-1])     
            
            i += 1
            if len(values) == N_celdas:
                break   



def leer_V_Max_Min_bms():
 
    ser.write(serial.to_bytes(leer_maxmin))
    time.sleep(espera) 
    contenedor_datos = []
    b = ser.read(13)
    data = b[4:-1]
    contenedor_datos.append(data)
           
    if len(contenedor_datos) > 1:
        respuesta = contenedor_datos
    elif len(contenedor_datos) == 1:
        respuesta = contenedor_datos[0]
        
    
    partes = struct.unpack('>h b h b 2x', respuesta)

    Vcelda_max_actual['Celda'] = partes[1]
    Vcelda_max_actual['Valor'] = partes[0] / 1000
    Vcelda_min_actual['Celda'] = partes[3]
    Vcelda_min_actual['Valor'] = partes[2] / 1000
    
     #asignamos valor max y min de la lectura actual
    DALY['Vceldamax'] = Vcelda_max_actual
    DALY['Vceldamin'] = Vcelda_min_actual 
  

#######################
if usar_daly == 1: # 1 entra 0 no entraria dato declaro en parametros.py

    try:
            
        while True:
            ## Inicializacion valores diario a las 00:00
            dia_anterior = dia
            dia = time.strftime("%Y-%m-%d")

            if dia_anterior != dia: #cambio de dia
                Vcelda_max_actual = {'Celda': 'Cx', 'Valor': 0} 
                Vcelda_min_actual = {'Celda': 'Cx', 'Valor': 100} 
                Valor_Max_dia = [0] * N_celdas
                Valor_Min_dia = [100] * N_celdas
                if leer_ciclos == 1:leer_ciclos_bms()
                


            ee='58'
            ########lectura de los datos que queramos tener se configura en parametros_fv.py ##########
            if leer_ciclos == 1:leer_ciclos_bms()       #lee los ciclos el numero de celdas y varias cosas mas que no tengo claro que son
            if leer_soc == 1:leer_soc_bms()             #lee soc ibat vbat
            if leer_temp == 1:leer_temp_bms()           #lee la temperaturas 
            if leer_V_Max_Min == 1:leer_V_Max_Min_bms() #lee el valor max y min de las celdas
            
            #este lo leemo si o si es la lectura de las celdas.
            
            leer_Vceldas_bms() #saca los valores de la celdas
            
            ######################################
            
           
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            
            ee = '59'
            
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
                datos = {'Nombre' : Nombre_celdas, 'Max': Valor_Max_dia,'Valor' : Valor_real,'Min' : Valor_Min_dia}
                ####  ARCHIVOS RAM en BD ############ 
                salida = json.dumps(datos)
                ee='61'
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'CELDAS'")
                ee='62'
                
                cursor.execute(sql)
                ee='65'
                salida = json.dumps(DALY)
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
                #comprobamos si el valor es mayor o menor al programado en parametros_fv.py para darlo como error de lectura
                # y asi no desvirtualizar la realidad.
                if Valor_error_max > DALY['Vceldamax']['Valor'] and Valor_error_min < DALY['Vceldamin']['Valor']:
                    
                
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

