# -*- coding: utf-8 -*-

# Versión mejorada con interfaz interactiva y ordenación específica
import os, glob
import subprocess, sys
import colorama
from colorama import Fore, Back, Style
colorama.init()

usar_motioneye = 0
from Parametros_FV import *

carpeta = '/home/pi/PVControl+/etc/systemd/system/'
enlaces_dir = '/etc/systemd/system/'

# Configurar para terminales que no soportan emojis
USE_EMOJIS = False  # Cambiar a True si tu terminal soporta emojis

def clear_screen():
    """Limpia la pantalla de la terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Imprime el encabezado del menú"""
    clear_screen()
    print(Fore.YELLOW + Style.BRIGHT + '=' * 60)
    print(Fore.YELLOW + Style.BRIGHT + '        GESTOR DE SERVICIOS PVControl+')
    print(Fore.YELLOW + Style.BRIGHT + '=' * 60)
    print(Style.RESET_ALL)

def get_service_status(service_name):
    """Obtiene el estado de un servicio"""
    try:
        # Primero verificamos si el servicio está cargado en systemd
        res = subprocess.run(['sudo', 'systemctl', 'is-enabled', service_name], 
                           capture_output=True, text=True)
        
        # Si el servicio no está habilitado/deshabilitado, puede que no exista
        if res.returncode != 0 and "No such file or directory" in res.stderr:
            return 'NO CREADO', Fore.BLUE + Style.BRIGHT, 'not_created'
        
        # Verificar estado activo/inactivo
        res = subprocess.run(['sudo', 'systemctl', 'is-active', service_name], 
                           capture_output=True, text=True)
        status = res.stdout.strip()
        
        if USE_EMOJIS:
            if status == 'active':
                return '🟢 ACTIVO', Fore.GREEN + Style.BRIGHT, 'active'
            elif status == 'inactive':
                return '🔴 INACTIVO', Fore.RED + Style.BRIGHT, 'inactive'
            elif status == 'failed':
                return '🔴 FALLIDO', Fore.RED + Style.BRIGHT, 'failed'
            else:
                return f'❓ {status}', Fore.YELLOW + Style.BRIGHT, 'unknown'
        else:
            if status == 'active':
                return '[ACTIVO]', Fore.GREEN + Style.BRIGHT, 'active'
            elif status == 'inactive':
                return '[INACTIVO]', Fore.RED + Style.BRIGHT, 'inactive'
            elif status == 'failed':
                return '[FALLIDO]', Fore.RED + Style.BRIGHT, 'failed'
            else:
                return f'[{status}]', Fore.YELLOW + Style.BRIGHT, 'unknown'
                
    except Exception as e:
        return 'ERROR', Fore.RED + Style.BRIGHT, 'error'

def is_service_linked(service_name):
    """Verifica si el servicio tiene un enlace creado"""
    enlace_path = os.path.join(enlaces_dir, service_name)
    return os.path.islink(enlace_path) or os.path.exists(enlace_path)

def is_service_loaded_in_systemd(service_name):
    """Verifica si el servicio está cargado en systemd (existe como servicio)"""
    try:
        # Verificar si systemd reconoce el servicio
        res = subprocess.run(['sudo', 'systemctl', 'status', service_name, '--no-pager'],
                           capture_output=True, text=True)
        
        # Si el servicio existe pero está inactivo
        if "Loaded: loaded" in res.stdout or "Loaded: not-found" not in res.stdout:
            return True
            
        # Verificar con list-unit-files
        res = subprocess.run(['sudo', 'systemctl', 'list-unit-files', service_name],
                           capture_output=True, text=True)
        
        return service_name in res.stdout
    except:
        return False

def get_service_category(servicio):
    """Determina la categoría del servicio para ordenación"""
    if not servicio['linked'] and servicio['status_code'] == 'not_created':
        return 2  # No creados (último grupo)
    elif servicio['status_code'] == 'active':
        return 0  # Activos (primer grupo)
    else:
        return 1  # Creados pero no activos (segundo grupo)

def remove_service_extension(name):
    """Elimina la extensión .service del nombre si existe"""
    if name.endswith('.service'):
        return name[:-8]  # Eliminar los últimos 8 caracteres ".service"
    return name

