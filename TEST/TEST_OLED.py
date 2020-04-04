# -*- coding: utf-8 -*-
import time
import random # para simulacion usando random.choice


#import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


basepath = '/home/pi/PVControl+/'

# Raspberry Pi pin configuration:
RST = 24

DEBUG = 0

NUM_OLED = 0
try:
    disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
    disp1.begin()
    NUM_OLED += 1
except:
    print ('No encontrado OLED en 3C')
    pass

if NUM_OLED == 1:
    try:
        disp2 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp2.begin()
        NUM_OLED += 1
        #print ('OLED 3C y 3D')
    except:
        #print ('OLED 3C')
        pass
else:
    try:
        disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D) 
        disp1.begin()
        NUM_OLED += 1
        #print ('OLED 3D')
    except:
        pass


if NUM_OLED >= 1:
    #disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)        
    #disp1.begin()
    disp1.clear()
    image = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp1.image(image)
    disp1.display()

    width = disp1.width
    height = disp1.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    font34 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 34)
    font16 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 16)
    font12 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 12)
    font10 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 10)
    font11 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 15)
    font6 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 10)

    OLED_contador1=0 # contador del pantallazo que presenta en secuencial
    OLED_salida_opcion1 = -1 # para elegir entre salida fija o secuencial
                            # se controla por MQTT con PVControl/Oled
                            # -1= secuencial....0,1,2,3... fija la pantalla marcada

if NUM_OLED == 2:
    #disp2 = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D)        
    #disp2.begin()
    disp2.clear()
    image2 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
    disp2.image(image2)
    disp2.display()
    OLED_contador2 = 0 # contador del pantallazo que presenta en secuencial
    OLED_salida_opcion2 = -1


# Initialize library.
#disp1.begin()
#disp2.begin()
try:
    # Clear display.
    disp1.clear()
    disp1.display()

    disp2.clear()
    disp2.display()
except:
    pass

try:
    #image = Image.open('happycat_oled_64.ppm').convert('1')
    image = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')

    # Display image.
    disp2.image(image)
    disp2.display()
except:
    pass
time.sleep(1)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp1.width
height = disp1.height
print (width, height)

image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


# Load font.
font = ImageFont.load_default()
font30 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 34)
font16 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 16)
font12 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 12)
font10 = ImageFont.truetype(basepath+'Minecraftia-Regular.ttf', 10)

font11 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 15)
font6 = ImageFont.truetype(basepath+'SmallTypeWriting.ttf', 10)

#font11 = ImageFont.truetype(basepath+'novamono.ttf', 16)



Rele_Out = [[0] * 8 for i in range(40)] # Situacion actual


