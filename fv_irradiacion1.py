#!/usr/bin/python
# -*- coding: utf-8 -*-
# version 2024-11-11
# SISTEMA FV MULTI-STRING - OPTIMIZADO SIN CONSULTAS DUPLICADAS

# ######## INICIO PARAMETRIZACION EQUIPO ####################
irradiacion = {
    'lat': 40.1403,
    'lon': -3.4256,
    'localidad': 'Chinchon',
    'timezone': 'Europe/Madrid',
    
    'id_equipos': 'SOL',
    'tabla_historica': 'TABLA_IRRADIACION',
    
    'strings': [
        {
            'id': 'string_1',
            'descripcion': 'Tejado principal - Sur',
            'orientacion': 180,
            'inclinacion': 45,
            'potencia_pico': 3500,
            'eficiencia': 0.8,
            'activo': True,
            'tipo_panel': 'Monocristalino'
        },
        {
            'id': 'string_3', 
            'descripcion': 'Tejado Coches - Suroeste',
            'orientacion': -135,
            'inclinacion': 25,
            'potencia_pico': 4800,
            'eficiencia': 0.89,
            'activo': True,
            'tipo_panel': 'Bifaciales'
        },
        {
            'id': 'string_4',
            'descripcion': 'Tejado Baterias - Sureste',
            'orientacion': 135,
            'inclinacion': 25,
            'potencia_pico': 4800,
            'eficiencia': 0.89,
            'activo': True,
            'tipo_panel': 'Monocristalino tipo N'
        },
        {
            'id': 'string_5',
            'descripcion': 'Tejado Coches - Suroeste',
            'orientacion': -135,
            'inclinacion': 47,
            'potencia_pico': 4800,
            'eficiencia': 0.89,
            'activo': True,
            'tipo_panel': 'Bifaciales'
        }
    ]
}
# ########### FIN PARAMETRIZACION EQUIPO ####################

import time, sys, subprocess
import json
from datetime import datetime, timedelta
import MySQLdb

try:
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry
    import pandas as pd
    print("✓ Todas las librerías importadas correctamente")
except ImportError as e:
    print(f"Error: Librerías requeridas no instaladas. Ejecuta:")
    print("pip install openmeteo-requests requests-cache retry-requests pandas")
    print("pip install urllib3==1.26.18") # para compatibilidad con libreria de Telegram
    
    sys.exit(1)

# Parametros Instalacion FV - VALORES POR DEFECTO
try:
    basepath = '/home/pi/PVControl+/'
    parametros_FV = basepath + "Parametros_FV.py"
    parametros_FV_DIST = basepath + "Parametros_FV_DIST.py"

    # Intentar cargar parámetros externos, si no usar valores por defecto
    servidor = "localhost"
    usuario = "usuario_pv"
    clave = "clave_pv" 
    basedatos = "control_pv"
    
    try:
        exec(open(parametros_FV_DIST).read(), globals())
    except:
        print("⚠ No se encontró Parametros_FV_DIST.py, usando valores por defecto")
    
    try:
        exec(open(parametros_FV).read(), globals())
    except:
        print("⚠ No se encontró Parametros_FV.py, usando valores por defecto")
        
except Exception as e:
    print(f"⚠ Error cargando parámetros: {e}, usando valores por defecto")
    servidor = "localhost"
    usuario = "usuario_pv"
    clave = "clave_pv"
    basedatos = "control_pv"


irradiacion = irradiacion1