def get_all_services():
    """Obtiene todos los servicios disponibles ordenados según criterio específico"""
    servicios = []
    
    # Buscar archivos .service
    for f in glob.glob(carpeta + '*.service'):
        service_file = os.path.basename(f)  # Nombre con extensión
        service_name = remove_service_extension(service_file)  # Nombre sin extensión
        linked = is_service_linked(service_file)
        
        if linked:
            # Si está enlazado, verificar el estado real (usamos el nombre con extensión para systemctl)
            status, color, status_code = get_service_status(service_file)
            
            # Si dice "NO CREADO" pero está enlazado, verificamos más profundamente
            if status_code == 'not_created' and linked:
                # Verificar si realmente está cargado en systemd
                if is_service_loaded_in_systemd(service_file):
                    # Si está cargado pero inactivo
                    if USE_EMOJIS:
                        status, color, status_code = '🔴 INACTIVO', Fore.RED + Style.BRIGHT, 'inactive'
                    else:
                        status, color, status_code = '[INACTIVO]', Fore.RED + Style.BRIGHT, 'inactive'
        else:
            status, color, status_code = 'NO CREADO', Fore.BLUE + Style.BRIGHT, 'not_created'
            
        servicios.append({
            'name': service_name,  # Nombre sin extensión para mostrar
            'file_name': service_file,  # Nombre con extensión para comandos
            'path': f,
            'linked': linked,
            'status': status,
            'color': color,
            'status_code': status_code,
            'full_path': f
        })
    
    # Ordenar según el criterio específico:
    # 1. Primero por categoría (activos → creados no activos → no creados)
    # 2. Luego alfabéticamente dentro de cada categoría (por nombre sin extensión)
    servicios.sort(key=lambda x: (get_service_category(x), x['name'].lower()))
    
    return servicios

def display_services(servicios):
    """Muestra la lista de servicios con su estado y categorías visuales"""
    print(Fore.CYAN + Style.BRIGHT + f"{'N°':<3} {'SERVICIO':<25} {'ESTADO':<15} {'ENLACE'}")
    print(Fore.CYAN + Style.BRIGHT + '-' * 60)
    
    # Variables para controlar las separaciones visuales
    last_category = -1
    category_titles = {
        0: Fore.GREEN + Style.BRIGHT + "SERVICIOS ACTIVOS",
        1: Fore.MAGENTA + Style.BRIGHT + "SERVICIOS CREADOS (INACTIVOS)",
        2: Fore.BLUE + Style.BRIGHT + "SERVICIOS NO CREADOS"
    }
    
    for i, servicio in enumerate(servicios, 1):
        current_category = get_service_category(servicio)
        
        # Mostrar separador de categoría si cambia
        if current_category != last_category:
            print(Fore.CYAN + Style.BRIGHT + '-' * 60)
            print(f"{' ':<3} {category_titles[current_category]:<25}")
            print(Fore.CYAN + Style.BRIGHT + '-' * 60)
            last_category = current_category
        
        enlace = '[SI]' if servicio['linked'] else '[NO]'
        enlace_color = Fore.GREEN + Style.BRIGHT if servicio['linked'] else Fore.RED + Style.BRIGHT
        
        print(f"{Fore.WHITE + Style.BRIGHT}{i:<3} {Fore.YELLOW + Style.BRIGHT}{servicio['name']:<25} "
              f"{servicio['color']}{servicio['status']:<15} {enlace_color}{enlace}")
    
    print(Fore.CYAN + Style.BRIGHT + '-' * 60)
    print(Style.RESET_ALL)

def create_service_link(service_path, service_file):
    """Crea el enlace simbólico para un servicio"""
    try:
        service_name = remove_service_extension(service_file)
        print(Fore.WHITE + Style.BRIGHT + f"Creando enlace para {service_name}...")
        
        # Crear enlace simbólico
        res = subprocess.run(['sudo', 'ln', '-sf', service_path, 
                            f'/etc/systemd/system/{service_file}'], 
                           capture_output=True, text=True)
        
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + f"  ✓ Enlace creado para {service_name}")
            else:
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Enlace creado para {service_name}")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.RED + Style.BRIGHT + f"  ✗ Error al crear enlace: {res.stderr}")
            else:
                print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al crear enlace: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Excepción al crear enlace: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Excepción al crear enlace: {str(e)}")
        return False

