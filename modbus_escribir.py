#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-23
#
import click,glob
import sys, time
import minimalmodbus

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW +'#' * 80)
print (Fore.CYAN + '         Lectura/Escritura interactiva de registros MODBUS-RTU ')
print(Fore.YELLOW + '#' * 80)
print()

salir = click.prompt(Fore.RED + '  Si no esta seguro pulse 0 para salir o 1 para continuar ', type=str, default='1')

if salir == "1": print()
else: sys.exit()


################### PARAMETROS CONEXION ############
carpeta = '/dev/ttyUSB*'

print(Fore.MAGENTA + '-' * 80)
print('    ------ CONFIGURACION COMUNICACION -----')
print('-' * 80)
print()
print(Fore.YELLOW + f'    Lista Dispositivos /dev/ttyUSBx....')

dispositivos = glob.glob(carpeta)
ndispositivos = len(dispositivos)
if ndispositivos == 0:
    print()
    print(Fore.RED + ' ERROR...NO se encuentran dispositivos ttyUSBx en carpeta /dev')
    sys.exit()

for f in range(ndispositivos):
    print (f'{Fore.MAGENTA}     {f}: {Fore.CYAN}{dispositivos[f]}')

print()
print(Fore.YELLOW)

id_dev = click.prompt('     ..... elija el numero del dispositivo a usar', type=int, default= 0)
dev = dispositivos[id_dev]

baudrate = click.prompt('     ..... introduzca baudios comunicacion', type=int, default= 9600)
id_modbus = click.prompt('     ..... introduzca id del dispositivo Modbus', type=int, default= 1)


print( Fore.CYAN+f'    Parametros comunicacion : dev:{dev} - baudios:{baudrate}  - id_modbus:{id_modbus} ')
print('-' * 80)
print()

print(Fore.MAGENTA + '-' * 80)
print('    ------ LECTURA/ESCRITURA REGISTRO MODBUS -----')
print('-' * 80)

while True:
    print()
    print(Fore.YELLOW)
    reg = click.prompt('     ..... introduzca numero registro (0= salir)', type=int, default= 0)
    if reg == 0: sys.exit()
    
    decimales = click.prompt('     ..... introduzca numero de decimales a considerar', type=int, default= 0)
     
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
    print()
    print(Fore.CYAN + f'     ........ Valor actual = {Lectura_actual}')
    
    print(Fore.YELLOW)
    valor = click.prompt('     ..... introduzca valor a escribir (-99999= solo lectura)', type=float, default= -99999)

    escritura = True if valor != -99999 else False

    # 
    if escritura:
        
        print (Fore.CYAN + f'     ........ Escribiendo en registro {reg} el valor {valor} con {decimales} decimales')
        modbus.write_register(reg, valor, decimales)  # Registro, valor, nº decimales

        # Lectura final:
        Lectura_final = modbus.read_register(reg, decimales)  # Registro, nº decimales
        print(f'     ........ Valor despues de la escritura = {Lectura_final}')
    
    modbus.serial.close()
    print()
    print(Fore.RESET + '*' * 80)
    seguir = click.prompt(' 0= Nuevo registro..... 1= salir', type=int, default= 1)

    if seguir == 1: sys.exit()

