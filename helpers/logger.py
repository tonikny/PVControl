# -*- coding: utf-8 -*-
"""
Logger simple y fork-safe para PVControl+

Este módulo proporciona un logger que funciona correctamente después de fork()
en multiprocessing, evitando los problemas de LoggerMultiprocessing con colas
compartidas.

Características:
- Sin colas compartidas ni Manager
- Sin locks que puedan corromperse tras fork
- Usa print() con flush para salida inmediata
- Compatible con códigos de color de colorama
- Niveles de logging configurables
- Soporte para variable de entorno LOGLEVEL
"""

import sys
import logging
import os
from typing import Optional
from colorama import Fore, Style

class Logger:
    """
    Logger simple y fork-safe para subprocessos de PVControl+.
    
    Usa print() directo en lugar de colas compartidas, evitando
    problemas de sincronización después de fork().
    
    Ejemplo:
        logger = Logger('fv_ads.ADS1', nivel=logging.DEBUG)
        logger.info('Iniciando captura')
        logger.error('Error de lectura')
    """
    
    # Niveles de logging
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    
    # Orden de prioridad para determinar nivel:
    # 1. Argumentos de línea de comandos (más prioridad)
    # 2. Variable de entorno LOGLEVEL
    # 3. Nivel por defecto (ERROR)
    
    def __init__(self, nombre: str = 'pvcontrol', nivel: Optional[int] = None):
        """
        Inicializa el logger.
        
        Args:
            nombre: Nombre del logger (se muestra en cada mensaje)
            nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
                   Si es None, se determina desde:
                   1. Argumentos de línea de comandos (-p, -p1, -p2)
                   2. Variable de entorno LOGLEVEL
                   3. Por defecto: ERROR
        """
        self.nombre = nombre
        
        # Determinar nivel desde argumentos si no se especifica
        if nivel is None:
            nivel = self._nivel_desde_argumentos_o_env()
        
        self.nivel = nivel
        
        # Verificar si hay códigos de color disponibles
        self.usar_colores = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _nivel_desde_argumentos_o_env(self) -> int:
        """
        Determina el nivel de logging con la siguiente prioridad:
        1. Argumentos de línea de comandos (-p, -p1, -p2)
        2. Variable de entorno LOGLEVEL
        3. Por defecto: ERROR
        """
        # 1. Prioridad máxima: argumentos de línea de comandos
        if '-p' in sys.argv:
            return logging.DEBUG
        elif '-p2' in sys.argv:
            return logging.INFO
        elif '-p1' in sys.argv:
            return logging.WARNING
        
        # 2. Segunda prioridad: variable de entorno LOGLEVEL
        loglevel_env = os.getenv('LOGLEVEL')
        if loglevel_env:
            loglevel_env = loglevel_env.upper()
            if loglevel_env == 'DEBUG':
                return logging.DEBUG
            elif loglevel_env == 'INFO':
                return logging.INFO
            elif loglevel_env == 'WARNING':
                return logging.WARNING
            elif loglevel_env == 'ERROR':
                return logging.ERROR
            elif loglevel_env == 'CRITICAL':
                return logging.CRITICAL
        
        # 3. Por defecto
        return logging.ERROR
    
    def _formatear(self, nivel_str: str, mensaje: str) -> str:
        """Formatea un mensaje con prefijo de nivel y nombre."""
        return f"[{nivel_str}] [{self.nombre}] {mensaje}"
    
    def debug(self, mensaje: str, *args) -> None:
        """Log mensaje de debug."""
        if self.nivel <= logging.DEBUG:
            msg = self._formatear('DEBUG', mensaje.format(*args) if args else mensaje)
            if self.usar_colores:
                msg = Fore.CYAN + msg + Style.RESET_ALL
            print(msg, flush=True)
    
    def info(self, mensaje: str, *args) -> None:
        """Log mensaje de información."""
        if self.nivel <= logging.INFO:
            msg = self._formatear('INFO', mensaje.format(*args) if args else mensaje)
            if self.usar_colores:
                msg = Fore.GREEN + msg + Style.RESET_ALL
            print(msg, flush=True)
    
    def warning(self, mensaje: str, *args) -> None:
        """Log mensaje de advertencia."""
        if self.nivel <= logging.WARNING:
            msg = self._formatear('WARNING', mensaje.format(*args) if args else mensaje)
            if self.usar_colores:
                msg = Fore.YELLOW + msg + Style.RESET_ALL
            print(msg, flush=True)
    
    def error(self, mensaje: str, *args) -> None:
        """Log mensaje de error."""
        if self.nivel <= logging.ERROR:
            msg = self._formatear('ERROR', mensaje.format(*args) if args else mensaje)
            if self.usar_colores:
                msg = Fore.RED + msg + Style.RESET_ALL
            print(msg, flush=True)
    
    def manual(self, mensaje: str, *args) -> None:
        """
        Muestra un mensaje manual que siempre se registra,
        independientemente del nivel de logging.
        
        Útil para mensajes importantes que el usuario debe ver.
        """
        msg = mensaje.format(*args) if args else mensaje
        if self.usar_colores:
            msg = Style.BRIGHT + msg + Style.RESET_ALL
        print(msg, flush=True)
    
    def es_debug(self) -> bool:
        """Devuelve True si el nivel es DEBUG."""
        return self.nivel <= logging.DEBUG

    def es_info(self) -> bool:
        """Devuelve True si el nivel es INFO o inferior."""
        return self.nivel <= logging.INFO

    @staticmethod
    def obtener_nivel_desde_args() -> int:
        """
        Obtiene el nivel de logging desde argumentos de línea de comandos o variable de entorno.
        
        Prioridad:
        1. Argumentos de línea de comandos (-p, -p1, -p2)
        2. Variable de entorno LOGLEVEL
        3. Por defecto: ERROR
        
        Returns:
            Nivel de logging (logging.DEBUG, logging.INFO, etc.)
            
        Ejemplo:
            nivel = Logger.obtener_nivel_desde_args()
            logger = Logger('mi_modulo', nivel)
        """
        # 1. Prioridad máxima: argumentos de línea de comandos
        if '-p' in sys.argv:
            return logging.DEBUG
        elif '-p2' in sys.argv:
            return logging.INFO
        elif '-p1' in sys.argv:
            return logging.WARNING

        # 2. Segunda prioridad: variable de entorno LOGLEVEL
        loglevel_env = os.getenv('LOGLEVEL')
        if loglevel_env:
            loglevel_env = loglevel_env.upper()
            if loglevel_env == 'DEBUG':
                return logging.DEBUG
            elif loglevel_env == 'INFO':
                return logging.INFO
            elif loglevel_env == 'WARNING':
                return logging.WARNING
            elif loglevel_env == 'ERROR':
                return logging.ERROR
            elif loglevel_env == 'CRITICAL':
                return logging.CRITICAL

        # 3. Por defecto
        return logging.ERROR


# Funciones de conveniencia para uso rápido
_log_global: Optional[Logger] = None


def obtener_logger(nombre: str = 'pvcontrol', nivel: Optional[int] = None) -> Logger:
    """
    Obtiene o crea un logger global.
    
    Args:
        nombre: Nombre del logger
        nivel: Nivel de logging
        
    Returns:
        Instancia de Logger
    """
    global _log_global
    if _log_global is None:
        _log_global = Logger(nombre, nivel)
    return _log_global


def debug(mensaje: str, *args) -> None:
    """Log debug usando logger global."""
    obtener_logger().debug(mensaje, *args)


def info(mensaje: str, *args) -> None:
    """Log info usando logger global."""
    obtener_logger().info(mensaje, *args)


def warning(mensaje: str, *args) -> None:
    """Log warning usando logger global."""
    obtener_logger().warning(mensaje, *args)


def error(mensaje: str, *args) -> None:
    """Log error usando logger global."""
    obtener_logger().error(mensaje, *args)
