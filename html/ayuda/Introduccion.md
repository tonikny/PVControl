
---
# 1 - PVControl+ en un vistazo rapido

---
Quizás lo mejor para definir el concepto de PVControl+ es hacerse una serie de preguntas


- A) ¿Tengo una instalación FV?

- B) ¿Me gustaría poder **MONITORIZAR** esa instalación?
    - Ver lo que producen la placas, consumos, etc en el día, semana, mes... con distintas gráficas en tiempo real e históricas
    - Si tengo baterías.... ver como se cargan o descargan (SOC, Voltaje batería, Intensidad de batería, voltaje de las celdas... )
    - Si estoy conectado a Red comercial, ver lo que consumo o inyecto
    - Poder monitorizar desde la propia FV o desde cualquier sitio si hay internet usando cualquier navegador WEB (móvil, pc, etc)
    - ...

- C) ¿Me gustaría poder **CONTROLAR** esa instalación?
    - Poder encender/apagar cosas (depuradora, luces, termo, ...) automáticamente o manualmente en función de condiciones (horario, situación de las baterías, producción de placas, etc)
    - ....
  
- D) ¿Me gustaría poder **MONITORIZAR Y CONTROLAR DE FORMA AVANZADA** esa instalación?
    - Por ejemplo tengo una mezcla de equipos inversores/reguladores del mismo o distinto fabricante
    - Me gustaría usar Telegram para ver/controlar rápidamente la situación de la FV y que me mande mensajes periódicos a un chat del móvil
    - Quiero un Control de excedentes con **control de potencia real** para aprovecharlos en Termos de agua, calefacciòn etc
    
    - Quiero poner un sistema avanzado de Monitorización/Control con posibilidad de:  
  
        - Integrarse con Home Assistant (mandar o recibir datos por MQTT)
        - Control de reles y/o sensores via WiFi con Tasmota
        - Uso de cámaras de vigilancia con Motioneye
        - etc
    
Si se ha contestado que SI solo a las preguntas A) y B) hay muchos sistemas y normalmente el propio sistema de monitorización del fabricante del equipo inversor/regulador puede servir

Si también se ha contestado que SI a la pregunta C)  ya hay menos sistemas que lo hagan pero existen alternativas y ya dependerá de los gustos y necesidades específicas de cada uno

Si se ha contestado a todas que SI, ya existen muy pocas opciones

---

> En particular el **control real de excedentes** con control de potencia para cualquier número de cargas (calefacción, termo, etc) tanto por cable como por WiFi es una característica muy avanzada de PVControl+ 

> Igualmente pasa con la característica de PVControl+ de poder **mezclar equipamiento de distintos fabricantes** (Hibridos tipo Axpert, Victron, SMA, SRNE, Goodwe, Huawei, Deye, Sofar, etc)

> Además el **uso de Telegram** da una funcionalidad muy cómoda y avanzada de poder monitorizar y controlar la FV

---

![](ayuda/img/portada.png)


Esta posibilidad de Monitorización avanzada y de control avanzado hace que instalar PVControl+ sea mas o menos complejo dependiendo de lo que queramos hacer

----

> **Para este capítulo de introducción vamos a considerar un ejemplo simple pero muy habitual que es tener un Hibrido tipo Axpert/Voltronic al que le conectamos placas y que tenga batería**

---


##  1.1 - Instalando PVControl+ en Hibridos tipo Axpert de forma rapida

### <span style="color:blue">1.1.1 ¿Que HW necesito? </span>

Partimos de que tenemos instalado el Hibrido conectado a las placas y batería

Para poder capturar los datos necesitamos conectar el Hibrido a un "cacharro" que esté encendido todo el tiempo y que se encargue de ir guardando los datos y poder presentarnoslos cuando queramos

Para dicho "cacharro" hay diversas alternativas, pero en este manual pondremos las mas recomendables en las que se usa PVControl+

---

- **Raspberry pi :** Es el equipo preferido dadas sus múltiples ventajas
    - Pequeño consumo dado que estara siempre encendido (4-7W)
    - Pequeño tamaño
    - Es el estandard que se usa con PVControl+ 
    - Se puede usar casi cualquier modelo de Raspberry (Zero, A+, Rpi3, Rpi4), aunque hoy en día parece razonable si se va a comprar una elegir al menos una Rpi4 de 2GB.

---

