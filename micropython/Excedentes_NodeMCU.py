# Version 27/Abr/2021  para NodeMCU --  3 Reles SSR AF o SC

###### INICIO CONFIGURACION #######
SSID='XXXXXXX'
PASS='YYYYYYYY'

# ################################
Nodo = b'29' # Numero de Nodo MQTT
# ################################
IP = '192.168.0.29'
IP_ROUTER = '192.168.0.1'

logica= 'pos' # pos= positiva ,  neg==negativa ... para uso en SC
# Mejor opcion logica neg en NodeMCU para SC, pos para AF

tipo_ssr = 'AF'
  # AF (SSR angulo fase por PWM)
  # SC (SSR Semiciclos)

pines=[4,5,14] # GPIO NodeMCU 

#config mqtt/red
SERVER = '192.168.0.15' # IP de la Raspberry
PORT = 1883
USER = 'rpi'
PASSWORD = 'fv'
 
Nodo = b'PVControl/Reles/' + Nodo

DEBUG = False

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

# Tuplas (%potencia, salida PWM necesaria) para uso SSR-AF
try:
  with open('ssr.txt', 'r') as f:
    ssr = ujson.load(f)
except:
  print ('Archivo ssr.txt no encontrado o con errores')
  ssr = [(0,0),(5,30),(10,40),(20,47),(30,51),(40,54),(50,58),(60,62),(70,68),(80,73),(90,78),
      (95,80),(100,100)] 
  with open('ssr.txt', 'w') as f: # pongo ssr.txt por defecto
    ujson.dump(tuple(ssr), f)

print('fichero ssr.txt:',ssr)

#eleccion por fichero del tipo de SSR
try:
  with open('tipo_ssr.txt', 'r') as f:
    tipo_ssr = ujson.load(f)
except:
  print ('Archivo tipo_ssr.txt no encontrado o con errores')
  
  with open('tipo_ssr.txt', 'w') as f:
    ujson.dump(tipo_ssr, f)

print('fichero tipo_ssr.txt:',tipo_ssr)

ssrd = {}
for i in ssr: ssrd[i[0]] = i[1]
print ('diccionario ssr= ',end='')
for i in sorted(ssrd): print(i,':',ssrd[i], end=' , ')

SSR={} # Diccionario para modificar en caliente lista de tuplas del SSR
flag_reiniciar = True # habilita reinicio si no se reciben mensajes MQTT en un tiempo

ee = 'p20' 
print (Nodo,IP)
nf = 0 # flag de print

if tipo_ssr == 'AF': # control por Angulo de Fase por PWM + RC
    freq = 1000
    duty_ini=0
elif tipo_ssr == 'SC':
    freq = 5
    if logica =='pos': duty_ini=0
    else: duty_ini=1023
  
Rele1 = PWM(Pin(pines[0]), freq=freq, duty=duty_ini)
Rele2 = PWM(Pin(pines[1]), freq=freq, duty=duty_ini)
Rele3 = PWM(Pin(pines[2]), freq=freq, duty=duty_ini)

ee = 'p30'
def reiniciar():
  global flag_reset, nf
  if flag_reset == 1:
    print ('###########')
    print (hora(),'reset')
    print ('###########')
    utime.sleep(2)
    reset()
  else:
    flag_reset = 1
    if RTC().datetime()[5]%5 <=0: # cada 5 minutos
      nf += 1
      if nf == 1: 
        print (hora(),'puesto flag_reset a 1')
    else:  
      nf = 0  

