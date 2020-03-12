#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------

import subprocess
import importlib

librerias = ['Adafruit_ADS1x15','pyModbusTCP','telebot','token','csv','glob','MySQLdb',
             'random','paho.mqtt.client','requests','Adafruit_SSD1306']

for i in librerias:
    try:
        print ('Chequeando libreria ',i, '.....',end='')
        module = importlib.import_module(i, package=None)
        print ( ' OK')
    except:
        print ('Libreria '+ i + ' NO encontrada..... se instala...', end='')
        ee = subprocess.getoutput("sudo pip3 install "+ i)
        print (' instalacion OK',ee)
        try:
            module = importlib.import_module(i, package=None)
            print ('Instalacion Libreria '+ i + ' comprobada')
        except:
            print ('Error en la instalacion de la libreria ' + i)


