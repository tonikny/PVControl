#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión con cargador limpio de parámetros (DIST + USER)

# #################### Control Ejecucion Servicio ########################################
from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'
# ########################################################################################

import time
import sys
import os
import json
import multiprocessing
import MySQLdb

from smbus import SMBus
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.logger_multiprocessing import LoggerMultiprocessing
from helpers.cargador_parametros import cargar_parametros

log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_cargador_limpio.py')


##### Carga de Parámetros - DIST + USER fusionados #####

# Cargar parámetros en el proceso principal (solo una vez)
params = cargar_parametros()

# Extraer variables necesarias para el main process
usar_ADS = params['usar_ADS']
nombre_ADS = params['nombre_ADS']

#Comprobacion argumentos en comando
DEBUG = 0
if '-p1' in sys.argv: DEBUG = 1
elif '-p2' in sys.argv: DEBUG = 2
elif '-p' in sys.argv: DEBUG = 100
elif '-p3' in sys.argv: DEBUG = 3

bus = SMBus(1) # Activo Bus I2C para ADS o PCF


def ADS_captura(ADS, params):
    """Captura datos para un ADS específico"""
    from helpers.logger_multiprocessing import LoggerMultiprocessing
    from helpers.gestor_bd import GestorBD
    
    logger_local = LoggerMultiprocessing(f"{__name__}-ADS{ADS}")
    
    # Extraer configuración para este ADS desde params dict
    nombre_ADS_local = params['nombre_ADS'][ADS]
    direccion_ADS = params['direccion_ADS'][ADS]
    var_ADS = params['var_ADS'][ADS]
    tmuestra_ADS = params['tmuestra_ADS'][ADS]
    rate_ADS = params['rate_ADS'][ADS]
    bucles_ADS = params['bucles_ADS'][ADS]
    gain_ADS = params['gain_ADS'][ADS]
    modo_ADS = params['modo_ADS'][ADS]
    res_ADS = params['res_ADS'][ADS]
    servidor = params['servidor']
    usuario = params['usuario']
    clave = params['clave']
    basedatos = params['basedatos']
    
    Ncapturas = 0
    time.sleep(0.02 * ADS)

    if DEBUG >= 1:
        print()
        logger_local.info(Fore.BLUE + '=' * 40 + f'Proceso{ADS}{nombre_ADS_local}' + '=' * 40)

    # Database connection
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)
    
    existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS_local)
    if not existe:
        logger_local.manual(Fore.RED + f'Registro RAM - clave = {nombre_ADS_local} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion_ADS}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS, busnum=1)

    d_ads = {}
    ADS_modo = 'Disparado'
    PARAMETROS_FV_PATH = params.get('_ruta_parametros', '/home/pi/PVControl+/Parametros_FV.py')
    t_cambio_parametros = os.path.getmtime(PARAMETROS_FV_PATH) - 100

    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            ERR_ADS = [0, 0, 0, 0]
            ee = '11'

            # Check for parameter changes
            try:
                current_mtime = os.path.getmtime(PARAMETROS_FV_PATH)
                if current_mtime != t_cambio_parametros:
                    # Reload parameters
                    from helpers.cargador_parametros import cargar_parametros
                    params = cargar_parametros()
                    t_cambio_parametros = current_mtime
                    
                    # Update local config
                    nombre_ADS_local = params['nombre_ADS'][ADS]
                    direccion_ADS = params['direccion_ADS'][ADS]
                    var_ADS = params['var_ADS'][ADS]
                    tmuestra_ADS = params['tmuestra_ADS'][ADS]
                    rate_ADS = params['rate_ADS'][ADS]
                    bucles_ADS = params['bucles_ADS'][ADS]
                    gain_ADS = params['gain_ADS'][ADS]
                    modo_ADS = params['modo_ADS'][ADS]
                    res_ADS = params['res_ADS'][ADS]

                    ee = '20'
                    if DEBUG >= 1:
                        logger_local.info(Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                                    f' -- Leyendo Parametros_FV.py para {nombre_ADS_local} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    ADS_modo = 'Disparado'

            except FileNotFoundError:
                pass
            except Exception as e:
                logger_local.error(f'Error verificando cambios: {e}')

            ee = 30.2

            if ADS_modo == 'Disparado':
                ee = '30'
                for indice, modo in enumerate(modo_ADS, 0):
                    if modo == 1:
                        ee = '30a'
                        L_ADS = []
                        for j in range(bucles_ADS[indice]):
                            try:
                                val = adc.read_adc(indice, gain=gain_ADS[indice], data_rate=rate_ADS[indice])
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):
                                    logger_local.error(f"Error lectura {nombre_ADS_local}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                else:
                                    raise
                    elif modo == 3:
                        ee = '30b'
                        indice1 = 0 if indice == 0 else 3
                        L_ADS = []
                        for j in range(bucles_ADS[indice]):
                            try:
                                val = adc.read_adc_difference(indice1, gain=gain_ADS[indice], data_rate=rate_ADS[indice])
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):
                                    logger_local.error(f"Error diferencial {nombre_ADS_local}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                else:
                                    raise
                    else:
                        continue
                    
                    if modo != 0:
                        MED_ADS = sum(L_ADS) / bucles_ADS[indice] if L_ADS else 0
                        d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0

            else:  # Continuo
                ee = '40'
                for indice, modo in enumerate(modo_ADS, 0):
                    if modo == 0:
                        continue
                    L_ADS = [0.0] * bucles_ADS[indice]
                    for i in range(bucles_ADS[indice]):
                        try:
                            L_ADS[i] = adc.get_last_result()
                        except OSError as e:
                            if e.errno in (5, 121):
                                logger_local.error(f"Error continua {nombre_ADS_local}")
                                time.sleep(0.005)
                                L_ADS[i] = 0
                            else:
                                raise
                        time.sleep(1 / rate_ADS[indice])

                    MED_ADS = sum(L_ADS) / bucles_ADS[indice]
                    d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                    ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            ee = '50'
            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                logger_local.debug(f'{t[-6:]}: {nombre_ADS_local}-Modo={modo_ADS} {str(ERR_ADS):16}-Captura = {d_ads}')

            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            gestor_bd.guardar_datos_equipo_dict(nombre_ADS_local, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            ee = '70'

            if DEBUG >= 2:
                logger_local.info(f'{time.time():.5f} / {ADS}: t1={t1:6.1f}-t2={t2:6.1f}')

            # Timing
            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra_ADS - t3, 0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_local.error(f"{tiempo} - Error {ee} en {nombre_ADS_local}: {e}")
            import traceback
            logger_local.error(f"Traza: {traceback.format_exc()}")
            sys.exit(1)


if __name__ == '__main__':
    # Control execution service
    hay_ads_activos = sum(usar_ADS)
    controlar_servicio(servicio, hay_ads_activos)

    if '-ADS1' in sys.argv:
        usar_ADS = [1, 0]
    elif '-ADS4' in sys.argv:
        usar_ADS = [0, 1]

    ADS_activos = [i for i in range(len(usar_ADS)) if usar_ADS[i] == 1]

    log_local.info(Fore.RESET + '=' * 50)
    log_local.info(Fore.BLUE + 'ADS_activos=')
    for i in ADS_activos:
        log_local.manual(Fore.RED + f' -{nombre_ADS[i]}=' + Fore.BLUE +
                    f' direc={params["direccion_ADS"][i]} - var= {params["var_ADS"][i]}')
    log_local.info(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Start processes - pass params dict to each
    for i in ADS_activos:
        multiprocessing.Process(target=ADS_captura, args=(i, params), name=f'ADS{i}').start()

    Procesos = multiprocessing.active_children()
    log_local.info(f'Procesos activos= {Procesos}')

    # Monitor loop
    while True:
        try:
            for p in Procesos:
                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    time.sleep(3)
                    i = int(p.name[-1])
                    multiprocessing.Process(target=ADS_captura, args=(i, params), name=f'ADS{i}').start()
                    Procesos = multiprocessing.active_children()
                    log_local.info(f'Procesos actualizados: {Procesos}')

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_cargador_limpio.py.......')
            for p in Procesos:
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
