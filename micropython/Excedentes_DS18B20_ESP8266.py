# Versión 24/Junio/2021
# SSR por semiciclos o Ángulo de Fase
# Lógica positiva o negativa
# Sensor temperatura por pin D4
# ###################################
import gc
from umqtt.simple import MQTTClient
gc.collect()
import math
gc.collect()
import network
gc.collect()
from machine import Pin,PWM,Timer,reset,RTC
gc.collect()
import micropython, time, os,sys
import onewire, ds18x20
import ujson
gc.collect()

###### INICIO CONFIGURACION #######
#Wifi que vamos a usar
SSID="Wifi"
PASS="Passwd"

# ################################
Nodo = b'24' # Numero de Nodo MQTT
# ################################
IP = '192.168.1.24'
IP_ROUTER = '192.168.1.1'

logica= 'neg' # pos= positiva ,  neg==negativa
# Mejor opción lógica neg en NodeMCU

tipo_ssr = 'SC'      # AF (angulo fase)  - SC (Semiciclos)

# Tuplas (%potencia, salida PWM necesaria) para uso SSR-AF
ssr = [(0,0),(5,30),(10,40),(20,47),(30,51),(40,54),(50,58),(60,62),(70,68),(80,73),(90,78),
      (95,80),(100,100)] 

pines=[5,4,14]   # pines NodeMCU = D1,D2,D5
dat = Pin(2)     # definir Pin sensor temperatura DS18B20 - D4 en nodeMCU

#config mqtt/red
SERVER = '192.168.1.15' # IP de la Raspberry
PORT = 1883
USER = 'rpi'
PASSWORD = 'fv'
 
Nodo = b'PVControl/Reles/' + Nodo

DEBUG = False #True #False

#nlog = nlog_max = 1000 # Nbucles para mandar OK al log

###### FIN CONFIGURACION #######

try:
  with open('ssr.txt', 'r') as f:
    ssr = ujson.load(f)
except:
  print ('Archivo ssr.txt no encontrado o con errores')
  with open('ssr.txt', 'w') as f:
    ujson.dump(tuple(ssr), f)

print(ssr)

print (Nodo,IP)
nf=0 # flag de print
def reiniciar():
  global flag_reset, nf
  if flag_reset == 1:
    print ('###########')
    print (hora(),'reset')
    print ('###########')
    time.sleep(2)
    reset()
  else:
    flag_reset = 1
    if RTC().datetime()[5]%5 <=0: # cada 5 minutos
      nf += 1
      if nf == 1: 
        print (hora(),'puesto flag_reset a 1')
    else:  
      nf = 0  

def sub_cb_af(topic, msg): # SSR con Angulo de Fase
  global t_ultimo_msg, DEBUG
  
  if DEBUG: 
    print (topic, msg)
  try:
    ee='10' 
    if topic == Nodo + b'/Conf':
      if msg == b'Debug=ON':
        DEBUG=True
      elif msg == b'Debug=OFF':
        DEBUG=False
      elif  msg == b'SSR':
        c.publish(topic+b'/R',str(ssr))
        
    ee='20'
    if topic[:-1] == Nodo:
      ee='22'
      x = float(msg)      
      ee='23'
      if tipo_ssr == 'SC': # Control por semiciclos
        ee='23a1'
        if logica == 'pos':
          salida = math.floor(x * 10.23) #logica pos
        else:
          salida = math.floor(1023- x * 10.23) #logica neg
      
        if x > 50: msg_freq = 100 - int(x)
        else: msg_freq = int(x)
        
        if x == 0: msg_freq = 50
        
        if topic[-1:] == b'1':
          Rele1.freq(msg_freq)
          Rele1.duty(salida)
        elif topic[-1:] == b'2':
          Rele2.freq(msg_freq)
          Rele2.duty(salida)
        elif topic[-1:] == b'3':
          Rele3.freq(msg_freq)
          Rele3.duty(salida)
      
      else: # tipo_ssr == 'AF' Control por Angulo de fase
        ee='23a2'
        for i in range(len(ssr)):
          if ssr[i][0] > x : break
        x1, y1 =  ssr[i-1][0], ssr[i-1][1] # puntos de la recta
        x2, y2 =  ssr[i][0], ssr[i][1]
        y = int(y1 + (y2-y1)/(x2-x1)*(x-x1)) # ecuacion recta
        ee='24'
        if logica == 'pos':
          salida = math.floor(y * 10.23) #logica pos
          voltios = round(y * 3.3 / 100, 2)
        else:
          salida = math.floor(1023- y * 10.23) #logica neg
          voltios = round(3.3 - y * 3.3 / 100, 2)
        
          
        if topic[-1:] == b'1': Rele1.duty(salida)
        elif topic[-1:] == b'2': Rele2.duty(salida)
        elif topic[-1:] == b'3': Rele3.duty(salida)
        
        if DEBUG:
          print('Nodo=',Nodo,time.ticks_diff(time.ticks_ms(), t_ultimo_msg),msg)  
          print('Valor recibido=', x)
          print('recta (',x1,',',y1,') - (',x2,',',y2,')')
          print('salida(',x,')=',y, ' ...',salida, '/', voltios,'V')
          print ('-' * 40)
          ee='24d'
          c.publish(Nodo+ topic[-1:]+b'/R',str(y))
          c.publish(Nodo+ topic[-1:]+b'/V',str(voltios))
     
          
      ee='25'
      t_ultimo_msg = time.ticks_ms()
  except:
    print ('Error en sub_cb_af =',ee)

