#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión con formato ADS como dict - Solución híbrida para máxima fiabilidad
# Combina: pre-carga de imports, reintentos con confirmación, y health check

from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'

# =============================================================================
# PRE-CARGA DE TODOS LOS IMPORTS (ANTES DE CUALQUIER FORK)
# Esto evita problemas de importación durante el fork
# =============================================================================
import time, sys, os, json, multiprocessing, MySQLdb
from smbus import SMBus
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.logger_multiprocessing import LoggerMultiprocessing
from helpers.cargador_parametros import cargar_parametros, obtener_ads_activos

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
MAX_STARTUP_RETRIES = 5          # Máximo número de reintentos al iniciar
HEALTH_CHECK_TIMEOUT = 10        # Segundos sin datos antes de reiniciar
I2C_STARTUP_DELAY = 3            # Segundos para inicializar I2C
I2C_BETWEEN_DELAY = 2            # Segundos entre inicio de procesos

log_local = LoggerMultiprocessing(nombre=__name__)
log_local.info(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_import.py')

# Cargar parámetros iniciales
params = cargar_parametros()
lista_ads = obtener_ads_activos(params)

log_local.info(f"ADS configurados: {len(params.get('ADS', {}))}")
log_local.info(f"ADS activos: {len(lista_ads)}")

DEBUG = 0
if '-p1' in sys.argv: DEBUG = 1
elif '-p2' in sys.argv: DEBUG = 2
elif '-p' in sys.argv: DEBUG = 100
elif '-p3' in sys.argv: DEBUG = 3


def ADS_captura(ADS_index, ads_params, ads_name, ads_config, startup_pipe=None, heartbeat_dict=None):
    """
    Captura datos para un ADS específico - SIN recarga interna

    Args:
        ADS_index: Índice del ADS
        ads_params: Parámetros de conexión a BD
        ads_name: Nombre del ADS (ej: 'ADS4')
        ads_config: Configuración completa del ADS
        startup_pipe: Pipe para confirmar inicio exitoso
        heartbeat_dict: Dict compartido para health check
    """
    import sys

    # 1. Initialize logger FIRST (before any pipe operations)
    # Esto evita problemas con la cola de logging después del fork
    try:
        logger_local = LoggerMultiprocessing(f"{__name__}-{ads_name}")
        logger_local.info(f'[{ads_name}] Subproceso iniciando...')
    except Exception as e:
        print(f'[ERROR {ads_name}] Failed to initialize logger: {e}', flush=True)
        # Fallback to basic logging
        logger_local = None

    # 2. Signal successful startup BEFORE any hardware initialization
    if startup_pipe:
        try:
            startup_pipe[1].send(True)
            startup_pipe[1].close()
            print(f'[INFO {ads_name}] Startup confirmed', flush=True)
            if logger_local:
                logger_local.info(f'[{ads_name}] Startup confirmado enviado')
        except Exception as e:
            print(f'[ERROR {ads_name}] Failed to send startup: {e}', flush=True)
            if logger_local:
                logger_local.error(f'[{ads_name}] Error enviando startup confirmation: {e}')

    # 3. Print startup message
    msg = f'### {ads_name} STARTING ###'
    print(msg, flush=True)
    print(msg, file=sys.stderr, flush=True)

    try:
        if logger_local:
            logger_local.info(f'Iniciando captura para {ads_name}')
        
        from helpers.gestor_bd import GestorBD

        # Extraer configuración
        nombre_ADS_local = ads_config['id']
        direccion_ADS = ads_config['direccion']
        var_ADS = ads_config['vars']
        tmuestra_ADS = ads_config['tmuestra']
        rate_ADS = ads_config['rate']
        bucles_ADS = ads_config['bucles']
        gain_ADS = ads_config['gain']
        modo_ADS = ads_config['modo']
        res_ADS = ads_config['res']
        servidor = ads_params['servidor']
        usuario = ads_params['usuario']
        clave = ads_params['clave']
        basedatos = ads_params['basedatos']

        Ncapturas = 0
        time.sleep(0.02 * ADS_index)

        if DEBUG >= 1:
            print()
            logger_local.info(Fore.BLUE + '=' * 40 + f'Proceso{ADS_index}{nombre_ADS_local}' + '=' * 40)

        # Database connection
        gestor_bd = GestorBD()

        existe = not gestor_bd.insertar_equipo_si_falta(nombre_ADS_local)
        if not existe:
            logger_local.manual(Fore.RED + f'Registro RAM - clave = {nombre_ADS_local} ya creado')

        logger_local.manual(f'Activando ADS en direccion {direccion_ADS}')
        
        # Initialize ADC with error handling
        try:
            adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS, busnum=1)
            logger_local.info(f'ADS en direccion {direccion_ADS} inicializado correctamente')
        except Exception as e:
            logger_local.error(f'Error FATAL inicializando ADS en direccion {direccion_ADS}: {e}')
            import traceback
            logger_local.error(f'Traza: {traceback.format_exc()}')
            sys.exit(1)

        d_ads = {}
        ADS_modo = 'Disparado'

        while True:
            try:
                ee = '10'
                t0 = time.perf_counter()
                ERR_ADS = [0, 0, 0, 0]
                ee = '11'

                # Update heartbeat
                if heartbeat_dict is not None:
                    heartbeat_dict[ads_name] = time.time()

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
                                    else:
                                        logger_local.error(f"Lectura devolvió None en {nombre_ADS_local}")
                                        L_ADS.append(0)
                                except OSError as e:
                                    logger_local.error(f"Error lectura en {nombre_ADS_local}: {e}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                except Exception as e:
                                    logger_local.error(f"Error INESPERADO en lectura {nombre_ADS_local}: {e}")
                                    L_ADS.append(0)
                        elif modo == 3:
                            ee = '30b'
                            indice1 = 0 if indice == 0 else 3
                            L_ADS = []
                            for j in range(bucles_ADS[indice]):
                                try:
                                    val = adc.read_adc_difference(indice1, gain=gain_ADS[indice], data_rate=rate_ADS[indice])
                                    if val is not None:
                                        L_ADS.append(val)
                                    else:
                                        logger_local.error(f"Lectura diferencial devolvió None en {nombre_ADS_local}")
                                        L_ADS.append(0)
                                except OSError as e:
                                    logger_local.error(f"Error diferencial en {nombre_ADS_local}: {e}")
                                    time.sleep(0.005)
                                    L_ADS.append(0)
                                except Exception as e:
                                    logger_local.error(f"Error INESPERADO en lectura diferencial {nombre_ADS_local}: {e}")
                                    L_ADS.append(0)
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
                                logger_local.error(f"Error continua en {nombre_ADS_local}: {e}")
                                time.sleep(0.005)
                                L_ADS[i] = 0
                            except Exception as e:
                                logger_local.error(f"Error INESPERADO en lectura continua {nombre_ADS_local}: {e}")
                                L_ADS[i] = 0
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
                    logger_local.info(f'{time.time():.5f} / {nombre_ADS_local}: t1={t1:6.1f}-t2={t2:6.1f}')

                # Timing
                t3 = (time.perf_counter() - t0)
                time.sleep(max(tmuestra_ADS - t3, 0))
                Ncapturas += 1

            except Exception as e:
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                logger_local.error(f"{tiempo} - Error en {nombre_ADS_local}: {e}")
                import traceback
                logger_local.error(f"Traza: {traceback.format_exc()}")
                sys.exit(1)
    
    except Exception as e:
        print(f'[ERROR {ads_name}] Fatal error: {e}', flush=True)
        import traceback
        print(f'[ERROR {ads_name}] Traceback: {traceback.format_exc()}', flush=True)
        sys.exit(1)


def get_ads_config_hash(ads_config):
    """Generate a hash of ADS config to detect changes"""
    items = []
    for key in sorted(ads_config.keys()):
        value = ads_config[key]
        if isinstance(value, list):
            value = tuple(value)
        elif isinstance(value, dict):
            value = tuple(sorted(value.items()))
        items.append((key, value))
    return hash(tuple(items))


if __name__ == '__main__':
    # Control execution service
    hay_ads_activos = len(lista_ads)
    controlar_servicio(servicio, hay_ads_activos > 0)

    log_local.info(Fore.RESET + '=' * 50)
    log_local.info(Fore.BLUE + 'ADS_activos=')
    for ads in lista_ads:
        log_local.manual(Fore.RED + f' -{ads["id"]}=' + Fore.BLUE +
                    f' direc={ads["direccion"]} - var= {ads["vars"]} - modo={ads["modo"]}')
    log_local.info(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Track active processes: {ads_name: (process, config_hash)}
    procesos_dict = {}
    
    # Create manager for heartbeat tracking
    manager = multiprocessing.Manager()
    heartbeat_dict = manager.dict()

    # Start initial processes with retry - staggered to avoid I2C contention
    # Start ADS with higher addresses first (they tend to have more I2C issues)
    lista_ads_sorted = sorted(lista_ads, key=lambda x: x.get('direccion', 0), reverse=True)
    
    for i, ads in enumerate(lista_ads_sorted):
        ads_name = ads['id']
        config_hash = get_ads_config_hash(ads)
        log_local.info(f'Iniciando proceso para {ads_name} (intento 1)')
        log_local.debug(f'{ads_name} config: {ads}')
        
        # Pass only minimal data to subprocess
        ads_params = {
            'servidor': params['servidor'],
            'usuario': params['usuario'],
            'clave': params['clave'],
            'basedatos': params['basedatos']
        }
        
        # Retry loop with exponential backoff
        started = False
        for attempt in range(MAX_STARTUP_RETRIES):
            # Create a pipe to receive startup confirmation
            startup_pipe = multiprocessing.Pipe()

            p = multiprocessing.Process(
                target=ADS_captura,
                args=(i, ads_params, ads_name, ads, startup_pipe, heartbeat_dict),
                name=f'p_{ads_name}'
            )
            p.start()

            # Wait for startup confirmation (max 5 seconds)
            startup_success = False
            for _ in range(50):  # 5 seconds total, checking every 0.1s
                if startup_pipe[0].poll(0.1):
                    try:
                        startup_success = startup_pipe[0].recv()
                    except Exception as e:
                        log_local.warning(f'{ads_name} error receiving startup: {e}')
                    break

            # Close parent's end of the pipe immediately after receiving
            startup_pipe[0].close()

            if startup_success and p.is_alive():
                log_local.info(f'{ads_name} confirmó inicio correctamente')
                started = True
                break
            else:
                log_local.warning(f'{ads_name} no confirmó inicio (intento {attempt+1}/{MAX_STARTUP_RETRIES})')
                p.terminate()
                p.join(timeout=2)
                if attempt < MAX_STARTUP_RETRIES - 1:
                    backoff = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                    log_local.info(f'Esperando {backoff}s antes de reintentar...')
                    time.sleep(backoff)
        
        if started:
            procesos_dict[ads_name] = (p, config_hash)
            heartbeat_dict[ads_name] = time.time()
            log_local.info(f'Proceso {p.name} iniciado correctamente')
            # Small delay before starting next process to avoid I2C contention
            if i < len(lista_ads_sorted) - 1:
                time.sleep(I2C_BETWEEN_DELAY)
        else:
            log_local.error(f'Error CRÍTICO: No se pudo iniciar {ads_name} después de {MAX_STARTUP_RETRIES} intentos')

    log_local.info(f'Procesos activos= {multiprocessing.active_children()}')

    # Monitor loop - reload params every second and restart changed/stuck processes
    consecutive_errors = 0
    
    while True:
        try:
            # Reload params
            params = cargar_parametros()
            lista_ads = obtener_ads_activos(params)
            current_ads_names = set(ads['id'] for ads in lista_ads)
            
            # Check for processes that should be stopped (disabled, changed, or stuck)
            for ads_name in list(procesos_dict.keys()):
                p, old_hash = procesos_dict[ads_name]
                
                # Check if process died
                if not p.is_alive():
                    log_local.info(f'Proceso {p} parado {p.name}')
                    del procesos_dict[ads_name]
                    continue
                
                # Check if ADS was disabled (no longer in active list)
                if ads_name not in current_ads_names:
                    log_local.info(f'ADS {ads_name} desactivado, terminando proceso...')
                    p.terminate()
                    p.join(timeout=3)
                    if p.is_alive():
                        p.kill()
                        p.join(timeout=1)
                    del procesos_dict[ads_name]
                    continue
                
                # Check if config changed
                for ads in lista_ads:
                    if ads['id'] == ads_name:
                        new_hash = get_ads_config_hash(ads)
                        if new_hash != old_hash:
                            log_local.info(f'Configuración de {ads_name} cambió, reiniciando...')
                            p.terminate()
                            p.join(timeout=3)
                            if p.is_alive():
                                p.kill()
                                p.join(timeout=1)
                            del procesos_dict[ads_name]
                        break
                
                # Health check: no data for HEALTH_CHECK_TIMEOUT seconds
                if ads_name in heartbeat_dict:
                    last_heartbeat = heartbeat_dict[ads_name]
                    elapsed = time.time() - last_heartbeat
                    if elapsed > HEALTH_CHECK_TIMEOUT:
                        log_local.warning(f'{ads_name} no produce datos desde hace {elapsed:.1f}s, reiniciando...')
                        p.terminate()
                        p.join(timeout=3)
                        if p.is_alive():
                            p.kill()
                            p.join(timeout=1)
                        del procesos_dict[ads_name]
                    elif elapsed > 5:
                        # Log warning if no data for 5 seconds (but don't restart yet)
                        log_local.debug(f'{ads_name} sin datos desde hace {elapsed:.1f}s')
            
            # Start processes for active ADS that don't have a process
            for i, ads in enumerate(lista_ads):
                ads_name = ads['id']
                if ads_name not in procesos_dict:
                    config_hash = get_ads_config_hash(ads)
                    log_local.info(f'Iniciando proceso para {ads_name}')
                    
                    ads_params = {
                        'servidor': params['servidor'],
                        'usuario': params['usuario'],
                        'clave': params['clave'],
                        'basedatos': params['basedatos']
                    }
                    
                    # Retry loop for restart
                    started = False
                    for attempt in range(MAX_STARTUP_RETRIES):
                        startup_pipe = multiprocessing.Pipe()
                        p = multiprocessing.Process(
                            target=ADS_captura, 
                            args=(i, ads_params, ads_name, ads, startup_pipe, heartbeat_dict), 
                            name=f'p_{ads_name}'
                        )
                        p.start()
                        
                        startup_success = False
                        for _ in range(50):
                            if startup_pipe[0].poll(0.1):
                                startup_success = startup_pipe[0].recv()
                                break
                        
                        if startup_success and p.is_alive():
                            started = True
                            break
                        else:
                            p.terminate()
                            p.join(timeout=1)
                            if attempt < MAX_STARTUP_RETRIES - 1:
                                time.sleep(2 ** attempt)
                    
                    if started:
                        procesos_dict[ads_name] = (p, config_hash)
                        heartbeat_dict[ads_name] = time.time()
                        log_local.info(f'Proceso {p.name} iniciado correctamente')
                        consecutive_errors = 0
                    else:
                        log_local.error(f'Error al iniciar {ads_name} después de {MAX_STARTUP_RETRIES} intentos')
                        consecutive_errors += 1
                        if consecutive_errors > 10:
                            log_local.error('Demasiados errores consecutivos, esperando...')
                            time.sleep(10)
                            consecutive_errors = 0
            
            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            log_local.error(Fore.RED + '=' * 50)
            log_local.error('Finalizando fv_ads_import.py.......')
            for ads_name, (p, _) in list(procesos_dict.items()):
                log_local.error(f'     ....Terminando hilo..{p}')
                p.terminate()
                p.join(timeout=2)
                if p.is_alive():
                    p.kill()
                time.sleep(0.5)
            sys.exit()
        
        except Exception as e:
            log_local.error(f'Error en bucle principal: {e}')
            import traceback
            log_local.error(f'Traza: {traceback.format_exc()}')
            consecutive_errors += 1
            if consecutive_errors > 10:
                log_local.error('Demasiados errores, esperando...')
                time.sleep(10)
                consecutive_errors = 0
            time.sleep(1)
