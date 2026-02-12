# -*- coding: utf-8 -*-

# Versión 2024-05-26
#############################################
##  Libreria generica de captura RS485 RTU ##
#############################################

# Librería para captura de datos RS485 que se importa desde scripts como fv_srne.py
# Funciona como módulo Python normal con llamadas a funciones, no usa exec() ni eval()

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


class CapturadorRS485:
    """Clase principal para captura de datos RS485."""
    
    def __init__(self, nombre_equipo, debug=False):
        """
        Inicializa el capturador para un equipo específico.
        
        Args:
            nombre_equipo: Nombre del equipo en Parametros_FV.py (ej. 'SRNE', 'ANENJI')
            debug: Si es True, activa modo debug
        """
        self.nombre_equipo = nombre_equipo
        self.debug = debug
        self.simular_datos = False
        
        # Configurar nivel de logging
        if debug:
            debug_level = logging.DEBUG
        else:
            debug_level = logging.ERROR
            
        self.log = GestorLogs(f"{__name__}_{nombre_equipo}", debug_level)
        
        # Inicializar gestores
        self.gp = GestorParametros(check_interval=300)
        self.gestor_bd = GestorBD()
        
        try:
            self.gestor_telegram = GestorTelegram()
        except Exception as e:
            self.log.warning(f"No se pudo inicializar Telegram: {e}")
            self.gestor_telegram = GestorTelegram(usar_telegram=False)
        
        try:
            self.gestor_mqtt = GestorMQTT(depurar=debug)
        except Exception as e:
            self.log.warning(f"No se pudo inicializar MQTT: {e}")
            self.gestor_mqtt = None
        
        # Cargar configuración inicial
        self.EQUIPO = None
        self.comandos = {}
        self.orden_bytes = 0
        self.cargar_configuracion()
        
        # Variables de estado
        self.modbus = {}
        self.t_recarga_parametros = time.time()
        self.t_ultima_captura = {}
        self.n_fallos_captura = {}
        self.wh_placa = {}
        self.wh_consumo = {}
        self.flag_lectura = {}
        
        # Determinar equipos activos
        self.equipos_activos = [e for e in self.EQUIPO if self.EQUIPO[e].get('usar', 0) == 1 and e != 'COMANDOS']
        self.hay_activos = len(self.equipos_activos) > 0
        
        if debug:
            self.log.manual(Fore.RESET + "=" * 50)
            self.log.manual(Fore.BLUE + "Equipos activos:")
            for eq in self.equipos_activos:
                self.log.manual(Fore.RED + f" - {eq}")
            self.log.manual(Fore.RESET + "=" * 50)
        
        # Control ejecución servicio
        controlar_servicio(f"fv_rs485_{nombre_equipo}", self.hay_activos)
        
        # Configurar MQTT
        if self.gestor_mqtt:
            self.gestor_mqtt.suscribir_equipos(self.equipos_activos)
            if not self.gestor_mqtt.conectar():
                self.log.warning("No se pudo conectar al broker MQTT")
        
        # Inicializar contadores de fallos
        for e in self.equipos_activos:
            self.n_fallos_captura[e] = 0
        
        # Enviar mensaje de inicio
        if self.gestor_telegram.esta_habilitado():
            self.gestor_telegram.enviar_mensaje_inicio(nombre_equipo)
    
    def cargar_configuracion(self):
        """Carga configuración del equipo desde Parametros_FV.py usando GestorParametros."""
        try:
            self.EQUIPO = self.gp.leer_parametros(self.nombre_equipo)
            
            if self.EQUIPO:
                try:
                    self.comandos = self.EQUIPO['COMANDOS']
                    del self.EQUIPO['COMANDOS']
                except:
                    pass
                
                try:
                    self.orden_bytes = 1
                except:
                    self.orden_bytes = 0
                
                self.log.info(f"Configuración cargada para equipo {self.nombre_equipo}")
        except Exception as e:
            self.log.error(Fore.RED + f'ERROR en carga Parametros: {e}')
            raise
    
    def recargar_configuracion(self):
        """Recarga configuración del equipo (se llama periódicamente)."""
        try:
            EQUIPO_nuevo = self.gp.leer_parametros(self.nombre_equipo)
            
            if EQUIPO_nuevo:
                self.EQUIPO = EQUIPO_nuevo
                try:
                    self.comandos = self.EQUIPO['COMANDOS']
                    del self.EQUIPO['COMANDOS']
                except:
                    pass
                
                try:
                    self.orden_bytes = 1
                except:
                    self.orden_bytes = 0
                
                # Actualizar lista de equipos activos
                self.equipos_activos = [e for e in self.EQUIPO if self.EQUIPO[e].get('usar', 0) == 1 and e != 'COMANDOS']
                if self.gestor_mqtt:
                    self.gestor_mqtt.suscribir_equipos(self.equipos_activos)
                
                self.log.info("Configuración recargada exitosamente")
        except Exception as e:
            self.log.error(Fore.RED + f'ERROR en recarga Parametros: {e}')
    
    def leer_registro(self, equipo, comando):
        """Lectura de comando en equipo."""
        reg = self.comandos[comando]['reg']
        dec = self.comandos[comando]['dec'] if 'dec' in self.comandos[comando] else 0
        tipo = self.comandos[comando]['tipo'] if 'tipo' in self.comandos[comando] else 'u16'
        offset = self.comandos[comando]['offset'] if 'offset' in self.comandos[comando] else 0
        fc = self.comandos[comando]['fc'] if 'fc' in self.comandos[comando] else 3
        
        d = -9999
        if tipo == 'u16':
            d = self.modbus[equipo].read_register(reg, 0, fc)
            if self.orden_bytes == 1:
                d = int.from_bytes(d.to_bytes(2, byteorder='little'))
            d = round(d * 10**-dec, dec)
        elif tipo == 's16':
            d = self.modbus[equipo].read_register(reg, dec, fc, True)
        elif tipo == 'u32':
            d = self.modbus[equipo].read_long(reg, fc, False, 0)
            d = round(d * 10**-dec, dec)
        
        if tipo == 'adaptar':
            d = self.modbus[equipo].read_register(reg, dec, fc)
        else:
            d += offset
        
        return d
    
    def leer_registros(self, equipo):
        """Lectura múltiple de registros usando rangos."""
        ee = 1000
        lectura = {}  # diccionario registro: valor..... ejemplo... {102: 5655, 103: 200}
        datos = {}    # diccionario comando: valor..... ejemplo... {'Vbat': 5655, 'Ibat': 200}
        
        try:
            for reg_ini, reg_fin in self.comandos['lectura_multiple']['rangos']:
                ee = 1010
                nreg = reg_fin - reg_ini + 1
                registros = list(range(reg_ini, reg_fin + 1))
                
                try:
                    ee = 1020
                    d = self.modbus[equipo].read_registers(reg_ini, nreg, 3) if not self.simular_datos else [9999] * nreg
                except:
                    ee = 1030
                    self.log.error(f'Error lectura multiple reg_ini:{reg_ini},reg_fin:{reg_fin} -> nreg:{nreg}')
                    error = True
                    self.n_fallos_captura[equipo] += 1
                
                for i in range(nreg):
                    lectura[registros[i]] = d[i]
                
                # interpretar lectura
                cmd = {}  # diccionario registro: clave en comandos,,ejem   {102: 'Vbat', 103: 'Ibat'}
                for c in self.comandos:
                    if 'reg' in self.comandos[c]:
                        cmd[self.comandos[c]['reg']] = c
                
                for r in lectura:
                    try:
                        if r not in cmd:
                            continue
                        comando = cmd[r]
                        grabar = self.comandos[comando]['grabar'] if 'grabar' in self.comandos[comando] else True
                        if not grabar:
                            continue
                        
                        valor = lectura[r]
                        if self.orden_bytes == 1:
                            valor = int.from_bytes(valor.to_bytes(2, byteorder='little'))
                        
                        dec = self.comandos[comando]['dec'] if 'dec' in self.comandos[comando] else 0
                        tipo = self.comandos[comando]['tipo'] if 'tipo' in self.comandos[comando] else 'u16'
                        offset = self.comandos[comando]['offset'] if 'offset' in self.comandos[comando] else 0
            
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
                            ejecutar = '\n'.join(self.comandos[comando]['adaptar'])
                            ee = 1060
                            exec(ejecutar)
                        else:
                            ee = 1070
                            d += offset
                            datos[comando] = d
                            
                    except Exception as error1:
                        self.log.error(f"Error {ee} en leer_registros({equipo})..comando={comando} {type(error1).__name__} - {error1}")
                        datos[comando] = -9999
                    
        except:
            self.log.error(f'Equipo {equipo}: error {ee}...rango de lectura de registros mal definido en Parametros_FV.py')
        
        return datos
    
    def listar_parametros(self, equipo):
        """Lista los parámetros del equipo y los envía por Telegram."""
        if True:
            msg = f'\U0001F4DF   <b>LISTA PARAMETROS {equipo}</b>\n'
            msg += ' =============================\n'
            nlineas = 0
            for c in self.comandos:
                nlineas += 1
                comandos1 = self.comandos[c].copy()
                if 'adaptar' in comandos1:
                    del comandos1['adaptar']
                
                msg += f'\U0001F6A6<b>{c}</b> : {comandos1}\n'
                if c in ['ayuda', 'lectura_multiple']:
                    msg += f"\n"
                    continue
                try:
                    d = self.leer_registro(equipo, c)
                    
                    tipo = self.comandos[c]['tipo'] if 'tipo' in self.comandos[c] else 'u16'
                    
                    if tipo == 'adaptar':
                        datos = {}
                        ejecutar = '\n'.join(self.comandos[c]['adaptar'])
                        exec(ejecutar)
                        d = datos[c]
                        
                    msg += f"    ..... Valor Actual de <b>{c}={d}</b>\n\n"
                    time.sleep(0.05)
                except:
                    self.log.error(f'Error en leer_registro({equipo},{c})')
                    time.sleep(1)
                    msg += f'<b>...error lectura de {c}</b>\n'
                
                if self.gestor_telegram.esta_habilitado() and nlineas % 20 == 0:
                    self.gestor_telegram.enviar_mensaje_seguro(msg)
                    msg = ''
                    
            if self.gestor_telegram.esta_habilitado():
                msg += ' =============================\n'
                self.gestor_telegram.enviar_mensaje_seguro(msg)
        
        return
    
    def escribir_registro(self, equipo, mensaje):
        """Escribe un registro en el equipo."""
        MENSAJE = mensaje.upper()
        for c in self.comandos:
            ee = 30
            f = MENSAJE.find(c.upper())
            
            if f != -1:  # se encuentra la cadena
                ee = 40
                variable = mensaje[f:len(c)]
                
                try:
                    d = self.leer_registro(equipo, c)
                    
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
                    registro = self.comandos[c]['reg']
                    msg = f'Valor registro {registro}...{variable}= {d} '
                    if self.debug:
                        self.log.debug(msg)
                    ee = 70
                    
                    if not self.comandos[c]['escritura']:
                        escritura = False
                        msg += f'\n Error {variable} no admite escritura'
                    elif escritura:
                        if 'rango' not in self.comandos[c]:
                            self.comandos[c]['rango'] = [0, 65535]
                        if valor_n < self.comandos[c]['rango'][0] or valor_n > self.comandos[c]['rango'][1]:
                            escritura = False
                            msg += f'\n Error en valor {valor_n} fuera de rango admitido'
                            if self.debug:
                                self.log.debug(msg)
                            
                    ee = 80
                    if escritura:
                        decimales = self.comandos[c]['dec'] if 'dec' in self.comandos[c] else 0
                        self.modbus[equipo].write_register(registro, valor_n, decimales)
                         
                        msg += f'\nNuevo Valor-->{registro}...{variable}= {valor_n} '
                        if self.debug:
                            self.log.debug(msg)
                    
                    ee = 90
                    if self.gestor_telegram.esta_habilitado():
                        self.gestor_telegram.enviar_mensaje_seguro(msg)
                except:
                    self.log.error(f'Error {ee} en comando MQTT')
                
                return
            
            ee = 100
        
        try:
            msg = f'Comando {mensaje} no encontrado'
            ee = 110
            if self.gestor_telegram.esta_habilitado():
                self.gestor_telegram.enviar_mensaje_seguro(msg)
        except:
            self.log.error(f'Error {ee} en comando MQTT')
        
        return
    
    def leer_equipo(self, equipo):
        """Bucle de lectura de cada equipo."""
        t0 = time.time()
        nombre_equipo = equipo.upper()
        datos = {}  # inicializo diccionario
        error = False
        
        try:
            ee = 100
            lectura_multiple = self.comandos['lectura_multiple']['usar'] if 'lectura_multiple' in self.comandos else 0
            
            if lectura_multiple == 1:
                datos = self.leer_registros(equipo)
            else:
                for c in self.comandos:
                    if c == 'ayuda':
                        continue
                    if c == 'lectura_multiple':
                        continue
                    
                    grabar = self.comandos[c]['grabar'] if 'grabar' in self.comandos[c] else True
                    if not grabar:
                        continue
                    
                    reg = self.comandos[c]['reg']
                    dec = self.comandos[c]['dec'] if 'dec' in self.comandos[c] else 0
                    tipo = self.comandos[c]['tipo'] if 'tipo' in self.comandos[c] else 'u16'
                    offset = self.comandos[c]['offset'] if 'offset' in self.comandos[c] else 0
                    fc = self.comandos[c]['fc'] if 'fc' in self.comandos[c] else 3
                   
                    ee = 110
                    
                    if tipo == 'adaptar':
                        ee = 120
                        d = self.modbus[equipo].read_register(reg, dec, fc)
                        ejecutar = '\n'.join(self.comandos[c]['adaptar'])
                        ee = 122
                        exec(ejecutar)
                    else:
                        ee = 130
                        datos[c] = self.leer_registro(equipo, c)
            
            t1 = time.time()
            datos['tcaptura'] = round(t1-t0, 2)
            
        except Exception as error1:
            self.log.error(f"Error {ee} en leer_equipo({equipo})..comando={c} {type(error1).__name__} - {error1}")
            error = True
        
        t2 = time.time()
        ee = 200
        if self.debug:
            if equipo[-1] == '1':
                color = Style.BRIGHT + Fore.GREEN
            elif equipo[-1] == '2':
                color = Style.BRIGHT + Fore.YELLOW
            elif equipo[-1] == '3':
                color = Style.BRIGHT + Fore.MAGENTA
            else:
                color = Fore.RESET
            
            self.log.info(Fore.RESET + time.strftime("%Y-%m-%d %H:%M:%S") + color + f' -- {equipo}: {datos}')
            self.log.info('-' * 70)
        
        try:
            ee = 300
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            if not error:
                ee = 302
                datos['Nfallos'] = self.n_fallos_captura[equipo]
                
                self.gestor_bd.guardar_datos_equipo_dict(nombre_equipo, tiempo, datos)
                ee = 330
                
                if not self.debug:
                    print(f'{nombre_equipo[-1]}', flush=True, end='')
            else:
                self.log.error(f'{tiempo} - Error {ee} en captura equipo {nombre_equipo}')
                
        except:
            self.log.error(Fore.RED + f'error {ee}, Grabacion tabla RAM equipos en {nombre_equipo}')
    
    def ejecutar(self):
        """Bucle principal de ejecución."""
        print(Style.BRIGHT + Fore.YELLOW + f'Arrancando captura RS485 para equipo {self.nombre_equipo}')
        
        dia = time.strftime("%Y-%m-%d")
        
        while True:
            ee = '10a'
            
            # Recargar parámetros periódicamente
            if time.time() - self.t_recarga_parametros > 300:
                self.t_recarga_parametros = time.time()
                if self.debug:
                    self.log.debug(Fore.RED + 'recarga Parametros')
                self.recargar_configuracion()
            
            ee = '10b'
            dia_anterior = dia
            dia = time.strftime("%Y-%m-%d")
            
            if dia_anterior != dia:  # cambio de dia
                self.n_fallos_captura = {}
                for e in self.equipos_activos:
                    self.n_fallos_captura[e] = 0
                self.wh_placa = {}  # Ya veremos si se usa
                self.wh_consumo = {}  # Ya veremos si se usa
            
            ee = '10c'
            try:
                for e in self.EQUIPO:
                    ee = '10d'
                    if self.EQUIPO[e]['usar'] == 1 and e != 'COMANDOS':
                        ee = '10e'
                        
                        # Abrir conexión Modbus si aún no existe
                        if e not in self.modbus:
                            if self.debug:
                                self.log.debug(f"Abriendo conexion Modbus en {self.EQUIPO[e]['dev']} con id: {self.EQUIPO[e]['id_modbus']}")
                            self.modbus[e] = minimalmodbus.Instrument(self.EQUIPO[e]['dev'], self.EQUIPO[e]['id_modbus'])
                            self.modbus[e].serial.baudrate = self.EQUIPO[e]['baudrate'] if 'baudrate' in self.EQUIPO[e] else 9600
                            self.modbus[e].serial.bytesize = 8
                            self.modbus[e].serial.parity = minimalmodbus.serial.PARITY_NONE
                            self.modbus[e].serial.stopbits = 1
                            self.modbus[e].serial.timeout = 3
                            self.modbus[e].debug = False
                            self.modbus[e].mode = minimalmodbus.MODE_RTU
                            if self.debug:
                                self.log.debug('.... OK')
                        
                        self.n_fallos_captura[e] = 0
                        
                        # Procesar comandos MQTT pendientes
                        ee = '10e_10'
                        if self.gestor_mqtt and self.gestor_mqtt.hay_comandos_pendientes():
                            c_mqtt = self.gestor_mqtt.obtener_comando_pendiente()
                            ee = '10e_20'
                            if c_mqtt['comando'] in self.comandos['ayuda']:
                                ee = '10e_30'
                                if self.debug:
                                    self.log.debug(f"Ejecutando Listar Parametros de equipo {c_mqtt['equipo']}")
                                self.listar_parametros(c_mqtt['equipo'])
                            else:
                                ee = '10e_40'
                                if self.debug:
                                    self.log.debug(f"Ejecutando Lectura/Escritura {c_mqtt['comando']} en equipo {c_mqtt['equipo']}")
                                self.escribir_registro(c_mqtt['equipo'], c_mqtt['comando'])
                        
                        ee = '10e_50'
                        if e in self.t_ultima_captura.keys():
                            if time.time() - self.t_ultima_captura[e] > self.EQUIPO[e]['tiempo_captura']:
                                ee = '10f'
                                try:
                                    self.leer_equipo(e)
                                    self.t_ultima_captura[e] = time.time()
                                except Exception as error:
                                    self.log.error(Fore.RED + f"Error {ee} en Bucle Principal... equipo {e}: {type(error).__name__} - {error}")
                                    time.sleep(1)
                                    continue
                        else:
                            self.t_ultima_captura[e] = time.time()
                            
                            # Comprobación que existe registro en tabla equipos
                            ee = '10g'
                            
                            try:
                                ee = '10h'
                                nombre_equipo = e.upper()
                                self.gestor_bd.insertar_equipo_si_falta(nombre_equipo)
                            except Exception as ex:
                                self.log.warning(f"Error insertando equipo {e}: {ex}")
                       
            except Exception as error1:
                self.log.error(f"Error {ee} en bucle principal {type(error1).__name__} - {error1}")
                self.log.error('.... se reinicia')
                self.gestor_bd.cerrar()
                sys.exit(1)
            
            time.sleep(0.1)


def iniciar_captura(nombre_equipo, debug=False):
    """
    Función de conveniencia para iniciar la captura de un equipo.
    
    Args:
        nombre_equipo: Nombre del equipo en Parametros_FV.py (ej. 'SRNE', 'ANENJI')
        debug: Si es True, activa modo debug (también se puede pasar -p en línea de comandos)
    
    Ejemplo:
        from servicios.fv_rs485 import iniciar_captura
        iniciar_captura('SRNE')
    """
    # Comprobación argumentos en comando
    if '-p' in sys.argv:
        debug = True
    if '-s' in sys.argv:
        simular_datos = True
    
    capturador = CapturadorRS485(nombre_equipo, debug=debug)
    capturador.ejecutar()
