#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2022-05-02

import sys, time
import serial
import json
#import pickle

import subprocess
import MySQLdb


equipo = 'BMV'


###### Parametros por defecto .... NO CAMBIAR ----  modificar en fichero Parametros_FV.py #########

usar_bmv = 0              # 1 para leer datos victron ..... 0 para no usar
dev_bmv = "/dev/serial0"  # puerto donde reconoce la RPi al BMV

grabar_datos_bmv = 0      # 1 = Graba la tabla bmv... 0 = No graba

n_muestra_bmv = 5         # Numero de muestras para guardar en BD tabla bmv

##################################################################################


from Parametros_FV import *

if usar_bmv == 0:
    print ('apagando servicio BMV por no configurar equipo')
    print (subprocess.getoutput('sudo systemctl stop bmv')) #python3
    sys.exit()

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)

#Comprobacion argumentos en comando
DEBUG= 0
narg = len(sys.argv)
if '-p1' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios
elif '-p' in sys.argv: DEBUG= 100 


# Comprobacion BD

try:
    ee = '10'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
                              
    Sql = """CREATE TABLE IF NOT EXISTS `bmv` (
      `id` int(11) NOT NULL,
      `Tiempo` datetime NOT NULL COMMENT 'Fecha captura',
      `SOC` float NOT NULL DEFAULT 0 COMMENT 'SOC bateria',
      `Vbat` float NOT NULL DEFAULT 0 COMMENT 'Voltaje Bateria',
      `Vm` float NOT NULL DEFAULT 0 COMMENT 'Valor Medio Bateria',
      `Temp` float NOT NULL DEFAULT 0 COMMENT 'Temperatura',
      `Ibat` float NOT NULL DEFAULT 0 COMMENT 'Intensidad Bateria',
      
      PRIMARY KEY (`id`),
      KEY `Tiempo` (`Tiempo`)
      )  ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
       """
                    
    import warnings # quitamos el warning que da si existe la tabla
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(Sql)   
        db.commit()
    
    
    ee = '10b'
    try: #inicializamos registro en BD RAM
        cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                      (equipo,'"{}"'))
        db.commit()
    except:
        pass    
    
                                
except:
    print (Fore.RED,f'ERROR {ee} - inicializando BD RAM')
    sys.exit()


#archivo_ram = '/run/shm/datos_bmv.pkl'
    
nombresBD = {'Tiempo':'Tiempo','Vbat':'Vbat','Ibat':'Ibat','SOC':'SOC','Vm':'Vm','Temp':'Temp'}
datosBD = {}
grabar_BD = grabar_datos_bmv
n_grabar_BD = n_grabar_BD_cont = n_muestra_bmv

ser = serial.Serial(dev_bmv, 19200, timeout=5000)
crlf = '\r\n'
tab = '\t'
key = ''
value = ''
dct = {} 
    
flag_Vbat = 0
dia = time.strftime("%Y-%m-%d")
    
