#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-23
#
################### PARAMETROS CONEXION ############
dev = '/dev/ttyUSB0'
baudrate = 9600
id_modbus = 1
####################################################

###### REGISTRO A ESCRIBIR #########################
reg = 324 # Vabs
valor = 54.5
decimales = 1
####################################################

import sys, time
import minimalmodbus

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando  '+ Fore.GREEN + sys.argv[0])


# CONEXION
modbus = minimalmodbus.Instrument(dev, id_modbus)
modbus.serial.baudrate = baudrate
modbus.serial.bytesize = 8
modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
modbus.serial.stopbits = 1
modbus.serial.timeout = 3
modbus.debug = False
modbus.mode = minimalmodbus.MODE_RTU

if '-d' in sys.argv: modbus.debug = True


## Cambio de valor en registro ##

# Lectura actual:
Lectura_actual = modbus.read_register(reg, decimales)  # Registro, nº decimales
print(f'Valor antes del cambio = {Lectura_actual}')

# 
print (f'.... escribiendo en registro {reg} el valor {valor} con {decimales} decimales')
modbus.write_register(reg, valor, decimales)  # Registro, valor, nº decimales

# Lectura actual:
Lectura_final = modbus.read_register(reg, decimales)  # Registro, nº decimales
print(f'Valor despues del cambio = {Lectura_final}')
