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
print ( "#" * 30)
print("Tabla = reles_segundos_on")

Sql = 'ALTER TABLE `control_solar`.`reles_segundos_on` ADD UNIQUE `id_rele_dia` (`id_rele`, `fecha`)'
try:
    cursor.execute(Sql)
    print ('Clave (`id_rele`, `fecha`) creada en reles_sendos_on')
except:
    print ('la Clave (`id_rele`, `fecha`) ya estaba creada en reles_sendos_on')

print ( "#" * 30)
print("Tabla = parametros1")

try:
    sql = """CREATE TABLE IF NOT EXISTS `parametros1` (
              `id_parametro` int(11) NOT NULL,
              `nombre` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
              `valor` varchar(100) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL,
              PRIMARY KEY (`id_parametro`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
         """    
    import warnings # quitamos el warning que da si existe la tabla
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cursor.execute(sql)
    print ('Creada tabla parametros1')
except:
    print ('Error en creacion tabla parametros1')
  
# #### Tabla Reles
print ( "#" * 30)
print("Tabla = RELES")

def c_campo(campo,sql):
    try:
        cursor.execute(sql)
        print (f'Creado campo {campo}')
    except: 
        print (f'Campo {campo} ya estaba creado')

Sql = "ALTER TABLE `reles` CHANGE `prioridad` `prioridad` INT(2) NULL DEFAULT '0' COMMENT 'Define la prioridad en la asignacion de excedentes \r\n - 0 no se utiliza en la asignacion de excedentes)\r\n\r\n - 1 Primera prioridad\r\n\r\n - 2 - Segunda prioridad\r\n\r\n - Etc'"
cursor.execute(Sql)

Sql="ALTER TABLE `reles` ADD `potencia` INT(11) NULL DEFAULT '0' COMMENT 'Watios potencia maxima que controla el rele'"            
c_campo('potencia',Sql)
    
Sql="ALTER TABLE `reles` ADD `retardo` INT(11) NULL DEFAULT '0' COMMENT 'Segundos a esperar entre dos cambios de estado del rele'"            
c_campo('retardo',Sql)

Sql="ALTER TABLE `reles` ADD `calibracion` VARCHAR(500) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL DEFAULT '[[0,0],[1,22],[5,31],[10,36],[20,43],[30,48],[40,53],[50,56],[60,60],[70,65],[80,70],[90,75],[95,77],[99,87],[100,100]]' COMMENT 'Calibracion respuesta SSR [%Potencia, Duty PWM]'"            
c_campo('calibracion',Sql)

cursor.execute("ALTER TABLE `reles` CHANGE `salto` `salto` FLOAT NULL DEFAULT '100'")
print ('Campo salto puesto a FLOAT') 
 
db.commit()


# Borramos tabla equipos y la creamos de nuevo
print ( "#" * 30)
print("Tabla = equipos....", end='')

sql = "DROP TABLE `equipos`"
import warnings # quitamos warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    cursor.execute(sql)

sql = """ CREATE TABLE IF NOT EXISTS `equipos` (
           `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
           `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
           `sensores` varchar(5000) COLLATE latin1_spanish_ci NOT NULL,
            PRIMARY KEY (`id_equipo`)
          ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    cursor.execute(sql)
    
try: #inicializamos registros en BD RAM si no existen
    cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  ('FV','{}'))
    db.commit()
except:
    pass
try: 
    cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  ('RELES','{}'))    
    db.commit()
except:
    pass
try: 
    cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                  ('TEMP','{}'))    
    db.commit()
except:
    pass
print ('...OK')


# tabla datos_celdas
print ( "#" * 30)
print("Tabla = datos_celdas....",end='')

sql = """    
    CREATE TABLE IF NOT EXISTS `datos_celdas` (
    `id_celda` int(11) NOT NULL AUTO_INCREMENT,
    `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
    `C1` float NOT NULL DEFAULT 0,
     PRIMARY KEY (`id_celda`),
     KEY `Tiempo` (`Tiempo`)
     ) 
     ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
     """
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    cursor.execute(sql)
print ('...OK')
db.commit()


cursor.close()
db.close()
