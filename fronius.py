# -*- coding: utf-8 -*-
#"""
#Version 17/Dic/21
#
#@author: Migue
#"""
#
crear_pkl = 0 # poner a 1 para versiones antiguas de PVControl que no usan BD en RAM


import requests
from requests.exceptions import HTTPError
import json
import time
import pickle
import subprocess, sys
import MySQLdb 

from Parametros_FV import *
#from csvFv import CsvFv

DEBUG = False
#Comprobacion argumentos en comando
if '-p' in sys.argv: DEBUG = True # para test .... realiza print en distintos sitios

if usar_fronius == 0:
    print (subprocess.getoutput('sudo systemctl stop fronius'))
    sys.exit()

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fronius.py') #+Style.RESET_ALL)
print()

    
class fronius:

    def __init__(self):
    
        self.dct = {}
        self.cmd_meter = 'http://' + IP_FRONIUS + '/solar_api/v1/GetPowerFlowRealtimeData.fcgi'
        self.cmd_inverter = 'http://' + IP_FRONIUS + '/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData'
        
    def read_data_meter(self):
    
        try:
        
            response = requests.get(self.cmd_meter)
            meter = json.loads(response.content)
            Wred = round((-1)*float((meter['Body']['Data']['Site']['P_Grid'])),2)
            Consumo = round((-1)*float((meter['Body']['Data']['Site']['P_Load'])),2)
            #print(Wred,Consumo)
            try:
                Wplaca = round(float((meter['Body']['Data']['Site']['P_PV'])),2)
            except:
                Wplaca = 0
            if DEBUG: print(Fore.GREEN+f' // METER: Wred={Wred:>6.1f} - Consumo={Consumo:>6.1f} - Wplaca= {Wplaca:>6.1f}')
            
            self.dct['Wred'] = Wred
            self.dct['Consumo'] = Consumo
            self.dct['Wplaca'] = Wplaca
            return self.dct
            
        except:
            
            if DEBUG: print(Fore.RED+'Error lectura meter')
            return None
            
            
    def read_data_inverter(self):
    
        try:
        
            response = requests.get(self.cmd_inverter)
            inverter = json.loads(response.content)
            #print('Vred',inverter)
            Vred = round(float((inverter['Body']['Data']['UAC']['Value'])),2)
            Ired = round(float((inverter['Body']['Data']['IAC']['Value'])),2)
            Vplaca = round(float((inverter['Body']['Data']['UDC']['Value'])),2)
            #EFF = Pout(AC)/Pin(DC) * 100
            #Pin = Vi * Ii
            if Vplaca == None: Vplaca=0
            Pin = Vplaca * float((inverter['Body']['Data']['IDC']['Value']))
            try:
                EFF = round(((float((inverter['Body']['Data']['PAC']['Value'])) / Pin) * 100),2)
            except:
                EFF=100
                pass
            
            if DEBUG: print(Fore.CYAN+f'INVERTER: Vred={Vred:>5.1f} - Vplaca={Vplaca:>5.1f}', end='')
            
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
    if usar_fronius == 1:
        try: #inicializamos BD
            # No se crea tabla especifica de fronius              
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            Sql = f""" CREATE TABLE IF NOT EXISTS `fronius` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `Tiempo` datetime NOT NULL,
              `xxxx` float NOT NULL DEFAULT 0,
              `yyyy` float NOT NULL DEFAULT 0,
              PRIMARY KEY (`id`),
              KEY `Tiempo` (`Tiempo`)
            ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci
            """                
            """
            import warnings # quitamos el warning que da si existe la tabla equipos
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cursor.execute(Sql)   
            db.commit()
            """
            try:
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                          ('FRONIUS','{}'))   
                db.commit()
            except:
                pass     
        except:
            print (Fore.RED+ 'ERROR inicializando BD RAM')
            sys.exit()
    
    while True:
        try:
            ve = fronius()           
            
            datos_inverter = ve.read_data_inverter()
            
            if usar_meter_fronius == 1:
                datos_meter = ve.read_data_meter()
                datos_inverter.update(datos_meter)                
                datos_inverter['Ired'] = round(datos_meter['Wred']/datos_inverter['Vred'],2)
                datos_inverter['Vred'] = round(datos_inverter['Vred'],2)
                datos_inverter['Iplaca'] = round(datos_meter['Wplaca']/datos_inverter['Vred'],2)
                datos_inverter['Aux1'] = round(datos_meter['Wred'],2)
                Temp = 0
                
            datos= datos_inverter
            
            tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
            tiempo_sg = time.time()
            
            datos['Tiempo'] = tiempo
            datos['Tiempo_sg'] = tiempo_sg
            
            #print(datos)
            if datos != None :
                if crear_pkl == 0:
                    try:####  ARCHIVOS RAM en BD ############ 
                        salida = json.dumps(datos)
                        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'FRONIUS'") # grabacion en BD RAM
                        cursor.execute(sql)
                        db.commit()
                    except:
                        print(Fore.RED+f'error, Grabacion tabla RAM equipos en FRONIUS')
                else:    
                    # lo logico es dejar de grabar el archivo pkl
                    with open('/run/shm/datos_fronius.pkl', mode='wb') as f:
                        pickle.dump(datos, f)      
                 
            
            time.sleep(2)
            
        except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
            break
        except:
            #print("error no conocido")
            time.sleep(5)
            #sys.exit()
