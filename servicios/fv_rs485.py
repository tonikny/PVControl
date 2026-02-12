# -*- coding: utf-8 -*-

# Versión 2024-05-26
#############################################
##  Libreria generica de captura RS485 RTU ##
#############################################

# Se llama desde el programa principal en donde se define el equipo, puerto etc junto con los registros a capturar

##################################################################

import sys
import time
import datetime
import json
import logging

import minimalmodbus
import colorama  # colores en ventana Terminal
from colorama import Fore, Back, Style

from helpers.gestor_parametros import GestorParametros
from helpers.gestor_bd import GestorBD
from helpers.gestor_logs import GestorLogs
from helpers.gestor_mqtt import GestorMQTT
from helpers.gestor_telegram import GestorTelegram
from helpers.control_servicio import controlar_servicio

colorama.init()


# Variables globales que se inicializarán en main()
log = None
gp = None
gestor_bd = None
gestor_mqtt = None
gestor_telegram = None

# Variables de configuración (se cargarán desde parámetros)
EQUIPO = {}
comandos = {}
orden_bytes = 0
simular_datos = 0

# Variables de estado
modbus = {}
t_recarga_parametros = 0
t_ultima_captura = {}
n_fallos_captura = {}
wh_placa = {}
wh_consumo = {}
flag_lectura = {}


def leer_registro(equipo, comando):
    """Lectura de comando en equipo."""
    reg = comandos[comando]['reg']
    dec = comandos[comando]['dec'] if 'dec' in comandos[comando] else 0
    tipo = comandos[comando]['tipo'] if 'tipo' in comandos[comando] else 'u16'
    offset = comandos[comando]['offset'] if 'offset' in comandos[comando] else 0
    fc = comandos[comando]['fc'] if 'fc' in comandos[comando] else 3
    
    d = -9999
    if tipo == 'u16':
        d = modbus[equipo].read_register(reg, 0, fc)
        if orden_bytes == 1:
            d = int.from_bytes(d.to_bytes(2, byteorder='little'))
        d = round(d * 10**-dec, dec)
    elif tipo == 's16':
        d = modbus[equipo].read_register(reg, dec, fc, True)
    elif tipo == 'u32':
        d = modbus[equipo].read_long(reg, fc, False, 0)
        d = round(d * 10**-dec, dec)
    
    if tipo == 'adaptar':
        d = modbus[equipo].read_register(reg, dec, fc)
    else:
        d += offset
    
    return d


def leer_registros(equipo):
    """Lectura múltiple de registros usando rangos."""
    global n_fallos_captura
    ee = 1000
    lectura = {}  # diccionario registro: valor..... ejemplo... {102: 5655, 103: 200}
    datos = {}    # diccionario comando: valor..... ejemplo... {'Vbat': 5655, 'Ibat': 200}
    
    try:
        for reg_ini, reg_fin in comandos['lectura_multiple']['rangos']:
            ee = 1010
            nreg = reg_fin - reg_ini + 1
            registros = list(range(reg_ini, reg_fin + 1))
            
            try:
                ee = 1020
                d = modbus[equipo].read_registers(reg_ini, nreg, 3) if simular_datos == 0 else [9999] * nreg
            except:
                ee = 1030
                log.error(f'Error lectura multiple reg_ini:{reg_ini},reg_fin:{reg_fin} -> nreg:{nreg}')
                error = True
                n_fallos_captura[equipo] += 1
            
            for i in range(nreg):
                lectura[registros[i]] = d[i]
            
            # interpretar lectura
            cmd = {}  # diccionario registro: clave en comandos,,ejem   {102: 'Vbat', 103: 'Ibat'}
            for c in comandos:
                if 'reg' in comandos[c]:
                    cmd[comandos[c]['reg']] = c
            
            for r in lectura:
                try:
                    if r not in cmd:
                        continue
                    comando = cmd[r]
                    grabar = comandos[comando]['grabar'] if 'grabar' in comandos[comando] else True
                    if not grabar:
                        continue
                    
                    valor = lectura[r]
                    if orden_bytes == 1:
                        valor = int.from_bytes(valor.to_bytes(2, byteorder='little'))
                    
                    dec = comandos[comando]['dec'] if 'dec' in comandos[comando] else 0
                    tipo = comandos[comando]['tipo'] if 'tipo' in comandos[comando] else 'u16'
                    offset = comandos[comando]['offset'] if 'offset' in comandos[comando] else 0
        
                    d = -9999
                    if tipo == 'u16':
                        d = round(valor * 10**-dec, dec)
                    elif tipo == 's16':
                        d = valor if valor < 32767 else valor - 65536
                        d = round(d * 10**-dec, dec)
                    elif tipo == 'u32':
                        valor_alto = lectura[r+1]
                        d = round((lectura[r+1] * 65536 + valor) * 10**-dec, dec)
                    
                    if tipo == 'adaptar':
                        ee = 1050
                        d = valor
                        ejecutar = '\n'.join(comandos[comando]['adaptar'])
                        ee = 1060
                        exec(ejecutar)
                    else:
                        ee = 1070
                        d += offset
                        datos[comando] = d
                        
                except Exception as error1:
                    log.error(f"Error {ee} en leer_registros({equipo})..comando={comando} {type(error1).__name__} - {error1}")
                    datos[comando] = -9999
                
    except:
        log.error(f'Equipo {equipo}: error {ee}...rango de lectura de registros mal definido en Parametros_FV.py')
    
    return datos