def enable_service(service_file):
    """Habilita un servicio"""
    service_name = remove_service_extension(service_file)
    try:
        res = subprocess.run(['sudo', 'systemctl', 'enable', service_file],
                           capture_output=True, text=True)
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + f"  ✓ Servicio {service_name} habilitado")
            else:
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Servicio {service_name} habilitado")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.YELLOW + Style.BRIGHT + f"  ⚠ Advertencia al habilitar: {res.stderr}")
            else:
                print(Fore.YELLOW + Style.BRIGHT + f"  [AVISO] Advertencia al habilitar: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Error al habilitar: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al habilitar: {str(e)}")
        return False

def start_service(service_file):
    """Inicia un servicio"""
    service_name = remove_service_extension(service_file)
    try:
        res = subprocess.run(['sudo', 'systemctl', 'start', service_file],
                           capture_output=True, text=True)
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + f"  ✓ Servicio {service_name} iniciado")
            else:
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Servicio {service_name} iniciado")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.RED + Style.BRIGHT + f"  ✗ Error al iniciar: {res.stderr}")
            else:
                print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al iniciar: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Error al iniciar: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al iniciar: {str(e)}")
        return False

def stop_service(service_file):
    """Detiene un servicio"""
    service_name = remove_service_extension(service_file)
    try:
        res = subprocess.run(['sudo', 'systemctl', 'stop', service_file],
                           capture_output=True, text=True)
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.YELLOW + Style.BRIGHT + f"  ✓ Servicio {service_name} detenido")
            else:
                print(Fore.YELLOW + Style.BRIGHT + f"  [OK] Servicio {service_name} detenido")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.RED + Style.BRIGHT + f"  ✗ Error al detener: {res.stderr}")
            else:
                print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al detener: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Error al detener: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al detener: {str(e)}")
        return False

def restart_service(service_file):
    """Reinicia un servicio"""
    service_name = remove_service_extension(service_file)
    try:
        res = subprocess.run(['sudo', 'systemctl', 'restart', service_file],
                           capture_output=True, text=True)
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + f"  ✓ Servicio {service_name} reiniciado")
            else:
                print(Fore.GREEN + Style.BRIGHT + f"  [OK] Servicio {service_name} reiniciado")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.RED + Style.BRIGHT + f"  ✗ Error al reiniciar: {res.stderr}")
            else:
                print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al reiniciar: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Error al reiniciar: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al reiniciar: {str(e)}")
        return False

def disable_service(service_file):
    """Deshabilita un servicio"""
    service_name = remove_service_extension(service_file)
    try:
        res = subprocess.run(['sudo', 'systemctl', 'disable', service_file],
                           capture_output=True, text=True)
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.YELLOW + Style.BRIGHT + f"  ✓ Servicio {service_name} deshabilitado")
            else:
                print(Fore.YELLOW + Style.BRIGHT + f"  [OK] Servicio {service_name} deshabilitado")
            return True
        else:
            if USE_EMOJIS:
                print(Fore.YELLOW + Style.BRIGHT + f"  ⚠ Advertencia al deshabilitar: {res.stderr}")
            else:
                print(Fore.YELLOW + Style.BRIGHT + f"  [AVISO] Advertencia al deshabilitar: {res.stderr}")
            return False
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Error al deshabilitar: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error al deshabilitar: {str(e)}")
        return False

