import time,sys
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

start = hora1 = time.time()

#Vbat
RES0 = (68+1.5)/1.5 * 12.63/12.33  # Divisor tension Vbat...(R2=68K..R1=1,5K) * ajuste por tolerancias en resistencias
RES0_gain = 2 
adc.start_adc(0, gain=RES0_gain, data_rate=250) #8,16,32,64,128,250,475,860
                                                 # start_adc_difference() para diferencial

print('Leyendo ADS1115 canal 0 durante 5 segundos...')
N=1
while (time.time() - start) <= 500.0:
    try:
        Vbat=0
        for i in range(N):
            Vbat += adc.get_last_result()
        Vbat= Vbat/N * 0.000125/RES0_gain * RES0
        
        print (round(time.time() - hora1,5),round(Vbat,5))
        hora1=time.time()
        # AVISO! Si se intenta leer otra entrada del ADS (read_adc) se desactiva la conversion continua
        time.sleep(0.025)

    except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
        break
        
# Stop conversion continua
adc.stop_adc()
sys.exit()
