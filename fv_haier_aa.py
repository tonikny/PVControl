#!/usr/bin/env python3
import asyncio
import json
import time
import traceback
import paho.mqtt.client as mqtt
import telebot
from pyhon import Hon
import MySQLdb
import sys
import os

# ============================================================
# Detectar si estamos en terminal (para prints)
# ============================================================
IS_TERMINAL = sys.stdout.isatty()

def safe_print(*args, **kwargs):
    if IS_TERMINAL:
        print(*args, **kwargs)

# ============================================================
# HAIER DICT por defecto
# ============================================================
HAIER = {
    'AA': {'usar': 1, 'Usuario_HON': 'xx@gmail.com', 'Password_HON': 'xx'},
    'BB': {'usar': 0, 'Usuario_HON': 'xx@gmail.com', 'Password_HON': 'xx'}
}

# ============================================================
# CARGA DE PARÁMETROS
# ============================================================
basepath = '/home/pi/PVControl+/'
exec(open(basepath + "Parametros_FV_DIST.py").read(), globals())
exec(open(basepath + "Parametros_FV.py").read(), globals())

HAIER_DICT = globals().get("HAIER", HAIER)

MQTT_BROKER = globals().get("mqtt_broker", "localhost")
MQTT_PORT   = int(globals().get("mqtt_puerto", 1883))
MQTT_USER   = globals().get("mqtt_usuario")
MQTT_PASS   = globals().get("mqtt_clave")

TOKEN = globals().get("TOKEN")
Aut   = globals().get("Aut", [])
TELEGRAM_TARGET = Aut[0] if Aut else None
bot = telebot.TeleBot(TOKEN) if TOKEN else None

DB_HOST = globals().get("servidor")
DB_USER = globals().get("usuario")
DB_PASS = globals().get("clave")
DB_NAME = globals().get("basedatos")
SAVE_INTERVAL = int(globals().get("SAVE_INTERVAL", 60))

# ============================================================
# TELEGRAM
# ============================================================
def send_telegram_single(msg):
    if not bot or TELEGRAM_TARGET is None:
        return
    try:
        bot.send_message(TELEGRAM_TARGET, msg)
    except Exception as e:
        safe_print("[TG] Error enviando mensaje:", e)

# ============================================================
# BASE DE DATOS
# ============================================================
def conectar_bd():
    try:
        db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        return db, db.cursor()
    except Exception as e:
        safe_print("[DB] Error:", e)
        return None, None

def guardar_datos(cursor, datos, id_equipo):
    try:
        sql = """
            INSERT INTO equipos (id_equipo, tiempo, sensores)
            VALUES (%s, NOW(), %s)
            ON DUPLICATE KEY UPDATE
                tiempo = VALUES(tiempo),
                sensores = VALUES(sensores)
        """
        cursor.execute(sql, (id_equipo, json.dumps(datos, ensure_ascii=False)))
        return True
    except Exception as e:
        safe_print("[DB] Error guardando:", e)
        return False

# ============================================================
# HELPERS
# ============================================================
def _get_attr_value(a):
    try:
        return a.value if hasattr(a, "value") else a
    except:
        return None

async def get_appliance_by_nick(hon, nick):
    for ac in hon.appliances:
        if getattr(ac, "nick_name", None) == nick:
            return ac
    return None

async def haier_info_dict(hon, nick):
    ac = await get_appliance_by_nick(hon, nick)
    if not ac:
        return {}
    try:
        await ac.update()
    except:
        pass
    try:
        params_raw = ac.attributes.get("parameters", {})
    except:
        params_raw = {}
    return {k: _get_attr_value(v) for k, v in params_raw.items()}

def haier_info_text(info):
    if not info:
        return "❌ Info no disponible"
    return (
        "📡 *Estado Aire Haier*\n"
        f"• On/Off: {info.get('onOffStatus')}\n"
        f"• Modo: {info.get('machMode')}\n"
        f"• Temp interior: {info.get('tempIndoor')}\n"
        f"• Temp consigna: {info.get('tempSel')}\n"
        f"• Temp exterior: {info.get('tempOutdoor')}\n"
        f"• Compresor: {info.get('compressorCurrent')}\n"
    )

# ============================================================
# MENSAJE DE AYUDA
# ============================================================
def haier_help_text():
    return (
        "📖 *COMANDOS DISPONIBLES:*\n"
        "• `info` - Estado actual del aire\n"
        "• `on` - Encender\n"
        "• `off` - Apagar\n"
        "• `temp XX` - Cambiar temperatura (ej: temp 25)\n"
        "• `modo X` - Cambiar modo (1:cool, 2:dry, 3:fan, 4:heat, 5:auto)\n"
        "• `ventilador X` - Velocidad ventilador (1:auto, 2:high, 3:medium, 4:low)\n"
        "• `?` o vacío - Mostrar esta ayuda"
    )

