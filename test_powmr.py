#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Versión 2024-05-19
#
################### PARAMETROS CONEXION ############
dev = '/dev/ttyUSB0'
baudrate = 2400
id_modbus = 5
####################################################

######### REGISTROS LECTURA ########################
"""
Original WiFi dongle sends two requests every few seconds to monitor inverter state.

read 45 registers (func 3) from slave 5 starting from address 4501 (Decimal) (raw: 05031195002d9143)
read 16 registers (func 3) from slave 5 starting from address 4546 (Decimal) (raw: 050311c20010e142)
Please refer wifi bridge code for state registers description.
"""
reg = {
    'Wplaca1': 4563,
    'Wplaca2': 4564,
    
    }

reg = {
    'Sprio': 4501,
    'Vac': 4502,
    'Fac': 4503,
    'Vplaca1': 4504,
    'Wplaca1': 4505,
    'Vbat': 4506,
    'SOC' : 4507,
    'Icarga':4508,
    'Idescarga':4509,
    'Vac_out':4510,
    'Fac_out':4511,
    'Wconsumo':4512,
    'Wconsumo_VA':4513,
    'Wconsumo_%':4514,
    'Wconsumo_%2':4515,
    'Flags_4516':4516,
    
    '4517':4517,
    '4518':4518,
    '4519':4519,
    '4520':4520,
    '4521':4521,
    '4522':4522,
    '4523':4523,
    '4524':4524,
    '4525':4525,
    '4526':4526,
    '4527':4527,
    '4528':4528,
    '4529':4529,
    
    'Error_code':4530,
    
    '4531':4531,
    '4532':4532,
    '4533':4533,
    '4534':4534,
    
    'Flags_4535':4535,
    'Carga_prio':4536,
    'Source_prio':4537,
    'AC_Input_range':4538,
    
    '4539':4539,
    
    'Fac_out_target':4540,
    
    '4541':4541,
    '4542':4542,
    
    'Carga_max_util':4543,
    'Vbat_back_utility':4544,
    'Vbat_back_battery':4545,
    'Vabs':4546,
    'Vflot' : 4547,
    'Vbat_cutoff':4548,
    'Vequ':4549,
    'Vequ_time':4550,
    'Vequ_timeout':4551,
    'Vequ_intervalo':4552,
    'Flags_4553':4553,
    'Flags_4554':4554,
    'Carga_estado':4555,
    
    '4556':4556,
    
    'Temp_Placas':4557,
    
    'Wplaca':4558,
    '4559':4559,
    '4560':4560,
    '4561':4561,
    '4562':4562,
    'Vplaca2':4563,
    'Wplaca2':4564,
    
    '5001':5001,
    '5002':5002,
    '5003':5003,
    '5004':5004,
    '5005':5005,
    '5006':5006,
    '5007':5007,
    '5008':5008,
    '5009':5009,
    '5010':5010,
    '5011':5011,
    '5012':5012,
    '5013':5013,
    '5014':5014,
    '5015':5015,
    '5016':5016,
    '5017':5017,
    '5018':5018,
    '5019':5019,
    
}


####################################################

