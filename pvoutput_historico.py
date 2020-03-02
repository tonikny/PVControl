#!/usr/bin/python

from datetime import datetime
import requests, time
import MySQLdb

from Parametros_FV import *

PV_OUTPUT_URL_TEMPLATE = "https://pvoutput.org/service/r2/addoutput.jsp?key=" + pvoutput_key + "&sid=" + pvoutput_id + "&d={}&g={}&c={}&tm={}&tx={}"

def update_pvoutput():
    
    for i in range (50, 100):
        attempt = 0
        while(attempt < 5): 

            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            
            sql='SELECT Fecha, kWh_placa, kWh_consumo, minTemp, maxTemp FROM diario WHERE Fecha=(DATE_SUB(curdate(), INTERVAL '
            sql=sql+str(i)+' DAY))'

            print sql
            time.sleep(5)
            
            cursor.execute(sql)
            energy_data=cursor.fetchone()

            print energy_data

            date = energy_data[0].strftime('%Y%m%d')
            energy_generated = int(energy_data[1])
            energy_consumed = int(energy_data[2])
            minTemp = float(energy_data[3])
            maxTemp = float(energy_data[4])

            cursor.close()
            db.close()

            PV_OUTPUT_URL = PV_OUTPUT_URL_TEMPLATE.format(date, energy_generated, energy_consumed, minTemp, maxTemp)

            print PV_OUTPUT_URL
            
            r = requests.get(PV_OUTPUT_URL)
            attempt += 1
            if(r.status_code != requests.codes.ok):
                time.sleep(3)
            else:
                break

if __name__ == '__main__':
    update_pvoutput()