def listar_parametros(equipo):
    """Lista los parámetros del equipo y los envía por Telegram."""
    if True:
        msg = f'\U0001F4DF   <b>LISTA PARAMETROS {equipo}</b>\n'
        msg += ' =============================\n'
        nlineas = 0
        for c in comandos:
            nlineas += 1
            comandos1 = comandos[c].copy()
            if 'adaptar' in comandos1:
                del comandos1['adaptar']
            
            msg += f'\U0001F6A6<b>{c}</b> : {comandos1}\n'
            if c in ['ayuda', 'lectura_multiple']:
                msg += f"\n"
                continue
            try:
                d = leer_registro(equipo, c)
                
                tipo = comandos[c]['tipo'] if 'tipo' in comandos[c] else 'u16'
                
                if tipo == 'adaptar':
                    datos = {}
                    ejecutar = '\n'.join(comandos[c]['adaptar'])
                    exec(ejecutar)
                    d = datos[c]
                    
                msg += f"    ..... Valor Actual de <b>{c}={d}</b>\n\n"
                time.sleep(0.05)
            except:
                log.error(f'Error en leer_registro({equipo},{c})')
                time.sleep(1)
                msg += f'<b>...error lectura de {c}</b>\n'
            
            if gestor_telegram.esta_habilitado() and nlineas % 20 == 0:
                gestor_telegram.enviar_mensaje_seguro(msg)
                msg = ''
                
        if gestor_telegram.esta_habilitado():
            msg += ' =============================\n'
            gestor_telegram.enviar_mensaje_seguro(msg)
    
    return


def escribir_registro(equipo, mensaje):
    """Escribe un registro en el equipo."""
    MENSAJE = mensaje.upper()
    for c in comandos:
        ee = 30
        f = MENSAJE.find(c.upper())
        
        if f != -1:  # se encuentra la cadena
            ee = 40
            variable = mensaje[f:len(c)]
            
            try:
                d = leer_registro(equipo, c)
                
                valor = mensaje[len(c):].strip()
                ee = 50
                if len(valor) > 0:
                    if valor[0] == '=':
                        valor = valor[1:]
                    valor_n = float(valor)
                    escritura = True
                else:
                    escritura = False
                    
                ee = 60
                registro = comandos[c]['reg']
                msg = f'Valor registro {registro}...{variable}= {d} '
                if log.es_debug():
                    log.debug(msg)
                ee = 70
                
                if not comandos[c]['escritura']:
                    escritura = False
                    msg += f'\n Error {variable} no admite escritura'
                elif escritura:
                    if 'rango' not in comandos[c]:
                        comandos[c]['rango'] = [0, 65535]
                    if valor_n < comandos[c]['rango'][0] or valor_n > comandos[c]['rango'][1]:
                        escritura = False
                        msg += f'\n Error en valor {valor_n} fuera de rango admitido'
                        if log.es_debug():
                            log.debug(msg)
                        
                ee = 80
                if escritura:
                    decimales = comandos[c]['dec'] if 'dec' in comandos[c] else 0
                    modbus[equipo].write_register(registro, valor_n, decimales)
                     
                    msg += f'\nNuevo Valor-->{registro}...{variable}= {valor_n} '
                    if log.es_debug():
                        log.debug(msg)
                
                ee = 90
                if gestor_telegram.esta_habilitado():
                    gestor_telegram.enviar_mensaje_seguro(msg)
            except:
                log.error(f'Error {ee} en comando MQTT')
            
            return
        
        ee = 100
    
    try:
        msg = f'Comando {mensaje} no encontrado'
        ee = 110
        if gestor_telegram.esta_habilitado():
            gestor_telegram.enviar_mensaje_seguro(msg)
    except:
        log.error(f'Error {ee} en comando MQTT')
    
    return


