
//  ====================== Version 2024-01-11 ===========================

// ===========================================================================
//                              ZONA HORARIA
// ===========================================================================

    zona_horaria = 'Europe/Madrid';

// ===========================================================================
// Pagina inicio.php  Actualizar segun los relojes y graficas que se usen
// ===========================================================================

   
   t_refresco = 5000; // tiempo en milisegundos de refresco de la pagina de inicio

  // BAT ==   relojes que estan en opcion baterias
  // RED ==   relojes que estan en opcion RED
  // COMUN == relojes que estan siempre

    // BAT - Reloj Vbat
    Vbat_min = 22; 
    Vbat_bajo_amarillo = 24;
    Vbat_verde = 25.4;
    Vbat_alto_amarillo = 28;
    Vbat_alto_rojo = 30;
    Vbat_max = 32;
    
    // RED -Reloj Vred    
	Vred_min = 200; 
	Vred_bajo_amarillo = 210;
	Vred_verde = 215;
	Vred_alto_amarillo = 240;
	Vred_alto_rojo = 250;
	Vred_max = 270; 

    // BAT - SOC
    SOC_min=20;
    SOC_max=100;
    
    // RED - AC/DC EFICIENCIA
	EFF_min = 20;
	EFF_max = 100;


    // COMUN - Reloj Temp --- considerar que Temp_Vbat_xxx es realmente Temp_Inversor_xxx en sistemas sin bateria
    Temp_bat_min = -10;
    Temp_bat_baja = 10;
    Temp_bat_normal = 20;
    Temp_bat_alta = 30;
    Temp_bat_max = 50;

    Temp_rpi_min = 0;
    Temp_rpi_normal = 40;
    Temp_rpi_alta = 60;
    Temp_rpi_max = 100;

    // COMUN - Reloj Consumo y Autoconsumo en caso de RED
    Consumo_watios_min = 0;
    Consumo_watios_amarillo = 3000;
    Consumo_watios_rojo = 4000;
    Consumo_watios_max = 6000;
      
      //BAT - Aguja Reloj Iconsumo 
       Consumo_amperios_min= 0;
       Consumo_amperios_amarillo = 125;
       Consumo_amperios_rojo = 166;
       Consumo_amperios_max= 210;

    // BAT - Reloj Ibat/Iplaca
    Intensidad_min = -130;
    Intensidad_descarga_amarillo = -40;
    Intensidad_carga_rojo = 80;
    Intensidad_max = 130;

    // RED - Reloj Wred
	Wred_min = -5000;
	Wred_negativo_rojo = -2000;
	Wred_negativo_amarillo = -1000;
	Wred_positivo_amarillo = 500;
	Wred_positivo_rojo = 2000;
	Wred_max = 5000;
    
    
    // COMUN - Reloj Watios Placa
    Watios_placa_baja_rojo = 300;
    Watios_placa_verde = 3000;
    Watios_placa_alta_amarillo = 4500;
    Watios_placa_max = 6000;

    // COMUN - Reloj Vplaca
    Vplaca_baja_amarillo = 40;
    Vplaca_baja_verde = 50;
    Vplaca_verde = 60;
    Vplaca_alta_amarillo = 70;
    Vplaca_max = 80;

  // ==== GRAFICO CELDAS ====
    // Voltaje_celdas
    Vcelda_min = [2.8, 2.8, 2.8, 2.8];
    Vcelda_max = [3.6, 3.6, 3.6, 3.6];

    Vcelda_franja_min = [3.0, 3.0, 3.0, 3.0];
    Vcelda_franja_max = [3.5, 3.5, 3.5, 3.5];
    
    Color_valores = ['rgba(43,41,245,1)','rgba(43,41,145,1)','rgba(43,41,45,1)','rgba(43,41,45,1)'];
    Color_celda_alta = ['rgba(243,41,245,1)','rgba(243,41,245,1)','rgba(243,41,245,1)','rgba(243,41,245,1)'];
    Color_celda_baja = ['rgba(43,241,245,1)','rgba(43,241,245,1)','rgba(43,241,245,1)','rgba(43,241,245,1)'];
    
    Color_valores_max = ['rgba(243,41,45,0.5)','rgba(243,41,45,0.5)','rgba(243,41,45,0.5)','rgba(243,41,45,0.5)'];
    Color_valores_min = ['rgba(243,240,41,0.8)','rgba(243,240,41,0.8)','rgba(243,240,41,0.8)','rgba(243,240,41,0.8)'];
    
    Escala_AH_BMS = [200, 200, 200, 200];
    Escala_intensidad_min_BMS = [-100,-100,-100,-100]
    Escala_intensidad_max_BMS = [100, 100, 100, 100]
    
    
    
  // === Grafico Tiempo Real en inicio.php ====
    Escala_intensidad_min = -140;
    Escala_intensidad_max = 240;

    Escala_Vbat_min = 22;
    Escala_Vbat_max = 35;

        Vabs = 28.8;  // linea Vabs
        Vflot = 27.2; // Linea Vflot
    
    // Watios RED , CONSUMO, PLACA
    Escala_Wred_min = -5000;
    Escala_Wred_max = 6000;


    // COMUN
    Escala_Vplaca_max = 200;
    Escala_PWM_max = 2000; 
    


    // Colores Tabla valores
    SOC_max_rojo = 70;
    SOC_max_naranja = 80;

    SOC_min_rojo = 60;
    SOC_min_naranja = 75;

    Vbat_max_alta_rojo = 30;
    Vbat_max_alta_naranja = 29;
    Vbat_max_baja_rojo = 25;
    Vbat_max_baja_naranja = 27;

    Vbat_min_rojo = 22;
    Vbat_min_naranja = 23;

    Nombre_Aux1 = 'Aux1';
    Unidades_Aux1 = '';
    Usar_color_Aux1 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux1_punto1 = 0;    //Por debajo de este valor, rojo
    Aux1_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux1_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux1_punto4 = 0;    //Por encima de este valor, rojo
	
    Nombre_Aux2 = 'Aux2';
    Unidades_Aux2 = '';
    Usar_color_Aux2 = 0;
    //   R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1   2   3   4
    Aux2_punto1 = 0;    //Por debajo de este valor, rojo
    Aux2_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux2_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux2_punto4 = 0;    //Por encima de este valor, rojo

    Nombre_Aux3 = 'Aux3';
    Unidades_Aux3 = '';
    Usar_color_Aux3 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux3_punto1 = 0;    //Por debajo de este valor, rojo
    Aux3_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux3_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux3_punto4 = 0;    //Por encima de este valor, rojo

    Nombre_Aux4 = 'Aux4';
    Unidades_Aux4 = '';
    Usar_color_Aux4 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux4_punto1 = 0;    //Por debajo de este valor, rojo
    Aux4_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux4_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux4_punto4 = 0;    //Por encima de este valor, rojo
	
    Nombre_Aux5 = 'Aux5';
    Unidades_Aux5 = '';
    Usar_color_Aux5 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux5_punto1 = 0;    //Por debajo de este valor, rojo
    Aux5_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux5_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux5_punto4 = 0;    //Por encima de este valor, rojo
	
    Nombre_Aux6 = 'Aux6';
    Unidades_Aux6 = '';
    Usar_color_Aux6 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux6_punto1 = 0;    //Por debajo de este valor, rojo
    Aux6_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux6_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux6_punto4 = 0;    //Por encima de este valor, rojo
	
    Nombre_Aux7 = 'Aux7';
    Unidades_Aux7 = '';
    Usar_color_Aux7 = 0;
    //R-A-V-A-R   (Definir los 4 puntos de intersección para color)
    // 1 2 3 4
    Aux7_punto1 = 0;    //Por debajo de este valor, rojo
    Aux7_punto2 = 0;    // Entre este valor y el punto3, verde
    Aux7_punto3 = 0;    // Ambar entre 3-4 o 1-2
    Aux7_punto4 = 0;    //Por encima de este valor, rojo
    
    
    // RED - Tabla Colores  RED
	  
	EFF_max_rojo = 70;
	EFF_max_naranja = 80;

	EFF_min_rojo = 60;
	EFF_min_naranja = 75;
    
	Vred_max_alta_rojo = 245;
	Vred_max_alta_naranja = 240;
	Vred_max_baja_rojo = 205;
	Vred_max_baja_naranja = 215;

	Vred_min_rojo = 205;
	Vred_min_naranja = 215;
    
    // Variables Auxilares
    Nombre_Aux1 = 'Aux1';
    Unidades_Aux1 = '';
    
    Nombre_Aux2 = 'Aux2';
    Unidades_Aux2 = '';
    
    Nombre_Aux3 = 'Aux3';
    Unidades_Aux3 = '';
    
    Nombre_Aux4 = 'Aux4';
    Unidades_Aux4 = '';
    
    Nombre_Aux5 = 'Aux5';
    Unidades_Aux5 = '';
    
    Nombre_Aux6 = 'Aux6';
    Unidades_Aux6 = '';
    
    Nombre_Aux7 = 'Aux7';
    Unidades_Aux7 = '';

        
