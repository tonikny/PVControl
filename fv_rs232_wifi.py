
# ######## INICIO PARAMETRIZACION EQUIPO ####################
# 
# UN BLOQUE COMO ESTE SE DEBE INCLUIR EN Parametros_FV.py
#
# ¡¡¡¡ NO MODIFICAR ESTE FICHERO !!!!
#
# ###########################################################

# CONFIGURACIÓN GENERALIZADA PARA MÚLTIPLES MODELOS USANDO DONGLE WIFI
RS232_WIFI = {
    'ANENJI1': {                      # Nombre del registro que aparecera en tabla equipos
        'usar': 0,                    # Desactivado
        'modelo': 'ANENJI6K2',        # Definir el modelo de equipo entre los modelos disponibles
        'IP': '',                     # IP del dongle WiFi, si '' se asignara segun scan de dongles en LAN
        'tiempo_captura': 5,          # Tiempo entra cada captura
    },
    
    'ANENJI2': {
        'usar': 0,  # Desactivado
        'modelo': 'ANENJI11K',
        'IP': '',
        'tiempo_captura': 5,
    },
    
    'ANENJI3': {
        'usar': 0,  # Activado
        'modelo': 'ANENJI6K2',
        'IP': '',
        'tiempo_captura': 5,
    },

    'MODELOS_EQUIPOS': {
        
        'ANENJI6K2': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos': [[201, 234], [300, 337], [406, 420]]
                },
            },
            
            'REGISTROS': {
                'WM': {
                    'reg': 201,
                    'tipo': 'adaptar',
                    'adaptar': [
                        "if d == 0: resultado = '0-Power On'",
                        "elif d == 1: resultado = '1-Standby'", 
                        "elif d == 2: resultado = '2-Mains'",
                        "elif d == 3: resultado = '3-Off-Grid'",
                        "elif d == 4: resultado = '4-Bypass'",
                        "elif d == 5: resultado = '5-Charging'",
                        "elif d == 6: resultado = '6-Fault'",
                    ]
                },
                'Vred': {'reg': 202, 'dec': 1},
                'Fred': {'reg': 203, 'dec': 2},
                'Wred': {'reg': 204},
                'Vred_aff': {'reg': 205, 'dec': 1},
                'Ired_aff': {'reg': 206, 'dec': 1},
                'Finv': {'reg': 207, 'dec': 2},
                'Winv': {'reg': 208, 'tipo': 's16'},
                'Winv_bat': {'reg': 209},
                'Vout': {'reg': 210, 'dec': 1},
                'Iout': {'reg': 211, 'dec': 1},
                'Fout': {'reg': 212, 'dec': 2},
                'Wout': {'reg': 213, 'tipo': 's16'},
                'VAout': {'reg': 214},
                'Vbat': {'reg': 215, 'dec': 1},
                'Ibat': {'reg': 216, 'dec': 1, 'tipo': 's16'},
                'Ibat1': {'reg': 232, 'dec': 1, 'tipo': 's16'},
                'Vplaca': {'reg': 219, 'dec': 1},
                'Iplaca': {'reg': 220, 'dec': 1},
                'Wplaca': {'reg': 223},
                'Wplaca_bat': {'reg': 224},
                'Carga%': {'reg': 225},
                'Temp_dc': {'reg': 226},
                'Temp_inv': {'reg': 227},
                'SOC': {'reg': 229},
                'I_carga_inv': {'reg': 233, 'dec': 1, 'tipo': 's16'},
                'I_carga_pla': {'reg': 234, 'dec': 1, 'tipo': 's16'},
                
                'Out_modo': {
                    'reg': 300,
                    'rango': [0, 4],
                    'tipo': 'adaptar',
                    'adaptar': [
                        "if d == 0: resultado = '0-Single'",
                        "elif d == 1: resultado = '1-Paralelo'",
                        "elif d == 2: resultado = '2-Fase1'",
                        "elif d == 3: resultado = '3-Fase2'",
                        "elif d == 4: resultado = '4-Fase3'"
                    ]
                },
                
                'Out_prio': {
                    'reg': 301,
                    'tipo': 'adaptar',
                    'escritura': True,
                    'rango': [0, 2],
                    'adaptar': [
                        "if d == 0: resultado = '0-Util_PV_Bat'",
                        "elif d == 1: resultado = '1-PV_Util_Bat'",
                        "elif d == 2: resultado = '2-PV_Bat_Util'"
                    ]
                },

                'Input_range': {'reg':302, 'rango':[0,1], 'escritura': True, 'parametro': 3},
                'Buzzer_mode_range': {'reg':303, 'rango':[0,2], 'escritura': True, 'parametro': 18},
                'LCD_light': {'reg':305, 'rango':[0,1], 'escritura': True, 'parametro': 20},
                'LCD_return': {'reg':306, 'rango':[0,1], 'escritura': True, 'parametro': 19},
                'Over_load_return': {'reg':308, 'rango':[0,1], 'escritura': True, 'parametro': 6},
                'Over_Temp_return': {'reg':309, 'rango':[0,1], 'escritura': True, 'parametro': 7},
                'Over_load_bypass': {'reg':310, 'rango':[0,1], 'escritura': True, 'parametro': 6},
              
                'Vbat_max'   : {'reg':323, 'dec': 1, 'rango':[55,66], 'escritura': True},
                'Vabs'       : {'reg':324, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'Vflot'      : {'reg':325, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'Voff_r_main': {'reg':326, 'dec': 1, 'rango':[40,48], 'escritura': True},
                'Voff_main'  : {'reg':327, 'dec': 1, 'rango':[40,48], 'escritura': True},
                'R328'       : {'reg':328, 'rango':[0,10000], 'escritura': True},
                'Voff'       : {'reg':329, 'dec': 1, 'rango':[40,48], 'escritura': True},
                'Tabs'       : {'reg':330, 'rango':[0,900], 'escritura': True, 'parametro': 32},
                'Prioridad_carga' : {'reg':331, 'rango':[0,3], 'escritura': True, 'parametro': 16},
                'Icarga_max'      : {'reg':332, 'dec': 1, 'rango':[2,80], 'escritura': True, 'parametro': 11},
                'Icarga_main'     : {'reg':333, 'dec': 1, 'rango':[2,30], 'escritura': True, 'parametro': 2},
                'Vequ'            : {'reg':334, 'dec': 1, 'rango':[48,62], 'escritura': True, 'parametro': 34},
                'Tequ'            : {'reg':335, 'dec': 0, 'rango':[0,900], 'escritura': True, 'parametro': 35},
                'Tequ_timeout'    : {'reg':336, 'dec': 0, 'rango':[0,900], 'escritura': True, 'parametro': 36},
                'Tequ_dias'       : {'reg':337, 'dec': 0, 'rango':[0,90], 'escritura': True, 'parametro': 37},
              
                'Modo_On_Off'     : {'reg':406, 'rango':[0,2], 'escritura': True},
                'Remote_Switch'   : {'reg':420, 'rango':[0,1], 'escritura': True},
            },
        },
        
        'ANENJI11K': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                   
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos':[[201,290],[301,391],[600,650],[702,702]]
                },
            },
            
            'REGISTROS': {
                'WM'       :  {'reg':201,         # Working Mode
                             'tipo':'adaptar',
                             'adaptar':[
                                     "if d == 0: resultado = '0-Power On'",
                                     "elif d == 1: resultado = '1-Standby'",
                                     "elif d == 2: resultado = '2-Mains'",
                                     "elif d == 3: resultado = '3-Off-Grid'",
                                     "elif d == 4: resultado = '4-Bypass'",
                                     "elif d == 5: resultado = '5-Charging'",
                                     "elif d == 6: resultado = '6-Fault'",
                                     ]
                            },

                'Fred'      : {'reg':203, 'dec':2},     # Frecuencia red AC entrada
                'Wred'      : {'reg':204},              # W de red AC.... ver  signo ??
                'Winv_bat'  : {'reg':206},              # Watios de AC entrada a bateria
                'R_207'     : {'reg':207},              # Bits flujo de potencia
              
                'Wred1_208' : {'reg':208},              #
                'Finv'      : {'reg':227, 'dec':2},     # Frecuencia Hibrido
                'W_228'     : {'reg':228},              # Potencia Activa Inversor
              
                'I_carga_inv' : {'reg':230, 'dec':1,'tipo':'s16'}, # Intensidad carga Inverter
                'Temp_inv'  : {'reg':231},                         # Watios Placas
                            
                'Iout'      : {'reg':252, 'dec':1},     # Salida Intensidad efectiva
                'Fout'      : {'reg':253, 'dec':2},     # Frecuencia Salida 
                'Wout'      : {'reg':254, 'tipo':'s16'},# W de salida total
                'VAout'     : {'reg':255},              # VA de salida
                'Carga%'    : {'reg':256},                # % Carga%
              
                'Vbat'      : {'reg':277, 'dec':1},                # Voltaje baterias
                'Ibat'      : {'reg':278, 'dec':1,'tipo':'s16'},   # Intensidad baterias
                'Wbat'      : {'reg':279, 'tipo':'s16'},           # Watios baterias....signo ??
              
                'SOC'       : {'reg':280},              # % SOC
                'Temp_dc'   : {'reg':281},              # Watios Placas
              
                'Wplaca'    : {'reg':302},              # Watios Placas
                'Wplaca_bat': {'reg':303},              # Watios Placas a baterias
                'I_carga_pla' : {'reg':304, 'dec':1},   # Intensidad carga Placas
                'Temp_PV'    : {'reg':305},             # Watios Placas
              
                'W_326'      : {'reg':326},             # 'Long ... positivo: producción energía de la red / negativo: energía vertida a la red;
              
                'W_red_L1'      : {'reg':340, 'tipo':'s16'},   # Potencia activa red L1
                
                'Vred_aff'   : {'reg':342, 'dec':1},     # Voltaje Affectivo red AC entrada
                'Ired_aff'   : {'reg':343, 'dec':1},     # Intensidad Affectiva red AC entrada
                'Winv'       : {'reg':344, 'tipo':'s16'},# W del inversor L1
              
                'Vout'       : {'reg':346, 'dec':1},     # Salida Voltaje efectivo
                'W_salida_L1': {'reg':348},              # Potencia activa salida L1
                'Carga%_L1'  : {'reg':350},              # % Carga L1
              
                'Vplaca1'    : {'reg':351, 'dec':1},     # Voltaje Placas
                'Iplaca1'    : {'reg':352, 'dec':1},     # Intensidad Placas
                'Wplaca1'    : {'reg':353},              # Watios Placas
              
                'V_red_L2'   : {'reg':376},              # Voltaje red L2
                'W_red_L2'   : {'reg':378},              # Potencia activa red L2
              
                'Winv_L2'    : {'reg':382, 'tipo':'s16'},# W promedio del inversor L2
                'W_L2'       : {'reg':386},              # W promedio potencia salida L2
                      
                'Vplaca2'    : {'reg':389, 'dec':1},     # Voltaje Placas
                'Iplaca2'    : {'reg':390, 'dec':1},     # Intensidad Placas
                'Wplaca2'    : {'reg':391},              # Watios Placas
              
                'Out_modo' :  {'reg':600,
                             'rango':[0,4],
                             'tipo':'adaptar',
                             'adaptar':[
                                     "if d == 0: resultado = '0-Single'",
                                     "elif d == 1: resultado = '1-Paralelo'",
                                     "elif d == 2: resultado = '2-Fase1'",
                                     "elif d == 3: resultado = '3-Fase2'",
                                     "elif d == 4: resultado = '4-Fase3'"
                                     ]
                            },
              
                'Out_prio' : {'reg':601,
                             'tipo':'adaptar',
                             'rango':[1,3],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: resultado = '0-???Util_PV_Bat'",
                                     "elif d == 1: resultado = '1-SUB'",
                                     "elif d == 2: resultado = '2-SBU'",
                                     "elif d == 3: resultado = '3-SUF'"                                     
                                     ]
                            },
                'Tipo_Bat' : {'reg':630,
                             'tipo':'adaptar',
                             'rango':[0,8],
                             'escritura': True,
                             'adaptar':[
                                     "if d == 0: resultado = '0-AGM'",
                                     "elif d == 1: resultado = '1-FLD'",
                                     "elif d == 2: resultado = '2-USER'",
                                     "elif d == 4: resultado = '4-Li2'",
                                     "elif d == 6: resultado = '6-Li4'",
                                     "elif d == 8: resultado = '8-LiB'"                                     
                                     ]
                            },
                'Prioridad_carga' : {'reg':632,
                                   'tipo':'adaptar',
                                   'rango':[0,4],
                                   'escritura': True,
                                   'adaptar':[
                                     "if d == 1: resultado = '1-SOF'",
                                     "elif d == 2: resultado = '2-SNU'",
                                     "elif d == 3: resultado = '3-OSO'",
                                     "elif d == 4: resultado = '4-SOR'",
                                     "elif d == 0: resultado = '0 ??'"
                                     ]
                                  },
              
                'Vabs'           : {'reg':637, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'Vflot'          : {'reg':638, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'Tabs'           : {'reg':639, 'rango':[0,900], 'escritura': True, 'parametro': 32},
                'Icarga_max'     : {'reg':640, 'dec': 1, 'rango':[2,80], 'escritura': True, 'parametro': 11},
                'Icarga_main'    : {'reg':641, 'dec': 1, 'rango':[2,30], 'escritura': True, 'parametro': 2},
              
                'R643'           : {'reg':643, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'R644'           : {'reg':644, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'R645'           : {'reg':645, 'dec': 1, 'rango':[48,62], 'escritura': True},
                'R646'           : {'reg':646, 'dec': 1, 'rango':[48,62], 'escritura': True},
              

                'R_702'    : {'reg':702},              # Generación de energía en el día Kwh

            },

        },

        'POWMR10K2': {  
            'COMANDOS': {
                'ayuda': ['h','?','i', 'info',''],
                   
                'lectura_multiple': {
                    'usar': 1,  # Lectura registro a registro
                    'rangos':[[4501,4564]]
                },
            },
            
            'REGISTROS': {
                'Sprio' : {'reg':4501}, 
                'Vac' : {'reg':4502, 'dec':1},
                'Fac' : {'reg':4503, 'dec':1},
                'Vplaca1' : {'reg':4504, 'dec':1},
                'Wplaca1' : {'reg':4505},
                'Vbat' : {'reg':4506, 'dec':1}, 
                'SOC' : {'reg':4507},
                'Icarga' : {'reg':4508}, 
                'Idescarga' : {'reg':4509}, 
                'Vac_out' : {'reg':4510, 'dec':1}, 
                'Fac_out' : {'reg':4511, 'dec':1}, 
                'Wconsumo' : {'reg':4512},
                'Wconsumo_VA' : {'reg':4513},
                'Wconsumo_%' : {'reg':4514},
                'Wconsumo_%2' : {'reg':4515},
                'Flags_4516' : {'reg':4516},
              
                '4517' : {'reg':4517},
                '4518' : {'reg':4518},
                '4519' : {'reg':4519},
                '4520' : {'reg':4520},
                '4521' : {'reg':4521},
                '4522' : {'reg':4522},
                '4523' : {'reg':4523},
                '4524' : {'reg':4524},
                '4525' : {'reg':4525},
                '4526' : {'reg':4526},
                '4527' : {'reg':4527},
                '4528' : {'reg':4528},
                '4529' : {'reg':4529},
              
                'Error_code' : {'reg':4530},
              
                '4531' : {'reg':4531},
                '4532' : {'reg':4532},
                '4533' : {'reg':4533},
                '4534' : {'reg':4534},
              
                'Flags_4535' : {'reg':4535},
              
                'Carga_prio' : {'reg':4536},
                'Source_prio' : {'reg':4537},
                'Vac_input_target' : {'reg':4538},
              
                '4539' : {'reg':4539},
              
                'Fac_out_target' : {'reg':4538},
              
                '4541' : {'reg':4541},
                '4542' : {'reg':4542},
              
                'Carga_max_util' : {'reg':4543},
                'Vbat_back_utility' : {'reg':4544, 'dec':1},
                'Vbat_back_bateria' : {'reg':4545, 'dec':1},
              
                'Vabs' : {'reg':4546, 'dec':1, 'rango':[48,64], 'escritura': True},
                'Vflot' : {'reg':4547, 'dec':1},
                'Vbat_cutoff' : {'reg':4548, 'dec':1},
                'Vequ' : {'reg':4549, 'dec':1},
                'Vequ_time' : {'reg':4550},
                'Vequ_timeout' : {'reg':4551},
                'Vequ_intervalo' : {'reg':4552},
              
                'Flags_4553' : {'reg':4553},
                'Flags_4554' : {'reg':4554},
                'Carga_estado' : {'reg':4555},
              
                '4556' : {'reg':4556},
                'Temp_placas' : {'reg':4557},
              
                'Wplaca_?' : {'reg':4558 },
              
                '4559' : {'reg':4559},
                '4560' : {'reg':4560},
                '4561' : {'reg':4561},
                '4562' : {'reg':4562},
              
                'Vplaca2' : {'reg':4563, 'dec':1},
                'Wplaca2' : {'reg':4564, },
                
            },

        },


    },   
}

