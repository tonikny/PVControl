#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 20-10-23
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

#########################
###### DALY ######
#########################
usar_daly = 0                   # 1 = Se usa 0 = No se usa
t_muestra_daly = 1              # segundos entre capturas para tabla en RAM 
grabar_datos_daly = 1           # 1 = Graba la tabla ... 0 = No graba
leer_soc_daly = 1               # 1 = leer soc ibat vbat .... 0 = NO SE USA
leer_temp_daly = 0              # 1 = leer la temperaturas ... 0 = NO SE USA 
leer_ciclos_daly = 1            # 1 = leer los ciclos el numero de celdas y varias cosas mas que no tengo claro = 0 NO SE USA
leer_V_Max_Min_daly = 1         # 1 = leer el valor max y min de las celdas ... 0 = NO SE USA
n_muestras_daly = 5             # grabar en BD en tabla permanente cada X capturas 
Valor_error_max_daly = 4.5      # no grabar si alguna lectura da este valor
Valor_error_min_daly = 2.8      # no grabar si alguna lectura da este valor
dev_daly = "/dev/ttyUSB0"       # puerto donde reconoce la RPi al Hibrido
equipo_bms = 'Daly'              # npmbre de la bms para estar identificada
from Parametros_FV import *

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_daly'
control = 'usar_daly'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_daly.py') #+Style.RESET_ALL)
equipo = equipo_bms
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
datos_globales={} # la usaremos para meter los todos los datos que queramos usar despues


##########################################################################
### LEEMOS NUMERO DE CELDAS
########################################################################## 
ser.write(serial.to_bytes(leer_ciclos_celdas)) 
time.sleep(0.4)
rcv = ser.read(13) 
datos = struct.unpack(">13B",rcv)  
if DEBUG != 0: print(Fore.GREEN+'datos_ciclos_celdas=',datos) 
           
#asginamos valores nceldas y ciclos
datos_globales['nceldas']= round(datos[4])
#DALY['nceldas'] = datos[4] # asignamos a Valores el numero de celdas
nceldas = datos_globales['nceldas'] # lo mismo pero abajo si no es asi no me lo coge
print (Fore.RED,f'N celdas activas = {nceldas}')
          
##########################################################################
##########################################################################  

##########################################################################
######  DECLARAMOS LAS VARIABLES A UTILIZAR
##########################################################################    
#Nombre_celdas = [ f'C{i+1}' for i in range(nceldas)]  # esto crea el nombre de las celdas C1,C2....


Nombre_Celdas = ['C'] * nceldas 
for i in range(nceldas): Nombre_Celdas[i] = f'C{i+1}' 
datos_globales['Nombres'] = Nombre_Celdas
Vceldas = [0.0] * nceldas
Vcelda_max = [0.0] * nceldas    # Maximo de cada celda diaria
Vcelda_min = [1000.0] * nceldas # Minino de cada celda diaria


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

except:
    pass   
    

try:
    #inicializamos registro en BD RAM
    cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      (f"BMS_{equipo}","{}"))
    db.commit()
except:
    pass   

Sql = f"""    
     CREATE TABLE IF NOT EXISTS `datos_celdas_{equipo}` (
    `id_celda` int(11) NOT NULL AUTO_INCREMENT,
    `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
    
    `Ibat` float NOT NULL DEFAULT 0,
    `C1` float NOT NULL DEFAULT 0,
     PRIMARY KEY (`id_celda`),
     KEY `Tiempo` (`Tiempo`)
     ) 
     ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
     """
cursor.execute (Sql)


try:

    Sql = f'SELECT * FROM datos_celdas_{equipo} LIMIT 1' 
    nreg=cursor.execute(Sql)
    ncel = len(cursor.description) - 3 # Nº de celdas declaradas en BD
    
    if ncel < nceldas:
        print (Fore.RED+ "ATENCION... el n de campos en BD es menor que el n de celdas declaradas en Parametros_FV.py")
        print ( " se crean nuevos campos en tabla datos_celdas")
        print ("-" * 50)
        for K in range(nceldas):
            try:
                Sql = f"ALTER TABLE `datos_celdas_{equipo}` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
    elif ncel > nceldas:
        print (Fore.RED+ "ATENCION... el n de campos en BD es mayor que el n de celdas declaradas en Parametros_FV.py")
        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
        print ("-" * 50)
        for K in range(nceldas,ncel):
            try:
                Sql = f"ALTER TABLE `datos_celdas_{equipo}` DROP `C{K+1}`"
                cursor.execute(Sql)
                db.commit()
                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} borrado')
            except:
                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
    
except:
    print(f'Error en la actualizacion del numero de campos en datos_celdas_{equipo}')
    
cursor.close()
db.close()


# ==========================================================
#----------------- BUCLE -----------------------------------
# ==========================================================


