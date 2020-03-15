#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-03-09

import  sys, time
#import os
import serial
from csvFv import CsvFv

import subprocess

from Parametros_FV import *

import MySQLdb

if usar_bmv == 0:
    print ('apagando servicio BMV por no configurar equipo')
    print (subprocess.getoutput('sudo systemctl stop bmv')) #python3
    sys.exit()

class bmv:

    def __init__(self, serialport):
        self.serialport = serialport
        self.ser = serial.Serial(serialport, 19200, timeout=5000)
        self.crlf = '\r\n'
        self.tab = '\t'
        self.key = ''
        self.value = ''
        self.dct = {}
        
    def read_data_single(self):
        try:
            flag_Vbat = 0
            while True:
                try:
                    ee=10
                    data = self.ser.readline()
                    ee=20
                    #print ('data=',data)
                    
                    data=data.strip(b'\r\n')
                    ee=30
                    data=data.split(b'\t')
                    #print ('data=',data, len(data))
                except:
                    print (time.strftime("%Y-%m-%d %H:%M:%S"),' - error readline ', ee, data)
                    self.ser.close()
                    time.sleep(0.2)
                    return None
                    
                try:
                    if len(data) == 2:
                        ee = 100
                        if data[0] == b"V": 
                            self.dct["Vbat"] = float(data[1]) / 1000         # Vbat
                            flag_Vbat = 1
                        elif data[0] == b"VPV": self.dct["Vplaca"] = float(data[1]) / 1000   # Vplaca
                        elif data[0] == b"PPV": self.dct["Wplaca"] = float(data[1])          # Wplaca
                        elif data[0] == b"I":   self.dct["Ibat"] = float(data[1]) / 1000     # Ibat
                        elif data[0] == b"VM":  self.dct["Vm"] = float(data[1]) / 1000       # Vbat en punto medio
                        elif data[0] == b"T":   self.dct["Temp"] = float(data[1])            # Temperatura
                        elif data[0] == b"SOC": self.dct["SOC"] = float(data[1]) / 10        # SOC
                                           
                        elif data[0].decode(encoding='UTF-8')[0]== "H": 
                            ee = 200
                            self.dct[data[0].decode(encoding='UTF-8')] = float(data[1])    ## distintas H*
                            
                        elif data[0] == b"CS":
                            ee = 300
                            if int(data[1]) == 0: self.dct["CS"] = 'OFF'
                            elif int(data[1]) == 2: self.dct["CS"] = 'FALLO'
                            elif int(data[1]) == 3: self.dct["CS"] = 'BULK'
                            elif int(data[1]) == 4: self.dct["CS"] = 'ABS'
                            elif int(data[1]) == 5: self.dct["CS"] = 'FLOT'
                         
                        elif data[0] == b'Checksum' and flag_Vbat == 1:
                            ee = 400
                            flag_Vbat = 0
                            self.dct['Tiempo_sg'] = time.time()
                            self.dct['Tiempo'] = time.strftime("%Y-%m-%d %H:%M:%S")
                            return self.dct
                            
                        else:
                            ee= 900 
                            self.dct[str(data[0])] = str(data[1])  # resto campos
                        
                except:
                    print('pasa por donde no debe=',ee)
                    time.sleep(0.2)
                    pass 
                
        except:
            print ("Error recolectando datos bmv", ee, ' data=',data, len(data))
            #self.ser.close()
            time.sleep(0.5)
            #self.ser = serial.Serial(serialport, 19200, timeout=5000)


if __name__ == '__main__':
    c = CsvFv('/run/shm/datos_bmv.csv')
    
    nombresBD = {'Tiempo':'Tiempo','Vbat':'Vbat','Ibat':'Ibat','SOC':'SOC','Vm':'Vm','Temp':'Temp'}
    datosBD = {}
    grabar_BD = grabar_datos_victron
    n_grabar_BD = n_grabar_BD_cont = 5
    
    while True:
        try:
            ee=10
            ve = bmv(dev_bmv)
            ee=20
            datos = ve.read_data_single()
            ee=30
            if datos != None :
                c.escribirCsv(datos)
                #print (datos) #descomenta esta linea para ver la salida completa de datos en el terminal
                #print ('--------------')
                
                try:
                    #print (datos['Tiempo'],' - Vbat=',datos['Vbat'],' - Ibat=',datos['Ibat'])
                    
                    n_grabar_BD_cont -= 1
                    #print ('------------ ',n_grabar_BD_cont,' ---------')
                    if grabar_BD == 1 and n_grabar_BD_cont == 0:
                        n_grabar_BD_cont = n_grabar_BD
                        
                        # Adapto nombres de campos para BD
                        for i,j in zip (nombresBD.keys(),nombresBD.values()):
                            try:
                                #print (i,j)
                                datosBD[i]= datos[j]
                            except:
                                datosBD[i] = 0
                                
                        #del dict['Tiempo_sg']
                        #print ('-------------------BD---------------------------')
                        #print (datosBD)
                        #print ('-------------')
                    
                        
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
                        n_campos = ', '.join(['%s'] * len(datosBD))
                        campos = ', '.join(datosBD.keys())
                        sql = "INSERT INTO bmv ( %s ) VALUES ( %s )" % (campos, n_campos)
                        #print (sql,list(datosBD.values()))
                        cursor.execute(sql, list(datosBD.values()))

                        db.commit()
                        cursor.close()
                        db.close()

                except:
                    print ('error grabacion BD')
                    pass
            else:
                print('no hay datos',ee)
            #print ('..........')
            time.sleep(0.2)
        except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
            break
        except:
            print("error no conocido", ee)
            #sys.exit()
        