class SistemaFVMultiStringOpenMeteo:
    def __init__(self, lat, lon, strings, localidad="", timezone="Europe/Madrid"):
        self.lat = lat
        self.lon = lon
        self.strings = strings
        self.localidad = localidad
        self.timezone = timezone
        
        # Setup the Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # Caché interno para evitar consultas duplicadas
        self._cache_datos_configuracion = {}
    
    def obtener_datos_compactos(self):
        """Obtener todos los datos en formato compacto - VERSIÓN OPTIMIZADA"""
        
        print("📊 Obteniendo datos del sistema FV...")
        
        # Limpiar caché al inicio
        self._cache_datos_configuracion = {}
        
        # PASO 1: Obtener configuraciones únicas y consultar API UNA SOLA VEZ
        configs_unicas = self._obtener_configuraciones_unicas()
        print(f"🔧 Configuraciones únicas a consultar: {len(configs_unicas)}")
        
        # Consultar API para cada configuración única
        datos_configs = {}
        for config in configs_unicas:
            datos = self._obtener_datos_configuracion(config['inclinacion'], config['orientacion'])
            if datos:
                clave = (config['inclinacion'], config['orientacion'])
                datos_configs[clave] = datos
                # Guardar en caché para uso posterior
                self._cache_datos_configuracion[clave] = datos
        
        # PASO 2: Procesar todos los datos de una vez
        forecast = self._combinar_pronosticos(datos_configs)
        detalle_strings = self._obtener_detalle_por_string_optimizado(datos_configs)
        produccion_estimada = self.calcular_produccion_estimada_compacta(forecast, detalle_strings)
        pronostico_horario = self.formatear_pronostico_horario_compacto(forecast)
        
        # Strings activos
        strings_activos = [s for s in self.strings if s.get('activo', True)]
        potencia_total = sum(s['potencia_pico'] for s in strings_activos)
        
        # Formato compacto final
        datos_compactos = {
            # Pronóstico horario para días 0, 1, 2
            **pronostico_horario,
            
            # Configuración
            "configuracion": {
                "localidad": self.localidad,
                "lat": self.lat,
                "lon": self.lon,
                "potencia_total": potencia_total,
                "strings_activos": len(strings_activos),
                "strings_total": len(self.strings)
            },
            
            # Producción estimada
            "produccion_estimada": produccion_estimada,
            
            # Strings
            "strings": self._obtener_info_strings_compacta()
        }
        
        return datos_compactos
    
    def _obtener_configuraciones_unicas(self):
        """Obtener configuraciones únicas de orientación/inclinación"""
        configs_unicas = []
        configs_vistas = set()
        
        for string in self.strings:
            if not string.get('activo', True):
                continue
                
            config_key = (string['inclinacion'], string['orientacion'])
            if config_key not in configs_vistas:
                configs_vistas.add(config_key)
                configs_unicas.append({
                    'inclinacion': string['inclinacion'],
                    'orientacion': string['orientacion']
                })
        
        return configs_unicas
    
    def _obtener_datos_configuracion(self, tilt, azimuth):
        """Obtener datos de Open-Meteo para configuración específica"""
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "hourly": "global_tilted_irradiance_instant",
            "timezone": self.timezone,
            "forecast_days": 15,
            "tilt": tilt,
            "azimuth": azimuth
        }
        
        try:
            print(f"🌤️ Consultando API: tilt={tilt}°, azimuth={azimuth}°")
            responses = self.openmeteo.weather_api(url, params=params)
            response = responses[0]
            
            # Procesar datos horarios
            hourly = response.Hourly()
            hourly_global_tilted = hourly.Variables(0).ValuesAsNumpy()
            
            # Crear rango de fechas
            hourly_dates = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
            
            # Convertir a formato compatible
            return self._procesar_datos_horarios(hourly_dates, hourly_global_tilted)
            
        except Exception as e:
            print(f"❌ Error obteniendo datos para tilt={tilt}, azimuth={azimuth}: {e}")
            return None
    
    def _procesar_datos_horarios(self, dates, irradiance_values):
        """Procesar datos horarios al formato del sistema"""
        
        pronostico = {}
        day_index = 0
        fecha_actual = ""
        
        for i, date in enumerate(dates):
            # Convertir a timezone local
            date_local = date.tz_convert(self.timezone)
            fecha = date_local.strftime('%Y-%m-%d')
            hora = date_local.strftime('%H:%M')
            
            if fecha != fecha_actual:
                day_index += 1
                fecha_actual = fecha
                pronostico[day_index] = {'Fecha': fecha}
            
            irradiancia = irradiance_values[i] if irradiance_values[i] is not None else 0
            pronostico[day_index][hora] = max(0, round(irradiancia))
        
        return pronostico
    
    def _combinar_pronosticos(self, datos_configs):
        """Combinar pronósticos de todas las configuraciones"""
        
        if not datos_configs:
            return self._datos_por_defecto()
        
        pronostico_combinado = {}
        
        for config_key, datos_config in datos_configs.items():
            tilt, azimuth = config_key
            
            for day_index, day_data in datos_config.items():
                if day_index not in pronostico_combinado:
                    pronostico_combinado[day_index] = {'Fecha': day_data['Fecha']}
                
                # Calcular contribución de strings con esta configuración
                strings_config = [
                    string for string in self.strings 
                    if string.get('activo', True) 
                    and string['inclinacion'] == tilt
                    and string['orientacion'] == azimuth
                ]
                
                if not strings_config:
                    continue
                
                # Para cada hora, sumar la producción de los strings con esta configuración
                for hora_str, irradiancia in day_data.items():
                    if hora_str == 'Fecha':
                        continue
                    
                    if hora_str not in pronostico_combinado[day_index]:
                        pronostico_combinado[day_index][hora_str] = 0
                    
                    # Calcular producción total para esta configuración
                    produccion_total = 0
                    for string in strings_config:
                        produccion_string = self._calcular_produccion_string(irradiancia, string)
                        produccion_total += produccion_string
                    
                    pronostico_combinado[day_index][hora_str] += produccion_total
        
        # Redondear valores horarios
        for day_index, hourly_data in pronostico_combinado.items():
            for hora in list(hourly_data.keys()):
                if hora != 'Fecha':
                    hourly_data[hora] = round(hourly_data[hora])
        
        return pronostico_combinado
    
    def _calcular_produccion_string(self, irradiancia_wm2, string_config):
        """Calcular producción para un string específico"""
        # Producción (W) = Irradiancia (W/m²) × Potencia pico (Wp) × Eficiencia / 1000
        produccion = (irradiancia_wm2 * string_config['potencia_pico'] * string_config['eficiencia']) / 1000
        return max(0, produccion)
    
    def _obtener_detalle_por_string_optimizado(self, datos_configs):
        """Obtener pronóstico detallado por cada string USANDO DATOS YA OBTENIDOS"""
        
        print("🔍 Calculando detalle por string...")
        detalle_strings = {}
        
        for string in self.strings:
            if not string.get('activo', True):
                continue
                
            # Buscar en los datos ya obtenidos
            config_key = (string['inclinacion'], string['orientacion'])
            if config_key in datos_configs:
                datos = datos_configs[config_key]
                pronostico_string = {}
                
                for day_index, day_data in datos.items():
                    pronostico_string[day_index] = {'Fecha': day_data['Fecha']}
                    
                    for hora_str, irradiancia in day_data.items():
                        if hora_str == 'Fecha':
                            continue
                        
                        produccion = self._calcular_produccion_string(irradiancia, string)
                        pronostico_string[day_index][hora_str] = round(produccion)
                
                detalle_strings[string['id']] = pronostico_string
        
        return detalle_strings
    
    def calcular_produccion_estimada_compacta(self, forecast, detalle_strings):
        """Calcular producción estimada en formato compacto"""
        
        produccion_estimada = {}
        
        # Calcular para hoy (día 0), mañana (día 1) y pasado (día 2)
        for dia_original in [1, 2, 3]:
            dia_compacto = dia_original - 1  # Convertir 1,2,3 a 0,1,2
            
            if dia_original not in forecast:
                continue
                
            fecha = forecast[dia_original]['Fecha']
            
            # Producción global del día
            produccion_total_dia = self._calcular_produccion_total_dia(forecast[dia_original])
            bloques_kwh = self._calcular_bloques_compactos(forecast[dia_original])
            
            # Producción por string
            produccion_strings = {}
            for string_id, string_detalle in detalle_strings.items():
                if dia_original in string_detalle:
                    produccion_string_dia = self._calcular_produccion_total_dia(string_detalle[dia_original])
                    produccion_strings[string_id] = round(produccion_string_dia / 1000, 2)
            
            produccion_estimada[dia_compacto] = {
                'fecha': fecha,
                'total_kwh': round(produccion_total_dia / 1000, 2),
                'manana': bloques_kwh['manana'],
                'central': bloques_kwh['central'],
                'tarde': bloques_kwh['tarde'],
                **produccion_strings  # Incluir producción por string directamente
            }
        
        return produccion_estimada
    
    def _calcular_produccion_total_dia(self, dia_data):
        """Calcular producción total de un día en Wh"""
        produccion_total = 0
        for hora_str, produccion in dia_data.items():
            if hora_str != 'Fecha':
                produccion_total += produccion
        return produccion_total
    
    def _calcular_bloques_compactos(self, dia_data):
        """Calcular producción por bloques en formato compacto"""
        bloques = {
            'manana': 0,    # 6:00 - 12:00
            'central': 0,   # 12:00 - 18:00  
            'tarde': 0      # 18:00 - 24:00
        }
        
        for hora_str, produccion in dia_data.items():
            if hora_str == 'Fecha':
                continue
            
            hora = int(hora_str.split(':')[0])
            
            if 6 <= hora < 12:
                bloques['manana'] += produccion
            elif 12 <= hora < 18:
                bloques['central'] += produccion
            elif 18 <= hora < 24:
                bloques['tarde'] += produccion
        
        # Convertir a kWh y redondear
        for bloque in bloques:
            bloques[bloque] = round(bloques[bloque] / 1000, 2)
        
        return bloques
    
    def formatear_pronostico_horario_compacto(self, forecast):
        """Formatear pronóstico horario en formato compacto (0,1,2)"""
        pronostico_compacto = {}
        
        for dia_original in [1, 2, 3]:
            dia_compacto = dia_original - 1  # Convertir 1,2,3 a 0,1,2
            
            if dia_original not in forecast:
                pronostico_compacto[dia_compacto] = self._generar_horas_cero()
                continue
            
            dia_data = forecast[dia_original]
            pronostico_compacto[dia_compacto] = self._generar_estructura_horaria(dia_data)
        
        return pronostico_compacto
    
    def _generar_horas_cero(self):
        """Generar estructura de 24 horas con valores cero"""
        horas = {}
        for hora in range(24):
            hora_str = f"{hora:02}:00"
            horas[hora_str] = 0
        return horas
    
    def _generar_estructura_horaria(self, dia_data):
        """Generar estructura horaria completa para un día"""
        horas = self._generar_horas_cero()
        
        for hora_str, produccion in dia_data.items():
            if hora_str != 'Fecha':
                horas[hora_str] = produccion
        
        return horas
    
    def _obtener_info_strings_compacta(self):
        """Obtener información de strings en formato compacto"""
        info_strings = {}
        
        for string in self.strings:
            if string.get('activo', True):
                info_strings[string['id']] = {
                    'descripcion': string['descripcion'],
                    'orientacion': string['orientacion'],
                    'inclinacion': string['inclinacion'],
                    'potencia_pico': string['potencia_pico'],
                    'eficiencia': string['eficiencia'],
                    'activo': True,
                    'tipo_panel': string.get('tipo_panel', 'No especificado')
                }
        
        return info_strings
    
    def _datos_por_defecto(self):
        """Generar datos por defecto cuando la API falla"""
        print("⚠ Generando datos por defecto...")
        
        hoy = datetime.now()
        pronostico = {}
        
        for day_index in range(1, 4):
            fecha = (hoy + timedelta(days=day_index-1)).strftime('%Y-%m-%d')
            pronostico[day_index] = {'Fecha': fecha}
            
            for hora in range(24):
                hora_str = f"{hora:02}:00"
                irradiancia_estimada = self._calcular_irradiancia_estimada(hora, hoy.month)
                pronostico[day_index][hora_str] = max(0, round(irradiancia_estimada))
        
        return pronostico
    
    def _calcular_irradiancia_estimada(self, hora, mes):
        """Calcular irradiancia estimada para fallback"""
        if mes in [12, 1]:
            inicio_sol, fin_sol = 8, 17
            max_irrad = 600
        elif mes in [6, 7]:
            inicio_sol, fin_sol = 6, 21
            max_irrad = 900
        else:
            inicio_sol, fin_sol = 7, 19
            max_irrad = 750
        
        if inicio_sol <= hora <= fin_sol:
            hora_media = (inicio_sol + fin_sol) / 2
            desviacion = abs(hora - hora_media)
            
            if desviacion <= 1:
                return max_irrad
            elif desviacion <= 3:
                return int(max_irrad * 0.8)
            elif desviacion <= 5:
                return int(max_irrad * 0.5)
            else:
                return int(max_irrad * 0.2)
        else:
            return 0