def sub_cb_af(topic, msg): # SSR con Angulo de Fase o Paso por Cero
  global t_ultimo_msg, DEBUG, ssr,SSR
  
  if DEBUG: 
    print (topic, msg)
  try:
    ee='10'
    p1= topic.find(b'/Conf/SSR')

    if topic == Nodo + b'/Conf':
      msg = msg.decode()
      if msg == 'Debug=ON':
        DEBUG=True
      elif msg == 'Debug=OFF': DEBUG=False
      elif msg in  ('AF','SC'):
        ee ='10b'
        print (msg)
        with open('tipo_ssr.txt', 'w') as f: # pongo tipo_ssr.txt por defecto
          ujson.dump(msg, f)
        utime.sleep(5)
        reset()
  
    elif p1 >= 0:
      try:
        SSR={}
        for i in range(len(ssr)):
          SSR[ssr[i][0]] = ssr[i][1]
        ee ='10c'
        exec(msg)
          
        ssr=[]
        ssr = list(SSR.items())
        ssr.sort()
        print('ssr=',ssr)
         
        with open('ssr.txt', 'w') as f: # pongo ssr.txt por defecto
          ujson.dump(ssr, f)
      except:
        print (ee,' Error ejecutando ',msg)
    
      c.publish(topic+b'/R',str(ssr))  
     
    ee='20'
    if topic[:-1] == Nodo:
      ee='22'
      x = int(msg)
      if DEBUG: print('Valor recibido=', x)
          
      if tipo_ssr == 'AF':
        for i in range(len(ssr)):
          if ssr[i][0] > x : break
        x1, y1 =  ssr[i-1][0], ssr[i-1][1] # puntos de la recta
        x2, y2 =  ssr[i][0], ssr[i][1]
        y = int(y1 + (y2-y1)/(x2-x1)*(x-x1)) # ecuacion recta
        
        msg_duty = int(y * 10.2301)
        voltios = round(y * 0.033, 2)
        
        if DEBUG:
          print('recta (',x1,',',y1,') - (',x2,',',y2,')')  
          print(tipo_ssr,'salida(',x,')=',y, 'Duty_PWM=',msg_duty, '/', voltios,'V')
          print ('-' * 40)
          c.publish(Nodo+b'/R','recta ('+str(x1)+','+str(y1)+') - ('+str(x2)+','+str(y2)+')')
        
          
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
        if tipo_ssr == 'AF': Rele1.duty(msg_duty)
        elif tipo_ssr == 'SC':  
          Rele1.freq(msg_freq)
          Rele1.duty(msg_duty)
          
      elif topic[-1:] == b'2':
        if tipo_ssr == 'AF': Rele2.duty(msg_duty)
        elif tipo_ssr == 'SC':
          Rele2.freq(msg_freq)
          Rele2.duty(msg_duty)

      elif topic[-1:] == b'3':
        if tipo_ssr == 'AF': pass
        elif tipo_ssr == 'SC':
          Rele3.freq(msg_freq)
          Rele3.duty(msg_duty)

      ee='22b'
      if DEBUG:
        c.publish(Nodo+ topic[-1:]+b'/R',msg)
        if tipo_ssr == 'AF': c.publish(Nodo+ topic[-1:]+b'/V',str(voltios))  
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
ee = '40'
print ('Inicio:',hora())

tp0 = utime.ticks_ms()

timer = Timer(-1)
timer.init(period=30000, mode=Timer.PERIODIC,callback=lambda t:reiniciar())
flag_reset = 0

tp1 = utime.ticks_diff(utime.ticks_ms(), tp0)

try:  
  connected = False # flag de conexion MQTT
  ee = '50'
  micropython.mem_info()
  
  cliente = b'NodeMCU'+Nodo #machine.unique_id()
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
t1 = utime.ticks_ms()

while True:
  try:
    if utime.ticks_diff(utime.ticks_ms(), t1) > 10000:
      t1= utime.ticks_ms()
      flag_reset = 0
  except:
    pass
    
  if flag_reiniciar and utime.ticks_diff(utime.ticks_ms(), t_ultimo_msg) > 120000: # reinicio si no recibe msg en 2 minutos
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
      c.subscribe(Nodo+b'/Conf/SSR')	  
      print(Nodo+b'/Conf')
      print(Nodo+b'/Conf/SSR')
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
      if n_errores > 10:
        print (hora(),' Reinicio por Error en try check_msg()') 
        try:
          c.publish(topic_log, Nodo+ b' reinicio check_msg')
        except:
          pass
        utime.sleep(2)
        reset() 
