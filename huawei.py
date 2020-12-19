#!/usr/bin/python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
#from Parametros_FV import *
from pyModbusTCP.client import ModbusClient
import time
import sys
import subprocess
import MySQLdb 
from Parametros_FV import *
import pickle


if usar_huawei == 0:
        #print (commands.getoutput('sudo systemctl stop srne'))
        print (subprocess.getoutput('sudo systemctl stop huawei'))
        sys.exit()
        
hua = ModbusClient()
hua.host(IP_HUAWEI)
hua.port(502)
hua.unit_id(0)
hua.open()

narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p':    DEBUG = True
else: DEBUG = False

time.sleep(1)

         
def leer_datos():
        
    INV = hua.read_holding_registers(32016, 4)               # V e I de strings
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
        if i[11] >32768:  i[11] = i[11] - 65536           
        
        datos ={}
        
        datos['Tiempo'] = time.strftime("%Y-%m-%d %H:%M:%S") 
        datos['Tiempo_sg'] = time.time()
        datos['Wred'] = i[11]
        datos['Wplaca'] = i[6]
        datos['Vplaca'] = round(i[0]*0.1,2)
        datos['Aux1'] = i[9]*0.001
        datos['Temp'] = round(i[8]*0.1,2)
        datos['EFF'] = round(i[7]*0.01,2)
        
        datos['Consumo'] = round(datos['Wplaca']- datos['Wred'],2)
        
        datos['Vred'] = round(i[4]*0.1,2)
        if datos['Vred'] == 0: datos['Vred'] = 230
        
        datos['Ired'] = round(datos['Wred'] / datos['Vred'],2)
        datos['Iplaca'] = round(datos['Wplaca'] / datos['Vred'],2)
        
        if DEBUG: print(datos)
        
        return (datos)
        
    else: return (None)   

while True:
    try:  
        datos = escribir_datos()
        if DEBUG: print('datos=',datos)
    
        if datos != None :
            with open('/run/shm/datos_huawei.pkl', mode='wb') as f:
                pickle.dump(datos, f) 
    except: 
        hua.close()
        time.sleep(6)
        hua.open()
        pass
    
    time.sleep(t_muestra_huawei)
