#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_growatt.py - Captura de datos para inversores Growatt via RS485

Script principal para captura de datos de inversores Growatt via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable GROWATT

Uso:
    python3 fv_growatt.py -p             # Con debug
    python3 fv_growatt.py                # Normal
    LOGLEVEL=INFO python3 fv_growatt.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo GROWATT
    main(nombre_equipo='GROWATT')
