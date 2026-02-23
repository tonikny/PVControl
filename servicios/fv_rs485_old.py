#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_rs485.py - Captura de datos RS485 Modbus RTU para PVControl+

Características:
- Logger para mensajes de depuración
- GestorBD para acceso a base de datos
- GestorProcesos para gestión de procesos
- Gestión de servicios externa
- Clase CapturadorRS485 específica para dispositivos RS485
- Soporte para múltiples equipos (SRNE, ANENJI, etc.)
- MQTT para comandos remotos
- Telegram para notificaciones

Uso:
    python3 fv_rs485.py -p             # Con debug
    python3 fv_rs485.py                # Normal
    LOGLEVEL=INFO python3 fv_rs485.py  # Via env

Para un equipo específico (ej. SRNE):
    python3 fv_srne.py -p              # Wrapper para SRNE
"""

import sys
import time
import os
from typing import Dict, List, Optional, Any

import minimalmodbus

# Helpers
from helpers.control_servicio import controlar_servicio
from helpers.gestor_parametros import GestorParametros
from helpers.logger import Logger
from helpers.gestor_bd import GestorBD
from helpers.gestor_mqtt import GestorMQTT
from helpers.gestor_telegram import GestorTelegram
from helpers.gestor_procesos import GestorProcesos


# =============================================================================
# CLASE ESPECÍFICA PARA CAPTURA RS485
# =============================================================================

class CapturadorRS485:
    """
    Capturador específico para dispositivos RS485 Modbus RTU.

    Soporta múltiples equipos configurados en Parametros_FV.py bajo una misma
    variable (ej. SRNE, ANENJI). Cada equipo puede tener múltiples registros
    Modbus configurados.

    Config dict esperado (desde Parametros_FV.py):
        {
            'id': 'SRNE1',
            'usar': 1,
            'dev': '/dev/ttyUSB0',
            'baudrate': 9600,
            'id_modbus': 1,
            'tiempo_captura': 5,
            'COMANDOS': {
                'Vbat': {'reg': 0x0101, 'dec': 1, 'tipo': 'u16'},
                'Ibat': {'reg': 0x0102, 'dec': 2, 'tipo': 's16'},
                # ... más comandos
            }
        }
    """

    def __init__(self, nombre_equipo: str, config: dict):
        """
        Inicializa el capturador RS485.

        Args:
            nombre_equipo: Nombre del equipo (ej. 'SRNE', 'ANENJI')
            config: Configuración completa del equipo desde Parametros_FV.py
        """
        self.nombre_equipo = nombre_equipo
        self.config = config
        self.log = Logger(f'proceso.{nombre_equipo}')

        # Estado del capturador
        self.modbus: Dict[str, minimalmodbus.Instrument] = {}
        self.comandos: Dict[str, Any] = {}
        self.orden_bytes: int = 0
        self.equipos_activos: List[str] = []
        self.n_fallos_captura: Dict[str, int] = {}
        self.t_ultima_captura: Dict[str, float] = {}
        self.t_recarga_parametros: float = 0

        # Gestores
        self.gestor_bd: Optional[GestorBD] = None
        self.gestor_mqtt: Optional[GestorMQTT] = None
        self.gestor_telegram: Optional[GestorTelegram] = None

        # Extraer configuración
        self._extraer_configuracion(config)

    def _extraer_configuracion(self, config: dict) -> None:
        """Extrae configuración del equipo."""
        # Copiar equipos activos (excluyendo 'COMANDOS')
        self.equipos_activos = [
            e for e in config
            if isinstance(config[e], dict) and config[e].get('usar', 0) == 1 and e != 'COMANDOS'
        ]

        # Extraer comandos
        if 'COMANDOS' in config:
            self.comandos = config['COMANDOS'].copy()
        else:
            self.comandos = {}

        # Orden de bytes (endianness)
        self.orden_bytes = config.get('orden_bytes', 0)

        # Inicializar contadores de fallos
        for e in self.equipos_activos:
            self.n_fallos_captura[e] = 0
            self.t_ultima_captura[e] = 0

        self.log.info(f"Equipos activos: {self.equipos_activos}")

    def inicializar(self) -> None:
        """Inicializa gestores y conexión Modbus."""
        self.log.info(f"Inicializando {self.nombre_equipo}...")

        # Inicializar GestorBD
        self.gestor_bd = GestorBD()
        for e in self.equipos_activos:
            self.gestor_bd.insertar_equipo_si_falta(e.upper())

        # Inicializar GestorTelegram
        try:
            self.gestor_telegram = GestorTelegram()
            if self.gestor_telegram.esta_habilitado():
                self.gestor_telegram.enviar_mensaje_inicio(self.nombre_equipo)
        except Exception as e:
            self.log.warning(f"No se pudo inicializar Telegram: {e}")
            self.gestor_telegram = GestorTelegram(usar_telegram=False)

        # Inicializar GestorMQTT
        try:
            self.gestor_mqtt = GestorMQTT(depurar=self.log.es_debug())
            self.gestor_mqtt.suscribir_equipos(self.equipos_activos)
            if not self.gestor_mqtt.conectar():
                self.log.warning("No se pudo conectar al broker MQTT")
        except Exception as e:
            self.log.warning(f"No se pudo inicializar MQTT: {e}")
            self.gestor_mqtt = None

        self.log.info(f"Dispositivo {self.nombre_equipo} inicializado correctamente")

    def _abrir_conexion_modbus(self, equipo: str) -> None:
        """Abre conexión Modbus para un equipo específico."""
        if equipo in self.modbus:
            return

        config_eq = self.config[equipo]
        self.log.debug(f"Abriendo conexión Modbus en {config_eq['dev']} con id: {config_eq['id_modbus']}")

        try:
            self.modbus[equipo] = minimalmodbus.Instrument(
                config_eq['dev'],
                config_eq['id_modbus']
            )
            self.modbus[equipo].serial.baudrate = config_eq.get('baudrate', 9600)
            self.modbus[equipo].serial.bytesize = 8
            self.modbus[equipo].serial.parity = minimalmodbus.serial.PARITY_NONE
            self.modbus[equipo].serial.stopbits = 1
            self.modbus[equipo].serial.timeout = 3
            self.modbus[equipo].mode = minimalmodbus.MODE_RTU
            self.modbus[equipo].debug = False
            self.log.debug(".... OK")
        except Exception as e:
            raise Exception(f"No se pudo abrir conexión Modbus para {equipo}: {e}")

    def leer_registro(self, equipo: str, comando: str) -> float:
        """
        Lee un registro individual de un equipo.

        Args:
            equipo: Nombre del equipo (ej. 'SRNE1')
            comando: Nombre del comando (ej. 'Vbat')

        Returns:
            Valor leído del registro
        """
        cmd = self.comandos[comando]
        reg = cmd['reg']
        dec = cmd.get('dec', 0)
        tipo = cmd.get('tipo', 'u16')
        offset = cmd.get('offset', 0)
        fc = cmd.get('fc', 3)

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
        elif tipo == 'adaptar':
            d = self.modbus[equipo].read_register(reg, dec, fc)

        if tipo != 'adaptar':
            d += offset

        return d

    def leer_registros(self, equipo: str) -> Dict[str, float]:
        """
        Lee múltiples registros usando rangos (lectura múltiple).

        Args:
            equipo: Nombre del equipo

        Returns:
            Diccionario {comando: valor}
        """
        ee = 1000
        lectura = {}  # {registro: valor}
        datos = {}    # {comando: valor}

        try:
            if 'lectura_multiple' not in self.comandos:
                return datos

            for reg_ini, reg_fin in self.comandos['lectura_multiple']['rangos']:
                ee = 1010
                nreg = reg_fin - reg_ini + 1
                registros = list(range(reg_ini, reg_fin + 1))

                try:
                    ee = 1020
                    d = self.modbus[equipo].read_registers(reg_ini, nreg, 3)
                except Exception as e:
                    ee = 1030
                    self.log.error(f'Error lectura multiple reg_ini:{reg_ini},reg_fin:{reg_fin} -> nreg:{nreg}')
                    self.n_fallos_captura[equipo] += 1
                    continue

                for i in range(nreg):
                    lectura[registros[i]] = d[i]

                # Interpretar lectura
                cmd = {}  # {registro: clave_comando}
                for c in self.comandos:
                    if 'reg' in self.comandos[c]:
                        cmd[self.comandos[c]['reg']] = c

                for r in lectura:
                    try:
                        if r not in cmd:
                            continue
                        comando = cmd[r]
                        grabar = self.comandos[comando].get('grabar', True)
                        if not grabar:
                            continue

                        valor = lectura[r]
                        if self.orden_bytes == 1:
                            valor = int.from_bytes(valor.to_bytes(2, byteorder='little'))

                        dec = self.comandos[comando].get('dec', 0)
                        tipo = self.comandos[comando].get('tipo', 'u16')
                        offset = self.comandos[comando].get('offset', 0)

                        d = -9999
                        if tipo == 'u16':
                            d = round(valor * 10**-dec, dec)
                        elif tipo == 's16':
                            d = valor if valor < 32767 else valor - 65536
                            d = round(d * 10**-dec, dec)
                        elif tipo == 'u32':
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

        except Exception as e:
            self.log.error(f'Equipo {equipo}: error {ee}...rango de lectura de registros mal definido en Parametros_FV.py')

        return datos

    def leer_datos(self, equipo: str) -> Dict[str, float]:
        """
        Lee todos los datos de un equipo.

        Args:
            equipo: Nombre del equipo

        Returns:
            Diccionario con todos los datos leídos
        """
        t0 = time.time()
        datos = {}
        error = False

        try:
            ee = 100
            lectura_multiple = self.comandos.get('lectura_multiple', {}).get('usar', 0)

            if lectura_multiple == 1:
                datos = self.leer_registros(equipo)
            else:
                for c in self.comandos:
                    if c in ['ayuda', 'lectura_multiple']:
                        continue

                    grabar = self.comandos[c].get('grabar', True)
                    if not grabar:
                        continue

                    ee = 110
                    datos[c] = self.leer_registro(equipo, c)

            t1 = time.time()
            datos['tcaptura'] = round(t1 - t0, 2)

        except Exception as error1:
            self.log.error(f"Error {ee} en leer_datos({equipo})..comando={c} {type(error1).__name__} - {error1}")
            error = True

        # Añadir Nfallos
        datos['Nfallos'] = self.n_fallos_captura.get(equipo, 0)

        if error:
            datos['error'] = True

        return datos

    def guardar_datos(self, equipo: str, datos: Dict[str, float]) -> None:
        """
        Guarda datos en base de datos.

        Args:
            equipo: Nombre del equipo
            datos: Diccionario con datos a guardar
        """
        try:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            self.gestor_bd.guardar_datos_equipo_dict(equipo.upper(), tiempo, datos)
        except Exception as e:
            self.log.error(f"Error guardando datos de {equipo}: {e}")

    def listar_parametros(self, equipo: str) -> None:
        """Lista los parámetros del equipo y los envía por Telegram."""
        if not self.gestor_telegram or not self.gestor_telegram.esta_habilitado():
            return

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
                tipo = self.comandos[c].get('tipo', 'u16')

                if tipo == 'adaptar':
                    datos = {}
                    ejecutar = '\n'.join(self.comandos[c]['adaptar'])
                    exec(ejecutar)
                    d = datos[c]

                msg += f"    ..... Valor Actual de <b>{c}={d}</b>\n\n"
                time.sleep(0.05)
            except Exception as e:
                self.log.error(f'Error en leer_registro({equipo},{c})')
                time.sleep(1)
                msg += f'<b>...error lectura de {c}</b>\n'

            if nlineas % 20 == 0:
                self.gestor_telegram.enviar_mensaje_seguro(msg)
                msg = ''

        msg += ' =============================\n'
        self.gestor_telegram.enviar_mensaje_seguro(msg)

    def escribir_registro(self, equipo: str, mensaje: str) -> None:
        """
        Escribe un registro en el equipo.

        Args:
            equipo: Nombre del equipo
            mensaje: Comando a ejecutar
        """
        MENSAJE = mensaje.upper()

        for c in self.comandos:
            ee = 30
            f = MENSAJE.find(c.upper())

            if f != -1:
                ee = 40
                variable = mensaje[f:len(c)]

                try:
                    d = self.leer_registro(equipo, c)
                    valor = mensaje[len(c):].strip()
                    ee = 50

                    if len(valor) > 0 and valor[0] == '=':
                        valor = valor[1:]
                        valor_n = float(valor)
                        escritura = True
                    else:
                        escritura = False

                    ee = 60
                    registro = self.comandos[c]['reg']
                    msg = f'Valor registro {registro}...{variable}= {d} '

                    if self.log.es_debug():
                        self.log.debug(msg)

                    ee = 70
                    if not self.comandos[c].get('escritura', False):
                        escritura = False
                        msg += f'\n Error {variable} no admite escritura'
                    elif escritura:
                        if 'rango' not in self.comandos[c]:
                            self.comandos[c]['rango'] = [0, 65535]
                        if valor_n < self.comandos[c]['rango'][0] or valor_n > self.comandos[c]['rango'][1]:
                            escritura = False
                            msg += f'\n Error en valor {valor_n} fuera de rango admitido'

                    ee = 80
                    if escritura:
                        decimales = self.comandos[c].get('dec', 0)
                        self.modbus[equipo].write_register(registro, valor_n, decimales)
                        msg += f'\nNuevo Valor-->{registro}...{variable}= {valor_n} '

                        if self.log.es_debug():
                            self.log.debug(msg)

                    ee = 90
                    if self.gestor_telegram and self.gestor_telegram.esta_habilitado():
                        self.gestor_telegram.enviar_mensaje_seguro(msg)

                except Exception as e:
                    self.log.error(f'Error {ee} en comando MQTT: {e}')

                return

            ee = 100

        try:
            msg = f'Comando {mensaje} no encontrado'
            ee = 110
            if self.gestor_telegram and self.gestor_telegram.esta_habilitado():
                self.gestor_telegram.enviar_mensaje_seguro(msg)
        except Exception as e:
            self.log.error(f'Error {ee} en comando MQTT: {e}')

    def procesar_comandos_mqtt(self) -> None:
        """Procesa comandos MQTT pendientes."""
        if not self.gestor_mqtt or not self.gestor_mqtt.hay_comandos_pendientes():
            return

        c_mqtt = self.gestor_mqtt.obtener_comando_pendiente()

        if c_mqtt['comando'] in self.comandos.get('ayuda', []):
            if self.log.es_debug():
                self.log.debug(f"Ejecutando Listar Parametros de equipo {c_mqtt['equipo']}")
            self.listar_parametros(c_mqtt['equipo'])
        else:
            if self.log.es_debug():
                self.log.debug(f"Ejecutando Lectura/Escritura {c_mqtt['comando']} en equipo {c_mqtt['equipo']}")
            self.escribir_registro(c_mqtt['equipo'], c_mqtt['comando'])

    def cerrar(self) -> None:
        """Libera recursos."""
        if self.gestor_bd:
            self.gestor_bd.cerrar()
        if self.gestor_mqtt:
            self.gestor_mqtt.desconectar()
        self.modbus.clear()
        self.log.info(f"Dispositivo {self.nombre_equipo} cerrado")


# =============================================================================
# FUNCIÓN DE PROCESO PARA MULTIPROCESSING
# =============================================================================

def proceso_captura(indice: int, config_equipo: dict, args_extra: dict):
    """
    Función que se ejecuta en cada subprocesso de captura.

    Args:
        indice: Índice del equipo (para multiplexación)
        config_equipo: Configuración del equipo (incluye 'id' y configuración completa)
        args_extra: Argumentos extra (nombre_equipo para el tipo de dispositivo)
    """
    nombre_equipo = args_extra.get('nombre_equipo', 'RS485')
    equipo_id = config_equipo['id']

    log = Logger(f'proceso.{nombre_equipo}.{equipo_id}')

    try:
        # Pequeña delay para multiplexar inicialización
        time.sleep(0.02 * indice)

        log.info(f"Iniciando captura para {nombre_equipo}.{equipo_id}")

        # Crear capturador RS485
        capturador = CapturadorRS485(nombre_equipo, config_equipo)

        # Inicializar
        capturador.inicializar()

        log.info(f"Comenzando bucle de captura para {nombre_equipo}.{equipo_id}")

        # Para hot-reload de parámetros
        ruta_parametros = "/home/pi/PVControl+/Parametros_FV.py"
        t_cambio_parametros = 0
        try:
            t_cambio_parametros = os.path.getmtime(ruta_parametros)
        except FileNotFoundError:
            pass

        dia = time.strftime("%Y-%m-%d")

        while True:
            try:
                t0 = time.perf_counter()

                # Verificar cambios en Parametros_FV.py (hot-reload)
                try:
                    actual_mtime = os.path.getmtime(ruta_parametros)
                    if actual_mtime != t_cambio_parametros:
                        log.info("Recargando Parametros_FV.py (cambio detectado)")
                        # Recargar gestor de parámetros
                        from helpers.gestor_parametros import obtener_gestor
                        gestor_global = obtener_gestor()
                        gestor_global.recargar()
                        t_cambio_parametros = actual_mtime
                        # Recargar configuración
                        capturador._extraer_configuracion(gestor_global.obtener(nombre_equipo))
                except Exception as e:
                    log.debug(f"Error verificando cambios en parámetros: {e}")

                # Verificar cambio de día
                dia_anterior = dia
                dia = time.strftime("%Y-%m-%d")
                if dia_anterior != dia:
                    # Resetear contadores de fallos
                    for e in capturador.equipos_activos:
                        capturador.n_fallos_captura[e] = 0

                # Procesar comandos MQTT pendientes
                capturador.procesar_comandos_mqtt()

                # Leer datos de cada equipo activo
                for equipo in capturador.equipos_activos:
                    # Abrir conexión Modbus si no existe
                    capturador._abrir_conexion_modbus(equipo)

                    # Verificar si es tiempo de captura
                    tiempo_captura = capturador.config[equipo].get('tiempo_captura', 5)
                    if time.time() - capturador.t_ultima_captura.get(equipo, 0) >= tiempo_captura:
                        try:
                            datos = capturador.leer_datos(equipo)
                            capturador.guardar_datos(equipo, datos)
                            capturador.t_ultima_captura[equipo] = time.time()

                            # Debug output
                            if log.es_debug():
                                log.info(f"-- {equipo}: {datos}")
                        except Exception as e:
                            log.error(f"Error leyendo {equipo}: {e}")
                            capturador.n_fallos_captura[equipo] += 1
                            time.sleep(1)

                # Timing
                t_transcurrido = time.perf_counter() - t0

                # Esperar hasta siguiente ciclo
                if log.es_debug():
                    log.debug(f"{nombre_equipo}.{equipo_id}: t={t_transcurrido*1000:.1f}ms")

                time.sleep(0.1)

            except Exception as e:
                log.error(f"Error en bucle de captura: {e}")
                import traceback
                log.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(1)

    except KeyboardInterrupt:
        log.info("Finalizando por KeyboardInterrupt")
        capturador.cerrar()
        sys.exit(0)
    except Exception as e:
        log.error(f"Error fatal en {nombre_equipo}.{equipo_id}: {e}")
        import traceback
        log.error(f"Traceback: {traceback.format_exc()}")
        capturador.cerrar()
        sys.exit(1)


# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================

SERVICIO = 'fv_rs485'
TIEMPO_ENTRE_PROCESOS = 0  # Segundos entre inicio de procesos


def main(nombre_equipo: str = 'RS485'):
    """
    Función principal para captura RS485.

    Args:
        nombre_equipo: Nombre del tipo de equipo en Parametros_FV.py (ej. 'SRNE', 'ANENJI')
    """
    log = Logger(f'{SERVICIO}.main')

    # Obtener gestor de parámetros
    gestor_params = GestorParametros()

    # Obtener equipos activos
    lista_equipos_activos = gestor_params.obtener_equipos_activos(nombre_equipo)

    # Control de ejecución del servicio
    controlar_servicio(SERVICIO, len(lista_equipos_activos) > 0)

    # Mostrar banner de inicio
    log.manual('=' * 50)
    log.manual(f'{nombre_equipo}_activos=')
    for equipo in lista_equipos_activos:
        log.manual(
            f' -{equipo["id"]}=' +
            f' dev={equipo.get("dev", "N/A")}' +
            f' - baudrate={equipo.get("baudrate", 9600)}' +
            f' - id_modbus={equipo.get("id_modbus", 1)}'
        )
    log.manual('=' * 50)

    # Crear y ejecutar gestor de procesos
    gestor = GestorProcesos(
        nombre=SERVICIO,
        funcion_captura=proceso_captura,
        lista_equipos=lista_equipos_activos,
        args_extra={'nombre_equipo': nombre_equipo},
        tiempo_entre_procesos=TIEMPO_ENTRE_PROCESOS
    )

    # Ejecutar (bloqueante hasta KeyboardInterrupt)
    gestor.ejecutar()


def iniciar_captura(nombre_equipo: str, debug: bool = False) -> None:
    """
    Inicia la captura de datos RS485 para un equipo específico.

    Esta función es un wrapper para compatibilidad con scripts antiguos.
    Se usa desde scripts como fv_srne.py.

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

    # Ejecutar main
    main(nombre_equipo)
