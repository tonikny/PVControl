#####  EJECUCION .... python3 aemet.py <opciones>

###### OPCIONES DE USO
# -localidad_XXXXX   se debe incuir el id de localidad de Aemet para el municipio  (  ejemplos 28147:Titulcia, 14021:Cordoba,....)
# -l  lluvia
# -t  temperatura
# -c  cielo

##### EJEMPLOS
##  python3 /home/pi/PVControl+/aemet.py -localidad_14021 -c      Descarga la prevision de cielo para Cordoba
##  python3 /home/pi/PVControl+/aemet.py -localidad_14021 -c -t   Descarga la prevision de cielo  y temperatura para Cordoba

import requests,sys,time,MySQLdb,json,subprocess
from Parametros_FV import *

try:
    import xmltodict
except:
    res = subprocess.run('sudo pip3 install xmltodict' , shell=True)
    if res.returncode == 0:
        import xmltodict
    else:
        print ('Error en instalacion libreria xmltodict')
        sys.exit()
        
sel = ''
DEBUG = False
if '-l' in sys.argv: sel += 'l' 
if '-t' in sys.argv: sel += 't'
if '-c' in sys.argv: sel += 'c'
if '-p' in sys.argv: DEBUG= True

for i in sys.argv:
    if '-localidad_' in i[:11]:
        print(sel,i[11:])
        break

URL = f"https://www.aemet.es/xml/municipios/localidad_{i[11:]}.xml"

response = requests.get(URL)

datos_dict= xmltodict.parse(response.content)
dp= datos_dict['root']['prediccion']

d={}
for k in dp['dia']:
    if k['@fecha'] == time.strftime("%Y-%m-%d"): dia = 0
    elif k['@fecha'] == time.strftime("%Y-%m-%d",time.localtime(time.time()+3600*24)): dia = 1
    else: dia = -1
    if dia >= 0:
        d[dia] = {}
        if 'c' in sel:
            d[dia]['cielo'] = {}
            if DEBUG: print ('Cielo:',k['estado_cielo'])
            for k1 in k['estado_cielo']:
                try:
                    if DEBUG: print ('Periodo:',k1['@periodo'],k1['@descripcion'])
                    d[dia]['cielo'][k1['@periodo']] = k1['@descripcion']
                except:
                    d[dia]['cielo'][k1['@periodo']] = ''

        if 't' in sel:
            d[dia]['temperatura'] = {}
            if DEBUG: print ('Temperatura:',k['temperatura'])
            try:
                d[dia]['temperatura']['maxima'] = float(k['temperatura']['maxima'])
                d[dia]['temperatura']['minima'] = float(k['temperatura']['minima']) 
            except:
                d[dia]['temperatura']['maxima'] = d[dia]['temperatura']['minima'] = 0.01
            
            for k1 in k['temperatura']['dato']:
                if DEBUG: print (k1,k1['@hora'],k1['#text'])
                d[dia]['temperatura'][k1['@hora']] = float(k1['#text'])
        
        if 'l' in sel:
            d[dia]['lluvia'] = {}
            if DEBUG: print (dia,'lluvia:',k['prob_precipitacion'])
            for k1 in k['prob_precipitacion']:
                try:
                    if DEBUG: print ('Periodo:',k1['@periodo'],k1['#text'])
                    d[dia]['lluvia'][k1['@periodo']] = float(k1['#text'])
                except:
                    d[dia]['lluvia'][k1['@periodo']] = ''
            
        if DEBUG: print('-' *80)

print (f'd= {d}')

# Comprobacion que la tabla en BD tiene los campos necesarios
try:
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    try: #inicializamos registro en BD RAM
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      ('AEMET','{}'))
        db.commit()
    except:
        pass
except:
    print (Fore.RED,'ERROR inicializando BD')
    sys.exit()

####  ARCHIVOS RAM en BD ############ 
try:
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    salida = json.dumps(d)
    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = 'AEMET'") # grabacion en BD RAM
    cursor.execute(sql)
    db.commit()   
                  
except:
    print(f'error, Grabacion tabla RAM equipos -- {d}')

cursor.close()
db.close()