def hora():
  h = (str(RTC().datetime()[1])+'/'+str(RTC().datetime()[2])
      +' - '+str(RTC().datetime()[4])+':'+str(RTC().datetime()[5])
      +':'+str(RTC().datetime()[6]))
  return h

print ('Inicio:',hora())

tp0 = time.ticks_ms()

timer = Timer(-1)
timer.init(period=30000, mode=Timer.PERIODIC,callback=lambda t:reiniciar())
flag_reset = 0

tp1 = time.ticks_diff(time.ticks_ms(), tp0)

try:  
  connected = False # flag de conexion MQTT

  if logica =='pos': duty_ini=0
  else: duty_ini=1023
  
  Rele1 = PWM(Pin(pines[0]), freq=5, duty=duty_ini)
  Rele2 = PWM(Pin(pines[1]), freq=5, duty=duty_ini)
  Rele3 = PWM(Pin(pines[2]), freq=5, duty=duty_ini)
  
  micropython.mem_info()
  
  cliente = b'NodeMCU'+Nodo #machine.unique_id()
  topic_log = b"PVControl/Log"
  t_ultimo_msg = time.ticks_ms()
  
  # configurar red
  tp2 = time.ticks_diff(time.ticks_ms(), tp1)

  print ('Configurando WAN',tp2)
  print (IP, IP_ROUTER)
  flag_reset = 0
  
  ap = network.WLAN(network.AP_IF)
  ap.active(False)
  wlan = network.WLAN(network.STA_IF)
  wlan.active(False)
  wlan.active(True)
  time.sleep(1)
  wlan.ifconfig([IP, '255.255.255.0',IP_ROUTER,'8.8.8.8'])
  
  if not wlan.isconnected():
    print('Conectando a la red...')
    wlan.connect(SSID, PASS)
    print ('-----')
    
    while not wlan.isconnected():
      time.sleep(0.3)
      if time.ticks_diff(time.ticks_ms(), t_ultimo_msg) > 10000:
        print( 'Error conexion Wifi al inicio')
        time.sleep(10)
        reset()

  print('Configuracion de red:', wlan.ifconfig())
  flag_reset = 0
  tp3 = time.ticks_diff(time.ticks_ms(), tp2)
  
  keepalive = 60 # manda un ping cada X segundos
  c = MQTTClient(cliente, server=SERVER, port=PORT, user=USER, password=PASSWORD, keepalive=keepalive)
  
  c.set_callback(sub_cb_af)
  print('-------------')
  gc.collect()

except:
  print ('Reinicio por Error en except antes de Bucle Principal')
  time.sleep(5)
  reset() 

n_errores = 0
t_ultimo_msg =  time.ticks_ms()

# ################## BUCLE PRINCIPAL #######################
print('Tiempos inicio =',tp1,tp2,tp3)
t1 = time.ticks_ms()

while True:
  #nlog -= 1
  try:
    if time.ticks_diff(time.ticks_ms(), t1) > 10000:
      t1= time.ticks_ms()
      flag_reset = 0
    #if nlog < 0:
      #print (time)
      #nlog = nlog_max
      #c.publish(topic_log, Nodo+ b' funcionando OK')
  except:
    pass
    
  if time.ticks_diff(time.ticks_ms(), t_ultimo_msg) > 60000*100: 
    print (hora(),' Reinicio por Error t_ultimo_msg')
    try:
      c.publish(topic_log, Nodo+ b' Reinicio por Error t_ultimo_msg')
    except:
      pass
    time.sleep(2) 
    #reset()
    t_ultimo_msg = time.ticks_ms()
  
  if not connected:
    print('Conectando BROKER MQTT...')
    try:
      ee=b'20'
      c.set_last_will(topic_log, Nodo+b' desconectado')
      try:
        c.disconnect()
        time.sleep(1)
      except:
        pass  
      c.connect()
      connected = True
      last_ping = time.ticks_ms()
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
      time.sleep(0.5)
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
        time.sleep(2) 
        reset()
      continue

  else:
    try:
      ee=b'40'
      for i in range(3): #10
        c.check_msg()
        #print(time.ticks_ms())
        time.sleep(0.02)
      ee=b'42'
      if time.ticks_ms() - last_ping >= keepalive * 500:
          try:
              ds = ds18x20.DS18X20(onewire.OneWire(dat))
              roms = ds.scan()
              ds.convert_temp()
              time.sleep_ms(750)
              for rom in roms:
                  temp=ds.read_temp(rom)
                  temp=round(temp,2)
                  c.publish(b'PVControl/Node'+Nodo[16:],str(temp))
                  print(b'PVControl/Node'+Nodo[16:],temp)
          except:
              print('No hay ningun DS18B20 conectado')
              pass 
          c.ping()
          last_ping = time.ticks_ms()
          if DEBUG: print('ping')
          n_errores = 0
  
    except KeyboardInterrupt:
      print (hora(),' Pulsado ctrl+c')
      timer.deinit()
      time.sleep(2)  
      sys.exit()
  
    except:
      n_errores += 1
      print(hora(),'error=',ee)
      if n_errores > 10:
        print (hora(),' Reinicio por Error en try check_msg()') 
        try:
          c.publish(topic_log, Nodo+ b' reinicio check_msg')
        except:
          pass
        time.sleep(2)
        reset() 