def leer_equipo(equipo):
    """Bucle de lectura de cada equipo."""
    global n_fallos_captura
    
    t0 = time.time()
    nombre_equipo = equipo.upper()
    datos = {}  # inicializo diccionario
    error = False
    
    try:
        ee = 100
        lectura_multiple = comandos['lectura_multiple']['usar'] if 'lectura_multiple' in comandos else 0
        
        if lectura_multiple == 1:
            datos = leer_registros(equipo)
        else:
            for c in comandos:
                if c == 'ayuda':
                    continue
                if c == 'lectura_multiple':
                    continue
                
                grabar = comandos[c]['grabar'] if 'grabar' in comandos[c] else True
                if not grabar:
                    continue
                
                reg = comandos[c]['reg']
                dec = comandos[c]['dec'] if 'dec' in comandos[c] else 0
                tipo = comandos[c]['tipo'] if 'tipo' in comandos[c] else 'u16'
                offset = comandos[c]['offset'] if 'offset' in comandos[c] else 0
                fc = comandos[c]['fc'] if 'fc' in comandos[c] else 3
               
                ee = 110
                
                if tipo == 'adaptar':
                    ee = 120
                    d = modbus[equipo].read_register(reg, dec, fc)
                    ejecutar = '\n'.join(comandos[c]['adaptar'])
                    ee = 122
                    exec(ejecutar)
                else:
                    ee = 130
                    datos[c] = leer_registro(equipo, c)
        
        t1 = time.time()
        datos['tcaptura'] = round(t1-t0, 2)
        
    except Exception as error1:
        log.error(f"Error {ee} en leer_equipo({equipo})..comando={c} {type(error1).__name__} - {error1}")
        error = True
    
    t2 = time.time()
    ee = 200
    if log.es_debug():
        if equipo[-1] == '1':
            color = Style.BRIGHT + Fore.GREEN
        elif equipo[-1] == '2':
            color = Style.BRIGHT + Fore.YELLOW
        elif equipo[-1] == '3':
            color = Style.BRIGHT + Fore.MAGENTA
        else:
            color = Fore.RESET
        
        log.info(Fore.RESET + time.strftime("%Y-%m-%d %H:%M:%S") + color + f' -- {equipo}: {datos}')
        log.info('-' * 70)
    
    try:
        ee = 300
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        if not error:
            ee = 302
            datos['Nfallos'] = n_fallos_captura[equipo]
            
            gestor_bd.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)
            ee = 330
            
            if not log.es_debug():
                print(f'{nombre_equipo[-1]}', flush=True, end='')
        else:
            log.error(f'{tiempo} - Error {ee} en captura equipo {nombre_equipo}')
            
    except:
        log.error(Fore.RED + f'error {ee}, Grabacion tabla RAM equipos en {nombre_equipo}')


