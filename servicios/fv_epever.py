#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_epever.py - Captura de datos para controladores EPEVER via RS485

Script principal para captura de datos de controladores EPEVER via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable EPEVER

Uso:
    python3 fv_epever.py -p             # Con debug
    python3 fv_epever.py                # Normal
    LOGLEVEL=INFO python3 fv_epever.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo EPEVER
    main(nombre_equipo='EPEVER')
