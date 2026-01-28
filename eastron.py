import serial
import time
import struct
import libscrc
from Parametros_FV import *
import pickle

ser = serial.Serial()
ser.baudrate = 2400
ser.parity = 'N'
ser.port=dev_eastron
ser.timeout = 1
ser.open()
time.sleep(1)
    
a=0
k=0
DEBUG = True
read_meter = [0x01,0x04,0x00,0x00,0x00,0x1A,0x71,0xC1]

def capturar_datos()

    ser.write(serial.to_bytes(read_meter)) 
    time.sleep(0.4)
    rcv = ser.read(57)    
    datos = struct.unpack(">3b 13f 2b",rcv)       
    
    if DEBUG: print('V',round(datos[3],2),'   I',round(datos[6],2),'   W',round(datos[9],2),'   VA',round(datos[12],2),'   VAR',round(datos[15],2),round(a,2),round(datos[6]/a,3))
    
    Tiempo_sg = time.time()
    Tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    
    datos = {'Tiempo_sg':Tiempo_sg,'Tiempo':Tiempo,'Vred':round(datos[3],2),'Ired':round(datos[9]/datos[3],2),'Consumo':-round(datos[9],2)}
    if datos != None : return(datos)
    else: return(None)
    
while True:

    t1 = time.time()
    
    datos = capturar_datos()
    
    if datos != None:
        with open('/run/shm/datos_eastron.pkl', mode='wb') as f:
            pickle.dump(datos, f)
    
    else:
        ser.close()
        time.sleep(1)
        ser.open()
    
    t2 = time.time()
    dt = t2-t1
    if (dt < 1):
        time.sleep(1-dt) 

        
    
    