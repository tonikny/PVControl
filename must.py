import time
import pymodbus
import Parametros_FV
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import sys
import pickle
import subprocess, sys
from Parametros_FV import *

if usar_must == 0:
        #print (commands.getoutput('sudo systemctl stop srne'))
        print (subprocess.getoutput('sudo systemctl stop must'))
        sys.exit()

modbus = ModbusClient(method='rtu', port=dev_must, baudrate=19200, timeout=1)
modbus.connect()
time.sleep(0.5)

DEBUG = False

datos = [[None]*6 for i in range(n_equipos_must)]
prod  = [[1.0]* n_equipos_must for i in range(1)]
res   = [[0]*1 for i in range(6)]



def leer_datos(a,b):
    
    R1 = modbus.read_holding_registers(15205, 4, unit=a)
    time.sleep(0.5)
    I1 = modbus.read_holding_registers(25205, 11, unit=b)
    time.sleep(0.5)
    I2 = modbus.read_holding_registers(25274, 1, unit=b)
    try:
        #print('a',a,'b',b,'R1',R1,'I1',I1,'I2',I2)
        Vbat = R1.registers[1]*0.1
        Ibat = I2.registers[0]
        Vplaca = R1.registers[0]*0.1
        Iplaca = R1.registers[3]
        Consumo = I1.registers[10]
        Pred = I1.registers[9]
        
        
        if Pred > 65536:
            Pred = 65536*2 - Pred
            
        if Ibat > 32768:
            #print('Ibat_ant', Ibat)
            Ibat = (32768*2 - Ibat) 
            #print( 'Ibat_post', Ibat)         
            
        else:
            Ibat = Ibat*(-1)
        #if DEBUG: print (Vbat, Vplaca, Iplaca, 'Consumo', Consumo,'Pred', Pred,'Ibat',Ibat)
        
        datos=[Vbat,Vplaca,Iplaca,Consumo,Pred,Ibat]
        if DEBUG: print(datos)
        return (datos)
        
    except:
        print ('error lectura')
        
        return None
        pass
        
    
        
while True:
    
    time.sleep(t_muestra_must)
    
    for i in range(n_equipos_must):    
        datos[i] = leer_datos(i+1,i+4)
    #print(datos)  

    for i in range(6):
        for j in range(n_equipos_must):    
           res[i][0] += prod[0][j] * datos[j][i]
           
    Vbat = round(res[0][0] / n_equipos_must,2)
    Vplaca = round(res[1][0] / n_equipos_must,2)
    Iplaca = round(res[2][0]/Vbat,2)
    Consumo = res[3][0]
    Pred = res[4][0]
    Ibat= res[5][0]
           
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    tiempo_sg = time.time()
    
    res=[[0], [0], [0], [0], [0], [0]]
    
    
    datos_p = {'Tiempo_sg': tiempo_sg,'Tiempo':tiempo,'Vbat':Vbat,'Vplaca':Vplaca,'Iplaca':Iplaca,'Consumo':Consumo,'Pred':Pred,'Ibat':Ibat}
    if DEBUG: print(datos_p)
    if datos != None :
        with open('/run/shm/datos_must.pkl', mode='wb') as f:
            pickle.dump(datos_p, f)
        
      
    
    

