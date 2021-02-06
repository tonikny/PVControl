#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Versión 2021-02-06

# ----------------------------------------------------------------------------------------------
#### Este Programa NO importa los datos de Parametros_FV.py por lo que ES NECESARIO dar de alta
#### los datos de la instalacion FV .... SHUNT1, SHUNT2, RES0,...
# ----------------------------------------------------------------------------------------------

# Usar desde linea de comandos con opciones -Vbat, -Ibat, -I, -V, o sin opcion  
# PARAR antes de usarlo el servicio fv con .... sudo systemctl stop fv y reiniciarlo tras su uso

#       python3 TEST_ADS1115.py    
#       python3 TEST_ADS1115.py -Vbat
#       python3 TEST_ADS1115.py -CVbat  (modo continuo en ADS)
#       python3 TEST_ADS1115.py -V
#       ......    

# desde carpeta /home/pi/PVControl+ 

# -----------------------------------------
#      PARAMETROS INSTALACION 
# -----------------------------------------
SHUNT1 = 100.0/75 #Shunt Ibat  A/mV
SHUNT2 = 100.0/75 #Shunt Iplaca A/mV
I_gain = 16 # Fondo escala 1=4,096 - 2=2,048 - 4=1,024 - 8=0,512   - 16=0,256

#Vbat
RES0 = (68+1.5)/1.5 * 12.63/12.33     # Divisor tension Vbat
RES0_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#Vaux
RES1 = (68+1.5)/1.5 * 12/12     # Divisor tension Vaux
RES1_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#Vplaca
RES2 = (68+1.5)/1.5 * 48/48     # Divisor tension Vplaca
RES2_gain = 2                   # Fondo escala 1=4,096 - 2=2.048
#V...
RES3 = (68+1.5)/1.5 * 48/48     # Divisor tension ....
RES3_gain = 2                   # Fondo escala 1=4,096 - 2=2.048


###############################################################################################

import time,sys 
import RPi.GPIO as GPIO
from smbus import SMBus
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import colorama # colores en ventana Terminal
from colorama import Fore, Back, Style
colorama.init()


bus = SMBus(1) #Rpi rev.B
GPIO.setmode(GPIO.BOARD)


###### Alta ADS1115 ADC (16-bit).
  #adc con pin addr a GND
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

  #adc con pin addr a 3V3
adc1 = Adafruit_ADS1x15.ADS1115(address=0x4b, busnum=1) 

#################################################################
######## Bucle para ajustar Parametros Vbat, Ibat, Iplaca #######
#################################################################

#Comprobacion argumentos en comando de fv.py
narg = len(sys.argv)
if str(sys.argv[narg-1]) == '-Vbat':
    MODO = 'Vbat'
elif str(sys.argv[narg-1]) == '-CVbat':
    MODO = 'CVbat'
elif str(sys.argv[narg-1]) == '-Ibat':
    MODO = 'Ibat'
elif str(sys.argv[narg-1]) == '-V':
    MODO = 'V'
elif str(sys.argv[narg-1]) == '-I':
    MODO = 'I'
else:
    MODO = 'NORMAL'


print (Style.BRIGHT + Fore.YELLOW + 'Arrancando'+ Fore.GREEN +' TEST ADS1115') #+Style.RESET_ALL)
print(Fore.GREEN+'MODO ='+MODO)
print()
print(Fore.RED+'Pulsa Ctrl-C para salir...')
print()
print(Fore.GREEN+f'Ganancia Ibat/Iplaca= {I_gain}  -- SHUNT1/SHUNT2= {SHUNT1:.2}/{SHUNT2:.2}',)
print(f'Ganancias Vbat/Vaux1/Vplaca/Vaux2 = {RES0_gain}/{RES1_gain}/{RES2_gain}/{RES3_gain}')
print (Fore.RESET)



