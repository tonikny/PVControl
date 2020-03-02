#!/usr/bin/python
# -*- coding: utf-8 -*-

# @programa: test_sbfreq.py
# @descripción: Control Triacs por frecuencia con Sunny Boy modelos 2.5 y superiores
# @autores: Gabriel Mayoral, Mleon, fran_pascualin, JanusHL para Control FV
# @creado: 28/09/2019
# @licencia: de un solo uso y después tirar...

# 

"""

30803  Grid frequency  Hz

"""
########### PARAMETROS ########################
simulacion = 1  # poner 0 o 1

PWMAMAX = 100  #Introducir porcentaje de carga máxima para Triac1
PWMBMAX = 100  #Introducir porcentaje de carga máxima para Triac2
PWMCMAX = 100    #Introducir porcentaje de carga máxima para Triac3
#PWMDMAX = 80   Introducir porcentaje de carga máxima para Triac4

# Direccion IP para los equipos a testear
IP_SMA = '192.168.0.253' # aquí pones la IP del SMA
IP_SB = '192.168.0.252' # aquí pones la IP del SB.... poner IP_SB = '' si no existe SB
  
UNIT_ID = 3 # unidad modbus del equipo SMA (suele ser 3)
PORT = 502

GRABAR_BD = 0
server = "http://data.cspin.es/fran.php"

#################################################
import datetime, time, sys
#import os
import time
#import msvcrt
import requests
import json
if simulacion == 0:
    import sma
    from sma import convert2 as c2
else:
    import random # para simulacion usando random.choice

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(31, GPIO.OUT)    #configuración de pines GPIO de Rpi
GPIO.setup(33, GPIO.OUT)    #configuración para tres salidas
GPIO.setup(35, GPIO.OUT)
#GPIO.setup(37, GPIO.OUT)

TRIAC1 = GPIO.PWM(31, 1000)     #frecuencia de PWM
TRIAC2 = GPIO.PWM(33, 1000)
TRIAC3 = GPIO.PWM(35, 1000)
#TRIAC4 = GPIO.PWM(37, 1000)

TRIAC1.start(0)                 #inicio pines para Triac
TRIAC2.start(0)
TRIAC3.start(0)
#TRIAC4.start(0)


SALTO1 = PWMAMAX                        #Saltos PWM Para 4 Triacs: SALTO3 = SALTO2 + PWMCMAX 
SALTO2 = SALTO1 + PWMBMAX               #PWMMAX = SALTO3 + PWMDMAX
PWMMAX = SALTO2 + PWMCMAX       

PWM = 0
Tp = 0.70                   #Término proporcional PID
Ti = 0.20                   #Término integral PID
Td = 0.10                   #Término derivativo PID
#K = 15.00                  #Constante de amplificación PID
frobj = 50.80           #Frecuencia objetivo
Kpos =  1.00
Kneg =  (52.00-frobj)/(frobj-50.00)         #modificación de 28/10/2019. Según parece la frecuencia a la que los SB comienzan a reducir potencia es 50.18 Hz.
cont = 0                                          #se aplica un factor multiplicativo para tener en cuenta la diferencia de márgenes de la frecuencia objetivo
                                            #al no estar centrada en 51 Hz
freq = [50.0,50.0,50.0,50.0,50.0,50.0]


if simulacion == 0:
    try:
        sma1 = sma.mbusTCP(3, IP_SMA, 502)
        sma1.openTCP()
    except:
        print('Error conexion SMA')
    try:
        sb1 = sma.mbusTCP(3, IP_SB, 502)
        sb1.openTCP()
    except:
        print('Error conexion SB')
    

