#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-12-08

import time,sys
import json
from multiprocessing import Pool

import MySQLdb 

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_ads.py') #+Style.RESET_ALL)

#Parametros Instalacion FV
#from Parametros_FV import *

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
                
#Comprobacion argumentos en comando
simular = DEBUG= 0
"""
arg = [x.upper() for x in sys.argv]
arg= arg[1:] # quito argumento con nombre del archivo
print(Fore.BLUE+'Comandos='+Fore.GREEN,arg)
for x in arg:
    if x[0]=='-': x= x[1:]
    exec(x)
"""

narg = len(sys.argv)
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta 
if '-p1' in sys.argv: DEBUG= 1 
elif '-p2' in sys.argv: DEBUG= 2 
elif '-p' in sys.argv: DEBUG= 100 


if sum(usar_ADS)== 0:
    print (subprocess.getoutput('sudo systemctl stop fv_ads'))
    sys.exit()


bus = SMBus(1) # Activo Bus I2C para ADS o PCF

def ADS_captura (ADS):  # como entrada solo el indice del ADS de las listas definidas en Parametros_FV.py    
    Ncapturas = 0
    time.sleep(0.02 * ADS) #multiplexo un poco los distintos procesos
    
    if DEBUG >=1:
        print()
        print(Fore.BLUE+'=' *40,'Proceso',ADS, nombre_ADS[ADS], '=' *40) 
    
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      (nombre_ADS[ADS],'{}'))
        db.commit()
        
    except:
        print(Fore.RED+f'Registro RAM - clave = {nombre_ADS[ADS]} ya creado')
    
    print (f'Activando ADS en direccion {direccion_ADS[ADS]}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS[ADS], busnum=1)
    
    d_ads = {}
    N = 60/tmuestra_ADS[ADS] * 1 # contador para refrescar Parametros_FV.py cada X minutos
    N1 = 0
    
    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            tp0= time.process_time()
            ERR_ADS = [0,0,0,0]  # Error bruto capturas ADS
            
            N1 -= 1 # solo recargo N veces independientemente del numero de ADS activos
            if N1 < 0 :
                ee = '20'
                print(Fore.CYAN+time.strftime("%Y-%m-%d %H:%M:%S"),
                      f' -- Leyendo Parametros_FV.py para {nombre_ADS[ADS]} - Capturas={Ncapturas}')
                Ncapturas = 0 
                try:
                    exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
                except:
                    print ('Error en Parametros_FV.py')
                ee = '20a'
                N1 = N
                ADS_modo = 'Disparado'  # valor por defecto
                if DEBUG >= 1: print (Fore.BLUE+f'Modo {nombre_ADS[ADS]} = '+Fore.GREEN,end='')
                
                for indice, modo in enumerate(modo_ADS[ADS], 0):
                    ee = '20b'
                    if modo == 2:
                        ee = '20c'
                        print(gain_ADS[ADS][indice],rate_ADS[ADS][indice])
                        adc.start_adc(indice,gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                        ee = '20d'
                        ADS_modo = 'Continuo'
                        if DEBUG >= 1: print (f'entrada A{indice} : ', end='')                       
                        break
                    elif modo == 4:
                        ee = '20d'
                        if indice == 0: indice1= 0
                        elif indice == 2: indice1 = 3
                        
                        adc.start_adc_difference(indice1, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                        ADS_modo = 'Continuo_Diferencial'
                        if DEBUG >= 1: print (f'entrada A{indice} : ', end='')
                        break
            
            if ADS_modo == 'Disparado':      
                ee = '30'
                for indice, modo in enumerate(modo_ADS[ADS], 0):
                    if modo == 1:
                        ee = '30a'
                        L_ADS = [adc.read_adc(indice, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice]) for j in range(bucles_ADS[ADS][indice]) ]
                    elif modo == 3:
                        ee = '30b' 
                        if indice == 0: indice1= 0
                        elif indice == 2: indice1 = 3
                        
                        L_ADS = [adc.read_adc_difference(indice1, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice]) for j in range(bucles_ADS[ADS][indice]) ]
                    ee = '30c'
                    if modo != 0:
                        #print(nombre_ADS[ADS],f'-- indice:{indice} - modo={modo}-gain={gain_ADS[ADS][indice]}-rate={rate_ADS[ADS][indice]} - bucles={bucles_ADS[ADS][indice]}')
                    
                        MED_ADS = sum(L_ADS)/bucles_ADS[ADS][indice]
                        d_ads[var_ADS[ADS][indice]] = round(MED_ADS * 0.000125 * res_ADS[ADS][indice] / gain_ADS[ADS][indice] ,3)            
                    
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS)
                    
                        if DEBUG >=100:
                             print (f'L_ADS-A{indice}={L_ADS} - {MED_ADS} Err:{ERR_ADS[indice]}- {var_ADS[ADS][indice]} ={d_ads[var_ADS[ADS][indice]]}')
    
            else: # 'Continuo o continuo diferencial'
                ee = '40'                    
                L_ADS = ([0.0] * bucles_ADS[ADS][indice])
                for i in range(bucles_ADS[ADS][indice]):
                    L_ADS[i] = adc.get_last_result() 
                    time.sleep (1/rate_ADS[ADS][indice])   
                
                MED_ADS = sum(L_ADS)/bucles_ADS[ADS][indice]
                d_ads[var_ADS[ADS][indice]] = round(MED_ADS * 0.000125 * res_ADS[ADS][indice] / gain_ADS[ADS][indice] ,3)            
            
                ERR_ADS[indice] = max(L_ADS) - min(L_ADS)
            
                if DEBUG >=100:
                    print (f'L_ADS-A{indice}={L_ADS}-{MED_ADS} Err:{ERR_ADS}- {var_ADS[ADS][indice]}={d_ads[var_ADS[ADS][indice]]}')
        
            ee = '50'                     
            t1 = (time.perf_counter() -t0)* 1000
            
            if DEBUG>=1:
                t = str(round(time.time(),3))
                if ADS == 0:
                    print (Fore.RESET, end='')
                elif ADS ==1:
                    print (Fore.BLUE, end='')
                elif ADS ==2:
                    print (Fore.CYAN, end='')
                else:
                    print (Fore.RED, end='')
                
                print (f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = ', d_ads)
            
            salida = json.dumps(d_ads)
            ee = '60'                     
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{nombre_ADS[ADS].upper()}'")
            cursor.execute(sql)
            db.commit()
        
            t2 = (time.perf_counter() - t0) * 1000
            tp2 =(time.process_time() - tp0) * 1000
            
            ee = '70'
            if DEBUG >= 2:
                print (f'{time.time():.5f} / {ADS}: t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:', end='')
                if ADS_modo == 'Disparado': print (rate_ADS[ADS],'Bucles:',bucles_ADS[ADS])
                else: print (rate_ADS[ADS],'Bucles:',bucles_ADS[ADS], f'- {ADS_modo} entrada {indice}')
            
            ee = '80'    
            if DEBUG >=100:
                print (Fore.CYAN+'*' * 80)
                print ('*' * 80)
            
            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra_ADS[ADS]-t3,0))
            Ncapturas += 1
            
        except:
            print(f'{tiempo} - Error {ee} en {nombre_ADS[ADS]}')
            #sys.exit()
        
if __name__ == '__main__':    

    if '-ADS1' in sys.argv: # fuerzo solo ADS1
        usar_ADS = [1,0]
    elif '-ADS4' in sys.argv: # fuerzo solo ADS4
        usar_ADS = [0,1]
    
    ADS_activos = [ i for i in range(len(usar_ADS)) if usar_ADS[i] == 1 ] # indices ADS activos


    print (Fore.RESET+'=' * 50)
    print(Fore.BLUE+'ADS_activos=')
    for i in ADS_activos: 
        print(Fore.RED+f' -{nombre_ADS[i]}={Fore.BLUE} direc={direccion_ADS[i]} - var= {var_ADS[i]} - modo={modo_ADS[i]} -',
              f'rate ={rate_ADS[i]} \n        tmuestra={tmuestra_ADS[i]} - bucles={bucles_ADS[i]} - gain={gain_ADS[i]} - ratio={res_ADS[i]}')
        print()
    print (Fore.RESET+'=' * 50)
    time.sleep(5)

    with Pool(len(ADS_activos)) as p:
        print(p.map(ADS_captura, ADS_activos))
