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
    from helpers.control_servicio import controlar_servicio

    # En fv_ads.py: verificar si hay ADS activos
    hay_ads_activas = sum(1 for v in ADS.values() if v.get("usar")) > 0
    controlar_servicio("fv_ads", hay_ads_activas)
"""

import sys
import subprocess

from helpers.logger import Logger

log = Logger(nombre=__name__)


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