def show_service_details(service_file):
    """Muestra detalles de un servicio"""
    service_name = remove_service_extension(service_file)
    print(Fore.CYAN + Style.BRIGHT + f"\n{'='*60}")
    print(Fore.CYAN + Style.BRIGHT + f"Detalles del servicio: {service_name}")
    print(Fore.CYAN + Style.BRIGHT + f"{'='*60}")
    
    # Mostrar estado completo
    res = subprocess.run(['sudo', 'systemctl', 'status', service_file, '--no-pager'],
                       capture_output=True, text=True)
    print(Fore.WHITE + Style.BRIGHT + res.stdout)
    
    # Mostrar propiedades adicionales
    res = subprocess.run(['sudo', 'systemctl', 'show', service_file, '--no-pager'],
                       capture_output=True, text=True)
    print(Fore.CYAN + Style.BRIGHT + "\nPropiedades del servicio:")
    print(Fore.WHITE + Style.BRIGHT + "-" * 40)
    
    # Filtrar propiedades importantes
    important_props = ['Description', 'LoadState', 'ActiveState', 
                      'SubState', 'UnitFileState', 'FragmentPath']
    
    for line in res.stdout.split('\n'):
        for prop in important_props:
            if line.startswith(prop + '='):
                prop_name, prop_value = line.split('=', 1)
                print(f"{Fore.YELLOW + Style.BRIGHT}{prop_name:<20}: {Fore.WHITE + Style.BRIGHT}{prop_value}")
                break

def manage_single_service(servicio):
    """Menú para gestionar un servicio individual"""
    while True:
        print_header()
        print(Fore.CYAN + Style.BRIGHT + f"GESTIONANDO: {servicio['name']}")
        
        # Mostrar categoría del servicio
        category = get_service_category(servicio)
        category_names = {
            0: Fore.GREEN + Style.BRIGHT + "CATEGORÍA: ACTIVO",
            1: Fore.MAGENTA + Style.BRIGHT + "CATEGORÍA: CREADO (INACTIVO)",
            2: Fore.BLUE + Style.BRIGHT + "CATEGORÍA: NO CREADO"
        }
        print(category_names.get(category, Fore.WHITE + Style.BRIGHT + "CATEGORÍA: DESCONOCIDA"))
        
        print(Fore.CYAN + Style.BRIGHT + f"Estado actual: {servicio['color']}{servicio['status']}")
        print(Fore.CYAN + Style.BRIGHT + f"Enlace creado: {'[SI]' if servicio['linked'] else '[NO]'}")
        print()
        
        if servicio['linked']:
            print(Fore.WHITE + Style.BRIGHT + "1. Iniciar servicio")
            print(Fore.WHITE + Style.BRIGHT + "2. Detener servicio")
            print(Fore.WHITE + Style.BRIGHT + "3. Reiniciar servicio")
            print(Fore.WHITE + Style.BRIGHT + "4. Habilitar inicio automático")
            print(Fore.WHITE + Style.BRIGHT + "5. Deshabilitar inicio automático")
            print(Fore.WHITE + Style.BRIGHT + "6. Ver detalles del servicio")
            print(Fore.WHITE + Style.BRIGHT + "7. Eliminar enlace (sin eliminar archivo)")
        else:
            print(Fore.WHITE + Style.BRIGHT + "1. Crear enlace y habilitar")
            print(Fore.WHITE + Style.BRIGHT + "2. Crear enlace, habilitar e iniciar")
        
        print(Fore.WHITE + Style.BRIGHT + "0. Volver al menú principal")
        print()
        
        opcion = input(Fore.GREEN + Style.BRIGHT + "Seleccione una opción: " + Fore.WHITE + Style.BRIGHT).strip()
        
        if opcion == '0':
            break
        elif opcion == '1':
            if servicio['linked']:
                start_service(servicio['file_name'])
            else:
                if create_service_link(servicio['path'], servicio['file_name']):
                    enable_service(servicio['file_name'])
                    servicio['linked'] = True
        elif opcion == '2':
            if servicio['linked']:
                stop_service(servicio['file_name'])
            else:
                if create_service_link(servicio['path'], servicio['file_name']):
                    enable_service(servicio['file_name'])
                    start_service(servicio['file_name'])
                    servicio['linked'] = True
        elif opcion == '3' and servicio['linked']:
            restart_service(servicio['file_name'])
        elif opcion == '4' and servicio['linked']:
            enable_service(servicio['file_name'])
        elif opcion == '5' and servicio['linked']:
            disable_service(servicio['file_name'])
        elif opcion == '6' and servicio['linked']:
            show_service_details(servicio['file_name'])
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")
        elif opcion == '7' and servicio['linked']:
            confirm = input(Fore.RED + Style.BRIGHT + f"¿Eliminar enlace de {servicio['name']}? (s/n): ").lower()
            if confirm == 's':
                subprocess.run(['sudo', 'rm', f'/etc/systemd/system/{servicio["file_name"]}'])
                if USE_EMOJIS:
                    print(Fore.YELLOW + Style.BRIGHT + f"  ✓ Enlace eliminado")
                else:
                    print(Fore.YELLOW + Style.BRIGHT + f"  [OK] Enlace eliminado")
                servicio['linked'] = False
        
        # Actualizar estado completo (no solo el texto)
        if servicio['linked']:
            servicio['status'], servicio['color'], servicio['status_code'] = get_service_status(servicio['file_name'])
        else:
            servicio['status'], servicio['color'], servicio['status_code'] = 'NO CREADO', Fore.BLUE + Style.BRIGHT, 'not_created'
        
        if opcion not in ['6']:  # Opción 6 ya mostró mensaje de espera
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")

