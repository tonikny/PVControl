#!/usr/bin/python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------

# #################### Control Ejecucion Servicio ########################################
servicio = 'sma'
control = 'usar_sma'
exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


from pyModbusTCP.client import ModbusClient
import os
import time
import commands
import pickle #,csv
import MySQLdb 
DEBUG = False

SOC_si = 0
t_to_abs = 0
VP11 = 0
VP12 = 0
VP21 = 0
VP22 = 0
IP11 = 0
IP12 = 0
IP21 = 0
IP22 = 0
Vbat=48.0
Ibat=0
Vplaca=0
Iplaca=0
Aux1=0
cont = 0
cont2 = 0
tant=time.time()
Vobj = 65
Consumo = 0
Temp = 0
SOC_si = 0
                
si = ModbusClient()
si.host(IP_SI)
si.port(502)
si.unit_id(3)

sb1 = ModbusClient()
sb1.host(IP_SB1)
sb1.port(502)
sb1.unit_id(3)

sb2 = ModbusClient()
sb2.host(IP_SB2)
sb2.port(502)
sb2.unit_id(3)
time_ini=time.time()

if usar_si == 1:     
    si.open()
if usar_sb1 == 1:   
    sb1.open()
if usar_sb2 == 1:   
    sb2.open()

def logBD(texto) : # Incluir en tabla de Log
    try: 
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        if DEBUG: print (tiempo,' ', texto)
        db.commit()
        db.close()
        
    except:
        pass

    
    
