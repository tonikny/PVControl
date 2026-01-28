#!/usr/bin/python
# -*- coding: utf-8 -*-
# version 2025-12-29

# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################

irradiacion = {
    'url': "https://www.tutiempo.net/radiacion-solar/titulcia.html",
    'factor': 7,                            # factor a multiplicar los w/m2 capturados para la FV instalada
                                            # tipicamente entre un 7-12% de los m2 de placas
    'id_equipos': 'SOL',                    # Nombre del registro en tabla equipos
    'tabla_historica': 'TABLA_IRRADIACION'  # Nombre de la tabla historica
}
# ########### FIN PARAMETRIZACION EQUIPO ####################

import time, sys, subprocess
import json
from datetime import datetime, timedelta

# Parametros Instalacion FV
basepath = '/home/pi/PVControl+/'
parametros_FV = basepath + "Parametros_FV.py"
parametros_FV_DIST = basepath + "Parametros_FV_DIST.py"

exec(open(parametros_FV_DIST).read(), globals())  # carga Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(), globals())       # carga Parametros_FV.py  .... Valores especificos de cada instalacion

import requests
from bs4 import BeautifulSoup
import re
import MySQLdb

url = irradiacion['url']

# Obtener valores de configuración con valores por defecto
factor = irradiacion.get('factor', 1)  # Por defecto 1 si no está definido
id_equipos = irradiacion.get('id_equipos', 'SOL')  # Por defecto 'SOL'
tabla_historica = irradiacion.get('tabla_historica', 'TABLA_IRRADIACION')  # Por defecto 'TABLA_IRRADIACION'

# Conectar a la base de datos
db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
cursor = db.cursor()

# Crear la tabla si no existe con la nueva estructura
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {tabla_historica} (
        Tiempo DATETIME PRIMARY KEY,      -- Identificador único basado en la fecha y hora
        
        Wirradiacion FLOAT DEFAULT 0,     -- Potencia irradiacion estimada para la FV instalada en W (W/m2 * factor)
        Wirradiacion_m2 FLOAT DEFAULT 0,  -- Potencia irradiacion por m2 en W/m2 (valor original de tutiempo)
        Wh_placa FLOAT DEFAULT 0,         -- Energía generada real en Wh
        Wh_bat FLOAT DEFAULT 0,           -- Energía a/desde bateria real en Wh
        Wh_red FLOAT DEFAULT 0,           -- Energía a/desde Red AC real en Wh
        Wh_consumo FLOAT DEFAULT 0,       -- Energía consumida durante la hora en Wh
        
        Excedente FLOAT DEFAULT 0,        -- Excedente estimado (si aplica)
        SOC FLOAT DEFAULT 0,              -- Estado de carga de la batería en %
        Temperatura FLOAT DEFAULT 0       -- Temperatura en °C (opcional)
    )
""")
db.commit()

# Verificar si existe el campo Wirradiacion_m2 y añadirlo si no existe
try:
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = '{basedatos}' 
        AND TABLE_NAME = '{tabla_historica}' 
        AND COLUMN_NAME = 'Wirradiacion_m2'
    """)
    
    if cursor.fetchone()[0] == 0:
        print(f"Campo Wirradiacion_m2 no encontrado en {tabla_historica}. Añadiendo campo...")
        cursor.execute(f"""
            ALTER TABLE {tabla_historica} 
            ADD COLUMN Wirradiacion_m2 FLOAT DEFAULT 0 AFTER Wirradiacion
        """)
        db.commit()
        print("Campo Wirradiacion_m2 añadido correctamente")
    else:
        print("Campo Wirradiacion_m2 ya existe en la tabla")
        
except Exception as e:
    print(f"Error al verificar/añadir campo Wirradiacion_m2: {e}")
    sys.exit()

# ==========================
# Parte 1: Captura de previsión de irradiación
# ==========================

# Descargar y decodificar el contenido de la página
response = requests.get(url, verify=False)
response.encoding = 'utf-8'

# Analizar el contenido con BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')
text = soup.get_text()

# Patrón para extraer la fecha de cada día
date_pattern = r"(Hoy|Mañana|Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s(\d{1,2} de [a-zA-Z]+)\d*:"

# Patrón para extraer los valores de hora y radiación
forecast_pattern = r"(\d{2}:\d{2})(\d+)\s?w/m2"

# Diccionario para almacenar los pronósticos por día
forecast = {}

# Extraer las secciones por cada día
days_matches = re.findall(date_pattern, text)

# Obtener fecha actual para determinar años correctos
now = datetime.now()
current_year = now.year
current_month = now.month

# Crear un índice para los días
day_index = 0