# ########### FIN PARAMETRIZACION EQUIPO ####################
  


# #################### Control Ejecucion Servicio ########################################
NEQUIPO = 'RS232_WIFI'
servicio = 'fv_rs232_wifi'
control = f"sum([{NEQUIPO}[b]['usar'] for b in {NEQUIPO} if b != 'MODELOS_EQUIPOS'])"

exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
# ########################################################################################


import asyncio
import socket
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import traceback
import MySQLdb
import os
import sys
import paho.mqtt.client as mqtt
import telebot
import re

"""
# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Parametros Instalacion FV
basepath = '/home/pi/PVControl+/'
parametros_FV = basepath + "Parametros_FV.py"
parametros_FV_DIST = basepath + "Parametros_FV_DIST.py"

exec(open(parametros_FV_DIST).read(),globals())   #carga Parametros_FV_DIST.py por si hay variables no definidas en Parametros_FV.py
exec(open(parametros_FV).read(),globals())        #carga Parametros_FV.py  .... Valores especificos de cada instalacion
"""


CONFIG_BD = {
    'host': servidor,
    'user': usuario, 
    'password': clave,
    'database': basedatos,
    'charset': 'utf8mb4'
}

# Configuración Telegram
USAR_TELEGRAM = usar_telegram
TOKEN_TELEGRAM = TOKEN

CHAT_IDS = [Aut[0]]  # Array para múltiples chats

# Configuración MQTT
BROKER_MQTT = mqtt_broker
PUERTO_MQTT = mqtt_puerto
USUARIO_MQTT = mqtt_usuario
CLAVE_MQTT = mqtt_clave

TOPIC_BASE = "PVControl"


# =============================================================================
# CÓDIGOS DE COLOR PARA CONSOLA
# =============================================================================

class Colores:
    RESET = '\033[0m'
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'

# =============================================================================
# CONFIGURACIÓN GLOBAL DEBUG
# =============================================================================

MODO_DEBUG = '-p' in sys.argv

def imprimir_debug(mensaje: str):
    if MODO_DEBUG:
        print(mensaje)

# =============================================================================
# MANEJO DE TELEGRAM
# =============================================================================

class ManejadorTelegram:
    def __init__(self, token: str, chat_ids: List[str]):
        self.token = token
        self.chat_ids = chat_ids
        self.bot = None
        self.inicializar_bot()
    
    def inicializar_bot(self):
        """Inicializa el bot de Telegram"""
        try:
            self.bot = telebot.TeleBot(self.token)
            self.bot.skip_pending = True
            print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- TELEGRAM: Bot inicializado{Colores.RESET}")
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- TELEGRAM: Error inicializando bot: {e}{Colores.RESET}")
            self.bot = None
    
    def enviar_mensaje(self, mensaje: str, formato_html: bool = True):
        """Envía mensaje a todos los chats configurados"""
        if not self.bot:
            return False
        
        try:
            for chat_id in self.chat_ids:
                if formato_html:
                    self.bot.send_message(chat_id, mensaje, parse_mode="HTML")
                else:
                    self.bot.send_message(chat_id, mensaje)
            return True
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- TELEGRAM: Error enviando mensaje: {e}{Colores.RESET}")
            return False

# =============================================================================
# MANEJO DE MQTT
# =============================================================================

