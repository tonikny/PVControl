import time
import sys

import Adafruit_ADS1x15  # Import the ADS1x15 module.
import colorama  # colores en ventana Terminal
from colorama import Fore, Style

from helpers.gestor_parametros_DI import GestorParametrosDI
from helpers.control_servicio import controlar_servicio
from helpers.control_procesos_DI import ControlProcesosDI
from helpers.gestor_logs_DI import GestorLogsDI

# from smbus import SMBus
# bus = SMBus(1)  # Activo Bus I2C para ADS o PCF

def leer_adc(callable_fn, ads_nombre, delay=0.005, logger_obj=None):
    # Use provided logger - it should always be provided from captura_ads
    logger_used = logger_obj

    try:
        return callable_fn()
    except OSError as e:
        if e.errno not in (5, 121):
            logger_used.error(f"OSError {e}")
            raise
        logger_used.error(f"Error lectura {ads_nombre}")
        time.sleep(delay)
        return None  # Return None to indicate failure

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
    gestor_bd = GestorBD()
    existe = not gestor_bd.insertar_equipo_si_falta(ads_nombre)
    if existe:
        logger_local.manual(Fore.RED + f"Registro RAM - clave = {ads_nombre} ya creado")

    # Inicializar ADC con reintento
    adc = None
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries and adc is None:
        try:
            logger_local.manual(f"Activando ADS en direccion {ads_actual.get('direccion')}, intento {retry_count + 1}")
            adc = Adafruit_ADS1x15.ADS1115(address=ads_actual.get("direccion"), busnum=1)
        except Exception as e:
            retry_count += 1
            logger_local.error(f"Error al inicializar ADS en dirección {ads_actual.get('direccion')}, intento {retry_count}/3: {e}")
            time.sleep(1)  # Esperar antes de reintentar
    
    if adc is None:
        logger_local.error(f"No se pudo inicializar el ADS {ads_nombre} después de {max_retries} intentos. Terminando proceso.")
        sys.exit(1)

    d_ads = {}
    modo_ads = "Disparado"
    version_parametros = 0

    # Variable para controlar si necesitamos reiniciar el ADC
    necesita_reiniciar_adc = False

    while True:
        try:
            # Reiniciar el ADC si es necesario
            if necesita_reiniciar_adc:
                logger_local.warning(f"Reiniciando conexión con ADS {ads_nombre}")
                try:
                    adc = Adafruit_ADS1x15.ADS1115(address=ads_actual.get("direccion"), busnum=1)
                    necesita_reiniciar_adc = False
                    logger_local.info(f"ADS {ads_nombre} reiniciado correctamente")
                except Exception as e:
                    logger_local.error(f"Error al reiniciar ADS {ads_nombre}: {e}")
                    time.sleep(5)  # Esperar antes de volver a intentar
                    continue  # Volver al inicio del bucle

            ee = "10"
            t0 = time.perf_counter()
            tp0 = time.process_time()
            err_ads = [0, 0, 0, 0]  # Error bruto capturas ADS
            ee = "11"
            # ---------------- Recargar configuración ----------------
            ads_config = gp_local.leer_parametros("ADS")
            if gp_local.version() != version_parametros:
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

            ee = "30.0"

            # ---------------- Captura de datos ----------------
            if modo_ads == "Disparado":
                ee = "30"
                for i, modo in enumerate(ads_actual["modo"]):
                    capturas = []
                    if modo == 1:
                        ee = "30a"
                        for _ in range(ads_actual["bucles"][i]):
                            val = leer_adc(
                                lambda: adc.read_adc(
                                    i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                                ),
                                ads_nombre,
                                logger_obj=logger_local  # Pasar logger al leer_adc
                            )
                            if val is not None:
                                capturas.append(val)
                            else:
                                # Si falla la lectura, marcar para reiniciar el ADC
                                necesita_reiniciar_adc = True
                                break  # Salir del bucle interno para reiniciar el ADC
                        if necesita_reiniciar_adc:
                            break  # Salir del bucle externo también
                    elif modo == 3:  # Diferencial
                        ee = "30b"
                        diff = 0 if i == 0 else 3
                        for _ in range(ads_actual["bucles"][i]):
                            val = leer_adc(
                                lambda: adc.read_adc_difference(
                                    diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                                ),
                                ads_nombre,
                                logger_obj=logger_local  # Pasar logger al leer_adc
                            )
                            if val is not None:
                                capturas.append(val)
                            else:
                                # Si falla la lectura, marcar para reiniciar el ADC
                                necesita_reiniciar_adc = True
                                break  # Salir del bucle interno para reiniciar el ADC
                        if necesita_reiniciar_adc:
                            break  # Salir del bucle externo también

                    else:
                        continue
                    ee = "30c"

                    if modo != 0 and not necesita_reiniciar_adc:  # Solo procesar si no hay error
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
                # Solo continuar si no hay necesidad de reiniciar el ADC
                if not necesita_reiniciar_adc:
                    ee = "40"
                    for i, modo in enumerate(ads_actual["modo"]):
                        # Skip if modo is 0 (not active)
                        if modo == 0:
                            continue
                            
                        n = ads_actual["bucles"][i]
                        rate = ads_actual["rate"][i]

                        capturas = []
                        for _ in range(n):
                            val = leer_adc(
                                lambda: adc.get_last_result(), ads_nombre,
                                logger_obj=logger_local  # Pasar logger al leer_adc
                            )
                            if val is not None:
                                capturas.append(val)
                            else:
                                # Si falla la lectura, marcar para reiniciar el ADC
                                necesita_reiniciar_adc = True
                                logger_local.error(f"Lectura fallida en canal {i} del ADS {ads_nombre}, marcando para reiniciar ADC")
                                break  # Salir del bucle interno para reiniciar el ADC
                            
                            time.sleep(1 / rate)

                        if necesita_reiniciar_adc:
                            break  # Salir del bucle externo también
                        
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

            # Solo guardar datos si no hay error
            if not necesita_reiniciar_adc:
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

        except (KeyboardInterrupt, SystemExit):
            # Permitir que las excepciones del sistema se propaguen
            logger_local.error(f"Interrupción del sistema, terminando proceso {ads_nombre}")
            raise
        except Exception as e:
            logger_local.error(
                Fore.RED
                + f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error {ee} en {ads_nombre}: {repr(e)}"
            )
            logger_local.error(f"{ads_nombre}....se intentará reiniciar la conexión con el dispositivo")
            necesita_reiniciar_adc = True  # Marcar para reiniciar el ADC

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
    # Iniciar y vigilar Procesos
    # --------------------------------------------------
    controlador_procesos = ControlProcesosDI(logger=log_local)
    procesos = controlador_procesos.iniciar_procesos(ads_activos, captura_ads)
    controlador_procesos.vigilar_procesos(procesos, ads_activos, captura_ads)

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    main()