# ============================================================
# HAIER COMANDOS
# ============================================================
async def haier_power_on(ac): await ac.commands["startProgram"].send(); return "Encendido"
async def haier_power_off(ac): await ac.commands["stopProgram"].send(); return "Apagado"
async def haier_set_temp(ac, t): ac.commands["settings"].parameters["tempSel"].value=float(t); await ac.commands["settings"].send(); return f"Temp {t}"
async def haier_set_mode(ac, m): ac.commands["settings"].parameters["machMode"].value=int(m); await ac.commands["settings"].send(); return f"Modo {m}"
async def haier_set_fan(ac, s): ac.commands["settings"].parameters["windSpeed"].value=int(s); await ac.commands["settings"].send(); return f"Fan {s}"

# ============================================================
# SESIONES PERSISTENTES
# ============================================================
class HaierSession:
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.hon = None
        self.lock = asyncio.Lock()

    async def get(self):
        async with self.lock:
            if not self.hon:
                self.hon = Hon(self.user, self.pwd)
                await self.hon.__aenter__()  # abrir sesión
            return self.hon

    async def reset(self):
        async with self.lock:
            if self.hon:
                try: await self.hon.__aexit__(None, None, None)
                except: pass
                self.hon = None

haier_sessions = {}
haier_queue = asyncio.Queue()

# ============================================================
# WORKER CENTRAL
# ============================================================
async def process_command(team, payload):
    cfg = HAIER_DICT.get(team)
    if not cfg or cfg.get("usar") != 1:
        return "Ignorado (no Haier)"

    # Manejar caso de payload vacío o "?"
    if not payload or payload.strip() == "?":
        return haier_help_text()

    if team not in haier_sessions:
        haier_sessions[team] = HaierSession(cfg["Usuario_HON"], cfg["Password_HON"])
    s = haier_sessions[team]

    try:
        hon = await s.get()
        ac = await get_appliance_by_nick(hon, team)
        parts = payload.split()
        action = parts[0].lower()

        if action == "info":
            info = await haier_info_dict(hon, team)
            if db_cursor:
                guardar_datos(db_cursor, info, team)
                if db_conn:
                    db_conn.commit()
            safe_print(f"[INFO] {team} info: {info}")
            return haier_info_text(info)

        if action == "on": return await haier_power_on(ac)
        if action == "off": return await haier_power_off(ac)
        if action == "temp" and len(parts)==2: return await haier_set_temp(ac, parts[1])
        if action == "modo" and len(parts)==2: return await haier_set_mode(ac, parts[1])
        if action == "ventilador" and len(parts)==2: return await haier_set_fan(ac, parts[1])

        return "Comando inválido. Envía '?' para ver comandos disponibles."

    except Exception as e:
        await s.reset()
        return f"Reconectado ({e})"

async def haier_worker():
    while True:
        team, payload, fut = await haier_queue.get()
        try:
            res = await process_command(team, payload)
        except Exception as e:
            res = f"Error: {e}"
        fut.set_result(res)

# ============================================================
# MQTT
# ============================================================
def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode().strip()
        parts = topic.split("/")
        if len(parts) < 2:
            return
        team = parts[1]

        cfg = HAIER_DICT.get(team)
        if not cfg or cfg.get("usar") != 1:
            return

        async def run():
            fut = asyncio.get_running_loop().create_future()
            await haier_queue.put((team, payload, fut))
            r = await fut
            safe_print(f"[MQTT] {team} {payload} -> {r}")
            send_telegram_single(f"📨 Comando: {payload}\nEquipo: {team}\n\nResultado:\n{r}")

        asyncio.run_coroutine_threadsafe(run(), loop)

    except Exception as e:
        safe_print("[MQTT] Error en on_message:", e)

# ============================================================
# TAREA PERIÓDICA (usa HaierSession para no abrir conexiones nuevas)
# ============================================================
async def periodic_task():
    while True:
        for team, cfg in HAIER_DICT.items():
            if cfg.get("usar") != 1:
                continue
            if team not in haier_sessions:
                haier_sessions[team] = HaierSession(cfg["Usuario_HON"], cfg["Password_HON"])
            s = haier_sessions[team]
            try:
                hon = await s.get()
                info = await haier_info_dict(hon, team)
                if db_cursor:
                    guardar_datos(db_cursor, info, team)
                    if db_conn:
                        db_conn.commit()
                safe_print(f"[TASK] {team} info guardada")
            except Exception as e:
                safe_print(f"[TASK] Error consultando {team}: {e}")
        await asyncio.sleep(SAVE_INTERVAL)

# ============================================================
# MAIN
# ============================================================
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

db_conn, db_cursor = conectar_bd()

client = mqtt.Client()
if MQTT_USER and MQTT_PASS:
    client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe("PVControl/#")
client.loop_start()

# Lanzar worker y tarea periódica
loop.create_task(haier_worker())
loop.create_task(periodic_task())
safe_print("[MAIN] Loop asyncio corriendo")

loop.run_forever()