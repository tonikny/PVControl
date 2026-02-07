import time
import sys
import multiprocessing

# from smbus import SMBus
import smbus
import Adafruit_ADS1x15  # Import the ADS1x15 module.

import colorama  # colores en ventana Terminal
from colorama import Fore, Style
from helpers.cargar_parametros import cargar_parametros, han_cambiado_parametros
from helpers.gestor_bd import GestorBD
from fv_control_servicio import controlar_servicio

colorama.init()

print(Style.BRIGHT + Fore.YELLOW + "Arrancando" + Fore.GREEN + " fv_ads.py")

##### Parametros_FV.py (lo que se indique en el archivo Parametros.py tiene prevalencia sobre lo aqui indicado) ################
###

# --------------------------------------------------
# Load Parametros_FV.py
# --------------------------------------------------

ads_config = cargar_parametros("ADS")

# --------------------------------------------------
# Control Ejecucion Servicio
# --------------------------------------------------

# Verificar si hay ADS activos - pasar booleano en lugar del dict completo
hay_ads_activas = sum(1 for v in ads_config.values() if v.get("usar", False)) > 0
controlar_servicio("fv_ads", hay_ads_activas)

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

bus = smbus.SMBus(1)  # Activo Bus I2C para ADS o PCF


def leer_adc(callable_fn, ads_name, delay=0.005):
    try:
        return callable_fn()
    except OSError as e:
        if e.errno not in (5, 121):
            print("OSError", e)
            raise
        print(f"Error lectura {ads_name}")
        time.sleep(delay)


# --------------------------------------------------
# Captura ADS
# --------------------------------------------------


