# -*- coding: utf-8 -*-
"""
Excepciones específicas para PVControl+

Módulo centralizado para excepciones relacionadas con hardware y captura de datos.
"""


class ErrorPVControl(Exception):
    """Clase base para todas las excepciones de PVControl+."""
    pass


class ErrorDispositivo(ErrorPVControl):
    """Error genérico de dispositivo hardware."""
    def __init__(self, mensaje: str, dispositivo: str = ""):
        self.dispositivo = dispositivo
        super().__init__(f"[{dispositivo}] {mensaje}" if dispositivo else mensaje)


class ErrorInicializacion(ErrorDispositivo):
    """Error al inicializar un dispositivo hardware."""
    pass


class ErrorI2C(ErrorDispositivo):
    """Error en comunicación I2C."""
    pass


class ErrorADC(ErrorI2C):
    """Error específico para convertidores ADC (ADS1115, etc.)."""
    pass


class ErrorModbus(ErrorDispositivo):
    """Error en comunicación Modbus."""
    pass


class ErrorLectura(ErrorDispositivo):
    """Error al leer datos de un dispositivo."""
    pass


class ErrorEscritura(ErrorDispositivo):
    """Error al escribir datos a un dispositivo."""
    pass


class ErrorBD(ErrorPVControl):
    """Error en operaciones de base de datos."""
    pass


class ErrorParametros(ErrorPVControl):
    """Error en configuración de parámetros."""
    pass


class ErrorServicio(ErrorPVControl):
    """Error en gestión de servicios del sistema."""
    pass