// Pagina Historico1.php,  Historico_horas.php, historico_con_temp.php  ........

    // Se usan los mismos datos puestos en grafica tempo real de inicio.php mas los siguientes parametros:
    
    
    Escala_Vred_min = 180;
    Escala_Vred_max = 280;

        
    Kwh_placa_max = 35;
    
    Kwh_bat_min = -10;
    Kwh_bat_max = 10;
    
    Kwh_red_min = -30;
    Kwh_red_max = 30;
    
    Kwh_consumo_min = 0;
    Kwh_consumo_max = 35;
    
    Temp_min = -10;
    Temp_max = 60;
    
    Modo_max = 10;  // 1= OFF, 2=BULK, 3= FLOT, 4= ABS,  5= EQU, 6= INYEC.RED, 7= CONSUMO RED
    
    Aux1_min = 0;
    Aux1_max = 100;
    
    Aux2_min = 0;
    Aux2_max = 100;
    
    
    // Poner a true si se quiere que aparezcan los ejes en la grafica o false para que no aparezcan
    Eje_Intensidad = true; // Eje Ibat e Iplaca
    Eje_Vbat = true;
    Eje_SOC = false;
    Eje_PWM = false;
    
    Eje_Vplaca = false;
    Eje_Wplaca = false;
    Eje_Wred = false;
    Eje_Vred = false;
    Eje_Wconsumo = false;
    
    Eje_Kwh_placa = false;
    Eje_Kwh_bat = false;
    Eje_Kwh_red = false;
    Eje_Kwh_consumo = false;
    
    Eje_Temp = false;
    Eje_Modo = false;
    
    Eje_Aux1 = false;
    Eje_Aux2 = false;
    
    // Poner a true si se quiere que se muestre la grafica por defecto o false para que salga como desactivada
    Ibat_visible = true;
    Iplaca_visible = true;
    Vbat_visible = true;
    SOC_visible = true;
    PWM_visible = true;
    
    Vplaca_visible = false;
    Wplaca_visible = false;
    Wred_visible = false;
    Wconsumo_visible = false;
    Vred_visible = false;
    
    Kwh_placa_visible = false;
    Kwh_bat_visible = false;
    Kwh_red_visible = false;
    Kwh_consumo_visible = false;
    
    Temp_visible = false;
    Modo_visible = true;
    
    Aux1_visible = false;
    Aux2_visible = false;

    
