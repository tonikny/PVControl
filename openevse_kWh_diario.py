#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb
import time
#import random # para simulacion usando random.choice

#import paho.mqtt.client as mqtt
from Parametros_FV import *

###### Parametros ############################

delay=1
update=0


tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
date = time.strftime("%Y-%m-%d")


def logBD() :
    try:
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,log))
        print (tiempo,' ', log)
        db.commit()
    except:
        db.rollback()
        print (tiempo,'Error en logBD()')

    return


try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    # Datos de Hoy
    sql="SELECT Fecha,Kwh_evse FROM open_evse_partial WHERE DATE(Fecha) = DATE(CURDATE()) ORDER BY Fecha"
    cursor.execute(sql)
    var=cursor.fetchall()
    nreg=cursor.rowcount


    # Sumamos los kWh de las posibles sesiones diarias de la tabla de parciales
    partial_kWh = var[0][1]
    total_kWh = 0
    for I in range(nreg):
        if var[I][1] >= partial_kWh:
            partial_kWh = var[I][1]
        else:
            total_kWh = total_kWh + partial_kWh
            partial_kWh = var[I][1]

    total_kWh = round(total_kWh + partial_kWh,2)

    #print ('Partial kWh:',partial_kWh)
    #print ('Total kWh:',total_kWh)

    # Datos de Hoy
    sql="SELECT DATE(Fecha),kWh_consumo3 FROM diario2 WHERE DATE(Fecha) = DATE(CURDATE())"
    cursor.execute(sql)
    var=cursor.fetchone()
    nreg_evse=cursor.rowcount

    if nreg_evse==0:
        try:
            cursor.execute("""INSERT INTO diario2 (Fecha,kWh_consumo3) VALUES(%s,%s)""",(date,total_kWh))  
            db.commit()
            update=1

        except:
            db.rollback()
            log='Error en la creacion del registro Evse'
            logBD()

    elif nreg_evse==1:
        try:
            cursor.execute("""UPDATE diario2 SET kWh_consumo3=%s WHERE Fecha=%s""",(total_kWh,date))
            db.commit()
            update=1

        except:
            db.rollback()
            log="Error en la actualizacion del registro Evse"
            logBD()

except:
    log='Error en tabla Evse(openevse_kWh_diario)'
    logBD()




