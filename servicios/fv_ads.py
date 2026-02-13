import logging
import time
import sys

import Adafruit_ADS1x15  # Import the ADS1x15 module.
import colorama  # colores en ventana Terminal
from colorama import Fore, Style

from helpers.gestor_parametros import GestorParametros
from helpers.gestor_bd import GestorBD
from helpers.control_servicio import controlar_servicio
from helpers.control_procesos import iniciar_procesos, vigilar_procesos
from helpers.gestor_logs import GestorLogs

# from smbus import SMBus
# bus = SMBus(1)  # Activo Bus I2C para ADS o PCF

def leer_adc(callable_fn, ads_nombre, delay=0.005):
    try:
        return callable_fn()
    except OSError as e:
        if e.errno not in (5, 121):
            log.error(f"OSError {e}")
            raise
        log.error(f"Error lectura {ads_nombre}")
        time.sleep(delay)

def captura_ads(ads_actual, indice_ads):
    """Captura datos del ADS especificado.

    Args:
        ads_actual: Diccionario con la configuración del ADS.
        indice_ads: Índice del ADS para multiplexación.
    """
    global gp
    n_capturas = 0
    ee = 0

    time.sleep(0.02 * indice_ads)  # multiplexo un poco los distintos procesos

    log.info(Fore.BLUE + "=" * 40 + "Proceso" + ads_actual["id"] + "=" * 40)

    ads_nombre = ads_actual["id"]
    gestor = GestorBD()
    existe = not gestor.insertar_equipo_si_falta(ads_nombre)
    if existe:
        log.manual(Fore.RED + f"Registro RAM - clave = {ads_nombre} ya creado")

    log.manual(f"Activando ADS en direccion {ads_actual.get('direccion')}")
    adc = Adafruit_ADS1x15.ADS1115(address=ads_actual.get("direccion"), busnum=1)

    d_ads = {}
    modo_ads = "Disparado"
    version_parametros = 0

    while True:
        try:
            ee = "10"
            t0 = time.perf_counter()
            tp0 = time.process_time()
            err_ads = [0, 0, 0, 0]  # Error bruto capturas ADS
            ee = "11"
            # ---------------- Recargar configuración ----------------
            ads_config = gp.leer_parametros("ADS")
            if gp.version() != version_parametros:
                version_parametros = gp.version()
                ee = "20"
                log.info(
                    Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S") +
                    f" -- Leyendo Parametros_FV.py para {ads_nombre} - Capturas={n_capturas}"
                )
                n_capturas = 0
                ee = "20a"

                modo_ads = "Disparado"  # valor por defecto
                ads_config_lista = gp.convertir_dict_a_list(ads_config)
                nuevo_ads = next(
                    (ads for ads in ads_config_lista if ads["id"] == ads_nombre),
                    None,
                )
                if nuevo_ads:
                    ads_actual = nuevo_ads
                else:
                    log.warning(f"No se encontró configuración para {ads_nombre}")

                for i, modo in enumerate(ads_actual["modo"]):
                    ee = "20b"
                    if modo == 2:
                        ee = "20c"
                        adc.start_adc(i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i])
                        ee = "20d"
                        modo_ads = "Continuo"
                        log.info(f"entrada A{i} : ")
                        break
                    elif modo == 4:
                        ee = "20d"
                        diff = 0 if i == 0 else 3
                        adc.start_adc_difference(
                            diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                        )
                        modo_ads = "Continuo_Diferencial"
                        log.info(f"entrada A{i} : ")
                        break

                log.info(Fore.BLUE + f"Modo {ads_nombre} = " + Fore.GREEN + modo_ads)

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
                            )
                            if val is not None:
                                capturas.append(val)
                    elif modo == 3:  # Diferencial
                        ee = "30b"
                        diff = 0 if i == 0 else 3
                        for _ in range(ads_actual["bucles"][i]):
                            val = leer_adc(
                                lambda: adc.read_adc_difference(
                                    diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                                ),
                                ads_nombre,
                            )
                            if val is not None:
                                capturas.append(val)

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
                        ee = 32
                        d_ads[var_name] = round(
                            mediana * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                        )
                        ee = 33
                        ee = 34
                        log.debug(
                            f"capturas-A{i}={capturas} - {mediana} "
                            f"Err:{err_ads[i]}- {var_name}={d_ads[var_name]}"
                        )

            else:  # Continuo o continuo diferencial
                ee = "40"
                for i, modo in enumerate(ads_actual["modo"]):
                    n = ads_actual["bucles"][i]
                    rate = ads_actual["rate"][i]

                    capturas = []
                    for _ in range(n):
                        val = leer_adc(
                            lambda: adc.get_last_result(), ads_nombre,
                        )
                        if val is not None:
                            capturas.append(val)
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

                    log.debug(
                        f"capturas-A{i}={capturas}-{mediana} "
                        f"Err:{err_ads[i]} - {var_name}={d_ads[var_name]}"
                    )

            ee = "50"
            t1 = (time.perf_counter() - t0) * 1000

            if log.es_debug():
                t = str(round(time.time(), 3))
                datos_log = f"{t[-6:]}: {ads_nombre}-Modo={ads_actual['modo']} {str(err_ads):16}-Captura = {d_ads}"
                if indice_ads == 0:
                    log.debug(Fore.RESET + datos_log)
                elif indice_ads == 1:
                    log.debug(Fore.GREEN + datos_log)
                elif indice_ads == 2:
                    log.debug(Fore.CYAN + datos_log)
                else:
                    log.debug(Fore.RED + datos_log)

            ee = "60"
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

            gestor.guardar_datos_equipo_dict(ads_nombre, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 = (time.process_time() - tp0) * 1000

            ee = "70"

            if log.es_info():
                log.info(
                    f"{time.time():.5f} / {ads_nombre}: "
                    f"t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:"
                )
                if modo_ads == "Disparado":
                    log.info(f"{ads_actual['rate']} Bucles: {ads_actual['bucles']}")
                else:
                    log.info(
                        f"{ads_actual['rate']} Bucles: {ads_actual['bucles']} "
                        f"- {modo_ads} entrada {ads_nombre}"
                    )

            ee = "80"
            log.debug(Fore.CYAN + "*" * 80)
            log.debug("*" * 80 + Fore.RESET)
            # ---------------- Timing ----------------
            t3 = time.perf_counter() - t0
            time.sleep(max(ads_actual["tmuestra"] - t3, 0))
            n_capturas += 1

        except Exception as e:
            log.error(
                Fore.RED
                + f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error {ee} en {ads_nombre}: {repr(e)}"
            )
            log.error(f"{ads_nombre}....se reinicia el proceso de captura del {ads_nombre}")
            sys.exit(1)

def preparar_lista_ads_activos(config):
    """Prepara la lista de ADS activos según los argumentos proporcionados."""
    if "-ADS1" in sys.argv:  # fuerzo solo ADS1
        for cfg in config:
            cfg["usar"] = cfg["id"] == "ADS1"
    elif "-ADS4" in sys.argv:  # fuerzo solo ADS4
        for cfg in config:
            cfg["usar"] = cfg["id"] == "ADS4"

    activos = [cfg for  cfg in config if cfg.get("usar")]

    log.manual(Fore.RESET + "=" * 50)
    log.manual(Fore.BLUE + "activos=")
    for cfg in activos:
        log.manual(
            Fore.RED
            + f" -{cfg['id']} "
            + Fore.BLUE
            + f"direc={cfg['direccion']} vars={cfg['vars']} modo={cfg['modo']}"
        )
    log.manual(Fore.RESET + "=" * 50)

    return activos

def main():
    """Función principal que ejecuta el flujo del programa."""
    colorama.init(autoreset=True)
    time.sleep(5)

    # --------------------------------------------------
    # Comprobacion argumentos en comando
    # --------------------------------------------------
    global simular
    if "-s" in sys.argv:
        simular = 1  # para desarrollo permite simular respuesta
    if "-p1" in sys.argv:
        debug_level = logging.WARNING
    elif "-p2" in sys.argv:
        debug_level = logging.INFO
    elif "-p" in sys.argv:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.ERROR

    global log
    log = GestorLogs(nombre=__name__, level=debug_level)
    log.info(Style.BRIGHT + Fore.YELLOW + "Arrancando" + Fore.GREEN + " fv_ads.py")

    # --------------------------------------------------
    # Cargar desde Parametros_FV.py
    # --------------------------------------------------
    global gp
    gp = GestorParametros()
    ads_config = gp.leer_parametros("ADS")
    # comandos = ads_config.pop("COMANDOS")
    ads_config = gp.convertir_dict_a_list(ads_config)

    # filtrar ADS activos
    ads_activos = preparar_lista_ads_activos(ads_config)
    print("ads_activos=", ads_activos)

    # --------------------------------------------------
    # Control Ejecucion Servicio
    # --------------------------------------------------
    hay_ads_activos = len(ads_activos) > 0
    controlar_servicio("fv_ads", hay_ads_activos)

    # --------------------------------------------------
    # Iniciar y vigilar Procesos
    # --------------------------------------------------
    procesos = iniciar_procesos(ads_activos, captura_ads)
    vigilar_procesos(procesos, ads_activos , captura_ads)

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    main()