// Definicion de los graficos personalizados
Grafica_Aux = {
    'TABLA_EJEMPLO' :{
            
    'Subtitulo' : 'Prueba---',
    
    'Ejes': [
             {// ########## 0 - Valores eje 0 ######################
              visible: true,
              opposite: true,
              min: 0,
              max: 200,
              tickInterval: 20,
              gridLineColor: 'transparent',
              minorGridLineColor: 'transparent',
              labels: {
                y: 5
                },
              title: {
                align: 'high',
                offset: -15,
                text: 'Texto en eje 0',
                rotation: 0,
                y: -5
                },
              plotLines: [{
                value: 0,
                width: 2,
                color: 'black',
                dashStyle: 'shortdash'
                }]
             },
             
             {// ########## 1 - Valores Intensidad ######################
              visible: true,
              opposite: false,
              min: -80,
              max: 80,
              tickInterval: 10,
              gridLineColor: 'transparent',
              minorGridLineColor: 'transparent',
              labels: {
                y: 5
                },
              title: {
                align: 'high',
                offset: 0,
                text: 'Texto en eje 1',
                rotation: 0,
                y: -10
                },
              },
              
             {// ########## 2 - Eje autoajuste ######################
              visible: false,
              opposite: true,
              
             },
            ],
    
    'Series': {
        'Variable1': {'eje':1, 'color':'#19ce88', 'tooltip': {valueDecimals: 1, valueSuffix: ' A'}},
        'Variable2': {'eje':1, 'color':'#F76354', 'tooltip': {valueDecimals: 1, valueSuffix: ' A'}},
        'Variable3': {'eje':1, 'color':'#0FF354', 'visible': false , 'tooltip': {valueDecimals: 1, valueSuffix: ' A'}},
        
        'Variable4': {'tipo':'area', 'color':'rgba(255, 183, 51,0.5)' , 'tooltip': {valueDecimals: 1, valueSuffix: ' AH'}},
        'Variable5': {'tipo':'area', 'color':'rgba(51, 242, 255 ,0.2)', 'tooltip': {valueDecimals: 1, valueSuffix: ' AH'}},
        
        
        'Variable6': {'eje':2, 'color':'rgba(255, 183, 51, 1)', 'tooltip': {valueDecimals: 1, valueSuffix: ' WH'}},
        'Variable7': {'eje':2, 'color':'rgba(51, 242, 255 ,0.2', 'tooltip': {valueDecimals: 1, valueSuffix: ' WH'}},
        
    },
    
	},
	
	'TABLA_IRRADIACION':{
        
        'Subtitulo' : 'PREVISION IRRADACION - REALIDAD',
        
        'Ejes': [
                 {// ########## 0 - Valores eje Wh ######################
                  visible: true,
                  opposite: true,
                  //min: 0,
                  //max: 200,
                  //tickInterval: 20,
                  gridLineColor: 'transparent',
                  minorGridLineColor: 'transparent',
                  labels: {
                    //align: 'left',
                    y: 5
                    },
                  title: {
                    align: 'high',
                    offset: -15,
                    text: 'Wh',
                    rotation: 0,
                    y: -5
                    },
                  
                 },
                 
                 {// ########## 1 - Watios ######################
                  visible: true,
                  opposite: false,
                  //min: -80,
                  //max: 80,
                  //tickInterval: 10,
                  //gridLineColor: 'transparent',
                  minorGridLineColor: 'transparent',
                  labels: {
                    //align: 'left',
                    y: 5
                    },
                  title: {
                    align: 'high',
                    offset: 0,
                    text: 'W',
                    rotation: 0,
                    y: -10
                    },
                  plotLines: [{
                    value: 500,
                    width: 2,
                    color: 'red',
                    dashStyle: 'shortdash',
                    label: {
                       text: '500W'
                    }
                    
                    }]
                  },
                 
                 {// ########## 2 - SOC - Temp... ######################
                  visible: false,
                  opposite: false,
                  minorGridLineColor: 'transparent',
                  labels: {
                    //align: 'left',
                    y: 5
                    },
                  title: {
                    align: 'high',
                    offset: 0,
                    text: 'W',
                    rotation: 0,
                    y: -10
                    },
                  plotLines: [{
                    value: 70,
                    width: 2,
                    color: 'red',
                    dashStyle: 'shortdash',
                    label: {
                      text: '70%'
                    }
                    
                  }]
                  },
                  
            ],
        
        'Series': {
            'Wh_placa': {'eje':0, 'tooltip': {valueDecimals: 1, valueSuffix: ' Wh'}, 'visible':true},
            'Wh_bat': {'eje':0, 'tooltip': {valueDecimals: 1, valueSuffix: ' Wh'}, 'visible':false},
            'Wh_red': {'eje':0, 'tooltip': {valueDecimals: 1, valueSuffix: ' Wh'}, 'visible':false},
            'Wh_consumo': {'eje':0, 'tooltip': {valueDecimals: 1, valueSuffix: ' Wh'}, 'visible':false},
            
            
            
            'Wirradiacion': {'eje':1, 'tooltip': {valueDecimals: 1, valueSuffix: ' W'}, 'visible':true},
            
            'Excedente': {'eje':2, 'tooltip': {valueDecimals: 1, valueSuffix: ' Wnor'}, 'visible':false},
            'SOC': {'eje':2, 'tooltip': {valueDecimals: 1, valueSuffix: ' %'}, 'visible':false},
            'Temperatura': {'eje':2, 'tooltip': {valueDecimals: 1, valueSuffix: ' ºC'}, 'visible':false},
            
            
        },  
    },
 
};