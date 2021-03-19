import socket
import sys
import time
import struct
import pickle
from Parametros_FV import *


if usar_goodwe == 0:
        #print (commands.getoutput('sudo systemctl stop srne'))
        print (subprocess.getoutput('sudo systemctl stop goodwe'))
        sys.exit()

narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-p': DEBUG = True
else: DEBUG = False

EFF=100


a = [0xaa,0x55,0xc0,0x7f,0x01,0x06,0x00,0x02,0x45]
b = bytearray(a)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.settimeout(5)

while True:
    t1=time.time()
    
    try:
        s.sendto(b, (IP_GOODWE, 8899))
          
        data, address = s.recvfrom(142)
        #if DEBUG:print(data,HEX)
    except:
        print('timeout')
        time.sleep(0.5)
        data=[]
        pass
    
    if len(data)==142:
        d = struct.unpack('>7B 2h 1B 2h 25B 4h 1B 5h 22B 1h 58B',data)
        if DEBUG:print(d)
        datos ={}
        datos['Tiempo'] = time.strftime("%Y-%m-%d %H:%M:%S") 
        datos['Tiempo_sg'] = time.time()
        datos['Vbat'] = round((d[13]*256+d[14])*0.1,2)
        datos['Ibat'] = round((d[21]*256+d[22])*0.1,2)*(-1)**(d[33]+1)
        modo_bat = d[33]
        print(datos['Vbat'],datos['Ibat'],'Mod_bat',modo_bat)
        datos['Wplaca'] = round((d[7]*d[8]+d[10]*d[11])/100,2)
        datos['Vred'] = d[37]/10
        
        datos['Fred'] = d[40]/100
        datos['Winv'] = d[69]
        
        datos['IE'] = d[73]
        if datos['Wplaca'] > 0 : datos['EFF']=round((datos['Winv']/datos['Wplaca'])*100,2)
        else: datos['EFF'] = 100
        datos['Wred'] = round(d[39],2)*(-1)**(datos['IE']+1)
        datos['Ired'] = round(datos['Wred']/datos['Vred'],2)
        #datos['Wbat'] =         
        datos['Consumo'] = round(datos['Winv']-datos['Wred'],2)
        datos['Vplaca'] = (d[7]+d[10])/20
        datos['Iplaca'] = round(datos['Wplaca'] / datos['Vbat'],2)
        #datos['Ired'] = round(datos['Wred'] / datos['Vred'],2)
        datos['Temp'] = d[48]/10
        
        if DEBUG:print(datos)
        
        with open('/run/shm/datos_goodwe.pkl', mode='wb') as f:
            pickle.dump(datos, f)
        
    t2 = time.time()-t1
    if t2  < t_muestra_goodwe:
        time.sleep(t_muestra_goodwe-t2)
        
        
        
        
