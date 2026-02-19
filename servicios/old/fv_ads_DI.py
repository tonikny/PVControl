import time
import sys
import multiprocessing

import Adafruit_ADS1x15  # Import the ADS1x15 module.
import colorama  # colores en ventana Terminal
from colorama import Fore, Style

from helpers.gestor_parametros_DI import GestorParametrosDI
from helpers.control_servicio import controlar_servicio
from helpers.gestor_logs_DI import GestorLogsDI

# from smbus import SMBus
# bus = SMBus(1)  # Activo Bus I2C para ADS o PCF

def leer_adc(callable_fn, ads_nombre, delay=0.005, logger_obj=None):
    # Use provided logger - it should always be provided from captura_ads
    logger_used = logger_obj

    try:
        result = callable_fn()
        # Add a small validation to ensure we got a valid reading
        if result is None:
            logger_used.warning(f"Resultado None obtenido para {ads_nombre}")
            time.sleep(delay)
            return 0  # Return a default value instead of None
        return result
    except OSError as e:
        if e.errno not in (5, 121):
            logger_used.error(f"OSError {e}")
            raise
        logger_used.error(f"Error lectura {ads_nombre}")
        time.sleep(delay)
        return 0  # Return a default value
    except Exception as e:
        logger_used.error(f"Error inesperado en lectura {ads_nombre}: {e}")
        time.sleep(delay)
        return 0  # Return a default value