while True:
    try:
        dia_anterior = dia
        dia = time.strftime("%Y-%m-%d")

        if dia_anterior != dia: #cambio de dia
            dct = {} # borrar claves creadas por errores de transmision cada dia
            
        # Leer una linea
        try:
            ee=10
            data = ''
            data = ser.readline()
            ee=20
            #print ('data=',data)
            
            data=data.strip(b'\r\n')
            ee=30
            data=data.split(b'\t')
            #print ('data=',data, len(data))
        except:
            if DEBUG ==1: print (Fore.CYAN + time.strftime("%Y-%m-%d %H:%M:%S"),' - error readline ', ee, data)
            time.sleep(0.2)
            continue

        # Interpretar dato leido
        try:
            ee = 100
            if len(data) == 2:
                ee = 110
                if data[0] == b"V": 
                    dct["Vbat"] = float(data[1]) / 1000         # Vbat
                    flag_Vbat = 1
                elif data[0] == b"VPV": dct["Vplaca"] = float(data[1]) / 1000   # Vplaca
                elif data[0] == b"PPV": dct["Wplaca"] = float(data[1])          # Wplaca
                elif data[0] == b"I":   dct["Ibat"] = float(data[1]) / 1000     # Ibat
                elif data[0] == b"VM":  dct["Vm"] = float(data[1]) / 1000       # Vbat en punto medio
                elif data[0] == b"T":   dct["Temp"] = float(data[1])            # Temperatura
                elif data[0] == b"SOC": dct["SOC"] = float(data[1]) / 10        # SOC
                                   
                elif data[0].decode(encoding='UTF-8')[0]== "H": 
                    ee = 120
                    dct[data[0].decode(encoding='UTF-8')] = float(data[1])    ## distintas H*
                    
                elif data[0] == b"CS":
                    ee = 130
                    if int(data[1]) == 0: dct["CS"] = 'OFF'
                    elif int(data[1]) == 2: dct["CS"] = 'FALLO'
                    elif int(data[1]) == 3: dct["CS"] = 'BULK'
                    elif int(data[1]) == 4: dct["CS"] = 'ABS'
                    elif int(data[1]) == 5: dct["CS"] = 'FLOT'
                 
                    
                else:
                    ee= 190
                    if data[0] != b"Checksum":
                        dct[data[0].decode(encoding='UTF-8')] = data[1].decode(encoding='UTF-8')
                    
        except:
            print(Fore.RED+'pasa por donde no debe=',ee, '-- data=',data)
            time.sleep(0.2)
             
        # Grabar en BD
        ee = 200
        if flag_Vbat ==1:
            flag_Vbat = 0
       
            try:####  ARCHIVOS RAM en BD ############ 
                ee = 210
                #dct['Tiempo_sg'] = time.time()
                
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                #dct['Tiempo'] = tiempo
                
                salida = json.dumps(dct)
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo.upper()}'") # grabacion en BD RAM
                #print (Fore.BLUE+sql)
                cursor.execute(sql)
                
            except:
                print(Fore.RED+f'error {ee}, Grabacion tabla RAM equipos en {equipo.upper()}')
                print (salida)
            
            """    
            # guardar el fichero RAM (se eliminara en versiones posteriores
            ee = 220
            with open(archivo_ram, 'wb') as f:
                pickle.dump(dct, f)
            """
            
            
            # Salida DEBUG
            try:
                if DEBUG == 1:
                    print (Fore.RESET+f" {time.strftime('%H:%M:%S')} : Vbat= {dct['Vbat']:.3f}V - Ibat= {dct['Ibat']:.3f}A - SOC= {dct['SOC']:.2f}%")
                
                elif DEBUG ==100:
                    print(Fore.RESET+'=' * 50)
                    print (Fore.YELLOW+time.strftime("%H:%M:%S"), end='')
                    print (Fore.CYAN+ '--', dct) 
            except:
                pass
            
            ee = 230
            try:
                n_grabar_BD_cont -= 1
                #print ('------------ ',n_grabar_BD_cont,' ---------')
                if grabar_BD == 1 and n_grabar_BD_cont == 0:
                    n_grabar_BD_cont = n_grabar_BD
                    
                    # Adapto nombres de campos para BD
                    for i,j in zip (nombresBD.keys(),nombresBD.values()):
                        try:
                            #print (i,j)
                            datosBD[i]= dct[j]
                        except:
                            datosBD[i] = 0
                            
                    n_campos = ', '.join(['%s'] * len(datosBD))
                    campos = ', '.join(datosBD.keys())
                    sql = "INSERT INTO bmv ( %s ) VALUES ( %s )" % (campos, n_campos)
                    #print (sql,list(datosBD.values()))
                    cursor.execute(sql, list(datosBD.values()))

            except:
                print ('error grabacion BD', ee)
                
            db.commit()
            
            #time.sleep(0.2)
        
    except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
        ser.close()
        cursor.close()
        db.close()
        break
    except:
        print("error no conocido", ee)
        time.sleep(1)
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