def manage_all_services(servicios, action):
    """Gestiona todos los servicios a la vez"""
    print_header()
    
    if action == 'create_start_all':
        print(Fore.CYAN + Style.BRIGHT + "CREANDO E INICIANDO TODOS LOS SERVICIOS")
        print(Fore.CYAN + Style.BRIGHT + "=" * 40)
        
        # Primero crear todos los enlaces para los no creados
        for servicio in servicios:
            if not servicio['linked']:
                print(Fore.WHITE + Style.BRIGHT + f"\nCreando {servicio['name']}...")
                if create_service_link(servicio['path'], servicio['file_name']):
                    enable_service(servicio['file_name'])
                    servicio['linked'] = True
        
        # Luego iniciar todos los servicios
        for servicio in servicios:
            if servicio['linked']:
                print(Fore.WHITE + Style.BRIGHT + f"\nIniciando {servicio['name']}...")
                start_service(servicio['file_name'])
    
    elif action == 'stop_all':
        print(Fore.CYAN + Style.BRIGHT + "DETENIENDO TODOS LOS SERVICIOS")
        print(Fore.CYAN + Style.BRIGHT + "=" * 40)
        
        for servicio in servicios:
            if servicio['linked']:
                print(Fore.WHITE + Style.BRIGHT + f"\nDeteniendo {servicio['name']}...")
                stop_service(servicio['file_name'])
    
    elif action == 'restart_all':
        print(Fore.CYAN + Style.BRIGHT + "REINICIANDO TODOS LOS SERVICIOS")
        print(Fore.CYAN + Style.BRIGHT + "=" * 40)
        
        for servicio in servicios:
            if servicio['linked']:
                print(Fore.WHITE + Style.BRIGHT + f"\nReiniciando {servicio['name']}...")
                restart_service(servicio['file_name'])

def create_start_non_existent(servicios):
    """Crea e inicia solo los servicios no creados"""
    print_header()
    print(Fore.CYAN + Style.BRIGHT + "CREANDO E INICIANDO SERVICIOS NO CREADOS")
    print(Fore.CYAN + Style.BRIGHT + "=" * 40)
    
    servicios_creados = 0
    
    for servicio in servicios:
        if not servicio['linked']:
            print(Fore.WHITE + Style.BRIGHT + f"\nCreando e iniciando {servicio['name']}...")
            if create_service_link(servicio['path'], servicio['file_name']):
                enable_service(servicio['file_name'])
                start_service(servicio['file_name'])
                servicio['linked'] = True
                servicios_creados += 1
            else:
                print(Fore.RED + Style.BRIGHT + f"  No se pudo crear {servicio['name']}")
        else:
            print(Fore.WHITE + Style.DIM + f"\n{servicio['name']} ya está creado, omitiendo...")
    
    if servicios_creados == 0:
        print(Fore.YELLOW + Style.BRIGHT + "\nNo hay servicios nuevos para crear.")
    else:
        if USE_EMOJIS:
            print(Fore.GREEN + Style.BRIGHT + f"\n✓ Se crearon e iniciaron {servicios_creados} servicios nuevos")
        else:
            print(Fore.GREEN + Style.BRIGHT + f"\n[OK] Se crearon e iniciaron {servicios_creados} servicios nuevos")