- **Portátil (mini PC):** típicamente con pantalla de 10''
    - Tiene teclado/ratón/pantalla incluída
    - Consume algo mas pero puede ser asumible (10-15w)
    - Muchas veces se tiene sin usar almacenado en un cajón

---

Una vez que ya tenemos en "cerebro", toca conectar Hibrido con "cerebro"

En este caso lo habitual es hacerlo **con un simple cable USB si el Hibrido tiene salida USB**

Si el Hibrido no tiene salida USB, es habitual que tenga salida RS232 por lo que necesitaremos un conversor RS232 a USB **(mucho mejor si el conversor es de tipo aislado para protejer tanto al Hibrido como a la Raspberry)** 

Asi quedaría el esquema de conexión:

![](ayuda/img/b00dbd202cf47818.png)

En este caso hemos incluido un CONVERTIDOR DC-DC para alimentar directamente desde baterías a la Rasberry en lugar de alimentarla desde 220VAC dado que tiene varias ventajas:

- Hay mayor eficiencia de consumo dado que no hace falta convertir desde bateria a 220VAC y despues desde 220VAC a 5V sino simplemente desde bateria a 5V

- La raspberry seguira funcionando aunque el Hibrido de apague
 
### <span style="color:blue">1.1.2 ¿Que SW necesito? </span>

Aunque PVControl+ se puede instalar en un equipo que ya tenga instalado el Sistema Operativo y otros programas, lo recomendable es dedicar la Raspberry en exclusiva para este trabajo

En este sentido se ha generado una imagen para cargar en una microSD y que el proceso sea lo mas simple posible

Aunque PVControl+ puede funcionar con microSD de 8GB, se recomienda que **la microSD sea de al menos 32GB del tipo A2**

Por tanto **lo primero es descargarse la imagen de PVControl+ desde internet y grabarla en la microSD**

**La imagen se puede descargar desde este link**


