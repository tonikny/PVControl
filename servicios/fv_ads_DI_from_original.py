#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-22

# #################### Control Ejecucion Servicio ########################################
from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'
#control = 'sum(usar_ADS)'
#exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

import time,sys,os
import json
import multiprocessing
import MySQLdb

from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

from helpers.gestor_logs_DI import GestorLogsDI
from helpers.gestor_parametros_DI import GestorParametrosDI

log_local = GestorLogsDI(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_DI_from_original.py')


##### Parametros_FV.py (lo que se indique en el archivo Parametros.py tiene prevalencia sobre lo aqui indicado) ################

# Load parameters using DI approach
from helpers.gestor_parametros_DI import GestorParametrosDI
from helpers.gestor_logs_DI import GestorLogsDI

log_main = GestorLogsDI(nombre=__name__)
gp_main = GestorParametrosDI(logger=log_main)

parametros = gp_main.leer_parametros("usar_ADS", "nombre_ADS", "direccion_ADS", "var_ADS", 
                                     "tmuestra_ADS", "rate_ADS", "bucles_ADS", 
                                     "gain_ADS", "modo_ADS", "res_ADS",
                                     "servidor", "usuario", "clave", "basedatos")

usar_ADS, nombre_ADS, direccion_ADS, var_ADS, tmuestra_ADS, rate_ADS, bucles_ADS, gain_ADS, modo_ADS, res_ADS, servidor, usuario, clave, basedatos = parametros

parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
t_cambio_parametros = os.path.getmtime(parametros_FV)

# Initialize local variables for parameter updates
nombre_ADS_usar = nombre_ADS
direccion_ADS_usar = direccion_ADS
var_ADS_usar = var_ADS
tmuestra_ADS_usar = tmuestra_ADS
rate_ADS_usar = rate_ADS
bucles_ADS_usar = bucles_ADS
gain_ADS_usar = gain_ADS
modo_ADS_usar = modo_ADS
res_ADS_usar = res_ADS

#Comprobacion argumentos en comando
simular = 0
DEBUG = 0

# Parse command line arguments
if '-s' in sys.argv: simular= 1 # para desarrollo permite simular respuesta
if '-p1' in sys.argv: 
    DEBUG = 1
elif '-p2' in sys.argv: 
    DEBUG = 2
elif '-p' in sys.argv: 
    DEBUG = 100
elif '-p3' in sys.argv:
    DEBUG = 3

bus = SMBus(1) # Activo Bus I2C para ADS o PCF

def ADS_captura (ADS):  # como entrada solo el indice del ADS de las listas definidas en Parametros_FV.py
    # Create local instances of DI components for this process
    from helpers.gestor_logs_DI import GestorLogsDI
    from helpers.gestor_parametros_DI import GestorParametrosDI
    from helpers.gestor_bd import GestorBD
    
    # Create instances with DI
    logger_local = GestorLogsDI(f"{__name__}-ADS{ADS}")
    gp_local = GestorParametrosDI(logger=logger_local)
    
    Ncapturas = 0
    time.sleep(0.02 * ADS) #multiplexo un poco los distintos procesos

    if DEBUG >=1:
        print()
        print(Fore.BLUE+'=' *40,'Proceso',ADS, nombre_ADS[ADS], '=' *40)
        # Also log using the DI logger
        logger_local.info(Fore.BLUE+'=' *40+f'Proceso{ADS} {nombre_ADS[ADS]}=' *40)

    # Use the DI database manager
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)
    
    # Attempt to insert the equipment record
    existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS[ADS])
    if not existe:
        print(Fore.RED+f'Registro RAM - clave = {nombre_ADS[ADS]} ya creado')

    print (f'Activando ADS en direccion {direccion_ADS[ADS]}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS[ADS], busnum=1)

    d_ads = {}
    # Use the same parameter file path as the original
    PARAMETROS_FV_PATH = "/home/pi/PVControl+/Parametros_FV.py"
    try:
        t_cambio_parametros = os.path.getmtime(PARAMETROS_FV_PATH) - 100
    except:
        t_cambio_parametros = time.time() - 1000  # fallback if file doesn't exist
    
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

            # Check for parameter changes using the original approach
            try:
                current_mtime = os.path.getmtime(PARAMETROS_FV_PATH)
                if current_mtime != t_cambio_parametros:
                    # Reload parameters using exec() like the original to update globals
                    exec(open(PARAMETROS_FV_PATH).read(), globals())
                    t_cambio_parametros = current_mtime

                    ee = '20'
                    if DEBUG >=1: print(Fore.CYAN+time.strftime("%Y-%m-%d %H:%M:%S"),
                                        f' -- Leyendo Parametros_FV.py para {nombre_ADS[ADS]} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    try:
                        # In the DI version, we update parameters via the GestorParametrosDI
                        # rather than exec(open(...))
                        pass
                    except:
                        print ('Error recargando parámetros')

                    ee = '20a'
                    #N1 = N
                    ADS_modo = 'Disparado'  # valor por defecto
                    if DEBUG >= 1: print (Fore.BLUE+f'Modo {nombre_ADS[ADS]} = '+Fore.GREEN,end='')

                    for indice, modo in enumerate(modo_ADS[ADS], 0):
                        ee = '20b'
                        if modo == 2:
                            ee = '20c'
                            #print(gain_ADS[ADS][indice],rate_ADS[ADS][indice])
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

            except FileNotFoundError:
                # Handle case where parameter file doesn't exist
                pass
            except Exception as e:
                logger_local.error(f'Error verificando cambios en parámetros: {e}')
                print(f'Error verificando cambios en parámetros: {e}')

            ee = 30.1
            #print (ADS_modo)
            ee = 30.2

            if ADS_modo == 'Disparado':
                ee = '30'
                for indice, modo in enumerate(modo_ADS[ADS], 0):
                    if modo == 1:
                        ee = '30a'
                        # Add error handling for I2C operations
                        def leer_adc_normal():
                            return adc.read_adc(indice, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                        
                        L_ADS = []
                        for j in range(bucles_ADS[ADS][indice]):
                            try:
                                val = leer_adc_normal()
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):  # Expected I2C errors
                                    print(f"Error lectura ADS{ADS}")
                                    logger_local.error(f"Error lectura ADS{ADS}")
                                    time.sleep(0.005)
                                    # Add a default value or skip
                                    L_ADS.append(0)
                                else:
                                    logger_local.error(f"OSError inesperado en lectura ADS{ADS}: {e}")
                                    raise
                    elif modo == 3:
                        ee = '30b'
                        if indice == 0: indice1= 0
                        elif indice == 2: indice1 = 3
                        
                        # Add error handling for I2C operations
                        def leer_adc_diferencial():
                            return adc.read_adc_difference(indice1, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                        
                        L_ADS = []
                        for j in range(bucles_ADS[ADS][indice]):
                            try:
                                val = leer_adc_diferencial()
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):  # Expected I2C errors
                                    print(f"Error lectura ADS{ADS}")
                                    logger_local.error(f"Error lectura ADS{ADS} en modo diferencial")
                                    time.sleep(0.005)
                                    # Add a default value or skip
                                    L_ADS.append(0)
                                else:
                                    logger_local.error(f"OSError inesperado en lectura diferencial ADS{ADS}: {e}")
                                    raise
                    ee = '30c'
                    if modo != 0:
                        #print(nombre_ADS[ADS],f'-- indice:{indice} - modo={modo}-gain={gain_ADS[ADS][indice]}-rate={rate_ADS[ADS][indice]} - bucles={bucles_ADS[ADS][indice]}')

                        MED_ADS = sum(L_ADS)/bucles_ADS[ADS][indice] if L_ADS else 0
                        d_ads[var_ADS[ADS][indice]] = round(MED_ADS * 0.000125 * res_ADS[ADS][indice] / gain_ADS[ADS][indice] ,3)

                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0

                        if DEBUG >=100:
                             print (f'L_ADS-A{indice}={L_ADS} - {MED_ADS} Err:{ERR_ADS[indice]}- {var_ADS[ADS][indice]} ={d_ads[var_ADS[ADS][indice]]}')

            else: # 'Continuo o continuo diferencial'
                ee = '40'
                L_ADS = ([0.0] * bucles_ADS[ADS][indice])
                for i in range(bucles_ADS[ADS][indice]):
                    try:
                        L_ADS[i] = adc.get_last_result()
                    except OSError as e:
                        if e.errno in (5, 121):  # Expected I2C errors
                            print(f"Error lectura continua ADS{ADS}")
                            logger_local.error(f"Error lectura continua ADS{ADS}")
                            time.sleep(0.005)
                            L_ADS[i] = 0  # Default value
                        else:
                            logger_local.error(f"OSError inesperado en lectura continua ADS{ADS}: {e}")
                            raise
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
                # Also log using the DI logger
                if ADS == 0:
                    logger_local.debug(Fore.RESET + f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                elif ADS == 1:
                    logger_local.debug(Fore.BLUE + f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                elif ADS == 2:
                    logger_local.debug(Fore.CYAN + f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                else:
                    logger_local.debug(Fore.RED + f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')

            salida = json.dumps(d_ads)
            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Use the DI database manager to save data
            gestor_bd.guardar_datos_equipo_dict(nombre_ADS[ADS], tiempo, d_ads)

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

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{tiempo} - Error {ee} en {nombre_ADS[ADS]}....se reinicia el proceso de captura del {nombre_ADS[ADS]}')
            logger_local.error(f"{tiempo} - Error {ee} en {nombre_ADS[ADS]}....se reinicia el proceso de captura del {nombre_ADS[ADS]}")
            logger_local.error(f"Detalle del error: {e}")
            import traceback
            logger_local.error(f"Traza del error: {traceback.format_exc()}")
            sys.exit()

if __name__ == '__main__':
    # Control execution service using DI
    hay_ads_activos = sum(usar_ADS)
    controlar_servicio(servicio, hay_ads_activos)

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

    # Arrancando procesos
    for i in ADS_activos:
        multiprocessing.Process(target = ADS_captura,args=(i,),name = f'ADS{i}').start()

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
                    multiprocessing.Process(target = ADS_captura,args=(i,),name = f'ADS{i}').start()
                    Procesos= multiprocessing.active_children()
                    print (Procesos)

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            print()
            print(Fore.RED + '=' * 50)
            print ('Finalizando fv_ads_DI_from_original.py.......')
            for p in Procesos:
                print(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()