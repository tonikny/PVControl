#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-22

import time,sys,os
import json
import multiprocessing
import MySQLdb 

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

from params.fv_ads_params import load_parametros 
import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


##### Parametros_FV.py (lo que se indique en el archivo Parametros.py tiene prevalencia sobre lo aqui indicado) ################

# usar_ADS = [0,0] # activar o no el ADS
# nombre_ADS = ['ADS1','ADS4']                                         # Nombre de los ADS
# direccion_ADS = [72,75]                                              # direccion I2C del ADS

# var_ADS = [['Vbat','Aux1', 'Vplaca','Aux2'],['Ibat','','Iplaca','']] # Nombre de las variables a capturar

# tmuestra_ADS = [5,5]                                                 # tiempo en sg entre capturas
# rate_ADS = [[250,250,250,250],[250,0,250,0]]                         # datarate de lectura
# bucles_ADS = [[10,5,5,5], [4,0,4,0]]                                 # Numero de bucles de lectura

# gain_ADS = [[2,2,2,2], [16,0,16,0]]                                  # Voltios Fondo escala 1=4,096V - 2=2.048V - 16= 256mV
# modo_ADS = [[1,1,1,1], [3,0,3,0]]                                    # 0=desactivado, 1=disparado, 2= Continuo, 3=diferencial, 4=diferencial_continuo
# res_ADS = [[47.46,47.46,47.46,47.46],[100/0.075,0,100/0.075,0]]      # ratio lectura ADS - Lectura real
######################################################

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_ads.py') #+Style.RESET_ALL)
par = load_parametros(parametros_FV)
t_cambio_parametros = os.path.getmtime(parametros_FV)

# #################### Control Ejecucion Servicio ########################################
servicio = 'fv_ads'
control = 'sum(par.usar_ADS)'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


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

bus = SMBus(1) # Activo Bus I2C para ADS o PCF

