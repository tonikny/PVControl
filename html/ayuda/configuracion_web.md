
---
#  Configuración Web PVControl+

---

La configuración de la Web de PVControl+ actualmente está evolucionando.

Los archivos habituales (ubicados en carpeta ../PVControl+/html) en dicha configuración son:


- **version.inc**: Es el archivo en donde con las variables $version  y $archivo_inicio se define la versión de la página de inicio y el menú que aparece...un ejemplo

    ```
    <?php
    // Version de la web
    // SC = bat sin celdas, CC = bat con celdas, RD = sin bat
    $version = "CC";
    $archivo_inicio = "inicio_con_celdas.php";
    ?>
    ```
    Este archivo se crea durante la Configuración Inicial de PVControl+ aunque también se puede crear o modificar con cualquier editor de textos
    
- **Parametros_Web.js** : Archivo en formato de variables Javascript para configurar los distintos parámetros de las gráficas, relojes, etc. (colores, máximos, mínimos,...) 
    - Este archivo controla básicamente todas las posibles configuraciones de las distintas páginas de la Web, si bien, dado que su desarrollo ha ido evolucionando según han aparecido necesidades su estructura no está muy bien consolidada
    
    - No obstante, suele ser bastante intuitivo de modificar según la parte que queramos adaptar de las distintas páginas Web (graficas históricas, etc.) y es editable desde la propia Web 
 
    ![](ayuda/img/Parametros_Web.jpg)

Estos dos archivos, hasta Julio/24, eran los únicos que nos servían para parametrizar la Web de PVControl+

No obstante lo anterior, y a raíz de desarrollar una nueva pagina Web que nos permite **dibujar la instalación FV** con líneas de conexión entre equipos etc. se vio la necesidad de realizar un nuevo planteamiento de la configuración

A fecha de la edición de este manual, **los archivos anteriores siguen siendo necesarios para la configuración de las páginas web de las Gráficas Históricas, Relojes, etc. ..** pero posiblemente esta nueva forma de configuración que se explicará seguidamente evolucionará para permitir una configuración completa de la Web

En el siguiente capítulo intentaremos explicar la configuración y  uso de esta nueva forma de parametrización de la Web 

   
---
#  Configuración Web para el Dibujo de la Instalación FV

---

