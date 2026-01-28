################ CONFIGURACION ##############################
mqtt_broker  = "192.168.1.10"
mqtt_puerto  = 1883
mqtt_usuario = "rpi"
mqtt_clave   = "fv"

# lista con [Nombre, Topic, valor por defecto, num decimales, unidades, rojo, amarillo, verde, amarillo, rojo]

Datos =  [['SOC',"PVControl/SOC",80,0,'%',25,50,100,100,100],
          ['Voltaje',"PVControl/Vbat", 24,1,'V',51,52,58.1,58.4,59],
          ['Intensidad',"PVControl/Ibat",0,0,'A',-120,-80,80,100,120],
          ['Placas',"PVControl/Wplaca",0,0,'W',-10,500,4000,5000,6000],
          
          ['INV_1',"PVControl/W1",0,0,'W',-1000,-1000,3000,4000,5000],
          ['INV_2',"PVControl/W2",0,0,'W',-1000,-1000,3000,4000,5000],
          ['TOTAL',"PVControl/W3",0,0,'W',-1000,-1000,6000,8000,10000] 
         ]
         
Titulo = '   BATERIAS'

t_refresco = 1 # tiempo de refresco en sg

######################################################

import time
from tkinter import *
import paho.mqtt.client as mqtt
import locale
locale.setlocale(locale.LC_ALL, '')

def on_connect(client, userdata, flags, rc):
    for s in Datos:
        client.subscribe(s[1])
    print("Suscripcion a topic MQTT realizada con resultado "+str(rc))
     
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print (time.strftime("%Y-%m-%d %H:%M:%S")," - desconexion MQTT.... reconectando...")
    else:
        client.loop_stop()
        client.disconnect()

def on_message(client, userdata, msg):
    global Datos, hora_msg, t_msg
    
    hora_msg = time.strftime("%H:%M:%S")
    t_msg = time.time()
    
    for i in range(len(Datos)):
        if msg.topic == Datos[i][1]:
            Datos[i][2] = round(float(msg.payload),Datos[i][3])
            
def muestra():
    global Datos, hora_msg, t_msg
    
    hora_label.configure(text = hora_msg)
    
    # Control de tiempo de ultima actualización
    if time.time()-t_msg > 120:
        hora_label.configure(bg = 'red')
    elif time.time()-t_msg > 20:
        hora_label.configure(bg = 'orange')
    else:
        hora_label.configure(bg = 'green')
    
    # Actualizo valores y fondo de color
    for i in range(1,8):
        exec(f"F{i}_label.configure(text = '{Datos[i-1][2]:,.{Datos[i-1][3]}f}'.replace(',', '@').replace('.', ',').replace('@', '.') + ' {Datos[i-1][4]}')")
        
        if Datos[i-1][2] < Datos[i-1][5] or Datos[i-1][2] > Datos[i-1][9]:
            exec(f"F{i}_label.configure(bg = 'red')")
        elif Datos[i-1][2] < Datos[i-1][6] or Datos[i-1][2] > Datos[i-1][8]:
            exec(f"F{i}_label.configure(bg = 'orange')")
        else:
            exec(f"F{i}_label.configure(bg = 'green')")
    
    
    root.after(t_refresco*1000, muestra)       

##################
###### MQTT ######
##################
             
client = mqtt.Client() #crear nueva instancia
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.reconnect_delay_set(3,15)
client.username_pw_set(mqtt_usuario, password=mqtt_clave)
try:
    client.connect(mqtt_broker, mqtt_puerto) #conectar al broker: url, puerto
except:
    print('Error de conexion al servidor MQTT')
time.sleep(.2)
client.loop_start()

####################################################33


hora_msg = time.strftime("%H:%M:%S")
t_msg = time.time()

root = Tk()
root.geometry('1150x500') #300
root.title('PVControl+  GUI')

canvas = Canvas(root, width = 400, height = 80,bg = 'seagreen')
canvas.pack(anchor = NW,fill = BOTH)#, expand = True)

#foto_logo = PhotoImage(file = 'PVControl+.gif') #logo.gif
#canvas.create_image(120, 40, image=foto_logo)

canvas.create_text(400, 35,text = Titulo, font = ('Helvetica', 40, 'bold'), fill='black')
#canvas.create_text(300, 50, text = '  ', font = ('Helvetica', 12, 'bold'), justify = 'center', fill='black')

#canvas.create_text(400, 200, text = 'SOC='+ SOC, font = ('Helvetica', 20, 'bold'), justify = 'center', fill='black')

canvas.update

# Creacion frames
hora_fr = Frame(root,bg="yellow",width=200,bd=2,height=50)

F1_fr = Frame(root,bg="khaki",width=250,bd=2,height=150)
F2_fr = Frame(root,bg="khaki",width=250,bd=2,height=150)
F3_fr = Frame(root,bg="hot pink",width=250,bd=2,height=150)
F4_fr = Frame(root,bg="khaki",width=300,bd=2,height=150)