def ADS_captura(ads_name, ads_idx):
    ads_actual = ads_config[ads_name]
    Ncapturas = 0
    ee = 0
    
    time.sleep(0.02 * ads_idx)  # multiplexo un poco los distintos procesos

    if DEBUG >= 1:
        print(Fore.BLUE + "=" * 40, "Proceso", ads_name, "=" * 40)

    gestor = GestorBD()
    existe = not gestor.insertar_equipo_si_falta(ads_name)
    if existe:
        print(Fore.RED + f"Registro RAM - clave = {ads_name} ya creado")

    print(f"Activando ADS en direccion {ads_actual['direccion']}")
    adc = Adafruit_ADS1x15.ADS1115(address=ads_actual["direccion"], busnum=1)

    d_ads = {}
    ADS_modo = "Disparado"
    primera_ejecucion = True

    while True:
        try:
            ee = "10"
            t0 = time.perf_counter()
            tp0 = time.process_time()
            ERR_ADS = [0, 0, 0, 0]  # Error bruto capturas ADS
            ee = "11"
            # ---------------- Reload config ----------------
            if han_cambiado_parametros() or primera_ejecucion:  # recargo Parametros_FV.py si hay cambios o es la primera vez
                ee = "20"
                if DEBUG >= 1:
                    print(
                        Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S"),
                        f" -- Leyendo Parametros_FV.py para {ads_name} - Capturas={Ncapturas}",
                    )
                Ncapturas = 0
                try:
                    ads_config_v = cargar_parametros("ADS")
                    ads_actual = ads_config_v[ads_name]
                except:
                    print("Error en Parametros_FV.py")

                primera_ejecucion = False
                ee = "20a"

                ADS_modo = "Disparado"  # valor por defecto
                if DEBUG >= 1:
                    print(Fore.BLUE + f"Modo {ads_name} = " + Fore.GREEN, end="")

                for i, modo in enumerate(ads_actual["modo"]):
                    ee = "20b"
                    if modo == 2:
                        ee = "20c"
                        adc.start_adc(i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i])
                        ee = "20d"
                        ADS_modo = "Continuo"
                        if DEBUG >= 1:
                            print(f"entrada A{i} : ", end="")
                        break
                    elif modo == 4:
                        ee = "20d"
                        diff = 0 if i == 0 else 3
                        adc.start_adc_difference(
                            diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                        )
                        ADS_modo = "Continuo_Diferencial"
                        if DEBUG >= 1:
                            print(f"entrada A{i} : ", end="")
                        break

            ee = 30.1
            ee = 30.2

            # ---------------- Captura ----------------
            if ADS_modo == "Disparado":
                ee = "30"
                for i, modo in enumerate(ads_actual["modo"]):
                    L_ADS = []
                    if modo == 1:
                        ee = "30a"
                        # L_ADS = [
                        #     adc.read_adc(i, gain=ads_actual['gain'][i], data_rate=ads_actual['rate'][i])
                        #     for _ in range(ads_actual['bucles'][i])
                        # ]
                        for _ in range(ads_actual["bucles"][i]):
                            val = leer_adc(
                                lambda: adc.read_adc(
                                    i, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                                ),
                                ads_name,
                            )
                            if val is not None:
                                L_ADS.append(val)
                    elif modo == 3:  # Diferencial
                        ee = "30b"
                        diff = 0 if i == 0 else 3
                        # L_ADS = [
                        #     adc.read_adc_difference(diff, gain=ads_actual['gain'][i], data_rate=ads_actual['rate'][i])
                        #     for _ in range(ads_actual['bucles'][i])
                        # ]
                        for _ in range(ads_actual["bucles"][i]):
                            val = leer_adc(
                                lambda: adc.read_adc_difference(
                                    diff, gain=ads_actual["gain"][i], data_rate=ads_actual["rate"][i]
                                ),
                                ads_name,
                            )
                            if val is not None:
                                L_ADS.append(val)

                    else:
                        continue
                    ee = "30c"
                    # print (f'{L_ADS}', end='')

                    if modo != 0:
                        ee = "30d"
                        # MED_ADS = sum(L_ADS) / len(L_ADS) if len(L_ADS) > 0 else 0 # Media
                        MED_ADS = sorted(L_ADS)[len(L_ADS) // 2]  # Mediana
                        ee = "31"

                        var_name = ads_actual["vars"][i]
                        if not var_name:
                            continue
                        ee = 32
                        d_ads[var_name] = round(
                            MED_ADS * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                        )
                        ee = 33
                        ERR_ADS[i] = max(L_ADS) - min(L_ADS)
                        ee = 34
                        if DEBUG >= 100:
                            print(
                                f"L_ADS-A{i}={L_ADS} - {MED_ADS} "
                                f"Err:{ERR_ADS[i]}- {var_name}={d_ads[var_name]}"
                            )

            else:  # Continuo o continuo diferencial
                ee = "40"
                for i, modo in enumerate(ads_actual["modo"]):
                    n = ads_actual["bucles"][i]
                    rate = ads_actual["rate"][i]

                    L_ADS = [0.0] * n
                    for i in range(n):
                        L_ADS[i] = adc.get_last_result()
                        time.sleep(1 / rate)

                    MED_ADS = sum(L_ADS) / n

                    var_name = ads_actual["vars"][i]
                    if not var_name:
                        continue

                    d_ads[var_name] = round(
                        MED_ADS * 0.000125 * ads_actual["res"][i] / ads_actual["gain"][i], 3
                    )

                    ERR_ADS[i] = max(L_ADS) - min(L_ADS)

                    if DEBUG >= 100:
                        print(
                            f"L_ADS-A{i}={L_ADS}-{MED_ADS} "
                            f"Err:{ERR_ADS} - {var_name}={d_ads[var_name]}"
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
                    f"{t[-6:]}: {ads_name}-Modo={ads_actual['modo']} {str(ERR_ADS):16}-Captura = ",
                    d_ads,
                )

            ee = "60"
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

            gestor.guardar_datos_equipo_dict(ads_name, tiempo, d_ads)

            t2 = (time.perf_counter() - t0) * 1000
            tp2 = (time.process_time() - tp0) * 1000

            ee = "70"

            if DEBUG >= 2:
                print(
                    f"{time.time():.5f} / {ads_name}: "
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
                        f"- {ads_actual['modo']} entrada {ads_name}",
                    )

            ee = "80"
            if DEBUG >= 100:
                print(Fore.CYAN + "*" * 80)
                print("*" * 80 + Fore.RESET)
            # ---------------- Timing ----------------
            t3 = time.perf_counter() - t0
            time.sleep(max(ads_actual["tmuestra"] - t3, 0))
            Ncapturas += 1

        except Exception as e:
            print(
                Fore.RED
                + f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Error {ee} en {ads_name}: {repr(e)}"
            )
            print(f"{ads_name}....se reinicia el proceso de captura del {ads_name}")
            sys.exit(1)


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    if "-ADS1" in sys.argv:  # fuerzo solo ADS1
        for name, cfg in ads_config.items():
            cfg["usar"] = name == "ADS1"
    elif "-ADS4" in sys.argv:  # fuerzo solo ADS4
        for name, cfg in ads_config.items():
            cfg["usar"] = name == "ADS4"

    ADS_activos = [name for name, cfg in ads_config.items() if cfg.get("usar")]

    print(Fore.RESET + "=" * 50)
    print(Fore.BLUE + "ADS_activos=")
    for name in ADS_activos:
        cfg = ads_config[name]
        print(
            Fore.RED
            + f" -{name} "
            + Fore.BLUE
            + f"direc={cfg['direccion']} vars={cfg['vars']} modo={cfg['modo']}"
        )
    print(Fore.RESET + "=" * 50)

    time.sleep(5)

    # Arrancando procesos
    for idx, name in enumerate(ADS_activos):
        multiprocessing.Process(
            target=ADS_captura, args=(name, idx), name=f"p_{name}"
        ).start()

    Procesos = multiprocessing.active_children()
    print("Procesos activos=", Procesos)

    # Bucle
    while True:
        try:
            for p in Procesos:
                if not p.is_alive():
                    print(f"Proceso {p} parado {p.name}")
                    time.sleep(3)
                    ads_name = p.name[2:]
                    idx = ADS_activos.index(ads_name)
                    multiprocessing.Process(
                        target=ADS_captura, args=(ads_name, idx), name=f"p_{ads_name}"
                    ).start()
                    Procesos = multiprocessing.active_children()

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            print()
            print(Fore.RED + "=" * 50)
            print("Finalizando fv_ads.py...")
            for p in Procesos:
                print(f"     ....Terminando hilo..{p}")
                p.terminate()
                time.sleep(1)
            sys.exit()