#print(Fore.CYAN,"Empieza el monitoreo de celdas desde daly hay :", Fore.RED,nceldas , Fore.CYAN,"que monitorizar")
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
    datos_globales['Vbat'] = round(partes[0] / 10)
    datos_globales['Ibat'] = round ((30000 - partes[2] ) / 10) # negativo descargando positivo cargando (30000-datos[6])/10
    datos_globales['SOC']= round(partes[3] / 10)

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
    datos_globales['Temp_Max'] = round(partes[0]-40)
    datos_globales['Temp_Min'] = round(partes[2]-40)

    
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
        
        

    #datos_globales['cargador_corriendo'] = partes[2]
    #datos_globales['carga en funcionamiento'] = partes[3]
    #datos_globales['state_bits'] = state_bits
    datos_globales['Nciclos'] = round(partes[5])
    datos_globales['Temperaturas']=round(partes[1])
    datos_globales['Switches'] = states

      

def leer_Vceldas_bms():
    CeldaMax = ('C1',0)
    CeldaMin = ('C1',1000)
## leemos desde la DALY los valores
    contenedor_datos = []
    if not contenedor_datos:
        max_responses = math.ceil(nceldas / 3)
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
    i = 0

    datos_globales['Vceldas'] = []
    
    for response_bytes in respuesta:
     
        partes = struct.unpack(">b 3h x", respuesta[x-1])
        if partes[0] != x:
            logger.warning("frame out of order, expected %i, got %i" % (x, response_bytes[0]))
            continue
        
        for value in partes[1:]:
            values[i] = value /1000
            datos_globales['Vceldas'] = datos_globales.get('Vceldas', []) + [values[i]]
            i += 1
        
            if len(values) == nceldas:
                break   
    for K in range(nceldas):
                K1 = f'C{K+1}'
                 
                Vcelda_max[K] = round(max(Vcelda_max[K],values[K]),3)
                Vcelda_min[K] = round(min(Vcelda_min[K],values[K]),3)
           
                if values[K] > CeldaMax[1]: CeldaMax = (K1,round(values[K],2))

                if values[K] < CeldaMin[1]: CeldaMin = (K1,round(values[K],2))
                

    datos_globales['Max'] = Vcelda_max
    datos_globales['Min'] = Vcelda_min



#######################
if usar_daly == 1: # 1 entra 0 no entraria dato declaro en parametros.py
    
    contador_ciclos = 0
    

    dia = time.strftime("%Y-%m-%d")
    
    for i in range(nceldas): Nombre_Celdas[i] = f'C{i+1}' 
    
    ee='58.1'
    try:
            
        while True:
            ee='58.88'
            
            
            
            
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_sg = time.time()
            diasemana = time.strftime("%w")
            hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
            dia_anterior = dia
            dia = time.strftime("%Y-%m-%d")
                
            ee='10'
            if dia_anterior != dia: #cambio de dia
                Vcelda_max = [0.0] * nceldas 
                Vcelda_min = [1000.0] * nceldas
                CeldaMax = ('C1',0)
                CeldaMin = ('C1',1000)
            ## Inicializacion valores diario a las 00:00
            
                if leer_ciclos_daly == 1:leer_ciclos_bms()
                

            ee='58.30'
            ########lectura de los datos que queramos tener se configura en parametros_fv.py ##########
            if leer_ciclos_daly == 1:leer_ciclos_bms()       #lee los ciclos el numero de celdas y varias cosas mas que no tengo claro que son
            if leer_soc_daly == 1:leer_soc_bms()             #lee soc ibat vbat
            if leer_temp_daly == 1:leer_temp_bms()           #lee la temperaturas 
             
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
                print('Error conexion BD')
                           
            try:
                ####  ARCHIVOS RAM en BD ############ 
                ee = 100
                salida = json.dumps(datos_globales)
                ee = 110
                        
                        #print(salida)
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'BMS_{equipo}'")
                #print(sql)
                cursor.execute(sql)
                        
                        
            except:
                print('error, Grabacion tabla RAM equipos', ee)


            
            
            try:
                ee='70'
                #comprobamos si el valor es mayor o menor al programado en parametros_fv.py para darlo como error de lectura
                # y asi no desvirtualizar la realidad.
             
                
                if grabar_datos_daly == 1 and n_muestras_daly_contador == n_muestras_daly-1:
                    n_muestras_daly_contador = 0         
                    # Insertar Registro en BD
                    campos = ",".join(Nombre_Celdas)
                    campos = 'Ibat,' + campos
                    pepe = datos_globales['Vceldas']    
                    valores = "','".join(str(v) for v in datos_globales['Vceldas'])
                    valores = str(datos_globales['Ibat']) +  "','" + valores
                        
                    Sql = f"INSERT INTO datos_celdas_{equipo} ("+campos+") VALUES ('"+valores+"')"
                        
                    #print(Sql)
                        
                    cursor.execute(Sql)
                    db.commit()
                    print (Fore.RED+'G' +Fore.RESET,end='',flush=True)
                        
                        
                else:
                    n_muestras_daly_contador+=1
                    if DEBUG == 0: print (Fore.BLUE+'D', end = '',flush=True)
                    
                ee='75'    
                db.commit()

                
            except:
                print('error, BD', Sql)
                db.rollback()
                pass    
            
    except:
        print ('Error en bucle ',ee)
        pass

