
###### Script de copia de seguridad de Archivos y tablas de BD en PVControl+ #############################################

# Uso interactivo : 

#     python fv_copia_seguridad.py

# Uso sin preguntar:

#     python fv_copia_seguridad.py -b
#         Ejecuta copia de seguridad y borra archivos de seguridad de mas de 30 dias de antiguedad

#     python fv_copia_seguridad.py -b -d10
#         Ejecuta copia de seguridad y borra archivos de seguridad de mas de 10 dias de antiguedad


# Los archivos y tablas sobre las que se realizara el backup se configuran en el diccionario "copia_seg":

#  Configuración para Archivos: 
#     activo... 1 para realizar backup ( poner a 0 para no realizar backup)
#     carpeta.. ruta en la que se ubica el archivo

#  Configuración para Tablas:
#     activo... 1 para realizar backup ( poner a 0 para no realizar backup)
#     tipo..... 
#             añadir: en la restauracion permite añadir los registros sin borrar los registros que ya tenga dicha tabla
#             sustituir: en la restauracion borrara la tabla que exista y añadira los registros del backup
#             preguntar: en modo interactivo permite elegir si se hace o no backup, y el tipo de backup

############################################################################################################################

copia_seg = {
    'archivos': {
        'Parametros_FV.py': {'activo': 1, 'carpeta': ''},             # Configuracion captura equipos PVControl+
        'Parametros_Web.js': {'activo': 1, 'carpeta': 'html'},        # Configuracion paginas web (relojes, historicas,..)
        'version.inc': {'activo': 1, 'carpeta': 'html'},
        'configuracion_activa.txt': {'activo': 1, 'carpeta': 'html'}, # Archivo para generar el Dibujo FV
        
    },
    'tablas': {
        'diario': {'activo': 1, 'tipo': 'añadir'},             # Resumen del dia
        'datos_c': {'activo': 1, 'tipo': 'preguntar'},         # Resumen cada 5 minutos

        'datos': {'activo': 0, 'tipo': 'añadir'},              # Datos historicos tipicamene cada 5 sg (¡¡¡CUIDADO CON TAMAÑO!!!)
        'datos_s': {'activo': 0, 'tipo': 'añadir'},            # Ultimos datos historicos a maxima resolucion 

        'reles': {'activo': 1, 'tipo': 'sustituir'},           # Reles dados de alta
        'reles_c': {'activo': 1, 'tipo': 'sustituir'},         # Condiciones FV de los Reles
        'reles_h': {'activo': 1, 'tipo': 'sustituir'},         # Condiciones Horarias de los Reles
        
        'reles_grab': {'activo': 0, 'tipo': 'añadir'},         # Historico de conmutaciones de los reles
        'reles_segundos_on': {'activo': 0, 'tipo': 'añadir'},  # Tiempo de encendido de reles al dia
        
        
        'condiciones': {'activo': 1, 'tipo': 'sustituir'},     # Condiciones Avanzadas
        
        'parametros': {'activo': 1, 'tipo': 'sustituir'}       # parametros configuracion (PID, Tmuestra,...)
    }
}

 
import os
import sys
import MySQLdb
import zipfile
import datetime
from shutil import copy2
from colorama import init, Fore, Back, Style

import argparse  

# Configurar el parser de argumentos
parser = argparse.ArgumentParser(description='Sistema de Backup/Restore PVControl+')
parser.add_argument('-b', '--backup', action='store_true', 
                    help='Ejecuta backup automático sin interacción')
parser.add_argument('-d', '--dias', type=int, default=30,
                    help='Número de días de backups a conservar (por defecto: 30)')
args = parser.parse_args()

# Inicializar colorama
init(autoreset=True)
bright = Style.BRIGHT

# Configuración de la aplicación
APLICACION_DIR = '/home/pi/PVControl+'
BACKUP_DIR = os.path.join(APLICACION_DIR, 'backBD')
TEMP_DIR = '/tmp/backup_temp'


# Configuración de la base de datos MariaDB
servidor = "localhost"
usuario = "rpi"
clave = "fv"
basedatos = "control_solar"