while True:
    t1 = time.time()
    if cont ==1 and usar_si == 1:                            #Lectura SMA SI: Parametros cada 2s
        try:
            cont2 = cont2 + 1
            Vbat = si.read_holding_registers(30851, 2)
            Vbat = Vbat[1]*0.01       
            Ibat = si.read_holding_registers(30843, 2)
            p_desc = si.read_holding_registers(31395, 2)
            p_carg = si.read_holding_registers(31393, 2)
            Aux1=   si.read_holding_registers(30803, 2)
            Aux1 = Aux1[1]*0.01
            
            if Ibat[0]<=32768:
                Ibat = -(Ibat[1]+Ibat[0]*65535)*0.001

            else:
                Ibat =  (65535-Ibat[1]+(65535-Ibat[0])*65536)*0.001
                    
            if DEBUG: print ('Vbat', Vbat,'Ibat',Ibat, 'Frec', Aux1)
        except:
            if DEBUG: print ('error de lectura SI')
            logBD('Error de Lectura SI Vbat,Ibat...')
            si.close()
            time.sleep(3)
            si.open()
            pass
                
        if cont2 == 10 and usar_si == 1:                     #Lectura SMA SI: Parametros cada 20s
            cont2 = 0
            try:
                t_to_abs = si.read_holding_registers(31007, 2)
                t_to_abs = t_to_abs[1]
                Temp = si.read_holding_registers(30849, 2)
                Temp = Temp[1]*0.1                
                v_abs = si.read_holding_registers(40085, 2)
                v_abs = v_abs[1]*0.01 * 24 
                v_flot = si.read_holding_registers(40091, 2)
                v_flot = v_flot[1]*0.01 * 24
                SOC_si = si.read_holding_registers(30845, 2)
                SOC_si = SOC_si[1]
            except:
                print ('Error lectura V Objetivo')
                logBD('Error de Lectura SI Temp,SOC...')
                Vobj = Vobj + 0.5
                si.close()
                time.sleep(3)
                si.open()
                pass
                
            if t_to_abs == 0:
                Vobj = v_flot - (Temp-20) * 24 * 0.004 - 0.8
            if t_to_abs != 0:
                Vobj = v_abs - (Temp-20) * 24 * 0.004 - 0.8
                    
            if Vobj < 53:
                Vobj = 65.00
                    
            if DEBUG: 
                print ('   Vabs', v_abs,'V_flot',v_flot, 't_to_abs', t_to_abs,'Vobj',Vobj,'SOC',SOC_si)
                logBD('Prueba log')
            try:
                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                cursor = db.cursor()
                query = """ UPDATE parametros SET objetivo_diver = %s WHERE id_parametros =%s """
                data = (Vobj,1)
                cursor.execute(query,data)
                db.commit()
            except:
                db.rollback()
                logBD('Error envio Vobj a BBDD-Parametros')
                pass
            try:
                cursor.close()
                db.close()
            except:
                pass            
          
    try:

        if cont ==10 and usar_sb1 == 1:                  #Lectura SB1 cada 2s
            t4=time.time()
            
            pot1 = sb1.read_holding_registers(30775, 2)
            pot1 = pot1[1]
            VP11 = sb1.read_holding_registers(30771, 2)
            VP11 = VP11[1] * 0.01
            IP11 = sb1.read_holding_registers(30769, 2)
            IP11 = IP11[1] * 0.001
            VP12 = sb1.read_holding_registers(30959, 2)
            VP12 = VP12[1] * 0.01
            IP12 = sb1.read_holding_registers(30957, 2)
            IP12 = IP12[1] * 0.001
            
            t5=time.time()
            
            t = t5-t4
            Vplaca = VP11
            if DEBUG: print ('   VP11',VP11,'VP12',VP12,'IP11',IP11,'IP12',IP12)
            
    except:
            
        print ('error lectura SB1')
        logBD('Error lectura SB1')
        sb1.close()
        time.sleep(3)
        sb1.open()
        pass
            
    try:
        if cont ==15 and usar_sb2 == 1:                  #Lectura SB2 cada 2s
            t6=time.time()
                                                                                                                                                                 
            pot2 = sb2.read_holding_registers(30775, 2)
            pot2 = pot2[1]
            IP21 = sb2.read_holding_registers(30769, 2)
            IP21 = IP21[1] * 0.001
            VP21 = sb2.read_holding_registers(30771, 2)
            VP21 = VP21[1] * 0.01
            IP22 = sb2.read_holding_registers(30957, 2)
            IP22 = IP22[1] * 0.001
            VP22 = sb2.read_holding_registers(30959, 2)
            VP22 = VP22[1] * 0.01
            
            
            t7=time.time()
            Consumo = (pot1+pot2+p_desc[1]-p_carg[1])
            Iplaca = (pot1+pot2)*1.0001
            Iplaca= Iplaca/Vbat
            if DEBUG: print ('       VP21',VP21,'VP22',VP22,'IP21',IP21,'IP22',IP22)
            
            
    except:
        print ('error lectura SB2')
        logBD('Error lectura SB2')
        sb2.close()
        time.sleep(3)
        sb2.open()
        pass      
    
    cont = cont + 1
    
    if cont == 20:
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        tiempo_sg = time.time()
        
        datos = {'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Ibat':Ibat,'Vbat':Vbat,'Iplaca': Iplaca,
                 'Vplaca':Vplaca,'Aux1':Aux1,'Consumo':Consumo,'Temp':Temp,'Vobj':Vobj,'SOC_si':SOC_si}
        
        with open('/run/shm/datos_sma.pkl', mode='wb') as f:
            pickle.dump(datos, f)
            
        """
        with open('/run/shm/datos_sma.csv', mode='w') as f:
            nombres = ['Tiempo_sg','Tiempo','Ibat','Vbat','Iplaca','Vplaca','Aux1','Consumo','Temp','Vobj','SOC_si']
            datos = csv.DictWriter(f, fieldnames=nombres)
            datos.writeheader()
            datos.writerow({'Tiempo_sg': tiempo_sg,'Tiempo': tiempo,'Ibat':Ibat,'Vbat':Vbat,'Iplaca': Iplaca,'Vplaca':Vplaca,'Aux1':Aux1,'Consumo':Consumo,'Temp':Temp,'Vobj':Vobj,'SOC_si':SOC_si})
            #print datos
        """
        
        try:
            
            if DEBUG: print (tiempo,Vbat,Ibat,SOC_si,t_to_abs,VP11,VP12,VP21,VP22,IP11,IP12,IP21,IP22)
            
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            cursor.execute("""INSERT INTO sma (Tiempo,Vbat,Ibat,SOC_si,t_to_abs,VP11,VP12,VP21,VP22,IP11,IP12,IP21,IP22) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(tiempo,Vbat,Ibat,SOC_si,t_to_abs,VP11,VP12,VP21,VP22,IP11,IP12,IP21,IP22))
            db.commit()
        except:
            #db.rollback()
            logBD('Error envio a tabla SMA')
            pass
        try:
            cursor.close()
            db.close()
        except:
            pass
   
    t = time.time()-t1
    if t<0.100:
        time.sleep(0.100-t)
    if cont >= 20:
        cont=0
        tant=time.time()
        if ((time.time()-tant) >6):
            print ('Vbat',Vbat,'Ibat',round(Ibat,2),'Pplaca',round(Iplaca*Vbat,2),'tlecturas',round(time.time()-tant,3))
        
    

