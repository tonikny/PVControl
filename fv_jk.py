#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Version 2024/01/31

"""
## USO desde ventana terminal

python3 fv_jk.py        # funcionamiento normal
   
python3 fv_jk.py -p     # saca por pantalla las distintas capturas

python3 fv_jk.py -scan  # realiza un scaneo de los dispositivos BT para poder identificar la MAC

python3 fv_jk.py -test  # realiza un test de forma autonoma sin estar integrado en PVControl+ con lo especificado en la variable BMS_JK

"""

########## NO TOCAR SALVO QUE SE QUIERA USAR FUERA DE PVControl+ con la opcion -test 
######### LA CONFIGURACION para PVControl+ SE DEBE HACER EN Parametros_FV_py con la siguiente estructura ##############

BMS_JK = {
    'JK1': {'usar':0,
            'MAC': 'C8:47:80:01:D8:CC',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 0, # 0 para NO grabar en BD
          },
          
    'JK2': {'usar':0,
            'MAC': 'C8:47:80:01:D9:0B',
            'tiempo_captura': 5,
            'ciclos_grabacion' : 0,
          },
    }

comandos = {
  'conectar': ['C', 'CONECTAR'],
  'desconectar': ['D', 'DESCONECTAR'],
  'informacion': ['I','INFO', 'INFORMACION'],
  'carga': ['CON','CARGA ON','COFF', 'CARGA OFF'],
  'descarga': ['DON','DESCARGA ON','DOFF', 'DESCARGA OFF'],
  'balance': ['BON','BALANCE ON','BOFF', 'BALANCE OFF'],
  'ayuda' : ['h','?','']
}

import asyncio
import math
import time
import MySQLdb 
import logging

from collections import defaultdict
from typing import List, Callable, Dict, Optional, Union

import json,sys

import paho.mqtt.client as mqtt
import telebot # Librería de la API del bot.
import timeout_decorator

flag = True
for s in ['-scan','-test']:
    if s in sys.argv:
        flag = False
        break

if flag:
    # #################### Control Ejecucion Servicio ########################################
    servicio = 'fv_jk'
    control = "sum([BMS_JK[b]['usar'] for b in BMS_JK])"

    exec(open("/home/pi/PVControl+/fv_control_servicio.py").read())
    # ########################################################################################
else:
    import sys,subprocess

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


DEBUG= 0
if '-p1' in sys.argv: DEBUG= 1 
elif '-p' in sys.argv: DEBUG= 100
elif '-test' in sys.argv: DEBUG= 100

BT_reinicio = 'sudo hciconfig hci0 reset'
print ("Reiniciando BT con: ", BT_reinicio, end = '.... ')
proceso = subprocess.run(BT_reinicio, shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     text=True
                    )
if proceso.returncode==0:
    msg = proceso.stdout
else:
    msg = proceso.stderr
print(msg)

#### Comprobacion libreria bleak
try:
    from bleak import BleakClient
except:
    res = subprocess.run('pip3 install bleak' , shell=True)
    if res.returncode == 0:
        try:
            from bleak import BleakClient
        except:
            print ('Error en instalacion libreria bleak')
            
async def scan():
    from bleak import BleakScanner
    devices = await BleakScanner.discover()
    
    for d in devices:
        print(d, end='')

        if d.address[:7] == 'C8:47:8':
            print(Fore.CYAN,'  ..... BMS JK', Fore.GREEN)
        else:
            print()
    
if '-scan' in sys.argv:
    print()
    print(Fore.RED, '=' * 80)
    print(Fore.YELLOW, '      ESCANEANDO DISPOSITIVOS BLUETOOTH.......')
    print(Fore.RED, '=' * 80)
    print (Fore.GREEN, end='')
    asyncio.run(scan())
    print(Fore.RED, '=' * 80)
    sys.exit()

@timeout_decorator.timeout(5, use_signals=False)
def bot_enviar_mensaje(cid, msg):
    bot.send_message(cid, msg)

try:
    if usar_telegram == 1:
        try:
            bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
            bot.skip_pending = True # Skip the pending messages
            cid = Aut[0]
            bot_enviar_mensaje(cid, f'Arrancando Programa Control BMS JK')
        except:
            print ('Error en envio de mensaje Telegram')
except:
    pass

