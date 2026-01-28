
---
# 1 - Gráficas Personalizadas

---
Aunque PVControl+ incluye uan serie de gráficas bastante útiles (carga diaria, Kwh al día, etc), es bastante posible que dependiendo del equipamiento que tengamos en la FV deseemos añadir alguna gráfica adicional, por ejemplo:


- Tengo varios sensores de temperatura y quiero tener una gráfica histórica de los mismos

- Tengo varios reguladores MPPT y querría ver gráficamente la producción de cada uno de ellos

- Tengo varios BMS y querría ver gráficas adicionales a las que tiene por defecto PVControl+

- etc..

En este manual se intenta explicar los pricipios básicos del uso de las gráficas personalizadas para lo que se usaran algunos ejemplos sencillos que permitan ver su configuración y funcionalidad

**SE PODRAN CREAR TANTAS GRAFICAS PERSONALIZADAS COMO SE QUIERA... si bien es recomendable tener consideraciones de espacio disponible en microSD, tiempo de ejecución, etc**


Los pasos básicos para crear una gráfica personalizada serían:

----

- <span style="color:blue">**En el archivo Parametros_FV.py**</span>

	- Definir el nombre de la tabla en la base de datos donde se guardaran los datos

	- Definir las variables que se desean guardar y cada cuanto tiempo se guarda un registro

	**Esta configuración de Parametros_FV.py es OBLIGATORIA para poder usar gráficas personalizadas**

----

- <span style="color:blue">**En el archivo html/Parametros_Web.js**</span>

	- Ajustar la visualización de la gráfica (Ejes, escalas, visible por defecto o no, etc) 

	**Esta configuración de Parametros_Web.js es OPCIONAL y sirve para ajustar mejor a nuestros gustos las gráficas**


Veamos pues ambas partes de dicha configuración
 
----

## <span style="color:blue">**1.1 Configuración de Parametros_FV.py**</span>

----

Como se ha comentado esta parte es OBLIGATORIA ...veamos algun ejemplo sencillo....

Imaginemos que tenemos captura del voltaje de bateria desde varios dispositivos... 

- Dos Hibridos Anenji que hemos definido como ANENJI1 y ANENJI2

- Dos reguladores MPPT Easun que hemos definido como MPPT1 y MPPT2

- Cuatro BMS JK que hemos definido como JK1, JK2, JK3 y JK4

- Un ADS1115 que esta definido como ADS1

Queremos sacar una gráfica que nos muestre todos esos valores y asi poder comparar facilmente 

Los pasos a seguir en Parametros_FV.py serian:

1. Asegurar que tenemos las variables definidas en la parte de "sensores" para poder usarlas
1. Definir la gráfica (Nombre de tabla, variables,...) en el apartado "Graficas_aux"

Si hemos definido bien la parte de **sensores** nos aparecera en la pestaña **Equipos** un registro por cada equipo en donde podemos identificar facilmente los datos que queremos incluir en nuestra gráfica 


![](ayuda/img/Equipos_Vbat.PNG)

Por tanto podemos definir unas variables con el nombre que queramos donde se guarden esos valores

Para ello **EN LA PARTE DE SENSORES** definiremos las variables que queremos usar

![](ayuda/img/definicion_variables.png)

Se podia haber optado por poner una sintaxis mas simple tipo

```
	
	'Vbat_ADS1' : {"d_['ADS1']['Vbat']"}
	
```

> Pero eso tendría el incoveniente que no podemos ajustar los decimales que queremos usar, y que si el registro ADS1 no existe en tabla equipos daria error


Con la sintaxis que se ha puesto 

```
	
	'Vbat_ADS1' : {"round(d_['ADS1']['Vbat'],2) if 'ADS1' in d_ else 0"}
	
```

> se redondea el valor a dos decimales y si no existe el registro ADS1 en tabla equipos se asigna el valor 0

---

Una vez ya definidas las variables... Vbat\_JK1, Vbat\_JK2, etc pasamos a definir la gráfica propiamente
 
![](ayuda/img/definicion_grafica_aux.png)


Unas consideraciones a esta definición:

- Nombre: **DEBE EMPEZAR por TABLA\_**

- activo: se pone a 1 para activar la captura y a 0 para desactivarla

- tmuestra: tiempo en segundos entra cada captura.... hay que tener en cuenta que si ponemos un tiempo muy pequeño la tabla asociada crecerá de tamaño proporcionalmente

- variables: se definen las variables a usar
> Se pueden poner todas en una unica linea en cuyo caso NO son necesarios los parentesis

> Se pueden utilizar cualquier variable que se tenga accesible como por ejemplo directamente Vbat, Ibat, PWM etc



> ---

> <span style="color:Darkmagenta"> **Con esto ya estaría definida la gráfica y ya se podría ver:**</span>

>> <span style="color:Darkmagenta">El registro correspondiente en la pestaña Equipos</span>
 
>> <span style="color:Darkmagenta">El grafico en la pestaña Hist_Personal </span>

> --- 

 
![Registro_en_Equipos|10](ayuda/img/tabla_vbat.png)

 
![Grafica_Vbat](ayuda/img/grafica_vbat.png)


> --- 

> **Tanto las escalas, colores, etc que mostrará la gráfica serán las definidas por defecto...si se quiere personalizar esta parte ya habría que configurar el archivo Parametros_Web.js según el apartado siguiente**

> --- 

<br>
<br>
<br>


----

## <span style="color:blue">**1.2 Configuración de Parametros_Web.js**</span>

----

Esta configuración el **OPCIONAL** y se puede configurar parcialmente (unas tablas si otras no, unas variables si otras no etc)


**PENDIENTE ESCRIBIR**

