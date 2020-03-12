#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import pymodbus
import sys
import logging, traceback
from csvFv import CsvFv
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

serialPort = '/dev/ttyUSB0' # USB
#serialPort = '/dev/ttyS0' # TTL

# 0x0100 -> XX | YY=SOC
# 0x0103 -> XX=Rtemp | YY=Btemp

logging.basicConfig(level=logging.INFO)

class Srne:
        
    def __init__(self, serialPort):
        self.modbus = ModbusClient(method='rtu', port=serialPort, baudrate=9600, timeout=1)
        self.modbus.connect()
        logging.info(__class__.__name__ + ":Objeto creado")
    
    
    def leerRegistros(self):
        
        for com in range(0xE001, 0xE021):

            try:
                Res = self.modbus.read_holding_registers(com, 2, unit=1)
                time.sleep(1)
            except:
                logging.warning (__class__.__name__ + ":Error lectura SRNE")
                break # para poder parar con crtl+c
                
            if not Res.isError():
                valor = Res.registers[0]
                x = format(valor, '04x')
                #logging.info (__class__.__name__ + ": RES="+x)
                hi = x[:2]
                lo = x[2:]
                decHi = int(hi,16)
                decLo = int(lo,16)
                strHi = str(decHi)
                strLo = str(decLo)
                #logging.info (__class__.__name__ + ": RES="+hi+"|"+lo+" => "+strHi+"|"+strLo)
            else:
                logging.warning (__class__.__name__ + ':Error lectura registros SRNE')
                
            strRes = '"'+format(com, '04x') + '","' + x + '","' + hi + '","' + lo+ '"'\
                    + "," + strHi + "," + strLo 
                    #+ "," + str(bytes.fromhex(strHi)) + ","+str(bytes.fromhex(strLo)) 
            print(strRes)
 
        self.modbus.close()

               
if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    Srne(serialPort).leerRegistros()
        
            
            


