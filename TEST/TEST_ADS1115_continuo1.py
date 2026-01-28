import Adafruit_ADS1x15 
import time
import math

# CONFIGURACIÓN
n_medidas = 12    # número de lecturas para una medida
gain = 16         # ganancia ADS
datarate = 16     # datarate ADS  
shunt_sensibilidad = 0.050 / 500  # 50mV/500A
t_muestra = 5     # tiempo entre muestras

# Cálculo correcto del factor de conversión
# ADS1115 con gain=16: ±0.256V, 15 bits efectivos (32767 counts)
voltaje_por_count = 0.256 / 32768.0  # 7.8125 µV por count
factor_conversion = voltaje_por_count / shunt_sensibilidad

print(f"Configuración ADS1115:")
print(f"  Ganancia: {gain} -> Rango: ±0.256V")
print(f"  Voltaje por count: {voltaje_por_count * 1000000:.4f} µV")
print(f"  Sensibilidad shunt: {shunt_sensibilidad * 1000:.3f} mV/A")
print(f"  Factor conversión: {factor_conversion:.6f} A/count")
print(f"  Resolución: {factor_conversion * 1000:.3f} mA por count")

# Códigos de colores ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Inicializamos ADS en dirección 0x48 y bus=1 
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

# Configuramos lectura Continuo_Diferencial en A0-A1
# 0 = A0 vs A1 -- 1 = A0 vs A3 -- 2 = A1 vs A3 -- 3 = A2 vs A3

adc.start_adc_difference(0, gain=gain, data_rate=datarate)

def calcular_media(lecturas):
    """Calcula la media de una lista de lecturas"""
    return sum(lecturas) / len(lecturas) if lecturas else 0

def calcular_desviacion(lecturas):
    """Calcula la desviación estándar de una lista de lecturas"""
    if len(lecturas) <= 1:
        return 0
    media = calcular_media(lecturas)
    varianza = sum((x - media) ** 2 for x in lecturas) / (len(lecturas) - 1)
    return math.sqrt(varianza)

def calcular_estadisticas(lecturas):
    """Calcula diversas estadísticas de un conjunto de lecturas"""
    if not lecturas:
        return {}
    
    # Estadísticas básicas
    media = calcular_media(lecturas)
    desviacion = calcular_desviacion(lecturas)
    minimo = min(lecturas)
    maximo = max(lecturas)
    rango = maximo - minimo
    
    # Conversión a corriente
    corriente_media = media * factor_conversion
    corriente_min = minimo * factor_conversion
    corriente_max = maximo * factor_conversion
    
    # Lecturas sin valores extremos
    if len(lecturas) > 2:
        lecturas_sin_extremos = sorted(lecturas)[1:-1]  # Elimina min y max
        media_sin_extremos = calcular_media(lecturas_sin_extremos)
        desviacion_sin_extremos = calcular_desviacion(lecturas_sin_extremos)
        corriente_media_sin_extremos = media_sin_extremos * factor_conversion
    else:
        lecturas_sin_extremos = lecturas
        media_sin_extremos = media
        desviacion_sin_extremos = desviacion
        corriente_media_sin_extremos = corriente_media
    
    return {
        'n_lecturas': len(lecturas),
        'lecturas_raw': lecturas.copy(),
        'media_raw': media,
        'desviacion_raw': desviacion,
        'min_raw': minimo,
        'max_raw': maximo,
        'rango_raw': rango,
        'media_sin_extremos_raw': media_sin_extremos,
        'desviacion_sin_extremos_raw': desviacion_sin_extremos,
        'corriente_media': corriente_media,
        'corriente_min': corriente_min,
        'corriente_max': corriente_max,
        'corriente_media_sin_extremos': corriente_media_sin_extremos,
        'lecturas_sin_extremos': lecturas_sin_extremos
    }