if MODO == 'Vbat':
    N = 40
    rate = 250
    while True:
        try:
            #### Vbat
            t1 = time.time()
            L_Vbat = [adc.read_adc(0, gain= RES0_gain, data_rate = rate) for i in range(N) ]
            t2 = time.time() -t1
            
            Max = max(L_Vbat)
            Min = min(L_Vbat)
            MED = sum(L_Vbat)/N
                        
            Vbat = round(MED* 0.000125 * RES0 / RES0_gain ,4)
            Vbat_err=  round((Max-Min) * 0.000125 * RES0 / RES0_gain ,2)
            
            L_Vbat_ord = L_Vbat.copy()
            L_Vbat_ord.sort()
            
            L_Vbat_dif = [L_Vbat_ord[i+1]-L_Vbat_ord[i] for i in range(len(L_Vbat_ord)-1)]
            L_Vbat_dif = [i for i in L_Vbat_dif if i != 0]
            L_Vbat_dif.sort()
            
            #print (L_Vbat)
            #print (L_Vbat_ord)
            #print (L_Vbat_dif)
            
            print (Fore.GREEN+'Vbat='+ Fore.RESET+f'{Vbat:.4}V'+ Fore.RED+ ' Error='+Fore.RESET,
                   f'{Max}/{Min}(',round((Max-Min)* 0.125 / RES0_gain,2),'mV ADS)-'+
                   Fore.RED+'(',round((Max-Min)* 0.125 * RES0 / RES0_gain,2) ,'mV conector)', end='')
            
            print ( Fore.GREEN,f'T.Ejec en {N}ciclos/rate={rate} = {t2:.3}', end='')
            if len(L_Vbat_dif) > 0:
                if L_Vbat_dif[0] < 16: print (Fore.GREEN,'-- ADS1115')
                else:                  print (Fore.RED,'-- ADS1015')
            else:                      print (Fore.BLUE,'-- ??')
        except:
            print ('Error ADS 1 - A0')
        
        time.sleep(0.2)
        

elif MODO == 'CVbat':
    N = 100
    rate = 860
    L_Vbat = ([0.0] * N)
    #adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)

    adc.start_adc(0, gain=RES0_gain, data_rate=rate) #8,16,32,64,128,250,475,860
                                                 # start_adc_difference() para diferencial
    while True:
        try:
            #### Vbat
            t1 = time.time()
            for i in range(N):
                L_Vbat[i] = adc.get_last_result() 
                time.sleep (1/rate)   
            t2 = time.time() -t1
            
            Max = max(L_Vbat)
            Min = min(L_Vbat)
            MED = sum(L_Vbat)/N
                        
            Vbat = round(MED* 0.000125 * RES0 / RES0_gain ,4)
            Vbat_err=  round((Max-Min) * 0.000125 * RES0 / RES0_gain ,2)
            
            L_Vbat_ord = L_Vbat.copy()
            L_Vbat_ord.sort()
            #L_Vbat_dif = []
            #for i in range(len(L_Vbat_ord)-1):
            #    L_Vbat_dif.append (L_Vbat_ord[i+1]-L_Vbat_ord[i])
            
            L_Vbat_dif = [L_Vbat_ord[i+1]-L_Vbat_ord[i] for i in range(len(L_Vbat_ord)-1) ]
            
            L_Vbat_dif_red = [i for i in L_Vbat_dif if i != 0]
            L_Vbat_dif_red.sort()
            
            L_Vbat_v = [ round(i * 0.000125 * RES0/ RES0_gain, 3) for i in L_Vbat ]
            
            print (L_Vbat_v)
            print ('-' * 50)
            #print (L_Vbat_ord)
            #print ('-' * 50)
            print (L_Vbat_dif)
            #print (L_Vbat_dif_red)
            
            print (Fore.GREEN+'Vbat='+ Fore.RESET+f'{Vbat}V'+ Fore.RED+ ' Error='+Fore.RESET,
                   f'{Max}/{Min}(',round((Max-Min)* 0.125 / RES0_gain,2),'mV ADS)-'+
                   Fore.RED+'(',round((Max-Min)* 0.125 * RES0 / RES0_gain,2) ,'mV conector)', end='')
            
            print ( Fore.GREEN,f'T.Ejec en {N}ciclos/rate={rate} = {t2:.3}', end='')
            if len(L_Vbat_dif_red) > 0:
                if L_Vbat_dif_red[0] < 16: print (Fore.GREEN,'-- ADS1115')
                else:                  print (Fore.RED,'-- ADS1015')
            else:                      print (Fore.BLUE,'-- ??')
        except:
            print ('Error ADS 1 - A0')
        
        time.sleep(0.2)
        

