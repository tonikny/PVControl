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

logging.basicConfig(level=logging.INFO)

class Srne:
        
    def __init__(self, serialPort):
        self.modbus = ModbusClient(method='rtu', port=serialPort, baudrate=9600, timeout=1)
        self.modbus.connect()
        self.datos = {}
        self.archivo = '/run/shm/datos_srne.csv'
        logging.info(__class__.__name__ + ":Objeto creado")
    
    
    def leerRegistros(self):
        
        csvfv = CsvFv(self.archivo)

        while True:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_sg = time.time()

            try:
                R_Vbat = self.modbus.read_holding_registers(0x0101, 2, unit=1)
                R_Vplaca = self.modbus.read_holding_registers(0x0107, 2, unit=1)
                R_Iplaca = self.modbus.read_holding_registers(0x0102, 2, unit=1)
                time.sleep(1)
            except:
                logging.warning (__class__.__name__ + ":Error lectura SRNE")
                break # para poder parar con crtl+c
                
            if not (R_Vbat.isError() or R_Vplaca.isError() or R_Iplaca.isError()):
                Vbat = R_Vbat.registers[0]/10
                Vplaca = R_Vplaca.registers[0]/10
                Iplaca = R_Iplaca.registers[0]/100
                #consumo = I1.registers[10]
                logging.debug (Vbat, Vplaca, Iplaca)
            else:
                logging.warning (__class__.__name__ + ':Error lectura registros SRNE')
 
                
            self.datos = {'Tiempo_sg':tiempo_sg, 'Tiempo':tiempo, 'Vbat':Vbat, 'Vplaca':Vplaca, 'Iplaca':Iplaca}
            csvfv.escribirCsv(self.datos)

            # prueba de lectura    
            dades = csvfv.leerCsv()
            aux = ""
            for d in dades:
                aux = aux + dades[d] + " - "
            print (aux)
            
            
        self.modbus.close()

               
if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    Srne(serialPort).leerRegistros()
        
            
            


