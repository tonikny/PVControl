import MySQLdb

db = MySQLdb.connect(host = "localhost", user = 'rpi', passwd = 'fv', db = 'control_solar')
cursor = db.cursor()

for tabla in ["datos", "datos_c"]:
    Sql = "ALTER TABLE "+ tabla +" CHANGE Mod_bat Mod_bat ENUM('OFF','BULK','FLOT','ABS','EQU','INYECT','CONS') CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL DEFAULT 'BULK'";
    print (Sql)
    cursor.execute(Sql)
    print('Mod_bat -OK')
print('#' * 60 )
Sql = """ALTER TABLE `parametros` CHANGE `sensor_PID` `sensor_PID`
          SET('Aux1','Aux2','Vplaca','Iplaca','Wplaca','Vbat','Ibat','Wbat','SOC',
               'Hz','Vred','Ired','Wred')
          CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL DEFAULT 'Vbat'
          COMMENT 'Variable de control PID'"""    
print (Sql)
cursor.execute(Sql)
print('sensor_PID - OK')

# ###### Tablas datos
for tabla in ["datos", "datos_c", "datos_s"]:
    print ( "#" * 30)
    print("Tabla = ", tabla)
    campos = [('Vred',"'V red AC'"),
              ('Wred',"'W inyectados o consumidos de red'"),
              ('Whn_red',"'Wh consumidos de red'"),
              ('Whp_red',"'Wh inyectados a red'")]          
    for campo in campos:
        try:
            Sql = "ALTER TABLE " + tabla+ " ADD " + campo[0] + " FLOAT NOT NULL DEFAULT '0' COMMENT "+ campo[1]
            #print (Sql)
            cursor.execute(Sql)
            print(campo[0],'... creado')
        except:
            print(campo[0],'... ya estaba creado')

# #### Tabla diario
for tabla in ["diario"]:
    print ( "#" * 30)
    print("Tabla = ", tabla)
    campos = [('Whn_red',"'Wh consumidos de red'"),
              ('Whp_red',"'Wh inyectados a red'"),
              ('maxWred',"'maximo W inyectados a red'"),
              ('minWred',"'minimo W consumidos de red'"),
              ('avgWred',"'media W de red'"),
              ('maxVred',"'maxima Vred'"),
              ('minVred',"'minima Vred'")]
    
    for campo in campos:
        try:
            Sql = "ALTER TABLE " + tabla+ " ADD " + campo[0] + " FLOAT NOT NULL DEFAULT '0' COMMENT "+ campo[1]
            #print (Sql)
            cursor.execute(Sql)
            print(campo[0],'... creado')
        except:
            print(campo[0],'... ya estaba creado')


# #### Tabla reles_segundos_on          
Sql = 'ALTER TABLE `control_solar`.`reles_segundos_on` ADD UNIQUE `id_rele_dia` (`id_rele`, `fecha`)'
try:
    cursor.execute(Sql)
    print ('Clave (`id_rele`, `fecha`) creada en reles_sendos_on')
except:
    print ('la Clave (`id_rele`, `fecha`) ya estaba creada en reles_sendos_on')


Sql = """CREATE TABLE `equipos` (
  `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
  `sensores` varchar(500) COLLATE latin1_spanish_ci NOT NULL
) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
"""

try:
    cursor.execute(Sql)
    print ('Creada tabla equipos')
except:
    print ('tabla equipos ya estaba creada ')


Sql = """ALTER TABLE `equipos`
  ADD UNIQUE KEY `sensor` (`id_equipo`);
  """
try:
    cursor.execute(Sql)
    print ('Creada clave en tabla equipos')
except:
    print ('clave en tabla equipos ya estaba creada ')
  
db.commit()
cursor.close()
db.close()
