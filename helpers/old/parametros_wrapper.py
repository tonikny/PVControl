"""
Cargador de Parámetros Dinámico para PVControl+

Carga parámetros sin hardcodear nombres de variables.
"""

import os
import importlib.util
from typing import Any


class ParametrosWrapper:
    """
    Wrapper dinámico para cargar parámetros desde archivo Python.
    
    Uso:
        params = ParametrosWrapper("/home/pi/PVControl+/Parametros_FV.py")
        
        # Acceder como atributos
        servidor = params.servidor
        ads1 = params.ADS1
        
        # Acceder como diccionario
        servidor = params['servidor']
        
        # Iterar
        for nombre, valor in params.items():
            print(f"{nombre}: {valor}")
    """
    
    def __init__(self, ruta_archivo: str):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
        
        self._ruta = ruta_archivo
        self._datos = {}
        self._cargar()
    
    def _cargar(self) -> None:
        """Carga todos los atributos públicos del archivo"""
        spec = importlib.util.spec_from_file_location("parametros", self._ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        
        # Extraer todos los atributos que no empiecen con _
        for attr in dir(modulo):
            if not attr.startswith('_'):
                self._datos[attr] = getattr(modulo, attr)
    
    def __getattr__(self, nombre: str) -> Any:
        """Permite acceso tipo params.servidor"""
        if nombre in self._datos:
            return self._datos[nombre]
        raise AttributeError(f"Parámetro '{nombre}' no encontrado")
    
    def __getitem__(self, nombre: str) -> Any:
        """Permite acceso tipo params['servidor']"""
        return self._datos.get(nombre)
    
    def get(self, nombre: str, default=None) -> Any:
        """Obtiene parámetro con valor por defecto"""
        return self._datos.get(nombre, default)
    
    def items(self):
        """Iterar sobre todos los parámetros"""
        return self._datos.items()
    
    def keys(self):
        """Obtener todas las claves"""
        return self._datos.keys()
    
    def values(self):
        """Obtener todos los valores"""
        return self._datos.values()
    
    def __contains__(self, nombre: str) -> bool:
        """Verificar si existe un parámetro"""
        return nombre in self._datos
    
    def to_dict(self) -> dict:
        """Convertir a diccionario (para multiprocessing)"""
        return self._datos.copy()
    
    def recargar(self) -> None:
        """Recargar parámetros desde archivo"""
        self._datos.clear()
        self._cargar()