def OLED(pantalla,modo):

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    if modo == 0:
        image1 = Image.open(basepath+'pvcontrol_128_64.png').resize((disp1.width, disp1.height), Image.ANTIALIAS).convert('1')
        disp1.image(image1)
        disp1.display()

    elif modo == 1:
        draw.rectangle((0, 0, 127, 20), outline=255, fill=0)
        draw.text((8, 0), 'SOC='+str(soc)+'%', font=font16, fill=255)
        draw.rectangle((0, 20, 64, 46), outline=255, fill=0)
        draw.rectangle((64, 20, 127, 46), outline=255, fill=0)
        draw.text((4, 22),  'Vbat='+str(vbat), font=font, fill=255)
        draw.text((69, 22), 'Ibat='+str(ibat), font=font, fill=255)
        draw.text((4, 34),  'Vpla='+str(vplaca), font=font, fill=255)
        draw.text((69, 34), 'Ipla='+str(iplaca), font=font, fill=255)

    elif modo == 2:
        draw.rectangle((0, 0, 90, 31), outline=255, fill=0)
        draw.text((8, 1), 'Vbat='+str(vbat), font=font11, fill=255)
        draw.text((8, 14), 'Ibat='+str(ibat), font=font11, fill=255)
        draw.rectangle((0, 31, 90, 63), outline=255, fill=0)     
        draw.text((8, 31), 'Vpla='+str(vplaca), font=font11, fill=255)
        draw.text((8, 45), 'Ipla='+str(iplaca), font=font11, fill=255)

        draw.rectangle((90, 0, 127, 20), outline=255, fill=255)     
        draw.text((100, 0), 'SOC', font=font, fill=0)
        draw.text((93, 10), str(soc), font=font, fill=0)
        
        draw.rectangle((90, 22, 127, 42), outline=255, fill=255)     
        draw.text((95, 22), 'Temp', font=font, fill=0)
        draw.text((93, 32), str(temp), font=font, fill=0)
        
        draw.rectangle((90, 44, 127, 63), outline=255, fill=255)     
        draw.text((95, 44), 'Exced.', font=font, fill=0)
        draw.text((100, 54), str(diver), font=font, fill=0)

    elif modo==3:
        draw.rectangle((0, 0, 63, 10), outline=255, fill=0)
        draw.text((2, 0), "Rele 1", font=font, fill=255)

        draw.rectangle((0, 10, 63, 20), outline=255, fill=255)
        draw.text((2, 10), "Rele 2", font=font, fill=0)

        draw.rectangle((0, 20, 63, 30), outline=255, fill=255)
        draw.text((2, 20), "Bomba Pozo", font=font, fill=0)

        draw.rectangle((0, 30, 63, 40), outline=255, fill=0)
        draw.text((2, 30), "Depuradora", font=font, fill=255)

        draw.rectangle((0, 40, 63, 50), outline=255, fill=0)
        draw.text((2, 40), "Calef. 1", font=font, fill=255)

        draw.rectangle((0, 50, 63, 60), outline=255, fill=255)
        draw.text((2, 50), "AA Salon", font=font, fill=0)

        draw.rectangle((66, 0, 127, 10), outline=255, fill=0)
        draw.text((66, 0), "Calef.Ppal", font=font, fill=255)

        draw.rectangle((66, 10, 127, 20), outline=255, fill=0)
        draw.text((66, 10), "Rele 333", font=font, fill=255)

        draw.rectangle((66, 20, 127, 30), outline=255, fill=255)
        draw.text((66, 20), "Rele 334", font=font, fill=0)

        draw.rectangle((66, 30, 127, 40), outline=255, fill=0)
        draw.text((66, 30), "Rele 335", font=font, fill=255)

        draw.rectangle((66, 40, 127, 50), outline=255, fill=0)
        draw.text((66, 40), "Rele 336", font=font, fill=255)

        draw.rectangle((66, 50, 127, 60), outline=255, fill=0)
        draw.text((66, 50), "Rele 337", font=font, fill=255)

    elif modo == 4:
        if soc == 100:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=255)
            draw.rectangle((3, 3, 124, 60), outline=255, fill=0)
            draw.rectangle((10, 10, 117, 53), outline=255, fill=255)
                        
            draw.text((13, 10), '100%', font=font30, fill=0)
        else:
            draw.rectangle((0, 0, 127, 63), outline=255, fill=0)
            draw.text((10, 10), str(soc)+'%', font=font30, fill=255)


    if pantalla == 1 and modo > 0:
        disp1.clear()
        disp1.image(image)
        disp1.display()
    

while True:
    excedentes=random.choice([0,1,2,3,4,5,6,7,8,9,10])
    soc=random.choice([80.3,80.2,100.0,100])
    vbat=random.choice([27.3,27.5,28.1])
    ibat=random.choice([20,27.5,-10.8,123,-134])
    vplaca=random.choice([27.3,27.5,28.1])
    iplaca=random.choice([20,27.5,-10.8,123,-134])
    temp=random.choice([22.3,22.5,22.1])
    diver=random.choice([1,1,0,0,1,0,0,0])
    
    #OLED(1,1, dato1,dato2,dato3,dato4,dato5)
    #time.sleep(2)
    print(0)
    OLED(1,0)
    time.sleep(2)
    
    print(1)
    OLED(1,1)
    time.sleep(2)
    
    print(2)
    OLED(1,2)
    time.sleep(2)
    
    print(3)
    OLED(1,3)
    time.sleep(2)
    
    print(4)
    OLED(1,4)
    time.sleep(2)
    
    
    """
    #draw.text((2, 49),     '(0X)(0000X0X)',  font=font11, fill=255)
    salto=7
    for i in range(0,40,salto):
        relleno=random.choice([0,255])
        draw.rectangle((i, 63, i+3, 51), outline=255, fill=relleno)

    for i in range(i+10,108,salto):
        relleno=random.choice([0,255])
        draw.rectangle((i, 63, i+3, 55), outline=255, fill=relleno)

    
    #Excedentes
    draw.rectangle((118, 63, 127, 49), outline=255, fill=0)
    draw.rectangle((120, 61-excedentes, 125, 61), outline=255, fill=255)
    

    # Display imagen.
    disp.image(image)
    disp.display()
    time.sleep(1)
    """


