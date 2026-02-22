# -*- coding: utf-8 -*-
"""
Gestor de Parámetros para PVControl+

Proporciona acceso con caché a los parámetros de configuración.
Carga los archivos una sola vez y mantiene el estado en memoria.

Características:
- Caché interna (no re-lee archivos en cada llamada)
- Solo devuelve variables específicas solicitadas
- Función genérica para obtener equipos activos de cualquier tipo

Uso:
    from helpers.gestor_parametros import GestorParametros
    
    gestor = GestorParametros()
    
    # Obtener variables específicas
    servidor = gestor.obtener('servidor')
    servidor, usuario = gestor.obtener('servidor', 'usuario')
    
    # Obtener equipos activos de cualquier tipo
    ads_activos = gestor.obtener_equipos_activos('ADS')
    anenji_activos = gestor.obtener_equipos_activos('ANENJI')
"""

import os
import importlib.util
from typing import Any, Dict, List, Optional


class GestorParametros:
    """
    Gestor de parámetros con caché para PVControl+.
    
    Carga Parametros_FV_DIST.py y Parametros_FV.py una sola vez,
    fusiona las configuraciones, y mantiene el resultado en caché.
    
    Ejemplo:
        gestor = GestorParametros()
        servidor = gestor.obtener('servidor')
        ads = gestor.obtener_equipos_activos('ADS')
    """
    
    # Rutas de archivos de configuración
    RUTA_PARAMETROS_DIST = "/home/pi/PVControl+/Parametros_FV_DIST.py"
    RUTA_PARAMETROS_USER = "/home/pi/PVControl+/Parametros_FV.py"
    
    def __init__(self):
        """
        Inicializa el gestor y carga parámetros en caché.
        
        La carga se realiza una sola vez. Llamadas posteriores
        usan la caché interna.
        """
        self._cache: Optional[Dict[str, Any]] = None
        self._cargar_parametros()
    
    def _importar_desde_ruta(self, ruta_archivo: str, nombre_modulo: str) -> Dict[str, Any]:
        """
        Importa un módulo desde una ruta específica y devuelve sus atributos públicos.
        
        Args:
            ruta_archivo: Ruta absoluta al archivo .py
            nombre_modulo: Nombre para el módulo importado
            
        Returns:
            Diccionario con todos los atributos públicos del módulo
        """
        spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_archivo)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        
        return {k: v for k, v in modulo.__dict__.items() if not k.startswith('_')}
    
    def _cargar_parametros(self) -> None:
        """
        Carga parámetros desde ambos archivos y los cachea.
        
        El orden de carga es:
        1. Parametros_FV_DIST.py - Valores por defecto
        2. Parametros_FV.py - Valores del usuario (sobreescribe)
        """
        # 1. Cargar valores por defecto (DIST)
        self._cache = self._importar_desde_ruta(
            self.RUTA_PARAMETROS_DIST,
            "parametros_dist"
        )
        
        # 2. Cargar valores del usuario (USER) y sobreescribir
        if os.path.exists(self.RUTA_PARAMETROS_USER):
            params_user = self._importar_desde_ruta(
                self.RUTA_PARAMETROS_USER,
                "parametros_user"
            )
            self._cache.update(params_user)
    
    def obtener(self, *nombres: str) -> Any:
        """
        Obtiene uno o múltiples parámetros por nombre.
        
        Args:
            *nombres: Nombres de los parámetros a obtener
            
        Returns:
            Si un solo nombre: el valor del parámetro
            Si múltiples nombres: tupla con los valores
            
        Ejemplo:
            >>> gestor = GestorParametros()
            >>> servidor = gestor.obtener('servidor')
            >>> servidor, usuario = gestor.obtener('servidor', 'usuario')
        """
        valores = [self._cache.get(nombre) for nombre in nombres]
        
        return valores[0] if len(valores) == 1 else tuple(valores)
    
    def obtener_dict(self, *nombres: str) -> Dict[str, Any]:
        """
        Obtiene múltiples parámetros como diccionario.
        
        Args:
            *nombres: Nombres de los parámetros a obtener
            
        Returns:
            Diccionario {nombre: valor} para cada parámetro solicitado
            
        Ejemplo:
            >>> gestor = GestorParametros()
            >>> config = gestor.obtener_dict('servidor', 'usuario', 'clave')
            >>> config['servidor']
            'localhost'
        """
        return {nombre: self._cache.get(nombre) for nombre in nombres}
    
    def obtener_equipos_activos(self, clave: str) -> List[Dict[str, Any]]:
        """
        Obtiene solo los equipos activos de un tipo específico.
        
        Args:
            clave: Nombre del tipo de equipo (ej: 'ADS', 'ANENJI', 'SRNE')
            
        Returns:
            Lista de dicts con configuración de cada equipo activo
            
        Ejemplo:
            >>> gestor = GestorParametros()
            >>> ads_activos = gestor.obtener_equipos_activos('ADS')
            >>> anenji_activos = gestor.obtener_equipos_activos('ANENJI')
        """
        if clave not in self._cache:
            return []
        
        equipos_dict = self._cache[clave]
        
        # Convertir dict a lista de dicts con 'id' incluido
        return [
            {"id": key, **value}
            for key, value in equipos_dict.items()
            if isinstance(value, dict) and value.get('usar', False)
        ]
    
    def obtener_todos_equipos(self, clave: str) -> List[Dict[str, Any]]:
        """
        Obtiene TODOS los equipos de un tipo (activos o no).
        
        Args:
            clave: Nombre del tipo de equipo (ej: 'ADS', 'ANENJI')
            
        Returns:
            Lista de dicts con configuración de cada equipo
        """
        if clave not in self._cache:
            return []
        
        equipos_dict = self._cache[clave]
        
        # Convertir dict a lista de dicts con 'id' incluido
        return [
            {"id": key, **value}
            for key, value in equipos_dict.items()
            if isinstance(value, dict)
        ]
    
    def recargar(self) -> None:
        """
        Fuerza la recarga de parámetros desde archivos.
        
        Útil si se sabe que los archivos han cambiado y se necesita
        actualizar la caché.
        """
        self._cache = None
        self._cargar_parametros()


# Instancia global para uso rápido (opcional)
_gestor_global: Optional[GestorParametros] = None


def obtener_gestor() -> GestorParametros:
    """
    Obtiene o crea la instancia global del gestor de parámetros.
    
    Returns:
        Instancia de GestorParametros
    """
    global _gestor_global
    if _gestor_global is None:
        _gestor_global = GestorParametros()
    return _gestor_global
