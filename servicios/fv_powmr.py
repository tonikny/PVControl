#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_powmr.py - Captura de datos para inversores PowMr via RS485

Script principal para captura de datos de inversores PowMr via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable POWMR

Uso:
    python3 fv_powmr.py -p             # Con debug
    python3 fv_powmr.py                # Normal
    LOGLEVEL=INFO python3 fv_powmr.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo POWMR
    main(nombre_equipo='POWMR')