# Comprobacion que la tabla en BD tiene los campos necesarios
def comprobar_bd(equipo, nceldas):
    ee = 100
    if '-test' not in sys.argv:
        try:
            ee = 110   
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()
            
            # Comprobacion si tabla equipos existe y si no se crea
            sql_create = """ CREATE TABLE IF NOT EXISTS `equipos` (
                          `id_equipo` varchar(50) COLLATE latin1_spanish_ci NOT NULL,
                          `tiempo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha Actualizacion',
                          `sensores` varchar(3000) COLLATE latin1_spanish_ci NOT NULL,
                           PRIMARY KEY (`id_equipo`)
                         ) ENGINE=MEMORY DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;"""

            import warnings # quitamos el warning que da si existe la tabla equipos
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cursor.execute(sql_create)
            ee = 120
            if BMS_JK[equipo]['usar'] == 1: # solo se chequea si se activa el BMS
                ee = 130
                try:#inicializamos registro en BD RAM
                    cursor.execute("INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)",
                                      (f"BMS_{equipo}","{}"))
                except:
                    pass   
                ee = 140
                try:
                    Sql = f"""    
                         CREATE TABLE IF NOT EXISTS `datos_celdas_{equipo}` (
                        `id_celda` int(11) NOT NULL AUTO_INCREMENT,
                        `Tiempo` datetime NOT NULL DEFAULT current_timestamp(),
                        `Ibat` float NOT NULL DEFAULT 0,
                        `AH_p` float NOT NULL DEFAULT 0,
                        `AH_n` float NOT NULL DEFAULT 0,
                        `SOC` float NOT NULL DEFAULT 0,
                        `C1` float NOT NULL DEFAULT 0,
                         PRIMARY KEY (`id_celda`),
                         KEY `Tiempo` (`Tiempo`)
                         ) 
                         ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_spanish_ci;
                         """
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        cursor.execute(Sql)
                    
                except:
                    pass
                
                #db.commit()
                # leer registro JK??
                ee = 150
                try:
                    ee = 155
                    Sql = f'SELECT * FROM datos_celdas_{equipo} LIMIT 1' 
                    nreg=cursor.execute(Sql)
                    #ncel = len(cursor.description) - 3 # Nº de celdas declaradas en BD
                    ncampos = [c[0] for c in cursor.description] # nombre de los campos
                    
                    ncel = 0
                    for campo in ncampos:
                        if campo[0] == 'C': ncel += 1
                        
                    ee = 159
                    #print(ncel, ncampos)
                    ee = 160
                    
                    ### Comprobacion nombres de campos
                    for c in ['Ibat','AH_p', 'AH_n', 'SOC']:
                        ee = 165
                        if c not in ncampos:
                            print(f'crear campo {c} en tabla datos_celdas_{equipo}')
                            Sql = f"ALTER TABLE `datos_celdas_{equipo}` ADD `{c}` FLOAT NOT NULL DEFAULT '0' "
                            cursor.execute(Sql)
                    
                    ee = 180
                    ### Comprobacion Nº de celdas
                    if ncel < nceldas:
                        print (Fore.RED+ "ATENCION... el nº de campos en BD es menor que el nº de celdas declaradas en Parametros_FV.py")
                        print ( " se crean nuevos campos en tabla datos_celdas")
                        print ("-" * 50)
                        for K in range(nceldas):
                            try:
                                Sql = f"ALTER TABLE `datos_celdas_{equipo}` ADD `C{K+1}` FLOAT NOT NULL DEFAULT '0'"
                                cursor.execute(Sql)
                                db.commit()
                                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} creado')
                            except:
                                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} ya estaba creado')
                    elif ncel > nceldas:
                        print (Fore.RED+ "ATENCION... el nº de campos en BD es mayor que el nº de celdas declaradas en Parametros_FV.py")
                        print ( " se borraran los campos sobrantes.... si hay datos en estos campos se perderan")
                        print ("-" * 50)
                        for K in range(nceldas,ncel):
                            try:
                                Sql = f"ALTER TABLE `datos_celdas_{equipo}` DROP `C{K+1}`"
                                cursor.execute(Sql)
                                db.commit()
                                if DEBUG >= 2: print (Fore.RED,f'Campo de celda C{K+1} borrado')
                            except:
                                if DEBUG >= 2: print (Fore.GREEN,f'Campo de celda C{K+1} no existe')
                    
                except:
                        print(f'Error {ee} en la actualizacion de campos en datos_celdas_{equipo}')
   
            db.commit()
            cursor.close()
            db.close()

        except:
            print('ERROR en creacion/comprobacion de la Base de datos.....se detiene programa')
            sys.exit()


###################### CLASES ########################3
class dotdict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    # __hasattr__ = dict.__contains__