for day_match in days_matches:
    day_of_week, date_str = day_match
    
    # Extraer el día y el mes
    day, month_name = date_str.split(" de ")
    month = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5,
        "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10,
        "Noviembre": 11, "Diciembre": 12
    }.get(month_name, 0)
    
    # Determinar el año correcto
    # Si el mes extraído es menor que el mes actual (ej: Enero vs Diciembre)
    # y estamos en diciembre, entonces el año debe ser el siguiente
    year = current_year
    if month < current_month and current_month == 12:
        year = current_year + 1
    # Si el mes extraído es mayor que el mes actual (ej: Diciembre vs Enero)
    # y estamos en enero, entonces el año debe ser el anterior
    elif month > current_month and current_month == 1:
        year = current_year - 1
    else:
        year = current_year
    
    # Formatear la fecha
    formatted_date = datetime(year, month, int(day)).strftime('%Y-%m-%d')
    
    # Extraer los pronósticos horarios del día
    day_forecast_pattern = re.search(f"{date_str}.*?(Pronóstico por hora.*?Radiación solar total:)", text, re.DOTALL)
    if day_forecast_pattern:
        day_forecast_text = day_forecast_pattern.group(0)
        forecast_matches = re.findall(forecast_pattern, day_forecast_text)
        
        # Añadir el pronóstico del día al diccionario con índice
        forecast[day_index] = {'Fecha': formatted_date}
        for time1, radiation in forecast_matches:
            forecast[day_index][time1] = int(radiation)

        # Incrementar el índice para el siguiente día
        day_index += 1

# Calculamos el total de cada día
for date in forecast:
    total_value = sum(forecast[date].get(hour, 0) for hour in forecast[date] if hour != 'Fecha')
    forecast[date]['Total'] = total_value

# Mostrar los resultados
#for day_index, hourly_data in forecast.items():
#    print(f"{day_index}: {hourly_data}")

# Bloque de inserción de los datos de irradiación
#fuente = url  # Identificar la fuente de los datos

for day_data in forecast.values():
    fecha_base = day_data['Fecha']
    print('fecha:', fecha_base)
    
    # Iterar a través de todas las horas del día
    for hora in range(24):
        hora_str = f"{hora:02}:00"  # Formato de hora en 'HH:MM'
        watts_por_m2 = day_data.get(hora_str, 0)  # Usar 0 si la hora no tiene valor en day_data
        watts_previstos_FV = watts_por_m2 * factor  # Aplicar factor de corrección FV

        # Construir el valor de fecha_hora combinando fecha_base y la hora
        fecha_hora_str = f"{fecha_base} {hora_str}"
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')

        # Preparar la consulta SQL para insertar
        sql = f"""
        INSERT INTO {tabla_historica} (Tiempo, Wirradiacion, Wirradiacion_m2)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            Wirradiacion = VALUES(Wirradiacion),
            Wirradiacion_m2 = VALUES(Wirradiacion_m2)
        """
        valores = (fecha_hora, watts_previstos_FV, watts_por_m2)

        # Ejecutar el SQL
        cursor.execute(sql, valores)
        
        print(valores)

# ==========================
# Parte 2: Actualizar Tabla equipos con información enriquecida y compatible
# ==========================

# inicializo registro tabla equipos si no existe
cursor.execute("""
    INSERT IGNORE INTO equipos (id_equipo, sensores)
    VALUES (%s, %s)
""", (id_equipos, '{}'))
#db.commit()

try:
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Procesar los próximos 3 días (hoy, mañana y pasado) manteniendo compatibilidad
    forecast_proximo = {}
    
    for day_key in [0, 1, 2]:
        if day_key in forecast:
            day_data = forecast[day_key]
            fecha = day_data['Fecha']
            
            # Calcular kWh totales del día (suma de W * factor / 1000)
            kwh_total = 0
            kwh_manana = 0    # 6-12h
            kwh_central = 0   # 12-18h  
            kwh_tarde = 0     # 18-24h
            
            # Crear estructura compatible manteniendo las horas a primer nivel
            day_forecast = {
                'Fecha': fecha,
                'kwh': 0,
                'manana': 0,
                'central': 0,
                'tarde': 0
            }
            
            for hora in range(24):
                hora_str = f"{hora:02}:00"
                watts_por_m2 = day_data.get(hora_str, 0)
                watts_corregidos = watts_por_m2 * factor
                wh_corregidos = watts_corregidos  # W por hora = Wh
                
                # Guardar valor corregido para esta hora (a primer nivel para compatibilidad)
                day_forecast[hora_str] = watts_corregidos
                
                # Acumular kWh total
                kwh_total += wh_corregidos / 1000
                
                # Acumular por periodos
                if 6 <= hora < 12:
                    kwh_manana += wh_corregidos / 1000
                elif 12 <= hora < 18:
                    kwh_central += wh_corregidos / 1000
                elif 18 <= hora < 24:
                    kwh_tarde += wh_corregidos / 1000
            
            # Actualizar los campos calculados
            day_forecast['kwh'] = round(kwh_total, 2)
            day_forecast['manana'] = round(kwh_manana, 2)
            day_forecast['central'] = round(kwh_central, 2)
            day_forecast['tarde'] = round(kwh_tarde, 2)
            
            # Añadir al diccionario principal (claves numéricas sin comillas)
            forecast_proximo[day_key] = day_forecast

    salida = json.dumps(forecast_proximo)
    
    print("Datos enriquecidos para tabla equipos (formato compatible):")
    print(salida)
    
    sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{id_equipos}'") # grabacion en BD RAM
    cursor.execute(sql)
    
              
