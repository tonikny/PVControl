import requests
import time, sys, json
from datetime import datetime
import MySQLdb 

basepath = '/home/pi/PVControl+/'
parametros_FV = basepath + "Parametros_FV.py"
parametros_FV_DIST = basepath + "Parametros_FV_DIST.py"

######## Parametros_FV.py ############
ECOWITT = {
    'ECOWITT': {
        'usar': 0,
        'APPLICATION_KEY': 'XXXXXX',
        'API_KEY' : 'XXXXX',
        'MAC' :  'XXXX',
        't_muestra' : 60
    }
}

exec(open(parametros_FV_DIST).read(),globals())   #carga Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(),globals())        #carga Parametros_FV.py  .... Valores especificos de cada instalacion


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'ECOWITT'
servicio = 'fv_ecowitt'
control =f"{NEQUIPO}['ECOWITT']['usar'] "

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################

N_equipo = 'ECOWITT'
APPLICATION_KEY= ECOWITT['ECOWITT']['APPLICATION_KEY']
API_KEY = ECOWITT['ECOWITT']['API_KEY']
MAC= ECOWITT['ECOWITT']['MAC']
t_muestra = ECOWITT['ECOWITT']['t_muestra']

URL = f'https://api.ecowitt.net/api/v3/device/info?application_key={APPLICATION_KEY}&api_key={API_KEY}&mac={MAC}'


DEBUG = False
#Comprobacion argumentos en comando
if '-p' in sys.argv: DEBUG = True # para test .... realiza print en distintos sitios

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' fv_ecowitt.py') #+Style.RESET_ALL)
print()


def convert_to_metric(data):
    value = float(data['value'])
    if data['unit'] == "ºF":
        return round((value - 32) * 5 / 9, 2)
    elif data['unit'] == "in" or data['unit'] == "in/hr":
        return round(value * 25.4, 2)
    elif data['unit'] == "mph":
        return round(value * 0.44704, 2)
    elif data['unit'] == "inHg":
        return round(value * 33.8639, 2)
    return value  # Sin conversión si la unidad ya está en métrica


def format_timestamp(timestamp):
    """Convierte una marca temporal UNIX en una cadena de fecha y hora legible."""
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def fetch_weather_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # Formateamos la fecha/hora para mostrarla solo una vez en la cabecera
        timestamp = weather_data['data']['last_update']['outdoor']['temperature']['time']
        timestamp_formatted = format_timestamp(timestamp)

        # Diccionario de salida sin unidades y con timestamp
        converted_data = {
            "timestamp": timestamp_formatted
        }

        for category, measurements in weather_data['data']['last_update'].items():
            for measurement, details in measurements.items():
                key = f"{category}_{measurement}"
                converted_data[key] = convert_to_metric(details)  # Solo asignamos el valor, sin unidad

        # Mostrar los datos en consola
        if DEBUG:        
            print(f"Datos de la estación meteorológica - Capturados el {timestamp_formatted}:")
            for key, value in converted_data.items():
                if key != "timestamp":
                    print(f"  {key}: {value}")
            
        return converted_data

    except requests.RequestException as e:
        print(f"Error al obtener los datos: {e}")
        return None


def main():
    url = URL    
    
    try: # creacion registro en tabla equipos
        
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                      (f'{N_equipo}','{}'))   
        db.commit()
    except:
        pass     
            
    cursor.close()
    db.close()
    
    
    while True:
        print("\nObteniendo datos de la estación meteorológica...")
        datos = fetch_weather_data(url)
        
        if datos != None :
            #tiempo = time.strftime('%Y-%m-%d %H:%M:%S')
            tiempo = datos["timestamp"]
            datos.pop("timestamp", None)
            
            #print(f'datos: {datos}')
            
            try:####  ARCHIVOS RAM en BD ############ 
               
                salida = json.dumps(datos, ensure_ascii=False)
                """
                if DEBUG:
                    print()
                    print (f'id_equipo = {N_equipo} -- salida=',salida)
                    print()
                """
                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                cursor = db.cursor()
                
                sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{N_equipo}'") # grabacion en BD RAM
                cursor.execute(sql)
                db.commit()
            except:
                print(Fore.RED+f'error, Grabacion tabla RAM equipos en {N_equipo}')
            
            cursor.close()
            db.close() 
        
        print(f"\nEsperando {t_muestra} segundos para la próxima lectura...\n")
        time.sleep(t_muestra) 

if __name__ == "__main__":
    main()
