# Version 22/Dic/2021  para ESP32 --  3 Reles SSR AF o SC

###### INICIO CONFIGURACION #######
SSID='XXXXXX'
PASS='YYYYYY'
# ################################
Nodo = b'23' # Numero de Nodo MQTT
# ################################
IP = '192.168.0.131' # IP que se le asigna al ESP32
IP_ROUTER = '192.168.0.1'

logica= 'pos' # pos= positiva ,  neg==negativa...solo para SC
# Mejor opcion logica pos en ESP32

tipo_ssr = 'SC'   # poner el tipo de SSR
# AF1 (SSR angulo fase por PWM)
# AF2 (SSR angulo fase por DAC)
# SC (SSR Semiciclos)
# .. futuro TRIAC (TRIAC)

pines=[12,13,14] # GPIO ESP32 = 12,13,14 

#config mqtt/red
SERVER = '192.168.0.130' # IP de la Raspberry
PORT = 1883
USER = 'rpi'
PASSWORD = 'fv'
 
Nodo = b'PVControl/Reles/' + Nodo

DEBUG = True 

#nlog = nlog_max = 1000 # Nbucles para mandar OK al log

###### FIN CONFIGURACION #######

# ###################################
import gc
from umqtt.simple import MQTTClient
gc.collect()
import network
gc.collect()
import machine
from machine import Pin,PWM,Timer,reset,RTC
from array import array
gc.collect()
import micropython, utime, os,sys
import ujson
gc.collect()

ee = 'p10'

#flag_reiniciar = True # habilita reinicio si no se reciben mensajes MQTT en un tiempo
flag_reset = 0
print (Nodo,IP)

if logica =='pos': duty_ini=0
else: duty_ini=1023

#eleccion por fichero del tipo de SSR
try:
  with open('tipo_ssr.txt', 'r') as f:
    tipo_ssr = ujson.load(f)
except:
  print ('Archivo tipo_ssr.txt no encontrado o con errores')
  
  with open('tipo_ssr.txt', 'w') as f:
    ujson.dump(tipo_ssr, f)

print('fichero tipo_ssr.txt:',tipo_ssr)


if tipo_ssr == 'AF2': # control por Angulo de Fase por DAC (maximo 2 reles)
  from machine import DAC # DAC rango:0-255 salida:0-3.3V
  dac1=DAC(Pin(25))   # GPIO 25    
  dac2=DAC(Pin(26))   # GPIO 26
  dac1.write(0) #salida 0v
  dac2.write(0) #salida 0V

elif tipo_ssr == 'AF1': # control por Angulo de Fase por PWM + RC
  Rele1 = PWM(Pin(pines[0]), freq=1000, duty=duty_ini)
  Rele2 = PWM(Pin(pines[1]), freq=1000, duty=duty_ini)
  Rele3 = PWM(Pin(pines[2]), freq=1000, duty=duty_ini)

  ee = 'p20'
elif tipo_ssr == 'SC':
  
  Rele1 = PWM(Pin(pines[0]), freq=5, duty=duty_ini)
  Rele2 = PWM(Pin(pines[1]), freq=5, duty=duty_ini)
  Rele3 = PWM(Pin(pines[2]), freq=5, duty=duty_ini)
    
ee = 'p30'
# Por interrupccion temporal se pone flag_reset=1 cada X seg .. si se mantiene a 1 se reinicia
# el bucle debe poner flag_reset=0 si todo va OK
def reiniciar():
  global flag_reset
  if flag_reset == 1:
    print ('###########')
    print (hora(),'reset')
    print ('###########')
    utime.sleep(2)
    reset()
  else:
    flag_reset = 1
  
  if RTC().datetime()[5]%5 <=0: # cada 5 minutos
    print (hora(),'Ejecutando Sub Timer')

