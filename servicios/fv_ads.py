#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_ads.py - Captura de datos ADS1115 para PVControl+

Características:
- Logger para mensajes de depuración
- GestorBD para acceso a base de datos
- GestorProcesos para gestión de procesos
- Gestión de servicios externa
- Clase ADS específica inline

Uso:
    python3 fv_ads.py -p             # Con debug
    python3 fv_ads.py                # Normal
    LOGLEVEL=INFO python3 fv_ads.py  # Via env
"""

import sys
import time
from typing import Dict

# Helpers
from helpers.control_servicio import controlar_servicio
from helpers.gestor_parametros import GestorParametros
from helpers.logger import Logger
from helpers.gestor_bd import GestorBD
from helpers.excepciones import ErrorInicializacion, ErrorLectura
from helpers.gestor_procesos import GestorProcesos


# =============================================================================
# CLASE ESPECÍFICA PARA ADS1115 (inline, no separada)
# =============================================================================

class CapturadorADS1115:
    """
    Capturador específico para ADS1115.

    Soporta todos los modos de operación del ADS1115:
    - modo=0: Canal desactivado
    - modo=1: Disparado (single-shot)
    - modo=2: Continuo (continuous)
    - modo=3: Diferencial disparado
    - modo=4: Diferencial continuo

    Config dict esperado:
        {
            'id': 'ADS1',
            'direccion': 0x48,
            'vars': ['Vbat', 'Aux1', 'Vplaca', 'Aux2'],
            'modo': [1, 0, 0, 0],  # 0=off, 1=single, 2=continuous, 3=diff, 4=diff_continuous
            'gain': [2, 2, 2, 2],
            'rate': [250, 250, 250, 250],
            'bucles': [10, 0, 0, 0],
            'res': [47.46, 47.46, 47.46, 47.46],
            'tmuestra': 0.2
        }
    """

    def __init__(self, nombre: str, config: dict):
        self.nombre = nombre
        self.config = config
        self._adc = None
        # El logger determina automáticamente el nivel desde args o LOGLEVEL
        self.log = Logger(f'proceso.{nombre}')

        # Estado para modo continuo
        self._modo_continuo = False
        self._indice_canal_continuo = 0
        self.Nfallos = 0  # Contador de errores acumulados

    def inicializar(self):
        """Inicializa hardware ADS1115."""
        self.log.info(f"Inicializando {self.nombre}...")
        try:
            import Adafruit_ADS1x15

            self._adc = Adafruit_ADS1x15.ADS1115(
                address=self.config['direccion'],
                busnum=1
            )

            # Verificar comunicación
            test_val = self._adc.read_adc(0, gain=2)
            self.log.debug(f"Lectura de prueba: {test_val}")
            self.log.info(f"Dispositivo {self.nombre} inicializado correctamente")

        except ImportError as e:
            raise ErrorInicializacion(f"Adafruit_ADS1x15 no instalado: {e}", self.nombre)
        except Exception as e:
            raise ErrorInicializacion(
                f"No se pudo inicializar ADS1115 en dirección {self.config['direccion']}: {e}",
                self.nombre
            )

    def _iniciar_modo_continuo(self):
        """
        Inicia el modo continuo para el primer canal activo encontrado.
        Soporta modo=2 (continuo) y modo=4 (diferencial continuo).
        """
        if self._adc is None:
            self.log.error("No se ha inicializado el ADC o ha habido un problema en la inicialización.")
            return
        
        for indice, modo in enumerate(self.config['modo']):
            if modo == 2:  # Continuo single-ended
                self.log.debug(f"Iniciando modo continuo en canal {indice}")
                self._adc.start_adc(
                    indice,
                    gain=self.config['gain'][indice],
                    data_rate=self.config['rate'][indice]
                )
                self._modo_continuo = True
                self._indice_canal_continuo = indice
                return
            elif modo == 4:  # Continuo diferencial
                indice_diff = 0 if indice == 0 else 3
                self.log.debug(f"Iniciando modo diferencial continuo en canal {indice_diff}")
                self._adc.start_adc_difference(
                    indice_diff,
                    gain=self.config['gain'][indice],
                    data_rate=self.config['rate'][indice]
                )
                self._modo_continuo = True
                self._indice_canal_continuo = indice
                return

    def leer_datos(self) -> Dict[str, float]:
        """
        Lee datos de todos los canales configurados.

        Soporta:
        - modo=1: Disparado (lee y convierte)
        - modo=2: Continuo (usa get_last_result)
        - modo=3: Diferencial disparado
        - modo=4: Diferencial continuo

        Para cada canal:
        - Almacena lecturas en lista 'capturas'
        - Calcula 'mediana' (valor central de lista ordenada)
        - Calcula error como max(capturas) - min(capturas)
        - Incrementa Nfallos si hay error de lectura
        """
        if self._adc is None:
            self.log.error("No se ha inicializado el ADC o ha habido un problema en la inicialización.")
            self.Nfallos += 1
            return {}

        datos = {}

        # Verificar si hay algún canal en modo continuo y iniciarlo si es necesario
        if not self._modo_continuo:
            self._iniciar_modo_continuo()

        # Si estamos en modo continuo, leer todos los canales con get_last_result()
        if self._modo_continuo:
            indice = self._indice_canal_continuo
            modo = self.config['modo'][indice]
            nombre_var = self.config['vars'][indice]

            if modo in [2, 4]:  # Continuo o diferencial continuo
                try:
                    # Leer múltiples muestras
                    capturas = []
                    for i in range(self.config['bucles'][indice]):
                        val = self._adc.get_last_result()
                        if val is not None:
                            capturas.append(val)
                        # Esperar según el data rate
                        if self.config['rate'][indice] > 0:
                            time.sleep(1.0 / self.config['rate'][indice])

                    # Calcular mediana y error
                    if capturas:
                        mediana = sorted(capturas)[len(capturas) // 2]  # Mediana
                        error = max(capturas) - min(capturas)

                        valor = round(
                            mediana * 0.000125 * self.config['res'][indice] / self.config['gain'][indice],
                            3
                        )
                        datos[nombre_var] = valor

                        self.log.debug(
                            f"Canal {indice} ({nombre_var}): mediana={mediana}, error={error}, valor={valor}"
                        )
                    else:
                        self.Nfallos += 1
                except Exception as e:
                    self.log.error(f"Error leyendo canal continuo {indice} ({nombre_var}): {e}")
                    self.Nfallos += 1
        else:
            # Modo disparado: leer cada canal según su configuración
            for indice in range(4):
                modo = self.config['modo'][indice]

                # Saltar canales desactivados
                if modo == 0:
                    continue

                nombre_var = self.config['vars'][indice]
                if not nombre_var:
                    continue

                try:
                    # Leer según el modo, almacenando en lista 'capturas'
                    capturas = []

                    if modo == 1:  # Single-ended disparado
                        for _ in range(self.config['bucles'][indice]):
                            val = self._adc.read_adc(
                                indice,
                                gain=self.config['gain'][indice],
                                data_rate=self.config['rate'][indice]
                            )
                            if val is not None:
                                capturas.append(val)

                    elif modo == 3:  # Differential disparado
                        indice_diff = 0 if indice == 0 else 3
                        for _ in range(self.config['bucles'][indice]):
                            val = self._adc.read_adc_difference(
                                indice_diff,
                                gain=self.config['gain'][indice],
                                data_rate=self.config['rate'][indice]
                            )
                            if val is not None:
                                capturas.append(val)
                    else:
                        continue

                    # Calcular mediana y error
                    if capturas:
                        mediana = sorted(capturas)[len(capturas) // 2]  # Mediana
                        error = max(capturas) - min(capturas)

                        valor = round(
                            mediana * 0.000125 * self.config['res'][indice] / self.config['gain'][indice],
                            3
                        )
                        datos[nombre_var] = valor

                        self.log.debug(
                            f"Canal {indice} ({nombre_var}): mediana={mediana}, error={error}, valor={valor}"
                        )
                    else:
                        self.Nfallos += 1

                except Exception as e:
                    self.log.error(f"Error leyendo canal {indice} ({nombre_var}): {e}")
                    self.Nfallos += 1

        # Añadir Nfallos a los datos que se guardarán en BD
        datos['Nfallos'] = self.Nfallos

        if not datos:
            raise ErrorLectura("Ningún canal activo leyó correctamente", self.nombre)

        return datos

    def cerrar(self):
        """Libera recursos del ADS1115."""
        self._adc = None
        self._modo_continuo = False
        self.log.info(f"Dispositivo {self.nombre} cerrado")


# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================
SERVICIO = 'fv_ads'
TIEMPO_ENTRE_PROCESOS = 0  # Segundos entre inicio de procesos para evitar contención I2C


def proceso_captura(indice_ads: int, config_ads: dict, config_bd: dict):
    """
    Función que se ejecuta en cada subprocesso de captura.

    Args:
        indice_ads: Índice del ADS (para multiplexación)
        config_ads: Configuración del ADS
        config_bd: Configuración de base de datos
    """
    import os

    nombre_ads = config_ads['id']

    # Logger específico para este subprocesso
    # El logger determina automáticamente el nivel desde args o LOGLEVEL
    log = Logger(f'proceso.{nombre_ads}')

    try:
        # Pequeña delay para multiplexar inicialización
        time.sleep(0.02 * indice_ads)

        log.info(f"Iniciando captura para {nombre_ads}")

        # Crear capturador ADS
        # El capturador usa el mismo logger, así que hereda el nivel automáticamente
        capturador = CapturadorADS1115(nombre_ads, config_ads)

        # Inicializar hardware
        capturador.inicializar()

        # Conectar a BD usando GestorBD
        gestor_bd = GestorBD()

        # Registrar equipo si no existe
        gestor_bd.insertar_equipo_si_falta(nombre_ads)

        log.info(f"Comenzando bucle de captura para {nombre_ads}")

        # Bucle principal de captura
        n_capturas = 0

        # Para hot-reload de parámetros
        ruta_parametros = "/home/pi/PVControl+/Parametros_FV.py"
        t_cambio_parametros = 0
        try:
            t_cambio_parametros = os.path.getmtime(ruta_parametros)
        except FileNotFoundError:
            pass

        while True:
            try:
                t0 = time.perf_counter()

                # Verificar cambios en Parametros_FV.py (hot-reload)
                try:
                    actual_mtime = os.path.getmtime(ruta_parametros)
                    if actual_mtime != t_cambio_parametros:
                        log.info("Recargando Parametros_FV.py (cambio detectado)")
                        n_capturas = 0
                        # Recargar gestor de parámetros
                        from helpers.gestor_parametros import obtener_gestor
                        gestor_global = obtener_gestor()
                        gestor_global.recargar()
                        t_cambio_parametros = actual_mtime
                        # Resetear modo continuo para re-evaluar
                        capturador._modo_continuo = False
                except Exception as e:
                    log.debug(f"Error verificando cambios en parámetros: {e}")

                # Leer datos
                datos = capturador.leer_datos()

                # Guardar en BD usando GestorBD
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                gestor_bd.guardar_datos_equipo_dict(nombre_ads, tiempo, datos)

                # Timing y debug
                t1 = (time.perf_counter() - t0) * 1000

                if log.es_debug():
                    log.debug(
                        f"{nombre_ads}: t={t1:6.1f}ms - datos={datos}"
                    )

                # Esperar hasta siguiente muestra
                t_transcurrido = time.perf_counter() - t0
                tiempo_espera = max(config_ads['tmuestra'] - t_transcurrido, 0)
                time.sleep(tiempo_espera)

                n_capturas += 1

            except Exception as e:
                log.error(f"Error en bucle de captura: {e}")
                import traceback
                log.error(f"Traceback: {traceback.format_exc()}")
                # Continuar con el bucle en lugar de salir

    except KeyboardInterrupt:
        log.info("Finalizando por KeyboardInterrupt")
        sys.exit(0)
    except Exception as e:
        log.error(f"Error fatal en {nombre_ads}: {e}")
        import traceback
        log.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


def main():
    """Función principal."""
    log = Logger('fv_ads.main')
    
    # Obtener gestor de parámetros (caché interno)
    gestor_params = GestorParametros()

    # Control de ejecución del servicio
    lista_ads_activos = gestor_params.obtener_equipos_activos('ADS')
    controlar_servicio(SERVICIO, len(lista_ads_activos) > 0)

    # Mostrar banner de inicio
    log.manual('=' * 50)
    log.manual('ADS_activos=')
    for ads in lista_ads_activos:
        log.manual(
            f' -{ads["id"]}=' +
            f' direc={ads["direccion"]} - var= {ads["vars"]} - modo={ads["modo"]}'
        )
    log.manual('=' * 50)

    # Crear y ejecutar gestor de procesos
    gestor = GestorProcesos(
        nombre='fv_ads',
        funcion_captura=proceso_captura,
        lista_equipos=lista_ads_activos,
        tiempo_entre_procesos=TIEMPO_ENTRE_PROCESOS
    )

    # Ejecutar (bloqueante hasta KeyboardInterrupt)
    gestor.ejecutar()


if __name__ == '__main__':
    main()
