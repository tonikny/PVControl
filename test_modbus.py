#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-07
#
################### PARAMETROS CONEXION ############
dev = '/dev/ttyUSB0'
baudrate = 9600
id_modbus = 1
####################################################

######### REGISTROS LECTURA ########################
reg = {
    'Vbat': 215,
    'Vplaca' : 219,
    'SOC' : 229,
    'Vflot' : 325
}
####################################################

import sys, time
import minimalmodbus

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando  '+ Fore.GREEN + sys.argv[0])

sim = 1 if '-s' in sys.argv else 0 # simulacion


# CONEXION
if sim == 0:
    modbus = minimalmodbus.Instrument(dev, id_modbus)
    modbus.serial.baudrate = baudrate
    modbus.serial.bytesize = 8
    modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
    modbus.serial.stopbits = 1
    modbus.serial.timeout = 3
    modbus.debug = False
    modbus.mode = minimalmodbus.MODE_RTU

    if '-d' in sys.argv: modbus.debug = True
else:
    print('Modo simulado')

# BUCLE
while True:
    print()
    print(Fore.RED + time.strftime("%Y-%m-%d %H:%M:%S") + Fore.RESET + '  ' + '#' * 80)
    for r in reg:
        try:
            d = modbus.read_registers(reg[r], 1, 3) if sim == 0 else 9999
        except:
            d = Fore.RED+'Error'+ Fore.RESET 
        print(Fore.GREEN + f'Registro {reg[r]}...{r} = {d}')
    time.sleep(5)
