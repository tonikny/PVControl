#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time 
import MySQLdb 


###### Parametros Base de Datos
servidor = 'localhost'
usuario = 'rpi'
clave = 'fv' 

servidor_remoto = '192.168.191.10'#'192.168.1.10'
usuario_remoto = 'ext' 
clave_remoto = 'fv' 

basedatos = 'control_solar'

tiempo1 = time.strftime("%Y-%m-%d %H:%M:%S")

texto=''
max_registros=3000

# --------------------- DEFINICION DE FUNCIONES --------------

def logBD(texto) : # Incluir en tabla de Log
    try: 
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo1,texto))
        #print (tiempo1,' ', texto)
        db.commit()
    except:
        db.rollback()

    cursor.close()
    db.close()
    return


bucle = bucle1 = True

while bucle or bucle1:
    
    ########## TABLA DATOS ############################

    #print('Tabla Datos')

    try:
        ee = '0'
        # RECUPERAR ULTIMO REGISTRO DE LA BD LOCAL #

        sql='SELECT id,Tiempo FROM datos ORDER BY Tiempo DESC limit 1'
        ee = '1'
        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        ee = 'BD conexion local'
        cursor1 = db1.cursor()
        ee = 'BD cursor local'
        
        nreg1=cursor1.execute(sql)
        nreg1=int(nreg1)  # numero de registros actuales
        #print ('Nº registros en BD local = ', nreg1)
        
        ee = 'BD execute local'
        
        if nreg1 == 0:
            Hora_BD = '2005-01-01'
            print('Primer conjunto registros')
        else:
            var=cursor1.fetchone()
            #print(var)
            Id=int(var[0])
            Hora_BD=str(var[1])
        
        print (time.strftime("%Y-%m-%d %H:%M:%S"),'- Fecha_BD Datos_Local=',Hora_BD) #,end="")
        
        #DATOS en Remoto
        sql='SELECT * FROM datos WHERE Tiempo > "'+Hora_BD + '" ORDER BY id limit 1000' # maximo cada vez

        #print (sql)    
        db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave_remoto, db = basedatos)
        
        ee = 'BD conexion remota'
        cursor2 = db2.cursor()
        ee = 'BD cursor remota'
        nreg= cursor2.execute(sql)
        ee = 'BD execute remota'
        nreg=int(nreg)  # numero de registros a actualizar
        if nreg > 0: 
            bucle = True
        else:
            bucle = False
            
        print ('nreg=',nreg)
        TD=cursor2.fetchall()
        cursor2.close()
        db2.close()
                
        for I in range(nreg):
            Id=int(TD[I][0])
            Tiempo=str(TD[I][1])
            Ibat=float(TD[I][2])
            Vbat=float(TD[I][3])
            SOC=float(TD[I][4])
            DS=float(TD[I][5])
            Aux1=float(TD[I][6])
            Aux2=float(TD[I][7])
            Whp_bat=float(TD[I][8])
            Whn_bat=float(TD[I][9])
            Iplaca=float(TD[I][10])
            Vplaca=float(TD[I][11])
            Wplaca=float(TD[I][12])
            Wh_placa=float(TD[I][13])
            Temp=float(TD[I][14])
            PWM=int(TD[I][15])
            #print (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM)
            
            cursor1.execute("""INSERT INTO datos (id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM))
        db1.commit()
             
    except:
        print ("error copia tabla datos "+ ee)
        texto= texto+'/datos'
        time.sleep(5)
        #logBD("error copia tabla datos")
        
    finally:
        cursor1.close()
        db1.close()

		
 ########## TABLA DATOS_s ############################

    #print('Tabla Datos_s')

    try:
        ee = '0'
        # RECUPERAR ULTIMO REGISTRO DE LA BD LOCAL #

        sql='SELECT id,Tiempo FROM datos_s ORDER BY Tiempo DESC limit 1'
        ee = '1'
        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        ee = 'BD conexion local'
        cursor1 = db1.cursor()
        ee = 'BD cursor local'
        
        nreg1=cursor1.execute(sql)
        nreg1=int(nreg1)  # numero de registros actuales
        #print ('Num registros en BD local = ', nreg1)
        
        ee = 'BD execute local'
        
        if nreg1 == 0:
            Hora_BD = '2005-01-01'
            print('Primer conjunto registros')
        else:
            var=cursor1.fetchone()
            #print(var)
            Id=int(var[0])
            Hora_BD=str(var[1])
        
        print (time.strftime("%Y-%m-%d %H:%M:%S"),'- Fecha_BD Datos_Local=',Hora_BD) #,end="")
        
        #DATOS en Remoto
        sql='SELECT * FROM datos_s WHERE Tiempo > "'+Hora_BD + '" ORDER BY id limit 1000' # maximo cada vez

        #print (sql)    
        db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave_remoto, db = basedatos)
        
        ee = 'BD conexion remota'
        cursor2 = db2.cursor()
        ee = 'BD cursor remota'
        nreg= cursor2.execute(sql)
        ee = 'BD execute remota'
        nreg=int(nreg)  # numero de registros a actualizar
        if nreg > 60: 
            bucle = True
        else:
            bucle = False
            
        print ('nreg=',nreg)
        TD=cursor2.fetchall()
        cursor2.close()
        db2.close()
                
        for I in range(nreg):
            Id=int(TD[I][0])
            Tiempo=str(TD[I][1])
            Ibat=float(TD[I][2])
            Vbat=float(TD[I][3])
            SOC=float(TD[I][4])
            DS=float(TD[I][5])
            Aux1=float(TD[I][6])
            Aux2=float(TD[I][7])
            Whp_bat=float(TD[I][8])
            Whn_bat=float(TD[I][9])
            Iplaca=float(TD[I][10])
            Vplaca=float(TD[I][11])
            Wplaca=float(TD[I][12])
            Wh_placa=float(TD[I][13])
            Temp=float(TD[I][14])
            PWM=int(TD[I][15])
            #print (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM)
            
            cursor1.execute("""INSERT INTO datos_s (id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (Id,Tiempo,Ibat,Vbat,SOC,DS,Aux1,Aux2,Whp_bat,Whn_bat,Iplaca,Vplaca,Wplaca,Wh_placa,Temp,PWM))
        db1.commit()
             
    except:
        print ("error copia tabla datos_s "+ ee)
        texto= texto+'/datos'
        time.sleep(5)
        #logBD("error copia tabla datos")
        
    finally:
        cursor1.close()
        db1.close()
		
		
		
    ######### TABLA HIBRIDO ############################
    try:
        ## RECUPERAR ULTIMO REGISTRO DE LA BD LOCAL ##
        sql='SELECT id,Tiempo FROM hibrido ORDER BY Tiempo DESC limit 1'
        db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor1 = db1.cursor()
        
        #cursor1.execute(sql)
        #var=cursor1.fetchone()
        
        nreg1=cursor1.execute(sql)
        nreg1=int(nreg1)  # numero de registros actuales
        
        if nreg1 == 0:
            Hora_BD = '2005-01-01'
            print('Primer conjunto registros Hibridos')
        else:
            var=cursor1.fetchone()
            Id=int(var[0])
            Hora_BD=str(var[1])
        
        Id=int(var[0])
        Hora_BD=str(var[1])
        print (' / Fecha_BD_Hibrido=',Hora_BD)
       
       
        #Hibrido FV
        sql='SELECT * FROM hibrido WHERE Tiempo > "'+Hora_BD + '" ORDER BY id limit 1000' # maximo 1 hora cada vez'

        #print (sql)    
        db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave, db = basedatos)
        #print ("1")
        cursor2 = db2.cursor()
        #print ("2")
        nreg= cursor2.execute(sql)
        #print ("3")
        nreg=int(nreg)  # numero de registros a actualizar
        #print ('nreg=',nreg)
        
        if nreg > 0: 
            bucle1 = True
        else:
            bucle1 = False
        
        TD=cursor2.fetchall()
        cursor2.close()
        db2.close()
                
        for I in range(nreg):
            Id=int(TD[I][0])
            Tiempo=str(TD[I][1])
            Iplaca=int(TD[I][2])
            Vplaca=float(TD[I][3])
            Wplaca=int(TD[I][4])
            Vbat=float(TD[I][5])
            Vbus=int(TD[I][6])
            Ibatp=int(TD[I][7])
            Ibatn=int(TD[I][8])
            Temp=int(TD[I][9])
            PACW=int(TD[I][10])
            PACVA=int(TD[I][11])
            Flot=int(TD[I][12])
            OnOff=int(TD[I][13])
            
            cursor1.execute("""INSERT INTO hibrido (id,Tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,Temp,PACW,PACVA,Flot,OnOff) 
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (Id,Tiempo,Iplaca,Vplaca,Wplaca,Vbat,Vbus,Ibatp,Ibatn,Temp,PACW,PACVA,Flot,OnOff))
        db1.commit()
    except:
        print ("error copia tabla hibrido")
        texto= texto+'/hibrido'
        #logBD("error copia tabla hibrido")
    finally:
        cursor1.close()
        db1.close()
        
#sys.exit()



########## TABLA RELES ############################
try:
    #DATOS FV LOCAL ,,, BORRAR TABLA RELES
    ee='R1'
    sql='TRUNCATE reles'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    ee='R2'
    cursor1 = db1.cursor()
    ee='R3'
    cursor1.execute(sql)
    ee='R4'
    print ('Borrada tabla reles')

  
    #DATOS FV
    sql='SELECT * FROM reles ORDER BY id_rele'
    ee='R5'
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave_remoto, db = basedatos)
    ee='R6'
    cursor2 = db2.cursor()
    ee='R7'
    nreg = cursor2.execute(sql)
    ee='R8'
    nreg = int(nreg)  # numero de reles a actualizar
    TD = cursor2.fetchall()
    cursor2.close()
    db2.close()
       
    # Insertamos todas las filas de nuevo

    for I in range(nreg):
        id_rele = int(TD[I][0])
        nombre = str(TD[I][1])
        modo = str(TD[I][2])
        estado = int(TD[I][3])
        grabacion = str(TD[I][4])
        salto = int(TD[I][5])
        prioridad =int(TD[I][6])
                
        #print ('insert ', id_rele, nombre,modo,estado,grabacion,salto,prioridad)

        cursor1.execute("INSERT INTO reles (id_rele,nombre,modo,estado,grabacion,salto,prioridad) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (id_rele,nombre,modo,estado,grabacion,salto,prioridad))
        
    db1.commit()
    cursor1.close()
    db1.close()
    print ('Tabla Reles copiada')
except:
    print ("error tabla reles ",ee)
    texto= 'reles'
    #logBD("error copia tabla reles")
    sys.exit()


########## TABLA RELES_GRAB ############################
try:
    ## RECUPERAR ULTIMO REGISTRO DE LA BD LOCAL ##
    sql='SELECT id_reles_grab,Tiempo FROM reles_grab ORDER BY Tiempo DESC limit 1'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()
    
    nreg1=cursor1.execute(sql)
    nreg1=int(nreg1)  # numero de registros actuales
    if nreg1 == 0:
        Hora_BD = '2005-01-01'
        print('Primer conjunto registros Reles_grab')
    else:
        var=cursor1.fetchone()
        Id=int(var[0])
        Hora_BD=str(var[1])
    print ('Hora_BD Reles_Grab=',Hora_BD)

    #DATOS FV
    sql='SELECT * FROM reles_grab WHERE Tiempo > "'+Hora_BD + '" ORDER BY Tiempo'
    
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave_remoto, db = basedatos)
    cursor2 = db2.cursor()
    nreg= cursor2.execute(sql)
    nreg=int(nreg)  # numero de registros a actualizar
    print ('nreg reles_grab=',nreg)
    TD=cursor2.fetchall()
    cursor2.close()
    db2.close()
            
    for I in range(nreg):
        Tiempo=str(TD[I][0])
        id_rele=int(TD[I][1])
        valor_rele=int(TD[I][2])
               
        #print (Tiempo, id_rele, valor_rele)
        
        cursor1.execute("INSERT INTO reles_grab (Tiempo,id_rele,valor_rele) VALUES(%s,%s,%s)",(Tiempo,id_rele,valor_rele))
    db1.commit()
         
    cursor1.close()
    db1.close()
except:
    print ("error reles_grab")
    texto= texto+'/reles-grab'
    #logBD("error copia tabla reles_grab")


########## TABLA LOG ############################
try:    
    ## RECUPERAR ULTIMO REGISTRO DE LA BD LOCAL ###
    sql='SELECT id_log,Tiempo FROM log ORDER BY Tiempo DESC limit 1'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()
    cursor1.execute(sql)
    var=cursor1.fetchone()
    Id=int(var[0])
    Hora_BD=str(var[1])
    print ('Hora_BD Log=',Hora_BD)

    #DATOS FV
    sql='SELECT * FROM log WHERE Tiempo > "'+Hora_BD + '" ORDER BY Tiempo'
        
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave, db = basedatos)
    cursor2 = db2.cursor()
    nreg= cursor2.execute(sql)
    nreg=int(nreg)  # numero de registros a actualizar
    print ('nreg log=',nreg)
    TD=cursor2.fetchall()
    cursor2.close()
    db2.close()
            
    for I in range(nreg):
        Tiempo=str(TD[I][1])
        log=str(TD[I][2])
               
        #print Tiempo, log
        
        cursor1.execute("INSERT INTO log (Tiempo,log) VALUES(%s,%s)",(Tiempo,log))
    db1.commit()
    cursor1.close()
    db1.close()
except:
    #print ("error log")
    texto= texto+'/log'
    #logBD("error copia tabla log")


########## TABLA RELES_SEGUNDOS_ON ############################
try:
    #DATOS FV LOCAL ,,, ULTIMO REGISTRO DE LA BD
    sql='SELECT id_reles_segundos_on,fecha FROM reles_segundos_on ORDER BY id_reles_segundos_on DESC limit 1'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()
    cursor1.execute(sql)
    var=cursor1.fetchone()
    try:
        Id_max = int(var[0])
    except:
        Id_max = 0
    print ('id_reles_segundos_on maximo en local=',Id_max)
   
    #DATOS FV para actualizar
    sql='SELECT * FROM reles_segundos_on WHERE fecha >= SUBDATE(NOW(), INTERVAL 10 DAY) ORDER BY id_reles_segundos_on'
    
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave, db = basedatos)
    cursor2 = db2.cursor()
    nreg = cursor2.execute(sql)
    
    nreg = int(nreg)  # numero de registros a actualizar
    print ('nreg actu....reles_segundos_on=',nreg)
    TD = cursor2.fetchall()
    cursor2.close()
    db2.close()

    for I in range(nreg):
        id_rele = int(TD[I][0])
        fecha = str(TD[I][1])
        segundos_on = float(TD[I][2])
        nconmutaciones = float(TD[I][3])
        id_reles_segundos_on = int(TD[I][4])
                       
        #print (id_reles_segundos_on, '/ ',id_rele,fecha,segundos_on,nconmutaciones)

        if id_reles_segundos_on > Id_max: 
            #print ('insert ', id_rele, fecha, segundos_on, nconmutaciones)
            cursor1.execute("INSERT INTO reles_segundos_on (id_rele,fecha,segundos_on,nconmutaciones) VALUES(%s,%s,%s,%s)",
                        (id_rele,fecha,segundos_on,nconmutaciones))
        else:
            #print ('update ', id_rele, fecha, segundos_on, nconmutaciones)
            sql = 'UPDATE reles_segundos_on SET segundos_on =' + str(segundos_on) + ', nconmutaciones = ' + str(nconmutaciones)
            sql = sql + ' WHERE id_reles_segundos_on = ' + str(id_reles_segundos_on)
            cursor1.execute(sql)

    db1.commit()
    cursor1.close()
    db1.close()        
except:
    print ("error reles_segundos_on")
    texto= texto+'/reles_segundos_on'
    #logBD("error copia tabla reles_segundos_on")


########## TABLA RELES_C ############################
try:

    #DATOS FV LOCAL ,,, BORRAR TABLA RELES_C
    sql='TRUNCATE reles_c'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()
    cursor1.execute(sql)
    #print ('Borrada tabla reles_c')

   
    #DATOS FV
    sql='SELECT * FROM reles_c ORDER BY id_reles_c'
    
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave, db = basedatos)
    cursor2 = db2.cursor()
    nreg = cursor2.execute(sql)
    
    nreg = int(nreg)  # numero de reles_c a actualizar
    TD = cursor2.fetchall()
    cursor2.close()
    db2.close()
            
    # Insertamos todas las filas de nuevo

    for I in range(nreg):
        id_rele = int(TD[I][0])
        operacion = str(TD[I][1])
        parametro = str(TD[I][2])
        condicion = str(TD[I][3])
        valor = float(TD[I][4])
        id_reles_c = int(TD[I][5])
        
                
        #print ('insert ', id_rele,operacion,parametro,condicion, valor,id_reles_c)

        cursor1.execute("""INSERT INTO reles_c (id_rele,operacion,parametro,condicion, valor,id_reles_c) VALUES(%s,%s,%s,%s,%s,%s)""",
                        (id_rele,operacion,parametro,condicion, valor,id_reles_c))
        

    db1.commit()
         
    cursor1.close()
    db1.close()
except:
    print ("error tabla reles_c")
    texto= texto+'/reles_c'
    #logBD("error copia tabla reles_c")


########## TABLA RELES_H ############################
try:
    #DATOS FV LOCAL ,,, BORRAR TABLA RELES_H
    sql='TRUNCATE reles_h'
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()
    cursor1.execute(sql)
    #print ('Borrada tabla reles_h')
    
    #DATOS FV
    sql='SELECT * FROM reles_h ORDER BY id_reles_h'
    db2 = MySQLdb.connect(host = servidor_remoto, user = usuario_remoto, passwd = clave, db = basedatos)
    cursor2 = db2.cursor()
    nreg = cursor2.execute(sql)
    nreg = int(nreg)  # numero de reles_h a actualizar
    TD = cursor2.fetchall()
    cursor2.close()
    db2.close()
            
    # Insertamos todas las filas de nuevo

    for I in range(nreg):
        id_rele = int(TD[I][0])
        parametro_h = str(TD[I][1])
        valor_h_ON = str(TD[I][2])
        valor_h_OFF = str(TD[I][3])
        id_reles_h = int(TD[I][4])
        
        #print ('insert ', id_rele,parametro_h,valor_h_ON,valor_h_OFF,id_reles_h)

        cursor1.execute("INSERT INTO reles_h (id_rele,parametro_h,valor_h_ON,valor_h_OFF,id_reles_h) VALUES(%s,%s,%s,%s,%s)",
                        (id_rele,parametro_h,valor_h_ON,valor_h_OFF,id_reles_h))
    db1.commit()
    cursor1.close()
    db1.close()
except:
    print ("error tabla reles_h")
    texto= texto+'/reles_h'
    #logBD("error copia tabla reles_h")




try:
    db1 = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor1 = db1.cursor()

    print ("Actualizacion BD hecha")
    #logBD("Copia seguridad BD hecha")

    cursor1.close()
    db1.close()
  
except:
    print ("Error Copia seguridad BD")
    texto= texto+'/BD'
    #logBD("Error Copia seguridad BD")


if texto != '':
    #logBD(texto)
    pass