def mostrar_lecturas_coloreadas(lecturas, titulo):
    """Muestra las lecturas individuales con colores para min/max"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{titulo}:{Colors.END}")
    print("-" * 60)
    
    min_val = min(lecturas)
    max_val = max(lecturas)
    
    for i, lectura in enumerate(lecturas, 1):
        corriente = lectura * factor_conversion
        
        # Aplicar colores según si es min, max o normal
        if lectura == min_val and len(lecturas) > 1:
            color = Colors.BLUE
            indicador = " (MIN)"
        elif lectura == max_val and len(lecturas) > 1:
            color = Colors.RED
            indicador = " (MAX)"
        else:
            color = Colors.WHITE
            indicador = ""
        
        print(f"  {Colors.YELLOW}Lectura {i:2d}:{Colors.END} {color}{lectura:8.2f} RAW{Colors.END} -> {Colors.GREEN}{corriente:8.3f} A{Colors.END}{color}{indicador}{Colors.END}")

def mostrar_resumen_final(stats):
    """Muestra un resumen final con colores de todas las estadísticas"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}          RESUMEN FINAL DE ESTADISTICAS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
    
    print(f"{Colors.BOLD}{Colors.CYAN}INFORMACION GENERAL:{Colors.END}")
    print(f"  {Colors.YELLOW}Numero de lecturas:{Colors.END} {Colors.WHITE}{stats['n_lecturas']}{Colors.END}")
    print(f"  {Colors.YELLOW}Rango de valores RAW:{Colors.END} {Colors.BLUE}{stats['min_raw']:.2f}{Colors.END} {Colors.WHITE}->{Colors.END} {Colors.RED}{stats['max_raw']:.2f}{Colors.END} {Colors.WHITE}(dif. {stats['rango_raw']:.2f}){Colors.END}")
    print(f"  {Colors.YELLOW}Rango de corriente:{Colors.END} {Colors.BLUE}{stats['corriente_min']:.3f} A{Colors.END} {Colors.WHITE}->{Colors.END} {Colors.RED}{stats['corriente_max']:.3f} A{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}ESTADISTICAS CON TODAS LAS LECTURAS:{Colors.END}")
    print(f"  {Colors.YELLOW}Media:{Colors.END}          {Colors.WHITE}{stats['media_raw']:10.2f} RAW{Colors.END} -> {Colors.GREEN}{stats['corriente_media']:10.3f} A{Colors.END}")
    print(f"  {Colors.YELLOW}Desviacion:{Colors.END}     {Colors.WHITE}{stats['desviacion_raw']:10.2f} RAW{Colors.END} -> {Colors.GREEN}{stats['desviacion_raw'] * factor_conversion:10.3f} A{Colors.END}")
    
    if len(stats['lecturas_raw']) > 2:
        print(f"\n{Colors.BOLD}{Colors.CYAN}ESTADISTICAS SIN VALORES EXTREMOS:{Colors.END}")
        print(f"  {Colors.YELLOW}Media:{Colors.END}          {Colors.WHITE}{stats['media_sin_extremos_raw']:10.2f} RAW{Colors.END} -> {Colors.GREEN}{stats['corriente_media_sin_extremos']:10.3f} A{Colors.END}")
        print(f"  {Colors.YELLOW}Desviacion:{Colors.END}     {Colors.WHITE}{stats['desviacion_sin_extremos_raw']:10.2f} RAW{Colors.END} -> {Colors.GREEN}{stats['desviacion_sin_extremos_raw'] * factor_conversion:10.3f} A{Colors.END}")
        
        # Calcular mejoras
        if stats['desviacion_raw'] > 0:
            mejora_desviacion = (1 - stats['desviacion_sin_extremos_raw'] / stats['desviacion_raw']) * 100
            dif_corriente = abs(stats['corriente_media'] - stats['corriente_media_sin_extremos'])
            dif_porcentaje = (dif_corriente / abs(stats['corriente_media']) * 100) if stats['corriente_media'] != 0 else 0
            
            print(f"\n{Colors.BOLD}{Colors.CYAN}MEJORAS AL ELIMINAR EXTREMOS:{Colors.END}")
            if mejora_desviacion > 0:
                print(f"  {Colors.YELLOW}Reduccion desviacion:{Colors.END} {Colors.GREEN}{mejora_desviacion:+.1f}%{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}Reduccion desviacion:{Colors.END} {Colors.RED}{mejora_desviacion:+.1f}%{Colors.END}")
            
            print(f"  {Colors.YELLOW}Diferencia en corriente:{Colors.END} {Colors.WHITE}{dif_corriente:.6f} A ({dif_porcentaje:.3f}%){Colors.END}")
    
    # Evaluación de calidad de medición
    print(f"\n{Colors.BOLD}{Colors.CYAN}EVALUACION DE CALIDAD:{Colors.END}")
    if stats['media_raw'] != 0:
        coef_variacion = (abs(stats['desviacion_raw']) / abs(stats['media_raw']) * 100)
        if coef_variacion < 2:
            evaluacion = f"{Colors.GREEN}EXCELENTE{Colors.END}"
        elif coef_variacion < 5:
            evaluacion = f"{Colors.GREEN}BUENA{Colors.END}"
        elif coef_variacion < 10:
            evaluacion = f"{Colors.YELLOW}ACEPTABLE{Colors.END}"
        else:
            evaluacion = f"{Colors.RED}ALTA VARIACION{Colors.END}"
        print(f"  {Colors.YELLOW}Coeficiente de variacion:{Colors.END} {Colors.WHITE}{coef_variacion:.1f}%{Colors.END} -> {evaluacion}")
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")

# BUCLE PRINCIPAL
try:
    ciclo = 0
    while True:
        ciclo += 1
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'#'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}    CICLO DE MEDICION #{ciclo} - CANAL A2-A3{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'#'*70}{Colors.END}")
        
        # Adquirir lecturas
        lecturas = []
        print(f"\n{Colors.YELLOW}Adquiriendo {n_medidas} lecturas desde A2-A3...{Colors.END}")
        
        for i in range(n_medidas):
            lectura = adc.get_last_result()
            lecturas.append(lectura)
            time.sleep(1/datarate)
        
        # Calcular estadísticas
        estadisticas = calcular_estadisticas(lecturas)
        
        # Mostrar lecturas una vez con colores
        mostrar_lecturas_coloreadas(estadisticas['lecturas_raw'], "LECTURAS CAPTURADAS (A2-A3)")
        
        # Mostrar resumen final con colores
        mostrar_resumen_final(estadisticas)
        
        # Espera entre conjuntos de mediciones
        print(f"\n{Colors.YELLOW}Esperando {t_muestra} segundos para proxima medicion...{Colors.END}")
        time.sleep(t_muestra)
        
except KeyboardInterrupt:
    print(f"\n\n{Colors.RED}Deteniendo mediciones...{Colors.END}")
    adc.stop_adc()
finally:
    adc.stop_adc()
