#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión con formato ADS como dict - Copia exacta de fv_ads_cargador_limpio.py

from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'

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
from helpers.cargador_parametros import cargar_parametros, obtener_ads_activos

log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_import.py')

# Cargar parámetros en el proceso principal (solo una vez)
params = cargar_parametros()

# Convertir ADS dict a formato lista para compatibilidad
def convertir_dict_a_lista(equipo):
    return [{"id": key, **value} for key, value in equipo.items()]

ADS_dict = params.get('ADS', {})
lista_ads = [ads for ads in convertir_dict_a_lista(ADS_dict) if ads.get('usar') in [True, 1]]

# Extraer variables en formato lista para compatibilidad con el código existente
usar_ADS = [1] * len(lista_ads)  # Todos activos ya que filtramos
nombre_ADS = [ads['id'] for ads in lista_ads]
direccion_ADS = [ads['direccion'] for ads in lista_ads]
var_ADS = [ads['vars'] for ads in lista_ads]
tmuestra_ADS = [ads['tmuestra'] for ads in lista_ads]
rate_ADS = [ads['rate'] for ads in lista_ads]
bucles_ADS = [ads['bucles'] for ads in lista_ads]
gain_ADS = [ads['gain'] for ads in lista_ads]
modo_ADS = [ads['modo'] for ads in lista_ads]
res_ADS = [ads['res'] for ads in lista_ads]

# Create filtered params dict with only active ADS (reindexed from 0)
params_filtered = {
    'nombre_ADS': nombre_ADS,
    'direccion_ADS': direccion_ADS,
    'var_ADS': var_ADS,
    'tmuestra_ADS': tmuestra_ADS,
    'rate_ADS': rate_ADS,
    'bucles_ADS': bucles_ADS,
    'gain_ADS': gain_ADS,
    'modo_ADS': modo_ADS,
    'res_ADS': res_ADS,
    'servidor': params['servidor'],
    'usuario': params['usuario'],
    'clave': params['clave'],
    'basedatos': params['basedatos']
}

log_local.info(f"ADS configurados: {len(ADS_dict)}")
log_local.info(f"ADS activos: {len(lista_ads)}")

#Comprobacion argumentos en comando
DEBUG = 0
if '-p1' in sys.argv: DEBUG = 1
elif '-p2' in sys.argv: DEBUG = 2
elif '-p' in sys.argv: DEBUG = 100
elif '-p3' in sys.argv: DEBUG = 3

bus = SMBus(1) # Activo Bus I2C para ADS o PCF


