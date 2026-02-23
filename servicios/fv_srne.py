"""
fv_srne.py - Captura de datos para reguladores SRNE via RS485

Script principal para captura de datos de reguladores SRNE via RS485.
Importa y ejecuta la librería genérica fv_rs485.py para realizar la captura.

La configuración del equipo se define en Parametros_FV.py bajo la variable SRNE

Ejemplo de configuración en Parametros_FV.py:
    SRNE = {
        'SRNE1': {
            'usar': 1,
            'dev': '/dev/ttyUSB0',
            'baudrate': 9600,
            'id_modbus': 1,
            'tiempo_captura': 5,
        },
        'SRNE2': {
            'usar': 1,
            'dev': '/dev/ttyUSB1',
            'baudrate': 9600,
            'id_modbus': 2,
            'tiempo_captura': 5,
        },
        'COMANDOS': {
            'SOC': {'reg': 0x0100},
            'Vbat': {'reg': 0x0101, 'dec': 1},
            'Ibat': {'reg': 0x0102, 'dec': 2},
            # ... más comandos
        }
    }

Uso:
    python3 fv_srne.py -p             # Con debug
    python3 fv_srne.py                # Normal
    LOGLEVEL=INFO python3 fv_srne.py  # Via env
"""

from servicios.fv_rs485 import main

if __name__ == "__main__":
    # Iniciar captura para el equipo SRNE
    # El flag -p activa el modo debug (también se puede usar LOGLEVEL=INFO)
    main(nombre_equipo='SRNE')