"""
    units[V]="mV";            descr[V]="Voltage" # descr[V]="Main (battery) voltage"
    units[VS]="mV";           descr[VS]="Auxiliary (starter) voltage"
    units[VM]="mV";           descr[VM]="Mid-point voltage of the battery bank"
    units[DM]=".1%";          descr[DM]="Mid-point deviation of the battery bank"
    units[VPV]="mV";          descr[VPV]="Panel voltage"
    units[PPV]="Watts";       descr[PPV]="Panel power"
    units[I]="mA";            descr[I]="Current" # descr[I]="Battery current"
    units[IL]="mA";           descr[IL]="Load current"
    units[LOAD]="none";       descr[LOAD]="Load output state (ON/OFF)"
    units[T]="degC";          descr[T]="Battery temp." #  descr[T]="Battery temperature"
    units[P]="Watts";         descr[P]="Instantaneous power"
    units[Pcalc]=".01Watts";  descr[Pcalc]="Power" # synthesized from V and I
    units[CE]="mAh";          descr[CE]="Charge consumed" # descr[CE]="Consumed Amp Hours"
    units[SOC]=".1%";         descr[SOC]="Capacity left" # descr[SOC]="State-of-charge"
    units[TTG]="minutes";     descr[TTG]="Time left" # descr[TTG]="Time-to-go"
    units[Alarm]="none";      descr[Alarm]="Alarm condition active"
    units[Relay]="none";      descr[Relay]="Relay state"
    units[AR]="alarm";        descr[AR]="Alarm reason"
    units[ARstring]="alarm";  descr[ARstring]="Alarm reason" # synthesized
    units[H1]="mAh";          descr[H1]="Depth of the deepest discharge"
    units[H2]="mAh";          descr[H2]="Depth of the last discharge"
    units[H3]="mAh";          descr[H3]="Depth of the average discharge"
    units[H4]="none";         descr[H4]="Number of charge cycles"
    units[H5]="none";         descr[H5]="Number of full discharges"
    units[H6]="mAh";          descr[H6]="Cumulative Amp Hours drawn"
    units[H7]="mV";           descr[H7]="Minimum main (battery) voltage"
    units[H8]="mV";           descr[H8]="Maximum main (battery) voltage"
    units[H9]="seconds";      descr[H9]="Time since full" # descr[H9]="Number of seconds since last full charge"
    units[H10]="none";        descr[H10]="Number of automatic synchronizations"
    units[H11]="none";        descr[H11]="Number of low main voltage alarms"
    units[H12]="none";        descr[H12]="Number of high main voltage alarms"
    units[H13]="none";        descr[H13]="Number of low aux. voltage alarms"
    units[H14]="none";        descr[H14]="Number of high aux. voltage alarms"
    units[H15]="mV";          descr[H15]="Minimum auxiliary (battery) voltage"
    units[H16]="mV";          descr[H16]="Maximum auxiliary (battery) voltage"
    units[H17]=".01kWh";      descr[H17]="Amount of discharged energy"
    units[H18]=".01kWh";      descr[H18]="Amount of charged energy"
    units[H19]=".01kWh";      descr[H19]="Yield total (user resettable counter)"
    units[H20]=".01kWh";      descr[H20]="Yield today"
    units[H21]="Watts";       descr[H21]="Maximum power today"
    units[H22]=".01kWh";      descr[H22]="Yield yesterday"
    units[H23]="Watts";       descr[H23]="Maximum power yesterday"
    units[ERR]="none";        descr[ERR]="Error code"
    units[CS]="none";         descr[CS]="State of operation"
    units[BMV]="ignore";      descr[BMV]="Model description (deprecated)"
    units[FW]="none";         descr[FW]="Firmware version"
    units[PID]="product";     descr[PID]="Product ID"
    units["SER#"]="none";     descr["SER#"]="Serial number"
    units[HSDS]="none";       descr[HSDS]="Day sequence number (0..364)"
    units[MODE]="none";       descr[MODE]="Device mode"
    units[AC_OUT_V]=".01V";   descr[AC_OUT_V]="AC output voltage"
    units[AC_OUT_I]=".1A";    descr[AC_OUT_I]="AC output current"
    units[WARN]="none";       descr[WARN]="Warning reason"
    units[TIME]="daytime";    descr[TIME]="Time" # synthesized
    units[Tstart]="minutes";  descr[Tstart]="Time since engine start" # synthesized
    units[Checksum]="ignore"; descr[Checksum]="Checksum"  # ignored

    # Alarm reason (AR) bits:
    alarm[0]="lowV";     # Low Voltage            # both
    alarm[1]="highV";    # High Voltage           # both
    alarm[2]="low%";     # Low SOC                # BMV only
    alarm[3]="lowAuxV";  # Low Starter Voltage    # BMV only
    alarm[4]="highAuxV"; # High Starter Voltage   # BMV only
    alarm[5]="lowT";     # Low Temperature        # both
    alarm[6]="lowT";     # High Temperature       # both
    alarm[7]="midV";     # Mid Voltage            # BMV only
    alarm[8]="ovrload";  # Overload               # inverter only
    alarm[9]="DCripple"; # DC-ripple              # inverter only
    alarm[10]="lowACV";  # Low V AC out           # inverter only
    alarm[11]="highACV"; # High V AC out          # inverter only
"""