class ManejadorMQTT:
    def __init__(self, broker: str, port: int, topic_base: str, lector_anenji):
        self.broker = broker
        self.port = port
        self.topic_base = topic_base
        self.lector = lector_anenji
        self.cliente = None
        self.comando_pendiente = None
        self.inicializar_cliente()

    def inicializar_cliente(self):
        """Inicializa el cliente MQTT con autenticación"""
        try:
            self.cliente = mqtt.Client()
            
            # Configurar autenticación si hay usuario y clave
            if USUARIO_MQTT and CLAVE_MQTT:
                self.cliente.username_pw_set(USUARIO_MQTT, CLAVE_MQTT)
                imprimir_debug(f"{Colores.CYAN}MQTT: Configurada autenticación con usuario '{USUARIO_MQTT}'{Colores.RESET}")
            
            self.cliente.on_connect = self._on_connect
            self.cliente.on_message = self._on_message
            self.cliente.on_disconnect = self._on_disconnect
            
            self.cliente.connect(self.broker, self.port, 60)
            self.cliente.loop_start()
            print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Cliente inicializado con autenticación{Colores.RESET}")
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Error inicializando cliente: {e}{Colores.RESET}")
            self.cliente = None
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback cuando se conecta al broker MQTT"""
        if rc == 0:
            print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Conectado al broker con autenticación{Colores.RESET}")
            
            # Suscribirse a los topics de todos los equipos activos
            for nombre_equipo, config_equipo in self.lector.config_equipos.items():
                if config_equipo.get('usar', 0):
                    topic = f"{self.topic_base}/{nombre_equipo}"
                    client.subscribe(topic)
                    print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Suscrito a {topic}{Colores.RESET}")
        else:
            # Códigos de error de conexión MQTT
            errores = {
                1: "Protocolo incorrecto",
                2: "Cliente ID inválido", 
                3: "Servidor no disponible",
                4: "Usuario o contraseña incorrectos",
                5: "No autorizado"
            }
            mensaje_error = errores.get(rc, f"Código desconocido: {rc}")
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Error de conexión: {mensaje_error}{Colores.RESET}")
    
    def _on_message(self, client, userdata, msg):
        """Callback cuando llega un mensaje MQTT"""
        try:
            topic = msg.topic
            mensaje = msg.payload.decode().strip()
            
            imprimir_debug(f"{Colores.CYAN}MQTT: Comando '{mensaje}' recibido en topic '{topic}'{Colores.RESET}")
            
            # Extraer nombre del equipo del topic
            nombre_equipo = topic.split('/')[-1].upper()
            
            # Guardar comando para procesar en el bucle principal
            self.comando_pendiente = {
                'equipo': nombre_equipo,
                'comando': mensaje,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Error procesando mensaje: {e}{Colores.RESET}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback cuando se desconecta del broker MQTT"""
        if rc != 0:
            print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Desconectado inesperadamente (código {rc}), reconectando...{Colores.RESET}")
            
            # Intentar reconectar con autenticación
            try:
                if USUARIO_MQTT and CLAVE_MQTT:
                    client.username_pw_set(USUARIO_MQTT, CLAVE_MQTT)
                client.reconnect()
            except Exception as e:
                print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Error en reconexión: {e}{Colores.RESET}")
        else:
            print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- MQTT: Desconectado{Colores.RESET}")

    def obtener_comando_pendiente(self):
        """Obtiene y limpia el comando pendiente"""
        comando = self.comando_pendiente
        self.comando_pendiente = None
        return comando

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def obtener_ip_local():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_local = s.getsockname()[0]
            return ip_local
    except Exception:
        print('No se detecta la IP local de la Raspberry')
        sys.exit(1)
    return "192.168.1.10"

def descubrir_dongles():
    print(f"{Colores.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- ESCANEO: Buscando dongles en la red...{Colores.RESET}")
    
    mensajes_descubrimiento = ["set>server="]
    
    dongles_descubiertos = []
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)
        
        for mensaje in mensajes_descubrimiento:
            imprimir_debug(f"{Colores.CYAN}Probando mensaje: {mensaje}{Colores.RESET}")
            try:
                sock.sendto(mensaje.encode(), ('255.255.255.255', 58899))
                tiempo_inicio = time.time()
                while time.time() - tiempo_inicio < 2:
                    try:
                        datos, direccion = sock.recvfrom(1024)
                        if direccion[0] not in [d['ip'] for d in dongles_descubiertos]:
                            dongles_descubiertos.append({
                                'ip': direccion[0],
                                'respuesta': datos.decode(errors='ignore'),
                                'mensaje': mensaje
                            })
                            print(f"{Colores.VERDE}✓ Dongle encontrado en {direccion[0]}{Colores.RESET}")
                    except socket.timeout:
                        continue
            except Exception as e:
                imprimir_debug(f"{Colores.AMARILLO}Error con mensaje {mensaje}: {str(e)}{Colores.RESET}")
    
    if not dongles_descubiertos:
        print(f"{Colores.AMARILLO}No se encontraron dongles en la red{Colores.RESET}")
    else:
        print(f"{Colores.VERDE}Se encontraron {len(dongles_descubiertos)} dongle(s){Colores.RESET}")
    
    return dongles_descubiertos

def obtener_color_equipo(nombre_equipo: str) -> str:
    numeros = [c for c in nombre_equipo if c.isdigit()]
    if numeros:
        ultimo_digito = int(numeros[-1])
        mapa_colores = {0: Colores.BLANCO, 1: Colores.VERDE, 2: Colores.AZUL, 3: Colores.AMARILLO,
                        4: Colores.MAGENTA, 5: Colores.CYAN, 6: Colores.ROJO, 7: Colores.VERDE,
                        8: Colores.AZUL, 9: Colores.MAGENTA}
        return mapa_colores.get(ultimo_digito, Colores.BLANCO)
    return Colores.BLANCO

# =============================================================================
# FUNCIONES DE COMUNICACIÓN MODBUS
# =============================================================================

def calcular_crc16_modbus(datos: bytes) -> int:
    crc = 0xFFFF
    for byte in datos:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def crear_peticion_modbus(id_transaccion: int, id_unidad: int, codigo_funcion: int, 
                        direccion_inicio: int, cantidad: int) -> bytes:
    trama_rtu = bytearray([
        id_unidad, codigo_funcion,
        (direccion_inicio >> 8) & 0xFF, direccion_inicio & 0xFF,
        (cantidad >> 8) & 0xFF, cantidad & 0xFF
    ])
    
    crc = calcular_crc16_modbus(trama_rtu)
    trama_rtu.extend([crc & 0xFF, (crc >> 8) & 0xFF])
    
    carga_util = bytearray([0xFF, 0x04]) + trama_rtu
    longitud = len(carga_util)
    
    comando = bytearray([
        (id_transaccion >> 8) & 0xFF, id_transaccion & 0xFF,
        0x00, 0x00,
        (longitud >> 8) & 0xFF, longitud & 0xFF
    ]) + carga_util

    return comando

def crear_escritura_registro(id_transaccion: int, id_unidad: int, direccion: int, valor: int) -> bytes:
    """Crea petición Modbus para escribir un registro usando función 16 (como minimalmodbus)"""
    # Para función 16: Write Multiple Registers
    # Aunque sea un solo registro, minimalmodbus usa función 16
    
    # 1. Construir trama Modbus-RTU para función 16
    trama_rtu = bytearray([
        id_unidad, 0x10,  # Función 16: Write Multiple Registers
        (direccion >> 8) & 0xFF, direccion & 0xFF,  # Address
        0x00, 0x01,  # Quantity: 1 registro
        0x02,  # Byte count: 2 bytes (1 registro × 2 bytes)
        (valor >> 8) & 0xFF, valor & 0xFF  # Value
    ])
    
    imprimir_debug(f"  DEBUG: Trama RTU función 16: {bytes_a_hex(trama_rtu)}")
    
    # 2. Calcular CRC Modbus
    crc = calcular_crc16_modbus(trama_rtu)
    trama_rtu.extend([crc & 0xFF, (crc >> 8) & 0xFF])
    
    imprimir_debug(f"  DEBUG: Trama RTU con CRC: {bytes_a_hex(trama_rtu)}")
    
    # 3. Añadir cabecera propietaria FF04
    carga_util = bytearray([0xFF, 0x04]) + trama_rtu
    longitud = len(carga_util)
    
    # 4. Encapsular en TCP Modbus
    trama_final = bytearray([
        (id_transaccion >> 8) & 0xFF, id_transaccion & 0xFF,
        0x00, 0x00,  # Protocol ID
        (longitud >> 8) & 0xFF, longitud & 0xFF
    ]) + carga_util

    imprimir_debug(f"  DEBUG: Trama final función 16: {bytes_a_hex(trama_final)}")
    imprimir_debug(f"  DEBUG: Escritura - Dirección: {direccion}, Valor: {valor}")

    return trama_final
    
def bytes_a_hex(datos: bytes) -> str:
    return ' '.join(f'{b:02x}' for b in datos)

