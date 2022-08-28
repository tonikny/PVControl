#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2022-08-20
#
#
import sys, time, datetime
import MySQLdb,json
import subprocess

import telebot # Librería de la API del bot.
import token

from pymodbus.client.sync import ModbusSerialClient

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando '+ Fore.GREEN + sys.argv[0]) #+Style.RESET_ALL)


#### Parametros_FV.py ##########
usar_deye = [1] 
dev_deye = ["/dev/ttyUSB0"]  # puerto donde reconoce la RPi al equipo
t_muestra_deye = [1]         # Tiempo en segundos entre muestras
con_bateria_deye = [0]            # Inversor con bateria = 1 , sin bateria = 0

grabar_datos_deye = [0]      # 1 = Graba la tabla deye.. 0 = No graba .... NO IMPLEMENTADO AUN
n_muestras_deye = [5]        # grabar en BD cada nmuestras .... NO IMPLEMENTADO AUN
usar_telegram = 1

# ###############################################
#Variables Script
can_e = 0 # Variable control cambio de estado
est_ant = '0' #estado anterior del inversor
# ##############################################


equipo = 'deye'
from Parametros_FV import *

if sum(eval(f'usar_{equipo}')) == 0:
    print (subprocess.getoutput(f'sudo systemctl stop fv_{equipo}'))
    sys.exit()

if usar_telegram == 1:
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages
    cid = Aut[0]
    bot.send_message(cid, f'Arrancando Programa Lectura DEYE')

#Comprobacion argumentos en comando
simular = DEBUG= 0
narg = len(sys.argv)
if '-p' in sys.argv: DEBUG= 1 # para desarrollo permite print en distintos sitios


#############################################################################
##### Script de captura cortesia de  Juan Andres Hernandez ##################
#############################################################################

version				=	"alpha-2022050201"	# Program Version
inverterConnection	=	ModbusSerialClient(method='rtu', port = dev_deye[0], baudrate=9600, timeout=3, parity='N', stopbits=1, bytesize=8)

dataSet				=	[0]*2				# Inverter Registers from 59 to 172 and from 173 to 284
dataSet1From		=	59
dataSet1Size		=	113
dataSet2From		=	dataSet1From+dataSet1Size
dataSet2Size		=	113

# Loop mode dumps data continuously
loopMode			=	True

# Time in seconds beteen readings in loop mode
highRateDataDelay	=	10			# 0 = Run continuously
lowRateDataEvery	=	5

# Classes
#

