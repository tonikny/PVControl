#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-12-22

# #################### Control Ejecucion Servicio ########################################
from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'
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

from helpers.logger_multiprocessing import LoggerMultiprocessing

log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_with_new_logger.py')


##### Parametros_FV.py (lo que se indique en el archivo Parametros.py tiene prevalencia sobre lo aqui indicado) ################

# Load parameters using the original approach (stable for multiprocessing)
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
exec(open(parametros_FV).read(),globals()) # carga inicial Parametros_FV.py
t_cambio_parametros = os.path.getmtime(parametros_FV)

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
    from helpers.logger_multiprocessing import LoggerMultiprocessing
    from helpers.gestor_parametros_DI import GestorParametrosDI
    from helpers.gestor_bd import GestorBD
    
    # Create instances with DI
    logger_local = LoggerMultiprocessing(f"{__name__}-ADS{ADS}")
    gp_local = GestorParametrosDI(logger=logger_local)
    
    Ncapturas = 0
    time.sleep(0.02 * ADS) #multiplexo un poco los distintos procesos

    if DEBUG >=1:
        print()
        logger_local.info(Fore.BLUE+'=' *40+'Proceso'+str(ADS)+str(nombre_ADS[ADS])+'=' *40)

    # Use the DI database manager
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)
    
    # Attempt to insert the equipment record
    existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS[ADS])
    if not existe:
        logger_local.manual(Fore.RED+f'Registro RAM - clave = {nombre_ADS[ADS]} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion_ADS[ADS]}')
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
                    if DEBUG >=1: 
                        logger_local.info(Fore.CYAN+time.strftime("%Y-%m-%d %H:%M:%S")+
                                    f' -- Leyendo Parametros_FV.py para {nombre_ADS[ADS]} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    try:
                        # In the DI version, we update parameters via the GestorParametrosDI
                        # rather than exec(open(...))
                        pass
                    except:
                        logger_local.manual('Error recargando parámetros')

                    ee = '20a'
                    #N1 = N
                    ADS_modo = 'Disparado'  # valor por defecto
                    if DEBUG >= 1: 
                        logger_local.info(Fore.BLUE+f'Modo {nombre_ADS[ADS]} = '+Fore.GREEN)

                    for indice, modo in enumerate(modo_ADS[ADS], 0):
                        ee = '20b'
                        if modo == 2:
                            ee = '20c'
                            #print(gain_ADS[ADS][indice],rate_ADS[ADS][indice])
                            adc.start_adc(indice,gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                            ee = '20d'
                            ADS_modo = 'Continuo'
                            if DEBUG >= 1: 
                                logger_local.info(f'entrada A{indice} : ')
                            break
                        elif modo == 4:
                            ee = '20d'
                            if indice == 0: indice1= 0
                            elif indice == 2: indice1 = 3

                            adc.start_adc_difference(indice1, gain=gain_ADS[ADS][indice], data_rate=rate_ADS[ADS][indice])
                            ADS_modo = 'Continuo_Diferencial'
                            if DEBUG >= 1: 
                                logger_local.info(f'entrada A{indice} : ')
                            break

            except FileNotFoundError:
                # Handle case where parameter file doesn't exist
                pass
            except Exception as e:
                logger_local.error(f'Error verificando cambios en parámetros: {e}')
                logger_local.manual(f'Error verificando cambios en parámetros: {e}')

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
                                    logger_local.manual(f"Error lectura ADS{ADS}")
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
                                    logger_local.manual(f"Error lectura ADS{ADS}")
                                    logger_local.error(f"Error lectura ADS{ADS} en modo diferencial")
                                    time.sleep(0.005)
                                    # Add a default value or skip
                                    L_ADS.append(0)
                                else:
                                    logger_local.error(f"OSError inesperado en lectura diferencial ADS{ADS}: {e}")
                                    raise
                    ee = '30c'
                    if modo != 0:
                        #logger_local.manual(nombre_ADS[ADS],f'-- indice:{indice} - modo={modo}-gain={gain_ADS[ADS][indice]}-rate={rate_ADS[ADS][indice]} - bucles={bucles_ADS[ADS][indice]}')

                        MED_ADS = sum(L_ADS)/bucles_ADS[ADS][indice] if L_ADS else 0
                        d_ads[var_ADS[ADS][indice]] = round(MED_ADS * 0.000125 * res_ADS[ADS][indice] / gain_ADS[ADS][indice] ,3)

                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0

                        if DEBUG >=100:
                             logger_local.debug(f'L_ADS-A{indice}={L_ADS} - {MED_ADS} Err:{ERR_ADS[indice]}- {var_ADS[ADS][indice]} ={d_ads[var_ADS[ADS][indice]]}')

            else: # 'Continuo o continuo diferencial'
                ee = '40'
                L_ADS = ([0.0] * bucles_ADS[ADS][indice])
                for i in range(bucles_ADS[ADS][indice]):
                    try:
                        L_ADS[i] = adc.get_last_result()
                    except OSError as e:
                        if e.errno in (5, 121):  # Expected I2C errors
                            logger_local.manual(f"Error lectura continua ADS{ADS}")
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
                    logger_local.debug(f'L_ADS-A{indice}={L_ADS}-{MED_ADS} Err:{ERR_ADS}- {var_ADS[ADS][indice]}={d_ads[var_ADS[ADS][indice]]}')

            ee = '50'
            t1 = (time.perf_counter() -t0)* 1000

            if DEBUG>=1:
                t = str(round(time.time(),3))
                if ADS == 0:
                    logger_local.debug(Fore.RESET+f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                elif ADS ==1:
                    logger_local.debug(Fore.BLUE+f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                elif ADS ==2:
                    logger_local.debug(Fore.CYAN+f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')
                else:
                    logger_local.debug(Fore.RED+f'{t[-6:]}: {nombre_ADS[ADS]}-Modo={modo_ADS[ADS]} {str(ERR_ADS):16}-Captura = {d_ads}')

            salida = json.dumps(d_ads)
            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Use the DI database manager to save data
            gestor_bd.guardar_datos_equipo_dict(nombre_ADS[ADS], tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 =(time.process_time() - tp0) * 1000

            ee = '70'
            if DEBUG >= 2:
                if ADS_modo == 'Disparado':
                    logger_local.info(f'{time.time():.5f} / {ADS}: t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:{rate_ADS[ADS]} Bucles:{bucles_ADS[ADS]}')
                else: 
                    logger_local.info(f'{time.time():.5f} / {ADS}: t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:{rate_ADS[ADS]} Bucles:{bucles_ADS[ADS]} - {ADS_modo} entrada {indice}')

            ee = '80'
            if DEBUG >=100:
                logger_local.debug(Fore.CYAN+'*' * 80)
                logger_local.debug('*' * 80)

            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra_ADS[ADS]-t3,0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
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

    log_local.info(Fore.RESET+'=' * 50)
    log_local.info(Fore.BLUE+'ADS_activos=')
    for i in ADS_activos:
        log_local.manual(Fore.RED+f' -{nombre_ADS[i]}='+Fore.BLUE+f' direc={direccion_ADS[i]} - var= {var_ADS[i]} - modo={modo_ADS[i]} -',
              f'rate ={rate_ADS[i]} \n        tmuestra={tmuestra_ADS[i]} - bucles={bucles_ADS[i]} - gain={gain_ADS[i]} - ratio={res_ADS[i]}')
    log_local.info(Fore.RESET+'=' * 50)
    time.sleep(5)

    # Arrancando procesos
    for i in ADS_activos:
        log_local.info(f'Iniciando proceso para {nombre_ADS[i]}')
        multiprocessing.Process(target = ADS_captura,args=(i,),name = f'ADS{i}').start()

    Procesos= multiprocessing.active_children() # lista procesos
    log_local.info(f'Procesos activos= {Procesos}')

    # Bucle
    while True:
        try:
            for p in Procesos:
                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    time.sleep(3)
                    i=int(p.name[-1])
                    log_local.info(f'Reiniciando proceso ADS{i}')
                    multiprocessing.Process(target = ADS_captura,args=(i,),name = f'ADS{i}').start()
                    Procesos= multiprocessing.active_children()
                    log_local.info(f'Procesos actualizados: {Procesos}')

            time.sleep(1)

        except KeyboardInterrupt:
            log_local.info('Recibida señal de interrupción')
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_with_new_logger.py.......')
            for p in Procesos:
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()