def decodificar_respuesta_modbus(respuesta: bytes, cantidad_esperada: int) -> Optional[List[int]]:
    imprimir_debug(f"  DEBUG: Respuesta completa ({len(respuesta)} bytes): {bytes_a_hex(respuesta)}")
    
    if len(respuesta) < 8:
        imprimir_debug(f"  DEBUG: Respuesta demasiado corta")
        return None
        
    id_unidad = respuesta[8] if len(respuesta) > 8 else 0
    codigo_funcion = respuesta[9] if len(respuesta) > 9 else 0
    
    imprimir_debug(f"  DEBUG: ID Unidad: {id_unidad:02x}, Código Función: {codigo_funcion:02x}")
    
    # Verificar error
    if codigo_funcion & 0x80:
        codigo_error = respuesta[10] if len(respuesta) > 10 else 0
        imprimir_debug(f"  DEBUG: Error Modbus - Código: {codigo_error:02x}")
        return None
    
    # Para escritura función 16
    if codigo_funcion == 0x10:
        imprimir_debug(f"  DEBUG: Respuesta escritura función 16")
        # La respuesta de función 16 es: dirección + cantidad
        if len(respuesta) >= 13:
            dir_respuesta = int.from_bytes(respuesta[11:13], 'big')
            cant_respuesta = int.from_bytes(respuesta[13:15], 'big')
            imprimir_debug(f"  DEBUG: Escritura confirmada - Dirección: {dir_respuesta}, Cantidad: {cant_respuesta}")
            return [cant_respuesta]  # Retornar la cantidad escrita
        else:
            imprimir_debug(f"  DEBUG: Respuesta escritura mínima - considerando éxito")
            return [1]
    
    # Para escritura función 6 (por si acaso)
    elif codigo_funcion == 0x06:
        imprimir_debug(f"  DEBUG: Respuesta escritura función 6")
        if len(respuesta) >= 15:
            dir_respuesta = int.from_bytes(respuesta[11:13], 'big')
            valor_respuesta = int.from_bytes(respuesta[13:15], 'big')
            imprimir_debug(f"  DEBUG: Escritura función 6 - Dirección: {dir_respuesta}, Valor: {valor_respuesta}")
            return [valor_respuesta]
        else:
            imprimir_debug(f"  DEBUG: Respuesta función 6 mínima")
            return [1]
    
    # Para lectura función 3
    elif codigo_funcion == 0x03:
        if len(respuesta) < 11:
            return None
            
        contador_bytes = respuesta[10]
        imprimir_debug(f"  DEBUG: Byte count: {contador_bytes}")
        
        if len(respuesta) < 11 + contador_bytes:
            imprimir_debug(f"  DEBUG: Respuesta incompleta")
            return None
            
        bytes_datos = respuesta[11:11 + contador_bytes]
        valores = []
        
        for i in range(0, contador_bytes, 2):
            if i + 1 < len(bytes_datos):
                valor = int.from_bytes(bytes_datos[i:i+2], 'big')
                valores.append(valor)
        
        imprimir_debug(f"  DEBUG: Leídos {len(valores)} registros")
        return valores[:cantidad_esperada]
    
    imprimir_debug(f"  DEBUG: Función no manejada: {codigo_funcion:02x}")
    return None
    
# =============================================================================
# CLASE PARA GESTIÓN DE CONEXIÓN TCP PERSISTENTE
# =============================================================================

class ManejadorConexionesTCP:
    def __init__(self, ip_local: str, puerto_local: int = 8899):
        self.ip_local = ip_local
        self.puerto_local = puerto_local
        self.conexiones: Dict[str, socket.socket] = {}
        self.candado = asyncio.Lock()
    
    async def obtener_conexion(self, ip_dongle: str) -> Optional[socket.socket]:
        async with self.candado:
            if ip_dongle in self.conexiones:
                try:
                    self.conexiones[ip_dongle].getpeername()
                    imprimir_debug(f"  DEBUG: Reutilizando conexión existente con {ip_dongle}")
                    return self.conexiones[ip_dongle]
                except:
                    imprimir_debug(f"  DEBUG: Conexión con {ip_dongle} cerrada, creando nueva")
                    del self.conexiones[ip_dongle]
            
            imprimir_debug(f"  DEBUG: Creando nueva conexión con {ip_dongle}")
            return await self._crear_conexion(ip_dongle)
    
    async def _crear_conexion(self, ip_dongle: str) -> Optional[socket.socket]:
        try:
            socket_config = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mensaje_config = f"set>server={self.ip_local}:{self.puerto_local};"
            socket_config.sendto(mensaje_config.encode(), (ip_dongle, 58899))
            socket_config.close()
            imprimir_debug(f"  DEBUG: Configuración enviada a {ip_dongle}: {mensaje_config}")
            
            socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_servidor.setblocking(False)
            socket_servidor.bind((self.ip_local, self.puerto_local))
            socket_servidor.listen(1)
            
            bucle = asyncio.get_event_loop()
            imprimir_debug(f"  DEBUG: Esperando conexión de {ip_dongle}...")
            socket_cliente, direccion_cliente = await asyncio.wait_for(
                bucle.sock_accept(socket_servidor),
                timeout=10.0
            )
            imprimir_debug(f"  DEBUG: Dongle {ip_dongle} conectado desde {direccion_cliente}")
            socket_cliente.setblocking(False)
            
            self.conexiones[ip_dongle] = socket_cliente
            socket_servidor.close()
            
            return socket_cliente
            
        except asyncio.TimeoutError:
            imprimir_debug(f"  DEBUG: Timeout esperando conexión de {ip_dongle}")
            return None
        except Exception as e:
            imprimir_debug(f"  DEBUG: Error creando conexión con {ip_dongle}: {e}")
            return None
    
    async def cerrar_conexion(self, ip_dongle: str):
        async with self.candado:
            if ip_dongle in self.conexiones:
                try:
                    self.conexiones[ip_dongle].close()
                except:
                    pass
                del self.conexiones[ip_dongle]
                imprimir_debug(f"  DEBUG: Conexión con {ip_dongle} cerrada")
    
    async def cerrar_todas_conexiones(self):
        async with self.candado:
            for ip_dongle in list(self.conexiones.keys()):
                await self.cerrar_conexion(ip_dongle)

# =============================================================================
# FUNCIONES DE PROCESAMIENTO
# =============================================================================

def obtener_configuraciones_registros(config_modelo: Dict) -> Dict[str, Dict]:
    """Extrae las configuraciones de registros de la configuración del modelo completo"""
    configuraciones_registros = {}
    
    imprimir_debug(f"DEBUG: Obteniendo configuraciones de registros de modelo: {list(config_modelo.keys())}")
    
    # Buscar en la sección REGISTROS que está al mismo nivel que COMANDOS
    if 'REGISTROS' in config_modelo:
        registros = config_modelo['REGISTROS']
        imprimir_debug(f"DEBUG: Encontrada sección REGISTROS con {len(registros)} elementos")
        
        for nombre_reg, config in registros.items():
            if isinstance(config, dict) and 'reg' in config:
                configuraciones_registros[nombre_reg] = config
                imprimir_debug(f"DEBUG: Añadido registro: {nombre_reg} -> reg:{config['reg']}")
            else:
                imprimir_debug(f"DEBUG: Ignorado {nombre_reg}: no es dict o no tiene 'reg'")
    
    imprimir_debug(f"DEBUG: Total registros encontrados: {len(configuraciones_registros)}")
    return configuraciones_registros
    
def procesar_valor_registro(nombre_reg: str, valor_crudo: int, config_reg: Dict) -> Any:
    try:
        imprimir_debug(f"DEBUG: Procesando {nombre_reg}: valor_crudo={valor_crudo}, config={config_reg}")
        
        resultado = valor_crudo
        
        if config_reg.get('tipo') == 's16':
            if resultado >= 32768:
                resultado -= 65536
            imprimir_debug(f"DEBUG: Aplicado s16: {valor_crudo} -> {resultado}")
                
        elif config_reg.get('tipo') == 'adaptar':
            d = valor_crudo
            resultado_adaptado = None
            bloque_codigo = '\n'.join(config_reg['adaptar'])
            imprimir_debug(f"DEBUG: Ejecutando adaptar para {nombre_reg}: d={d}")
            variables_locales = {'d': d, 'resultado': resultado_adaptado}
            exec(bloque_codigo, {}, variables_locales)
            if variables_locales.get('resultado') is not None:
                resultado = variables_locales['resultado']
                imprimir_debug(f"DEBUG: Adaptado: {valor_crudo} -> {resultado}")
            else:
                resultado = d
                imprimir_debug(f"DEBUG: No se adaptó, usando valor crudo: {d}")
                
        if 'dec' in config_reg and config_reg.get('tipo') != 'adaptar':
            resultado = resultado / (10 ** config_reg['dec'])
            imprimir_debug(f"DEBUG: Aplicado decimal {config_reg['dec']}: {valor_crudo} -> {resultado}")
            
        if 'offset' in config_reg:
            resultado += config_reg['offset']
            imprimir_debug(f"DEBUG: Aplicado offset {config_reg['offset']}: {valor_crudo} -> {resultado}")
            
        imprimir_debug(f"DEBUG: Resultado final {nombre_reg}: {resultado}")
        return resultado
        
    except Exception as e:
        imprimir_debug(f"DEBUG: Error procesando {nombre_reg}: {e}")
        return valor_crudo

def crear_grupos_registros(rangos_multiples: List) -> List[tuple]:
    if not rangos_multiples:
        return []
    
    grupos = []
    for inicio, fin in rangos_multiples:
        cantidad = fin - inicio + 1
        grupos.append((inicio, cantidad, f"Registros {inicio}-{fin}"))
    
    return grupos

def extraer_registros_individuales(datos_grupo: Dict, direccion_inicio: int, valores: List[int], 
                          configuraciones_registros: Dict) -> Dict:
    imprimir_debug(f"DEBUG: Extraiendo registros desde dirección {direccion_inicio}, {len(valores)} valores")
    
    for i, valor in enumerate(valores):
        dir_registro = direccion_inicio + i
        registro_encontrado = False
        
        for nombre_reg, config in configuraciones_registros.items():
            if config.get('reg') == dir_registro:
                valor_procesado = procesar_valor_registro(nombre_reg, valor, config)
                datos_grupo[nombre_reg] = valor_procesado
                registro_encontrado = True
                imprimir_debug(f"DEBUG: Registro {dir_registro} -> {nombre_reg} = {valor} -> {valor_procesado}")
                break
        
        if not registro_encontrado:
            imprimir_debug(f"DEBUG: Registro {dir_registro} no encontrado en configuración")
    
    imprimir_debug(f"DEBUG: Total registros extraídos: {len(datos_grupo)}")
    return datos_grupo

# =============================================================================
# BASE DE DATOS
# =============================================================================

class ManejadorBaseDatos:
    def __init__(self, config: Dict):
        self.config = config
        self.conexion = None
        self.conectar()
    
    def conectar(self):
        try:
            self.conexion = MySQLdb.connect(**self.config)
            print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Conexión BD OK{Colores.RESET}")
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Error BD: {e}{Colores.RESET}")
            self.conexion = None
    
    def guardar_datos_equipo(self, id_equipo: str, sensores: Dict[str, Any]) -> bool:
        if not self.conexion:
            return False
        
        try:
            cursor = self.conexion.cursor()
            sensores_json = json.dumps(sensores, ensure_ascii=False)
            consulta = """
            INSERT INTO equipos (id_equipo, tiempo, sensores) 
            VALUES (%s, NOW(), %s)
            ON DUPLICATE KEY UPDATE 
                tiempo = NOW(), 
                sensores = %s
            """
            cursor.execute(consulta, (id_equipo, sensores_json, sensores_json))
            self.conexion.commit()
            return True
        except Exception as e:
            try:
                self.conectar()
            except:
                pass
            return False

