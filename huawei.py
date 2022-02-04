#!/usr/bin/python
# -*- coding: utf-8 -*-
#  version 17/Dic/21
#--------------------------------------------------------------------------
from pyModbusTCP.client import ModbusClient
import time
import sys
import subprocess
import MySQLdb 
import json
from Parametros_FV import *
import pickle

if usar_huawei == 0:
        print (subprocess.getoutput('sudo systemctl stop huawei'))
        sys.exit()
        
hua = ModbusClient()
hua.host(IP_HUAWEI)
hua.port(502)
hua.unit_id(0)
hua.open()

Equipo = 'HUAWEI'
crear_pkl = 0 # poner a 1 para versiones antiguas de PVControl que no usan BD en RAM

DEBUG = False
#Comprobacion argumentos en comando
if '-p' in sys.argv: DEBUG = True # para test .... realiza print en distintos sitios

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' huawei.py')
print()

time.sleep(1)

def leer_datos():
        
    INV = hua.read_holding_registers(32016, 8)               # V e I de strings
    VGR = hua.read_holding_registers(32066,1 )               # V red
    PP =  hua.read_holding_registers(32080, 2)               # Potencia campo FV    
    E  =  hua.read_holding_registers(32086,1 )               # Eficiencia DC/AC
    T  =  hua.read_holding_registers(32087,1 )               # temperatura inversor
    R  =  hua.read_holding_registers(32088,1 )               # Resistencia Aislamiento
    PR =  hua.read_holding_registers(37113, 2)               # Potencia en punto frontera
       
    res = INV + VGR + PP + E + T +  R + PR   
    if DEBUG: print('res=',res)
    
    if res == None: return (None)
    else: return(res)
        
def escribir_datos():       

    i = leer_datos()
    
    if i != None:
        
        #Wred = i[11]
        if i[15] >32768:  i[15] = i[15] - 65536           
        
        datos ={}
        
        datos['Tiempo'] = time.strftime("%Y-%m-%d %H:%M:%S") 
        datos['Tiempo_sg'] = time.time()
        datos['Wred'] = i[15]
        datos['Wplaca'] = i[10]
        datos['Vplaca_1'] = round(i[0]*0.1,2)
        datos['Vplaca_2'] = round(i[2]*0.1,2)
        datos['Vplaca'] = (datos['Vplaca_1'] + datos['Vplaca_2'])/2
        datos['Iplaca_1'] = round(i[1]*0.01,2)
        datos['Iplaca_2'] = round(i[3]*0.01,2)
        datos['Aux1'] = i[13]*0.001
        datos['Temp'] = round(i[12]*0.1,2)
        datos['EFF'] = round(i[11]*0.01,2)
        
        datos['Consumo'] = round(datos['Wplaca']- datos['Wred'],2)
        
        datos['Vred'] = round(i[8]*0.1,2)
        if datos['Vred'] == 0: datos['Vred'] = 230
        
        datos['Ired'] = round(datos['Wred'] / datos['Vred'],2)
        datos['Iplaca'] = round(datos['Wplaca'] / datos['Vred'],2)
        
        if DEBUG: print(datos)
        
        return (datos)
        
    else: return (None)   

try: #inicializamos BD
    # No se crea tabla especifica de fronius              
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try:
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  (Equipo,'{}'))   
        db.commit()
    except:
        pass     
except:
    print (Fore.RED+ 'ERROR inicializando BD RAM')
    sys.exit()

    

while True:
    try:  
        datos = escribir_datos()
        if DEBUG: print('datos=',datos)
    
        if datos != None :
            if crear_pkl == 0:
                try:####  ARCHIVOS RAM en BD ############
                    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            
                    salida = json.dumps(datos)
                    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'HUAWEI'") # grabacion en BD RAM
                        
                    cursor.execute(sql)
                    db.commit()
                except:
                    print(Fore.RED+f'error, Grabacion tabla RAM equipos en {Equipo}')
            else:    
                # lo logico es dejar de grabar el archivo pkl
                with open('/run/shm/datos_huawei.pkl', mode='wb') as f:
                    pickle.dump(datos, f)      
                
    except: 
        hua.close()
        time.sleep(6)
        hua.open()
        pass
    
    time.sleep(t_muestra_huawei)