def ADS_captura (ADS):  # como entrada solo el indice del ADS de las listas definidas en Parametros_FV.py    
    # global parametros_FV
    
    Ncapturas = 0
    time.sleep(0.02 * ADS) #multiplexo un poco los distintos procesos
    
    if DEBUG >=1:
        print()
        print(Fore.BLUE+'=' *40,'Proceso',ADS, par.nombre_ADS[ADS], '=' *40) 
    
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",(par.nombre_ADS[ADS],'{}'))
        db.commit()
        
    except:
        print(Fore.RED+f'Registro RAM - clave = {par.nombre_ADS[ADS]} ya creado')
    
    print (f'Activando ADS en direccion {par.direccion_ADS[ADS]}')
    adc = Adafruit_ADS1x15.ADS1115(address=par.direccion_ADS[ADS], busnum=1)
    
    d_ads = {}
    t_cambio_parametros = os.path.getmtime(parametros_FV) - 100
    ADS_modo = 'Disparado'  # valor por defecto
    
    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            tp0= time.process_time()
            ERR_ADS = [0,0,0,0]  # Error bruto capturas ADS
            ee = '11'
            #print(t_cambio_parametros)
            ee = '12'
            #print(parametros_FV)
            ee = '13'
            
            if os.path.getmtime(parametros_FV) != t_cambio_parametros: #recargo Parametros_FV.py si hay cambios
                ee = '20'
                if DEBUG >=1: print(Fore.CYAN+time.strftime("%Y-%m-%d %H:%M:%S"),
                                    f' -- Leyendo Parametros_FV.py para {par.nombre_ADS[ADS]} - Capturas={Ncapturas}')
                Ncapturas = 0 
                try:
                    parametros = load_parametros(parametros_FV)
                    t_cambio_parametros = os.path.getmtime(parametros_FV)
                except:
                    print ('Error en Parametros_FV.py')
            
                ee = '20a'
                #N1 = N
                ADS_modo = 'Disparado'  # valor por defecto
                if DEBUG >= 1: print (Fore.BLUE+f'Modo {par.nombre_ADS[ADS]} = '+Fore.GREEN,end='')
                
                for indice, modo in enumerate(par.modo_ADS[ADS], 0):
                    ee = '20b'
                    if modo == 2:
                        ee = '20c'
                        #print(par.gain_ADS[ADS][indice],par.rate_ADS[ADS][indice])
                        adc.start_adc(indice,gain=par.gain_ADS[ADS][indice], data_rate=par.rate_ADS[ADS][indice])
                        ee = '20d'
                        ADS_modo = 'Continuo'
                        if DEBUG >= 1: print (f'entrada A{indice} : ', end='')                       
                        break
                    elif modo == 4:
                        ee = '20d'
                        if indice == 0: indice1= 0
                        elif indice == 2: indice1 = 3
                        
                        adc.start_adc_difference(indice1, gain=par.gain_ADS[ADS][indice], data_rate=par.rate_ADS[ADS][indice])
                        ADS_modo = 'Continuo_Diferencial'
                        if DEBUG >= 1: print (f'entrada A{indice} : ', end='')
                        break
            
            ee = 30.1
            #print (ADS_modo)
            ee = 30.2
            print("ADS_modo",ADS_modo)
            if ADS_modo == 'Disparado':      
                ee = '30'
                for indice, modo in enumerate(par.modo_ADS[ADS], 0):
                    if modo == 1:
                        ee = '30a'
                        L_ADS = [adc.read_adc(indice, gain=par.gain_ADS[ADS][indice], data_rate=par.rate_ADS[ADS][indice]) for j in range(par.bucles_ADS[ADS][indice]) ]
                    elif modo == 3:
                        ee = '30b' 
                        if indice == 0: indice1= 0
                        elif indice == 2: indice1 = 3
                        
                        # for j in range(par.bucles_ADS[ADS][indice]):
                        #     print(f'[adc.read_adc_difference({indice1}, gain={par.gain_ADS[ADS][indice]}, data_rate={par.rate_ADS[ADS][indice]}) range(par.bucles_ADS[ADS][indice]={range(par.bucles_ADS[ADS][indice])}')
                        L_ADS = [adc.read_adc_difference(indice1, gain=par.gain_ADS[ADS][indice], data_rate=par.rate_ADS[ADS][indice]) for j in range(par.bucles_ADS[ADS][indice]) ]
                    ee = '30c'
                    if modo != 0:
                        #print(par.nombre_ADS[ADS],f'-- indice:{indice} - modo={modo}-gain={par.gain_ADS[ADS][indice]}-rate={par.rate_ADS[ADS][indice]} - bucles={par.bucles_ADS[ADS][indice]}')
                    
                        MED_ADS = sum(L_ADS)/par.bucles_ADS[ADS][indice]

                        var_name = par.var_ADS[ADS][indice]
                        if not var_name: continue
                        d_ads[var_name] = round(MED_ADS * 0.000125 * par.res_ADS[ADS][indice] / par.gain_ADS[ADS][indice] ,3)            
                    
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS)
                    
                        if DEBUG >=100:
                             print (f'L_ADS-A{indice}={L_ADS} - {MED_ADS} Err:{ERR_ADS[indice]}- {par.var_ADS[ADS][indice]} ={d_ads[par.var_ADS[ADS][indice]]}')
    
            else: # 'Continuo o continuo diferencial'
                ee = '40'
                print('Continuo o continuo diferencial: indice=',indice, par.modo_ADS[ADS][indice], par.bucles_ADS[ADS][indice], par.gain_ADS[ADS][indice], par.rate_ADS[ADS][indice])
                L_ADS = ([0.0] * par.bucles_ADS[ADS][indice])
                for i in range(par.bucles_ADS[ADS][indice]):
                    L_ADS[i] = adc.get_last_result() 
                    time.sleep (1/par.rate_ADS[ADS][indice])   
                
                MED_ADS = sum(L_ADS)/par.bucles_ADS[ADS][indice]

                var_name = par.var_ADS[ADS][indice]
                if not var_name: continue
                d_ads[var_name] = round(MED_ADS * 0.000125 * par.res_ADS[ADS][indice] / par.gain_ADS[ADS][indice] ,3)            
            
                ERR_ADS[indice] = max(L_ADS) - min(L_ADS)
            
                if DEBUG >=100:
                    print (f'L_ADS-A{indice}={L_ADS}-{MED_ADS} Err:{ERR_ADS}- {par.var_ADS[ADS][indice]}={d_ads[par.var_ADS[ADS][indice]]}')
        
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
                
                print (f'{t[-6:]}: {par.nombre_ADS[ADS]}-Modo={par.modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = ', d_ads)
            
            salida = json.dumps(d_ads)
            ee = '60'                     
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE equipos SET tiempo=%s, sensores=%s WHERE id_equipo=%s",(tiempo, salida, par.nombre_ADS[ADS].upper()))
            db.commit()
        
            t2 = (time.perf_counter() - t0) * 1000
            tp2 =(time.process_time() - tp0) * 1000
            
            ee = '70'
            if DEBUG >= 2:
                print (f'{time.time():.5f} / {ADS}: t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:', end='')
                if ADS_modo == 'Disparado': print (par.rate_ADS[ADS],'Bucles:',par.bucles_ADS[ADS])
                else: print (par.rate_ADS[ADS],'Bucles:',par.bucles_ADS[ADS], f'- {ADS_modo} entrada {indice}')
            
            ee = '80'    
            if DEBUG >=100:
                print (Fore.CYAN+'*' * 80)
                print ('*' * 80)
            
            t3 = (time.perf_counter() - t0)
            time.sleep(max(par.tmuestra_ADS[ADS]-t3,0))
            Ncapturas += 1
            
        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            print(Fore.RED + f"{tiempo} - Error {ee} en {par.nombre_ADS[ADS]}: {repr(e)}")
            print(f'{par.nombre_ADS[ADS]}....se reinicia el proceso de captura del {par.nombre_ADS[ADS]}')
            sys.exit(1)

        
