#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
import timeout_decorator

from crc16 import crc16xmodem
from struct import pack
from traceback import format_exc


dev_hibrido ='/dev/hidraw0'
log = '/home/pi/log/infini'
        

# ---- Comandos HIBRIDO
@timeout_decorator.timeout(10, use_signals=False)
def comando(cmd):
    global t_muestra
    ee = 0
    try:
        if cmd == "ERROR":
            while True:
                time.sleep(1)

        ee = 10
        if cmd == "POP02":   # ERROR firmware - CRC correcto es: 0xE2 0x0A
            cmd_crc = '\x50\x4f\x50\x30\x32\xe2\x0b\x0d'

        elif cmd[:9] == '^S007POP1':
                cmd_crc = '^S007POP1\x0e\x10\r'
                
        elif cmd[:9] == '^S007LON0':
                cmd_crc = '^S007LON0\x69\xd8\r'
                        
        else:
            checksum = crc16xmodem(cmd)
            cmd_crc = cmd + pack('>H', checksum) + '\r'

        ee = 20
        print 'Comando con CRC=',repr(cmd_crc)
        if os.path.exists(dev_hibrido):
            fd = open(dev_hibrido,'rb+')
            time.sleep(.15)
            ee = 30
            print 'Byte1=',repr(cmd_crc[:8])
            fd.write(cmd_crc[:8])
            
            ee = 40
            if len(cmd_crc) > 8:
                print 'Byte2=',repr(cmd_crc[8:16])
                fd.flush()
                fd.write(cmd_crc[8:16])

            ee = 45
            if len(cmd_crc) > 16:
                print 'Byte3=',repr(cmd_crc[16:])
                fd.flush()
                fd.write(cmd_crc[16:])
            
            ee = 50
            time.sleep(.15)
            
            r = fd.read(8).encode('string-escape')

            ee = 60
            while r.find('r') == -1 :
                time.sleep(.15)
                r = r + fd.read(8).encode('string-escape')
            
            ee = 70
            r = time.strftime("%Y-%m-%d %H:%M:%S")+ " "+cmd+" "+r
            s1 = r.split("\\")
            s = s1[0][0:].split(" ")
            s[3]=s[3][1:] #quito el parentesis inicial de la respuesta
            #print s
            t_muestra=5
    
    except:
        #print'Error Comando ',
        t_muestra=12
        s = 'Error Hibrido = '+ str(ee)
        
    finally:
        #print 'finally'
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
print 'fichero log =',log

while repeticion:
    #time.sleep(t_muestra)
    narg = len(sys.argv)
    try:
        if str(sys.argv[narg-1]) != '-R':
            repeticion = False   
        else:
            narg=narg-1

        for i in range (1,narg):
            cmd = str(sys.argv[i])
            print 'Comando=',cmd
            #with open(log, 'a+') as f:
            #    f.write(dia + ' / ' + hora + ' ' + cmd + '\n')
            
            r = comando(cmd)
            
            print r
            with open(log, 'a+') as f:
                f.write(",".join(r))
                f.write ('\n')
        if repeticion == True:    
            time.sleep(t_muestra)
    except:
        print ("error comando")
        with open(log, 'a+') as f:
            f.write("error comando\n")
        break
        
