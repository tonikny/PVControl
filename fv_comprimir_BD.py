#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Version 2019-12-16

import sys, time, MySQLdb

#Parametros Instalacion FV
from Parametros_FV import *

#print (servidor, usuario,clave,basedatos)

bucle = True

while bucle:
    #print (bucle)
    ########## TABLA DATOS_C ############################

    ## RECUPERAR ULTIMO REGISTRO DE LA BD COMPRIMIDA ##
    try:
        ee = '0'
        #DATOS_C
        sql1='SELECT id,Tiempo FROM datos_c ORDER BY id DESC limit 1'
        ee = '1'
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        ee = '2'
        cursor1 = db.cursor()
        ee = '3'
        cursor1.execute(sql1)
        ee = '4'
        var=cursor1.fetchone()
        ee = '5'
        try:
            Id_max = int(var[0])
            ee = '6'
            Hora_BD = str(var[1])
            print ('Hora_BD datos_c =',Hora_BD, ' Id_max = ', Id_max)
        except:
            Id_max = 1
            Hora_BD = '2000-01-01 00:00:00'
            print ('Copia primer conjunto de registros')
       
        #DATOS 
        ee = '7'
        
        sql2 = ("SELECT MAX(id),MAX(Tiempo),AVG(Ibat),AVG(Vbat),AVG(SOC),AVG(DS),AVG(Aux1),AVG(Aux2),"+
                " MAX(Whp_bat),MAX(Whn_bat),AVG(Iplaca),AVG(Vplaca),AVG(Wplaca),MAX(Wh_placa),"+
                " AVG(Temp),AVG(PWM),MAX(Mod_bat)" +
                " FROM datos WHERE id > " + str(Id_max) + " AND id < " + str(Id_max + 10000) +
                " GROUP BY DAY(Tiempo),((60/5)*HOUR(TIME(Tiempo))+FLOOR(MINUTE(TIME(Tiempo))/5))" +
                " ORDER BY id " )
        
        ee = '8'
        cursor2 = db.cursor()
        ee = '9'
        nreg= cursor2.execute(sql2)
        ee = '10'
        nreg=int(nreg)  # numero de registros a actualizar
        print ('nreg datos=',nreg)
        
        TD=cursor2.fetchall()
        cursor2.close()

        if nreg <= 1 :
            bucle = False
            continue
        
        ee = '11'        
        for I in range(nreg-1):
            if I == 2 :
                print (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM)
            
            Id        = int(TD[I][0])
            Tiempo    = str(TD[I][1])
            Ibat      = round(float(TD[I][2]),2)
            Vbat      = round(float(TD[I][3]),2)
            SOC       = round(float(TD[I][4]),2)
            DS        = round(float(TD[I][5]),2)
            Aux1      = round(float(TD[I][6]),2)
            Aux2      = round(float(TD[I][7]),2)
            Whp_bat   = round(float(TD[I][8]),2)
            Whn_bat   = round(float(TD[I][9]),2)
            Iplaca    = round(float(TD[I][10]),2)
            Vplaca    = round(float(TD[I][11]),2)
            Wplaca    = round(float(TD[I][12]),2)
            Wh_placa  = round(float(TD[I][13]),2)
            Temp      = round(float(TD[I][14]),2)
            PWM       = int(TD[I][15])
            Mod_bat = str(TD[I][16])
            #print (Mod_bat, TD[I][16])
            
            #print (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat)
            ee = '13' 
            cursor1.execute("""INSERT INTO datos_c (id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat) 
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
               (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat))
            ee = '14' 
        
        print (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM,Mod_bat)
            
        print ()     
        db.commit()
             
        cursor1.close()
        db.close()
            
    except:
        print ("error copia tabla datos "+ ee)
        #texto= texto+'/datos'
        #logBD("error copia tabla datos")
        cursor1.close()
        
        db.close()
        bucle = False
    
