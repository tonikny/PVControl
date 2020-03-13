#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys, subprocess
import logging, traceback
from csvFv import CsvFv
from Bd import *
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from Parametros_FV import *

if usar_srne == 0:
    #print (commands.getoutput('sudo systemctl stop srne'))
    print (subprocess.getoutput('sudo systemctl stop srne'))
    sys.exit()

## Srne_Params.py ---------------------------------------------------
# Constantes de configuracion

# dev_srne= '/dev/ttyUSB0' # USB (configuracion en Parametro_FV.py)
#           '/dev/ttyS0' # TTL

# frecuencia de muestreo del regulador
FREQ_MUESTREO = 1 #seg
# frecuencia de grabación en la Bd
FREQ_BD = 5 #seg
# nivel de depuración (logging.CRITICAL, .ERROR, .WARNING, .INFO, .DEBUG)
DEBUG_LEVEL = logging.WARNING
#--------------------------------------------------------------------

##
# Gestion de reguladores modbus SRNE
# (Probado con el modelo MC-4885N25)
#
class Srne:
            
    archivoCvs = '/run/shm/datos_srne.csv' # archivo ram
    
    ##
    # creacion e inicializacion del objeto
    def __init__(self, serialPort):
        logging.info(__class__.__name__ + ":Objeto creado") 
        try:      
            self.modbus = ModbusClient(method='rtu', port=serialPort, baudrate=9600, timeout=1)
            self.modbus.connect()
        except:
            logging.error(__class__.__name__ + ":Error de conexión Modbus")
            traceback.print_exc()
            return False
        self.datos = {}
        self.timeBd = time.time()
        self.bd = Bd()
        self.csvfv = CsvFv(self.archivoCvs)
    
    ##
    # convierte el estado del regulador
    # @param codigo (byte)
    # @return (string) estado del regulador
    def getEstado (self, codigo):
        if 0 > codigo > 6: return None
        else:
            estados = { 0 : "DEACTIVATED",
                        1 : "ACTIVATED",
                        2 : "BULK",
                        3 : "EQUALIZE",
                        4 : "ABSORTION",
                        5 : "FLOAT",
                        6 : "LIMITING"
                        }
            return estados[codigo]
            
    ##
    # Guardar datos en archivo ram y base de datos
    def guardarDatos (self):
        # escribir archivo ram
        self.csvfv.escribirCsv(self.datos)

        # escribir en la bd si ha pasado eltiempo estipulado
        if time.time() - self.timeBd >= FREQ_BD:
            datosBd = self.datos
            del datosBd["Tiempo_sg"] # no guardamos este campo en la bd
            self.bd.insert("srne", self.datos)
            self.timeBd = time.time()
        
    ##
    # Lectura de registros por modbus y almacenamiento
    def leerRegistros(self):
        while True:
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_sg = time.time()
            # Lectura de registros
            try:
                R_Vbat = self.modbus.read_holding_registers(0x0101, 2, unit=1)
                R_Vplaca = self.modbus.read_holding_registers(0x0107, 2, unit=1)
                R_Iplaca = self.modbus.read_holding_registers(0x0102, 2, unit=1)
                R_Est = self.modbus.read_holding_registers(0x0120, 2, unit=1)
                time.sleep(FREQ_MUESTREO)
            except:
                traceback.print_exc()
                logging.warning (__class__.__name__ + ":Error lectura SRNE")
                #break # para poder parar con crtl+c

            # Procesado de los datos    
            if not (R_Vbat.isError() or R_Vplaca.isError() or \
                    R_Iplaca.isError() or R_Est.isError()):
                Vbat = R_Vbat.registers[0]/10
                Vplaca = R_Vplaca.registers[0]/10
                Iplaca = R_Iplaca.registers[0]/100
                est = R_Est.registers[0]
                estInt = int(format(est, '02x')) # 8 lower bits
                Estado = self.getEstado(estInt)
                
                self.datos = {'Tiempo_sg':tiempo_sg, 'Tiempo':tiempo, 'Vbat':Vbat, 'Vplaca':Vplaca, 'Iplaca':Iplaca, 'Estado':Estado}
                self.guardarDatos()

                logging.info ("Datos: %s %s %s %s", str(Vbat), str(Vplaca), str(Iplaca), Estado)
            else:
                logging.warning (__class__.__name__ + ':Error lectura registros SRNE')

        self.modbus.close()
        self.bd.desconecta()
        

               
if __name__ == '__main__':
    #main(sys.argv[1:])
    logging.basicConfig(level=DEBUG_LEVEL)
    Srne(dev_srne).leerRegistros()
        
            
            


