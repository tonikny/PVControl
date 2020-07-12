
import time,sys
import datetime
import MySQLdb 

#Parametros Instalacion FV
from Parametros_FV import *


db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
cursor = db.cursor()


sql = 'SELECT * FROM reles'
nreles = cursor.execute(sql)
nreles = int(nreles)  # = numero de reles

columns = [column[0] for column in cursor.description]
reles = []
for row in cursor.fetchall():
    reles.append(dict(zip(columns, row)))
print('Diccionario completo')
print(reles)

print('Rele 0')
print(reles[0])

print('Modo del Rele 0')
print(reles[0]['modo'])


print('Listado Id_rele, Modo')
for r in reles:
    print (r['id_rele'],r['modo'])
    

cursor.close()
db.close()