""" Read registers
4501 : Output Source Priority (Returns index with offset. I'd prefer to use register 4537) settings
4502 : AC Voltage measurement
4503 : AC Frequency measurement
4504 : PV Voltage (?) measurement
4505 : Charging (right now) settings
4506 : Battery Voltage measurement
4507 : Battery SoC measurement
4508 : Battery Charge Current measurement
4509 : Battery Discharge Current measurement
4510 : Load Voltage measurement
4511 : Load Frequency measurement
4512 : Load Power measurement
4513 : Load VA measurement
4514 : Load Percent measurement
4515 : Load Percent measurement
4516 : Binary flags binary_flags
0x100 Something overload related (?)
4530 : Error Code
4535 : Settings binary flags binary_flags
0x1 Record Fault Code settings
0x2 Battery Equalization settings
0x4 Equalization Activated Immediately settings
0x100 Alarm settings
0x400 Backlight settings
0x800 Restart On Overload settings
0x1000 Restart On Overheat settings
0x2000 Beep On Primary Source Fail settings
0x4000 Return To Default Screen settings
0x8000 Overload Bypass settings
4536 : Charger Source Priority settings
4537 : Output Source Priority (More correct one) settings
4538 : AC Input Voltage Range settings
4540 : Target Output Frequency settings
4541 : Max Total Charging Current settings
4542 : Target Output Voltage settings
4543 : Max Utility Charging Current settings
4544 : Back To Utility Source Voltage settings
4545 : Back To Battery Source Voltage settings
4546 : Bulk Charging Voltage settings
4547 : Floating Charging Voltage settings
4548 : Low CutOff Voltage settings
4549 : Battery Equalization Voltage settings
4550 : Battery Equalized Time settings
4551 : Battery Equalized Timeout settings
4552 : Equalization Interval settings
4553 : Binary flags binary_flags
0x100 On Battery
0x200 AC Active
0x1000 Load Off (Inverted "Load Enabled")
0x2000 AC Active
0x4000 Load Enabled
4554 : Binary flags binary_flags
0x1 On Battery
0x100 AC Active
0x8000 AC Active
4555 : Charger Status (0 - Off, 1 - Idle, 2 - Active)
4557 : Temperature sensor (HVM3.6M confirmed, HVM2.4H not confirmed)


Write registers

Register	Description	HVM2.4H
5002	Buzzer Alarm (range 0-1, settings menu 18)	+
5004	Backlight control (range 0-1, settings menu 20)	
5005	Auto restart when overload occurs (range 0-1, settings menu 6)	
5006	Auto restart when over temperature occurs (range 0-1, settings menu 7)	
5007	Beep On Primary Source Fail (range 0-1, settings menu 22)	+
5008	Auto return to default display screen (range 0-1, settings menu 19)	
5009	Overload Bypass (0-1, settings menu 23)	+
5010	Record fault code (range 0-1, settings menu 25)	
5017	Charger Source Priority (range 0-3, settings menu 16)	+
5018	Output Source Priority (range 0-2, settings menu 1)	+
5019	AC input voltage range (range 0-1, settings menu 3) (0 - 90-280VAC, 1 - 170-280VAC)	
5020	Battery type (range 0-2, settings menu 5)	
5021	Output frequency (range 0-1, settings menu 9) (0 - 50hz, 1 - 60hz)	
5022	Max Total Charge Current (range 10-80, settings menu 2)	+
5023	Output voltage (one of 220, 230, 240, settings menu 10)	
5024	Utility Charge Current (one of 2, 10, 20, 30, 40, 50, 60, settings menu 11)	+
5025	Comeback Utility Mode Voltage (SBU) (0.5 volts step, settings menu 12)	
5026	Comeback Battery Mode Voltage (SBU) (0.5 volts step, settings menu 13)	
5027	Bulk charging voltage (settings menu 26)	
5028	Floating charging voltage (settings menu 27)	
5029	Low DC cut-off voltage (settings menu 29)	
5030	Battery equalization voltage (settings menu 31)	
5031	Battery equalized time (settings menu 33)	
5032	Battery equalized timeout (settings menu 34)	
5033	Equalization interval (settings menu 35)

"""


import sys, time
import minimalmodbus

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()

print (Style.BRIGHT + Fore.YELLOW + 'Arrancando  '+ Fore.GREEN + sys.argv[0])

sim = 1 if '-s' in sys.argv else 0 # simulacion


# CONEXION
if sim == 0:
    modbus = minimalmodbus.Instrument(dev, id_modbus)
    modbus.serial.baudrate = baudrate
    modbus.serial.bytesize = 8
    modbus.serial.parity = minimalmodbus.serial.PARITY_NONE
    modbus.serial.stopbits = 1
    modbus.serial.timeout = 3
    modbus.debug = False
    modbus.mode = minimalmodbus.MODE_RTU
    
    
    if '-d' in sys.argv: modbus.debug = True
else:
    print('Modo simulado')

# BUCLE
while True:
    print()
    print(Fore.RED + time.strftime("%Y-%m-%d %H:%M:%S") + Fore.RESET + '  ' + '#' * 80)
    for r in reg:
        try:
            d = modbus.read_registers(reg[r], 1, 3) if sim == 0 else 9999
            time.sleep(0.1)
        except:
            d = Fore.RED+'Error'+ Fore.RESET
    
        #raw_bytes = bytearray()
        #raw_bytes.extend(reg.to_bytes(2, byteorder='big'))  # Cambia 'big' a 'little' si el dispositivo utiliza little-endian
        try:
           if int(reg[r]/1000)==4:
               d= int.from_bytes(d[0].to_bytes(2, byteorder='little'))
            
        except:
            print(Fore.RED + f"Registro {reg[r]}...ERROR.... {r} ")
            continue
        print(Fore.GREEN + f"Registro {reg[r]}...{r} = {d}")
        
    #sys.exit()        
    time.sleep(1)