def mostrar_configuracion():
    """Muestra la configuración actual con colores brillantes"""
    print(bright + Fore.CYAN + "\nCONFIGURACIÓN ACTUAL")
    print(bright + Fore.YELLOW + "\nARCHIVOS:")
    for archivo, config in copia_seg['archivos'].items():
        estado = bright + (Fore.GREEN + "ACTIVO" if config['activo'] else Fore.RED + "INACTIVO")
        print(f"  {bright}{archivo.ljust(20)} {estado.ljust(15)} Carpeta: '{config['carpeta']}'")
    
    print(bright + Fore.YELLOW + "\nTABLAS:")
    for tabla, config in copia_seg['tablas'].items():
        estado = bright + (Fore.GREEN + "ACTIVO" if config['activo'] else Fore.RED + "INACTIVO")

        if config['tipo'] == 'añadir':
            tipo = bright + Fore.BLUE + "AÑADIR"
        elif config['tipo'] == 'sustituir':
            tipo = bright + Fore.MAGENTA + "SUSTITUIR"
        else:
            tipo = bright + Fore.CYAN + "PREGUNTAR"
        print(f"  {bright}{tabla.ljust(20)} {estado.ljust(15)} Tipo: {tipo}")

    
    print(bright + Fore.CYAN + "\nRUTAS:" )
    print(f"  {bright}Aplicación: {APLICACION_DIR}")
    print(f"  {bright}Backup: {BACKUP_DIR}")

def conectar_mariadb():
    try:
        conn = MySQLdb.connect(
            host=servidor,
            user=usuario,
            passwd=clave,
            db=basedatos
        )
        return conn
    except MySQLdb.Error as e:
        print(bright + Fore.RED + f"\nError al conectar a MariaDB: {e}" )
        return None

def mostrar_menu():
    print(bright + Fore.CYAN + "\n" + "="*50)
    print(bright + Fore.YELLOW + "     Sistema de Backup/Restore PVControl+")
    print(bright + Fore.CYAN + "="*50 )
    print(bright + Fore.GREEN + "1. Realizar backup")
    print(bright + Fore.BLUE + "2. Realizar restore")
    print(bright + Fore.RED + "3. Salir")
    print(bright + Fore.CYAN + "="*50 )
    return input("Seleccione una opción (1-3): ")

def crear_directorio_si_no_existe(directorio):
    if not os.path.exists(directorio):
        os.makedirs(directorio)
        print(bright + Fore.YELLOW + f"Directorio {directorio} creado." )

def obtener_dispositivos_usb():
    dispositivos = []
    for root, dirs, files in os.walk('/media'):
        for d in dirs:
            dispositivos.append(os.path.join(root, d))
    return dispositivos

def seleccionar_destino_backup():
    print(bright + Fore.CYAN + "\nSeleccione destino del backup:")
    print(bright + Fore.GREEN + f"1. Carpeta local ({BACKUP_DIR})")
    
    usb_devices = obtener_dispositivos_usb()
    if usb_devices:
        print(bright + Fore.YELLOW + "Dispositivos USB disponibles:")
        for i, device in enumerate(usb_devices, start=2):
            print(f"{bright + Fore.BLUE}{i}. {device}")
    
    opcion = input(f"\n{bright + Fore.CYAN}Seleccione opción (1-{len(usb_devices)+1}): ")
    
    try:
        opcion = int(opcion)
        if opcion == 1:
            return BACKUP_DIR
        elif 2 <= opcion <= len(usb_devices)+1:
            return usb_devices[opcion-2]
        else:
            print(bright + Fore.RED + "Opción no válida. Usando carpeta local por defecto.")
            return BACKUP_DIR
    except ValueError:
        print(bright + Fore.RED + "Entrada no válida. Usando carpeta local por defecto.")
        return BACKUP_DIR

def generar_nombre_backup(automatico=False):
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"aut_backup_{fecha}.zip" if automatico else f"backup_{fecha}.zip"

def preguntar_tipo_procesamiento(tabla):
    """Pregunta al usuario cómo procesar una tabla"""
    print(f"\n{bright + Fore.YELLOW}Tabla configurada como 'preguntar': {tabla}")
    print(f"{bright}1. Omitir esta tabla")
    print(f"2. Procesar como 'añadir' (insertar/actualizar registros)")
    print(f"3. Procesar como 'sustituir' (recrear tabla completa)")
    
    while True:
        opcion = input(f"{bright + Fore.CYAN}Seleccione opción (1-3): ")
        if opcion == '1':
            return None  # Omitir
        elif opcion == '2':
            return 'añadir'
        elif opcion == '3':
            return 'sustituir'
        else:
            print(f"{bright + Fore.RED}Opción no válida. Intente nuevamente.")

