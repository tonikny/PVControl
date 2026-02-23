#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_must.py - Captura de datos para inversores MUST via RS485

Script principal para captura de datos de inversores MUST via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable MUST

Uso:
    python3 fv_must.py -p             # Con debug
    python3 fv_must.py                # Normal
    LOGLEVEL=INFO python3 fv_must.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo MUST
    main(nombre_equipo='MUST')
