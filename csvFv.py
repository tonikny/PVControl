#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging

##


class CsvFv:
    """
    CsvFv: Acceso a archivos Ram (acepta dict y list)

    uso:    from csvFv import CsvFv
            c = CsvFv(archivo)
            c.escribir_csv(datos)
            datos = c.leer_csv(["list"])  # por defecto "dict"
    """
    def __init__(self, archivo):
        self.archivo = archivo

    def escribirCsvfloat(self, datos):
        self.escribir(datos)

    def escribirCsv(self, datos):
        """
        Escribe datos al archivo csv
        :param datos (dict|list)
        """
        try:
            with open(self.archivo, mode='w') as f:
                if isinstance(datos, dict):
                    nombres = datos.keys()
                    dat = csv.DictWriter(f, fieldnames=nombres,
                                         quoting=csv.QUOTE_NONNUMERIC)
                    dat.writeheader()
                    dat.writerow(datos)
                elif isinstance(datos, list):
                    dat = csv.writer(f, delimiter=',',
                                     quoting=csv.QUOTE_NONNUMERIC)
                    dat.writerow(datos)
        except (IOError, csv.Error):
            logging.warning("CsvFv: No se pudo escribir "+self.archivo)

    def leerCsvfloat(self, formato="dict"):
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
            logging.warning("CsvFv: No se pudo leer "+self.archivo)


    def leerCsv(self, formato="dict"):
        """
        Lee datos del archivo csv
        :param formato ["dict" | "list"]
        :returns: (Dict) datos
        """
        datos = None
        try:
            with open(self.archivo, mode='r') as f:
                if formato == "list":
                    csv_reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                else:
                    csv_reader = csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC)
                datos = next(csv_reader, None)
                if not datos:
                    raise ValueError('CsvFv: No hay datos')
                return datos
        except (IOError, csv.Error):
            logging.warning("CsvFv: No se pudo leer "+self.archivo)
