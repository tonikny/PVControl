#!/usr/bin/python

#import sys
import glob

sensores = glob.glob("/sys/bus/w1/devices/28*/w1_slave")

while True:
    for sensor in sensores:
      tfile = open(sensor)
      texto = tfile.read()
      tfile.close()
      segundalinea = texto.split("\n")[1]
      temp_datos = segundalinea.split(" ")[9]
      temp = float(temp_datos[2:])/1000
      print ("sensor", sensor, "=", temp, " grados.")
    print
    