####### BUCLE PRINCIPAL
try:
    while True:
        try:
        #leemos frecuencia
            if simulacion == 0:
                #### Lectura SMA
                data = sma1.read_data(30803, 2)
                Translate=c2()
                Translate.u16.h = data[1]
                Translate.u16.l = data[0]
                valor = Translate.uint32
                valor = valor*0.01
                if valor > 52.5:
                    valor = 50
                
                data = sma1.read_data(30775, 2)
                Translate=c2()
                Translate.u16.h = data[1]
                Translate.u16.l = data[0]
                pot1 = Translate.uint32
                pot1 = pot1*0.001
                print('Potencia Grupo1: ',pot1)

                #### Lectura SB
                data = sb1.read_data(30775, 2)
                Translate=c2()
                Translate.u16.h = data[1]
                Translate.u16.l = data[0]
                pot2 = Translate.uint32
                pot2 = pot2*0.001
                print('Potencia Grupo2: ',pot2)

                print('Potencia total: ',pot1+pot2)
                
                
            else:
                valor = freq[0]+random.randrange(-5, 5, 1)/100 #random.randrange(-5, 0, 1)/100
                print('valor=',valor)
                if valor <50:
                    valor=50
                if valor >=52:
                    valor=52
                
                pot1=pot2=1 # simulo potencia fija de 1Kw
                                      
        
            # desplazamos la lista hacia la derecha        
            freq = freq[-1:] + freq[:-1]                        
            freq[0] = valor
            potT=pot1+pot2
            frec=freq[0]
            
        except TypeError:
            #raise  # provisional para saber el error
            print ("error leyendo datos...")
            freq = freq[-1:] + freq[:-1]  # se desplaza la lista incluso con error... JHL
            freq[0] = 50

            # control del error modbus en pruebas JHL
            cont +=1
            if cont>5:
                cont=0
                time.sleep(3)
                try:
                    sma1.openTCP(IP_SMA)  # Mleon :esta parte no la tengo clara 
                    sb1.openTCP(IP_SB)
                except:
                    raise

            
        ###### GRABAR EN BD
        
        if GRABAR_BD == 1:
            try:
                data = {'frec':frec,'pot1':pot1,'pot2':pot2,'potT':potT,'PWM':PWM}   
                data1=json.dumps(data)
                r = requests.post(url = server, data = data1)
                # Texto de respuesta  
                respuesta = r.text
                print("Respuesta server: %s"%respuesta)
                print (r.status_code)
                print (r.headers['content-type'])
            except:
                pass
                
                
        ###### CALCULO PID        
        for i in range(6):
            print (round(freq[i],3)) # aqui tenemos la lista con las 5 últimas frecuencias

        EINT = 0 
        for i in range(5):
            EINT = EINT + (freq[i] + freq[i + 1]) / 2
        print ('MEDIA=',EINT)
        
        EP =   freq[0] - frobj
        EINT = (EINT - frobj*5)/5
        ED =   freq[0] - freq[1]
        
        if (abs(freq[0]-frobj)<0.1):
            K = 1.5*potT
        else:
            K= 3.5 * potT
            
        INCPWM = K * (Tp * EP + Ti * EINT + Td * ED)
        if(INCPWM<0):
            INCPWM=INCPWM*Kneg
        PWM = PWM + INCPWM
        

        
        if PWM >= PWMMAX:  #Límite superior PWM
            PWM = PWMMAX

        if PWM <= 0:     #Límite inferior PWM
            PWM = 0
        if INCPWM >= 0:
            print ('Termino P:', round(K*Tp*EP,2),'Termino I:', round(K*Ti*EINT,2),'Termino D:', round(K*Td*ED,2),'INCPWM:', round(INCPWM,2),'PWM:', round(PWM,2))
        if INCPWM < 0:
            print ('Termino P:', round(K*Kneg*Tp*EP,2),'Termino I:', round(K*Kneg*Ti*EINT,2),'Termino D:', round(K*Kneg*Td*ED,2),'INCPWM:', round(INCPWM,2),'PWM:', round(PWM,2))
        PWMA = min(SALTO1,PWM)
        PWMB = max(0,min(PWM-SALTO1,PWMBMAX))
        PWMC = max(0,min(PWM-SALTO2,PWMCMAX))
        #PWMD = max(0,min(PWM-SALTO3,PWMDMAX))

        TRIAC1.ChangeDutyCycle(PWMA)
        TRIAC2.ChangeDutyCycle(PWMB)
        TRIAC3.ChangeDutyCycle(PWMC)
        #TRIAC4.ChangeDutyCycle(PWMD)
        
        time.sleep(1) # esperamos 1 segundo
        
except KeyboardInterrupt:
    pass

# paramos el programa pulsando ESC solo en windows
#    if msvcrt.kbhit():
#        if ord(msvcrt.getch()) == 27:
#            break
# ponemos a 0 los Gpios para apagar los triacs JHL - 29/09/2019

TRIAC1.ChangeDutyCycle(0)
TRIAC2.ChangeDutyCycle(0)
TRIAC3.ChangeDutyCycle(0)
#TRIAC4.ChangeDutyCycle(0)
time.sleep(1) # por si acaso - JanusHL

# desconectamos los sockets
if simulacion == 0:
    print('\nCERRANDO SOCKETS ')
    sb1.closeTCP()
    sma1.closeTCP()
