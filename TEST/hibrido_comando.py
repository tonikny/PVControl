#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
import timeout_decorator

from crc16 import crc16xmodem
from struct import pack
from traceback import format_exc

################################################################
dev_hibrido ='/dev/hidraw0'   # dipositivo donde reconoce al hibrido enla carpeta /dev
usar_crc = 1                  # El protocolo usa CRC o no

grabar_fichero_log = 0        # Se guardan las repuestas del hibrido en un archivo de log
log = '/home/pi/'             # path al archivo de log (debe existir la carpeta)

DEBUG = False                 # saca mas informacion por pantalla
###################################################################

################## Ejemplos de uso #########################################################

#  sudo python3 hibrido_comando.py QPIGS           manda el comando QPIGS una unica vez y finaliza

#  sudo python3 hibrido_comando.py QPIGS -R        manda el comando QPIGS cada 5 sg

#  sudo python3 hibrido_comando.py QPIGS QMD       manda los comandos QPIGS y QMD una unica vez y finaliza

#  sudo python3 hibrido_comando.py QPIGS QMD -R    manda los comandos QPIGS y QMD cada 5 sg
################################################################################################



import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

# ---- Comandos HIBRIDO
@timeout_decorator.timeout(40, use_signals=False)
def comando(cmd):
    global t_muestra
    ee = 0
    
    cmd1 = cmd.encode()
    if DEBUG: print(f'Procesando comando {cmd1}')
    
    
    try:
        
        if cmd1 == b"ERROR":
            while True:
                time.sleep(1)

        ee = 10
        
        if usar_crc == 1:
            if cmd1 == b"POP02":   # ERROR firmware - CRC correcto es: 0xE2 0x0A
                cmd_crc = b'\x50\x4f\x50\x30\x32\xe2\x0b\x0d'
            elif cmd1[:9] == b'^S007POP1':
                cmd1 = b'^S007POP1\x0e\x10\r'    
            elif cmd1[:9] == b'^S007LON0':
                cmd1 = b'^S007LON0\x69\xd8\r'
            else:
                checksum = crc16xmodem(cmd1)
                cmd_crc = cmd1 + pack('>H', checksum) + b'\r'
        else:
            cmd_crc = cmd1 + b'\r'

        if DEBUG: print ('Comando_crc=',cmd_crc)
    except:
        print (Fore.RED + 'error A')
    
    try:   
        ee = 20
        if DEBUG: print ('Comando con CRC=',repr(cmd_crc))
        if os.path.exists(dev_hibrido):
            fd = open(dev_hibrido,'rb+')
            time.sleep(.20)
            ee = 30
            if DEBUG: print ('Byte1=',repr(cmd_crc[:8]))
            fd.write(cmd_crc[:8])
            
            ee = 40
            if len(cmd_crc) > 8:
                if DEBUG: print ('Byte2=',repr(cmd_crc[8:16]))
                fd.flush()
                fd.write(cmd_crc[8:16])

            ee = 45
            if len(cmd_crc) > 16:
                if DEBUG: print ('Byte3=',repr(cmd_crc[16:]))
                fd.flush()
                fd.write(cmd_crc[16:])
            
            ee = 50
            time.sleep(.5)

            if DEBUG: print ('leyendo desde el Hibrido...')
            
            r = fd.read(5)

            
            ee = 60
            while r.find(b'\r') == -1 :
                ee += 1
                time.sleep(.05)
                r = r + fd.read(1)
    except:
        if DEBUG: print ('error Bloque B')
             
    
    try:
         
        if DEBUG: print ('respuesta hibrido completa =',r)
            
        if DEBUG: print ('longitud respuesta=',len(r))

        r = r[0:len(r)-3] # quita CRC
        #print ('respuesta hibrido completa sin CRC =',r)        

        ee = 70
            
        #Añado a la respuesta fecha hora y comando enviado
        r = time.strftime("%Y-%m-%d %H:%M:%S").encode()+ b" " + cmd1 + b" " + r 

        # Creo lista separando por espacio
        s = r.split(b" ")
            
        if DEBUG: print ('s=',s)

        s[3]=s[3][1:] #quito el parentesis inicial de la respuesta
        #print ('respuesta sin parentesis inicial',s)
            
        t_muestra=5
    
    except:
        print ('Error Comando ', end='')
        t_muestra=12
        s = 'Error Hibrido = '+ str(ee)
        
    finally:
        try:
            fd.close()
        except:
            pass
        #print s
        return s


##### Bucle infinito  ######################
t_muestra = 5
repeticion = True

dia = time.strftime("%Y-%m-%d")
mes = time.strftime("%Y-%m")
hora = time.strftime("%H:%M:%S")

log = log + '-' + mes # nombre del fichero log por cada mes
#print ('fichero log =',log)

while repeticion:
    ee = 100
    #time.sleep(t_muestra)
    narg = len(sys.argv)
    try:
        ee = 200
        if str(sys.argv[narg-1]) != '-R': # compruebo si esta el parametro -R
            repeticion = False    
        else:
            narg=narg-1

        ee = 300
        for i in range (1,narg): # Bucle que recorre cada comando introducido
            cmd = str(sys.argv[i])
            if DEBUG: print ('Enviando Comando=',cmd)
            ee = 400

            r = comando(cmd)

            ee = 500
            if DEBUG: print ('Respuesta Hibrido = {r}')
            print (Fore.YELLOW + '#'*40)
            print (Fore.GREEN,b",".join(r))
            
            if grabar_fichero_log == 1:
                with open(log, 'ab+') as f:
                    f.write(b",".join(r))
                    f.write (b'\n')
                
            if i < narg-1:
                time.sleep(5)
            ee = 700
        if repeticion == True:    
            time.sleep(t_muestra)
    except:
        print ("error comando=",ee)
        if grabar_fichero_log == 1:
            with open(log, 'a+') as f:
                f.write("error comando\n")
        break
        