def hacer_backup_tablas(conn, tablas_config, temp_dir):
    print(bright + Fore.CYAN + "\nRealizando backup de tablas de la base de datos...")
    cursor = conn.cursor()
    
    for tabla, config in tablas_config.items():
        if not config['activo']:
            print(f"  {bright + Fore.YELLOW}- Tabla {tabla} omitida (activo=False)")
            continue
        
        # Manejo del tipo 'preguntar'
        tipo_procesamiento = config['tipo']
        if tipo_procesamiento == 'preguntar':
            tipo_procesamiento = preguntar_tipo_procesamiento(tabla)
            if not tipo_procesamiento:
                print(f"  {bright + Fore.YELLOW}- Tabla {tabla} omitida por usuario")
                continue
            
        try:
            # Obtener estructura de la tabla
            cursor.execute(f"SHOW CREATE TABLE {tabla}")
            estructura = cursor.fetchone()[1]
            
            # Obtener datos de la tabla
            cursor.execute(f"SELECT * FROM {tabla}")
            datos = cursor.fetchall()
            
            # Obtener nombres de columnas
            cursor.execute(f"DESCRIBE {tabla}")
            columnas = [col[0] for col in cursor.fetchall()]
            
            # Crear archivo SQL
            backup_file = os.path.join(temp_dir, f"{tabla}.sql")
            total_registros = len(datos)
            
            print(f"  {bright}Procesando tabla {tabla} como {tipo_procesamiento}... (0/{total_registros} registros)", end='', flush=True)
            
            with open(backup_file, 'w') as f:
                f.write(f"-- Configuración: {config}\n")
                f.write(f"DROP TABLE IF EXISTS {tabla};\n\n" if tipo_procesamiento == 'sustituir' else "")
                f.write(f"{estructura};\n\n")
                
                if datos:
                    for i, fila in enumerate(datos, 1):
                        valores = ", ".join([f"'{str(v)}'" if v is not None else "NULL" for v in fila])
                        if tipo_procesamiento == 'añadir':
                            sets = ", ".join([f"{col}=VALUES({col})" for col in columnas])
                            f.write(f"INSERT INTO {tabla} VALUES ({valores}) ON DUPLICATE KEY UPDATE {sets};\n")
                        else:
                            f.write(f"REPLACE INTO {tabla} VALUES ({valores});\n")
                        
                        if i % 100 == 0 or i == total_registros:
                            print(f"\r  {bright}Procesando tabla {tabla}... ({i}/{total_registros} registros)", end='', flush=True)
            
            print(f"\r  {bright + Fore.GREEN}- Tabla {tabla} backup completado ({total_registros} registros) - Tipo: {tipo_procesamiento}")
        except MySQLdb.Error as e:
            print(f"\r  {bright + Fore.RED}¡Error al hacer backup de la tabla {tabla}! {e}")

