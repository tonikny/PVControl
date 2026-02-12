import os
import sys
import time
import importlib.util

from helpers.gestor_logs import GestorLogs

# Rutas por defecto basadas en la ubicación del proyecto
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

class GestorParametros:
    """
    Gestiona la carga de parámetros de PVControl+.

    Args:
        check_interval (int): Intervalo de verificación de cambios en el archivo de parámetros (en segundos).

    Ejemplo:
        gestor = GestorParametros(10)
        ADS, ANENJI = gestor.leer_parametros("ADS", "ANENJI")
    """

    def __init__(self, check_interval=5):
        self.check_interval = check_interval
        self._dist = None
        self._user = None
        self._mtime = 0
        self._size = 0
        self._last_check = 0
        self._version = 0
        self._log = GestorLogs(__name__)
        self._log.debug("Iniciando Gestor de Parámetros")

    def _cargar_modulo(self, ruta):
        # evitar cache .pyc
        old_flag = sys.dont_write_bytecode
        sys.dont_write_bytecode = True

        try:
            nombre = f"config_{os.path.basename(ruta)}_{time.time_ns()}"
            spec = importlib.util.spec_from_file_location(nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            return modulo
        finally:
            sys.dont_write_bytecode = old_flag

    def _obtener(self, nombre):
        """Prioriza valores del usuario y usa DIST como respaldo."""
        if hasattr(self._user, nombre):
            return getattr(self._user, nombre)

        if hasattr(self._dist, nombre):
            return getattr(self._dist, nombre)

        raise AttributeError(f"Parámetro '{nombre}' no definido")

    def _carga_inicial(self):
        self._dist = self._cargar_modulo(RUTA_DIST)

        # el archivo de usuario puede existir pero estar vacio
        try:
            self._user = self._cargar_modulo(RUTA_USER)
            self._mtime = os.path.getmtime(RUTA_USER)
            self._size = os.path.getsize(RUTA_USER)
        except FileNotFoundError:
            self._log.warning("Archivo de usuario no encontrado, usando solo DIST")
            self._user = None
            self._mtime = 0
            self._size = 0

        self._last_check = time.monotonic()
        self._version = 1
        self._log.info("Configuración cargada")


    def _recargar_si_es_necesario(self):

        now = time.monotonic()

        if now - self._last_check < self.check_interval:
            return

        self._last_check = now

        try:
            mtime = os.path.getmtime(RUTA_USER)
            size = os.path.getsize(RUTA_USER)
        except FileNotFoundError:
            self._log.error(f"Archivo no encontrado: {RUTA_USER}")
            return

        # sin cambios
        if mtime == self._mtime and size == self._size:
            return

        # ignorar archivo vacio
        if size == 0:
            self._log.error("Archivo vacío; se mantiene configuración anterior")
            return

        try:
            nuevo_user = self._cargar_modulo(RUTA_USER)
        except Exception:
            self._log.error("Error recargando configuración; se mantiene la anterior")
            return

        self._user = nuevo_user
        self._mtime = mtime
        self._size = size
        self._version += 1

        self._log.info(f"Configuración recargada (v{self._version})")
        
    # ---------- API pública ----------

    def leer_parametros(self, *nombres):
        """ Retorna una o diversas variables del archivo de parámetros.
        
        Ejemplo:
        ```
        ADS, ANENJI = gestor.leer_parametros("ADS", "ANENJI)
        ```
        """
        self._log.debug(f"Parámetros solicitados: {' '.join(nombres)}")

        if self._user is None:
            self._carga_inicial()
        else:
            self._recargar_si_es_necesario()

        valores = [self._obtener(nombre) for nombre in nombres]
        self._log.debug(f"Parámetros obtenidos: {valores}")

        return valores[0] if len(valores) == 1 else tuple(valores)



    def version(self):
        """
        Retorna la versión actual de la configuración.

        Ejemplo:
            ```
            ultima_version = gestor.version()
            while True:
                EQUIPO = gestor.leer_parametros("EQUIPO")

                if gestor.version() != ultima_version:
                    ultima_version = gestor.version() 
                    reinicializar_equipos(...)
                ...
            ```
        """
        return self._version
    
    def convertir_dict_a_list(self, equipo):
        """
        Convierte un dict a una lista de dicts.

        Param:
        ```
        EQUIPO = {
            EQUIPO1: {
                "usar": True,
                "ip": "237.84.2.178",
                "puerto": 80
            }
        }
        ```
        Return:
        ```
        EQUIPO = [
            {
                "id": "EQUIPO1",
                "usar": True,
                "ip": "237.84.2.178",
                "puerto": 80
            }
        ]
        ```
        """
        return [
            {"id": key, **value}
            for key, value in equipo.items()
        ]
