#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2020-01-09

"""
float I; // I Intensidad instantanea
float V; // V Voltaje instananeo
int P; //P potencia instantanea 
float SOC;// SOC estado de carga
float TTG;// TTG time to go
float CE;// Consumo Amp/h
int H1;//Profundidad descarga mÃ¡xima
int H5;//Numero de descargas completas
float H7;//Minimo voltaje bateria
"""
#import paho.mqtt.publish as publish, os, serial, sys, time
import  os, sys, time
import serial
import csv
import subprocess
from Parametros_FV import *
import MySQLdb 

if usar_victron == 0:
    print (subprocess.getoutput('sudo systemctl stop victron'))
    sys.exit()

Estado = 'OFF'
DEBUG = False #True

class bmv:

    def __init__(self, serialport):
        self.serialport = serialport
        self.ser = serial.Serial(serialport, 19200, timeout=5000)
        #self.ser = serial.Serial("dev/ttyUSB1", 19200, timeout=500)
        self.crlf = '\r\n'
        self.tab = '\t'
        self.key = ''
        self.value = ''
        self.dict = {}
        self.cont = 0

    def read_data_single(self):
        global grabar
        try:
            while True:
                data = self.ser.readline()
                data=data.strip('\r\n')
                data=data.split('\t')
                if data[0]=="V":
                    self.dict["V"]=data[1]
                    self.cont+=1
                elif data[0]=="VPV":
                    self.dict["VPV"]=data[1]
                    self.cont+=1
                elif data[0]=="PPV":
                    self.dict["PPV"]=data[1]
                    self.cont+=1
                elif data[0]=="I":
                    self.dict["I"]=data[1]
                    self.cont+=1
                elif data[0]=="H19":
                    self.dict["H19"]=data[1]
                    self.cont+=1
                elif data[0]=="H20":
                    self.dict["H20"]=data[1]
                    self.cont+=1
                elif data[0]=="H21":
                    self.dict["H21"]=data[1]
                    self.cont+=1
                elif data[0]=="H22":
                    self.dict["H22"]=data[1]
                    self.cont+=1
                elif data[0]=="CS":
                    self.dict["CS"]=data[1]
                    self.cont+=1
                
                if self.cont==9:
                    self.cont=0
                    grabar +=1
                    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                    tiempo_sg = time.time()
                    if DEBUG: print (self.dict)

                    Vbat = float(self.dict['V'])*0.001
                    Iplaca = float(self.dict['I'])*0.001
                    Vplaca = float(self.dict['VPV'])*0.001
                    Pplaca = float(self.dict['PPV'])
                    CS = int(self.dict['CS'])
                    if CS == 0:  Estado = 'OFF'
                    elif CS ==2: Estado = 'FAULT'
                    elif CS ==3: Estado = 'BULK'
                    elif CS==4:  Estado='ABSORTION'
                    elif CS==5:  Estado ='FLOAT'
                    if DEBUG: print (Estado)
                    
                    if grabar >=5:
                        grabar = 0
                        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor1 = db1.cursor()
                        cursor1.execute("""INSERT INTO victron (Tiempo,Iplaca,Vplaca,Vbat,Estado) VALUES(%s,%s,%s,%s,%s)""", (tiempo,Iplaca,Vplaca,Vbat,Estado))
                        db1.commit()
                    
                    with open('/run/shm/datos_victron.csv', mode='w') as f:
                        nombres = ['Tiempo_sg','Tiempo','Iplaca','Vplaca','Vbat']
                        datos = csv.DictWriter(f, fieldnames=nombres)
                        datos.writeheader()
                        datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Iplaca': Iplaca,
                                        'Vplaca':Vplaca, 'Vbat':Vbat})

                    return self.dict

        except:
            print ("Error en while recolectando datos victron")
            self.ser.close()


               
if __name__ == '__main__':
    grabar=0
    while True:    
        ve = bmv(dev_victron)
        datos = ve.read_data_single()
        #print (datos)  #descomenta esta linea para ver la salida de datos en el terminal
        #time.sleep(3)
