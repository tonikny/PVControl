
import MySQLdb
import logging
import traceback


#from Bd_Params import *

## Bd_Params.py
# Configuracion de la base de datos (se configura en Parametros_FV.py)
#  servidor =
#  usuario =
#  clave =
#  basedatos =

SERVIDOR = 'localhost'
USUARIO = 'rpi'
CLAVE = 'fv'
BASEDATOS = 'control_solar'

##
# Bd: Acceso a la base de datos
#
# uso:  from Bd import *
#       bd = Bd(servidor,usuario,clave,basedatos)
#       bd.insert("tabla", dict_datos)
#       bd.desconecta()

##
# Clase para manejar la base de datos
#
class Bd:

    ##
    # conectar con la BD
    def __init__(self, host=SERVIDOR, user=USUARIO,
                 passwd=CLAVE, db=BASEDATOS):
        self.servidor = host
        self.usuario = user
        self.clave = passwd
        self.basedatos = db

        logging.info(__class__.__name__ + ":Objeto creado")
        try:
            self.bd = MySQLdb.connect(self.servidor, self.usuario,
                                      self.clave, self.basedatos)
            self.cursor = self.bd.cursor()
            logging.info(__class__.__name__ + ":BD conectada")
        except MySQLdb._exceptions.Error as err:
            logging.error(__class__.__name__ + ":Error de conexión a la BD"+format(err))
            traceback.print_exc()

    ##
    # insertar datos en la tablasrne
    # @param tabla Tabla de la base de datos
    # @params datos Diccionario {columna:valor,...}
    def insert(self, tabla, datos):
        try:
            campos = ",".join(datos.keys())
            valores = "','".join(str(v) for v in datos.values())
            insertQuery = "INSERT INTO "+tabla+" ("+campos+") VALUES ('"+valores+"')"
            logging.info(__class__.__name__ + ":"+insertQuery)
            self.cursor.execute(insertQuery)
            self.bd.commit()
        except MySQLdb._exceptions.Error as err:
            logging.error(__class__.__name__ + ":Error insertando en la BD"+format(err))
            traceback.print_exc()

    ##
    # desconectar la BD
    def desconecta(self):
        self.cursor.close()
        self.bd.close()