def sub_cb_af(topic, msg): # SSR con Angulo de Fase o Paso por Cero
  global t_ultimo_msg, DEBUG
  
  if DEBUG: 
    print (topic, msg)
  try:
    ee='10' 
    
    if topic == Nodo + b'/Conf':
      msg = msg.decode()
      if msg == 'Debug=ON':
        DEBUG=True
      elif msg == 'Debug=OFF': DEBUG=False
      elif msg in  ('AF1','AF2','SC'):
        ee ='10b'
        print (msg)
        with open('tipo_ssr.txt', 'w') as f: # actualizo tipo_ssr.txt
          ujson.dump(msg, f)
        utime.sleep(5)
        reset()
        
    ee='20'
    if topic[:-1] == Nodo:
      ee='22'
      x = int(msg)
      if DEBUG: print('Valor recibido=', x)
          
      if tipo_ssr[0:2] == 'AF':    
        
        if tipo_ssr == 'AF2': # uso salidas DAC
          v_dac = int(x * 2.55)
          voltios = round(x * 0.033, 2)
          if DEBUG:
            print(tipo_ssr,'mensaje=',x,'-- Vdac=',v_dac, '/', voltios,'V')
            print ('-' * 40)
            
        elif tipo_ssr == 'AF1': # uso salidas PWM
          msg_duty = int(x * 10.2301)
          voltios = round(x * 0.033, 2)
          if DEBUG:
            print(tipo_ssr,'mensaje=',x,'-- Duty_PWM=',msg_duty, '/', voltios,'V')
            print ('-' * 40)
  
      elif tipo_ssr == 'SC':
        msg_freq = x 
        if logica == 'pos':
          msg_duty = int(float(msg)*10.2301) #logica pos
        else:
          msg_duty = int(1023-float(msg)*10.2301) #logica neg
        if msg_freq > 50: msg_freq = 100 - msg_freq 
        if msg_freq == 0: msg_freq = 50
        if DEBUG:
          print ('-' * 40)
          print('Tipo SSR=',tipo_ssr, 'Duty_PWM=',msg_duty, 'Freq=',msg_freq )
          print ('-' * 40)
        
      ee='22a'
      if topic[-1:] == b'1':        
        if tipo_ssr == 'AF2': dac1.write(v_dac) #salida rele1 0-3V3
        elif tipo_ssr == 'AF1': Rele1.duty(msg_duty)
        elif tipo_ssr == 'SC':
          Rele1.freq(msg_freq)
          Rele1.duty(msg_duty)
          
      elif topic[-1:] == b'2':
        if tipo_ssr == 'AF2': dac2.write(v_dac) #salida rele2 0-3V3
        elif tipo_ssr == 'AF1': Rele2.duty(msg_duty)
        elif tipo_ssr == 'SC':
          Rele2.freq(msg_freq)
          Rele2.duty(msg_duty)

      elif topic[-1:] == b'3':
        if tipo_ssr == 'AF2': pass
        elif tipo_ssr == 'AF1': pass
        elif tipo_ssr == 'SC':
          Rele3.freq(msg_freq)
          Rele3.duty(msg_duty)

      ee='22b'
      if DEBUG:
        c.publish(Nodo+ topic[-1:]+b'/R',msg)
        if tipo_ssr[0:2] == 'AF': c.publish(Nodo+ topic[-1:]+b'/V',str(voltios))
     
        print('Nodo=',Nodo,'  - time_diff=',utime.ticks_diff(utime.ticks_ms(), t_ultimo_msg),'  - msg=',msg)  
      
      ee='22c'
      t_ultimo_msg = utime.ticks_ms()
  except:
    print ('Error en sub_cb_af =',ee)

def hora():
  h = (str(RTC().datetime()[1])+'/'+str(RTC().datetime()[2])
      +' - '+str(RTC().datetime()[4])+':'+str(RTC().datetime()[5])
      +':'+str(RTC().datetime()[6]))
  return h
ee = 'p40'
print ('Inicio:',hora())

tp0 = utime.ticks_ms()

#Interrupcion de whatchdog
timer = Timer(-1)
timer.init(period=30000, mode=Timer.PERIODIC,callback=lambda t:reiniciar()) # 30sg
flag_reset = 0

tp1 = utime.ticks_diff(utime.ticks_ms(), tp0)

