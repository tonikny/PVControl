#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-17
#
################### PARAMETROS CONEXION ############
dev = '/dev/ttyUSB0'
baudrate = 9600
id_modbus = 1
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
    
    datos = {} # Inicializamos diccionario datos capturados
    
    #Capturamos registros desde 201 al 234 
    try:
       reg_ini = 201
       reg_fin = 234
       nreg = reg_fin - reg_ini + 1
       
       d = modbus.read_registers(reg_ini, nreg, 3) if sim == 0 else [9999] * nreg 
       datos['WM'] = d[201-reg_ini] # Working Mode
       datos['Vred'] = round(d[202 - reg_ini] / 10,2)  # Voltaje red AC entrada
       
       datos['Wred'] = round(d[204 - reg_ini] / 10,2)  # W de red AC.... ver  signo ??
       
       datos['Vbat'] = round(d[215 - reg_ini] / 10,2)  # Voltaje bateria
       datos['Ibat'] = round(d[216 - reg_ini] / 10,2)  # Intensidad bateria
       
       datos['Wplaca'] = d[223 - reg_ini]  # Waatios Placa
       
    except:
       d = Fore.RED+'Error'+ Fore.RESET 
    
    print(Fore.GREEN + f'Datos= {datos}')
    time.sleep(5)