class FuturesPool:
    """
    Manage a collection of named futures.
    """
    def __init__(self):
        self._futures: Dict[str, asyncio.Future] = {}

    def acquire(self, name: str):
        if isinstance(name, tuple):
            tuple(self.acquire(n) for n in name)
            return FutureContext(name, pool=self)

        assert name not in self._futures, "already waiting for %s" % name
        fut = asyncio.Future()
        self._futures[name] = fut
        return FutureContext(name, pool=self)

    def set_result(self, name, value):
        fut = self._futures.get(name, None)
        if fut:
            if fut.done():
                # silently remove done future
                self.remove(name)
            else:
                fut.set_result(value)

    def clear(self):
        for fut in self._futures.values():
            fut.cancel()
        self._futures.clear()

    def remove(self, name):
        if isinstance(name, tuple):
            return tuple(self.remove(n) for n in name)
        self._futures.pop(name, None)

    async def wait_for(self, name: str, timeout):
        if isinstance(name, tuple):
            tasks = [self.wait_for(n, timeout) for n in name]
            return await asyncio.gather(*tasks, return_exceptions=False)

        try:
            return await asyncio.wait_for(self._futures.get(name), timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            raise
        finally:
            self.remove(name)

class FutureContext:
    def __init__(self, name: str, pool: 'FuturesPool'):
        self.name = name
        self.pool = pool

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.remove(self.name)
                      
class DeviceInfo:
    def __init__(self, model: str, hw_version: str, sw_version: str, name: Optional[str], sn: Optional[str] = None, pass1: Optional[str] = None, pass2: Optional[str] = None):
        self.model = model
        self.hw_version = hw_version
        self.sw_version = sw_version
        self.name = name
        self.sn = sn
        self.pass1 = pass1
        self.pass2 = pass2


    def __str__(self):
        s = f'DeviceInfo({self.model},hw-{self.hw_version},sw-{self.sw_version}'
        if self.name:
            s += ',' + self.name
        if self.sn:
            s += ',#' + self.sn
        
        return s + ')'

class BmsSample:
    def __init__(self, voltage, current, power=math.nan,
                 charge=math.nan, capacity=math.nan, cycle_capacity=math.nan,
                 num_cycles=math.nan, soc=math.nan,
                 balance_current=math.nan,
                 temperatures: List[float] = None,
                 mos_temperature=math.nan,
                 switches: Optional[Dict[str, bool]] = None,
                 uptime=math.nan, timestamp=None):
        """

        :param voltage:
        :param current: Current out of the battery (negative=charging, positive=discharging)
        :param charge: The charge available in Ah, aka remaining capacity, between 0 and `capacity`
        :param capacity: The capacity of the battery in Ah
        :param cycle_capacity: Total absolute charge meter (coulomb counter). Increases during charge and discharge. Can tell you the battery cycles (num_cycles = cycle_capacity/2/capacity). A better name would be cycle_charge. This is not well defined.
        :param num_cycles:
        :param soc: in % (0-100)
        :param balance_current:
        :param temperatures:
        :param mos_temperature:
        :param uptime BMS uptime in seconds
        """
        self.voltage: float = voltage
        self.current: float = current or 0  # -
        self._power = power  # 0 -> +0
        self.balance_current = balance_current

        # infer soc from capacity if soc is nan or type(soc)==int (for higher precision)
        if capacity > 0 and (math.isnan(soc) or (isinstance(soc, int) and charge > 0)):
            soc = round(charge / capacity * 100, 2)
        elif math.isnan(capacity) and soc > .2:
            capacity = round(charge / soc * 100)

        # assert math.isfinite(soc)

        self.charge: float = charge
        self.capacity: float = capacity
        self.soc: float = soc
        self.cycle_capacity: float = cycle_capacity
        self.num_cycles: float = num_cycles
        self.temperatures = temperatures
        self.mos_temperature = mos_temperature
        self.switches = switches
        self.uptime = uptime
        self.timestamp = timestamp or time.time()

        if switches:
            assert all(map(lambda x: isinstance(x, bool), switches.values())), "non-bool switches values %s" % switches

    @property
    def power(self):
        """
        :return: Power (P=U*I) in W
        """
        return (self.voltage * self.current) if math.isnan(self._power) else self._power

    def __str__(self):
        # noinspection PyStringFormat
        return 'BmsSampl(%(soc).1f%%,U=%(voltage).1fV,I=%(current).2fA,P=%(power).0fW,q=%(charge).1fAh/%(capacity).0f,mos=%(mos_temperature).1fC)' % {

        #return 'BmsSampl(%(soc).1f%%,U=%(voltage).1fV,I=%(current).2fA,P=%(power).0fW,q=%(charge).1fAh/%(capacity).0f,mos=%(mos_temperature).1fÃÂ°C)' % {
            **self.__dict__,
            "power": self.power
        }

    def invert_current(self):
        return self.multiply_current(-1)

    def multiply_current(self, x):
        res = copy(self)
        if res.current != 0:  # prevent -0 values
            res.current *= x
        if not math.isnan(res._power) and res._power != 0:
            res._power *= x
        return res

class BtBms:
      
      
    def __init__(self, address: str, name: str, keep_alive=False, psk=None, adapter=None, verbose_log=False,
                 _uses_pin=False):
        self.address = address
        self.name = name
        self.keep_alive = keep_alive
        self.verbose_log = verbose_log
        self.logger = get_logger(verbose_log)
        self._fetch_futures = FuturesPool()
        self._psk = psk
        self._connect_time = 0

        if not _uses_pin and psk:
            self.logger.warning('%s usually does not use a pairing PIN', type(self).__name__)

        if address.startswith('test_'):
            from bmslib.models.dummy import BleakDummyClient
            self.client = BleakDummyClient(address, disconnected_callback=self._on_disconnect)
        else:
            kwargs = {}
            if psk:
                try:
                    import bleak.backends.bluezdbus.agent
                except ImportError:
                    self.logger.warn(
                        "Installed bleak version %s has no pairing agent, pairing with a pin will likely fail! "
                        "Disable `install_newer_bleak` option or run `pip3 -r requirements.txt`",
                        bleak_version())

            self._adapter = adapter
            if adapter:  # hci0, hci1 (BT adapter hardware)
                kwargs['adapter'] = adapter

            self.client = BleakClient(address,
                                      handle_pairing=bool(psk),
                                      disconnected_callback=self._on_disconnect,
                                      **kwargs
                                      )

    async def start_notify(self, char_specifier, callback: Callable[[int, bytearray], None], **kwargs):
        if not isinstance(char_specifier, list):
            char_specifier = [char_specifier]
        exception = None
        for cs in char_specifier:
            try:
                await self.client.start_notify(cs, callback, **kwargs)
                return cs
            except Exception as e:
                exception = e
        await enumerate_services(self.client, self.logger)
        raise exception

    def characteristic_uuid_to_handle(self, uuid: str, property_name: str) -> Union[str, int]:
        for service in self.client.services:
            for char in service.characteristics:
                if char.uuid == uuid and property_name in char.properties:
                    return char.handle
        return uuid

    def _on_disconnect(self, _client):
        if self.keep_alive and self._connect_time:
            self.logger.warning('BMS %s disconnected after %.1fs!', self.__str__(), time.time() - self._connect_time)

        try:
            self._fetch_futures.clear()
        except Exception as e:
            self.logger.warning('error clearing futures pool: %s', str(e) or type(e))

    async def _connect_client(self, timeout):
        await self.client.connect(timeout=timeout)
        if self.verbose_log:
            await enumerate_services(self.client, logger=self.logger)
        self._connect_time = time.time()
        if self._psk:
            def get_passkey(device: str, pin, passkey):
                if pin:
                    self.logger.info(f"Device {device} is displaying pin '{pin}'")
                    return True

                if passkey:
                    self.logger.info(f"Device {device} is displaying passkey '{passkey:06d}'")
                    return True

                self.logger.info(f"Device {device} asking for psk, giving '{self._psk}'")
                return str(self._psk) or None

            self.logger.debug("Pairing %s using psk '%s'...", self.name, self._psk)
            res = await self.client.pair(callback=get_passkey)
            if not res:
                self.logger.error("Pairing failed!")

    @property
    def is_connected(self):
        return self.client.is_connected

    async def connect(self, timeout=20):
        """
        Establish a BLE connection
        :param timeout:
        :return:
        """
        await self._connect_client(timeout=timeout)

    async def _connect_with_scanner(self, timeout=20):
        """
        Starts a bluetooth discovery and tries to establish a BLE connection with back off.
         This fixes connection errors for some BMS (jikong). Use instead of connect().

        :param timeout:
        :return:
        """
        import bleak
        scanner_kw = {}
        if self._adapter:
            scanner_kw['adapter'] = self._adapter
        scanner = bleak.BleakScanner(**scanner_kw)
        self.logger.debug("starting scan")
        await scanner.start()

        attempt = 1
        while True:
            try:
                discovered = set(b.address for b in scanner.discovered_devices)
                
                print(f'discovered:{discovered}')
                
                if self.client.address not in discovered:
                    raise Exception('Device %s not discovered. Make sure it in range and is not being controled by '
                                    'another application. (%s)' % (self.client.address, discovered))

                self.logger.debug("connect attempt %d", attempt)
                await self._connect_client(timeout=timeout / 2)
                break
            except Exception as e:
                await self.client.disconnect()
                if attempt < 8:
                    self.logger.debug('retry %d after error %s', attempt, e)
                    await asyncio.sleep(0.2 * (1.5 ** attempt))
                    attempt += 1
                else:
                    await scanner.stop()
                    raise

        await scanner.stop()

    async def disconnect(self):
        await self.client.disconnect()
        self._fetch_futures.clear()

    async def fetch_device_info(self) -> DeviceInfo:
        """
        Retrieve static BMS device info (HW, SW version, serial number, etc)
        :return: DeviceInfo
        """
        raise NotImplementedError()

    async def fetch(self) -> BmsSample:
        """
        Retrieve a BMS sample
        :return:
        """
        raise NotImplementedError()

    async def fetch_voltages(self) -> List[int]:
        """
        Get cell voltages in mV. The implementation can require a prior fetch(), depending on BMS BLE data frame design.
        So the caller must call fetch() prior to fetch_voltages()
        :return: List[int]
        """
        raise NotImplementedError()

    async def fetch_temperatures(self) -> List[float]:
        
        #Get temperature readings in C. The implementation can require a prior fetch(), depending on BMS BLE data frame design.
        #So the caller must call fetch() prior to fetch_temperatures()
        #:return:
        raise NotImplementedError()

    async def subscribe(self, callback: Callable[[BmsSample], None]):
        raise NotImplemented()

    async def subscribe_voltages(self, callback: Callable[[List[int]], None]):
        raise NotImplemented()

    async def set_switch(self, switch: str, state: bool):
        """
        Send a switch command to the BMS to control a physical switch, usually a MOSFET or relay.
        :param switch:
        :param state:
        :return:
        """
        raise NotImplementedError()

    def __str__(self):
        return f'{self.__class__.__name__}({self.client.address})'

    async def __aenter__(self):
        # print("enter")
        if self.keep_alive and self.is_connected:
            return
        await self.connect()

    async def __aexit__(self, *args):
        # print("exit")
        if self.keep_alive:
            return
        if self.client.is_connected:
            await self.disconnect()

    def __await__(self):
        return self.__aexit__().__await__()

    def set_keep_alive(self, keep):
        if keep:
            self.logger.info("BMS %s keep alive enabled", self.__str__())
        self.keep_alive = keep

    def debug_data(self):
        return None

class JKBt(BtBms):
    CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

    TIMEOUT = 20

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        if kwargs.get('psk'):
            self.logger.warning('JK usually does not use a pairing PIN')
        self._buffer = bytearray()
        self._resp_table = {}
        self.num_cells = None
        self._callbacks: Dict[int, List[Callable[[bytes], None]]] = defaultdict(List)
        self.char_handle_notify = self.CHAR_UUID
        self.char_handle_write = self.CHAR_UUID

    def _buffer_crc_check(self):
        crc_comp = calc_crc(self._buffer[0:MIN_RESPONSE_SIZE - 1])
        crc_expected = self._buffer[MIN_RESPONSE_SIZE - 1]
        if crc_comp != crc_expected:
            self.logger.debug("crc check failed, %s != %s, %s", crc_comp, crc_expected, self._buffer)
        return crc_comp == crc_expected

    def _notification_handler(self, _sender, data):
        HEADER = bytes([0x55, 0xAA, 0xEB, 0x90])

        if data[0:4] == HEADER:  # and len(self._buffer)
            self.logger.debug("header, clear buf %s", self._buffer)
            self._buffer.clear()

        self._buffer += data

        self.logger.debug("bms msg(%d) (buf%d): %s\n", len(data), len(self._buffer), to_hex_str(data))

        if len(self._buffer) >= MIN_RESPONSE_SIZE:
            if len(self._buffer) > MAX_RESPONSE_SIZE:
                self.logger.warning('buffer longer than expected %d %s', len(self._buffer), self._buffer)

            crc_ok = self._buffer_crc_check()

            if not crc_ok and HEADER in self._buffer:
                idx = self._buffer.index(HEADER)
                self.logger.debug("crc check failed, header at %d, discarding start of %s", idx, self._buffer)
                self._buffer = self._buffer[idx:]
                crc_ok = self._buffer_crc_check()

            if not crc_ok:
                self.logger.error("crc check failed, discarding buffer %s", self._buffer)
            else:
                self._decode_msg(bytearray(self._buffer))
            self._buffer.clear()

    def _decode_msg(self, buf):
        resp_type = buf[4]
        self.logger.debug('got response %d (len%d)', resp_type, len(buf))
        self._resp_table[resp_type] = buf
        self._fetch_futures.set_result(resp_type, self._buffer[:])
        callbacks = self._callbacks.get(resp_type, None)
        if callbacks:
            for cb in callbacks:
                cb(buf)

    async def connect(self, timeout=15):
        """
        Connecting JK with bluetooth appears to require a prior bluetooth scan and discovery, otherwise the connectiong fails with
        `[org.bluez.Error.Failed] Software caused connection abort`. Maybe the scan triggers some wake up?
        :param timeout:
        :return:
        """

        try:
            await super().connect(timeout=6)
        except Exception as e:
            self.logger.info("normal connect failed (%s), connecting with scanner", str(e) or type(e))
            await self._connect_with_scanner(timeout=timeout)

        # there might be 2 chars with same uuid (weird?), one for notify/read and one for write
        # https://github.com/fl4p/batmon-ha/issues/83
        self.char_handle_notify = self.characteristic_uuid_to_handle(self.CHAR_UUID, 'notify')
        self.char_handle_write = self.characteristic_uuid_to_handle(self.CHAR_UUID, 'write')

        self.logger.debug('char_handle_notify=%s, char_handle_write=%s', self.char_handle_notify,
                          self.char_handle_write)

        await self.start_notify(self.char_handle_notify, self._notification_handler)
        await asyncio.sleep(2)
        await self._q(cmd=0x97, resp=0x03)  # device info
        await asyncio.sleep(2)
        await self._q(cmd=0x96, resp=(0x02, 0x01))  # device state (resp 0x01 & 0x02)
        # after these 2 commands the bms will continuously send 0x02-type messages

        buf = self._resp_table[0x01]
        
        i16 = lambda i: int.from_bytes(buf[i:(i + 2)], byteorder='little', signed=True)
        u32 = lambda i: int.from_bytes(buf[i:(i + 4)], byteorder='little', signed=False)
        f32u = lambda i: u32(i) * 1e-3
        f32s = lambda i: int.from_bytes(buf[i:(i + 4)], byteorder='little', signed=True) * 1e-3

        self.num_cells = buf[114]
        
        self.Nceldas = buf[114]
        
        self.Capacidad = f32s(130)
        self.UVP = f32s(10)
        self.UVPR = f32s(14)
        self.OVP = f32s(18)
        self.OVPR = f32s(22)

        self.Trig_Vol = f32s(26)
        self.SOC_100 = f32s(30)
        self.SOC_0 = f32s(34)
        
        
        self.Cal_Curr = f32s(38)

        self.Power_OFF = f32s(46)
        
        """
        Cont_Charge_Curr = f32s(50)
        Charge_OCP = f32s(54)
        Charge_OCPR = f32s(58)
        Cont_Charge_Curr = f32s(62)

        DisCharge_OCP = f32s(66)
        DisCharge_OCPR = f32s(70)
        # 74,78,82,86,90,94,98,102,106,110
        
        
        print(f'q_buf{buf}')
        print(f'Nceldas: {Nceldas} - Capacidad:{Capacidad}')
        print(f'UVP: {UVP} - UVPR: {UVPR}')
        print(f'OVP: {OVP} - OVPR: {OVPR}')
        """
        
        assert 0 < self.num_cells <= 24, "num_cells unexpected %s" % self.num_cells
        # self.capacity = int.from_bytes(buf[130:134], byteorder='little', signed=False) * 0.001

    async def disconnect(self):
        await self.client.stop_notify(self.char_handle_notify)
        await super().disconnect()

    async def _q(self, cmd, resp):
        with self._fetch_futures.acquire(resp):
            frame = _jk_command(cmd, [])
            self.logger.debug("write %s", frame)
            
            ###########################################
            if DEBUG == 100: print(Fore.RESET+f'Escribe en client.write_gatt_char {self} --{self.char_handle_write} -- frame={frame}')
            ###########################################
            
            await self.client.write_gatt_char(self.char_handle_write, data=frame)
            return await self._fetch_futures.wait_for(resp, self.TIMEOUT)

    async def _write(self, address, value):
        frame = _jk_command(address, value)
        await self.client.write_gatt_char(self.char_handle_write, data=frame)

    async def fetch_device_info(self):
        # https://github.com/jblance/mpp-solar/blob/master/mppsolar/protocols/jkabstractprotocol.py
        # https://github.com/syssi/esphome-jk-bms/blob/main/components/jk_bms_ble/jk_bms_ble.cpp#L1059
        buf = self._resp_table[0x03]
        
        print('#' * 80)
        print('INFO:  ', buf)
        print('#' * 80)
        
        """
        for i in range(300):
            try:
                print(f'{i} ->', end='')
                print(read_str(buf, i))
            except:
                pass
        """
        
        
        return DeviceInfo(
            model=read_str(buf, 6),
            hw_version=read_str(buf, 6 + 16),
            sw_version=read_str(buf, 6 + 16 + 8),
            name=read_str(buf, 6 + 16 + 8 + 16),
            sn=read_str(buf, 6 + 16 + 8 + 16 + 40),
            pass1=read_str(buf, 6 + 16 + 8 + 16 + 16), 
            pass2=read_str(buf, 6 + 16 + 8 + 16 + 40 + 32 ),
        )

    def _decode_sample(self, buf) -> BmsSample:
        buf_set = self._resp_table[0x01]
        
        #print(buf_set)
        #print(buf_set[1],buf_set[2],'---',buf_set[118],buf_set[122],buf_set[126])
        
        
        """
        print ('buf_set = ',buf_set)
        print()
        print ('buf = ',buf)
        """
        
        
        is_new_11fw = buf[189] == 0x00 and buf[189 + 32] > 0
        offset = 0
        if is_new_11fw:
            offset = 32
            self.logger.debug('New 11.x firmware, offset=%s', offset)
            
        offset = 32   
            
        i16 = lambda i: int.from_bytes(buf[i:(i + 2)], byteorder='little', signed=True)
        u32 = lambda i: int.from_bytes(buf[i:(i + 4)], byteorder='little', signed=False)
        f32u = lambda i: u32(i) * 1e-3
        f32s = lambda i: int.from_bytes(buf[i:(i + 4)], byteorder='little', signed=True) * 1e-3

        #temp = lambda x: float('nan') if x == -2000 else (x / 10)
        temp = lambda x: -99 if x == -2000 else (x / 10)

        return BmsSample(
            voltage=f32u(118 + offset),
            current=-f32s(126 + offset),
            soc=buf[141 + offset],

            cycle_capacity=f32u(154 + offset),  # total charge TODO rename cycle charge
            capacity=f32u(146 + offset),  # computed capacity (starts at self.capacity, which is user-defined),
            charge=f32u(142 + offset),  # "remaining capacity"

            temperatures=[temp(i16(130 + offset)), temp(i16(132 + offset))],
            mos_temperature=i16(112 + offset) / 10, #actualizado a 112 en lugar de 134
            balance_current=i16(138 + offset) / 1000,

            # 146 charge_full (see above)
            num_cycles=u32(150 + offset),
            switches=dict(
                carga=bool(buf_set[118]),
                descarga=bool(buf_set[122]),
                balance=bool(buf_set[126]), 
                
            ),
            #  #buf[166 + offset]),  charge FET state
            # buf[167 + offset]), discharge FET state
            uptime=float(u32(162 + offset)),  # seconds
        )

    async def fetch(self, wait=True) -> BmsSample:

        """
        Decode JK02
        references
        * https://github.com/syssi/esphome-jk-bms/blob/main/components/jk_bms_ble/jk_bms_ble.cpp#L360
        * https://github.com/jblance/mpp-solar/blob/master/mppsolar/protocols/jk02.py
        """
        
        if wait:
            with self._fetch_futures.acquire(0x02):
                await self._fetch_futures.wait_for(0x02, self.TIMEOUT)
               
        buf = self._resp_table[0x02]
        
        return self._decode_sample(buf)

    async def subscribe(self, callback: Callable[[BmsSample], None]):
        self._callbacks[0x02].append(lambda buf: callback(self._decode_sample(buf)))

    async def fetch_voltages(self):
        """
        :return: list of cell voltages in mV
        """
        if self.num_cells is None:
            raise Exception("num_cells not set")
        buf = self._resp_table[0x02]
        voltages = [int.from_bytes(buf[(6 + i * 2):(6 + i * 2 + 2)], byteorder='little') for i in
                    range(self.num_cells)]
        return voltages

    async def set_switch(self, switch: str, state: bool):
        # from https://github.com/syssi/esphome-jk-bms/blob/4079c22eaa40786ffa0cabd45d0d98326a1fdd29/components/jk_bms_ble/switch/__init__.py
        addresses = dict(
            carga=0x1D,
            descarga=0x1E,
            balance=0x1F
        )
        await self._write(addresses[switch], [0x1 if state else 0x0, 0, 0, 0])
        await asyncio.sleep(1)
        await self._q(cmd=0x96, resp=(0x02, 0x01))  # query settings

    def debug_data(self):
        return self._resp_table

###################### FUNCIONES ########################3
def get_logger(verbose=False):
    # log_format = '%(asctime)s %(levelname)-6s [%(filename)s:%(lineno)d] %(message)s'
    log_format = '%(asctime)s %(levelname)s [%(module)s] %(message)s'
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=log_format, datefmt='%H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    return logger

def dict_to_short_string(d:dict):
    return '(' + ','.join( f'{k}={v}' for k,v in d.items() if v is not None) + ')'

def to_hex_str(data):
    return " ".join(map(lambda b: hex(b)[2:], data))
    
async def enumerate_services(client: BleakClient, logger):
    for service in client.services:
        logger.info(f"[Service] {service}")
        for char in service.characteristics:
            if "read" in char.properties:
                try:
                    value = bytes(await client.read_gatt_char(char.uuid))
                    logger.info(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                    )
                except Exception as e:
                    logger.error(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}"
                    )

            else:
                value = None
                logger.info(
                    f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                )

            for descriptor in char.descriptors:
                try:
                    value = bytes(
                        await client.read_gatt_descriptor(descriptor.handle)
                    )
                    logger.info(f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                except Exception as e:
                    logger.error(f"\t\t[Descriptor] {descriptor}) | Value: {e}")

def get_logger(verbose=False):
    # log_format = '%(asctime)s %(levelname)-6s [%(filename)s:%(lineno)d] %(message)s'
    log_format = '%(asctime)s %(levelname)s [%(module)s] %(message)s'
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level, format=log_format, datefmt='%H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    return logger

def dict_to_short_string(d:dict):
    return '(' + ','.join( f'{k}={v}' for k,v in d.items() if v is not None) + ')'

def to_hex_str(data):
    return " ".join(map(lambda b: hex(b)[2:], data))

def calc_crc(message_bytes):
    return sum(message_bytes) & 0xFF

def read_str(buf, offset, encoding='utf-8'):
    return buf[offset:buf.index(0x00, offset)].decode(encoding=encoding)

def _jk_command(address, value: list):
    n = len(value)
    assert n <= 13, "val %s too long" % value
    frame = bytes([0xAA, 0x55, 0x90, 0xEB, address, n])
    frame += bytes(value)
    frame += bytes([0] * (13 - n))
    frame += bytes([calc_crc(frame)])
    
    #print (f'Comando .... address={address} - value={value} -- frame={frame} ')
    
    
    return frame

MIN_RESPONSE_SIZE = 300
MAX_RESPONSE_SIZE = 320

def print_c(eq):
    print()
    if eq[-1] =='1' : print(Fore.GREEN, end='')
    elif eq[-1] =='2' : print(Fore.YELLOW, end='')
    elif eq[-1] =='3' : print(Fore.BLUE, end='')
    elif eq[-1] =='4' : print(Fore.MAGENTA, end='')
    
################ CAPTURA DATOS #####################
async def leer(equipo):
    
    mac_address = BMS_JK[equipo]['MAC']
    
    conectar = BMS_JK[equipo]['usar']
    
    datos = {}
    nfallos = nfallos_ant = 0
    nconexiones = 1
    trecarga = time.time()
    contador_ciclos = 0
    
    Interruptores = {}
    flag_estado_interruptores = 0
                
    print_c(equipo)
    print (f'Iniciando equipo= {equipo}... MAC= {mac_address}')
     
    
    bms = JKBt(mac_address, name = equipo, verbose_log = False)
    
    # await bmslib.bt.bt_discovery(logger=get_logger())
    
    ##### MQTT ###########################################
    def on_connect(client, userdata, flags, rc):
        print(f"{equipo}....MQTT Conectado.... codigo {rc}")
        client.subscribe(f"PVControl/{equipo}")
        
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print (f"Desconexion MQTT de {equipo}... intentando reconexion")
        else:
            client.loop_stop()
            client.disconnect()

    def on_message(client, userdata, msg):
        nonlocal conectar, datos, Interruptores
        
        #if usar_telegram == 1: bot.send_chat_action(cid,'typing')
        
        cmd=msg.payload.decode().upper()
        print (Fore.CYAN + f'Comando {cmd} en equipo {equipo} recibido')
        
        # Comandos de interruptores
        for cd in comandos:
            print (f'Chequear {cmd} in {comandos[cd]}... tipo comando : {cd}')
            
            if cmd in comandos[cd]:
                if 'ON' in cmd:
                    print (f'Interruptor {cd} a ON')
                    Interruptores[cd] = True 
                    break
                
                elif 'OFF' in cmd:
                    print (f'Interruptor {cd} a OFF')
                    Interruptores[cd] = False
                    break
                
                elif cd == 'conectar':
                    print (f'CONECTAR {equipo}')
                    conectar = 1
                    break
                
                elif cd == 'desconectar':
                    print (f'DESCONECTAR {equipo}')
                    conectar = 0
                    break
                    
                elif cd == 'informacion':
                    print ('comando I en {equipo}')
                    respuesta = json.dumps(datos)
                    client.publish(f"PVControl/{equipo}/Respuesta",respuesta)
                    if usar_telegram == 1: 
                        L1 = f'Datos {equipo}=  {cmd}'
                        L2 = respuesta
                        tg_msg = L1+'\n'+L2
                        print_c(equipo)
                        print (tg_msg) 
                        bot_enviar_mensaje(cid, tg_msg)
                    break
                    
                elif cd == 'ayuda':
                    print(f'Comando ayuda recibido')
                    msg= ''
                    for c in comandos:
                        msg += f'{c:12} - comandos: {comandos[c]}\n\n' 
                    print (msg)
                    if usar_telegram == 1: bot_enviar_mensaje(cid, msg)
                    break
                    
    client = mqtt.Client(f"{equipo}") #crear nueva instancia
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(3,15)
    client.username_pw_set(mqtt_usuario, password=mqtt_clave)
    try:
        client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
    except:
        print(f'Error de conexion al servidor MQTT en {equipo}')
    time.sleep(.2)

    client.loop_start()  
    #######################################################
    
    
    try:
        async with bms:
            # Desconectarse antes de intentar la nueva conexion
            if bms.is_connected:
                await bms.disconnect()
                
            await bms.connect()  # Conectar al nuevo dispositivo BMS
            
            info = await bms.fetch_device_info()
            
            
            nceldas = bms.Nceldas # asignamos el numero de celdas que reporta el BMS
                        
            comprobar_bd(equipo, nceldas) # comprobamos/creamos tablas en BD
            
            
            Nombre_Celdas = ['C'] * nceldas 
            Vceldas = [0.0] * nceldas
            Vcelda_max = [0.0] * nceldas    # Maximo de cada celda diaria
            Vcelda_min = [1000.0] * nceldas # Minino de cada celda diaria
            CeldaMax = ('C1',0)
            CeldaMin = ('C1',1000)
            dia = time.strftime("%Y-%m-%d")
            AH_p = AH_n = 0.0 # amperios hora ciclados en el dia
            AH_p_ant = AH_n_ant = 0.0 # amperios hora ciclados ayer
            tcaptura = time.time() # marca tiempo para ver tiempo de ciclo
            
            for i in range(nceldas): Nombre_Celdas[i] = f'C{i+1}' 
            
            # Captura AH_p y AH_n desde el ultimo registro de BD
            try:
                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                cursor = db.cursor()
                Sql = f'SELECT * FROM datos_celdas_{equipo} LIMIT 1' 
                nreg=cursor.execute(Sql)
                
                sql= f"SELECT AH_p, AH_n, DATE(Tiempo) FROM datos_celdas_{equipo} ORDER BY id_celda DESC limit 1"
                 
                cursor.execute(sql)
                var = cursor.fetchone()
                fecha = str(var[2])
                
                if fecha == time.strftime("%Y-%m-%d"): #Comprueba que es el mismo dia
                    AH_p = float(var[0])
                    AH_n = float(var[1])
                else:
                    AH_p = AH_n = 0.0
                
            except:
                print('No hay registros en BD.. se inicializa AH_p = AH_n = 0.0')
                AH_p = AH_n = 0.0
                
                #sys.exit()
            cursor.close()
            db.close()
            
            print_c(equipo)            
            print(Style.BRIGHT+f' =========== DATOS BMS {"=" * 70}')
            print(f'  Nombre:{info.name} - Modelo:{info.model} - HW:{info.hw_version} - SW:{info.sw_version} - Nserie:{info.sn}')
            print(f'  Nceldas: {bms.Nceldas} - Capacidad:{bms.Capacidad}')
            print(f'  pass1: {info.pass1} - pass2:{info.pass2}')

            print(f'  OVP: {bms.OVP:.2f} - OVPR: {bms.OVPR:.2f} - UVPR: {bms.UVPR:.2f} - UVP: {bms.UVP:.2f} - Power_OFF:{bms.Power_OFF:.2f}')
            print(f' ======================={"=" * 70}')
            print(Style.RESET_ALL)
            #print(info)
            
            await asyncio.sleep(5) # tiempo para ver los datos
            
            ##### BUCLE ##########
            while True:  
                t_ciclo_ini = time.time() 
                ### --------------------- RECARGA Parametros_FV.py ----------------------
                
                if time.time()- trecarga > 300: # cada 300 sg
                    try:
                        trecarga = time.time()
                        exec(open(parametros_FV).read(),globals()) #recargo Parametros_FV.py por si hay cambios
                    except:
                        print (f'{equipo}: Error en carga Parametros_FV.py')
                    
                    #print_c(equipo)
                    #print (f' conexion {equipo}:{conectar}')
                    
                if BMS_JK[equipo]['usar'] == 0 or conectar == 0:
                    if bms.is_connected:
                        print (Fore.CYAN+f' Desconectando {equipo}.... ') 
                        await bms.disconnect()
                
                    await asyncio.sleep(10)
                    continue
                
                ### --------------------- LECTURA FECHA / HORA ----------------------
                tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
                tiempo_sg = time.time()
                diasemana = time.strftime("%w")
                hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
                dia_anterior = dia
                dia = time.strftime("%Y-%m-%d")
                
                ee='10'
                if dia_anterior != dia: #cambio de dia
                    Vcelda_max = [0.0] * nceldas 
                    Vcelda_min = [1000.0] * nceldas
                    CeldaMax = ('C1',0)
                    CeldaMin = ('C1',1000)
                    AH_p_ant = round(AH_p, 2)
                    AH_n_ant = round(AH_n, 2)
                    AH_p = AH_n = 0.0
                    nfallos_ant = nfallos
                    nfallos = 0
                
                try:
                    sample = await bms.fetch(wait=True)
                    t_muestra = time.time() - tcaptura # tiempo de ciclo de captura
                    tcaptura = time.time()
                    
                except:
                    nfallos += 1
                    print()
                    print (Fore.RED+f'{equipo}...Error captura datos  - nfallos={nfallos}')
                    print()
                    #if nfallos > 2 : #sys.exit()
                    
                    print (Fore.CYAN+'Intento de reconexion...')
                    
                    try:
                        if not bms.is_connected:
                            nconexiones += 1
                            
                            await asyncio.sleep(3)
                            await bms.connect()  # Conectar de nuevo dispositivo BMS
                    
                        info = await bms.fetch_device_info()
            
                        if DEBUG >= 1:
                            print_c(equipo)
                            print(' ======RECONEXION ===== DATOS BMS =========')
                            print(f'Nombre:{info.name} - Modelo:{info.model} - HW:{info.hw_version} - SW:{info.sw_version} - Nserie:{info.sn}')
                            #print(info)
                    except:
                        print(Fore.CYAN+f'{equipo}...NO ES POSIBLE CONECTAR.....')
                        await asyncio.sleep(5)
                        sys.exit()
                
                
                datos_ant = datos.copy()
                datos={}

                if DEBUG == 100:
                    print_c(equipo)
                    print (tiempo,f'dato {bms.name}:','=' * 40)
                    #print(f'dato {bms.name}:', sample)
                        
                datos['Vbat']= round(sample.voltage,2)
                datos['Ibat']= - round(sample.current,2)
                datos['SOC']= round(sample.soc,2)
                
                temperatures = sample.temperatures # or await bms.fetch_temperatures()
                datos['Temperaturas']= temperatures
                datos['Tmosfet'] = round(sample.mos_temperature,2)
                
                datos['Ibalance'] = round(sample.balance_current,2)
                
                datos['Tencendido'] = sample.uptime
                datos['Nciclos']= round(sample.num_cycles,2)
                datos['Ciclos'] = round(sample.cycle_capacity,2) # total charge TODO rename cycle charge
                datos['Capacidad_T'] = round(sample.capacity,2)  # computed capacity (starts at self.capacity, which is user-defined),
                datos['Capacidad_R'] = round(sample.charge,2) # "remaining capacity"
                
                if datos['Ibat'] > 0 :  AH_p += datos['Ibat'] * t_muestra/3600
                else:                   AH_n -= datos['Ibat'] * t_muestra/3600
                    
                datos['AH_p'] = round(AH_p,2)
                datos['AH_n'] = round(AH_n,2)
                
                datos['AH_p_ayer'] = AH_p_ant
                datos['AH_n_ayer'] = AH_n_ant
                
                datos['Nfallos'] = nfallos
                datos['Nfallos_ayer'] = nfallos_ant
                
                datos['Nconexiones'] = nconexiones
                
                
                datos['Interruptores'] = sample.switches
                
                if flag_estado_interruptores == 0:
                    for i in datos['Interruptores']: 
                        Interruptores[i] = datos['Interruptores'][i]
                    flag_estado_interruptores = 1
                
                for i in Interruptores:
                    if datos['Interruptores'][i] != Interruptores[i]:
                        print (f'{equipo}: Cambiando Interruptor {i} a {Interruptores[i]}')
                        try:
                            await bms.set_switch(i, Interruptores[i])
                            await asyncio.sleep(4)
                            msg = f'{equipo}: Interruptor {i} puesto a {Interruptores[i]}'
                        except:
                            await asyncio.sleep(4)
                            msg = f'{equipo}: Error en poner Interruptor {i} a {Interruptores[i]}'
                        msg = msg + f'\n{Interruptores}'
                        print(msg)
                        if usar_telegram == 1: bot_enviar_mensaje(cid, msg)
                                            
                
                #print(f"Soc:{s.soc}",f"Bateria:{s.voltage}","V",'I_bal=', s.balance_current,"Celdas:", await bms.fetch_voltages())
                #print(f"Soc :",s, 'I_bal=', s.balance_current, await bms.fetch_voltages())
                #new_state = not s.switches['charge']
                #await bms.set_switch('charge', new_state)
                #await bms._q(cmd=0x96, resp= 0x01)
                #print('set charge', new_state)
                #await asyncio.sleep(4)
                #s = await bms.fetch(wait=True)
                #print(s) 
                
                #print(f"Mosf_Temperatura : {s.mos_temperature}")
                #print(f"Temperatura : {s.temperatures}")
                
                
                #cell_voltages = await bms.fetch_voltages()
                
                #new_state = not sample.switches['discharge']
                #await bms.set_switch('discharge', new_state)


                Vceldas_mV = await bms.fetch_voltages()
                
                for i in range(nceldas): Vceldas[i] = round(Vceldas_mV[i]/1000,4)
                    
                datos['Vceldas']= Vceldas
                                

                ## Calculo valor minimo y maximo diario de cada celda y valor min/max de todas las celdas
                for K in range(nceldas):
                    K1 = f'C{K+1}'
                    
                    Vcelda_max[K] = round(max(Vcelda_max[K],Vceldas[K]),3)
                    Vcelda_min[K] = round(min(Vcelda_min[K],Vceldas[K]),3)
                    
                    if Vceldas[K] > CeldaMax[1]: CeldaMax = (K1,round(Vceldas[K],2))
                    if Vceldas[K] < CeldaMin[1]: CeldaMin = (K1,round(Vceldas[K],2))
                DifCeldas = round(max(Vceldas)- min(Vceldas),2)

                datos['Max']= Vcelda_max
                datos['Min']= Vcelda_min
                datos['Nombres']= Nombre_Celdas
                
                contador_ciclos += 1
                
                
                if DEBUG == 100: print(datos)         
                    
                if '-test' not in sys.argv: 

                    try:
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
                    except:
                        print('Error conexion BD')
                        sys.exit()
                    
                    try:
                        ####  ARCHIVOS RAM en BD ############ 
                        ee = 100
                        salida = json.dumps(datos)
                        ee = 110
                        
                        #print(salida)
                        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}', `sensores` = '{salida}' WHERE `id_equipo` = 'BMS_{equipo}'")
                        #print(sql)
                        cursor.execute(sql)
                        
                    except:
                        print('error, Grabacion tabla RAM equipos', ee)
                    
                    if contador_ciclos == BMS_JK[equipo]['ciclos_grabacion']: 
                        #await asyncio.sleep(3) # no entiendo este sleep???
                        
                        if DEBUG == 100: print(f'{equipo}...Grabando en BD...')
                               
                        # Insertar Registro en tabla datos_celdas
                        try:
                            ee = 120
                            campos = ",".join(Nombre_Celdas)
                            campos = 'Ibat, AH_p, AH_n, SOC, ' + campos
                            ee = 122
                            valores = "','".join(str(v) for v in Vceldas)
                            valores = f"'{datos['Ibat']}','{datos['AH_p']}','{datos['AH_n']}','{datos['SOC']}','{valores}'"
                            ee = 124
                            Sql = f"INSERT INTO datos_celdas_{equipo} ({campos}) VALUES ({valores})"
                            
                            #print(Sql)
                            
                            cursor.execute(Sql)
                            
                            ee = 126    
                            if DEBUG == 1:
                                if equipo[-1] =='1' : print(Fore.GREEN, end='')
                                elif equipo[-1] =='2' : print(Fore.YELLOW, end='')
                                elif equipo[-1] =='3' : print(Fore.BLUE, end='')
                                elif equipo[-1] =='4' : print(Fore.MAGENTA, end='')
                                print ('G',end='',flush=True)
                            
                        except:
                            print(f'error {ee} -  Grabacion tabla datos_celdas_{equipo}')
                             
                        
                        
                        contador_ciclos = 0  
                    
                    db.commit()
                    cursor.close()
                    db.close()
                
                t_ciclo = time.time() - t_ciclo_ini 
                espera = max(0.1, BMS_JK[equipo]['tiempo_captura'] - t_ciclo)
                await asyncio.sleep(espera)
                        
    except KeyboardInterrupt:
        print('Interrupción por CTRL+C')
    except:
        print(f'Interrupción por fallo lectura en {equipo}')
    finally:
        if bms.is_connected:
            await bms.disconnect()
    sys.exit()


async def main():
    
    tasks = []
    
    # Arrancando procesos
    for equipo in BMS_JK:
        if BMS_JK[equipo]['usar'] == 1:
            tasks.append(asyncio.create_task(leer(equipo)))
            await asyncio.sleep(5)
    
    await asyncio.gather(*tasks)

    #print ('except en main() de fv_jk')
    
    print()
    print(Fore.CYAN+'Finalizada captura BMS JK.....')
    print()
    
       
if __name__ == '__main__':
    asyncio.run(main())
    
