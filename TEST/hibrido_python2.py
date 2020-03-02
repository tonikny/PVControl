#!/usr/bin/python
# -*- coding: utf-8 -*-

# Versión 2019-03-14

import os, sys, time, commands
import timeout_decorator

from crc16 import crc16xmodem
from struct import pack
from traceback import format_exc

import MySQLdb 
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token
import paho.mqtt.client as mqtt

import csv

from Parametros_FV import *

if usar_hibrido == 0:
    print commands.getoutput('sudo systemctl stop hibrido')
    sys.exit()

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
    bot.send_message(cid, 'Arrancando Programa Control Hibrido')


# -----------------------MQTT MOSQUITTO ------------------------

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("PVControl/Hibrido")
    client.subscribe("PVControl/Hibrido/Opcion") # Ya vere para que
    
 
def on_disconnect(client, userdata, rc):
        if rc != 0:
            print "Desconexion MQTT.... intentando reconexion"
        else:
            client.loop_stop()
            client.disconnect()

def on_message(client, userdata, msg):
    global hora,t_muestra,nbucle

    try:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        hora_ant= hora
        hora = time.time()
        print int(hora-hora_ant),
        if nbucle > 0:
            nbucle -= 1
        
        #print(msg.topic+" "+str(msg.payload))
        
        if msg.topic== "PVControl/Hibrido":
            cmd=str(msg.payload)#.upper()

            r= comando(cmd)
            #print r
            
            if cmd == 'QPIGSBD' and len(r) >= 24:
                ##########################################################################
                #            CAMBIAR INDICES  DE r[] DEPENDIENDO DEL MODELO DE HIBRIDO
                ##########################################################################
                Iplaca = r[15]
                Vplaca = r[16]
                Wplaca = r[22]

                Vbat = r[11]
                Vbus = r[10]

                Ibatp = r[12]
                Ibatn = r[18]

                PACW = r[8]
                PACVA = r[7]

                Temp = r[14]

                Flot = r[23][0]
                OnOff = r[23][1]
                ##########################################################################
                
                client.publish("PVControl/Hibrido/Iplaca",Iplaca)
                client.publish("PVControl/Hibrido/Vplaca",Vplaca)
                client.publish("PVControl/Hibrido/Wplaca",Wplaca)

                client.publish("PVControl/Hibrido/Vbat",Vbat)
                client.publish("PVControl/Hibrido/Vbus",Vbus)
                
                client.publish("PVControl/Hibrido/Ibatp",Ibatp)
                client.publish("PVControl/Hibrido/Ibatn",Ibatn)

                client.publish("PVControl/Hibrido/PACW",PACW)
                client.publish("PVControl/Hibrido/PACVA",PACVA)
                
                client.publish("PVControl/Hibrido/Temp",Temp)
                             
                client.publish("PVControl/Hibrido/Flot",Flot)
                client.publish("PVControl/Hibrido/OnOff",OnOff)

                if grabar_datos_hibrido == 1:
                    try:
                        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor1 = db1.cursor()
                        cursor1.execute("""INSERT INTO hibrido (Tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,
                                                                PACW,PACVA,Temp,Flot,OnOff)
                                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                        (tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,PACW,PACVA,Temp,Flot,OnOff))
                        db1.commit()
                    except:
                        db1.rollback()
                        print 'error grabacion tabla hibrido'
                        print tiempo, r
                    try:
                        cursor1.close()
                        db1.close()
                    except:
                        pass

                try:
                    with open('/run/shm/datos_hibrido.csv', mode='w') as f:
                        nombres = ['Tiempo_sg','Tiempo','Iplaca', 'Vplaca', 'Wplaca','Vbat','Vbus','Ibatp','Ibatn','PACW','PACVA','Temp','Flot','OnOff']
                        datos = csv.DictWriter(f, fieldnames=nombres)
                        datos.writeheader()
                        datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Iplaca': Iplaca,'Vplaca': Vplaca,'Wplaca': Wplaca,
                         'Vbat': Vbat,'Vbus':Vbus,'Ibatp':Ibatp,'Ibatn':Ibatn,
                         'PACW':PACW,'PACVA':PACVA,'Temp':Temp,'Flot':Flot,'OnOff':OnOff})
                except:
                    print 'Error grabacion fichero datos_hibrido.csv'

                    
            elif cmd == 'QPIGSBD':
                print 'X',
                pass

            else:
                print r, len(r) 
                client.publish("PVControl/Hibrido/Respuesta",str(r))
                if usar_telegram == 1: 
                    L1 = 'Comando Recibido ='+ cmd
                    L2 = str(r)
                    tg_msg = L1+'\n'+L2
                    print tg_msg 
                    bot.send_message(cid, tg_msg)
            
    except:
        print 'error en on_message'

client = mqtt.Client("hibrido") #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()

# ---- Comandos HIBRIDO

@timeout_decorator.timeout(10, use_signals=False)
def comando(cmd):
    global t_muestra
    cmd1 = cmd

    try:
        #print 'Comando'
        if cmd1 == "ERROR":
            while True:
                time.sleep(1)

        if cmd1 == 'QPIGSBD':
            cmd1 = 'QPIGS'
                        
        if usar_crc == 1:
            if cmd1 == "POP02":   # ERROR firmware - CRC correcto es: 0xE2 0x0A
                cmd_crc = '\x50\x4f\x50\x30\x32\xe2\x0b\x0d'
            else:
                checksum = crc16xmodem(cmd1)
                cmd_crc = cmd1 + pack('>H', checksum) + '\r'
        else:
            cmd_crc = cmd1 + '\r'
                
        if os.path.exists(dev_hibrido):
            fd = open(dev_hibrido,'r+')
            time.sleep(.15)
            
            fd.write(cmd_crc[:8])
            if len(cmd_crc) > 8:
                fd.flush()
                fd.write(cmd_crc[8:])
            time.sleep(.15)
            r = fd.read(8).encode('string-escape')
            while r.find('r') == -1 :
                time.sleep(.15)
                r = r + fd.read(8).encode('string-escape')
                
                
            r = time.strftime("%Y-%m-%d %H:%M:%S")+ " "+cmd+" "+r
            s1 = r.split("\\")
            s = s1[0][0:].split(" ")
            s[3]=s[3][1:] #quito el parentesis inicial de la respuesta
            #print s
            t_muestra=5
    
    except:
        #print'Error Comando ',
        t_muestra=12
        s = 'Error Hibrido'
        
    finally:
        #print 'finally'
        try:
            fd.close()
        except:
            pass
        #print s
        return s

        
##### Bucle infinito  ######################
hora = time.time()

client.publish('PVControl/Hibrido/Respuesta','Arrancando Control Hibrido')
t_muestra = 5
nbucle=0

while True:
    nbucle+=1
    time.sleep(t_muestra)
    if nbucle < 6:
        client.publish('PVControl/Hibrido','QPIGSBD')       
    else:
        sys.exit()

    

# *** COMANDOS HIBRIDO ***

#Axpert Commands and examples
#QPI           8# Device protocol ID inquiry
#QID          18# The device serial number inquiry
#QVFW           # Main CPU Firmware version inquiry
#QVFW2          # Another CPU Firmware version inquiry
#QFLAG          # Device flag status inquiry
#QPIGS       110# Device general status parameters inquiry
                # GridVoltage, GridFrequency, OutputVoltage, OutputFrequency, OutputApparentPower, OutputActivePower, OutputLoadPercent, BusVoltage, BatteryVoltage, BatteryChargingCurrent, BatteryCapacity, InverterHeatSinkTemperature, PV-InputCurrentForBattery, PV-InputVoltage, BatteryVoltageFromSCC, BatteryDischargeCurrent, DeviceStatus,
#QMOD          5# Device mode inquiry P: PowerOnMode, S: StandbyMode, L: LineMode, B: BatteryMode, F: FaultMode, H: PowerSavingMode
#QPIWS          # Device warning status inquiry: Reserved, InverterFault, BusOver, BusUnder, BusSoftFail, LineFail, OPVShort, InverterVoltageTooLow, InverterVoltageTooHIGH, OverTemperature, FanLocked, BatteryVoltageHigh, BatteryLowAlarm, Reserved, ButteryUnderShutdown, Reserved, OverLoad, EEPROMFault, InverterSoftFail, SelfTestFail, OPDCVoltageOver, BatOpen, CurrentSensorFail, BatteryShort, PowerLimit, PVVoltageHigh, MPPTOverloadFault, MPPTOverloadWarning, BatteryTooLowToCharge, Reserved, Reserved
#QDI            # The default setting value information
#QMCHGCR        # Enquiry selectable value about max charging current
#QMUCHGCR       # Enquiry selectable value about max utility charging current
#QBOOT          # Enquiry DSP has bootstrap or not
#QOPM           # Enquiry output mode
#QPIRI       102# Device rating information inquiry - nefunguje
#QPGS0          # Parallel information inquiry
                # TheParallelNumber, SerialNumber, WorkMode, FaultCode, GridVoltage, GridFrequency, OutputVoltage, OutputFrequency, OutputAparentPower, OutputActivePower, LoadPercentage, BatteryVoltage, BatteryChargingCurrent, BatteryCapacity, PV-InputVoltage, TotalChargingCurrent, Total-AC-OutputApparentPower, Total-AC-OutputActivePower, Total-AC-OutputPercentage, InverterStatus, OutputMode, ChargerSourcePriority, MaxChargeCurrent, MaxChargerRange, Max-AC-ChargerCurrent, PV-InputCurrentForBattery, BatteryDischargeCurrent
#PEXXX          # Setting some status enable
#PDXXX          # Setting some status disable
#PF             # Setting control parameter to default value
#FXX            # Setting device output rating frequency
#POP02          # set to SBU
#POP01          # set to Solar First
#POP00          # Set to UTILITY
#PBCVXX_X       # Set battery re-charge voltage
#PBDVXX_X       # Set battery re-discharge voltage
#PCP00          # Setting device charger priority: Utility First
#PCP01          # Setting device charger priority: Solar First
#PCP02          # Setting device charger priority: Solar and Utility
#PGRXX          # Setting device grid working range
#PBTXX          # Setting battery type
#PSDVXX.X       # Setting battery cut-off voltage
#PCVVXX.X       # Setting battery C.V. charging voltage
#PBFTXX.X       # Setting battery float charging voltage
#PPVOCKCX       # Setting PV OK condition
#PSPBX          # Setting solar power balance
#MCHGC0XX       # Setting max charging Current          M XX
#MUCHGC002      # Setting utility max charging current  0 02
#MUCHGC010      # Setting utility max charging current  0 10
#MUCHGC020      # Setting utility max charging current  0 20
#MUCHGC030      # Setting utility max charging current  0 30
#POPMMX         # Set output mode       M 0:single, 1: parrallel, 2: PH1, 3: PH2, 4: PH3

"""
QBEQI          # Datos Ecualizacion
PBEQEn<cr>: Set battery equalization enable/disable. 
PBEQT<nnn><cr>: Set battery equalized time. 
PBEQP<nnn><cr>: Set the period of battery equalization.
PBEQMC<nnn><cr>: Set the max current of battery equalization. 
PBEQV<nn.nn><cr>: Set battery equalized voltage. 
PCVT<nnn><cr>: Set battery C.V. charge time. 
PBEQOT<nnn><cr>: Set the time of battery equalized timeout. 
"""

#notworking
#PPCP000        # Setting parallel device charger priority: UtilityFirst - notworking
#PPCP001        # Setting parallel device charger priority: SolarFirst - notworking
#PPCP002        # Setting parallel device charger priority: OnlySolarCharging - notworking






"""
#### Los que tienen 4# es que el COMANDO NO FUNCIONA

comando("QPI")
comando("QID")
####comando("QID2")
comando("QSID")
comando("QVFW")
comando("QVFW2")
comando("QVFW3")
comando("QVFW4")
comando("QMD")
comando("QPIRI")
####comando("QVFTR")
####comando("QPIHF")
####comando("QPICF")
####comando("QSVFW2")
comando("QPIGS")
####comando("Q3GV")
####comando("Q3GC")
####comando("Q3GW")
####comando("Q3AV")
####comando("Q3AC")
####comando("Q3AL")
#comando("Q3AW")

comando("QMOD")
comando("QFS")

####comando("QPIFS")
####comando("QSPIFS")
####comando("QTPIFS")
####comando("QT")
comando("QFLAG")
####comando("QFET")
####comando("QEY")
####comando("QEM")
####comando("QED")
####comando("QEH")
####comando("QBYV")
####comando("QBYF")
####comando("QGOV")
####comando("QGOF")
####comando("QOPMP")
#########comando("QMPPTV")
####comando("QMCHGCR")
####comando("QMUCHGCR")
#########comando("QPVIPV")
####comando("QLST")
####comando("QTPR")
comando("QDI")
####comando("QDI2")
comando("QPIWS") 
####comando("QSTS")
####comando("QGLTV";
####comando("QADI";
####comando("QVB";
####comando("QCHGC";
####comando("QMCC";
####comando("QII";
####comando("QPIBI";
####comando("QCHGS";
####comando("QPINBI";
####comando("QFT";
####comando("QDM";
####comando("T";

comando("SON"; encender UPS

####comando("SOFF";
####comando("TN";
####comando("CT";
####comando("BZOFF";
####comando("BZON";
####comando("Sn"; n minutos
####comando("SnRn";
####comando("CS";
####comando("TL";

    public static final String ST = "ST";

    public static final String EPO = "EPO";

    public static final String DPO = "DPO";

    public static final String CLR = "CLR";

    public static final String FGE = "FGE";

    public static final String FGD = "FGD";

    public static final String CHTH = "CHTH";

    public static final String CHTL = "CHTL";

    public static final String QCHT = "QCHT";

    public static final String POP = "POP";

    public static final String PCP = "PCP";

    public static final String PGR = "PGR";

    public static final String BATLOW = "BATLOW";

    public static final String BATUN = "PSDV";

    public static final String PBT = "PBT";

    public static final String F = "F";

    public static final String PE = "PE";

    public static final String PD = "PD";

    public static final String BATN = "BATN";

    public static final String BATCN = "BATCN";

    public static final String CHGC = "CHGC";

    public static final String DAT = "DAT";

    public static final String PSF = "PSF";

    public static final String PGF = "PGF";

    public static final String PLV = "PLV";

    public static final String PHV = "PHV";

    public static final String GOLF = "GOLF";

    public static final String GOHF = "GOHF";

    public static final String GOLV = "GOLV";

    public static final String GOHV = "GOHV";

    public static final String OPMP = "OPMP";

    public static final String MPPTHV = "MPPTHV";

    public static final String MPPTLV = "MPPTLV";

    public static final String PVIPHV = "PVIPHV";

    public static final String PVIPLV = "PVIPLV";

    public static final String LST = "LST";

    public static final String PF = "PF";

    public static final String GLTHV = "GLTHV";

    public static final String GLTLV = "GLTLV";

    public static final String GORV = "GORV";

    public static final String GORF = "GORF";

    public static final String V = "V";

    public static final String MCHGC = "MCHGC";

    public static final String MNCHGC = "MNCHGC";

    public static final String MCHGV = "MCHGV";

    public static final String PBCV = "PBCV";

    public static final String PBDV = "PBDV";

    public static final String F50 = "F50";

    public static final String F60 = "F60";

    public static final String ID = "ID";

    public static final String REEP = "REEP";

    public static final String VB = "VB";

    public static final String BPVA = "BPVA";

    public static final String BSVA = "BSVA";

    public static final String L1VA = "L1VA";

    public static final String L2VA = "L2VA";

    public static final String L3VA = "L3VA";

    public static final String SL1VA = "SL1VA";

    public static final String SL2VA = "SL2VA";

    public static final String SL3VA = "SL3VA";

    public static final String I1VA = "I1VA";

    public static final String I2VA = "I2VA";

    public static final String I3VA = "I3VA";

    public static final String P1VA = "P1VA";

    public static final String P2VA = "P2VA";

    public static final String P3VA = "P3VA";

    public static final String AUTO = "AUTO";

    public static final String DSPAR = "DSPAR";

    public static final String MCUAR = "MCUAR";

    public static final String FT = "FT";

    public static final String DM = "DM";

    public static final String PVN = "PVN";

    public static final String PPS = "PPS";

    public static final String QPPS = "QPPS";

    public static final String SOPF = "SOPF";

    public static final String QOPF = "QOPF";

    public static final String PDG = "PDG";

    public static final String QPDG = "QPDG";

    public static final String PPD = "PPD";

    public static final String QPPD = "QPPD";

    public static final String PFL = "PFL";

    public static final String QPFL = "QPFL";

    public static final String PCVV = "PCVV";

    public static final String PBFT = "PBFT";

    public static final String QPGSN = "QPGS";

    public static final String POPM = "POPM";

    public static final String PPCP = "PPCP";

    public static final String MUCHGCR = "MUCHGC";

    public static final String PPVOKC = "PPVOKC";

    public static final String PSPB = "PSPB";

    public static final String QPGSN0 = "QPGS0"

"""