# =============================================================================
# CLASE PRINCIPAL CON MQTT Y TELEGRAM - MODIFICADA PARA MÚLTIPLES MODELOS
# =============================================================================

class LectorRS232Wifi:
    def __init__(self, config: Dict):
        self.ip_local = obtener_ip_local()
        self.puerto_local = 8899
        
        self.manejador_conexiones = ManejadorConexionesTCP(self.ip_local, self.puerto_local)
        self.config_completa = config
        
        # Separar equipos y modelos
        self.config_equipos = {}
        self.modelos_equipos = {}
        
        for clave, valor in config.items():
            if clave == 'MODELOS_EQUIPOS':
                self.modelos_equipos = valor
            elif isinstance(valor, dict) and 'IP' in valor:
                self.config_equipos[clave] = valor
        
        # Configuración actual por equipo (se actualiza dinámicamente)
        self.configuraciones_actuales = {}
        self.configuraciones_registros_actuales = {}
        
        self.ultimos_tiempos_lectura = {}
        self.contadores_errores = {}
        self.fallos_diarios = {}
        self.ultimo_reinicio_diario = datetime.now().date()
        self.max_errores_antes_reinicio = 5
        self.bd = ManejadorBaseDatos(CONFIG_BD)
        
        # Inicializar Telegram
        self.telegram = ManejadorTelegram(TOKEN_TELEGRAM, CHAT_IDS) if USAR_TELEGRAM else None
        
        # Inicializar MQTT
        self.mqtt = ManejadorMQTT(BROKER_MQTT, PUERTO_MQTT, TOPIC_BASE, self)
        
        # Escanear dongles
        self.dongles_descubiertos = descubrir_dongles()

        # Asignar IPs automáticamente si es necesario
        self._asignar_ips_automaticamente()
        
        # Verificar configuración
        self._verificar_configuracion_ips()

  
        if not self._tiene_equipos_activos():
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: No hay equipos activos. Finalizando script.{Colores.RESET}")
            sys.exit(1)
        
        self._asignar_colores_equipos()
        self._inicializar_temporizadores()
        self._mostrar_configuracion_inicial()
        
        # Enviar mensaje de inicio por Telegram
        if self.telegram:
            mensaje_inicio = self._crear_mensaje_inicio()
            self.telegram.enviar_mensaje(mensaje_inicio)

    def _asignar_ips_automaticamente(self):
        """Asigna automáticamente las IPs de los dongles detectados a los equipos activos sin IP"""
        equipos_sin_ip = []
        equipos_activos = []
        
        # Identificar equipos activos y equipos sin IP
        for nombre_equipo, config_equipo in self.config_equipos.items():
            if config_equipo.get('usar', 0):
                equipos_activos.append(nombre_equipo)
                ip_actual = config_equipo.get('IP', '')
                if not ip_actual or ip_actual.strip() == '':
                    equipos_sin_ip.append(nombre_equipo)
        
        if not equipos_sin_ip or not self.dongles_descubiertos:
            return
        
        print(f"{Colores.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Asignando IPs automáticamente...{Colores.RESET}")
        print(f"{Colores.CYAN}Equipos activos sin IP: {equipos_sin_ip}{Colores.RESET}")
        print(f"{Colores.CYAN}Dongles detectados: {[d['ip'] for d in self.dongles_descubiertos]}{Colores.RESET}")
        
        # Filtrar dongles disponibles (que no estén asignados a ningún equipo activo)
        ips_equipos_activos = {config['IP'] for nombre, config in self.config_equipos.items() 
                              if config.get('usar', 0) and config.get('IP')}
        
        dongles_disponibles = [
            dongle for dongle in self.dongles_descubiertos 
            if dongle['ip'] not in ips_equipos_activos
        ]
        
        print(f"{Colores.CYAN}Dongles disponibles: {[d['ip'] for d in dongles_disponibles]}{Colores.RESET}")
        
        if not dongles_disponibles:
            print(f"{Colores.AMARILLO}No hay dongles disponibles para asignar{Colores.RESET}")
            return
        
        # Ordenar equipos alfabéticamente para asignación consistente
        equipos_sin_ip.sort()
        
        # Asignar dongles a equipos
        for i, nombre_equipo in enumerate(equipos_sin_ip):
            if i < len(dongles_disponibles):
                ip_asignada = dongles_disponibles[i]['ip']
                self.config_equipos[nombre_equipo]['IP'] = ip_asignada
                print(f"{Colores.VERDE}Asignado {nombre_equipo} → {ip_asignada}{Colores.RESET}")
            else:
                print(f"{Colores.AMARILLO}No hay dongles suficientes para {nombre_equipo}{Colores.RESET}")
        
        # Actualizar mensaje de Telegram si hay cambios
        if self.telegram and equipos_sin_ip and len(equipos_sin_ip) <= len(dongles_disponibles):
            mensaje = "🔧 <b>Asignación automática de IPs completada:</b>\n"
            for nombre_equipo in equipos_sin_ip:
                if nombre_equipo in self.config_equipos:
                    ip_asignada = self.config_equipos[nombre_equipo].get('IP', 'No asignada')
                    mensaje += f"  • {nombre_equipo} → {ip_asignada}\n"
            self.telegram.enviar_mensaje(mensaje)

    def _verificar_configuracion_ips(self):
        """Verifica la configuración de IPs y muestra advertencias"""
        problemas = []
        
        for nombre_equipo, config_equipo in self.config_equipos.items():
            if config_equipo.get('usar', 0):
                ip = config_equipo.get('IP', '')
                
                if not ip or ip.strip() == '':
                    problemas.append(f"{nombre_equipo}: Sin IP configurada")
                elif ip not in [d['ip'] for d in self.dongles_descubiertos]:
                    problemas.append(f"{nombre_equipo}: IP {ip} no coincide con dongles detectados")
        
        if problemas:
            mensaje = "⚠️ <b>Problemas de configuración detectados:</b>\n" + "\n".join(problemas)
            print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- CONFIG: {mensaje}{Colores.RESET}")
            if self.telegram:
                self.telegram.enviar_mensaje(mensaje)



    def _crear_mensaje_inicio(self) -> str:
        """Crea un mensaje de inicio compacto para Telegram"""
        mensaje = "🚀 <b>Arrancando Programa fv_rs232_wifi.py</b>\n"
        mensaje += f"📡 <b>IP Raspberry:</b> {self.ip_local}\n\n"
        mensaje += "<b>Equipos configurados:</b>\n"
        
        equipos_activos = 0
        for nombre_equipo, config_equipo in self.config_equipos.items():
            usar = config_equipo.get('usar', 0)
            modelo = config_equipo.get('modelo', 'Desconocido')
            ip = config_equipo.get('IP', 'No configurada')
            
            emoji_estado = "🟢" if usar else "🔴"
            estado = "ACTIVO" if usar else "INACTIVO"
            
            mensaje += f"{emoji_estado} <b>{nombre_equipo}</b> - {estado}\n"
            mensaje += f"   📟 {modelo} | 🌐 {ip}\n"
            
            if usar:
                equipos_activos += 1
        
        mensaje += f"\n<b>Resumen:</b> {equipos_activos}/{len(self.config_equipos)} equipos activos\n"
        
        # Estado servicios
        servicios = []
        if self.bd.conexion: servicios.append("📊 BD")
        if self.telegram: servicios.append("🤖 Telegram")
        if self.mqtt and self.mqtt.cliente: servicios.append("📡 MQTT")
        
        if servicios:
            mensaje += f"<b>Servicios:</b> {' | '.join(servicios)} 🟢\n"
        
        # Dongles encontrados - NUEVA SECCIÓN
        if self.dongles_descubiertos:
            mensaje += f"\n<b>🔍 Dongles WiFi encontrados:</b>\n"
            for i, dongle in enumerate(self.dongles_descubiertos, 1):
                ip_dongle = dongle.get('ip', 'Desconocida')
                respuesta = dongle.get('respuesta', 'Sin respuesta')
                # Acortar la respuesta si es muy larga
                if len(respuesta) > 30:
                    respuesta = respuesta[:30] + "..."
                
                mensaje += f"  {i}. 🌐 {ip_dongle}\n"
                mensaje += f"     📟 Respuesta: {respuesta}\n"
        else:
            mensaje += f"\n<b>🔍 Dongles WiFi:</b> ❌ No se encontraron dongles\n"
        
        return mensaje
    
    def _contar_equipos_activos(self) -> int:
        return sum(1 for nombre, config in self.config_equipos.items() 
                  if config.get('usar', 0))
    
    def _tiene_equipos_activos(self) -> bool:
        cantidad_activos = self._contar_equipos_activos()
        print(f"{Colores.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Equipos activos: {cantidad_activos}{Colores.RESET}")
        return cantidad_activos > 0
    
    def _asignar_colores_equipos(self):
        for nombre_equipo in self.config_equipos:
            self.config_equipos[nombre_equipo]['color'] = obtener_color_equipo(nombre_equipo)
    
    def _mostrar_configuracion_inicial(self):
        print(f"{Colores.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Iniciando captura{Colores.RESET}")
        print(f"{Colores.CYAN}IP local: {self.ip_local}, Puerto: {self.puerto_local}{Colores.RESET}")
        print(f"{Colores.CYAN}Modelos disponibles: {list(self.modelos_equipos.keys())}{Colores.RESET}")
        print(f"{Colores.CYAN}Modo debug: {'ACTIVADO' if MODO_DEBUG else 'DESACTIVADO'}{Colores.RESET}")
        print(f"{Colores.CYAN}Telegram: {'ACTIVADO' if USAR_TELEGRAM else 'DESACTIVADO'}{Colores.RESET}")
        print(f"{Colores.CYAN}MQTT: ACTIVADO (con autenticación){Colores.RESET}")
        print(f"{Colores.CYAN}Base de datos: {'CONECTADA' if self.bd.conexion else 'ERROR'}{Colores.RESET}")
        
        print(f"\n{Colores.CYAN}=== EQUIPOS CONFIGURADOS ==={Colores.RESET}")
        for nombre_equipo, config_equipo in self.config_equipos.items():
            if config_equipo.get('usar', 0):
                color = config_equipo.get('color', Colores.BLANCO)
                modelo = config_equipo.get('modelo', 'Desconocido')
                estado = f"{Colores.VERDE}ACTIVO{Colores.RESET}"
            else:
                color = Colores.AMARILLO
                modelo = config_equipo.get('modelo', 'Desconocido')
                estado = f"{Colores.ROJO}INACTIVO{Colores.RESET}"
            
            print(f"{color}  {nombre_equipo} - {estado}")
            print(f"    Modelo: {modelo} | IP: {config_equipo['IP']} | Tiempo: {config_equipo['tiempo_captura']}s{Colores.RESET}")
        
        equipos_activos = self._contar_equipos_activos()
        print(f"\n{Colores.CYAN}=== RESUMEN ==={Colores.RESET}")
        print(f"{Colores.CYAN}  Total equipos: {len(self.config_equipos)}{Colores.RESET}")
        print(f"{Colores.CYAN}  Equipos activos: {equipos_activos}{Colores.RESET}")
        print(f"{Colores.CYAN}  Equipos inactivos: {len(self.config_equipos) - equipos_activos}{Colores.RESET}")
        
        # Dongles encontrados - NUEVA SECCIÓN EN CONSOLA
        print(f"\n{Colores.CYAN}=== DONGLES WIFI ENCONTRADOS ==={Colores.RESET}")
        if self.dongles_descubiertos:
            for i, dongle in enumerate(self.dongles_descubiertos, 1):
                ip_dongle = dongle.get('ip', 'Desconocida')
                respuesta = dongle.get('respuesta', 'Sin respuesta')
                mensaje = dongle.get('mensaje', 'Desconocido')
                
                print(f"{Colores.VERDE}  {i}. IP: {ip_dongle}{Colores.RESET}")
                print(f"     Mensaje: {mensaje}")
                print(f"     Respuesta: {respuesta[:50]}{'...' if len(respuesta) > 50 else ''}")
        else:
            print(f"{Colores.AMARILLO}  No se encontraron dongles WiFi{Colores.RESET}")    

    def _obtener_configuracion_modelo(self, nombre_equipo: str) -> Dict:
        """Obtiene la configuración del modelo para un equipo específico"""
        config_equipo = self.config_equipos[nombre_equipo]
        modelo = config_equipo.get('modelo')
        
        imprimir_debug(f"DEBUG: Obteniendo configuración para {nombre_equipo}, modelo: {modelo}")
        imprimir_debug(f"DEBUG: Modelos disponibles: {list(self.modelos_equipos.keys())}")
        
        if modelo and modelo in self.modelos_equipos:
            config = self.modelos_equipos[modelo]
            imprimir_debug(f"DEBUG: Configuración encontrada para modelo {modelo}: {list(config.keys())}")
            return config
        else:
            # Modelo por defecto si no se encuentra
            print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- AVISO: Modelo '{modelo}' no encontrado para {nombre_equipo}, usando ANENJI6K2 por defecto{Colores.RESET}")
            config = self.modelos_equipos.get('ANENJI6K2', {})
            imprimir_debug(f"DEBUG: Usando configuración por defecto: {list(config.keys())}")
            return config
            
    def _actualizar_configuracion_equipo(self, nombre_equipo: str):
        """Actualiza la configuración actual para un equipo basado en su modelo"""
        config_modelo = self._obtener_configuracion_modelo(nombre_equipo)
        self.configuraciones_actuales[nombre_equipo] = config_modelo
        
        imprimir_debug(f"DEBUG: Actualizando configuración para {nombre_equipo}")
        imprimir_debug(f"DEBUG: Configuración modelo keys: {list(config_modelo.keys())}")
        
        configuraciones_registros = obtener_configuraciones_registros(config_modelo)
        self.configuraciones_registros_actuales[nombre_equipo] = configuraciones_registros
        
        imprimir_debug(f"DEBUG: Registros configurados para {nombre_equipo}: {len(configuraciones_registros)}")
        if configuraciones_registros:
            imprimir_debug(f"DEBUG: Primeros 5 registros: {list(configuraciones_registros.keys())[:5]}")            

    def _inicializar_temporizadores(self):
        tiempo_actual = time.time()
        for nombre_equipo, config_equipo in self.config_equipos.items():
            if config_equipo.get('usar', 0):
                # Inicializar con un tiempo en el pasado para forzar primera lectura inmediata
                self.ultimos_tiempos_lectura[nombre_equipo] = tiempo_actual - config_equipo.get('tiempo_captura', 30)
                self.contadores_errores[nombre_equipo] = 0
                self.fallos_diarios[nombre_equipo] = 0
                self._actualizar_configuracion_equipo(nombre_equipo)
                
    def _reiniciar_contadores_diarios_si_necesario(self):
        hoy = datetime.now().date()
        if hoy > self.ultimo_reinicio_diario:
            for nombre_equipo in self.fallos_diarios:
                self.fallos_diarios[nombre_equipo] = 0
            self.ultimo_reinicio_diario = hoy
    
    def _debe_leer_equipo(self, nombre_equipo: str) -> bool:
        if nombre_equipo not in self.ultimos_tiempos_lectura:
            return True
            
        config_equipo = self.config_equipos[nombre_equipo]
        intervalo = config_equipo.get('tiempo_captura', 30)
        
        tiempo_actual = time.time()
        tiempo_ultima_lectura = self.ultimos_tiempos_lectura[nombre_equipo]
        tiempo_transcurrido = tiempo_actual - tiempo_ultima_lectura
        
        debe_leer = tiempo_transcurrido >= intervalo
        
        if debe_leer:
            imprimir_debug(f"DEBUG: {nombre_equipo} - LECTURA NECESARIA: " +
                          f"Transcurrido {tiempo_transcurrido:.2f}s >= Intervalo {intervalo}s")
        
        return debe_leer

    
    def _manejar_error_equipo(self, nombre_equipo: str, error: Exception):
        self.contadores_errores[nombre_equipo] += 1
        self.fallos_diarios[nombre_equipo] += 1
        contador_errores = self.contadores_errores[nombre_equipo]
        
        color_equipo = self.config_equipos[nombre_equipo].get('color', Colores.ROJO)
        mensaje_error = f"{color_equipo}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- ERROR {nombre_equipo}: {error} (fallos hoy: {self.fallos_diarios[nombre_equipo]}){Colores.RESET}"
        print(mensaje_error)
        
        if self.telegram:
            self.telegram.enviar_mensaje(f"❌ <b>ERROR {nombre_equipo}</b>\n{error}\nFallos hoy: {self.fallos_diarios[nombre_equipo]}")
        
        if contador_errores >= self.max_errores_antes_reinicio:
            mensaje_fatal = f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Demasiados errores en {nombre_equipo}. Deteniendo script...{Colores.RESET}"
            print(mensaje_fatal)
            if self.telegram:
                self.telegram.enviar_mensaje(f"🛑 <b>SISTEMA DETENIDO</b>\nDemasiados errores en {nombre_equipo}")
            asyncio.create_task(self.manejador_conexiones.cerrar_todas_conexiones())
            raise SystemExit(f"Demasiados errores consecutivos en {nombre_equipo}")
    
    def _reiniciar_contador_errores_equipo(self, nombre_equipo: str):
        self.contadores_errores[nombre_equipo] = 0
    
    async def _leer_registro_unico(self, ip_dongle: str, registro: int, cantidad: int = 1) -> Optional[List[int]]:
        try:
            socket_cliente = await self.manejador_conexiones.obtener_conexion(ip_dongle)
            if not socket_cliente:
                return None
            
            id_transaccion = 0x0772
            comando = crear_peticion_modbus(id_transaccion, 0x01, 0x03, registro, cantidad)
            
            imprimir_debug(f"  DEBUG: Enviando lectura registro {registro}, cantidad {cantidad}")
            
            bucle = asyncio.get_event_loop()
            await bucle.sock_sendall(socket_cliente, comando)
            
            respuesta = await asyncio.wait_for(
                bucle.sock_recv(socket_cliente, 1024),
                timeout=3.0
            )
            
            valores = decodificar_respuesta_modbus(respuesta, cantidad)
            return valores
            
        except asyncio.TimeoutError:
            await self.manejador_conexiones.cerrar_conexion(ip_dongle)
            return None
        except Exception as e:
            await self.manejador_conexiones.cerrar_conexion(ip_dongle)
            return None
    
    async def _escribir_registro_unico(self, ip_dongle: str, registro: int, valor: int) -> bool:
        """Escribe un valor en un registro específico"""
        try:
            socket_cliente = await self.manejador_conexiones.obtener_conexion(ip_dongle)
            if not socket_cliente:
                imprimir_debug("  DEBUG: No se pudo obtener conexión")
                return False
            
            id_transaccion = 0x0772
            comando = crear_escritura_registro(id_transaccion, 0x01, registro, valor)
            
            imprimir_debug(f"  DEBUG: Enviando escritura registro {registro}, valor {valor}")
            
            bucle = asyncio.get_event_loop()
            await bucle.sock_sendall(socket_cliente, comando)
            
            # Esperar respuesta
            respuesta = await asyncio.wait_for(
                bucle.sock_recv(socket_cliente, 1024),
                timeout=5.0
            )
            
            imprimir_debug(f"  DEBUG: Respuesta escritura recibida ({len(respuesta)} bytes): {bytes_a_hex(respuesta)}")
            
            # ANALIZAR LA RESPUESTA EN DETALLE
            if len(respuesta) == 0:
                imprimir_debug("  DEBUG: Respuesta vacía - fallo")
                return False
                
            elif len(respuesta) == 8 and respuesta == b'\x07\x72\x00\x00\x00\x02\xff\x04':
                imprimir_debug("  DEBUG: Respuesta corta recibida (8 bytes) - posible rechazo del comando")
                return False
                
            elif len(respuesta) >= 11:
                # Respuesta de longitud normal, decodificar normalmente
                valores = decodificar_respuesta_modbus(respuesta, 1)
                exito = valores is not None
                imprimir_debug(f"  DEBUG: Decodificación normal - éxito: {exito}")
                return exito
                
            else:
                # Respuesta de longitud intermedia
                imprimir_debug(f"  DEBUG: Respuesta de longitud inusual: {len(respuesta)} bytes")
                valores = decodificar_respuesta_modbus(respuesta, 1)
                exito = valores is not None
                imprimir_debug(f"  DEBUG: Decodificación forzada - éxito: {exito}")
                return exito
                
        except asyncio.TimeoutError:
            imprimir_debug(f"  DEBUG: Timeout en escritura del registro {registro}")
            await self.manejador_conexiones.cerrar_conexion(ip_dongle)
            return False
        except Exception as e:
            imprimir_debug(f"  DEBUG: Error en escritura del registro {registro}: {e}")
            await self.manejador_conexiones.cerrar_conexion(ip_dongle)
            return False
    
    async def _leer_grupos_multiples(self, ip_dongle: str, grupos_registros: List[tuple], configuraciones_registros: Dict) -> Dict[str, Any]:
        todos_datos = {}
        
        for dir_inicio, cantidad, nombre_grupo in grupos_registros:
            valores = await self._leer_registro_unico(ip_dongle, dir_inicio, cantidad)
            if valores:
                todos_datos = extraer_registros_individuales(todos_datos, dir_inicio, valores, configuraciones_registros)
            else:
                return {}
            
            await asyncio.sleep(0.05)
        
        return todos_datos
    
    async def _leer_registros_individuales(self, ip_dongle: str, configuraciones_registros: Dict) -> Dict[str, Any]:
        todos_datos = {}
        
        for nombre_reg, config in configuraciones_registros.items():
            if 'reg' in config:
                registro = config['reg']
                valores = await self._leer_registro_unico(ip_dongle, registro, 1)
                if valores and len(valores) > 0:
                    valor_procesado = procesar_valor_registro(nombre_reg, valores[0], config)
                    todos_datos[nombre_reg] = valor_procesado
                else:
                    todos_datos[nombre_reg] = None
            
            await asyncio.sleep(0.02)
        
        return todos_datos
    
    async def leer_registro_equipo(self, nombre_equipo: str, nombre_registro: str) -> Optional[Any]:
        """Lee un registro específico de un equipo"""
        if nombre_equipo not in self.config_equipos:
            return None
        
        config_equipo = self.config_equipos[nombre_equipo]
        if not config_equipo.get('usar', 0):
            return None
        
        # Asegurarse de que tenemos la configuración actualizada
        if nombre_equipo not in self.configuraciones_registros_actuales:
            self._actualizar_configuracion_equipo(nombre_equipo)
        
        configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
        
        if nombre_registro not in configuraciones_registros:
            return None
        
        config_registro = configuraciones_registros[nombre_registro]
        ip_dongle = config_equipo['IP']
        registro = config_registro['reg']
        
        valores = await self._leer_registro_unico(ip_dongle, registro, 1)
        if valores and len(valores) > 0:
            return procesar_valor_registro(nombre_registro, valores[0], config_registro)
        
        return None
    
    async def escribir_registro_equipo(self, nombre_equipo: str, nombre_registro: str, valor: Any) -> bool:
        """Escribe un valor en un registro específico de un equipo"""
        imprimir_debug(f"DEBUG: Iniciando escritura - Equipo: {nombre_equipo}, Registro: {nombre_registro}, Valor: {valor}")
        
        if nombre_equipo not in self.config_equipos:
            imprimir_debug("DEBUG: Equipo no encontrado")
            return False
        
        config_equipo = self.config_equipos[nombre_equipo]
        if not config_equipo.get('usar', 0):
            imprimir_debug("DEBUG: Equipo no está en uso")
            return False
        
        # Asegurarse de que tenemos la configuración actualizada
        if nombre_equipo not in self.configuraciones_registros_actuales:
            self._actualizar_configuracion_equipo(nombre_equipo)
        
        configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
        
        if nombre_registro not in configuraciones_registros:
            imprimir_debug(f"DEBUG: Registro '{nombre_registro}' no encontrado en configuraciones")
            return False
        
        config_registro = configuraciones_registros[nombre_registro]
        
        # Verificar si el registro permite escritura
        if not config_registro.get('escritura', False):
            imprimir_debug(f"DEBUG: Registro '{nombre_registro}' no permite escritura")
            return False
        
        # Verificar rango si está definido
        if 'rango' in config_registro:
            rango_min, rango_max = config_registro['rango']
            if valor < rango_min or valor > rango_max:
                imprimir_debug(f"DEBUG: Valor {valor} fuera de rango [{rango_min}, {rango_max}]")
                return False
        
        # Ajustar valor según decimales
        if 'dec' in config_registro:
            valor_ajustado = int(valor * (10 ** config_registro['dec']))
            imprimir_debug(f"DEBUG: Valor ajustado por decimales: {valor} -> {valor_ajustado}")
        else:
            valor_ajustado = int(valor)
            imprimir_debug(f"DEBUG: Valor sin ajuste decimal: {valor_ajustado}")
        
        ip_dongle = config_equipo['IP']
        registro = config_registro['reg']
        
        imprimir_debug(f"DEBUG: Enviando escritura a IP: {ip_dongle}, Registro: {registro}, Valor: {valor_ajustado}")
        
        exito = await self._escribir_registro_unico(ip_dongle, registro, valor_ajustado)
        
        imprimir_debug(f"DEBUG: Resultado escritura: {'EXITOSO' if exito else 'FALLIDO'}")
        
        return exito

    async def leer_datos_equipo(self, nombre_equipo: str) -> Optional[Dict[str, Any]]:
        config_equipo = self.config_equipos[nombre_equipo]
        ip_dongle = config_equipo['IP']
        
        if nombre_equipo not in self.configuraciones_actuales:
            self._actualizar_configuracion_equipo(nombre_equipo)
        
        config_modelo = self.configuraciones_actuales[nombre_equipo]
        configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
        
        tiempo_inicio = time.time()
        
        try:
            if 'COMANDOS' in config_modelo and config_modelo['COMANDOS']['lectura_multiple']['usar']:
                grupos_registros = crear_grupos_registros(
                    config_modelo['COMANDOS']['lectura_multiple']['rangos']
                )
                datos = await self._leer_grupos_multiples(ip_dongle, grupos_registros, configuraciones_registros)
            else:
                datos = await self._leer_registros_individuales(ip_dongle, configuraciones_registros)
            
            tiempo_captura = time.time() - tiempo_inicio
            
            if datos:
                datos_validos = any(valor is not None for valor in datos.values())
                
                if datos_validos:
                    self._reiniciar_contador_errores_equipo(nombre_equipo)
                    # Actualizar el tiempo de la última lectura AL FINALIZAR
                    self.ultimos_tiempos_lectura[nombre_equipo] = time.time()
                    
                    datos['tcaptura'] = round(tiempo_captura, 2)
                    datos['Nfallos'] = self.fallos_diarios[nombre_equipo]
                    datos['modelo'] = config_equipo.get('modelo', 'Desconocido')
                    
                    imprimir_debug(f"DEBUG: {nombre_equipo} - Captura completada en {tiempo_captura:.2f}s, próxima en {config_equipo.get('tiempo_captura', 30)}s")
                    return datos
                else:
                    raise Exception("Datos recibidos pero todos vacíos o inválidos")
            else:
                raise Exception("No se pudieron leer los datos del dispositivo")
                
        except Exception as e:
            imprimir_debug(f"DEBUG: Error en leer_datos_equipo para {nombre_equipo}: {str(e)}")
            self._manejar_error_equipo(nombre_equipo, e)
            return None
    
    def guardar_datos_base_datos(self, nombre_equipo: str, datos: Dict[str, Any]):
        exito = self.bd.guardar_datos_equipo(nombre_equipo, datos)
        if not exito:
            color_equipo = self.config_equipos[nombre_equipo].get('color', Colores.AMARILLO)
            print(f"{color_equipo}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- AVISO: No se pudo guardar en BD {nombre_equipo}{Colores.RESET}")
    
    def formatear_salida_compacta(self, nombre_equipo: str, datos: Dict[str, Any]) -> str:
        config_equipo = self.config_equipos[nombre_equipo]
        color_equipo = config_equipo.get('color', Colores.BLANCO)
        
        json_str = json.dumps(datos, ensure_ascii=False, separators=(',', ':'))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"{color_equipo}{timestamp} -- {nombre_equipo}: {json_str}{Colores.RESET}"
    
    async def listar_parametros_equipo(self, nombre_equipo: str):
        """Lista todos los parámetros de un equipo"""
        if not self.telegram:
            return
        
        imprimir_debug(f"DEBUG: Iniciando listado de parámetros para {nombre_equipo}")
        
        # Asegurarse de que tenemos la configuración actualizada
        if nombre_equipo not in self.configuraciones_registros_actuales:
            self._actualizar_configuracion_equipo(nombre_equipo)
        
        configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
            
        mensaje = f"📟   <b>LISTA PARAMETROS {nombre_equipo}</b>\n"
        mensaje += f"Modelo: {self.config_equipos[nombre_equipo].get('modelo', 'Desconocido')}\n"
        mensaje += "=============================\n"
        
        lineas_por_mensaje = 0
        mensaje_actual = mensaje
        
        # Evitar procesar 'ayuda' y 'lectura_multiple' como registros normales
        registros_a_evitar = ['ayuda', 'lectura_multiple']
        
        for nombre_reg, config in configuraciones_registros.items():
            if nombre_reg in registros_a_evitar:
                continue
            
            # Mostrar configuración del registro
            config_display = config.copy()
            if 'adaptar' in config_display:
                del config_display['adaptar']
            
            mensaje_actual += f"🚦<b>{nombre_reg}</b> : {config_display}\n"
            
            # Leer valor actual con manejo de errores mejorado
            try:
                valor_actual = await self.leer_registro_equipo(nombre_equipo, nombre_reg)
                if valor_actual is not None:
                    mensaje_actual += f"    ..... Valor Actual de <b>{nombre_reg}={valor_actual}</b>\n\n"
                else:
                    mensaje_actual += f"    ..... <b>Error lectura de {nombre_reg}</b>\n\n"
            except Exception as e:
                mensaje_actual += f"    ..... <b>Excepción en {nombre_reg}: {str(e)}</b>\n\n"
            
            lineas_por_mensaje += 1
            
            # Enviar mensaje cada 15 líneas para evitar límites de Telegram
            if lineas_por_mensaje >= 15:
                mensaje_actual += "=============================\n"
                self.telegram.enviar_mensaje(mensaje_actual)
                mensaje_actual = ""
                lineas_por_mensaje = 0
                await asyncio.sleep(1)  # Pausa entre mensajes
        
        # Enviar mensaje final si queda contenido
        if mensaje_actual:
            mensaje_actual += "=============================\n"
            self.telegram.enviar_mensaje(mensaje_actual)
        
        imprimir_debug(f"DEBUG: Listado de parámetros completado para {nombre_equipo}") 
   
    async def procesar_comando_mqtt(self, comando: Dict):
        """Procesa un comando recibido por MQTT"""
        nombre_equipo = comando['equipo']
        mensaje_comando = comando['comando']
        
        imprimir_debug(f"Timestamp: {datetime.now()} Procesando comando MQTT: {nombre_equipo} - '{mensaje_comando}'")
        
        # Comando vacío -> Listar todos los parámetros
        if not mensaje_comando.strip():
            imprimir_debug(f"DEBUG: Comando vacío detectado, listando parámetros...")
            await self.listar_parametros_equipo(nombre_equipo)
            return
        
        # Verificar si el comando contiene "=" (formato PARAMETRO=VALOR)
        if '=' in mensaje_comando:
            partes = mensaje_comando.split('=', 1)  # Dividir solo en el primer =
            nombre_parametro = partes[0].strip()
            valor_str = partes[1].strip()
        else:
            # Formato: PARAMETRO VALOR
            partes = mensaje_comando.strip().split()
            if len(partes) < 2:
                # Solo un parámetro - lectura
                nombre_parametro = partes[0]
                valor_str = None
            else:
                nombre_parametro = partes[0]
                valor_str = partes[1]
        
        # Asegurarse de que tenemos la configuración actualizada
        if nombre_equipo not in self.configuraciones_registros_actuales:
            self._actualizar_configuracion_equipo(nombre_equipo)
        
        configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
        
        # Validar que el parámetro existe
        if nombre_parametro not in configuraciones_registros:
            mensaje_error = f"Parámetro '{nombre_parametro}' no encontrado en modelo {self.config_equipos[nombre_equipo].get('modelo', 'Desconocido')}"
            if self.telegram:
                self.telegram.enviar_mensaje(f"❌ {mensaje_error}")
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {mensaje_error}{Colores.RESET}")
            return
        
        # Si no hay valor, es una lectura
        if valor_str is None:
            await self._procesar_lectura_parametro(nombre_equipo, nombre_parametro)
            return
        
        # Si hay valor, es una escritura
        await self._procesar_escritura_parametro(nombre_equipo, nombre_parametro, valor_str)
        
    async def _procesar_lectura_parametro(self, nombre_equipo: str, nombre_parametro: str):
        """Procesa una lectura de parámetro"""
        valor_actual = await self.leer_registro_equipo(nombre_equipo, nombre_parametro)
        if valor_actual is not None:
            # Asegurarse de que tenemos la configuración actualizada para obtener el registro
            if nombre_equipo not in self.configuraciones_registros_actuales:
                self._actualizar_configuracion_equipo(nombre_equipo)
            
            configuraciones_registros = self.configuraciones_registros_actuales[nombre_equipo]
            registro = configuraciones_registros[nombre_parametro]['reg']
            
            mensaje_respuesta = f"Valor registro {registro}...{nombre_parametro}= {valor_actual}"
            if self.telegram:
                self.telegram.enviar_mensaje(mensaje_respuesta)
            print(f"{Colores.VERDE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {mensaje_respuesta}{Colores.RESET}")
        else:
            mensaje_error = f"Error leyendo parámetro {nombre_parametro}"
            if self.telegram:
                self.telegram.enviar_mensaje(f"❌ {mensaje_error}")
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- {mensaje_error}{Colores.RESET}")

    async def _procesar_escritura_parametro(self, nombre_equipo: str, nombre_parametro: str, valor_str: str):
        """Procesa una escritura de parámetro"""
        try:
            # Convertir valor
            if '.' in valor_str:
                valor = float(valor_str)
            else:
                valor = int(valor_str)
            
            # Leer valor actual
            valor_actual = await self.leer_registro_equipo(nombre_equipo, nombre_parametro)
            
            if valor_actual is None:
                mensaje_error = f"No se pudo leer el valor actual de {nombre_parametro}"
                if self.telegram:
                    self.telegram.enviar_mensaje(f"❌ {mensaje_error}")
                return
            
            # Escribir nuevo valor
            exito = await self.escribir_registro_equipo(nombre_equipo, nombre_parametro, valor)
            
            if exito:
                # Pequeña pausa y confirmación
                await asyncio.sleep(1)
                valor_despues = await self.leer_registro_equipo(nombre_equipo, nombre_parametro)
                
                if valor_despues == valor:
                    mensaje = f"✅ Parametro cambiado con exito\n{nombre_parametro}: {valor_actual} → {valor_despues}"
                else:
                    mensaje = f"⚠️ Escritura parcial\n{nombre_parametro}: {valor_actual} → {valor_despues} (esperado: {valor})"
                    
                if self.telegram:
                    self.telegram.enviar_mensaje(mensaje)
                    
            else:
                mensaje_error = f"❌ Error en escritura de {nombre_parametro}"
                if self.telegram:
                    self.telegram.enviar_mensaje(mensaje_error)
                
        except Exception as e:
            mensaje_error = f"❌ Error: {str(e)}"
            if self.telegram:
                self.telegram.enviar_mensaje(mensaje_error)
            
    async def ejecutar_bucle_continuo(self):
        """Bucle principal con gestión individual de tiempos por equipo"""
        try:
            while True:
                tiempo_inicio_ciclo = time.time()
                
                self._reiniciar_contadores_diarios_si_necesario()
                
                # Procesar comandos MQTT pendientes
                comando_mqtt = self.mqtt.obtener_comando_pendiente()
                if comando_mqtt:
                    await self.procesar_comando_mqtt(comando_mqtt)
                
                # Leer equipos que necesiten lectura y calcular tiempos individuales
                tiempos_restantes = []
                
                for nombre_equipo, config_equipo in self.config_equipos.items():
                    if config_equipo.get('usar', 0) and self._debe_leer_equipo(nombre_equipo):
                        tiempo_inicio_lectura = time.time()
                        datos = await self.leer_datos_equipo(nombre_equipo)
                        
                        if datos:
                            # Mostrar en consola
                            salida = self.formatear_salida_compacta(nombre_equipo, datos)
                            print(salida)
                            print("-" * 80)
                            
                            # Guardar en base de datos
                            self.guardar_datos_base_datos(nombre_equipo, datos)
                            
                            # Calcular tiempo restante para este equipo específico
                            tiempo_lectura = time.time() - tiempo_inicio_lectura
                            intervalo = config_equipo.get('tiempo_captura', 30)
                            tiempo_restante = max(0, intervalo - tiempo_lectura)
                            tiempos_restantes.append(tiempo_restante)
                            
                            imprimir_debug(f"DEBUG: {nombre_equipo} - Lectura: {tiempo_lectura:.2f}s, " +
                                         f"Intervalo: {intervalo}s, " +
                                         f"Restante: {tiempo_restante:.2f}s")
                
                # Calcular tiempo de espera óptimo
                if tiempos_restantes:
                    # Esperar al menos hasta que el equipo más "urgente" necesite lectura
                    tiempo_espera = min(tiempos_restantes)
                    tiempo_espera = max(0.1, tiempo_espera)  # Mínimo 0.1 segundos
                    
                    imprimir_debug(f"DEBUG: Esperando {tiempo_espera:.2f}s (mínimo de {len(tiempos_restantes)} equipos)")
                else:
                    # Si no se leyó ningún equipo, calcular cuánto esperar hasta la próxima lectura
                    tiempo_espera = self._calcular_tiempo_espera_sin_lecturas()
                
                # Esperar el tiempo calculado
                await asyncio.sleep(tiempo_espera)
                        
        except KeyboardInterrupt:
            print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Detenido por usuario{Colores.RESET}")
            if self.telegram:
                self.telegram.enviar_mensaje("🛑 <b>SISTEMA DETENIDO POR USUARIO</b>")
            await self.manejador_conexiones.cerrar_todas_conexiones()
        except Exception as e:
            print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Error crítico: {e}{Colores.RESET}")
            if self.telegram:
                self.telegram.enviar_mensaje(f"💥 <b>ERROR CRÍTICO</b>\n{str(e)}")
            await self.manejador_conexiones.cerrar_todas_conexiones()
            traceback.print_exc()

    def _calcular_tiempo_espera_sin_lecturas(self) -> float:
        """Calcula el tiempo de espera cuando no hay lecturas en este ciclo"""
        tiempo_proxima_lectura = float('inf')
        tiempo_actual = time.time()
        
        for nombre_equipo, config_equipo in self.config_equipos.items():
            if config_equipo.get('usar', 0):
                intervalo = config_equipo.get('tiempo_captura', 30)
                tiempo_ultima = self.ultimos_tiempos_lectura.get(nombre_equipo, 0)
                tiempo_transcurrido = tiempo_actual - tiempo_ultima
                tiempo_restante = max(0, intervalo - tiempo_transcurrido)
                tiempo_proxima_lectura = min(tiempo_proxima_lectura, tiempo_restante)
        
        # Esperar hasta la próxima lectura, pero máximo 1 segundo para revisar comandos MQTT
        tiempo_espera = max(0.1, min(1.0, tiempo_proxima_lectura))
        imprimir_debug(f"DEBUG: Sin lecturas - Próxima en {tiempo_proxima_lectura:.2f}s, Esperando {tiempo_espera:.2f}s")
        
        return tiempo_espera
            
# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

async def principal():
    lector = LectorRS232Wifi(RS232_WIFI)
    await lector.ejecutar_bucle_continuo()

def ejecutar_como_servicio():
    try:
        asyncio.run(principal())
    except KeyboardInterrupt:
        print(f"{Colores.AMARILLO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Servicio detenido{Colores.RESET}")
    except Exception as e:
        print(f"{Colores.ROJO}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- SISTEMA: Error servicio: {e}{Colores.RESET}")

if __name__ == "__main__":
    ejecutar_como_servicio()