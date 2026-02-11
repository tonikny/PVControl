"""
Módulo de Control de Ejecución de Servicios

Este módulo proporciona funciones para controlar la ejecución de servicios
de PVControl+ basándose en la configuración de parámetros.

Características:
- Detiene servicios automáticamente cuando no hay equipos activos
- Sin uso de exec() o eval() para mayor seguridad
- Funciones explícitas para cada tipo de control
- Comentarios en español

Uso:
    from fv_control_servicio import controlar_servicio
    
    # En fv_ads.py: verificar si hay ADS activos
    hay_ads_activas = sum(1 for v in ADS.values() if v.get("usar")) > 0
    controlar_servicio("fv_ads", hay_ads_activas)
"""

import sys
import subprocess

from helpers.gestor_logs import Logger

log = Logger(name=__name__)

def controlar_servicio(nombre_servicio: str, debe_ejecutarse: bool) -> None:
    """
    Controla la ejecución de un servicio basándose en una condición booleana.
    
    Si debe_ejecutarse es False, el servicio se detiene mediante systemctl
    y el script sale con sys.exit().
    
    Args:
        nombre_servicio: Nombre del servicio systemd (ej. "fv_ads", "fv_rs485")
        debe_ejecutarse: True si el servicio debe continuar, False para detenerlo
        
    Ejemplo:
        >>> # Detener si no hay ADS activos
        >>> hay_ads = sum(1 for v in ADS.values() if v.get("usar")) > 0
        >>> controlar_servicio("fv_ads", hay_ads)
    """
    if not debe_ejecutarse:
        parar_servicio(nombre_servicio)


def parar_servicio(nombre_servicio: str) -> None:
    """
    Detiene un servicio mediante systemctl y termina la ejecución del script.
    
    Args:
        nombre_servicio: Nombre del servicio systemd a detener
    """
    log.info(f'Se ejecuta ... sudo systemctl stop {nombre_servicio} ... parada servicio {nombre_servicio}')
    try:
        resultado = subprocess.getoutput(f'sudo systemctl stop {nombre_servicio}')
        log.info(resultado)
    except Exception as e:
        log.error(f"Error deteniendo servicio {nombre_servicio}: {e}")
    finally:
        sys.exit(0)


def verificar_equipos_activos(config_dict: dict, clave_usar: str = "usar") -> bool:
    """
    Verifica si hay equipos activos en un diccionario de configuración.
    
    Args:
        config_dict: Diccionario de configuración (ej. ADS, RS485)
        clave_usar: Clave que indica si el equipo está activo (por defecto "usar")
        
    Returns:
        True si hay al menos un equipo activo, False en caso contrario
        
    Ejemplo:
        >>> ADS = {"ADS1": {"usar": True}, "ADS2": {"usar": False}}
        >>> verificar_equipos_activos(ADS)
        True
    """
    try:
        return sum(1 for v in config_dict.values() if v.get(clave_usar, False)) > 0
    except (AttributeError, TypeError):
        # Si config_dict no es un dict o no tiene el método get
        return False


def verificar_parametro_boolean(valor) -> bool:
    """
    Verifica si un parámetro booleano es verdadero.
    
    Args:
        valor: Valor a verificar (puede ser bool, int, str, etc.)
        
    Returns:
        True si el valor es verdadero, False en caso contrario
        
    Ejemplo:
        >>> verificar_parametro_boolean(True)
        True
        >>> verificar_parametro_boolean(1)
        True
        >>> verificar_parametro_boolean("True")
        True
        >>> verificar_parametro_boolean(False)
        False
    """
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return valor > 0
    if isinstance(valor, str):
        return valor.lower() in ('true', '1', 'yes', 'si', 'sí')
    return False