def activate_web():
    """Activa la página web de PVControl+"""
    print_header()
    print(Fore.YELLOW + Style.BRIGHT + "ACTIVANDO WEB PVControl+")
    print(Fore.YELLOW + Style.BRIGHT + "=" * 40)
    
    try:
        # Eliminar directorio actual si existe
        res = subprocess.run(['sudo', 'rm', '-R', '/var/www/html'], 
                           capture_output=True, text=True)
        
        # Crear enlace simbólico
        res = subprocess.run(['sudo', 'ln', '-sf', '/home/pi/PVControl+/html', '/var/www/html'],
                           capture_output=True, text=True)
        
        if res.returncode == 0:
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + "  ✓ Web PVControl+ activada correctamente")
            else:
                print(Fore.GREEN + Style.BRIGHT + "  [OK] Web PVControl+ activada correctamente")
            print(Fore.GREEN + Style.BRIGHT + "  Enlace creado: /var/www/html → /home/pi/PVControl+/html")
        else:
            if USE_EMOJIS:
                print(Fore.RED + Style.BRIGHT + f"  ✗ Error: {res.stderr}")
            else:
                print(Fore.RED + Style.BRIGHT + f"  [ERROR] Error: {res.stderr}")
    
    except Exception as e:
        if USE_EMOJIS:
            print(Fore.RED + Style.BRIGHT + f"  ✗ Excepción: {str(e)}")
        else:
            print(Fore.RED + Style.BRIGHT + f"  [ERROR] Excepción: {str(e)}")
    
    input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")

def refresh_services_list():
    """Refresca y reordena la lista de servicios"""
    if USE_EMOJIS:
        print(Fore.YELLOW + Style.BRIGHT + "🔄 Actualizando lista de servicios...")
    else:
        print(Fore.YELLOW + Style.BRIGHT + "[...] Actualizando lista de servicios...")
    return get_all_services()

def show_help():
    """Muestra la ayuda de parámetros"""
    print(Fore.YELLOW + Style.BRIGHT + "GESTOR DE SERVICIOS PVControl+ - Ayuda de parámetros")
    print(Fore.YELLOW + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + "Uso: python script.py [OPCIÓN]")
    print()
    print(Fore.WHITE + Style.BRIGHT + "Opciones:")
    print(Fore.GREEN + Style.BRIGHT + "  -t, --todos      Crear e iniciar TODOS los servicios")
    print(Fore.RED + Style.BRIGHT + "  -p, --parar      Detener TODOS los servicios")
    print(Fore.BLUE + Style.BRIGHT + "  -f, --faltantes  Crear e iniciar solo servicios NO CREADOS")
    print(Fore.MAGENTA + Style.BRIGHT + "  -h, --help       Mostrar esta ayuda")
    print(Fore.WHITE + Style.BRIGHT + "  (sin parámetros)  Modo interactivo")
    print()
    print(Fore.YELLOW + Style.BRIGHT + "Ejemplos:")
    print(Fore.WHITE + Style.BRIGHT + "  python script.py -t     # Crear e iniciar todos")
    print(Fore.WHITE + Style.BRIGHT + "  python script.py -p     # Detener todos")
    print(Fore.WHITE + Style.BRIGHT + "  python script.py -f     # Crear solo los faltantes")

