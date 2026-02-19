#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión simplificada - basada en fv_ads_repo.py que funciona
# Sin LoggerMultiprocessing, sin Manager, sin Pipe - solo print y multiprocessing básico

from helpers.control_servicio import controlar_servicio
servicio = 'fv_ads'

import time, sys, os, json, multiprocessing, MySQLdb
import Adafruit_ADS1x15
import colorama
from colorama import Fore, Style
colorama.init()

from helpers.cargador_parametros import cargar_parametros, obtener_ads_activos

print(Style.BRIGHT + Fore.YELLOW + 'Arrancando' + Fore.GREEN + ' fv_ads_simple.py')

params = cargar_parametros()
lista_ads = obtener_ads_activos(params)

# Get DB credentials from params
servidor = params.get('servidor', 'localhost')
usuario = params.get('usuario', 'rpi')
clave = params.get('clave', 'fv')
basedatos = params.get('basedatos', 'control_solar')

print(f"ADS activos: {len(lista_ads)}")

DEBUG = 0
if '-p' in sys.argv: DEBUG = 100

def ADS_captura(ADS_index, ads_config):
    """Captura datos para un ADS específico - versión simple sin logger"""
    
    nombre_ADS = ads_config['id']
    direccion_ADS = ads_config['direccion']
    var_ADS = ads_config['vars']
    tmuestra_ADS = ads_config['tmuestra']
    rate_ADS = ads_config['rate']
    bucles_ADS = ads_config['bucles']
    gain_ADS = ads_config['gain']
    modo_ADS = ads_config['modo']
    res_ADS = ads_config['res']
    
    Ncapturas = 0
    time.sleep(0.02 * ADS_index)  # multiplexo un poco los distintos procesos

    if DEBUG >= 1:
        print()
        print(Fore.BLUE + '=' * 40 + f'Proceso{ADS_index}{nombre_ADS}' + '=' * 40)

    # Database connection
    db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      (nombre_ADS, '{}'))
        db.commit()
    except:
        print(Fore.RED + f'Registro RAM - clave = {nombre_ADS} ya creado')

    print(f'Activando ADS en direccion {direccion_ADS}')
    adc = Adafruit_ADS1x15.ADS1115(address=direccion_ADS, busnum=1)

    d_ads = {}
    ADS_modo = 'Disparado'

    while True:
        try:
            ee = '10'
            t0 = time.perf_counter()
            ERR_ADS = [0, 0, 0, 0]
            ee = '11'

            if ADS_modo == 'Disparado':
                ee = '30'
                for indice, modo in enumerate(modo_ADS, 0):
                    if modo == 1:
                        ee = '30a'
                        L_ADS = [adc.read_adc(indice, gain=gain_ADS[indice], data_rate=rate_ADS[indice]) 
                                 for j in range(bucles_ADS[indice])]
                    elif modo == 3:
                        ee = '30b'
                        indice1 = 0 if indice == 0 else 3
                        L_ADS = [adc.read_adc_difference(indice1, gain=gain_ADS[indice], data_rate=rate_ADS[indice]) 
                                 for j in range(bucles_ADS[indice])]
                    else:
                        continue

                    if modo != 0:
                        MED_ADS = sum(L_ADS) / bucles_ADS[indice]
                        d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                        ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            else:  # Continuo
                ee = '40'
                for indice, modo in enumerate(modo_ADS, 0):
                    if modo == 0:
                        continue
                    L_ADS = [0.0] * bucles_ADS[indice]
                    for i in range(bucles_ADS[indice]):
                        L_ADS[i] = adc.get_last_result()
                        time.sleep(1 / rate_ADS[indice])

                    MED_ADS = sum(L_ADS) / bucles_ADS[indice]
                    d_ads[var_ADS[indice]] = round(MED_ADS * 0.000125 * res_ADS[indice] / gain_ADS[indice], 3)
                    ERR_ADS[indice] = max(L_ADS) - min(L_ADS)

            ee = '50'
            t1 = (time.perf_counter() - t0) * 1000

            if DEBUG >= 1:
                t = str(round(time.time(), 3))
                print(f'{t[-6:]}: {nombre_ADS}-Modo={modo_ADS} {str(ERR_ADS):16}-Captura = {d_ads}')

            ee = '60'
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            salida = json.dumps(d_ads)
            sql = f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{nombre_ADS.upper()}'"
            cursor.execute(sql)
            db.commit()

            t2 = (time.perf_counter() - t0) * 1000
            ee = '70'

            if DEBUG >= 2:
                print(f'{time.time():.5f} / {nombre_ADS}: t1={t1:6.1f}-t2={t2:6.1f}')

            t3 = (time.perf_counter() - t0)
            time.sleep(max(tmuestra_ADS - t3, 0))
            Ncapturas += 1

        except Exception as e:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f'{tiempo} - Error {ee} en {nombre_ADS}....se reinicia')
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    # Control execution service
    hay_ads_activos = len(lista_ads)
    controlar_servicio(servicio, hay_ads_activos > 0)

    print(Fore.RESET + '=' * 50)
    print(Fore.BLUE + 'ADS_activos=')
    for ads in lista_ads:
        print(Fore.RED + f' -{ads["id"]}=' + Fore.BLUE +
              f' direc={ads["direccion"]} - var= {ads["vars"]} - modo={ads["modo"]}')
    print(Fore.RESET + '=' * 50)
    time.sleep(5)

    # Start processes - simple approach like fv_ads_repo.py
    for i, ads in enumerate(lista_ads):
        multiprocessing.Process(target=ADS_captura, args=(i, ads), name=f'p_{ads["id"]}').start()

    Procesos = multiprocessing.active_children()
    print('Procesos activos=', Procesos)

    # Monitor loop - simple is_alive() check
    while True:
        try:
            for p in Procesos:
                if not p.is_alive():
                    print(f'Proceso {p} parado {p.name}')
                    time.sleep(3)
                    # Extract index from process name and restart
                    ads_name = p.name.replace('p_', '')
                    for i, ads in enumerate(lista_ads):
                        if ads['id'] == ads_name:
                            multiprocessing.Process(target=ADS_captura, args=(i, ads), name=f'p_{ads_name}').start()
                            break
                    Procesos = multiprocessing.active_children()
                    print(Procesos)

            time.sleep(1)

        except KeyboardInterrupt:
            time.sleep(1)
            print(Fore.RED + '=' * 50)
            print('Finalizando fv_ads_simple.py.......')
            for p in Procesos:
                print(f'     ....Terminando hilo..{p}')
                p.terminate()
                time.sleep(1)
            sys.exit()