except Exception as e:
    print(f'error, Grabacion tabla RAM equipos -- {e}')
    sys.exit()

# ==========================
# Parte 3: Captura de valores reales
# ==========================

# Consultar y procesar los valores reales desde la tabla "datos"
sql_datos_reales = """
    WITH datos_dia1 AS (
        SELECT 
            DATE_FORMAT(Tiempo, '%Y-%m-%d %H:00:00') AS bloque_hora,
            Wh_placa,
            (Whp_bat - Whn_bat) AS Wh_bat,
            (Whp_red - Whn_red) AS Wh_red,
            (Wh_placa - (Whp_bat - Whn_bat) - (Whp_red - Whn_red)) AS Wh_consumo,
            SOC,
            ROW_NUMBER() OVER (PARTITION BY DATE_FORMAT(Tiempo, '%Y-%m-%d %H') ORDER BY Tiempo DESC) AS rn
        FROM datos
        WHERE Tiempo BETWEEN CURDATE() - INTERVAL 1 DAY AND CURDATE() - INTERVAL 1 SECOND
    ),
    datos_dia2 AS (
        SELECT 
            DATE_FORMAT(Tiempo, '%Y-%m-%d %H:00:00') AS bloque_hora,
            Wh_placa,
            (Whp_bat - Whn_bat) AS Wh_bat,
            (Whp_red - Whn_red) AS Wh_red,
            (Wh_placa - (Whp_bat - Whn_bat) - (Whp_red - Whn_red)) AS Wh_consumo,
            SOC,
            ROW_NUMBER() OVER (PARTITION BY DATE_FORMAT(Tiempo, '%Y-%m-%d %H') ORDER BY Tiempo DESC) AS rn
        FROM datos
        WHERE Tiempo BETWEEN CURDATE() AND CURDATE() + INTERVAL 1 DAY - INTERVAL 1 SECOND
    )
    SELECT 
        bloque_hora,
        Wh_placa - COALESCE(LAG(Wh_placa) OVER (ORDER BY bloque_hora), 0) AS Wh_placa,
        Wh_bat - COALESCE(LAG(Wh_bat) OVER (ORDER BY bloque_hora), 0) AS Wh_bat,
        Wh_red - COALESCE(LAG(Wh_red) OVER (ORDER BY bloque_hora), 0) AS Wh_red,
        Wh_consumo - COALESCE(LAG(Wh_consumo) OVER (ORDER BY bloque_hora), 0) AS Wh_consumo,
        SOC  -- Directamente tomamos el SOC sin LAG
        
    FROM datos_dia1
    WHERE rn = 1

    UNION ALL

    SELECT 
        bloque_hora,
        Wh_placa - COALESCE(LAG(Wh_placa) OVER (ORDER BY bloque_hora), 0) AS Wh_placa,
        Wh_bat - COALESCE(LAG(Wh_bat) OVER (ORDER BY bloque_hora), 0) AS Wh_bat,
        Wh_red - COALESCE(LAG(Wh_red) OVER (ORDER BY bloque_hora), 0) AS Wh_red,
        Wh_consumo - COALESCE(LAG(Wh_consumo) OVER (ORDER BY bloque_hora), 0) AS Wh_consumo,
        SOC  -- Directamente tomamos el SOC sin LAG
        
    FROM datos_dia2
    WHERE rn = 1
    ORDER BY bloque_hora;
"""

cursor.execute(sql_datos_reales)
datos_reales = cursor.fetchall()

# Insertar o actualizar los valores reales en la tabla irradiacion
for Tiempo, Wh_placa, Wh_bat, Wh_red, Wh_consumo, SOC  in datos_reales:
    valores_insercion_real = (Tiempo, Wh_placa, Wh_bat, Wh_red, Wh_consumo, SOC)
    
    sql_insercion_real = f"""
        INSERT INTO {tabla_historica} (Tiempo, Wh_placa, Wh_bat, Wh_red, Wh_consumo, SOC)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            Wh_placa = VALUES(Wh_placa), 
            Wh_bat = VALUES(Wh_bat), 
            Wh_red = VALUES(Wh_red), 
            Wh_consumo = VALUES(Wh_consumo), 
            SOC = VALUES(SOC)
        """

    cursor.execute(sql_insercion_real, valores_insercion_real)

# Confirmar los cambios
db.commit()

# Cerrar la conexión
cursor.close()
db.close()