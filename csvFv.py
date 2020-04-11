#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging

##
# CsvFv: Acceso a archivos Ram
#
# uso:  from csvFv import CsvFv
#       c = CsvFv(archivo)
#       c.escribirCsv(datos)
#       datos = c.leerCsv()

class CsvFv:

    def __init__(self, archivo):
        self.archivo = archivo

    ##
    # Escribe datos al archivo
    # @param datos (Dict)
    def escribirCsv(self, datos):
        try:
            with open(self.archivo, mode='w') as f:
                nombres = datos.keys()
                dat = csv.DictWriter(f, fieldnames=nombres)
                dat.writeheader()
                dat.writerow(datos)
        except (IOError, csv.Error):
            logging.warning("CsvFv: No se pudo escribir CSV ")

    ##
    # Lee datos del archivocsv
    # @return datos (Dict)
    def leerCsv(self):
        datos = None
        try:
            with open(self.archivo, mode='r') as f:
                csv_reader = csv.DictReader(f) 
                datos = next(csv_reader, None)
                if not datos:
                    raise ValueError('CsvFv: No hay datos')
                return datos
        except (IOError, csv.Error):
            logging.warning("CsvFv: No se pudo leer CSV")
    
    def leerCsvfloat(self):
        datos = None
        try:
            with open(self.archivo, mode='r') as f:
                csv_reader = csv.DictReader(f) 
                datos = next(csv_reader, None)
                for k, v in datos.items():
                    try:
                        datos[k] = float(v)
                    except:
                        pass
                if not datos:
                    raise ValueError('CsvFv: No hay datos')
                return datos
        except (IOError, csv.Error):
            logging.warning("CsvFv: No se pudo leer CSV")
