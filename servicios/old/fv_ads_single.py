#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión para systemd - Un proceso por dispositivo ADS
# Se ejecuta como: python3 fv_ads_single.py ADS1  o  python3 fv_ads_single.py ADS4

import time,sys,os
import json
import MySQLdb
from smbus import SMBus
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.logger_multiprocessing import LoggerMultiprocessing

# Get ADS name from command line
if len(sys.argv) < 2:
    print("Uso: python3 fv_ads_single.py <ADS_NAME>")
    print("Ejemplo: python3 fv_ads_single.py ADS1")
    sys.exit(1)

ADS_NAME = sys.argv[1].upper()  # ADS1 or ADS4

# Initialize logger
log_local = LoggerMultiprocessing(nombre=f"fv_ads_{ADS_NAME}")
log_local.info(Style.BRIGHT + Fore.YELLOW + f'Arrancando {ADS_NAME}')

# Load parameters
parametros_FV = "/home/pi/PVControl+/Parametros_FV.py"
exec(open(parametros_FV).read(), globals())

# Find the index for this ADS
try:
    ADS_index = nombre_ADS.index(ADS_NAME)
except ValueError:
    log_local.error(f"{ADS_NAME} no encontrado en la configuración")
    sys.exit(1)

# Extract configuration for this ADS
direccion = direccion_ADS[ADS_index]
var = var_ADS[ADS_index]
tmuestra = tmuestra_ADS[ADS_index]
rate = rate_ADS[ADS_index]
bucles = bucles_ADS[ADS_index]
gain = gain_ADS[ADS_index]
modo = modo_ADS[ADS_index]
res = res_ADS[ADS_index]

DEBUG = 0
if '-p' in sys.argv: DEBUG = 100
elif '-p2' in sys.argv: DEBUG = 2
elif '-p1' in sys.argv: DEBUG = 1

bus = SMBus(1)

def ADS_captura():
    """Captura datos para un único ADS"""
    from helpers.gestor_bd import GestorBD
    
    logger_local = LoggerMultiprocessing(f"{__name__}-{ADS_NAME}")
    gestor_bd = GestorBD(servidor=servidor, usuario=usuario, clave=clave, basedatos=basedatos)
    
    Ncapturas = 0
    
    # Register in database
    existe = not gestor_bd.insertar_equipo_si_falta(ADS_NAME)
    if not existe:
        logger_local.manual(Fore.RED + f'Registro RAM - clave = {ADS_NAME} ya creado')

    logger_local.manual(f'Activando ADS en direccion {direccion}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion, busnum=1)

    d_ads = {}
    ADS_modo = 'Disparado'
    t_cambio_parametros = os.path.getmtime(parametros_FV) - 100

    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            tp0 = time.process_time()
            ERR_ADS = [0,0,0,0]
            ee = '11'

            # Check for parameter changes
            try:
                if os.path.getmtime(parametros_FV) != t_cambio_parametros:
                    exec(open(parametros_FV).read(), globals())
                    t_cambio_parametros = os.path.getmtime(parametros_FV)
                    
                    # Reload configuration for this ADS
                    ADS_index = nombre_ADS.index(ADS_NAME)
                    direccion = direccion_ADS[ADS_index]
                    var = var_ADS[ADS_index]
                    tmuestra = tmuestra_ADS[ADS_index]
                    rate = rate_ADS[ADS_index]
                    bucles = bucles_ADS[ADS_index]
                    gain = gain_ADS[ADS_index]
                    modo = modo_ADS[ADS_index]
                    res = res_ADS[ADS_index]

                    ee = '20'
                    if DEBUG >= 1:
                        logger_local.info(Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                                    f' -- Leyendo Parametros_FV.py para {ADS_NAME} - Capturas={Ncapturas}')
                    Ncapturas = 0
                    ADS_modo = 'Disparado'
                    
                    if DEBUG >= 1:
                        logger_local.info(Fore.BLUE + f'Modo {ADS_NAME} = ' + Fore.GREEN)

                    for indice, modo_valor in enumerate(modo, 0):
                        ee = '20b'
                        if modo_valor == 2:
                            adc.start_adc(indice, gain=gain[indice], data_rate=rate[indice])
                            ADS_modo = 'Continuo'
                            if DEBUG >= 1:
                                logger_local.info(f'entrada A{indice} : ')
                            break
                        elif modo_valor == 4:
                            indice1 = 0 if indice == 0 else 3
                            adc.start_adc_difference(indice1, gain=gain[indice], data_rate=rate[indice])
                            ADS_modo = 'Continuo_Diferencial'
                            if DEBUG >= 1:
                                logger_local.info(f'entrada A{indice} : ')
                            break

            except FileNotFoundError:
                pass
            except Exception as e:
                logger_local.error(f'Error verificando cambios en parámetros: {e}')

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
                                    logger_local.error(f"Error lectura {ADS_NAME}")
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
                                    logger_local.error(f"Error lectura diferencial {ADS_NAME}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                else:
                                    raise
                    else:
                        continue
                    
                    ee = '30c'
                    if modo_valor != 0:
                        MED_ADS = sum(L_ADS)/bucles[indice] if L_ADS else 0
                        d_ads[var[indice]] = round(MED_ADS * 0.000125 * res[indice] / gain[indice], 3)
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS) if L_ADS else 0

                        if DEBUG >= 100:
                            logger_local.debug(f'L_ADS-A{indice}={L_ADS} - {MED_ADS} Err:{ERR_ADS[indice]}- {var[indice]} ={d_ads[var[indice]]}')

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
                                logger_local.error(f"Error lectura continua {ADS_NAME}")
                                time.sleep(0.005)
                                L_ADS[i] = 0
                            else:
                                raise
                        time.sleep(1/rate[indice])

                    MED_ADS = sum(L_ADS)/bucles[indice]
                    d_ads[var[indice]] = round(MED_ADS * 0.000125 * res[indice] / gain[indice], 3)
                    ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            ee = '50'
            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                logger_local.debug(f'{t[-6:]}: {ADS_NAME}-Modo={modo} {str(ERR_ADS):16}-Captura = {d_ads}')

            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            gestor_bd.guardar_datos_equipo_dict(ADS_NAME, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 = (time.process_time() - tp0) * 1000

            ee = '70'
            if DEBUG >= 2:
                logger_local.info(f'{time.time():.5f} / {ADS_NAME}: t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f}')

            # Timing
            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra - t3, 0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_local.error(f"{tiempo} - Error {ee} en {ADS_NAME}: {e}")
            import traceback
            logger_local.error(f"Traza: {traceback.format_exc()}")
            sys.exit(1)

if __name__ == '__main__':
    log_local.info(f"Iniciando captura para {ADS_NAME}")
    ADS_captura()