# Defines a simple register. A register may contain data from multiple addresses.
class Register:
	registerName = ""
	baseAddress = 0
	sizeOfRegister = 0
	multiplier = 0
	unit = 0

	def __init__(self, registerName, baseAddress, sizeOfRegister, multiplier, unit):
		self.registerName = registerName
		self.baseAddress = baseAddress
		self.sizeOfRegister = sizeOfRegister
		self.multiplier = multiplier
		self.unit = unit

	# Return the usable value of the register or "NotValid"
	def getData(self):
		dataSetIndex = -1
		returnValue = ""
		#print("Obteniendo dato de ",self.registerName)
		#print("Obteniendo dato del índice: ", self.baseAddress)
		if self.baseAddress < dataSet2From:
			dataSetIndex = 0
			registerIndex = self.baseAddress - dataSet1From
			#print("DataSet1From: ",dataSet1From)
		else:
			dataSetIndex = 1
			registerIndex = self.baseAddress - dataSet2From
			#print("DataSet2From: ",dataSet2From)

		#print("dataSetindex ", dataSetIndex)
		#print("registerIndex ", registerIndex)

		if dataSet[dataSetIndex].isError():
			returnValue = "NotValid"
		else:
			if self.sizeOfRegister == 1:
				#print("Dato con una dirección")
				returnValue = dataSet[dataSetIndex].registers[registerIndex]

				# Humanize Running State values.
				if self.baseAddress == 59:
					if returnValue == 0:
						returnValue = "Stand By"
					elif returnValue == 1:
						returnValue = "Self Checking"
					elif returnValue == 2:
						returnValue = "Normal"
					elif returnValue == 3:
						returnValue = "Fault"

				# Temperatures are calculated as data-1000 in register. 1000 = 0ºC. Add them on this list
				if self.baseAddress in [90, 91, 95, 182]:
					returnValue = returnValue - 1000
				# Some values are represented as signed int
				if self.baseAddress in [190, 191, 172]:
					if returnValue > 32767:
						#print(self.baseAddress)
						returnValue -= 65535
				returnValue *= self.multiplier

				# Humanize Grid Side Relay Status
				if self.baseAddress in [194]:
					if returnValue == 1:
						returnValue = "on"
					elif returnValue == 0:
						returnValue = "off"
					else:
						returnValue = "unknown"

				# Humanize Time of Use Selling
				if self.baseAddress == 248:
					if (returnValue & int("11111111",2)) == 0xFF:
						returnValue = "on"
					elif (returnValue & int("11111111",2)) == 0x00:
						returnValue = "off"
					# Time of Use Selling dumpt the time table too
					#returnValue = [returnValue, "linea 1", "linea 2", "linea 3", "linea 4", "linea 5", "linea 6" ]
					

				# Humanize Grid Mode
				if self.baseAddress == 284:
					if returnValue == 0:
						returnValue = "General_Standard"
					elif returnValue == 1:
						returnValue = "UL1741&IEE1547"
					elif returnValue == 2:
						returnValue = "CPUC_RULE21"
					elif returnValue == 3:
						returnValue = "SRD-UL1741"


			# 
			if self.sizeOfRegister == 2:
				#print("Datos con dos direcciones")
				#print("Primera palabra ",dataSet[dataSetIndex].registers[registerIndex])
				returnValue = dataSet[dataSetIndex].registers[registerIndex]
				nextAddress = 1
				# Some values are not in consecutive addresses. Add them on this list
				if self.baseAddress in [78]:
					#print("Dos registros no contínuos")
					nextAddress = 2
				# Values are usually in consecutive registers
				else:
					nextAddress = 1
					#print("Dos registros contínuos")

				#print("Segunda palabra ",dataSet[dataSetIndex].registers[registerIndex+nextAddress])
				returnValue += dataSet[dataSetIndex].registers[registerIndex+nextAddress] << 16
				returnValue *= self.multiplier

		if type(returnValue) == float:
			returnValue = round(returnValue, 2)
		return returnValue

