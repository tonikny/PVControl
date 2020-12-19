# -*- coding: utf-8 -*-
#"""
#Created on Fri May  1 20:29:13 2020
#
#@author: Migue
#"""
#
import requests
from requests.exceptions import HTTPError
import json
import time
import pickle
import subprocess, sys
from Parametros_FV import *
from csvFv import CsvFv

DEBUG = False

if usar_fronius == 0:
        #print (commands.getoutput('sudo systemctl stop srne'))
        print (subprocess.getoutput('sudo systemctl stop fronius'))
        sys.exit()





    
class fronius:

    def __init__(self):
    
        self.dct = {}
        self.cmd_meter = 'http://' + IP_FRONIUS + '/solar_api/v1/GetPowerFlowRealtimeData.fcgi'
        self.cmd_inverter = 'http://' + IP_FRONIUS + '/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData'
        
        
    def read_data_meter(self):
    
        try:
        
            response = requests.get(self.cmd_meter)
            meter = json.loads(response.content)
            Wred = (-1)*float((meter['Body']['Data']['Site']['P_Grid']))
            Consumo = round((-1)*float((meter['Body']['Data']['Site']['P_Load'])),2)
            #print(Wred,Consumo)
            try:
                Wplaca = float((meter['Body']['Data']['Site']['P_PV']))
            except:
                Wplaca = 0
            if DEBUG: print('Wred',Wred,'Consumo',Consumo,'Wplaca',Wplaca)
            
            self.dct['Wred'] = Wred
            self.dct['Consumo'] = Consumo
            self.dct['Wplaca'] = Wplaca
            return self.dct
            
        except:
            
            if DEBUG: print('Error lectura meter')
            return None
            
            
    def read_data_inverter(self):
    
        try:
        
            response = requests.get(self.cmd_inverter)
            inverter = json.loads(response.content)
            #print('Vred',inverter)
            Vred = float((inverter['Body']['Data']['UAC']['Value']))
            Ired = float((inverter['Body']['Data']['IAC']['Value']))
            Vplaca = float((inverter['Body']['Data']['UDC']['Value']))
            #EFF = Pout(AC)/Pin(DC) * 100
            #Pin = Vi * Ii
            if Vplaca == None: Vplaca=0
            Pin = Vplaca * float((inverter['Body']['Data']['IDC']['Value']))
            try:
                EFF = round(((float((inverter['Body']['Data']['PAC']['Value'])) / Pin) * 100),2)
            except:
                EFF=100
                pass
            
            if DEBUG: print('Vred',Vred,'Vplaca',Vplaca)
            
            self.dct['Vred'] = Vred
            self.dct['Ired'] = Ired
            self.dct['Vplaca'] = Vplaca
            self.dct['EFF'] = EFF
            return self.dct
            
        except:
            
            if DEBUG: print('Error lectura inverter')
            self.dct['Vred'] = 230
            self.dct['Vplaca'] = 0
            self.dct['EFF'] = 100
            return self.dct

if __name__ == '__main__':
    #c = CsvFv('/run/shm/datos_fronius.csv') 
    
    while True:
        try:
            ve = fronius()           
            
            datos_inverter = ve.read_data_inverter()
            
            if usar_meter_fronius == 1:
                datos_meter = ve.read_data_meter()
                datos_inverter.update(datos_meter)                
                datos_inverter['Ired'] = datos_meter['Wred']/datos_inverter['Vred']
                datos_inverter['Vred'] = datos_inverter['Vred']
                datos_inverter['Iplaca'] = datos_meter['Wplaca']/datos_inverter['Vred']
                datos_inverter['Aux1'] = datos_meter['Wred']
                Temp = 0
                
            datos= datos_inverter
            
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_sg = time.time()
            
            datos['Tiempo'] = tiempo
            datos['Tiempo_sg'] = tiempo_sg
            
            #print(datos)
            if datos != None :
                with open('/run/shm/datos_fronius.pkl', mode='wb') as f:
                    pickle.dump(datos, f)      
             
            
            time.sleep(2)
            
        except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
            break
        except:
            #print("error no conocido")
            time.sleep(5)
            #sys.exit()