Según lo comentado, se ha desarrollado una nueva página web (fv.html) que nos permite "Dibujar" con líneas animadas, que simulan conexiones, gráficos con distintos "Bloques" que configuran una instalación FV (Placas solares, Inversores, Baterías, etc. 

En cada Bloque se pueden definir "Elementos" a mostrar como por ejemplo Watios placa, Voltaje batería etc.

Como unas imágenes suelen aclarar más que mucho texto pongo algunos ejemplos de dibujos de instalaciones más o menos complejos para que se tenga una idea antes de entrar a explicar con mayor detalle la forma en la que se realiza la configuración de dichos dibujos


![Animacion1](ayuda/img/Animacion1.gif)

![Animacion2](ayuda/img/Animacion2.gif)

![Animacion3](ayuda/img/Animacion3.gif)

![](ayuda/img/Dibujo_FV_3.JPG)
![](ayuda/img/Dibujo_FV_4.JPG)
 

Lo primero a dejar claro es que **se pueden definir y usar tantos dibujos como se quieran** simplemente guardando con un nombre de archivo distinto cada configuración en la **carpeta ../PVControl+/html/configuraciones**

A su vez se permite cambiar fácilmente desde la propia Web el dibujo a presentar mediante el botón "cambiar configuración" que nos listara los distintos archivos que contenga la carpeta para poder seleccionar el que se quiera mostrar


![](ayuda/img/Dibujo_FV_4_cambio_configuracion.JPG)


A fecha de edición de este manual es posible que a veces se necesite refrescar la página con CTRL + F5 para activar la nueva configuración, aunque se espera corregir este tema

Este cambio de configuración mediante el botón lo que hace simplemente es actualizar el archivo **../PVControl+/html/configuracion_activa.txt** con el nombre del fichero a usar, luego también se puede editar y cambiar manualmente dicho fichero con cualquier editor de texto

----

Una vez explicados los conceptos básicos, veamos cómo se configura, para ello lo primero es ver **las distintas zonas de la pantalla que podemos configurar** 

![](ayuda/img/Dibujo_FV_zonas.JPG)


Como se ve, en esta página Web se han definido distintas zonas de la pantalla, teniendo cada una posibilidad de configuración

Para ello el archivo de configuración se estructura como un único diccionario en formato Javascript llamado **config** al que se le pueden ir definiendo las distintas zonas de configuración

En este sentido es muy recomendable tener un editor de textos que permita "colapsar" o "expandir" los niveles dado que nos ayudara en su edición

Por ejemplo, dentro de la Raspberry se incluye como editor "geany" que nos permite esta opción de ir colapsando niveles 

![](ayuda/img/Dibujo_FV_conf_nivel_0.JPG)


Como se ve se debe empezar por

```

const config = {

```

y acabar con

```
};
``` 

***¡¡¡ESTO ES IMPRESCINDIBLE Y NO SE DEBE MODIFICAR!!!** 

----

Veamos ahora los distintos apartados de dicho archivo de configuracíón

**NO es necesario que los apartados esten en el mismo orden que se muestran**

----

<div style="background-color: #fffbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">menu_web</span>

</div>


Nos permite definir la estructura del menú que nos aparecerá indicando el texto que mostrara el menú y el archivo al que direcciona

![](ayuda/img/Dibujo_FV_conf_menu_web.JPG)

Por tanto cado uno puede configurarse el menu a sus preferencias, añadiendo paginas Web personales si las crea (gráficos etc )



<div style="background-color: #fffbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">laterales</span>

</div>


Nos permite definir los elementos a mostrar tanto de la zona del lateral izquierdo como en el lateral derecho

**Se pueden definir o no según necesidad o preferencias**

![](ayuda/img/Dibujo_FV_conf_laterales.JPG)

Como se observa una vez definido que queremos incluir el lateral izquierdo se dan de alta la clave "elements" en donde colgarán los distintos elementos a mostrar

Veamos con el ejemplo mostrado como se definen dichos elementos:

Cada elemento tiene un nombre, por ejemplo, CONTROL, FV, SOC etc. que es texto libre por lo que cada uno puede poner lo que quiera

De dicho nombre se cuelgan una serie de atributos que parametrizan lo que se mostrará

**Se puede anular el efecto de cada atributo simplemente no declarándolo o poniendo // delante del mismo (// es comentario en Javascript)**

* campoBD: 'FV.SOC', define el campo dentro de la tabla equipos de donde se capturará el valor a mostrar según la sintaxis que se muestra en los ejemplos

* value: 0,  valor inical a mostrar

* unit: '%',  unidades de medida a mostrar como V, ºC etc

* size: '20px', tamaño de letra

* //titleColor: 'black',   color de la letra del titulo

* //valueColor: 'black',   color de la letra del valor

* backgroundColor: '#FFE36C',  color de fondo

* bold: true,     si el texto esta en negrita o no

* showTitle: false,  si se muestra el nombre del elemento o no


Se ha implementado también un sistema de control de avisos que permite cambiar el color de fondo dependiendo de si se cumple o no la condición que se ponga

Se pueden poner tantas condiciones como se quiera

su sintaxis es según se muestra

```
avisos: {
    1: {color:'lightpink', condicion:'value < 70'},
    2: {color:'lightgreen', condicion:'value > 70'},
}, 

```

en lugar de 1, 2 ,.. se puede poner cualquier texto descriptivo de la condición



<div style="background-color: #fffbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">filas (zona central del dibujo)</span>

</div>



**La zona central de la pantalla es donde se dibuja la Instalación FV**

Para ello se deben definir "filas" y dentro de cada fila "bloques"


<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: Arial, sans-serif; line-height: 1.6;">

<p><strong>Dentro de cada bloque se podrá definir:</strong></p>

<ul>
    <li><strong>Imagen y su tamaño</strong></li>
    <li><strong>Conexiones con otros Bloques</strong></li>
    <li><strong>Avisos</strong></li>
    <li><strong>Elementos con datos a mostrar</strong></li>
    <li><strong>Botones de comandos por MQTT</strong></li>
</ul>

</div>


Cada fila nos permite organizar los distintos bloques verticalmente, en cada fila se podrán poner los bloques que queramos simplemente limitados por el tamaño máximo del dibujo que queramos

* Los bloques en una misma fila se separarán horizontalmente y cada fila se separará verticalmente

* Para controlar cuanto se separan los bloques esta la variable **blockMargin**

>> `  blockMargin: '20px 45px 0px 45px', // separacion bloques ..arriba derecha abajo izquierda`


>>    **Este valor de blockMargin se define por defecto para todos los bloques, pero se puede particularizar en cada blque para adaptar el dibujo**



Una vez clarificados algunos conceptos veamos cómo se van definiendo las distintas filas con bloques a dibujar:

Imaginemos que queremos dividir la pantalla en tres filas verticalmente, simplemente daremos de alta tres filas en el archivo de configuración


![](ayuda/img/Dibujo_FV_conf_filas.JPG)


Si ahora desplegamos por ejemplo la fila1 veremos los distintos Bloques dados de alta en dicha fila

 
![](ayuda/img/Dibujo_FV_conf_bloques.JPG)

En donde se ve que se ha dado de alta un único bloque al que hemos denominado placa1

Igualmente si desplegamos todas las filas para ver los bloques dados de alta se observa:

![](ayuda/img/Dibujo_FV_conf_bloques1.JPG)

* En la fila1 tenemos un único bloque llamado Placa1
* En la fila2 tenemos tres bloques llamados Red1, Inversor1 y Casa1
* En la fila3 tenemos un único bloque llamado BATERIA

>> **Como se ve el nombre de cada bloque es libre, pero es importante que sea único y que lo tengamos claro (mayúsculas/minúsculas etc.) para después hacer las conexiones**


Ya podemos ver como se define cada bloque desplegando uno:


![](ayuda/img/Dibujo_FV_conf_bloques2.JPG)


Observamos que el bloque "placa1"  se ha definido:

* image: 'placa1.avif',  nos permite poner cualquier archivo de imagen (png, jpg, avif, etc) que tengamos en carpeta /PVControl+/html/img/equipos

* size: { width: 100, height: 100 }, define el tamaño de la imagen

* connectTo: { id: 'Inversor1', from: 'bottom',  to: 'top', control: 'Wplaca', max: 3000, min: 0,}, donde definimos
>> * el bloque al que se conectara 
>> * Desde donde saldrá la línea (bottom, top, left y right)
>> * Hasta donde llegara la línea (bottom, top, left y right)
>> * El elemento de control que nos servirá para variar dinámicamente el color y grosor de la línea de conexión
>> * el valor máximo y mínimo del elemento de control que se considera para el ancho de la línea de conexión

>> * También se puede definir con `colorLineaPositiva:'black',`  y `colorLineaNegativa:'red',`  los colores de la líneas en caso de valor positivo o negativo...si no se define será Negro/Rojo
 
>> * Igualmente con `flujoLinea:'inverso',` se puede definir que la animación de la línea sea desde bloque destino a bloque origen...si no se define será desde bloque origen a destino


>> ***Se permite definir varias líneas por bloque, en ese caso se debe introducir en connectTo un diccionario con todas las líneas que se quieran***

>>>  connectTo: {

>>>>   Linea1:{id: ....}, 

>>>>   Linea2:{id: ....}

>>>  }  

>> Si de un bloque no sale ninguna línea se debe poner `connectTo: null,` 


* con respecto al tema de **"avisos" a nivel de bloque,** nos permite definir condiciones que si se cumplen se podrá cambiar la imagen, color de fondo ,---- además se podra o no mostrar un signo de "aviso" con parpadeo

> En este caso para dar más flexibilidad la sintaxis de las condiciones está basada en javascript, por lo que para acceder al dato de Wplaca del registro FV de la tabla equipos se define segun  `d_["FV"]["Wplaca"]` en lugar de la sintaxis abreviada que podemos usar en el atributo campoBD de los elementos que sería `FV.Wplaca`

> Así por ejemplo se ve una condición para que se ponga el fondo en color cyan si el registro FV de la tabla equipos tienen una fecha/hora más antigua de 1 minuto sobre la fecha/hora actualizar

>> `3: {color:'cyan', condicion:'new Date(d_["FV"]["tiempo"]) < new Date(now.getTime() - 1 * 60 * 1000)'},//1 minuto`


* Elements: Ya podemos definir los distintos elementos a mostrar con una sintaxis muy similar a cuando los definimos en la zona lateral pero donde también tenemos los atributos:

> * position: { x: 36, y: 47 }, para colocar en coordenadas x,y con respecto al bloque donde se mostrara el valor
> * sensor:   nos permite definir con más flexibilidad que campoBD a través de expresiones javascript el origen del valor a mostrar, permitiendo operaciones aritméticas etc.
> * visualizacion:   nos permite definir si el elemento se mostrará en la ventana normal o solo en la modal.


<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: Arial, sans-serif; line-height: 1.6;">

<p><strong>Por tanto para seleccionar el dato que queremos mostrar en cada elemento tenemos dos posibles alternativas:</strong></p>

<ul>
    <li><strong>campoBD : con una sintaxis mas facil de usar y permite acceder a cualquier campo de la tabla equipos</strong></li>
    <li><strong>sensor : con una sintaxis algo mas compleja, pero nos permite realizar operaciones (suma, resta, )... o cualquier expresión javascript para acceder al dato que queremos mostrar</strong></li>
</ul>

</div>

> * Tambien existe la posibilidad de establecer **"avisos" a nivel de cada elemento** nos permite definir condiciones que si se cumplen se podrá cambiar color de texto, color de fondo , visualizacion, etc


![](ayuda/img/avisos_elementos_1.jpg)

![](ayuda/img/avisos_elementos_2.jpg)


<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: Arial, sans-serif; line-height: 1.6;">

<p><strong>La posibilidad de establecer AVISOS tanto a nivel de BLOQUE como en cada ELEMENTO nos permite configurar de una forma versátil y visual lo que se muestra en a Web</strong></p>

<p><strong>Es IMPORTANTE tener en cuenta que los datos que se pueden mostrar en los ELEMENTOS son aquellos que están en la tabla EQUIPOS</strong></p>

</div>


Por tanto, debemos configurar el archivo Parametros_FV.py para que se capturen todos los datos que queremos representar


Así, si queremos representar la Vbat que captura tanto un Hibrido Anenji como de varios BMS JK,  debemos tener esos datos disponibles en la pestaña equipos


![](ayuda/img/Equipos_Vbat.PNG)



<div style="background-color: #fffbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">gráficas</span>

</div>


Nos permite incorporar en la parte de debajo del Dibujo de la FV  las paginas Web que se deseen (Historico de carga, Kwh, etc)

Se define según la siguiente estructura:


![](ayuda/img/Definicion_graficas.JPG) 


* columnas:  define las columnas de la cuadricula donde colocaremos las distintas paginas Web, permitiendo por ejemplo si se definen dos columnas colocar dos paginas web en la misma fila

* archivos : lista de las paginas web que queremos mostrar con la expresión del archivo a mostrar, tamaño , borde y la colocacion dentro de la cuadricula "gridArea"

> Expliquemos un poco mas el uso de gridArea:

>> La sintaxis es  gridArea: Fila_Inicial / Columna_Inicial / Fila_Final / Columna_Final

>> Asi por ejemplo:  

>>>  gridArea: '1 / 1 / 2 / 3'  implica que ocupará desde la fila 1 hasta la fila 2 y desde la columna 1 hasta la 3 (todo el ancho)

>>>  gridArea: '2 / 1 / 3 / 3'  implica que ocupará desde la fila 2 hasta la fila 3 y desde la columna 1 hasta la 3 (todo el ancho)

>>>  gridArea: '3 / 1 / 4 / 2'  implica que ocupará desde la fila 3 hasta la fila 4 y desde la columna 1 hasta la 2 (mitad del ancho izquierdo)

>>>  gridArea: '3 / 2 / 4 / 3'  implica que ocupará desde la fila 3 hasta la fila 4 y desde la columna 2 hasta la 3 (mitad del ancho derecho)

> Por tanto, usando el ejemplo de definición que hemos puesto (grafica historica y Kwh) nos dará esta salida debajo del Dibujo 


> ![](ayuda/img/Grafica_0.JPG) 

> Si cambiamos la definición para mostrar en la parte de abajo dos gráficas ( por ejmplo KWh y promedios) tendríamos la siguiente definición


> ![](ayuda/img/Definicion_graficas_1.JPG)

> que nos dará la siguiente salida
 

> ![](ayuda/img/Grafica_1.JPG) 


<div style="background-color: #fffbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">MQTT</span>

</div>


En PVControl+ se usa extensivamente MQTT (actuar sobre reles, cambiar psrametros de equipos, etc)

Por tanto se ha incorporado la posibilidad de conectarse al broker MQTT y poder definir **botones a nivel de bloque** que envien comandos  (activar un rele,  etc)

Los pasos para su uso son:

> Configurar la conexión al Broker MQTT

> Creación de los botones en los bloques donde se quiera utilizar

Empecemos por la configuracion del broker:

> ![](ayuda/img/MQTT_0.JPG)

> Define los parámetros de conexión al Broker MQTT (IP del servidor, puerto, usuario, clave) asi como la clave que nos solicitará la pagina Web si queremos activar un boton "protegido" según lo que veremos mas adelante "clave_web"

> Si queremos que los valores no se muestren en la pestaña de parametros incluiremos al final  // *** para que se oculten


Una vez configurada la conexión MQTT veamos como se dan de alta a nivel de cada bloque los botones que enviarán comandos MQTT

Imaginemos que tenemos un bloque de un enchufe TASMOTA que queremos mostrar y poder cambiar el modo de funcionamiento mediante 3 botones (ON, OFF , PRG )

Queremos que el boton de ON nos solicite la clave si lo pulsamos, y en los botones de OFF y PRG no queremos usar clave

La configuración sería añadir en la definición del bloque tras la parte de los "elementos", una nueva parte "comandos":

> ![](ayuda/img/MQTT_1.JPG)

 
con dicha configuración al pulsar en el bloque se nos abrirá una ventana modal que incluye los botones que se han definido

> ![](ayuda/img/MQTT_2.JPG)

 
 
 Otro ejemplo podría ser si queremos mandarle algun comando a un equipo (MPPT, Hibrido, etc) que admite configuración por MQTT o Telegram como por ejemplo los MPPT Easun, Hibridos Anenji etc
 
 En este caso podemos ver una posible configuración de botones que cambiarían el valor de Vabs y Vflot de un MPPT Easun
 
> ![](ayuda/img/MQTT_3.JPG) 

> En este caso se muestra la posibilidad de "organizar los botones en filas"....dando el siguiente resultado


> ![](ayuda/img/MQTT_4.JPG) 


Otro ejemplo podria ser la configuración de BMS JK para activar/descativar mosfet de carga/descarga y la conexión Bluetooth

> ![](ayuda/img/MQTT_5.JPG) 

> que nos daría la siguiente salida

> ![](ayuda/img/MQTT_6.JPG) 
 

Un último ejemplo para poder usar una SQL para actuar sobre la Base de datos (**¡¡¡cuidado con su uso si no se sabe utilizar SQL!!!**)

En este caso queremos incrmentar o decrementar en 0.01 el valor de objetivo_PID que se guarda en la tabla parametros

> ![](ayuda/img/MQTT_7.JPG) 

> ![](ayuda/img/MQTT_8.JPG) 


Otra característica de la integración con MQTT es que cada vez que se reciba un mensaje en el topic "PVControl/WEB" se nos abrirá una ventana mostrando los mensajes recibidos

> ![](ayuda/img/MQTT_9.JPG) 

> ![](ayuda/img/MQTT_10.JPG) 

<div style="background-color: #00fbcc; padding: 20px; border-radius: 8px; border: 2px solid #ffcc00; text-align: center; font-size: 1.5em;">

<span style="color: blue; font-weight: bold;">Ver/Modificar archivos de configuración</span>

</div>

Para facilitar la edición y modificación de los archivos de configuración desde la propia web se ha creado la pestaña "parametros" que nos muestra y nos permite editar los distintos archivos de configuración de PVControl+

> Parametros_FV.py : configura la captura de los distintos equipos en los programas de python, graficos personalizados, bot de telegram etc

> Parametros_Web.js : Mientras no se integre en el archivo siguiente sirve para configurar las distintas gráficas creadas en PVControl+ (valores máximos, mínimos, ejes etc)

> Configuración del "Dibujo de la FV": el archivo que hemos tratado en este apartado
 
> **Además de estos tres archivos de texto, para la configuración de PVControl+ existe también la tabla parametros en base de datos que se puede modificar con phpmyadmin, Telegram o desde el propio Dibujo de la FV creando botones del tipo SQL**
 
 
> ![](ayuda/img/parametros_0.JPG) 

> ![](ayuda/img/parametros_1.JPG)

Si activamos la edición (clave por defecto "fv") ....ya podremos ver y editar los archivos

> ![](ayuda/img/parametros_2.JPG)



<div style="background-color: #f0f8ff; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: Arial, sans-serif; line-height: 1.6;">

<p><strong>¡¡¡ATENCION HAY QUE SER CUIDADOSO EN LA EDICION DE ESTOS ARCHIVOS!!!</strong></p>

<ul>
    <li><strong>Un error en el archivo Parameros_FV.py nos provocara fallos en la captura de los equipos mostrándonos fallo en la tabla equipos</strong><br>
    En este caso el "status" de la tabla equipos nos dara una idea, tambien podemos ejecutando el archivo Parametros_FV.py para analizar la causa del error (python Parametros_FV.py)
    </li>
    <br>
    <li><strong>Un error en el archivo de configuración del dibujo de la FV nos provocará que dicho dibujo deje de verse o se verá con fallos</strong> <br>
    En este caso pulsar F12 en el navegador y abrir la consola nos dara pistas del error</li>
</ul>

</div>

 
