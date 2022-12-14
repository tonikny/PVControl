#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2019-12-15

import MySQLdb
import time 

from Parametros_FV import *

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
rango1 = time.strftime('%Y-%m-%d 00:00:00')
rango2 = time.strftime('%Y-%m-%d 23:59:59')


def logBD() :
    try:
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,log))
        #print (tiempo,' ', log)
        db.commit()
    except:
        db.rollback()
        #print (tiempo,'Error en logBD()')
    
    return



try:

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

   
    sql="SELECT MAX(DATE(Tiempo)), MAX(Vbat), MIN(Vbat), AVG(Vbat), MAX(SOC), MIN(SOC), AVG(SOC), \
        MAX(Ibat), MIN(Ibat), AVG(Ibat), MAX(Iplaca), AVG(Iplaca), MAX(Wh_placa), \
        MAX(Whp_bat), MAX(Whn_bat), MAX(Wh_placa-(Whp_bat-Whn_bat)-(Whp_red-Whn_red)), MAX(Temp), MIN(Temp), AVG(Temp), \
        MAX(Whp_red), MAX(Whn_red), MAX(Wred), MIN(Wred),AVG(Wred),MAX(Vred), MIN(Vred) \
        FROM datos WHERE Tiempo BETWEEN '" + rango1 + "' AND '" + rango2 +"'"
        
    print(sql)
    
    cursor.execute(sql)
    var=cursor.fetchall()
    
except Exception as e:

    print (tiempo,"Error, la base de datos no existe")


try:
    sql="SELECT DATE(Fecha) FROM diario WHERE DATE(Fecha) = DATE(CURDATE())"
    cursor.execute(sql)
    var1=cursor.fetchone()
    nreg=cursor.rowcount
    #print ('Nreg=',nreg)
    
    if nreg==0:
        try: # 26 campos
            cursor.execute("""INSERT INTO diario (Fecha,maxVbat,minVbat,avgVbat,maxSOC,minSOC,avgSOC,maxIbat,minIbat,
                avgIbat,maxIplaca,avgIplaca,Wh_placa,Whp_bat,Whn_bat,Wh_consumo,maxTemp,minTemp,avgTemp,
                Whp_red,Whn_red,maxWred,minWred,avgWred,maxVred,minVred) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                (var[0][0]         ,round(var[0][1],2) ,round(var[0][2],2) ,round(var[0][3],2) ,round(var[0][4],2) ,
                round(var[0][5],2) ,round(var[0][6],2) ,round(var[0][7],2) ,round(var[0][8],2) ,round(var[0][9],2) ,
                round(var[0][10],2),round(var[0][11],2),round(var[0][12],2),round(var[0][13],2),round(var[0][14],2),
                round(var[0][15],2),round(var[0][16],2),round(var[0][17],2),round(var[0][18],2),round(var[0][19],2),
                round(var[0][20],2),round(var[0][21],2),round(var[0][22],2),round(var[0][23],2),round(var[0][24],2),
                round(var[0][25],2) ))

            db.commit()    
            log='Registro diario creado'
            logBD()

        except:
            db.rollback()
            log='Error en la creacion del registro diario'
            logBD()
    else:
        try:
            cursor.execute("""UPDATE diario SET maxVbat=%s,minVbat=%s,avgVbat=%s,maxSOC=%s,
                minSOC=%s,avgSOC=%s,maxIbat=%s,minIbat=%s,avgIbat=%s,maxIplaca=%s,avgIplaca=%s,
                Wh_placa=%s,Whp_bat=%s,Whn_bat=%s,Wh_consumo=%s,maxTemp=%s,minTemp=%s,
                avgTemp=%s,Whp_red=%s,Whn_red=%s,maxWred=%s,minWred=%s,avgWred=%s,maxVred=%s,minVred=%s
                WHERE Fecha=%s""", 
                (round(var[0][1],2),round(var[0][2],2) ,round(var[0][3],2) ,round(var[0][4],2) ,
                round(var[0][5],2) ,round(var[0][6],2) ,round(var[0][7],2) ,round(var[0][8],2) ,
                round(var[0][9],2) ,round(var[0][10],2),round(var[0][11],2),round(var[0][12],2),
                round(var[0][13],2),round(var[0][14],2),round(var[0][15],2),round(var[0][16],2),
                round(var[0][17],2),round(var[0][18],2),round(var[0][19],2),round(var[0][20],2),
                round(var[0][21],2),round(var[0][22],2),round(var[0][23],2),round(var[0][24],2),
                round(var[0][25],2),var[0][0]))

            db.commit()
            #log='Registro diario actualizado'
            #logBD()

        except:
        
            db.rollback()

            log="Error en la actualizacion del registro diario"
            logBD()
except:
    log='Error en tabla diario'
    logBD()
    

        