class inverterData:
	# Name, First Address, Size in 16bit words, multiplier, unit
	EstadoInv				    =	Register("RunningState", 59, 1, 1, "")
	DayActivePower				=	Register("DayActivePower", 60, 1, 0.1, "kWh")
	TotalActivePower			=	Register("TotalActivePower", 63, 2, 0.1, "kWh")
	DayBattCharge				=	Register("DayBattCharge", 70, 1, 0.1, "kwh")
	DayBattDischarge			=	Register("DayBattDisCharge", 71, 1, 0.1, "kwh")
	TotalBatteryChargePower		=	Register("TotalBatteryChargePower", 72, 2, 0.1, "W")
	TotalBatteryDischargePower	=	Register("TotalBatteryDischargePower", 74, 2, 0.1, "W")
	DayGridBuyPower				=	Register("DayGridBuyPower", 76, 1, 0.1, "kWh")
	DayGridSellPower			=	Register("DayGridSellPower", 77, 1, 0.1, "kWh")
	TotalGridBuyPower			=	Register("TotalGridBuyPower", 78, 2, 0.1, "kWh")		# Registers 78 and 80 instead of 78 and 79
	TotalGridSellPower			=	Register("TotalGridSellPower", 81, 2, 0.1, "kWh")
	DayLoadPower				=	Register("DayLoadPower", 84, 1, 0.1, "kWh")
	TotalLoadPower				=	Register("TotalLoadPower", 85, 2, 0.1, "kWh")
	YearLoadPower				=	Register("YearLoadPower", 87, 2, 0.1, "kWh")
	RadiatorTempDC				=	Register("RadiatorTempDC", 90, 1, 0.1, "ºC")
	IGBTTemp					=	Register("IGBTTemp", 91, 1, 0.1, "ºC")
	Inductance1Temp				=	Register("Inductance1Temp", 92, 1, 0.1, "ºC")
	EnvironmentTemp				=	Register("EnvironmentTemp", 95, 1, 0.1, "ºC")
	HistPVPower					=	Register("HistPVPower", 96, 2, 0.1, "kWh")
	DayPVPower					=	Register("DayPVPower", 108, 1, 0.1, "kWh")
	Vplaca1					    =	Register("DCVoltage1", 109, 1, 0.1, "V")
	Iplaca1					    =	Register("DCCurrent1", 110, 1, 0.1, "A")
	Vplaca2					    =	Register("DCVoltage2", 111, 1, 0.1, "V")
	Iplaca2					    =	Register("DCCurrent2", 112, 1, 0.1, "A")
	Vred			            =	Register("GridSideVoltageL1N", 150, 1, 0.1, "V")
	LoadVoltageL1				=	Register("LoadVoltageL1", 157, 1, 0.1, "V")
	Wred		                =	Register("GridExternalTotalPower", 172, 1, 1, "W")
	Wconsumo			        =	Register("LoadSideTotalPower", 178, 1, 1, "W")
	Tbat			            =	Register("BatteryTemperature", 182, 1, 0.1, "ºC")
	Vbat				        =	Register("Vbat", 183, 1, 0.01, "V")
	BatteryCapacity				=	Register("BatteryCapacity", 184, 1, 1, "%")
	PV1InputPower				=	Register("PV1InputPower", 186, 1, 1, "W")
	PV2InputPower				=	Register("PV2InputPower", 187, 1, 1, "W")
	BatteryOutputPower			=	Register("BatteryOutputPower", 190, 1, 1, "w")
	Ibatn		                =	Register("BatteryOutputCurrent", 191, 1, 0.01, "A")
	GridSideRelayStatus			=	Register("GridSideRelayStatus", 194, 1, 1, "")			# 0=Disconnected ; 1=Connected
	TimeOfUseSelling			=	Register("TimeOfUSeSelling", 248, 1, 1, "")
	GridMode					=	Register("GridMode", 284, 1, 1, "")
	GridExternalLimeterCT1		=	Register("GridExternalLimeterCT1", 170, 1, 1,"w")  # no esta claro que es este parametro , en teoria la pontencia minima que consuma para asegurar el NO vertido
	#Ired		                =	Register("GridSideCurrentL1", 164, 1, 0.01, "A")
	Ired		                =	Register("GridExternalLimeterCurrentL1", 162, 1, 0.01, "A")
	Ired2		                =	Register("GridExternalLimeterCurrentL2", 163, 1, 0.01, "A")
	GrideSideL1P   =	Register("GrideSideL1P", 172, 1, 1, "W")
	GrideSideL2P   =	Register("GrideSideL1P", 170, 1, 1, "W")
#
#
# returns:
#		 0 = All Registers
#		 1 = Some registers not readed
#		-1 = No register could be read
#