def hacer_backup_archivos(archivos_config, temp_dir):
    print(Fore.CYAN + "\nRealizando backup de archivos...")
    for archivo, config in archivos_config.items():
        if not config['activo']:
            print(f"  - {bright + Fore.YELLOW}Archivo {archivo} omitido (activo=False)")
            continue
            
        try:
            # Construir ruta completa del archivo (relativa a APLICACION_DIR)
            ruta_relativa = os.path.join(config['carpeta'], archivo) if config['carpeta'] else archivo
            ruta_completa = os.path.join(APLICACION_DIR, ruta_relativa)
            
            if os.path.exists(ruta_completa):
                dest_path = os.path.join(temp_dir, 'archivos', ruta_relativa)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                copy2(ruta_completa, dest_path)
                print(f"  - {bright + Fore.GREEN}Archivo {ruta_relativa} copiado correctamente")
                
                # Manejo especial para configuracion_activa.txt
                if archivo == 'configuracion_activa.txt' and config['carpeta'] == 'html':
                    try:
                        # Leer el archivo de configuración activa
                        with open(ruta_completa, 'r') as f:
                            config_activa = f.read().strip()
                        
                        if config_activa:
                            # Construir ruta del archivo de configuración referenciado
                            ruta_config = os.path.join(APLICACION_DIR, 'html', 'configuraciones', config_activa)
                            if os.path.exists(ruta_config):
                                dest_config = os.path.join(temp_dir, 'archivos', 'html', 'configuraciones', config_activa)
                                os.makedirs(os.path.dirname(dest_config), exist_ok=True)
                                copy2(ruta_config, dest_config)
                                print(f"  {bright + Fore.GREEN}- Archivo de configuración {config_activa} copiado correctamente{Style.RESET_ALL}")
                            else:
                                print(f"  {bright + Fore.YELLOW}¡Advertencia! Archivo de configuración {config_activa} no encontrado{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"  {bright + Fore.YELLOW}¡Advertencia! No se pudo copiar el archivo de configuración referenciado: {str(e)}{Style.RESET_ALL}")
                
            else:
                print(f"  {bright + Fore.YELLOW}¡Advertencia! Archivo {ruta_relativa} no encontrado en {APLICACION_DIR}")
        except Exception as e:
            print(f"  {bright + Fore.RED}¡Error al copiar archivo {archivo}! {str(e)}")

def crear_backup():
    inicio = datetime.datetime.now()
    destino = seleccionar_destino_backup()
    nombre_archivo = input(f"\n{bright + Fore.CYAN}Nombre del archivo de backup (dejar en blanco para {generar_nombre_backup()}): ")
    
    if not nombre_archivo:
        nombre_archivo = generar_nombre_backup()
    
    if not nombre_archivo.endswith('.zip'):
        nombre_archivo += '.zip'
    
    ruta_completa = os.path.join(destino, nombre_archivo)
    
    # Crear directorio temporal
    crear_directorio_si_no_existe(TEMP_DIR)
    
    # Conectar a MariaDB
    conn = conectar_mariadb()
    if not conn:
        return
    
    try:
        # Backup de tablas
        hacer_backup_tablas(conn, copia_seg['tablas'], TEMP_DIR)
        
        # Backup de archivos
        hacer_backup_archivos(copia_seg['archivos'], TEMP_DIR)
        
        # Crear archivo ZIP
        print(bright + Fore.CYAN + "\nCreando archivo ZIP...")
        with zipfile.ZipFile(ruta_completa, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(TEMP_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, TEMP_DIR)
                    zipf.write(file_path, arcname)
        
        tiempo_total = datetime.datetime.now() - inicio
        minutos, segundos = divmod(tiempo_total.total_seconds(), 60)
        print(f"\n{bright + Fore.GREEN}Backup completado correctamente en: {int(minutos)} minutos y {int(segundos)} segundos")
        print(f"{bright + Fore.GREEN}Archivo creado en: {ruta_completa}")
        
    except Exception as e:
        print(f"\n{bright + Fore.RED}¡Error durante el backup! {str(e)}")
    finally:
        # Limpiar y cerrar conexión
        if conn:
            conn.close()
        # Eliminar directorio temporal
        for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(TEMP_DIR)

def listar_archivos_backup():
    archivos = []
    print(bright + Fore.CYAN + "\nBuscando archivos de backup...")
    
    # Buscar en la carpeta local
    if os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            if f.endswith('.zip'):
                archivos.append(os.path.join(BACKUP_DIR, f))
    
    # Buscar en dispositivos USB
    for usb in obtener_dispositivos_usb():
        for root, dirs, files in os.walk(usb):
            for f in files:
                if f.endswith('.zip'):
                    archivos.append(os.path.join(root, f))
    
    if not archivos:
        print(bright + Fore.YELLOW + "No se encontraron archivos de backup.")
        return None
    
    print(bright + Fore.CYAN + "\nArchivos de backup disponibles:")
    for i, archivo in enumerate(archivos, start=1):
        print(f"{bright + Fore.BLUE}{i}. {archivo}")
    
    seleccion = input(f"\n{bright + Fore.CYAN}Seleccione el archivo a restaurar (1-{len(archivos)}): ")
    try:
        seleccion = int(seleccion) - 1
        if 0 <= seleccion < len(archivos):
            return archivos[seleccion]
        else:
            print(bright + Fore.RED + "Selección fuera de rango.")
            return None
    except ValueError:
        print(bright + Fore.RED + "Entrada no válida.")
        return None

def restaurar_tablas(conn, temp_dir):
    print(bright + Fore.CYAN + "\nRestaurando tablas de la base de datos..." )
    cursor = conn.cursor()
    
    # Obtener lista de tablas en el backup
    tablas_backup = set()
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.endswith('.sql'):
                tablas_backup.add(f[:-4])
    
    # Verificar tablas a restaurar
    tablas_a_restaurar = [t for t, cfg in copia_seg['tablas'].items() 
                         if t in tablas_backup and cfg['activo']]
    
    if not tablas_a_restaurar:
        print(bright + Fore.YELLOW + "No se encontraron tablas para restaurar en el backup." )
        return
    
    print(bright + Fore.CYAN + "Tablas a restaurar:", ", ".join(tablas_a_restaurar))
    
    for tabla in tablas_a_restaurar:
        config = copia_seg['tablas'][tabla]
        tipo_procesamiento = config['tipo']
        
        # Manejo del tipo 'preguntar'
        if tipo_procesamiento == 'preguntar':
            tipo_procesamiento = preguntar_tipo_procesamiento(tabla)
            if not tipo_procesamiento:
                print(f"  {bright + Fore.YELLOW}- Tabla {tabla} omitida por usuario")
                continue
        
        try:
            sql_file = os.path.join(temp_dir, f"{tabla}.sql")
            contador = {'insertados': 0, 'actualizados': 0, 'eliminados': 0}
            
            # Función para mostrar progreso
            def mostrar_progreso():
                if tipo_procesamiento == 'añadir':
                    print(f"\r  {bright}Procesando {tabla}: {Fore.GREEN}↑{contador['insertados']} | "
                          f"{Fore.YELLOW}↻{contador['actualizados']}", end='', flush=True)
                else:
                    print(f"\r  {bright}Procesando {tabla}: {Fore.RED}×{contador['eliminados']} | "
                          f"{Fore.GREEN}↑{contador['insertados']}", end='', flush=True)
            
            # Leer el archivo SQL
            with open(sql_file, 'r') as f:
                sql_content = f.read()
                
            print(f"  {bright}Procesando tabla {tabla} ({tipo_procesamiento})...")
            
            # Ejecutar cada comando SQL
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if not statement:
                    continue
                    
                try:
                    # Contar DROP TABLE para sustituir
                    if tipo_procesamiento == 'sustituir' and 'DROP TABLE' in statement:
                        cursor.execute(statement)
                        contador['eliminados'] = 1
                        mostrar_progreso()
                        continue
                        
                    # Ejecutar la sentencia
                    cursor.execute(statement)
                    
                    # Contar operaciones según el tipo
                    if tipo_procesamiento == 'añadir':
                        if "ON DUPLICATE KEY UPDATE" in statement:
                            if cursor.rowcount == 1:
                                contador['insertados'] += 1
                            else:
                                contador['actualizados'] += 1
                    else:  # sustituir
                        if "REPLACE INTO" in statement or "INSERT INTO" in statement:
                            contador['insertados'] += cursor.rowcount
                    
                    mostrar_progreso()
                        
                except MySQLdb.Error as e:
                    if e.args[0] == 1050 and 'CREATE TABLE' in statement:
                        continue
                    raise e
            
            # Resumen final
            if tipo_procesamiento == 'añadir':
                print(f"\r  {bright}{tabla}: {Fore.GREEN}{contador['insertados']} nuevos | "
                      f"{bright + Fore.YELLOW}{contador['actualizados']} actualizados          ")
            else:
                print(f"\r  {bright}{tabla}: {Fore.RED}Tabla recreada | "
                      f"{bright + Fore.GREEN}{contador['insertados']} registros insertados          ")
            
            conn.commit()
            print(f"  {bright + Fore.GREEN}✓ Tabla {tabla} completada")
            print('-' * 50)
            
        except Exception as e:
            conn.rollback()
            print(f"\n  {bright + Fore.RED}✗ Error en {tabla}: {str(e)}")

def restaurar_archivos(temp_dir):
    print(bright + Fore.CYAN + "\nRestaurando archivos..." )
    archivos_dir = os.path.join(temp_dir, 'archivos')
    
    if not os.path.exists(archivos_dir):
        print(bright + Fore.YELLOW + "No se encontraron archivos para restaurar en el backup." )
        return
    
    for archivo, config in copia_seg['archivos'].items():
        if not config['activo']:
            continue
            
        try:
            # Ruta en el backup
            ruta_relativa = os.path.join(config['carpeta'], archivo) if config['carpeta'] else archivo
            backup_path = os.path.join(archivos_dir, ruta_relativa)
            
            if os.path.exists(backup_path):
                # Ruta de destino (relativa a APLICACION_DIR)
                dest_path = os.path.join(APLICACION_DIR, ruta_relativa)
                
                # Crear directorios si no existen
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copiar archivo
                copy2(backup_path, dest_path)
                print(f"  - {bright + Fore.GREEN}Archivo {ruta_relativa} restaurado correctamente")

                # Manejo especial para configuracion_activa.txt
                if archivo == 'configuracion_activa.txt' and config['carpeta'] == 'html':
                    try:
                        # Leer el archivo de configuración activa recién restaurado
                        with open(dest_path, 'r') as f:
                            config_activa = f.read().strip()
                        
                        if config_activa:
                            # Construir ruta del archivo de configuración en el backup
                            backup_config = os.path.join(archivos_dir, 'html', 'configuraciones', config_activa)
                            if os.path.exists(backup_config):
                                dest_config = os.path.join(APLICACION_DIR, 'html', 'configuraciones', config_activa)
                                os.makedirs(os.path.dirname(dest_config), exist_ok=True)
                                copy2(backup_config, dest_config)
                                print(f"  {bright + Fore.GREEN}- Archivo de configuración {config_activa} restaurado correctamente{Style.RESET_ALL}")
                            else:
                                print(f"  {bright + Fore.YELLOW}¡Advertencia! Archivo de configuración {config_activa} no encontrado en el backup{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"  {bright + Fore.YELLOW}¡Advertencia! No se pudo restaurar el archivo de configuración referenciado: {str(e)}{Style.RESET_ALL}")
            
            
            
            
            else:
                print(f"  {bright + Fore.YELLOW}¡Advertencia! Archivo {archivo} no encontrado en el backup")
                
        except Exception as e:
            print(f"  {bright + Fore.RED}¡Error al restaurar archivo {archivo}! {str(e)}")

def hacer_restore():
    inicio = datetime.datetime.now()
    archivo_backup = listar_archivos_backup()
    if not archivo_backup:
        return
    
    print(f"\n{bright + Fore.CYAN}Se restaurará desde: {archivo_backup}")
    confirmacion = input(f"{bright + Fore.YELLOW}¿Continuar? (s/n): ").lower()
    if confirmacion != 's':
        print(bright + Fore.YELLOW + "Restauración cancelada.")
        return
    
    # Crear directorio temporal
    crear_directorio_si_no_existe(TEMP_DIR)
    
    # Conectar a MariaDB
    conn = conectar_mariadb()
    if not conn:
        return
    
    try:
        # Extraer archivo ZIP
        print(bright + Fore.CYAN + "\nExtrayendo archivo de backup...")
        with zipfile.ZipFile(archivo_backup, 'r') as zipf:
            zipf.extractall(TEMP_DIR)
        
        # Restaurar tablas
        restaurar_tablas(conn, TEMP_DIR)
        
        # Restaurar archivos
        restaurar_archivos(TEMP_DIR)
        
        tiempo_total = datetime.datetime.now() - inicio
        minutos, segundos = divmod(tiempo_total.total_seconds(), 60)
        print(f"\n{bright + Fore.GREEN}Restauración completada correctamente en {int(minutos)} minutos y {int(segundos)} segundos")
        
    except Exception as e:
        print(f"\n{Fore.RED}¡Error durante la restauración! {str(e)}")
    finally:
        # Limpiar y cerrar conexión
        if conn:
            conn.close()
        # Eliminar directorio temporal
        for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(TEMP_DIR)

def crear_backup_automatico():
    """Realiza un backup automático sin interacción del usuario"""
    # Configurar rutas y nombre de archivo
    destino_backup = BACKUP_DIR  # Carpeta de destino para el backup
    nombre_archivo_backup = generar_nombre_backup(automatico=True)
    ruta_archivo_backup = os.path.join(destino_backup, nombre_archivo_backup)
    
    # Crear directorios necesarios
    crear_directorio_si_no_existe(TEMP_DIR)
    crear_directorio_si_no_existe(destino_backup)
    
    # Conectar a MariaDB
    conn = conectar_mariadb()
    if not conn:
        return
    
    try:
        # Backup de tablas (omitiendo 'preguntar' y solo activas)
        print(bright + Fore.CYAN + "\nRealizando backup de tablas...")
        cursor = conn.cursor()
        
        for tabla, config in copia_seg['tablas'].items():
            # Omitir tablas inactivas o tipo 'preguntar' en modo automático
            if not config['activo'] or config['tipo'] == 'preguntar':
                print(f"  {bright + Fore.YELLOW}- Tabla {tabla} omitida (modo automático)")
                continue
                
            tipo_procesamiento = config['tipo']
            
            try:
                # Obtener estructura de la tabla
                cursor.execute(f"SHOW CREATE TABLE {tabla}")
                estructura = cursor.fetchone()[1]
                
                # Obtener datos de la tabla
                cursor.execute(f"SELECT * FROM {tabla}")
                datos = cursor.fetchall()
                
                # Obtener nombres de columnas
                cursor.execute(f"DESCRIBE {tabla}")
                columnas = [col[0] for col in cursor.fetchall()]
                
                # Crear archivo SQL temporal
                ruta_archivo_tabla = os.path.join(TEMP_DIR, f"{tabla}.sql")
                total_registros = len(datos)
                
                print(f"  {bright}Procesando tabla {tabla}... (0/{total_registros} registros)", end='', flush=True)
                
                with open(ruta_archivo_tabla, 'w') as f:
                    f.write(f"-- Configuración: {config}\n")
                    f.write(f"DROP TABLE IF EXISTS {tabla};\n\n" if tipo_procesamiento == 'sustituir' else "")
                    f.write(f"{estructura};\n\n")
                    
                    if datos:
                        for i, fila in enumerate(datos, 1):
                            valores = ", ".join([f"'{str(v)}'" if v is not None else "NULL" for v in fila])
                            if tipo_procesamiento == 'añadir':
                                sets = ", ".join([f"{col}=VALUES({col})" for col in columnas])
                                f.write(f"INSERT INTO {tabla} VALUES ({valores}) ON DUPLICATE KEY UPDATE {sets};\n")
                            else:
                                f.write(f"REPLACE INTO {tabla} VALUES ({valores});\n")
                            
                            if i % 100 == 0 or i == total_registros:
                                print(f"\r  {bright}Procesando tabla {tabla}... ({i}/{total_registros} registros)", end='', flush=True)
                
                print(f"\r  {bright + Fore.GREEN}- Tabla {tabla} backup completado ({total_registros} registros)")
            except MySQLdb.Error as e:
                print(f"\r  {bright + Fore.RED}¡Error al hacer backup de la tabla {tabla}! {e}")

        # Backup de archivos (solo los activos)
        print(bright + Fore.CYAN + "\nRealizando backup de archivos...")
        for archivo, config in copia_seg['archivos'].items():
            if not config['activo']:
                print(f"  {bright + Fore.YELLOW}- Archivo {archivo} omitido (activo=False)")
                continue
                
            try:
                # Construir ruta completa del archivo origen
                ruta_relativa_archivo = os.path.join(config['carpeta'], archivo) if config['carpeta'] else archivo
                ruta_completa_origen = os.path.join(APLICACION_DIR, ruta_relativa_archivo)
                
                if os.path.exists(ruta_completa_origen):
                    ruta_destino_temporal = os.path.join(TEMP_DIR, 'archivos', ruta_relativa_archivo)
                    os.makedirs(os.path.dirname(ruta_destino_temporal), exist_ok=True)
                    copy2(ruta_completa_origen, ruta_destino_temporal)
                    print(f"  {bright + Fore.GREEN}- Archivo {ruta_relativa_archivo} copiado correctamente")
                    
                    # Manejo especial para configuracion_activa.txt
                    if archivo == 'configuracion_activa.txt' and config['carpeta'] == 'html':
                        try:
                            with open(ruta_completa_origen, 'r') as f:
                                config_activa = f.read().strip()
                            
                            if config_activa:
                                ruta_config_origen = os.path.join(APLICACION_DIR, 'html', 'configuraciones', config_activa)
                                if os.path.exists(ruta_config_origen):
                                    ruta_config_destino = os.path.join(TEMP_DIR, 'archivos', 'html', 'configuraciones', config_activa)
                                    os.makedirs(os.path.dirname(ruta_config_destino), exist_ok=True)
                                    copy2(ruta_config_origen, ruta_config_destino)
                                    print(f"  {bright + Fore.GREEN}- Archivo de configuración {config_activa} copiado correctamente")
                        except Exception as e:
                            print(f"  {bright + Fore.YELLOW}¡Advertencia! No se pudo copiar el archivo de configuración referenciado: {str(e)}")
                else:
                    print(f"  {bright + Fore.YELLOW}¡Advertencia! Archivo {ruta_relativa_archivo} no encontrado")
            except Exception as e:
                print(f"  {bright + Fore.RED}¡Error al copiar archivo {archivo}! {str(e)}")
        
        # Crear archivo ZIP final
        print(bright + Fore.CYAN + "\nCreando archivo ZIP...")
        with zipfile.ZipFile(ruta_archivo_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(TEMP_DIR):
                for file in files:
                    ruta_absoluta_archivo = os.path.join(root, file)
                    ruta_relativa_en_zip = os.path.relpath(ruta_absoluta_archivo, TEMP_DIR)
                    zipf.write(ruta_absoluta_archivo, ruta_relativa_en_zip)
        
        # Limpiar backups antiguos (mantener solo los 30 más recientes)
        limpiar_backups_antiguos()
        
        print(f"\n{bright + Fore.GREEN}Backup automático completado correctamente en: {ruta_archivo_backup}")
        
    except Exception as e:
        print(f"\n{bright + Fore.RED}¡Error durante el backup automático! {str(e)}")
    finally:
        # Limpiar y cerrar conexión
        if conn:
            conn.close()
        # Eliminar directorio temporal
        for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(TEMP_DIR)

def limpiar_backups_antiguos():
    """Mantiene solo los backups automáticos de los últimos N días"""
    try:
        # Obtener el umbral de fecha (hoy - días especificados)
        umbral_fecha = datetime.datetime.now() - datetime.timedelta(days=args.dias)
        
        # Obtener lista de backups automáticos
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.startswith('aut_backup_') and f.endswith('.zip'):
                try:
                    # Extraer la fecha del nombre del archivo
                    fecha_str = f[11:-4]  # Extrae YYYYMMDD_HHMMSS
                    fecha_backup = datetime.datetime.strptime(fecha_str, "%Y%m%d_%H%M%S")
                    backups.append((fecha_backup, os.path.join(BACKUP_DIR, f)))
                except ValueError:
                    continue  # Si el formato no coincide, ignorar el archivo
        
        # Eliminar backups más antiguos que el umbral
        eliminados = 0
        for fecha_backup, archivo in backups:
            if fecha_backup < umbral_fecha:
                try:
                    os.remove(archivo)
                    print(f"  {bright + Fore.YELLOW}- Eliminado backup antiguo: {os.path.basename(archivo)}")
                    eliminados += 1
                except Exception as e:
                    print(f"  {bright + Fore.RED}- Error al eliminar {os.path.basename(archivo)}: {str(e)}")
        
        # Mostrar resumen
        if eliminados > 0:
            print(f"  {bright + Fore.CYAN}- Se eliminaron {eliminados} backups antiguos (conservando últimos {args.dias} días)")
        else:
            print(f"  {bright + Fore.CYAN}- No se encontraron backups anteriores a {args.dias} días")
            
    except Exception as e:
        print(f"  {bright + Fore.RED}- Error al limpiar backups antiguos: {str(e)}")

def limpiar_backups_antiguos1():
    """Mantiene solo los 30 backups automáticos más recientes"""
    try:
        # Obtener lista de backups automáticos ordenados por fecha (más reciente primero)
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.startswith('aut_backup_') and f.endswith('.zip'):
                fecha_str = f[11:-4]  # Extraer parte de la fecha del nombre
                try:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y%m%d_%H%M%S")
                    backups.append((fecha, os.path.join(BACKUP_DIR, f)))
                except ValueError:
                    continue
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(reverse=True, key=lambda x: x[0])
        
        # Eliminar los backups que excedan el límite
        if len(backups) > 30:
            for fecha, archivo in backups[30:]:
                try:
                    os.remove(archivo)
                    print(f"  {bright + Fore.YELLOW}- Eliminado backup antiguo: {os.path.basename(archivo)}")
                except Exception as e:
                    print(f"  {bright + Fore.RED}- Error al eliminar {archivo}: {str(e)}")
                    
    except Exception as e:
        print(f"  {bright + Fore.RED}- Error al limpiar backups antiguos: {str(e)}")

def main():
    
    # Mostrar configuración al inicio
    mostrar_configuracion()

    # Modo automático
    if args.backup:
        print(bright + Fore.CYAN + "\nIniciando backup automático..." )
        crear_backup_automatico()
        return

    
    while True:
        opcion = mostrar_menu()
        
        if opcion == '1':
            crear_backup()
        elif opcion == '2':
            hacer_restore()
        elif opcion == '3':
            print(bright + Fore.GREEN + "Saliendo del programa...")
            break
        else:
            print(bright + Fore.RED + "Opción no válida. Intente nuevamente.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()