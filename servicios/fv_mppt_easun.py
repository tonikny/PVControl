#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_mppt_easun.py - Captura de datos para controladores MPPT EASUN via RS485

Script principal para captura de datos de controladores MPPT EASUN via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable MPPT_EASUN

Uso:
    python3 fv_mppt_easun.py -p             # Con debug
    python3 fv_mppt_easun.py                # Normal
    LOGLEVEL=INFO python3 fv_mppt_easun.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo MPPT_EASUN
    main(nombre_equipo='MPPT_EASUN')
