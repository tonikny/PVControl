#!/usr/bin/python
# -*- coding: utf-8 -*-

# Test modbus multiples registros para SB modelos 2.5 y superiores
# JanusHL para Control FV - 20/05/2019

"""

30803  Grid frequency  Hz

"""

simulacion = 1  # poner 0 o 1

#import os
import time
#import msvcrt
if simulacion == 0:
    import sma
    from sma import convert2 as c2
else:
    import random # para simulacion usando random.choice

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

TRIAC1 = GPIO.PWM(24, 1000)
TRIAC2 = GPIO.PWM(25, 1000)
TRIAC3 = GPIO.PWM(26, 1000)
TRIAC4 = GPIO.PWM(27, 1000)

TRIAC1.start(0)
TRIAC2.start(0)
TRIAC3.start(0)
TRIAC4.start(0)
 
# Direccion TCP/IP para el equipo a testear
TCP_IP = '192.168.0.253' # aquí pones la IP del SMA
UNIT_ID = 3 # unidad modbus del equipo SMA (suele ser 3)
PORT = 502

PWM = 0
Tp = 0.50                   #Término proporcional PID
Ti = 0.40                   #Término integral PID
Td = 0.10                   #Término derivativo PID
K = 20.00                   #Constante de amplificación PID
frobj = 51.05               #Frecuencia objetivo
freq = [51.5,50.0,50.0,50.0,50.0,50.0]

if simulacion == 0:
    try:
        mbus = sma.mbusTCP(UNIT_ID, TCP_IP, PORT)
        mbus.openTCP()
    except:
        #raise
        print ("error Iniciando proceso...")

reg_ini = 30803
num_regs = 2

try:
    while True:
        try:
        #leemos frecuencia
            if simulacion == 0:
                data = mbus.read_data(reg_ini, num_regs)
                Translate=c2()
                Translate.u16.h = data[1]
                Translate.u16.l = data[0]
                valor = Translate.uint32
                valor = valor*0.01
            else:
                valor = freq[0]+random.randrange(-20, 20, 1)/100
                if valor <50:
                    valor=50
                if valor >=52:
                    valor=52;
                                      
        
            # desplazamos la lista hacia la derecha        
            freq = freq[-1:] + freq[:-1]                        
            freq[0] = valor

        except:
            raise
            print ("error leyendo datos...")
            freq[0] = 50
            
# --------------------
        #for i in range(0,6):
        #    print (round(freq[i],3))# aqui tenemos la lista con las 5 últimas frecuencias
        
        print(freq)
        
        
        EINT = 0 
        for i in range(5):
            EINT = EINT + (freq[i] + freq[i + 1]) / 2
        
        EP =   freq[0] - frobj
        EINT = (EINT - frobj*5)/5
        ED =   freq[0] - freq[1]
        
        INCPWM = K * (Tp * EP + Ti * EINT + Td * ED)
        PWM = PWM + INCPWM
        
        
        
        if PWM >= 400:  #Límite superior PWM
            PWM = 400

        if PWM <= 0:     #Límite inferior PWM
            PWM = 0
            
        print ('Termino P:', round(K*Tp*EP,2),'Termino I:', round(K*Ti*EINT,2),'Termino D:', round(K*Td*ED,2),'INCPWM:', round(INCPWM,2),'PWM:', round(PWM,2))
        PWMA = min(100,PWM)
        PWMB = max(0,min(PWM-100,100))
        PWMC = max(0,min(PWM-200,100))
        PWMD = max(0,min(PWM-300,100))

        TRIAC1.ChangeDutyCycle(PWMA)
        TRIAC2.ChangeDutyCycle(PWMB)
        TRIAC3.ChangeDutyCycle(PWMC)
        TRIAC4.ChangeDutyCycle(PWMD)
        
        time.sleep(5) # esperamos 1 segundo
        
except KeyboardInterrupt:
    pass

# paramos el programa pulsando ESC solo en windows
#    if msvcrt.kbhit():
#        if ord(msvcrt.getch()) == 27:
#            break

# desconectamos los sockets
if simulacion == 0:
    print('\nCLOSING '+ TCP_IP)
    mbus.closeTCP()
