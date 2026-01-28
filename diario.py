#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2023-08-08

# Creacion/actualización de los registros de la tabla diario...ejemplos

# python3 diario.py    ..............# genera/actualiza tabla diario del dia actual
# python3 diario.py -ini0 -fin0   ...# genera/actualiza tabla diario del dia actual

# python3 diario.py -ini0 -fin1   ...# genera/actualiza tabla diario del dia de ayer y dia actual
# python3 diario.py -ini0 -fin365   ...# genera/actualiza tabla diario de 365 dias desde el dia actual


import MySQLdb
import time,sys

from datetime import date,timedelta

from Parametros_FV_DIST import *
from Parametros_FV import *

inicio = fin = 0
DEBUG = False
if '-p' in sys.argv: DEBUG = True 
for t in sys.argv:
    if t[:4].upper() == '-INI': inicio = int(t[4:])
    if t[:4].upper() == '-FIN': fin = int(t[4:])
    

def logBD(log) :
    try:
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,log))
        #print (tiempo,' ', log)
        db.commit()
    except:
        db.rollback()
        #print (tiempo,'Error en logBD()')
    
    return

def act_diario(ndias):

    d = date.today() - timedelta(ndias)
    rango1 = str(d) + ' 00:00:00'
    rango2 = str(d) + ' 23:59:59'

    if DEBUG: print (rango1, rango2)

    try:

        sql = "SELECT MAX(DATE(Tiempo)), MAX(Vbat), MIN(Vbat), AVG(Vbat), MAX(SOC), MIN(SOC), AVG(SOC), \
            MAX(Ibat), MIN(Ibat), AVG(Ibat), MAX(Iplaca), AVG(Iplaca), MAX(Wh_placa), \
            MAX(Whp_bat), MAX(Whn_bat), MAX(Wh_placa-(Whp_bat-Whn_bat)-(Whp_red-Whn_red)), MAX(Temp), MIN(Temp), AVG(Temp), \
            MAX(Whp_red), MAX(Whn_red), MAX(Wred), MIN(Wred),AVG(Wred),MAX(Vred), MIN(Vred) \
            FROM datos WHERE Tiempo BETWEEN '" + rango1 + "' AND '" + rango2 +"'"


        cursor.execute(sql)
        var=cursor.fetchall()
        
        if var[0][0] == None : nreg_datos = '0'
        else : nreg_datos = '1'
        
        if DEBUG: print (var)
    except:
        print (tiempo,"Error, la base de datos no existe")

    if nreg_datos == '0' : return 'Sin datos'
    
    try:
        sql = f"SELECT DATE(Fecha) FROM diario WHERE DATE(Fecha) = SUBDATE(CURDATE(),{ndias})"
        cursor.execute(sql)
        var1=cursor.fetchone()
        nreg=cursor.rowcount
        #print ('Nreg=',nreg)
        
        if nreg==0:
            nreg_datos = 'Insert'
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
                logBD(f'Registro diario del {d} creado')

            except:
                db.rollback()
                logBD(f'Error en la creacion del registro diario del {d}')
        else:
            nreg_datos = 'Update'
            try:
                cursor.execute("""UPDATE diario SET
                    maxVbat=%s,minVbat=%s,avgVbat=%s  ,maxSOC=%s   , minSOC=%s  ,avgSOC=%s ,maxIbat=%s,
                    minIbat=%s,avgIbat=%s,maxIplaca=%s,avgIplaca=%s, Wh_placa=%s,Whp_bat=%s,
                    Whn_bat=%s,Wh_consumo=%s,maxTemp=%s,minTemp=%s,avgTemp=%s,Whp_red=%s,
                    Whn_red=%s,maxWred=%s,minWred=%s,avgWred=%s,maxVred=%s,minVred=%s
                    WHERE Fecha=%s""", 
                    (round(var[0][1],2),round(var[0][2],2) ,round(var[0][3],2) ,round(var[0][4],2) ,
                    round(var[0][5],2) ,round(var[0][6],2) ,round(var[0][7],2) ,round(var[0][8],2) ,
                    round(var[0][9],2) ,round(var[0][10],2),round(var[0][11],2),round(var[0][12],2),
                    round(var[0][13],2),round(var[0][14],2),round(var[0][15],2),round(var[0][16],2),
                    round(var[0][17],2),round(var[0][18],2),round(var[0][19],2),round(var[0][20],2),
                    round(var[0][21],2),round(var[0][22],2),round(var[0][23],2),round(var[0][24],2),
                    round(var[0][25],2),var[0][0]))

                db.commit()
                if DEBUG: logBD(f'Registro diario del {d} actualizado')

            except:
                print (f'error en actualizacion diario del {d}')
                db.rollback()
                logBD('Error actualizacion registro diario del {d}')
    
    except:
        logBD('Error en tabla diario')
    
    return nreg_datos
        
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()

for nd in range(inicio,fin+1):
    nr = act_diario(nd)
    print (date.today() - timedelta(nd), '--', nr)
    
    
cursor.close()
db.close()