def inicializar_tabla_historica(cursor, nombre_tabla):
    """Inicializar tabla histórica con nombre parametrizado"""
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                Tiempo DATETIME PRIMARY KEY,
                Wirradiacion FLOAT DEFAULT 0,
                Wh_placa FLOAT DEFAULT 0,
                Wh_bat FLOAT DEFAULT 0,
                Wh_red FLOAT DEFAULT 0,
                Wh_consumo FLOAT DEFAULT 0,
                Excedente FLOAT DEFAULT 0,
                SOC FLOAT DEFAULT 0,
                Temperatura FLOAT DEFAULT 0
            )
        """)
        print(f"✓ Tabla {nombre_tabla} verificada")
    except Exception as e:
        print(f"❌ Error inicializando tabla {nombre_tabla}: {e}")

def guardar_datos_compactos(cursor, datos_compactos, id_equipos):
    """Guardar datos en formato compacto"""
    
    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Convertir a JSON string para el campo sensores
        salida = json.dumps(datos_compactos)
        
        # Insertar o actualizar en equipos
        sql = """
            INSERT INTO equipos (id_equipo, tiempo, sensores)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                tiempo = VALUES(tiempo),
                sensores = VALUES(sensores)
        """
        
        cursor.execute(sql, (id_equipos, tiempo, salida))
        
        if cursor.rowcount == 1:
            print(f"✅ Nuevo registro {id_equipos} creado")
        elif cursor.rowcount == 2:
            print(f"✅ Registro {id_equipos} actualizado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error guardando datos en {id_equipos}: {e}")
        return False

def insertar_pronostico_irradiacion(cursor, forecast, nombre_tabla):
    """Insertar pronóstico en tabla histórica"""
    
    try:
        registros_insertados = 0
        
        for day_data in forecast.values():
            fecha_base = day_data['Fecha']
            
            for hora in range(24):
                hora_str = f"{hora:02}:00"
                watts_previstos = day_data.get(hora_str, 0)

                fecha_hora_str = f"{fecha_base} {hora_str}"
                fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')

                sql = f"""
                INSERT INTO {nombre_tabla} (Tiempo, Wirradiacion)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE Wirradiacion = VALUES(Wirradiacion)
                """
                cursor.execute(sql, (fecha_hora, watts_previstos))
                registros_insertados += 1
        
        print(f"✅ {registros_insertados} registros insertados/actualizados en {nombre_tabla}")
        return True
        
    except Exception as e:
        print(f"❌ Error insertando en {nombre_tabla}: {e}")
        return False

def obtener_datos_reales_produccion(cursor, tabla_historica):
    """Obtener datos reales de producción desde la tabla 'datos' y actualizar tabla histórica"""
    
    try:
        print("📊 Obteniendo datos reales de producción...")
        
        # Consulta SQL para calcular Wh producidos por hora desde valores acumulados
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
                SOC
            FROM datos_dia1
            WHERE rn = 1

            UNION ALL

            SELECT 
                bloque_hora,
                Wh_placa - COALESCE(LAG(Wh_placa) OVER (ORDER BY bloque_hora), 0) AS Wh_placa,
                Wh_bat - COALESCE(LAG(Wh_bat) OVER (ORDER BY bloque_hora), 0) AS Wh_bat,
                Wh_red - COALESCE(LAG(Wh_red) OVER (ORDER BY bloque_hora), 0) AS Wh_red,
                Wh_consumo - COALESCE(LAG(Wh_consumo) OVER (ORDER BY bloque_hora), 0) AS Wh_consumo,
                SOC
            FROM datos_dia2
            WHERE rn = 1
            ORDER BY bloque_hora;
        """
        
        cursor.execute(sql_datos_reales)
        datos_reales = cursor.fetchall()
        
        print(f"📈 Se encontraron {len(datos_reales)} registros de datos reales")
        
        # Insertar o actualizar los valores reales en la tabla histórica
        registros_actualizados = 0
        for Tiempo, Wh_placa, Wh_bat, Wh_red, Wh_consumo, SOC in datos_reales:
            # Asegurar que los valores no sean negativos (puede ocurrir al reiniciar contadores)
            Wh_placa = max(0, Wh_placa) if Wh_placa is not None else 0
            Wh_bat = Wh_bat if Wh_bat is not None else 0
            Wh_red = Wh_red if Wh_red is not None else 0
            Wh_consumo = max(0, Wh_consumo) if Wh_consumo is not None else 0
            SOC = SOC if SOC is not None else 0
            
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
            
            cursor.execute(sql_insercion_real, (Tiempo, Wh_placa, Wh_bat, Wh_red, Wh_consumo, SOC))
            registros_actualizados += 1
        
        print(f"✅ {registros_actualizados} registros reales actualizados en {tabla_historica}")
        return True
        
    except Exception as e:
        print(f"❌ Error procesando datos reales: {e}")
        return False

