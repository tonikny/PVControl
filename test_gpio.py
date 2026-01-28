import gpiozero
import time
#led = LED(17)
#led = LED("GPIO17")
#led = LED("BCM17")
#pin = "BOARD11"
#red = gpiozero.PWMLED(pin)
#red = gpiozero.PWMOutputDevice(pin, active_high=True, initial_value=0, frequency=200)
#led = LED("WPI0")
#led = LED("J8:11")

Rele_SSR = {}
id_rele = 411
NGPIO = 0


NGPIO_PIN = f'BOARD{id_rele % 100}'
Rele_SSR[id_rele] = (gpiozero.PWMOutputDevice(NGPIO_PIN , active_high=True, initial_value=0, frequency=5))

Rele_SSR[id_rele].value = 0
NGPIO +=1

print (Rele_SSR)

# funcion
adr = 411
out = 30

while True:
    print(adr, out)
    if int(adr/100) == 4: # Rele GPIO .. esta por regulacion SC
        try:
            # actualizo valor
            Rele_SSR[id_rele].value = out / 100.0
            
            # actualizo frecuencia
            if out == 0 or out == 100:
                pass
            elif out <= 50:
                Rele_SSR[id_rele].frequency = out
            
            else:
                Rele_SSR[id_rele].frequency = 100 - out
            out += 10
            if out > 100: out = 0
            time.sleep(4) 
        except:
            print (f'{time.strftime("%H:%M:%S")} Error rele GPIO')
            print (Rele_SSR[id_rele], adr,out)
            break        
    