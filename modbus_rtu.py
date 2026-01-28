#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-01-24
#
####################################################################################
## Permite leer/escribir cualquier registro en equipos con Protocolo Modbus RTU

#    Modo interactivo ......  python modbus_rtu.py


#    Modo autonomo ....permite introducir los parametros desde linea de comando

#        python modbus_rtu.py -h   muestra ayuda de los distintos parametros

#        python modbus_rtu.py --registro 517
#        python modbus_rtu.py -r 517  (forma compacta)
#          .... Lectura del registro 517 considerando 1 decimal
#               ... (dev=/dev/ttyUSB0, baudrate=9600, id_modbus=1)

#        python modbus_rtu.py --registro 517 --valor 14.5
#        python modbus_rtu.py -r 517 -v 14.5 (forma compacta)
#          .... Escritura del registro 517 con el valor 14.5 considerando 1 decimal
#               ... (dev=/dev/ttyUSB0, baudrate=9600, id_modbus=1)

#        python modbus_rtu.py --dev /dev/ttyUSB1 --baudrate 2400 --id_modbus 2 --registro 517 --dec 0
#          .... Lectura del registro 517 considerando 0 decimal
#               ... (dev=/dev/ttyUSB1, baudrate=2400, id_modbus=2)

#        python modbus_rtu.py --dev /dev/ttyUSB1 --baudrate 2400 -id_modbus 1 --registro 517 --valor 14.5 --dec 0
#          .... Escritura del registro 517 con valor 14.5 considerando 0 decimal
#               ... (dev=/dev/ttyUSB1, baudrate=2400, id_modbus=2)

#        python modbus_rtu.py -d /dev/ttyUSB0 --b 2400 -i 2 -r 517 -v 14.5 --dec 0 (forma compacta)
#          .... Escritura del registro 517 con valor 14.5 considerando 0 decimal
#####################################################################################

import click,glob
import sys, time
import minimalmodbus
import argparse

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


parser = argparse.ArgumentParser()
parser.add_argument("-d","--dev", default='/dev/ttyUSB0', help="dev del dispositivo")
parser.add_argument("-b","--baudrate",  type=int, default=9600, help="baudrate del dispositivo")
parser.add_argument("-i","--id_modbus",  type=int, default=1, help="id_modbus del dispositivo")
parser.add_argument("-r","--registro",  type=int, help="Nº de registro Modbus")
parser.add_argument("-v","--valor",  type=float, default=-99999 ,help="Valor registro a escribir sin decimales")
parser.add_argument("--dec", default=1, type=int, help="Nº decimales a considerar")

args = parser.parse_args()
print(args)

if args.registro == None :
    modo = 'manual'
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
    print()
    print(Fore.YELLOW)
    reg = click.prompt('     ..... introduzca numero registro (0= salir)', type=int, default= 0)
    if reg == 0: sys.exit()
    
    decimales = click.prompt('     ..... introduzca numero de decimales a considerar', type=int, default= 0)
    

else:
    modo = 'autonomo'
    print ('Ejecutando en modo autonomo')
    dev = args.dev
    baudrate = args.baudrate
    id_modbus = args.id_modbus
    reg = args.registro
    decimales = args.dec
    


# CONEXION
modbus = minimalmodbus.Instrument(dev, id_modbus)
modbus.serial.baudrate = baudrate
modbus.serial.bytesize = 8
modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
modbus.serial.stopbits = 1
modbus.serial.timeout = 3
modbus.debug = False
modbus.mode = minimalmodbus.MODE_RTU

# Lectura actual:
Lectura_actual = modbus.read_register(reg, decimales)  # Registro, nº decimales
print()
print(Fore.CYAN + f'     ........ Valor actual registro {reg} = {Lectura_actual}')

## Cambio de valor en registro ##
#print(args.valor)

if args.valor == -99999 and modo=='manual':
    print(Fore.YELLOW)
    valor = click.prompt('     ..... introduzca valor a escribir (-99999= solo lectura)', type=float, default= -99999)
else:
    valor = args.valor
    
escritura = True if valor != -99999 else False

if escritura:        
    print (Fore.CYAN + f'     ........ Escribiendo en registro {reg} el valor {valor} con {decimales} decimales')
    modbus.write_register(reg, valor, decimales)  # Registro, valor, nº decimales

    # Lectura final:
    Lectura_final = modbus.read_register(reg, decimales)  # Registro, nº decimales
    print(f'     ........ Valor despues de la escritura = {Lectura_final}')
    
    modbus.serial.close()
 
    """
    if '-d' in sys.argv: modbus.debug = True
    print()
    print(Fore.RESET + '*' * 80)
    seguir = click.prompt(' 0= Nuevo registro..... 1= salir', type=int, default= 1)

    if seguir == 1: sys.exit()
    """
    

