import os
import sys
import time
import threading
import importlib.util
from collections import OrderedDict

from helpers.gestor_logs import GestorLogs

# Rutas por defecto basadas en la ubicación del proyecto
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RUTA_DIST = os.path.join(BASE_PATH, 'Parametros_FV_DIST.py')
RUTA_USER = os.path.join(BASE_PATH, 'Parametros_FV.py')

# Constante para el máximo de módulos cacheados para prevenir fugas de memoria
_MAX_CACHED_MODULES = 2  # Versión actual + 1 versión anterior

class GestorParametros:
    """
    Gestiona la carga de parámetros de PVControl+ con mejoras de seguridad y eficiencia.

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
        self._lock = threading.Lock()
        self._module_cache = OrderedDict()  # Caché para prevenir fugas de memoria
        self._load_initial_configs()
        self._log.debug("Gestor de Parámetros inicializado con éxito")

    def _clean_module_cache(self):
        """Limpia el caché manteniendo solo los módulos más recientes."""
        while len(self._module_cache) >= _MAX_CACHED_MODULES:
            # Elimina el módulo más antiguo
            oldest_key = next(iter(self._module_cache))
            del self._module_cache[oldest_key]

    def _cargar_modulo(self, ruta):
        """Carga un módulo desde archivo con manejo seguro de caché."""
        # Prevenir caché .pyc
        old_flag = sys.dont_write_bytecode
        sys.dont_write_bytecode = True

        try:
            # Usar timestamp como parte del nombre para evitar conflictos
            nombre = f"config_{os.path.basename(ruta).replace('.', '_')}_{int(time.time())}"
            
            # Limpiar caché si es necesario
            with self._lock:
                self._clean_module_cache()
                
            spec = importlib.util.spec_from_file_location(nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
            
            # Guardar en caché
            with self._lock:
                self._module_cache[nombre] = modulo
                
            return modulo
        except Exception as e:
            self._log.error(f"Error al cargar módulo {ruta}: {e}")
            raise
        finally:
            sys.dont_write_bytecode = old_flag

    def _obtener_con_defensa(self, nombre, default_value=None):
        """
        Obtiene un parámetro con defensa contra valores incorrectos.
        
        Args:
            nombre (str): Nombre del parámetro a obtener
            default_value: Valor por defecto si el parámetro no existe o es inválido
            
        Returns:
            El valor del parámetro o el valor por defecto
        """
        # Intentar obtener del usuario primero
        if self._user is not None and hasattr(self._user, nombre):
            try:
                valor = getattr(self._user, nombre)
                # Defensa básica contra tipos inesperados
                if valor is None:
                    self._log.warning(f"Parámetro '{nombre}' es None, usando valor por defecto")
                    return default_value
                return valor
            except Exception as e:
                self._log.error(f"Error al acceder al parámetro '{nombre}' en archivo de usuario: {e}")
                return default_value
        
        # Si no está en usuario, intentar desde dist
        if self._dist is not None and hasattr(self._dist, nombre):
            try:
                valor = getattr(self._dist, nombre)
                # Defensa básica contra tipos inesperados
                if valor is None:
                    self._log.warning(f"Parámetro '{nombre}' es None en archivo DIST, usando valor por defecto")
                    return default_value
                return valor
            except Exception as e:
                self._log.error(f"Error al acceder al parámetro '{nombre}' en archivo DIST: {e}")
                return default_value
        
        # Si no se encuentra en ninguno, usar valor por defecto
        self._log.warning(f"Parámetro '{nombre}' no encontrado, usando valor por defecto")
        return default_value

    def _load_initial_configs(self):
        """Carga inicial de configuraciones DIST y USER."""
        try:
            self._dist = self._cargar_modulo(RUTA_DIST)
        except Exception as e:
            self._log.error(f"Error al cargar archivo DIST {RUTA_DIST}: {e}")
            self._dist = None  # Permitir continuar aunque DIST falle

        # El archivo de usuario puede existir pero estar vacío
        try:
            self._user = self._cargar_modulo(RUTA_USER)
            self._mtime = os.path.getmtime(RUTA_USER)
            self._size = os.path.getsize(RUTA_USER)
        except FileNotFoundError:
            self._log.warning("Archivo de usuario no encontrado, usando solo DIST")
            self._user = None
            self._mtime = 0
            self._size = 0
        except Exception as e:
            self._log.error(f"Error al cargar archivo de usuario {RUTA_USER}: {e}")
            self._user = None
            self._mtime = 0
            self._size = 0

        self._last_check = time.monotonic()
        self._version = 1
        self._log.info("Configuraciones iniciales cargadas")

    def _recargar_si_es_necesario(self):
        """Recarga la configuración del usuario si ha cambiado."""
        with self._lock:  # Proteger acceso concurrente
            now = time.monotonic()

            if now - self._last_check < self.check_interval:
                return False

            self._last_check = now

            try:
                mtime = os.path.getmtime(RUTA_USER)
                size = os.path.getsize(RUTA_USER)
            except FileNotFoundError:
                self._log.error(f"Archivo no encontrado durante recarga: {RUTA_USER}")
                return False

            # Sin cambios
            if mtime == self._mtime and size == self._size:
                return False

            # Ignorar archivo vacío
            if size == 0:
                self._log.error("Archivo vacío detectado; se mantiene configuración anterior")
                return False

            try:
                nuevo_user = self._cargar_modulo(RUTA_USER)
            except Exception as e:
                self._log.error(f"Error recargando configuración; se mantiene la anterior: {e}")
                return False

            self._user = nuevo_user
            self._mtime = mtime
            self._size = size
            self._version += 1

            self._log.info(f"Configuración recargada (v{self._version})")
            return True

    # ---------- API pública ----------

    def leer_parametros(self, *nombres, default_values=None):
        """
        Retorna una o diversas variables del archivo de parámetros con defensa contra valores incorrectos.
        
        Args:
            *nombres: Nombres de los parámetros a leer
            default_values: Valores por defecto para cada parámetro (opcional)
            
        Ejemplo:
        ```
        ADS, ANENJI = gestor.leer_parametros("ADS", "ANENJI")
        # Con valores por defecto:
        ADS, ANENJI = gestor.leer_parametros("ADS", "ANENJI", default_values=[{}, {}])
        ```
        """
        if default_values is None:
            default_values = [None] * len(nombres)
        elif len(default_values) != len(nombres):
            raise ValueError("Número de valores por defecto no coincide con número de parámetros")
        
        self._log.debug(f"Parámetros solicitados: {' '.join(nombres)}")

        # Actualizar configuración si es necesario
        self._recargar_si_es_necesario()

        valores = []
        for i, nombre in enumerate(nombres):
            valor = self._obtener_con_defensa(nombre, default_values[i])
            valores.append(valor)

        self._log.debug(f"Parámetros obtenidos: {valores}")

        return valores[0] if len(valores) == 1 else tuple(valores)

    def version(self):
        """
        Retorna la versión actual de la configuración.
        """
        with self._lock:
            return self._version

    def convertir_dict_a_list(self, equipo):
        """
        Convierte un dict a una lista de dicts con defensa contra entradas incorrectas.
        
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
        if not isinstance(equipo, dict):
            self._log.warning(f"Entrada no es un diccionario: {type(equipo)}, devolviendo lista vacía")
            return []
        
        resultado = []
        for key, value in equipo.items():
            if not isinstance(value, dict):
                self._log.warning(f"Valor para clave '{key}' no es un diccionario, omitiendo")
                continue
            resultado.append({"id": key, **value})
        
        return resultado