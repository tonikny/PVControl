#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión con formato ADS como dict - Basado en fv_ads_cargador_limpio.py que funciona

from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'

import time, sys, os, json, multiprocessing, MySQLdb
from smbus import SMBus
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.logger_multiprocessing import LoggerMultiprocessing
from helpers.cargador_parametros import cargar_parametros, convertir_dict_a_lista

# Logger FIRST - before any other initialization
log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_import.py')

PARAMETROS_FV_PATH = "/home/pi/PVControl+/Parametros_FV.py"

# Load params using cargador_parametros (uses importlib, not exec)
params_dict = cargar_parametros()

# Get ADS as list
lista_ads = convertir_dict_a_lista(params_dict.get('ADS', {}))
lista_ads = [ads for ads in lista_ads if ads.get('usar') in [True, 1]]

log_local.info(f"ADS configurados: {len(params_dict.get('ADS', {}))}")
log_local.info(f"ADS activos: {len(lista_ads)}")

DEBUG = 0
if '-p1' in sys.argv: DEBUG = 1
elif '-p2' in sys.argv: DEBUG = 2
elif '-p' in sys.argv: DEBUG = 100
elif '-p3' in sys.argv: DEBUG = 3


def ADS_captura(ADS_index, params_dict):
    """Captura datos para un ADS específico"""
    from helpers.logger_multiprocessing import LoggerMultiprocessing
    from helpers.gestor_bd import GestorBD
    from helpers.cargador_parametros import cargar_parametros, convertir_dict_a_lista

    logger_local = LoggerMultiprocessing(f"{__name__}-ADS{ADS_index}")

    # Extraer configuración inicial desde params dict
    nombre_ADS_local = params_dict['nombre_ADS'][ADS_index]
    direccion_ADS = params_dict['direccion_ADS'][ADS_index]
    var_ADS = params_dict['var_ADS'][ADS_index]
    tmuestra_ADS = params_dict['tmuestra_ADS'][ADS_index]
    rate_ADS = params_dict['rate_ADS'][ADS_index]
    bucles_ADS = params_dict['bucles_ADS'][ADS_index]
    gain_ADS = params_dict['gain_ADS'][ADS_index]
    modo_ADS = params_dict['modo_ADS'][ADS_index]
    res_ADS = params_dict['res_ADS'][ADS_index]
    servidor = params_dict['servidor']
    usuario = params_dict['usuario']
    clave = params_dict['clave']
    basedatos = params_dict['basedatos']

    Ncapturas = 0
    time.sleep(0.02 * ADS_index)

    if DEBUG >= 1:
        print()
        logger_local.info(Fore.BLUE + '=' * 40 + f'Proceso{ADS_index}{nombre_ADS_local}' + '=' * 40)

    print(f'Capturando ADS {nombre_ADS_local}...')
    sys.stdout.flush()

    # Database connection
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)

    existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS_local)
    if not existe:
        logger_local.manual(Fore.RED + f'Registro RAM - clave = {nombre_ADS_local} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion_ADS}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS, busnum=1)

    d_ads = {}
    ADS_modo = 'Disparado'
    t_cambio_parametros = os.path.getmtime(PARAMETROS_FV_PATH) - 100

    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            ERR_ADS = [0, 0, 0, 0]

            # Check for parameter changes and reload
            try:
                current_mtime = os.path.getmtime(PARAMETROS_FV_PATH)
                if current_mtime != t_cambio_parametros:
                    # Reload parameters
                    params_dict = cargar_parametros()
                    t_cambio_parametros = current_mtime
                    
                    # Update local config
                    nombre_ADS_local = params_dict['nombre_ADS'][ADS_index]
                    direccion_ADS = params_dict['direccion_ADS'][ADS_index]
                    var_ADS = params_dict['var_ADS'][ADS_index]
                    tmuestra_ADS = params_dict['tmuestra_ADS'][ADS_index]
                    rate_ADS = params_dict['rate_ADS'][ADS_index]
                    bucles_ADS = params_dict['bucles_ADS'][ADS_index]
                    gain_ADS = params_dict['gain_ADS'][ADS_index]
                    modo_ADS = params_dict['modo_ADS'][ADS_index]
                    res_ADS = params_dict['res_ADS'][ADS_index]
                    
                    ee = '20'
                    if DEBUG >= 1:
                        logger_local.info(Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                                    f' -- Leyendo Parametros_FV.py para {nombre_ADS_local} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    ADS_modo = 'Disparado'
            except FileNotFoundError:
                pass
            except Exception as e:
                logger_local.error(f'Error recargando parámetros: {e}')

            ee = '11'

            if ADS_modo == 'Disparado':
                for indice, modo_valor in enumerate(modo_ADS, 0):
                    if modo_valor == 1:
                        L_ADS = []
                        for j in range(bucles_ADS[indice]):
                            val = adc.read_adc(indice, gain=gain_ADS[indice], data_rate=rate_ADS[indice])
                            L_ADS.append(val)
                    elif modo_valor == 3:
                        indice1 = 0 if indice == 0 else 3
                        L_ADS = []
                        for j in range(bucles_ADS[indice]):
                            val = adc.read_adc_difference(indice1, gain=gain_ADS[indice], data_rate=rate_ADS[indice])
                            L_ADS.append(val)
                    else:
                        continue

                    if modo_valor != 0:
                        MED_ADS = sum(L_ADS) / bucles_ADS[indice] if L_ADS else 0
                        d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0
            else:  # Continuo
                for indice, modo_valor in enumerate(modo_ADS, 0):
                    if modo_valor == 0:
                        continue
                    L_ADS = [adc.get_last_result() for _ in range(bucles_ADS[indice])]
                    time.sleep(bucles_ADS[indice] / rate_ADS[indice])

                    MED_ADS = sum(L_ADS) / bucles_ADS[indice]
                    d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                    ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                logger_local.debug(f'{t[-6:]}: {nombre_ADS_local}-Modo={modo_ADS} {str(ERR_ADS):16}-Captura = {d_ads}')

            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            gestor_bd.guardar_datos_equipo_dict(nombre_ADS_local, tiempo, d_ads)

            if DEBUG >= 2:
                logger_local.info(f'{time.time():.5f} / {nombre_ADS_local}: t1={t1:6.1f}')

            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra_ADS - t3, 0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_local.error(f"{tiempo} - Error en {nombre_ADS_local}: {e}")
            import traceback
            logger_local.error(f"Traza: {traceback.format_exc()}")
            sys.exit(1)


if __name__ == '__main__':
    # Control execution service
    controlar_servicio(servicio, len(lista_ads) > 0)

    log_local.info(Fore.RESET + '=' * 50)
    log_local.info(Fore.BLUE + 'ADS_activos=')
    for ads in lista_ads:
        log_local.manual(Fore.RED + f' -{ads["id"]}=' + Fore.BLUE +
                    f' direc={ads["direccion"]} - var= {ads["vars"]} - modo={ads["modo"]}')
    log_local.info(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Use 'spawn' instead of 'fork' to avoid I2C state inheritance issues
    multiprocessing.set_start_method('spawn', force=True)

    # Start processes - pass ADS index and full params_dict
    procesos = []
    for idx, ads in enumerate(lista_ads):
        p = multiprocessing.Process(target=ADS_captura, args=(idx, params_dict), name=f'p_{ads["id"]}')
        p.start()
        procesos.append(p)
        log_local.info(f'Iniciado proceso {p.name}')

    log_local.info(f'Procesos activos= {multiprocessing.active_children()}')

    # Monitor loop
    while True:
        try:
            for p in procesos:
                if DEBUG >= 1:
                    log_local.info(f'Proceso {p} vivo {p.name}')

                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    time.sleep(3)

                    ads_id = p.name.replace('p_', '')
                    for idx, ads in enumerate(lista_ads):
                        if ads['id'] == ads_id:
                            nuevo_p = multiprocessing.Process(
                                target=ADS_captura,
                                args=(idx, params_dict),
                                name=f'p_{ads_id}'
                            )
                            nuevo_p.start()
                            procesos[procesos.index(p)] = nuevo_p
                            log_local.info(f'Reiniciado proceso {nuevo_p.name}')
                            break

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_import.py.......')
            for p in procesos:
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