- [`Descargar imagen microSD PVControl+  -> PVControl_64b_2023_12_15.gz (Bookworm)`](https://drive.google.com/file/d/1seF2_l8mc9WNYgdMVV-9V2zbrSCRDLJG/view?usp=drive_link)



Una vez descargada hay que grabarla en la microSD,para ello existen muchos programas, por ejemplo se puede usar la utilidad propia de raspberry pi image o la utilidad de balenaetcher


- [https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/](https://www.raspberrypi.org/blog/raspberry-pi-imager-imaging-utility/)

- [https://www.hwlibre.com/etcher/](https://www.hwlibre.com/etcher/)

---

> En la imagen de PVControl+ ya viene básicamente todo preinstalado, pero lógicamente hay que adaptar algunos parámetros a la instalación de cada uno

> **COMO SEGURIDAD MI CONSEJO ES GUARDAR UNA IMAGEN DE LA microSD EN EL PC ANTES DE TRASTEAR, PARA PODER VOLVER A LA SITUACION INICIAL SIEMPRE QUE SEA NECESARIO**

> **UNA VEZ TENGAMOS LA INSTALACION FUNCIONANDO ES MUY RECOMENDABLE SACAR PERIODICAMENTE UNA IMAGEN DE LA microSD PARA TENERLA COMO SEGURIDAD**

---

### <span style="color:blue">1.1.3 Ya tengo la Raspberry y la imagen de PVControl+....¿y ahora que? </span>

####1.1.3.1. Acceso a la Raspberry
Lo primero es poder acceder a la RPi para poder configurarla con los datos de nuestra instalación (Wifi, etc)



[https://www.raspberrypi.org/documentation/remote-access/README.md](https://www.raspberrypi.org/documentation/remote-access/README.md)

Como se ves hay varias formas, explico algunas:


- **Monitor/Teclado/Raton**

   > Una forma muy cómoda y fácil de poder acceder a la RPi para configurarla es enchufarla a un Monitor/TV con entrada HDMI y usar un teclado/raton

   >**Si esta opción es posible, es la mas recomendable dado que siempre funcionará sin problemas**



- **Acceso por VNC**

> VNC nos permite ver el escritorio de la RPi en un PC, y por tanto manejar la RPI como si se tuviera enchufado un Monitor/Teclado/Ratón

> Para ello debemos instalar en nuestro PC un visor de VNC (VNCViewer por ejm)

>[https://www.realvnc.com/es/connect/download/viewer/](https://www.realvnc.com/es/connect/download/viewer/)

>Igualmente hace falta que la Raspberry esté conectada al router (por cable Ethernet si no se ha incluido antes la WiFi de nuestra casa en la Raspberry)

>Una vez tengamos VNC Viewer instalado lo ejecutaremos en el PC y tendremos que decirle la IP de la Raspberry a la que nos queremos conectar para ver en la pantalla del PC como si fuera la pantalla de la Raspberry

> Por ejemplo si la IP de la Raspberry fuera la 192.168.0.14 se pondría en VNCViewer 

>![Entrada VNCViewer](ayuda/img/f3002fa81bcacb37.png)

> Hay varias formas de saber la IP que tiene asignada la Raspberry

> - Mirarlo en el Router
> - Instalar en el movil una app que nos diga todos los equipos conectado en nuestra red
>> [https://play.google.com/store/apps/details?id=com.pzolee.wifiinfo&hl=en_US](https://play.google.com/store/apps/details?id=com.pzolee.wifiinfo&hl=en_US)
>>> ![](ayuda/img/6e66241367966dc8.png)


>- Otra posibilidad que muchas veces funciona es intentar
conectar poniendo ….. rpi.local


>     ![](ayuda/img/f86ea53dacf0adf2.png)



> ----------

>Una  vez introducimos la IP nos podremos conectar a la Raspberry dando el usuario/clave

>En la imagen de PVControl+ se ha puesto el siguiente usuario/clave:

>- **Usuario : pi**

>- **Clave: PVControl+**

>Evidentemente si pensamos que podemos tener problemas de que alguien NO autorizado se pueda conectar debemos cambiar dicha contraseña


----------

####1.1.3.2. ¡¡Ya veo el escritorio de la Raspberry!!

Muy bien, felicidades, ya podemos ver el escritorio de la Raspberry en nuestro TV o en el PC, por lo que ya podemos hacer unas primeras configuraciones


- **WIFI**

>Si queremos que la Raspberry cuando este conectada al Hibrido este conectada a internet por WiFi en lugar de por cable, debemos dar de alta nuestra red WiFi y contraseña

>![](ayuda/img/9afe5fbfe4aaa405.png)


- **EXPANDIR TARJETA microSD**

>La imagen realizada se puede poner en una microSD de al menos 8GB...se recomienda una de microSD de 32GB, por lo que una vez copiada la imagen en la SD hay que ver la capacidad de la tarjeta para asegurar que se utiliza toda la capacidad disponible

>En las últimas versiones de las Raspberry **NO es necesario expandir la tarjeta** dado que se autoexpande, en todo caso podemos mirar la capacidad de la microsd abriendo una ventana de terminal y poniendo el comando

>> `df -h `

> para ver si coincide con el tamaño de la tarjeta

> En el caso de que la capacidad que aparezca sea inferior al tamaño de la microSD hay que **expandir la microSD**


> Para expandir la microSD desde una ventana de terminal se ejecuta:

>> `sudo raspi-config`

>> opción Advanced 
>> ![](ayuda/img/3444837f66ee4350.png)

>> opción A1
>> ![](ayuda/img/d127ff6be32c2ed5.png)

>> Con esto la próxima vez que se reinicie ya se tendrá la capacidad completa de la tarjeta que podemos ver con el comando `df -h`

>> ![](ayuda/img/93b0c6fc01924c98.png)



- **Actualizar PVControl+**

>![](ayuda/img/git_pull.png)

. 

----------

### <span style="color:blue"> 1.1.4 Conectando la Raspberry con el Hibrido y configurando PVControl+</span>

Ya tenemos la Raspberry preparada para poder conectarla en su lugar definitivo y enchufarla por USB al Hibrido

Por tanto conectamos segun el esquema indicado anteriormente y nos vamos a PC para poder acceder por VNC y configurar la conexion Raspberry-Hibrido

Evidentemente si tenemos pantalla/teclado/raton conectado a la Raspberry lo podemos configurar directamente en la Raspberry


#### 1.1.4.1 Conocer los puertos y protocolos de comunicaciones del Hibrido
Lo primero es ver en que puerto de comunicaciones reconoce la Raspberry al Hibrido para poder configurarlo

Para ello abriremos una ventana de terminal y ejecutaremos

>`cd PVControl+` ....para ir a la carpeta /pi/PVControl+

>`sudo systemctl stop hibrido` ....para asegurar que el servicio hibrido esta parado

> `sudo python3 hibrido.py -test` ....ejecuta un programa para ver el tipo de Hibrido y el puerto de comunicaciones

> ![](ayuda/img/hibrido_test.png)

> Nos fijaremos en cual test responde el Hibrido con datos, consiguiendo por tanto los siguientes datos:

> - **Puerto:** Por ejemplo /dev/hidraw0 o /dev/ttyUSB0 o /dev/hidraw1 etc...
   
> - **Comando:** nos dice el Protocolo que esta usando:

>     - Si el comando es **QPIGS el protocolo sera normalmente el 30 (mas habitual) o el 16**
>     - Si el comando es **^P005GS el protocolo sera el 18**

> - **CRC:** si el equipo usa CRC o no en las comunicaciones

Si no vemos respuesta en ningun test debemos repasar la conexión (cable USB, etc) y repetir el test y, en caso de no conseguirlo, ir al apartado de resolución de problemas

#### 1.1.4.2 Configurando Inicialmente PVControl+ (archivo Parametros_FV.py)

Una vez ya sabemos el puerto, protocolo y CRC que usa nuestro Hibrido debemos decírselo a PVControl+

Para ello PVControl+ usa un archivo muy importante de configuración llamado **Parametros_FV.py** donde se definen muchos de los parámetros de su funcionamiento

Por tanto vamos a ejecutar un programilla de ayuda para la configuración inicial del Hibrido con PVControl+

Desde la venana de **terminal abierta en la carpeta PVControl+** tecleamos:
 
> `python3 PVControl_Configuracion_Inicial_Hibrido.py`

> ![](ayuda/img/intro_conf_hibrido_01.png)

> pulsamos **1** e **Intro** y se nos abre el archivo Parametros_FV.py con un programa llamado Thonny donde debemos poner los datos de nuestra FV (marcados en amarillo)

> ![](ayuda/img/intro_conf_hibrido_02.png)

> Tras actualizar los datos (en el ejemplo cambio a 200 los AH de la bateria, el sistema a 24V y el puerto de comunicaciones a ttyUSB0), debemos guardar y salir

>> ---

>>**ES MUY IMPORTANTE SER CUIDADOSO CON TECLEAR CORRECTAMENTE  (comillas, comas, etc) Y NO PONER CARACTERES RAROS ...PROVOCARA QUE NO FUNCIONE PVControl+**

>> ---

> ![](ayuda/img/intro_conf_hibrido_03.png)

> Se realizan una serie de comprobaciones y al finalizar nos pregunta el estado del SOC actual de la bateria.... pondremos el valor si lo conocemos (por ejemplo 80) y si no lo sabemos pulsamos INTRO directamente 

> ![](ayuda/img/intro_conf_hibrido_04.png)

> **Tras actualizar el SOC nos pide autorizacion  para seguir con la actualizacion de la Web....Pulsamos INTRO**

> ![](ayuda/img/intro_conf_hibrido_05.png)

> **Pulsamos de nuevo INTRO para confirmar la actualizacion de la Web con los datos que se muestran**

> ![](ayuda/img/intro_conf_hibrido_06.png)

> Se actualiza la WEB y nos pide conformacion para reiniciar los servicios .... **pulsamos INTRO**

> ![](ayuda/img/intro_conf_hibrido_07.png)

> Trara reiniciar los servicios finaliza el programa 

> ![](ayuda/img/intro_conf_hibrido_08.png)

> Aunque no es estrictamente necesario, mejor si **reiniciamos la Raspberry**

> Tras reiniciar la Raspberry utilizamos cualquier navegador...

>> PC, Móvil o la propia Raspberry (**NO UTILIZAR el navegador en la Raspberry salvo que sea una RPi 4**)

>> Ponemos en el navegador la IP de la Raspberry y nos debe aparece la Web de PVControl+

> ![](ayuda/img/intro_conf_hibrido_09.png)

> ---

> <span style="color:Darkmagenta"> **Es muy conveniente abrir la pagina de la WEB de Equipos/Equipos para comprobar que todo esta OK y que el Hibrido esta respondiendo correctamente** </span>

> --- 

> ![](ayuda/img/intro_conf_hibrido_10.png)

---

> <span style="color:red">**Ya estaría finalizada la configuración simplificada de PVControl+ para Hibridos tipo Voltronic/Axpert** </span>

> **Para un uso más avanzado (Telegram, etc) ya haría falta ampliar el archivo Parametros_FV.py según se explica en al Manual Completo de Instalación**

> **Para personalizar mas la WEB se debe editar el archivo /html/Parametros_Web.js según se explica en al Manual Completo de Instalación**

--- 





