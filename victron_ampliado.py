#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-01-09

import os, sys, time
import csv,traceback
from Parametros_FV import *
import MySQLdb 
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse

if usar_victron == 0:
    print (subprocess.getoutput('sudo systemctl stop victron'))
    sys.exit()

serialport = '/dev/ttyUSB0' # USB
#serialport = '/dev/ttyS0' # TTL
DEBUG = True

class srne:

    Estado = 'OFF'
        
    def __init__(self, serialport):
        self.modbus = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)
        self.modbus.connect()
        self.dict = {}
        
    def read_data_single(self):
        try:
            while True:
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                tiempo_sg = time.time()

                R_Vbat = self.modbus.read_holding_registers(0x0101, 2, unit=1)
                R_Vplaca = self.modbus.read_holding_registers(0x0107, 2, unit=1)
                R_Iplaca = self.modbus.read_holding_registers(0x0102, 2, unit=1)
                R_Estado = self.modbus.read_holding_registers(0x0120, 2, unit=1)
                R_Temp = self.modbus.read_holding_registers(0x0103, 2, unit=1)
                time.sleep(0.5)

                if not (R_Vbat.isError() or R_Vplaca.isError() or R_Iplaca.isError()):
                    Vbat = float(R_Vbat.registers[0])/10
                    Vplaca = float(R_Vplaca.registers[0])/10
                    Iplaca = float(R_Iplaca.registers[0])/100
                    Est = int(R_Estado.registers[0])
                    if Est == 0:  Estado = 'DEACTIVATED'
                    elif Est ==1: Estado = "ACTIVATED"
                    elif Est ==2: Estado = 'BULK'
                    elif Est ==3: Estado = 'EQUALIZE'
                    elif Est ==4: Estado = 'ABSORTION'
                    elif Est ==5: Estado = 'FLOAT'
                    elif Est ==6: Estado = 'LIMITING'
                    else: Estado = ''
                    x = format(R_Temp.registers[0], '04x')
                    Treg = int(x[:2])
                    Tbat = int(x[2:])
                    
                    #print (Treg,Tbat)
                    if DEBUG: print (Vbat, Vplaca, Iplaca, Estado,Treg,Tbat)
                else:
                    print ('Error lectura')
                
                try:
                    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                    cursor1 = db1.cursor()
                    cursor1.execute("""INSERT INTO victron (Tiempo,Iplaca,Vplaca,Vbat,Estado) VALUES(%s,%s,%s,%s,%s)""", (tiempo,Iplaca,Vplaca,Vbat,Estado))
                    db1.commit()
                except:
                    print ("Error grabando BD")

                with open('/run/shm/datos_victron.csv', mode='w') as f:
                    nombres = ['Tiempo_sg','Tiempo','Iplaca','Vplaca','Vbat']
                    datos = csv.DictWriter(f, fieldnames=nombres)
                    datos.writeheader()
                    datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Iplaca': Iplaca,
                                    'Vplaca':Vplaca, 'Vbat':Vbat, 'Estado':Estado})
                
                time.sleep(5)
                return self.dict

        except:
            print ("Error en while recolectando datos SRNE")

        self.modbus.close()


               
if __name__ == '__main__':
    grabar=0
    while True:    
        s = srne(dev_victron)
        datos = s.read_data_single()
        #print (datos)  #descomenta esta linea para ver la salida de datos en el terminal
        #time.sleep(3)

