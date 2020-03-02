import RPi.GPIO as GPIO # Cargamos la libreria RPi.GPIO  
from time import sleep  # cargamos la función sleep del módulo time 
  
GPIO.setmode(GPIO.BCM)  # Ponemos la Raspberry en modo BCM  
  
GPIO.setup(15, GPIO.OUT)  # Ponemos el pin GPIO nº25 como salida para el LED #1  
GPIO.setup(14, GPIO.OUT)  # Ponemos el pin GPIO nº24 como salida para el LED #2  
  
white = GPIO.PWM(15, 100)   # Creamos el objeto 'white' en el pin 25 a 100 Hz  
red = GPIO.PWM(14, 100)     # Creamos el objeto 'red' en el pin 24 a 100 Hz 
  
white.start(0)              # Iniciamos el objeto 'white' al 0% del ciclo de trabajo (completamente apagado)  
red.start(100)              # Iniciamos el objeto 'red' al 100% del ciclo de trabajo (completamente encendido)  
  
# A partir de ahora empezamos a modificar los valores del ciclo de trabajo
  
pause_time = 0.02           # Declaramos un lapso de tiempo para las pausas
  
try:                        # Abrimos un bloque 'Try...except KeyboardInterrupt'
    while True:             # Iniciamos un bucle 'while true'  
        for i in range(0,101):            # De i=0 hasta i=101 (101 porque el script se detiene al 100%)
            white.ChangeDutyCycle(i)      # LED #1 = i
            red.ChangeDutyCycle(100 - i)  # LED #2 resta 100 - i
            print (i,100-i)
            sleep(pause_time)             # Pequeña pausa para no saturar el procesador
        for i in range(100,-1,-1):        # Desde i=100 a i=0 en pasos de -1  
            white.ChangeDutyCycle(i)      # LED #1 = i
            red.ChangeDutyCycle(100 - i)  # LED #2 resta 100 - i  
            sleep(pause_time)             # Pequeña pausa para no saturar el procesador  
  
except KeyboardInterrupt:   # Se ha pulsado CTRL+C!!
    white.stop()            # Detenemos el objeto 'white'
    red.stop()              # Detenemos el objeto 'red'
    GPIO.cleanup()          # Limpiamos los pines GPIO y salimos