def ADS_captura(ADS_index, params, ads_name):
    """Captura datos para un ADS específico"""
    from helpers.logger_multiprocessing import LoggerMultiprocessing
    from helpers.gestor_bd import GestorBD
    from helpers.cargador_parametros import cargar_parametros, obtener_ads_activos

    logger_local = LoggerMultiprocessing(f"{__name__}-{ads_name}")

    # Get active ADS list from params
    ads_activos = obtener_ads_activos(params)
    
    # Find this ADS by name (not by index) to handle config changes
    ads_config = None
    for ads in ads_activos:
        if ads['id'] == ads_name:
            ads_config = ads
            break
    
    if ads_config is None:
        logger_local.error(f"ADS {ads_name} no encontrado en la configuración activa")
        sys.exit(1)
    
    # Extraer configuración para este ADS
    nombre_ADS_local = ads_config['id']
    direccion_ADS = ads_config['direccion']
    var_ADS = ads_config['vars']
    tmuestra_ADS = ads_config['tmuestra']
    rate_ADS = ads_config['rate']
    bucles_ADS = ads_config['bucles']
    gain_ADS = ads_config['gain']
    modo_ADS = ads_config['modo']
    res_ADS = ads_config['res']
    servidor = params['servidor']
    usuario = params['usuario']
    clave = params['clave']
    basedatos = params['basedatos']

    Ncapturas = 0
    time.sleep(0.02 * ADS_index)

    if DEBUG >= 1:
        print()
        logger_local.info(Fore.BLUE + '=' * 40 + f'Proceso{ADS_index}{nombre_ADS_local}' + '=' * 40)

    # Database connection
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)

    existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS_local)
    if not existe:
        logger_local.manual(Fore.RED + f'Registro RAM - clave = {nombre_ADS_local} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion_ADS}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS, busnum=1)

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
            ERR_ADS = [0, 0, 0, 0]
            ee = '11'

            # Check for parameter changes
            try:
                current_mtime = os.path.getmtime(PARAMETROS_FV_PATH)
                if current_mtime != t_cambio_parametros:
                    # Reload parameters
                    params = cargar_parametros()
                    t_cambio_parametros = current_mtime
                    
                    # Get active ADS and find this one by name
                    ads_activos = obtener_ads_activos(params)
                    ads_config = None
                    for ads in ads_activos:
                        if ads['id'] == ads_name:
                            ads_config = ads
                            break
                    
                    if ads_config:
                        nombre_ADS_local = ads_config['id']
                        direccion_ADS = ads_config['direccion']
                        var_ADS = ads_config['vars']
                        tmuestra_ADS = ads_config['tmuestra']
                        rate_ADS = ads_config['rate']
                        bucles_ADS = ads_config['bucles']
                        gain_ADS = ads_config['gain']
                        modo_ADS = ads_config['modo']
                        res_ADS = ads_config['res']

                        ee = '20'
                        if DEBUG >= 1:
                            logger_local.info(Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                                        f' -- Leyendo Parametros_FV.py para {nombre_ADS_local} - Capturas={Ncapturas}')
                        Ncapturas = 0
                        ADS_modo = 'Disparado'
                    else:
                        logger_local.warning(f"ADS {ads_name} desactivado o no encontrado. Terminando proceso.")
                        sys.exit(0)

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
                logger_local.info(f'{time.time():.5f} / {ads_name}: t1={t1:6.1f}-t2={t2:6.1f}')

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
    hay_ads_activos = len(lista_ads)
    controlar_servicio(servicio, hay_ads_activos > 0)

    log_local.info(Fore.RESET + '=' * 50)
    log_local.info(Fore.BLUE + 'ADS_activos=')
    for i in range(len(lista_ads)):
        log_local.manual(Fore.RED + f' -{nombre_ADS[i]}=' + Fore.BLUE +
                    f' direc={direccion_ADS[i]} - var= {var_ADS[i]}')
    log_local.info(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Start processes - pass ADS index, params dict, and ADS name
    procesos_nombres = set()  # Track active process names
    for i in range(len(lista_ads)):
        ads_name = nombre_ADS[i]
        multiprocessing.Process(target=ADS_captura, args=(i, params, ads_name), name=f'p_{ads_name}').start()
        procesos_nombres.add(ads_name)

    Procesos = multiprocessing.active_children()
    log_local.info(f'Procesos activos= {Procesos}')

    # Monitor loop
    while True:
        try:
            # Always reload params first to get current active ADS
            params = cargar_parametros()
            lista_ads = obtener_ads_activos(params)
            
            # Start processes for newly active ADS
            for i, ads in enumerate(lista_ads):
                ads_name = ads['id']
                if ads_name not in procesos_nombres:
                    log_local.info(f'Iniciando nuevo proceso para {ads_name}')
                    p = multiprocessing.Process(target=ADS_captura, args=(i, params, ads_name), name=f'p_{ads_name}')
                    p.start()
                    procesos_nombres.add(ads_name)
            
            # Check for dead processes and restart them (only if still active)
            for p in list(Procesos):
                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    ads_name = p.name.replace('p_', '')
                    procesos_nombres.discard(ads_name)
                    
                    # Only restart if ADS is still active
                    if ads_name in [ads['id'] for ads in lista_ads]:
                        time.sleep(3)
                        # Find ADS index
                        for idx, ads in enumerate(lista_ads):
                            if ads['id'] == ads_name:
                                nuevo_p = multiprocessing.Process(target=ADS_captura, args=(idx, params, ads_name), name=f'p_{ads_name}')
                                nuevo_p.start()
                                procesos_nombres.add(ads_name)
                                log_local.info(f'Reiniciado proceso {nuevo_p.name}')
                                break
                    else:
                        log_local.info(f'ADS {ads_name} desactivado, no se reinicia')
            
            Procesos = multiprocessing.active_children()
            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_import.py.......')
            for p in Procesos:
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
