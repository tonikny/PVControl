#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_anenji.py - Captura de datos para inversores ANENJI via RS485

Script principal para captura de datos de inversores ANENJI via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable ANENJI

Ejemplo de configuración en Parametros_FV.py:
    ANENJI = {
        'ANENJI1': {
            'usar': 1,
            'dev': '/dev/ttyUSB0',
            'baudrate': 9600,
            'id_modbus': 1,
            'tiempo_captura': 5,
        },
        'ANENJI2': {
            'usar': 1,
            'dev': '/dev/ttyUSB1',
            'baudrate': 9600,
            'id_modbus': 1,
            'tiempo_captura': 3,
        },
        'COMANDOS': {
            'Vbat': {'reg': 215, 'dec': 1, 'tipo': 'u16'},
            'Ibat': {'reg': 216, 'dec': 1, 'tipo': 's16'},
            'SOC': {'reg': 229, 'tipo': 'u16'},
            # ... más comandos
        }
    }

Uso:
    python3 fv_anenji.py -p             # Con debug
    python3 fv_anenji.py                # Normal
    LOGLEVEL=INFO python3 fv_anenji.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo ANENJI
    main(nombre_equipo='ANENJI')