def captura_ads(ads_actual, indice_ads):
    """Captura datos del ADS especificado.

    Args:
        ads_actual: Diccionario con la configuración del ADS.
        indice_ads: Índice del ADS para multiplexación.
    """
    # Crear instancias locales de los gestores para cada proceso con inyección de dependencias
    from helpers.gestor_parametros_DI import GestorParametrosDI
    from helpers.gestor_bd import GestorBD

    # Crear instancias con dependencias inyectadas
    logger_local = GestorLogsDI(f"{__name__}-{ads_actual['id']}")
    gp_local = GestorParametrosDI(logger=logger_local)

    n_capturas = 0
    ee = "0"  # Inicializar con string para consistencia

    time.sleep(0.02 * indice_ads)  # multiplexo un poco los distintos procesos

    logger_local.info(Fore.BLUE + "=" * 40 + "Proceso" + ads_actual["id"] + "=" * 40)

    ads_nombre = ads_actual["id"]
    logger_local.debug(f"Iniciando conexión con base de datos para {ads_nombre}")
    try:
        gestor_bd = GestorBD()
        logger_local.debug(f"Base de datos conectada para {ads_nombre}")
        
        logger_local.debug(f"Verificando existencia de equipo {ads_nombre}")
        existe = not gestor_bd.insertar_equipo_si_falta(ads_nombre)
        logger_local.debug(f"Equipo {ads_nombre} verificación completada")
    except Exception as e:
        logger_local.error(f"Error fatal en operación de base de datos para {ads_nombre}: {e}")
        import traceback
        logger_local.error(f"Detalle del error: {traceback.format_exc()}")
        sys.exit(1)
    
    if existe:
        logger_local.manual(Fore.RED + f"Registro RAM - clave = {ads_nombre} ya creado")

    logger_local.manual(f"Activando ADS en direccion {ads_actual.get('direccion')}")
    logger_local.debug(f"Creando instancia de ADS1115 en dirección {ads_actual.get('direccion')}")
    try:
        adc = Adafruit_ADS1x15.ADS1115(address=ads_actual.get("direccion"), busnum=1)
        logger_local.debug(f"ADS1115 en dirección {ads_actual.get('direccion')} inicializado correctamente")
    except Exception as e:
        logger_local.error(f"Error fatal al inicializar ADS en dirección {ads_actual.get('direccion')}: {e}")
        import traceback
        logger_local.error(f"Detalle del error: {traceback.format_exc()}")
        sys.exit(1)

    d_ads = {}
    modo_ads = "Disparado"
    version_parametros = 0

    # Store initial parameter modification time to avoid frequent file system calls
    import os
    # Determine the path to Parametros_FV.py based on the project structure
    PARAMETROS_FV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Parametros_FV.py")
    try:
        t_cambio_parametros = os.path.getmtime(PARAMETROS_FV_PATH) - 100  # Small offset to force initial check
    except:
        # If file doesn't exist, use a default past time
        t_cambio_parametros = time.time() - 1000

    while True:
        try:
            ee = "10"
            t0 = time.perf_counter()
            tp0 = time.process_time()
            err_ads = [0, 0, 0, 0]  # Error bruto capturas ADS
            ee = "11"
            # ---------------- Recargar configuración (similar to original) ----------------
            # Only check for parameter changes using direct file modification time check
            # Don't call gp_local.leer_parametros("ADS") unless there's an actual change
            try:
                current_mtime = os.path.getmtime(PARAMETROS_FV_PATH)
                if current_mtime != t_cambio_parametros:
                    # Only reload parameters when there's an actual change
                    ads_config = gp_local.leer_parametros("ADS")
                    t_cambio_parametros = current_mtime
                    
                    version_parametros = gp_local.version()
                    ee = "20"
                    logger_local.info(
                        Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                        f" -- Leyendo Parametros_FV.py para {ads_nombre} - Capturas={n_capturas}"
                    )
                    n_capturas = 0
                    ee = "20a"

                    modo_ads = "Disparado"  # valor por defecto
                    ads_config_lista = gp_local.convertir_dict_a_list(ads_config)
                    nuevo_ads = next(
                        (ads for ads in ads_config_lista if ads["id"] == ads_nombre),
                        None,
                    )
                    if nuevo_ads:
                        ads_actual = nuevo_ads
                    else:
                        logger_local.warning(f"No se encontró configuración para {ads_nombre}")

                    for i, modo in enumerate(ads_actual["modo"]):
                        ee = "20b"
                        if modo == 2:
                            ee = "20c"
                            adc.start_adc(i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i])
                            ee = "20d"
                            modo_ads = "Continuo"
                            logger_local.info(f"entrada A{i} : ")
                            break
                        elif modo == 4:
                            ee = "20d"
                            diff = 0 if i == 0 else 3
                            adc.start_adc_difference(
                                diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                            )
                            modo_ads = "Continuo_Diferencial"
                            logger_local.info(f"entrada A{i} : ")
                            break

                    logger_local.info(Fore.BLUE + f"Modo {ads_nombre} = " + Fore.GREEN + modo_ads)
            except FileNotFoundError:
                # Handle case where parameter file doesn't exist
                pass
            except Exception as e:
                logger_local.error(f"Error verificando cambios en parámetros: {e}")

            ee = "30.0"

            # ---------------- Captura de datos ----------------
            if modo_ads == "Disparado":
                ee = "30"
                for i, modo in enumerate(ads_actual["modo"]):
                    if modo == 1:
                        ee = "30a"
                        capturas = [leer_adc(
                            lambda: adc.read_adc(
                                i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                            ),
                            ads_nombre,
                            logger_obj=logger_local  # Pasar logger al leer_adc
                        ) for j in range(ads_actual["bucles"][i])]
                    elif modo == 3:  # Diferencial
                        ee = "30b"
                        diff = 0 if i == 0 else 3
                        capturas = [leer_adc(
                            lambda: adc.read_adc_difference(
                                diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                            ),
                            ads_nombre,
                            logger_obj=logger_local  # Pasar logger al leer_adc
                        ) for j in range(ads_actual["bucles"][i])]
                    else:
                        continue
                    ee = "30c"

                    if modo != 0:
                        ee = "30d"
                        if capturas:
                            mediana = sorted(capturas)[len(capturas) // 2]  # Mediana
                            err_ads[i] = max(capturas) - min(capturas)
                        else:
                            mediana = 0
                            err_ads[i] = 0
                        ee = "31"

                        var_name = ads_actual["vars"][i]
                        if not var_name:
                            continue
                        ee = "32"
                        d_ads[var_name] = round(
                            mediana * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                        )
                        ee = "33"
                        ee = "34"
                        logger_local.debug(
                            f"capturas-A{i}={capturas} - {mediana} "
                            f"Err:{err_ads[i]}- {var_name}={d_ads[var_name]}"
                        )

            else:  # Continuo o continuo diferencial
                ee = "40"
                for i, modo in enumerate(ads_actual["modo"]):
                    n = ads_actual["bucles"][i]
                    rate = ads_actual["rate"][i]

                    capturas = ([0.0] * n)
                    for j in range(n):
                        capturas[j] = leer_adc(
                            lambda: adc.get_last_result(), ads_nombre,
                            logger_obj=logger_local  # Pasar logger al leer_adc
                        )
                        time.sleep(1 / rate)

                    if capturas:
                        mediana = sorted(capturas)[len(capturas) // 2]  # Mediana
                        err_ads[i] = max(capturas) - min(capturas)
                    else:
                        mediana = 0
                        err_ads[i] = 0

                    var_name = ads_actual["vars"][i]
                    if not var_name:
                        continue

                    d_ads[var_name] = round(
                        mediana * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                    )

                    logger_local.debug(
                        f"capturas-A{i}={capturas}-{mediana} "
                        f"Err:{err_ads[i]} - {var_name}={d_ads[var_name]}"
                    )

            ee = "50"
            t1 = (time.perf_counter() - t0) * 1000

            if logger_local.es_debug():
                t = str(round(time.time(), 3))
                datos_log = f"{t[-6:]}: {ads_nombre}-Modo={ads_actual['modo']} {str(err_ads):16}-Captura = {d_ads}"
                if indice_ads == 0:
                    logger_local.debug(Fore.RESET + datos_log)
                elif indice_ads == 1:
                    logger_local.debug(Fore.GREEN + datos_log)
                elif indice_ads == 2:
                    logger_local.debug(Fore.CYAN + datos_log)
                else:
                    logger_local.debug(Fore.RED + datos_log)

            ee = "60"
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

            gestor_bd.guardar_datos_equipo_dict(ads_nombre, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 = (time.process_time() - tp0) * 1000

            ee = "70"

            if logger_local.es_info():
                msg =f"{time.time():.5f} / {ads_nombre}: "
                msg += f"t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:"

                if modo_ads == "Disparado":
                    msg += f"{ads_actual['rate']} Bucles: {ads_actual['bucles']}"
                else:
                    msg += f"{ads_actual['rate']} Bucles: {ads_actual['bucles']} "
                    msg += f"- {modo_ads} entrada {ads_nombre}"
                logger_local.info(msg)

            ee = "80"
            logger_local.debug(Fore.CYAN + "*" * 80)
            logger_local.debug("*" * 80 + Fore.RESET)

            # ---------------- Timing ----------------
            t3 = time.perf_counter() - t0
            time.sleep(max(ads_actual["tmuestra"] - t3, 0))
            n_capturas += 1

        except:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_local.error(f"{tiempo} - Error {ee} en {ads_nombre}....se reinicia el proceso de captura del {ads_nombre}")
            sys.exit()

def preparar_lista_ads_activos(config, logger_obj):
    """Prepara la lista de ADS activos según los argumentos proporcionados."""
    if "-ADS1" in sys.argv:  # fuerzo solo ADS1
        for cfg in config:
            cfg["usar"] = cfg["id"] == "ADS1"
    elif "-ADS4" in sys.argv:  # fuerzo solo ADS4
        for cfg in config:
            cfg["usar"] = cfg["id"] == "ADS4"

    activos = [cfg for  cfg in config if cfg.get("usar")]

    logger_obj.manual(Fore.RESET + "=" * 50)
    logger_obj.manual(Fore.BLUE + "activos=")
    for cfg in activos:
        logger_obj.manual(
            Fore.RED
            + f" -{cfg['id']} "
            + Fore.BLUE
            + f"direc={cfg['direccion']} vars={cfg['vars']} modo={cfg['modo']}"
        )
    logger_obj.manual(Fore.RESET + "=" * 50)

    return activos

def main():
    try:
        colorama.init(autoreset=True)
        time.sleep(5)

        # --------------------------------------------------
        # Comprobacion argumentos especificos en comando
        # --------------------------------------------------
        simular = 0
        if "-s" in sys.argv:
            simular = 1  # para desarrollo permite simular respuesta

        # Crear instancias con inyección de dependencias
        log_local = GestorLogsDI(nombre=__name__)
        gp_local = GestorParametrosDI(logger=log_local)

        log_local.info(Style.BRIGHT + Fore.YELLOW + "Arrancando" + Fore.GREEN + " fv_ads_DI.py")

        # --------------------------------------------------
        # Cargar desde Parametros_FV.py
        # --------------------------------------------------
        ads_config = gp_local.leer_parametros("ADS")
        # comandos = ads_config.pop("COMANDOS")  # si tuviera comandos se borraria de la lista
        ads_config = gp_local.convertir_dict_a_list(ads_config)

        # filtrar ADS activos
        ads_activos = preparar_lista_ads_activos(ads_config, log_local)

        # --------------------------------------------------
        # Control Ejecucion Servicio
        # --------------------------------------------------
        hay_ads_activos = len(ads_activos) > 0
        controlar_servicio("fv_ads", hay_ads_activos)

        # --------------------------------------------------
        # Arrancando procesos
        # --------------------------------------------------
        for idx, ads in enumerate(ads_activos):
            multiprocessing.Process(target=captura_ads, args=(ads, idx), name=f'p_{ads["id"]}').start()

        procesos = multiprocessing.active_children()  # lista procesos
        log_local.info(f'Procesos activos= {procesos}')

        # --------------------------------------------------
        # Bucle de vigilancia
        # --------------------------------------------------
        while True:
            try:
                for p in procesos:
                    if not p.is_alive():
                        log_local.info(f'Proceso {p} parado {p.name}')
                        time.sleep(3)
                        # Extract index from process name (assuming format "p_ADSX" where X is the index)
                        # Actually, we need to map the process name back to the correct ads config
                        nombre = p.name[2:]  # Remove "p_" prefix
                        # Find the corresponding config in ads_activos
                        ads_config_item = None
                        idx = None
                        for i, ads in enumerate(ads_activos):
                            if ads['id'] == nombre:
                                ads_config_item = ads
                                idx = i
                                break
                        
                        if ads_config_item is not None:
                            # Restart the process with the same config
                            multiprocessing.Process(target=captura_ads, args=(ads_config_item, idx), name=f'p_{nombre}').start()
                            procesos = multiprocessing.active_children()
                        else:
                            log_local.error(f"Error: proceso {nombre} no encontrado en la configuración")

                time.sleep(1)

            except KeyboardInterrupt:
                time.sleep(1)
                log_local.error('=' * 50)
                log_local.error('Finalizando fv_ads_DI.py.......')
                for p in procesos:
                    log_local.error(f'     ....Terminando hilo..{p}')
                    p.terminate()
                    time.sleep(1)
                sys.exit()

    except Exception as e:
        log_local = GestorLogsDI(nombre=__name__)
        log_local.error(f"Error durante la inicialización del servicio: {e}")
        import traceback
        log_local.error(f"Detalle del error: {traceback.format_exc()}")
        sys.exit(1)

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    main()