#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión con cargador limpio de parámetros - Formato ADS como dict

# #################### Control Ejecucion Servicio ########################################
from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'
# ########################################################################################

import time,sys,os
import json
import multiprocessing
import MySQLdb

from smbus import SMBus
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.logger_multiprocessing import LoggerMultiprocessing
from helpers.cargador_parametros import (
    cargar_parametros,
    obtener_todos_ads,
    obtener_ads_activos
)

log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_dict_format.py')


##### Carga de Parámetros - DIST + USER fusionados #####

# Cargar parámetros en el proceso principal (solo una vez)
params = cargar_parametros()

# Obtener configuración ADS en formato lista
todos_ads = obtener_todos_ads(params)
ads_activos = obtener_ads_activos(params)

log_local.info(f"ADS configurados: {len(todos_ads)}")
log_local.info(f"ADS activos: {len(ads_activos)}")

#Comprobacion argumentos en comando
DEBUG = 0
if '-p1' in sys.argv: DEBUG = 1
elif '-p2' in sys.argv: DEBUG = 2
elif '-p' in sys.argv: DEBUG = 100
elif '-p3' in sys.argv: DEBUG = 3

bus = SMBus(1) # Activo Bus I2C para ADS o PCF


def ADS_captura(ads_config, params):
    """Captura datos para un ADS específico"""
    from helpers.logger_multiprocessing import LoggerMultiprocessing
    from helpers.gestor_bd import GestorBD
    
    logger_local = LoggerMultiprocessing(f"{__name__}-{ads_config['id']}")
    
    # Extraer configuración desde ads_config dict
    ads_id = ads_config['id']
    direccion = ads_config['direccion']
    vars_ = ads_config['vars']
    tmuestra = ads_config['tmuestra']
    rate = ads_config['rate']
    bucles = ads_config['bucles']
    gain = ads_config['gain']
    modo = ads_config['modo']
    res = ads_config['res']
    
    # DB params from main params dict
    servidor = params['servidor']
    usuario = params['usuario']
    clave = params['clave']
    basedatos = params['basedatos']
    
    # Find ADS index for legacy code
    ADS_index = ads_config.get('_index', 0)
    
    Ncapturas = 0
    time.sleep(0.02 * ADS_index)

    if DEBUG >= 1:
        print()
        logger_local.info(Fore.BLUE + '=' * 40 + f'Proceso{ADS_index}{ads_id}' + '=' * 40)

    # Database connection
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)
    
    existe = not gestor_bd.insertar_equipo_si_falta(ads_id)
    if not existe:
        logger_local.manual(Fore.RED + f'Registro RAM - clave = {ads_id} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion, busnum=1)

    d_ads = {}
    ADS_modo = 'Disparado'
    PARAMETROS_FV_PATH = "/home/pi/PVControl+/Parametros_FV.py"
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
                    params = cargar_parametros()
                    t_cambio_parametros = current_mtime
                    
                    # Update ADS config from reloaded params
                    todos_ads = obtener_todos_ads(params)
                    for ads in todos_ads:
                        if ads['id'] == ads_id:
                            ads_config = ads
                            break
                    
                    # Refresh local vars
                    direccion = ads_config['direccion']
                    vars_ = ads_config['vars']
                    tmuestra = ads_config['tmuestra']
                    rate = ads_config['rate']
                    bucles = ads_config['bucles']
                    gain = ads_config['gain']
                    modo = ads_config['modo']
                    res = ads_config['res']

                    ee = '20'
                    if DEBUG >= 1:
                        logger_local.info(Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                                    f' -- Leyendo Parametros_FV.py para {ads_id} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    ADS_modo = 'Disparado'

            except FileNotFoundError:
                pass
            except Exception as e:
                logger_local.error(f'Error verificando cambios: {e}')

            ee = 30.2

            if ADS_modo == 'Disparado':
                ee = '30'
                for indice, modo_valor in enumerate(modo, 0):
                    if modo_valor == 1:
                        ee = '30a'
                        L_ADS = []
                        for j in range(bucles[indice]):
                            try:
                                val = adc.read_adc(indice, gain=gain[indice], data_rate=rate[indice])
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):
                                    logger_local.error(f"Error lectura {ads_id}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                else:
                                    raise
                    elif modo_valor == 3:
                        ee = '30b'
                        indice1 = 0 if indice == 0 else 3
                        L_ADS = []
                        for j in range(bucles[indice]):
                            try:
                                val = adc.read_adc_difference(indice1, gain=gain[indice], data_rate=rate[indice])
                                if val is not None:
                                    L_ADS.append(val)
                            except OSError as e:
                                if e.errno in (5, 121):
                                    logger_local.error(f"Error diferencial {ads_id}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                else:
                                    raise
                    else:
                        continue
                    
                    if modo_valor != 0:
                        MED_ADS = sum(L_ADS) / bucles[indice] if L_ADS else 0
                        d_ads[vars_[indice]] = round(MED_ADS * 0.000125 * res[indice] / gain[indice], 3)
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0

            else:  # Continuo
                ee = '40'
                for indice, modo_valor in enumerate(modo, 0):
                    if modo_valor == 0:
                        continue
                    L_ADS = [0.0] * bucles[indice]
                    for i in range(bucles[indice]):
                        try:
                            L_ADS[i] = adc.get_last_result()
                        except OSError as e:
                            if e.errno in (5, 121):
                                logger_local.error(f"Error continua {ads_id}")
                                time.sleep(0.005)
                                L_ADS[i] = 0
                            else:
                                raise
                        time.sleep(1 / rate[indice])

                    MED_ADS = sum(L_ADS) / bucles[indice]
                    d_ads[vars_[indice]] = round(MED_ADS * 0.000125 * res[indice] / gain[indice], 3)
                    ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            ee = '50'
            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                logger_local.debug(f'{t[-6:]}: {ads_id}-Modo={modo} {str(ERR_ADS):16}-Captura = {d_ads}')

            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            gestor_bd.guardar_datos_equipo_dict(ads_id, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            ee = '70'

            if DEBUG >= 2:
                logger_local.info(f'{time.time():.5f} / {ads_id}: t1={t1:6.1f}-t2={t2:6.1f}')

            # Timing
            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra - t3, 0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_local.error(f"{tiempo} - Error {ee} en {ads_id}: {e}")
            import traceback
            logger_local.error(f"Traza: {traceback.format_exc()}")
            sys.exit(1)


if __name__ == '__main__':
    # Control execution service
    controlar_servicio(servicio, len(ads_activos) > 0)

    log_local.info(Fore.RESET + '=' * 50)
    log_local.info(Fore.BLUE + 'ADS_activos=')
    for ads in ads_activos:
        log_local.manual(Fore.RED + f' -{ads["id"]}=' + Fore.BLUE +
                    f' direc={ads["direccion"]} - var= {ads["vars"]} - modo={ads["modo"]}')
    log_local.info(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Start processes - pass ads_config dict and full params to each
    procesos = []
    for idx, ads in enumerate(ads_activos):
        ads['_index'] = idx  # Add index for legacy code
        p = multiprocessing.Process(target=ADS_captura, args=(ads, params), name=f'ADS{ads["id"]}')
        p.start()
        procesos.append(p)
        log_local.info(f'Iniciado proceso {p.name}')

    log_local.info(f'Procesos activos= {multiprocessing.active_children()}')

    # Monitor loop
    while True:
        try:
            for p in procesos:
                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    time.sleep(3)
                    # Find ADS config for this process
                    ads_id = p.name.replace('ADS', '')
                    for ads in ads_activos:
                        if ads['id'] == ads_id:
                            ads['_index'] = procesos.index(p)
                            nuevo_p = multiprocessing.Process(target=ADS_captura, args=(ads, params), name=f'ADS{ads_id}')
                            nuevo_p.start()
                            procesos[procesos.index(p)] = nuevo_p
                            log_local.info(f'Reiniciado proceso {nuevo_p.name}')
                            break

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_dict_format.py.......')
            for p in procesos:
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
