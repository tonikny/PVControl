
// Pagina inicio_XXXX.php
// Actualizar los relojes necesarios y demas variables de acuerdo a la instalacion
// 

	// Reloj Vbat
	Vbat_min = 44; 
	Vbat_bajo_amarillo = 48;
	Vbat_verde = 50.8;
	Vbat_alto_amarillo = 56;
	Vbat_alto_rojo = 60;
	Vbat_max = 64; 

    // Reloj Vred    
	Vred_min = 200; 
	Vred_bajo_amarillo = 210;
	Vred_verde = 215;
	Vred_alto_amarillo = 240;
	Vred_alto_rojo = 250;
	Vred_max = 270; 
    
	// SOC
	SOC_min=60;
	SOC_max=100;

    // AC/DC EFICIENCIA
	EFF_min = 60;
	EFF_max = 100;
	
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
	Consumo_amperios_amarillo = 60;
	Consumo_amperios_rojo = 80;
	Consumo_amperios_max= 100;

	// Reloj Ibat/Iplaca
	Intensidad_min = -65;
	Intensidad_descarga_amarillo = -20;
	Intensidad_carga_rojo = 40;
	Intensidad_max = 65;

    // Reloj Excedentes
	Wred_min = -5000;
	Wred_negativo_rojo = -2000;
	Wred_negativo_amarillo = -1000;
	Wred_positivo_amarillo = 500;
	Wred_positivo_rojo = 2000;
	Wred_max = 5000;
    
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
	Escala_intensidad_min = -65;
	Escala_intensidad_max = 100;

	Escala_Vbat_min = 44;
	Escala_Vbat_max = 140;
    Vabs = 57.6;  // linea Vabs
	Vflot = 54.4; // Linea Vflot
    
    Escala_Wred_min = -5000;
	Escala_Wred_max = 5000;
    
    Vred_alto = 240;  // linea Vred alto
	Vred_bajo = 200; // Linea Vred bajo
	
    Escala_PWM_max = 400; 
	Escala_Vplaca_max = 400; 


	// Tabla Colores
	SOC_max_rojo = 70;
	SOC_max_naranja = 80;

	SOC_min_rojo = 60;
	SOC_min_naranja = 75;

	Vbat_max_alta_rojo = 60;
	Vbat_max_alta_naranja = 58;
	Vbat_max_baja_rojo = 50;
	Vbat_max_baja_naranja = 54;

	Vbat_min_rojo = 44;
	Vbat_min_naranja = 46;
	
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
    
    Nombre_Aux1 = 'Aux1'
    Nombre_Aux2 = 'Aux2'
    Nombre_Aux3 = 'Aux3'
    Nombre_Aux4 = 'Aux4'
	Nombre_Aux5 = 'Aux5'
    Nombre_Aux6 = 'Aux6'
	Nombre_Aux7 = 'Aux7'
	
	
// Pagina Historico1.php,  Historico_horas.php, historico_con_temp.php  ........

	// Se usan los mismos datos puestos en el Grafico Tiempo Real de inicio.php
	Escala_Aux1_min = 0;
	Escala_Aux1_max = 120;

	