F5_fr = Frame(root,bg="khaki",width=300,bd=2,height=150)
F6_fr = Frame(root,bg="khaki",width=300,bd=2,height=150)
F7_fr = Frame(root,bg="khaki",width=300,bd=2,height=150)

#Coloco frames en root
hora_fr.place(x=800,y=10)# fill = BOTH)#,expand = True)

F1_fr.place(x=5,y=120)# fill = BOTH)#,expand = True)
F2_fr.place(x=260,y=120)# fill = BOTH)#,expand = True)
F3_fr.place(x=515,y=120)# fill = BOTH)#,expand = True)
F4_fr.place(x=770,y=120)# fill = BOTH)#,expand = True)

F5_fr.place(x=10,y=320)
F6_fr.place(x=320,y=320)
F7_fr.place(x=630,y=320)


# Titulos de frames

hora_label = Label(hora_fr,  text = "Hora_mensaje", font = ('Helvetica', 30, 'bold'))
hora_label.place(x=2, y=2, height=40,width = 190)

# Variables
for i in range(1,8):
    # Titulos
    exec(f"F{i}_tit=Label(F{i}_fr, relief ='groove',text=' {Datos[i-1][0]} ',font=('Verdana',18,'bold'))")
    exec(f"F{i}_tit.place(x=50, y=0, height=30,width = 150)")
    
    # Valores
    #exec(f"F{i}_label=Label(F{i}_fr, text=' {Datos[i-1][2]} {Datos[i-1][4]} ',font=('Helvetica',50))")
    exec(f"F{i}_label=Label(F{i}_fr, text=' {Datos[i-1][2]} {Datos[i-1][4]} ',font=('Arial',50, 'bold'))")
    if i<4: exec(f"F{i}_label.place(x=5, y=50, height=80,width = 225)") # primera linea
    else: exec(f"F{i}_label.place(x=5, y=50, height=80,width = 275)")   # segunda linea

muestra()

root.mainloop()

COLORS = ['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
          'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
          'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
          'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
          'light slate gray', 'gray', 'light gray', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
          'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
          'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
          'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
          'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
          'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
          'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
          'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
          'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
          'indian red', 'saddle brown', 'sandy brown',
          'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
          'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
          'pale violet red', 'maroon', 'medium violet red', 'violet red',
          'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
          'thistle', 'snow2', 'snow3',
          'snow4', 'seashell2', 'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2',
          'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
          'PeachPuff3', 'PeachPuff4', 'NavajoWhite2', 'NavajoWhite3', 'NavajoWhite4',
          'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
          'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
          'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
          'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
          'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
          'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
          'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
          'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
          'LightSkyBlue3', 'LightSkyBlue4', 'Slategray1', 'Slategray2', 'Slategray3',
          'Slategray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
          'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
          'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
          'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
          'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
          'cyan4', 'DarkSlategray1', 'DarkSlategray2', 'DarkSlategray3', 'DarkSlategray4',
          'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
          'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
          'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
          'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
          'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
          'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
          'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
          'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
          'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
          'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
          'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
          'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
          'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
          'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
          'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
          'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
          'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
          'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
          'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
          'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
          'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
          'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
          'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
          'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
          'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
          'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
          'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
          'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
          'grey1', 'grey2', 'grey3', 'grey4', 'grey5', 'grey6', 'grey7', 'grey8', 'grey9', 'grey10',
          'grey11', 'grey12', 'grey13', 'grey14', 'grey15', 'grey16', 'grey17', 'grey18', 'grey19',
          'grey20', 'grey21', 'grey22', 'grey23', 'grey24', 'grey25', 'grey26', 'grey27', 'grey28',
          'grey29', 'grey30', 'grey31', 'grey32', 'grey33', 'grey34', 'grey35', 'grey36', 'grey37',
          'grey38', 'grey39', 'grey40', 'grey42', 'grey43', 'grey44', 'grey45', 'grey46', 'grey47',
          'grey48', 'grey49', 'grey50', 'grey51', 'grey52', 'grey53', 'grey54', 'grey55', 'grey56',
          'grey57', 'grey58', 'grey59', 'grey60', 'grey61', 'grey62', 'grey63', 'grey64', 'grey65',
          'grey66', 'grey67', 'grey68', 'grey69', 'grey70', 'grey71', 'grey72', 'grey73', 'grey74',
          'grey75', 'grey76', 'grey77', 'grey78', 'grey79', 'grey80', 'grey81', 'grey82', 'grey83',
          'grey84', 'grey85', 'grey86', 'grey87', 'grey88', 'grey89', 'grey90', 'grey91', 'grey92',
          'grey93', 'grey94', 'grey95', 'grey97', 'grey98', 'grey99']