elif MODO == 'V':
    print(Fore.YELLOW+'LECTURA ADS 1 =')
    print()
    
    N = 20
    while True:
        try:
            Suma1 = Suma2 = Suma3 = Suma4 =0
            for i in range(N):
                l1 = adc.read_adc(0, gain=1)
                l2 = adc.read_adc(1, gain=1)
                l3 = adc.read_adc(2, gain=1)
                l4 = adc.read_adc(3, gain=1)
                Suma1 += l1
                Suma2 += l2
                Suma3 += l3
                Suma4 += l4
            ADS1 = Suma1/N   
            ADS2 = Suma2/N   
            ADS3 = Suma3/N   
            ADS4 = Suma4/N   
            V1 = round(ADS1* 0.000125 * RES0 ,2)
            V2 = round(ADS2* 0.000125 * RES1 ,2)
            V3 = round(ADS3* 0.000125 * RES2 ,2)
            V4 = round(ADS4* 0.000125 * RES3 ,2)
    
            print (Fore.GREEN+'Vbat=',Fore.RESET,V1,'V / ',end='')
            print (Fore.GREEN+'Vaux1=',Fore.RESET,V2,'V / ',end='')
            print (Fore.GREEN+'Vplaca=',Fore.RESET,V3,'V / ',end='')
            print (Fore.GREEN+'Vaux2=',Fore.RESET,V4,'V')
            
        except:
            print ('Error ADS 1')
        
        time.sleep(0.2)

elif MODO == 'I':
    print(Fore.YELLOW+'LECTURA ADS 4 =')
    print()
    
    N = 20
    while True:
        try:
            Suma1 = Suma2 = 0
            for i in range(N):
                l1 = adc1.read_adc_difference(0, gain=I_gain, data_rate=64)
                Suma1 += l1
            ADS1 = Suma1 / N    
            
            for i in range(N):
                l2 = adc1.read_adc_difference(3, gain=I_gain, data_rate=64)
                Suma2 += l2
            ADS2 = Suma2 / N   
            V1 = round(ADS1 * 0.125 * SHUNT1 / I_gain ,2)
            V2 = round(ADS2 * 0.125 * SHUNT2 / I_gain, 2)
            
            print (Fore.GREEN+'Ibat=',Fore.RESET,V1,'A / ',end='')
            print (Fore.GREEN+'Iplaca=',Fore.RESET,V2,'A')
            
        except:
            print ('Error ADS 4')
        
        time.sleep(0.2)

elif MODO == 'Ibat':
    N = 20
    while True:
        try:
            #### Ibat
            Suma = 0
            Max = -40000
            Min = 40000
            for i in range(N):
                l = adc1.read_adc_difference(0, gain=I_gain, data_rate=64)
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            ADS = Suma/N    
            Ibat = round(ADS* 0.125 * SHUNT1 / I_gain ,2)
            Ibat_err=  round((Max-Min) * 0.125 * SHUNT1 / I_gain ,2)
            
            print (Fore.GREEN+'Ibat=',Fore.RESET,Ibat,'Ibat '+ Fore.RED+ 'Error=',Fore.RESET,
                   Max,'/',Min,'(',round((Max-Min)* 0.125 / I_gain,2),'mV en ADS)-',
                   Fore.RED,'(',round((Max-Min)* 0.125 * SHUNT1 / I_gain,2) ,'A en Shunt1)')
        except:
            print ('Error ADS 4 - A0-A1')
    
        time.sleep(0.2)

    
    
    """
    while True:
        try:
            Suma = 0
            Max = -40000
            Min = 40000
            t1= time.time()
            
            for i in range(N):
                x1 = x2 = 0
                while x1 == 0 or x2 < 100:
                    l = adc1.read_adc_difference(0, gain=I_GAIN, data_rate=64)
                    if abs(l) < 30000: x = 1 #; print('x')
                    x2 += 1
                    
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            t2= time.time()
            
            ADS = Suma/N    
            V = round(ADS * Ratio * SHUNT1,2)
            Vmax= max(Vmax,V)
            Vmin= min(Vmin,V)
            
            
            mV = round(ADS * Ratio,2)
            
            
            
            
            print (round (t2-t1,2),Fore.GREEN+'Ibat=',Fore.WHITE,V,'A',Fore.GREEN+'mV=',
                   Fore.RESET,mV, Fore.RED+ 'Error=',Fore.RESET,
                   Max,'/',Min,'(',round((Max-Min)* Ratio ,2),'mV en ADS)-',
                   Fore.RED,'(',round((Max-Min)* Ratio * SHUNT1 ,2) ,'A en conector)-En medida=',
                   round(Vmax-Vmin ,2), 'A')
            
        except:
            print ('Error ADS 4 - A0_A1')
    """