def process_command_line_args():
    """Procesa los argumentos de línea de comandos"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['-h', '--help']:
            show_help()
            return True  # Indicar que se mostró ayuda
        
        servicios = get_all_services()
        
        if arg in ['-t', '--todos']:
            manage_all_services(servicios, 'create_start_all')
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para salir...")
            return True
        
        elif arg in ['-p', '--parar']:
            manage_all_services(servicios, 'stop_all')
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para salir...")
            return True
        
        elif arg in ['-f', '--faltantes']:
            create_start_non_existent(servicios)
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para salir...")
            return True
        
        else:
            print(Fore.RED + Style.BRIGHT + f"Parámetro desconocido: {arg}")
            print(Fore.YELLOW + Style.BRIGHT + "Use -h para ver la ayuda")
            return True
    
    return False  # No se procesaron argumentos, continuar con modo interactivo

def main():
    """Función principal"""
    global USE_EMOJIS
    
    # Verificar si se pasaron parámetros de línea de comandos
    if process_command_line_args():
        return  # Salir si se procesaron argumentos
    
    # Detectar si la terminal soporta emojis
    try:
        # Intentar escribir un emoji simple
        print("Probando compatibilidad con emojis...", end="")
        print("✓", end="\r")
        USE_EMOJIS = True
        print(" " * 40 + "\r", end="")  # Limpiar línea
    except:
        USE_EMOJIS = False
        print("Terminal no compatible con emojis, usando texto simple")
    
    servicios = get_all_services()
    
    while True:
        # Mostrar menú principal
        print_header()
        display_services(servicios)
        
        # Opciones del menú principal
        print(Fore.WHITE + Style.BRIGHT + "OPCIONES:")
        print(Fore.WHITE + Style.BRIGHT + "  [1-" + str(len(servicios)) + "] Seleccionar servicio individual")
        print(Fore.GREEN + Style.BRIGHT + "  C  Crear e iniciar todos los servicios")
        print(Fore.YELLOW + Style.BRIGHT + "  R  Reiniciar todos los servicios")
        print(Fore.RED + Style.BRIGHT + "  S  Detener todos los servicios")
        print(Fore.BLUE + Style.BRIGHT + "  F  Crear e iniciar solo servicios no creados")
        print(Fore.CYAN + Style.BRIGHT + "  W  Activar/Actualizar página web")
        print(Fore.MAGENTA + Style.BRIGHT + "  A  Actualizar lista de servicios")
        print(Fore.WHITE + Style.BRIGHT + "  H  Mostrar ayuda de parámetros")
        print(Fore.WHITE + Style.BRIGHT + "  Q  Salir")
        print()
        
        opcion = input(Fore.GREEN + Style.BRIGHT + "Seleccione una opción: " + Fore.WHITE + Style.BRIGHT).strip().upper()
        
        if opcion == 'Q':
            print(Fore.YELLOW + Style.BRIGHT + "\nSaliendo del gestor de servicios...")
            break
        
        elif opcion == 'H':
            show_help()
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")
        
        elif opcion == 'C':
            manage_all_services(servicios, 'create_start_all')
            servicios = refresh_services_list()  # Refrescar después de cambios
        
        elif opcion == 'R':
            manage_all_services(servicios, 'restart_all')
            servicios = refresh_services_list()  # Refrescar después de cambios
        
        elif opcion == 'S':
            manage_all_services(servicios, 'stop_all')
            servicios = refresh_services_list()  # Refrescar después de cambios
        
        elif opcion == 'F':
            create_start_non_existent(servicios)
            servicios = refresh_services_list()  # Refrescar después de cambios
        
        elif opcion == 'W':
            activate_web()
        
        elif opcion == 'A':
            servicios = refresh_services_list()
            if USE_EMOJIS:
                print(Fore.GREEN + Style.BRIGHT + "  ✓ Lista de servicios actualizada")
            else:
                print(Fore.GREEN + Style.BRIGHT + "  [OK] Lista de servicios actualizada")
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")
        
        elif opcion.isdigit():
            idx = int(opcion) - 1
            if 0 <= idx < len(servicios):
                # Guardar índice para mantener posición si es posible
                old_name = servicios[idx]['name']
                manage_single_service(servicios[idx])
                
                # Refrescar lista y tratar de mantener la selección
                servicios = refresh_services_list()
                
                # Buscar el mismo servicio en la nueva lista
                for new_idx, servicio in enumerate(servicios):
                    if servicio['name'] == old_name:
                        # El servicio mantendrá su nueva posición automáticamente
                        # debido al reordenamiento por categorías
                        break
            else:
                print(Fore.RED + Style.BRIGHT + "Número de servicio no válido")
                input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")
        
        else:
            print(Fore.RED + Style.BRIGHT + "Opción no válida")
            input(Fore.CYAN + Style.BRIGHT + "\nPresione Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + Style.BRIGHT + "\n\nPrograma interrumpido por el usuario")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"\nError inesperado: {str(e)}")
    finally:
        print(Fore.RESET + Style.RESET_ALL)