try:  
  connected = False # flag de conexion MQTT
  ee = '50'
  micropython.mem_info()
  
  cliente = b'ESP32'+Nodo #machine.unique_id()
  topic_log = b"PVControl/Log"
  t_ultimo_msg = utime.ticks_ms()
  ee = '52'
  # configurar red
  tp2 = utime.ticks_diff(utime.ticks_ms(), tp1)

  print ('Configurando WAN',tp2)
  print (IP, IP_ROUTER)
  flag_reset = 0
  ee = '54'
  ap = network.WLAN(network.AP_IF)
  ap.active(False)
  wlan = network.WLAN(network.STA_IF)
  wlan.active(False)
  wlan.active(True)
  utime.sleep(1)
  wlan.ifconfig([IP, '255.255.255.0',IP_ROUTER,'8.8.8.8'])
  ee = '60'
  if not wlan.isconnected():
    print('Conectando a la red...')
    wlan.connect(SSID, PASS)
    print ('-----')
    
    while not wlan.isconnected():
      utime.sleep(0.3)
      if utime.ticks_diff(utime.ticks_ms(), t_ultimo_msg) > 10000:
        print( 'Error conexion Wifi al inicio')
        utime.sleep(10)
        reset()
  ee = '70'
  print('Configuracion de red:', wlan.ifconfig())
  flag_reset = 0
  tp3 = utime.ticks_diff(utime.ticks_ms(), tp2)
  
  keepalive = 60 # manda un ping cada X segundos
  c = MQTTClient(cliente, server=SERVER, port=PORT, user=USER, password=PASSWORD, keepalive=keepalive)  
  c.set_callback(sub_cb_af)
  print('-------------')
  gc.collect()
  ee = '80'
except:
  print ('Reinicio por Error en except antes de Bucle Principal',ee)
  utime.sleep(5)
  reset() 

n_errores = 0
t_ultimo_msg =  utime.ticks_ms()

# ################## BUCLE PRINCIPAL #######################
print('Tiempos inicio =',tp1,tp2,tp3)

while True:
  flag_reset = 0 # reseteo flag_reset
    
  if utime.ticks_diff(utime.ticks_ms(), t_ultimo_msg) > 300000: # reinicio si no recibe msg en 5 minutos
    print (hora(),' Reinicio por Error t_ultimo_msg')
    try:
      c.publish(topic_log, Nodo+ b' Reinicio por Error t_ultimo_msg')
    except:
      pass
    utime.sleep(2) 
    reset()
  
  if not connected:
    print('Conectando BROKER MQTT...')
    try:
      ee=b'b20'
      c.set_last_will(topic_log, Nodo+b' desconectado')
      try:
        c.disconnect()
        utime.sleep(1)
      except:
        pass  
      cc = c.connect()
      connected = True
      last_ping = utime.ticks_ms()
      print('Suscribiendose a los Topic...')
      for i in range(3):
        print(Nodo+str(i+1))
        c.subscribe(Nodo+str(i+1))
      c.subscribe(Nodo+b'/Conf')
      print(Nodo+b'/Conf')
      print('....Suscripcion hecha')
      c.publish(topic_log, Nodo+ b' conectado ')
      print(Nodo+ b' conectado')
      gc.collect()
      
    except: # OSError:
      utime.sleep(0.5)
      connected = False
      if DEBUG:
        print('Error conexion',ee)
      n_errores += 1
      if n_errores > 10: 
        print (hora(),' Reinicio por Error en try suscripcion')
        try:
          c.publish(topic_log, Nodo+ b' reinicio try  suscripcion')
        except:
          pass
        utime.sleep(2) 
        reset()
      continue

  else: # Bucle normal
    try:
      ee=b'b40'
      for i in range(3): #10
        c.check_msg()
        utime.sleep(0.02)
      ee=b'b42'
      if utime.ticks_ms() - last_ping >= keepalive * 500:    
        c.ping()
        last_ping = utime.ticks_ms()
        if DEBUG: print('ping')
        n_errores = 0
        
    except KeyboardInterrupt:
      print (hora(),' Pulsado ctrl+c')
      timer.deinit()
      #state = machine.disable_irq()
      utime.sleep(2)  
      sys.exit()
  
    except:
      n_errores += 1
      print(hora(),'error=',ee)
      utime.sleep(2)
      if n_errores > 10:
        print (hora(),' Reinicio por Error en try check_msg()') 
        try:
          c.publish(topic_log, Nodo+ b' reinicio check_msg')
        except:
          pass
        utime.sleep(2)
        reset() 