elif MODO == 'NORMAL':
    N=20
    while True:
        try:
            #### Vbat
            Suma = 0
            Max = -40000
            Min = 40000
            for i in range(N):
                l = adc.read_adc(0, gain= RES0_gain)
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            ADS = Suma/N    
            Vbat = round(ADS* 0.000125 * RES0 / RES0_gain ,2)
            Vbat_err=  round((Max-Min) * 0.000125 * RES0 / RES0_gain ,2)
            
            ee='N20'
            #### Vaux1
            ADS = adc.read_adc(1, gain=RES1_gain)
            Vaux1 = round(ADS* 0.000125 * RES1 / RES1_gain ,2)
            
            ee='N30'
            #### Vplaca
            ADS = adc.read_adc(2, gain=RES2_gain)
            Vplaca = round(ADS* 0.000125 * RES2 / RES2_gain ,2)
            
            ee='N40'            
            #### Vaux2
            ADS = adc.read_adc(3, gain=RES3_gain)
            Vaux2 = round(ADS* 0.000125 * RES3 / RES3_gain ,2)
        except:
            Vbat = Vaux1 = Vplaca = Vaux2 = Vbat_err = -99
        
        try:    
            ee='N50'
            #### Ibat
            Suma = 0
            Max = -40000
            Min = 40000
            for i in range(N):
                l = adc1.read_adc_difference(0, gain=I_gain, data_rate=64)
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            ADS = Suma/N
            #print ('Ibat=',ADS, Max, Min, Max-Min)
            Ibat = round(ADS* 0.125 * SHUNT1 / I_gain ,2)
            Ibat_err=  round((Max-Min) * 0.125 * SHUNT1 / I_gain ,2)
            
            ee='N60'
            #### Iplaca
            Suma = 0
            Max = -40000
            Min = 40000
            for i in range(N):
                l = adc1.read_adc_difference(3, gain=I_gain, data_rate=64)
                Suma += l
                Max = max(Max,l)
                Min = min(Min,l)
            ADS = Suma/N
            #print ('Iplaca=',ADS, Max, Min, Max-Min)
            Iplaca = round(ADS* 0.125 * SHUNT2 / I_gain ,2)
            Iplaca_err=  round((Max-Min) * 0.125 * SHUNT2 / I_gain ,2)
            
        except:
            Ibat = Ibat_err = Iplaca = Iplaca_err = -99
        try:    
            ee='N80'
            
            print(Fore.GREEN+'Vbat='+Fore.WHITE,'{0:>5}'.format(Vbat), end='')
            print(Fore.GREEN+'| Ibat='+Fore.WHITE,'{0:>6}'.format(Ibat), end='')
            print(Fore.YELLOW+'| Iplaca='+Fore.WHITE,'{0:>6}'.format(Iplaca), end='')
            print(Fore.YELLOW+'| Vplaca='+Fore.WHITE,'{0:>6}'.format(Vplaca), end='')
            print(Fore.BLUE+'| Vaux1='+Fore.WHITE,'{0:>5}'.format(Vaux1), end='')
            print(Fore.BLUE+'| Vaux2='+Fore.WHITE,'{0:>5}'.format(Vaux2), end='')
            print(Fore.RED+'| Vbat_err='+Fore.WHITE,'{0:>4}'.format(Vbat_err), end='')
            print(Fore.RED+'| Ibat_err='+Fore.WHITE,'{0:>4}'.format(Ibat_err), end='')
            
            print()
           
        except:
            print ('Error ADS1115', ee)

        time.sleep(2)

