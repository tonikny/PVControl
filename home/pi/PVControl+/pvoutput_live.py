#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-12-15

from datetime import datetime
import requests, time
import MySQLdb

from Parametros_FV import *

PV_OUTPUT_URL_TEMPLATE = "https://pvoutput.org/service/r2/addstatus.jsp?key="+ pvoutput_key +"&sid=" + pvoutput_id +"&d={}&t={}&v1={}&v3={}&v5={}&v6={}"

def update_pvoutput():
    attempt = 0
    
    while(attempt < 5):
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)    
        cursor = db.cursor()
        sql='SELECT  Wh_placa, Whp_bat, Whn_bat, Vbat, Temp FROM datos ORDER BY id DESC LIMIT 1'
        cursor.execute(sql)
        energy_data=cursor.fetchone()

        energy_generated = int(energy_data[0])
        print ('energy_generated=',energy_generated)
        print ('Whp_bat=', int(energy_data[1]))
        print ('Whn_bat=', int(energy_data[2]))
        energy_consumed = energy_generated - (int(energy_data[1]) - int(energy_data[2]))
        print ('energy_consumed=',energy_consumed)
        Vbat = float(energy_data[3])
        print ('Vbat=', Vbat)
        Temp = float(energy_data[4])
        print ('Temp=', Temp)

        cursor.close()
        db.close()

        date = datetime.today().strftime('%Y%m%d')
        hora = time.strftime("%H:%M")


        PV_OUTPUT_URL = PV_OUTPUT_URL_TEMPLATE.format(date, hora, energy_generated, energy_consumed, Temp, Vbat)
        r = requests.get(PV_OUTPUT_URL)
        attempt += 1
        if(r.status_code != requests.codes.ok):
            time.sleep(3)
        else:
            break

if __name__ == '__main__':
    if usar_pvoutput == 1:
        update_pvoutput()
    else:
        print ("Registro PVoutput no actualizado -- Variable usar_pvoutput esta a 0 en Parametros_FV.py")
