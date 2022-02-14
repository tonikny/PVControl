
// Pagina inicio.php

	// Reloj Vbat
	Vbat_min = 22; 
	Vbat_bajo_amarillo = 24;
	Vbat_verde = 25.4;
	Vbat_alto_amarillo = 28;
	Vbat_alto_rojo = 30;
	Vbat_max = 32; 

	// SOC
	SOC_min=60;
	SOC_max=100;


	// reloj Temp
	Temp_bat_min = -10;
	Temp_bat_baja = 10;
	Temp_bat_normal = 20;
	Temp_bat_alta = 30;
	Temp_bat_max = 50;

	Temp_rpi_min = 0;
	Temp_rpi_normal = 40;
	Temp_rpi_alta = 60;
	Temp_rpi_max = 100;

	// Reloj Consumo
	Consumo_watios_min = 0;
	Consumo_watios_amarillo = 3000;
	Consumo_watios_rojo = 4000;
	Consumo_watios_max = 5000;

	Consumo_amperios_min= 0;
	Consumo_amperios_amarillo = 125;
	Consumo_amperios_rojo = 166;
	Consumo_amperios_max= 210;

	// Reloj Ibat/Iplaca
	Intensidad_min = -130;
	Intensidad_descarga_amarillo = -40;
	Intensidad_carga_rojo = 80;
	Intensidad_max = 130;


	// Reloj Watios Placa
	Watios_placa_baja_rojo = 300;
	Watios_placa_verde = 3000;
	Watios_placa_alta_amarillo = 4500;
	Watios_placa_max = 6000;

	// Reloj Vplaca
	Vplaca_baja_amarillo = 40;
	Vplaca_baja_verde = 50;
	Vplaca_verde = 60;
	Vplaca_alta_amarillo = 70;
	Vplaca_max = 80;


	// Voltaje_celdas
	Vcelda_min = 1.7;
	Vcelda_max = 2.6;

	Vcelda_franja_min = 1.8;
	Vcelda_franja_max = 2.5;
	
	// Grafico Tiempo Real
	Escala_intensidad_min = -140;
	Escala_intensidad_max = 240;

	Escala_Vbat_min = 22;
	Escala_Vbat_max = 35;

	Vabs = 28.8;  // linea Vabs
	Vflot = 27.2; // Linea Vflot

	Escala_PWM_max = 800; 
	Escala_Vplaca_max = 400; 


	// Tabla Colores
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
	
    Nombre_Aux1 = 'Vbat2_12v'
    Unidades_Aux1 = 'V'
    
    Nombre_Aux2 = 'Vbat2_0v'
    Unidades_Aux2 = 'V'
    
    Nombre_Aux3 = 'Wpl_H'
    Unidades_Aux3 = 'W'
    
    Nombre_Aux4 = 'PACW_H'
	Unidades_Aux4 = 'W'
    
    Nombre_Aux5 = 'COTEX'
    Unidades_Aux5 = 'W'
    
    Nombre_Aux6 = 'Aux6'
	Unidades_Aux6 = ''
    
    Nombre_Aux7 = 'Dif_Cel'
	Unidades_Aux7 = 'mV'
    
// Pagina Historico1.php,  Historico_horas.php, historico_con_temp.php  ........

	// Se usan los mismos datos puestos en inicio.php mas los siguientes:
	
    Vred_max = 300
    Watios_red_min = -2000
    Watios_red_max = 2000
    
    Kwh_placa_max = 35
    
    Kwh_bat_min = -10
    Kwh_bat_max = 10
    
    Kwh_red_min = -30
    Kwh_red_max = 30
    
    Kwh_consumo_min = -30
    Kwh_consumo_max = 30
    
    Aux1_min = 12
	Aux1_max = 15
    
    Aux2_min = 12
	Aux2_max = 15
    
    
    // Poner a true si se quiere que aparezcan los ejes en la grafica o false para que no aparezcan
    Eje_Intensidad = true // Ibat e Iplaca
    Eje_Vbat = false
    Eje_SOC = false
    Eje_PWM = false
    
    Eje_Vplaca = false
    Eje_Wplaca = false
    Eje_Wred = false
    Eje_Vred = false
    Eje_Wconsumo = false
    
    Eje_Kwh_placa = false
    Eje_Kwh_bat = false
    Eje_Kwh_red = false
    Eje_Kwh_consumo = false
    
    Eje_Temp = false
    
    Eje_Aux1 = false
    Eje_Aux2 = false
    
    // Poner a true si se quiere que aparezca la grafica por defecto o false para que este desactivada
    Ibat_visible = true
    Iplaca_visible = true
    Vbat_visible = true
    SOC_visible = true
    PWM_visible = true
    
    Vplaca_visible = false
    Wplaca_visible = false
    Wred_visible = false
    Wconsumo_visible = false
    Vred_visible = false
    
    Kwh_placa_visible = false
    Kwh_bat_visible = false
    Kwh_red_visible = false
    Kwh_consumo_visible = false
    
    Temp_visible = false
    
    Modo_visible = true
    
    Aux1_visible = false
    Aux2_visible = false
    