def main():
    """Función principal"""
    
    print("=" * 60)
    print("SISTEMA FV MULTI-STRING")
    print("=" * 60)
    
    # Obtener nombres de tablas parametrizados
    id_equipos = irradiacion.get('id_equipos', 'SOL')
    tabla_historica = irradiacion.get('tabla_historica', 'TABLA_IRRADIACION')
    
    print(f"📊 ID Equipos: {id_equipos}")
    print(f"📈 Tabla Histórica: {tabla_historica}")
    
    # Conectar a BD
    try:
        db = MySQLdb.connect(host=servidor, user=usuario, passwd=clave, db=basedatos)
        cursor = db.cursor()
        print("✅ Conexión a BD establecida")
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        print("⚠ Continuando sin conexión a BD...")
        return
    
    # Inicializar tabla histórica con nombre parametrizado
    inicializar_tabla_historica(cursor, tabla_historica)
    
    # Inicializar sistema FV
    sistema_fv = SistemaFVMultiStringOpenMeteo(
        lat=irradiacion['lat'],
        lon=irradiacion['lon'],
        strings=irradiacion['strings'],
        localidad=irradiacion['localidad'],
        timezone=irradiacion.get('timezone', 'Europe/Madrid')
    )
    
    # Obtener datos en formato compacto (OPTIMIZADO)
    datos_compactos = sistema_fv.obtener_datos_compactos()
    
    # Obtener forecast para tabla histórica (usando el mismo método interno)
    forecast = sistema_fv._combinar_pronosticos(sistema_fv._cache_datos_configuracion)
    
    # Mostrar resumen
    config = datos_compactos['configuracion']
    produccion = datos_compactos['produccion_estimada']
    
    print("\n" + "=" * 40)
    print("RESUMEN DEL SISTEMA FV")
    print("=" * 40)
    print(f"📍 Ubicación: {config['localidad']}")
    print(f"⚡ Potencia total: {config['potencia_total']} Wp")
    print(f"🔧 Strings: {config['strings_activos']} activos")
    
    # Mostrar producción estimada
    for dia in [0, 1, 2]:
        if dia in produccion:
            datos_dia = produccion[dia]
            print(f"\n📅 Día {dia} ({datos_dia['fecha']}):")
            print(f"   Total: {datos_dia['total_kwh']} kWh")
            print(f"   Bloques: Mañana {datos_dia['manana']} kWh | "
                  f"Central {datos_dia['central']} kWh | "
                  f"Tarde {datos_dia['tarde']} kWh")
            # Mostrar producción por string
            for string_id, kwh in datos_dia.items():
                if string_id not in ['fecha', 'total_kwh', 'manana', 'central', 'tarde']:
                    print(f"   {string_id}: {kwh} kWh")
    
    # Guardar datos en BD
    print("\n💾 Guardando datos en base de datos...")
    
    # 1. Guardar datos compactos en tabla equipos
    if guardar_datos_compactos(cursor, datos_compactos, id_equipos):
        print(f"✅ Datos compactos guardados en registro {id_equipos}")
    else:
        print(f"❌ Error guardando en {id_equipos}")
    
    # 2. Insertar pronóstico en tabla histórica
    if insertar_pronostico_irradiacion(cursor, forecast, tabla_historica):
        print(f"✅ Pronóstico guardado en {tabla_historica}")
    else:
        print(f"❌ Error guardando pronóstico en {tabla_historica}")
    
    # 3. ACTUALIZAR CON DATOS REALES DE PRODUCCIÓN
    if obtener_datos_reales_produccion(cursor, tabla_historica):
        print(f"✅ Datos reales de producción actualizados en {tabla_historica}")
    else:
        print(f"❌ Error actualizando datos reales en {tabla_historica}")
    
    # Confirmar cambios y cerrar conexión
    try:
        db.commit()
        cursor.close()
        db.close()
        print("✅ Cambios confirmados en BD")
    except Exception as e:
        print(f"❌ Error confirmando cambios: {e}")
    
    print("\n🎯 Script ejecutado exitosamente!")
    print(f"⏰ Hora de finalización: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()