def main():
    """Función principal que ejecuta el flujo del programa."""
    global log, gp, gestor_bd, gestor_mqtt, gestor_telegram
    global modbus, t_recarga_parametros, t_ultima_captura
    global n_fallos_captura, wh_placa, wh_consumo, flag_lectura
    global nombre_equipo_rs485, EQUIPO, comandos, orden_bytes, simular_datos
    
    colorama.init(autoreset=True)
    time.sleep(2)
    
    # --------------------------------------------------
    # Comprobacion argumentos en comando
    # --------------------------------------------------
    global simular
    simular = 0
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
    
    log = GestorLogs(__name__, debug_level)
    log.info(Style.BRIGHT + Fore.YELLOW + "Arrancando" + Fore.GREEN + " fv_rs485.py")
    
    # --------------------------------------------------
    # Inicializar gestores
    # --------------------------------------------------
    gp = GestorParametros(check_interval=300)
    gestor_bd = GestorBD()
    
    try:
        gestor_telegram = GestorTelegram()
    except Exception as e:
        log.warning(f"No se pudo inicializar Telegram: {e}")
        gestor_telegram = GestorTelegram(usar_telegram=False)
    
    try:
        gestor_mqtt = GestorMQTT(depurar=log.es_debug())
    except Exception as e:
        log.warning(f"No se pudo inicializar MQTT: {e}")
        gestor_mqtt = None
    
    # --------------------------------------------------
    # Cargar configuración de equipos
    # --------------------------------------------------
    # Buscar argumento -NEQUIPO=<nombre_equipo> o usar valor por defecto
    nombre_equipo_rs485 = None
    for arg in sys.argv:
        if arg.startswith("-NEQUIPO="):
            nombre_equipo_rs485 = arg.split("=")[1]
            break
    
    if nombre_equipo_rs485 is None:
        log.error("Debe especificar el tipo de equipo con -NEQUIPO=<nombre>")
        log.error("Ejemplo: python3 fv_rs485.py -NEQUIPO=ANENJI")
        sys.exit(1)
    
    # Cargar configuración del equipo especificado
    try:
        EQUIPO = gp.leer_parametros(nombre_equipo_rs485)
        log.info(f"Configuración cargada para equipo: {nombre_equipo_rs485}")
    except Exception as e:
        log.error(f"No se encontró configuración para equipo '{nombre_equipo_rs485}': {e}")
        sys.exit(1)
    
    # Extraer comandos
    try:
        comandos = EQUIPO['COMANDOS']
        del EQUIPO['COMANDOS']
    except:
        log.warning("No se encontraron COMANDOS en la configuración del equipo")
        comandos = {}
    
    # Configurar orden de bytes
    try:
        orden_bytes_config = gp.leer_parametros("orden_bytes")
        orden_bytes = 1 if orden_bytes_config == 1 else 0
    except:
        orden_bytes = 0
    
    # Configurar simulación
    simular_datos = 1 if simular == 1 else 0
    
    if log.es_debug():
        log.debug(f"EQUIPO: {EQUIPO}")
        log.debug(f"orden_bytes: {orden_bytes}")
        log.debug(f"simular_datos: {simular_datos}")
    
    # Enviar mensaje de inicio
    if gestor_telegram.esta_habilitado():
        gestor_telegram.enviar_mensaje_inicio(nombre_equipo_rs485)
    
    # --------------------------------------------------
    # Control Ejecucion Servicio
    # --------------------------------------------------
    # Verificar si hay equipos activos
    equipos_activos = [e for e in EQUIPO if EQUIPO[e].get('usar', 0) == 1]
    hay_activos = len(equipos_activos) > 0
    
    log.info(f"Equipos RS485 activos: {len(equipos_activos)}")
    for eq in equipos_activos:
        log.info(f"  - {eq}")
    
    controlar_servicio("fv_rs485", hay_activos)
    
    # --------------------------------------------------
    # Configurar MQTT
    # --------------------------------------------------
    if gestor_mqtt:
        gestor_mqtt.suscribir_equipos(equipos_activos)
        if not gestor_mqtt.conectar():
            log.warning("No se pudo conectar al broker MQTT")
    
    # --------------------------------------------------
    # Bucle principal
    # --------------------------------------------------
    dia = time.strftime("%Y-%m-%d")
    t_recarga_parametros = time.time()
    t_ultima_captura = {}
    n_fallos_captura = {}
    wh_placa = {}
    wh_consumo = {}
    flag_lectura = {}
    
    # Inicializar contadores de fallos para equipos activos
    for e in equipos_activos:
        n_fallos_captura[e] = 0
    
    while True:
        ee = '10a'
        
        # Recargar parámetros periódicamente
        if time.time() - t_recarga_parametros > 300:
            t_recarga_parametros = time.time()
            if log.es_debug():
                log.debug(Fore.RED + 'recarga Parametros')
            try:
                # Recargar configuración del equipo
                equipo_nuevo = gp.leer_parametros(nombre_equipo_rs485)
                if equipo_nuevo:
                    global EQUIPO, comandos
                    EQUIPO = equipo_nuevo
                    try:
                        comandos = EQUIPO['COMANDOS']
                        del EQUIPO['COMANDOS']
                    except:
                        pass
                    
                    # Actualizar orden de bytes si cambió
                    global orden_bytes
                    try:
                        orden_bytes_config = gp.leer_parametros("orden_bytes")
                        orden_bytes = 1 if orden_bytes_config == 1 else 0
                    except:
                        orden_bytes = 0
                    
                    # Actualizar lista de equipos activos
                    equipos_activos = [e for e in EQUIPO if EQUIPO[e].get('usar', 0) == 1]
                    if gestor_mqtt:
                        gestor_mqtt.suscribir_equipos(equipos_activos)
                    
                    log.info("Configuración recargada exitosamente")
            except Exception as e:
                log.error(Fore.RED + f'ERROR en recarga Parametros: {e}')
        
        ee = '10b'
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")
        
        if dia_anterior != dia:  # cambio de dia
            n_fallos_captura = {}
            for e in equipos_activos:
                n_fallos_captura[e] = 0
            wh_placa = {}
            wh_consumo = {}
        
        ee = '10c'
        try:
            for e in EQUIPO:
                ee = '10d'
                if EQUIPO[e]['usar'] == 1:
                    ee = '10e'
                    
                    # Abrir conexión Modbus si aún no existe
                    if e not in modbus:
                        if log.es_debug():
                            log.debug(f"Abriendo conexion Modbus en {EQUIPO[e]['dev']} con id: {EQUIPO[e]['id_modbus']}")
                        modbus[e] = minimalmodbus.Instrument(EQUIPO[e]['dev'], EQUIPO[e]['id_modbus'])
                        modbus[e].serial.baudrate = EQUIPO[e]['baudrate'] if 'baudrate' in EQUIPO[e] else 9600
                        modbus[e].serial.bytesize = 8
                        modbus[e].serial.parity = minimalmodbus.serial.PARITY_NONE
                        modbus[e].serial.stopbits = 1
                        modbus[e].serial.timeout = 3
                        modbus[e].debug = False
                        modbus[e].mode = minimalmodbus.MODE_RTU
                        if log.es_debug():
                            log.debug('.... OK')
                    
                    n_fallos_captura[e] = 0
                    
                    # Procesar comandos MQTT pendientes
                    ee = '10e_10'
                    if gestor_mqtt and gestor_mqtt.hay_comandos_pendientes():
                        c_mqtt = gestor_mqtt.obtener_comando_pendiente()
                        ee = '10e_20'
                        if c_mqtt['comando'] in comandos['ayuda']:
                            ee = '10e_30'
                            if log.es_debug():
                                log.debug(f"Ejecutando Listar Parametros de equipo {c_mqtt['equipo']}")
                            listar_parametros(c_mqtt['equipo'])
                        else:
                            ee = '10e_40'
                            if log.es_debug():
                                log.debug(f"Ejecutando Lectura/Escritura {c_mqtt['comando']} en equipo {c_mqtt['equipo']}")
                            escribir_registro(c_mqtt['equipo'], c_mqtt['comando'])
                    
                    ee = '10e_50'
                    if e in t_ultima_captura.keys():
                        if time.time() - t_ultima_captura[e] > EQUIPO[e]['tiempo_captura']:
                            ee = '10f'
                            try:
                                leer_equipo(e)
                                t_ultima_captura[e] = time.time()
                            except Exception as error:
                                log.error(Fore.RED + f"Error {ee} en Bucle Principal... equipo {e}: {type(error).__name__} - {error}")
                                time.sleep(1)
                                continue
                    else:
                        t_ultima_captura[e] = time.time()
                        
                        # Comprobación que existe registro en tabla equipos
                        ee = '10g'
                        
                        try:
                            ee = '10h'
                            nombre_equipo = e.upper()
                            gestor_bd.insertar_equipo_si_falta(nombre_equipo)
                        except Exception as ex:
                            log.warning(f"Error insertando equipo {e}: {ex}")
                   
        except Exception as error1:
            log.error(f"Error {ee} en bucle principal {type(error1).__name__} - {error1}")
            log.error('.... se reinicia')
            gestor_bd.cerrar()
            sys.exit(1)
        
        time.sleep(0.1)


# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    main()