if __name__ == '__main__':    

    if '-ADS1' in sys.argv: # fuerzo solo ADS1
        par.usar_ADS = [1,0]
    elif '-ADS4' in sys.argv: # fuerzo solo ADS4
        par.usar_ADS = [0,1]
    
    ADS_activos = [ i for i in range(len(par.usar_ADS)) if par.usar_ADS[i] == 1 ] # indices ADS activos


    print (Fore.RESET+'=' * 50)
    print(Fore.BLUE+'ADS_activos=')
    for i in ADS_activos: 
        print(Fore.RED+f' -{par.nombre_ADS[i]}={Fore.BLUE} direc={par.direccion_ADS[i]} - var= {par.var_ADS[i]} - modo={par.modo_ADS[i]} -',
              f'rate ={par.rate_ADS[i]} \n        tmuestra={par.tmuestra_ADS[i]} - bucles={par.bucles_ADS[i]} - gain={par.gain_ADS[i]} - ratio={par.res_ADS[i]}')
        print()
    print (Fore.RESET+'=' * 50)
    time.sleep(5)
    
    # Arrancando procesos
    for i in ADS_activos:
        multiprocessing.Process(target = ADS_captura,args=(i,),name = f'p_ADS{i}').start()
    
    Procesos= multiprocessing.active_children() # lista procesos
    print ('Procesos activos=',Procesos)
    
    # Bucle     
    while True:
        try:
            for p in Procesos:
                if not p.is_alive():
                    print (f'Proceso {p} parado',p.name)
                    time.sleep(3)
                    i=int(p.name[-1])
                    multiprocessing.Process(target = ADS_captura,args=(i,),name = f'p_ADS{i}').start()
                    Procesos= multiprocessing.active_children()
                    print (Procesos)
                    
            time.sleep(1)
            
        except:
            time.sleep(1)
            print()
            print(Fore.RED + '=' * 50)
            print ('Finalizando fv_ads.py.......')
            for p in Procesos:
                print(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
