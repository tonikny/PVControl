#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2024-05-26
#
# Script principal para captura de datos de reguladores SRNE via RS485
#
# Este script funciona como punto de entrada que importa y ejecuta la librería
# genérica fv_rs485.py para realizar la captura de datos.
#
# La configuración del equipo se define en Parametros_FV.py bajo la variable SRNE
#
# Ejemplo de configuración en Parametros_FV.py:
# SRNE = {
#     'SRNE1': {
#         'usar': 1,
#         'dev': '/dev/ttyUSB0',
#         'baudrate': 9600,
#         'id_modbus': 1,
#         'tiempo_captura': 5,
#     },
#     'COMANDOS': {
#         'SOC': {'reg': 0x0100},
#         'Vbat': {'reg': 0x0101, 'dec': 1},
#         # ... más comandos
#     }
# }

import sys
from servicios.fv_rs485 import iniciar_captura

if __name__ == "__main__":
    # Iniciar captura para el equipo SRNE
    iniciar_captura('SRNE', debug=('-p' in sys.argv))
