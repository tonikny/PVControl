#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_anenji11kw.py - Captura de datos para inversores ANENJI 11KW via RS485

Script principal para captura de datos de inversores ANENJI 11KW via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable ANENJI11KW

Uso:
    python3 fv_anenji11kw.py -p             # Con debug
    python3 fv_anenji11kw.py                # Normal
    LOGLEVEL=INFO python3 fv_anenji11kw.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo ANENJI11KW
    main(nombre_equipo='ANENJI11KW')