def readInverterData():
	global dataSet
	global inverterConnection
	#global dataSet2
	returnValue = -1
	dataSet1Readed = False
	dataSet2Readed = False

	#print(inverterConnection.is_socket_open())

	try:
		# Am I already connected
		if inverterConnection.is_socket_open() == False:
		#	print("Conectando al Inversor")
			inverterConnection.connect()  # Trying for connect to Modbus Server/Slave
		#else:
		#	print("Ya estoy connectado al inversor")

		if inverterConnection.is_socket_open():
			dataSet[0] = inverterConnection.read_holding_registers(address=dataSet1From, count=dataSet1Size, unit=1)
			if not dataSet[0].isError():
				#print("Primer lote leído.")
				dataSet1Readed = True
			else:
				dataSet1Readed = False

			dataSet[1] = inverterConnection.read_holding_registers(address=dataSet2From, count=dataSet2Size, unit=1)
			if not dataSet[1].isError():
				#print("Segundo lote leído.")
				dataSet2Readed = True
			else:
				dataSet2Readed = False

			if dataSet1Readed == True or dataSet2Readed == True:
				returnValue = 0
			else:
				returnValue = 1

			#inverterConnection.close()

		else:
			print('Cannot create modbus connection')
			returnValue = -1

	except IOError:
		print("Error reading from the inverter")
	except ValueError:
		print("Inverter response is invalid")
	except:
		print("An exception ocurred")
	
	return returnValue



# Comprobacion BD

n_muestras_contador = [1 for i in range(len(eval(f'usar_{equipo}')))] # contadores grabacion BD

try:
    ee = '10'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()
    
    for i in range(len(eval(f'usar_{equipo}'))):
        ee = '10a'    
        if eval(f'usar_{equipo}[{i}]') == 1:
            if i==0: N_Equipo = ""
            else: N_Equipo = f"{i}"
            try: #inicializamos registro RAM en BD 
                ee = '10b'
                cursor.execute("""INSERT INTO equipos (id_equipo,sensores) VALUES (%s,%s)""",
                              (equipo.upper()+ N_Equipo ,'{}'))   
                db.commit()
            except:
                pass             
                                
except:
    print (Fore.RED,f'ERROR {ee} - inicializando BD RAM')
    sys.exit()


def logBD(msg) : # Incluir en tabla de Log
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,msg))
        #print (tiempo,' ', msg)
        db.commit()
    except:
        db.rollback()
    
    return


