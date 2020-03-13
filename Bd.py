
import MySQLdb 
import logging
import traceback
from Parametros_FV import *

#from Bd_Params import *

## Bd_Params.py 
# Configuracion de la base de datos (se configura en Parametros_FV.py)
#  servidor =
#  usuario =
#  clave =
#  basedatos =

##
# Bd: Acceso a la base de datos
#
# uso:  from Bd import *
#       bd = Bd()
#       bd.insert("tabla", dict_datos)
#       bd.desconecta()

##
# Clase para manejar la base de datos
#
class Bd:
    
#    bd = None
#    cursor = None
        
    ##
    # conectar con la BD
    def __init__(self, host = servidor, user = usuario, passwd = clave, db = basedatos):
        logging.info(__class__.__name__ + ":Objeto creado")
        try:
            self.bd = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            self.cursor = self.bd.cursor()
            logging.info(__class__.__name__ + ":BD conectada")
        except:
            logging.error(__class__.__name__ + ":Error de conexión a la BD")
            traceback.print_exc()
            
    ##
    # insertar datos en la tablasrne
    # @param tabla Tabla de la base de datos
    # @params datos Diccionario {columna:valor,...}    
    def insert (self, tabla, datos):
        try:
            campos = ",".join(datos.keys())
            valores = "','".join(str(v) for v in datos.values())
            insertQuery = "INSERT INTO "+tabla+" ("+campos+") VALUES ('"+valores+"')"
            logging.info(__class__.__name__ + ":"+insertQuery)
            self.cursor.execute(insertQuery)
            self.bd.commit()
        except:
            logging.error(__class__.__name__ + ":Error insertando en la BD")
            traceback.print_exc()


    ##
    # desconectar la BD
    def desconecta():
        self.cursor.close()
        self.bd.close()

