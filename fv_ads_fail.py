import time
import sys

# from smbus import SMBus
import Adafruit_ADS1x15  # Import the ADS1x15 module.

import colorama  # colores en ventana Terminal
from colorama import Fore, Style
from helpers.gestor_parametros import cargar_parametros, recargar_parametros, convertir_dict_a_list
from helpers.gestor_bd import GestorBD
from helpers.control_servicio import controlar_servicio
from helpers.control_procesos import iniciar_procesos, vigilar_procesos

###

# --------------------------------------------------
# Comprobacion argumentos en comando
# --------------------------------------------------

simular = DEBUG = 0

if "-s" in sys.argv:
    simular = 1  # para desarrollo permite simular respuesta
if "-p1" in sys.argv:
    DEBUG = 1
elif "-p2" in sys.argv:
    DEBUG = 2
elif "-p" in sys.argv:
    DEBUG = 100

# bus = SMBus(1)  # Activo Bus I2C para ADS o PCF


def leer_adc(callable_fn, ads_nombre, delay=0.005):
    try:
        return callable_fn()
    except OSError as e:
        if e.errno not in (5, 121):
            print("OSError", e)
            raise
        print(f"Error lectura {ads_nombre}")
        time.sleep(delay)

def captura_ads(ads_actual, ads_idx):
    """Captura datos del ADS especificado.
    
    Args:
        ads_actual: Diccionario con la configuración del ADS
        ads_idx: Índice del ADS para multiplexación
    """
    n_capturas = 0
    ee = 0
    
    time.sleep(0.02 * ads_idx)  # multiplexo un poco los distintos procesos

    if DEBUG >= 1:
        print(Fore.BLUE + "=" * 40, "Proceso", ads_actual["id"], "=" * 40)

    ads_nombre = ads_actual["id"]
    gestor = GestorBD()
    existe = not gestor.insertar_equipo_si_falta(ads_nombre)
    if existe:
        print(Fore.RED + f"Registro RAM - clave = {ads_nombre} ya creado")

    print(f"Activando ADS en direccion {ads_actual.get('direccion')}")
    adc = Adafruit_ADS1x15.ADS1115(address=ads_actual.get("direccion"), busnum=1)

    d_ads = {}
    modo_ads = "Disparado"

    while True:
        try:
            ee = "10"
            t0 = time.perf_counter()
            tp0 = time.process_time()
            err_ads = [0, 0, 0, 0]  # Error bruto capturas ADS
            ee = "11"
            # ---------------- Reload config ----------------
            ads_config_v = recargar_parametros()
            if ads_config_v:  # recargo Parametros_FV.py si hay cambios (o es la primera vez)
                ee = "20"
                if DEBUG >= 1:
                    print(
                        Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S"),
                        f" -- Leyendo Parametros_FV.py para {ads_nombre} - Capturas={n_capturas}",
                    )
                n_capturas = 0
                ee = "20a"

                modo_ads = "Disparado"  # valor por defecto
                if DEBUG >= 1:
                    print(Fore.BLUE + f"Modo {ads_nombre} = " + Fore.GREEN, end="")

                for i, modo in enumerate(ads_actual["modo"]):
                    ee = "20b"
                    if modo == 2:
                        ee = "20c"
                        adc.start_adc(i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i])
                        ee = "20d"
                        modo_ads = "Continuo"
                        if DEBUG >= 1:
                            print(f"entrada A{i} : ", end="")
                        break
                    elif modo == 4:
                        ee = "20d"
                        diff = 0 if i == 0 else 3
                        adc.start_adc_difference(
                            diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                        )
                        modo_ads = "Continuo_Diferencial"
                        if DEBUG >= 1:
                            print(f"entrada A{i} : ", end="")
                        break

            ee = "30.0"

            # ---------------- Captura ----------------
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
                        # media = sum(capturas) / len(capturas) if len(capturas) > 0 else 0 # Media
                        mediana = sorted(capturas)[len(capturas) // 2]  # Mediana
                        ee = "31"

                        var_name = ads_actual["vars"][i]
                        if not var_name:
                            continue
                        ee = 32
                        d_ads[var_name] = round(
                            mediana * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                        )
                        ee = 33
                        err_ads[i] = max(capturas) - min(capturas)
                        ee = 34
                        if DEBUG >= 100:
                            print(
                                f"capturas-A{i}={capturas} - {mediana} "
                                f"Err:{err_ads[i]}- {var_name}={d_ads[var_name]}"
                            )

            else:  # Continuo o continuo diferencial
                ee = "40"
                for i, modo in enumerate(ads_actual["modo"]):
                    n = ads_actual["bucles"][i]
                    rate = ads_actual["rate"][i]

                    capturas = [0.0] * n
                    for i in range(n):
                        val = leer_adc(
                            lambda: adc.get_last_result(), ads_nombre,
                        )
                        if val is not None:
                            capturas.append(val)
                        # capturas[i] = adc.get_last_result()
                        time.sleep(1 / rate)

                    # media = sum(capturas) / n
                    mediana = sorted(capturas)[len(capturas) // 2]  # Mediana

                    var_name = ads_actual["vars"][i]
                    if not var_name:
                        continue

                    d_ads[var_name] = round(
                        mediana * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                    )

                    err_ads[i] = max(capturas) - min(capturas)

                    if DEBUG >= 100:
                        print(
                            f"capturas-A{i}={capturas}-{mediana} "
                            f"Err:{err_ads} - {var_name}={d_ads[var_name]}"
                        )

            ee = "50"
            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                if ads_idx == 0:
                    print(Fore.RESET, end="")
                elif ads_idx == 1:
                    print(Fore.BLUE, end="")
                elif ads_idx == 2:
                    print(Fore.CYAN, end="")
                else:
                    print(Fore.RED, end="")

                print(
                    f"{t[-6:]}: {ads_nombre}-Modo={ads_actual['modo']} {str(err_ads):16}-Captura = ",
                    d_ads,
                )

            ee = "60"
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

            gestor.guardar_datos_equipo_dict(ads_nombre, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 = (time.process_time() - tp0) * 1000

            ee = "70"

            if DEBUG >= 2:
                print(
                    f"{time.time():.5f} / {ads_nombre}: "
                    f"t1={t1:6.1f}-t2={t2:6.1f} --tp={tp2:5.2f} -- Rate:",
                    end="",
                )
                if ads_actual["modo"] == "Disparado":
                    print(ads_actual["rate"], "Bucles:", ads_actual["bucles"])
                else:
                    print(
                        ads_actual["rate"],
                        "Bucles:",
                        ads_actual["bucles"],
                        f"- {ads_actual['modo']} entrada {ads_nombre}",
                    )

            ee = "80"
            if DEBUG >= 100:
                print(Fore.CYAN + "*" * 80)
                print("*" * 80 + Fore.RESET)
            # ---------------- Timing ----------------
            t3 = time.perf_counter() - t0
            time.sleep(max(ads_actual["tmuestra"] - t3, 0))
            n_capturas += 1

        except Exception as e:
            print(
                Fore.RED
                + f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error {ee} en {ads_nombre}: {repr(e)}"
            )
            print(f"{ads_nombre}....se reinicia el proceso de captura del {ads_nombre}")
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

    print(Fore.RESET + "=" * 50)
    print(Fore.BLUE + "activos=")
    for cfg in activos:
        print(
            Fore.RED
            + f" -{cfg['id']} "
            + Fore.BLUE
            + f"direc={cfg['direccion']} vars={cfg['vars']} modo={cfg['modo']}"
        )
    print(Fore.RESET + "=" * 50)

    return activos

def main():
    """Función principal que ejecuta el flujo del programa."""
    colorama.init()
    time.sleep(5)

    print(Style.BRIGHT + Fore.YELLOW + "Arrancando" + Fore.GREEN + " fv_ads.py")

    # --------------------------------------------------
    # Cargar desde Parametros_FV.py
    # --------------------------------------------------
    ads_config = cargar_parametros("ADS")
    ads_config = convertir_dict_a_list(ads_config)

    # filtrar ADS activos
    ads_activos = preparar_lista_ads_activos(ads_config)

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