def leer_equipo(equipo,I_Equipo):
    global n_muestras_contador, dataReadResult, can_e, est_ant
    
    if I_Equipo == 0: N_Equipo = ""
    else: N_Equipo = f"{I_Equipo}"

    datos= {} # Diccionarios datos
    
    try:
        dataReadResult = readInverterData() 
    
        datos['WplacaST1'] = inverterData.PV1InputPower.getData()
        datos['WplacaST2'] = inverterData.PV2InputPower.getData()
        datos['EstadoInv'] = inverterData.EstadoInv.getData()
        datos['IGBTTemp'] = inverterData.IGBTTemp.getData()
        datos['Vplaca1'] = inverterData.Vplaca1.getData()
        datos['Iplaca1'] = inverterData.Iplaca1.getData()
        datos['Vplaca2'] = inverterData.Vplaca2.getData()
        datos['Iplaca2'] = inverterData.Iplaca2.getData()
        datos['Vred'] = inverterData.Vred.getData()
        #datos['LoadVoltageL1'] = inverterData.LoadVoltageL1.getData()
        datos['Wred'] = -(inverterData.Wred.getData())
        datos['Wconsumo'] = inverterData.Wconsumo.getData()
        #datos['TotalActivePower'] = inverterData.TotalActivePower.getData()       
        #datos['DayPVPower'] = inverterData.DayPVPower.getData()
        datos['Wplaca'] = datos['WplacaST1'] + datos['WplacaST2']
        #datos['Iplaca'] = (datos['Iplaca1'] + datos['Iplaca2'])/2 # Revisar que sea correcto
        #datos['Vplaca'] = datos['Wplaca'] / datos['Iplaca'] # Revisar que sea correcto
        datos['Vplaca'] = (datos['Vplaca1'] + datos['Vplaca2'])/2 # Revisar que sea correcto
        datos['Iplaca'] = datos['Wplaca'] / datos['Vplaca'] # Revisar que sea correcto
        if datos['Wred'] < 0:
            datos["Ired"] = -(inverterData.Ired.getData())
        else:
            datos["Ired"] = (inverterData.Ired.getData())
        #datos["Ired2"] = inverterData.Ired2.getData()
        
        if eval(f'con_bateria_deye{N_Equipo}[{I_Equipo}]') == 1:
            datos['BatteryOutputPower'] = inverterData.BatteryOutputPower.getData()
            datos['Vbat'] = inverterData.Vbat.getData()
            datos['Tbat'] = inverterData.Tbat.getData()
            datos['Ibatn'] = inverterData.Ibatn.getData()
            

    except:
        print (Fore.RED + 'ERROR EN CAPTURA DATOS DEYE')
        
    try:
        if usar_telegram_deye[I_Equipo] == 1:
            ee = '25a'
            if can_e == 0:
                ee = '25b'
                L1 = f"Estado inversor{N_Equipo}: {datos['EstadoInv']}" 
                can_e = 1
                est_ant = str(datos['EstadoInv'])
                tg_msg = L1
                ee = '25c'
                print (tg_msg) 
                bot.send_message(cid, tg_msg)
                     
            if est_ant !=  str(datos['EstadoInv']):
                ee = '25d'
                can_e = 0
                print("Cambio variable can_e: " + str(can_e))
                logBD('Estado inversor DEYE: '+ str(datos['EstadoInv'])) # incluyo mensaje en el log
    except:
        logBD(' Fallo en script DEYE en el punto '+str(ee)) # incluyo mensaje en el log
        
        
     
    if DEBUG == 1:
        for i in datos: print(f'{i}= {datos[i]}')    

    
    try:####  ARCHIVOS RAM en BD ############ 
        ee = '40'
        tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
        salida = json.dumps(datos)
        sql = (f"UPDATE equipos SET `tiempo` = '{tiempo}',sensores = '{salida}' WHERE id_equipo = '{equipo.upper()}{N_Equipo}'") # grabacion en BD RAM
        #print (Fore.RED+sql)
        cursor.execute(sql)
        #db.commit()
    except:
        print(Fore.RED+f'error, Grabacion tabla RAM equipos en {equipo.upper()}{N_Equipo}')
    

    if eval(f'grabar_datos_{equipo}[{I_Equipo}]') == 1: 
        ee = '50'
        try:
            # Insertar Registro en BD
            if n_muestras_contador[I_Equipo] == 1:
                ee = '50a'
                datos['Tiempo'] = tiempo
                
                #del Datos['Ibat'] # se quitan las claves que no estan en tabla BD
                
                campos = ",".join(datos.keys())
                valores = "','".join(str(v) for v in datos.values())
                
                # PENDIENTE
                if DEBUG == 1: print (tiempo,' No se graba tabla por ahora')
                """
                Sql = f"INSERT INTO {equipo}{N_Equipo} ("+campos+") VALUES ('"+valores+"')"
                #print (Fore.RESET+Sql)
                cursor.execute(Sql)
                print (Fore.RED+'G'+N_Equipo,end='/',flush=True)
                db.commit()
                """
                
                
                ee = '50d'
            
            if n_muestras_contador[I_Equipo] >= eval(f'n_muestras_{equipo}[{I_Equipo}]'):
                n_muestras_contador[I_Equipo] = 1
            else:
                n_muestras_contador[I_Equipo] +=1                   
        except:
            db.rollback()
            print (f'Error {ee} grabacion tabla {equipo}{N_Equipo}')
            
    db.commit()


while True:
    try:
        for i in range(len(eval(f'usar_{equipo}'))):
            if eval(f'usar_{equipo}[{i}]') == 1:
                if i==0: N_Equipo = ""
                else: N_Equipo = f'{i}'
                
                if int(time.time()) % eval(f't_muestra_{equipo}[{i}]') == 0: leer_equipo(equipo,i)
                    
    except:
        print ('Error desconocido....')
        sys.exit()
    
    time.sleep(1)


