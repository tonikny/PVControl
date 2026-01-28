# backup_variables.py
"""
Gestor de backup dinámico para variables del sistema FV.
Con actualización en caliente de configuración.
"""
import json
import time
import threading
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import sys

# ============================================
# FUNCIÓN PRINTT() - PRINT SOLO EN TERMINAL
# ============================================
def printT(*args, **kwargs):
    """
    Print que solo funciona si estamos en terminal.
    No muestra nada cuando se ejecuta como servicio.
    """
    # Verificar si stdout es una terminal
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        print(*args, **kwargs)
    # Si no hay terminal, no hacer nada (silencioso)


class BackupVariables:
    """
    Gestor de backup para variables dinámicas.
    Maneja variables que se crean/actualizan desde el diccionario 'sensores'.
    Con actualización en caliente de configuración.
    """
    
    def __init__(self, archivo_config: str = "/home/pi/PVControl+/Parametros_FV.py"):
        """
        Inicializa el gestor de backup.
        
        Args:
            archivo_config: Archivo de configuración con diccionario 'sensores'
        """
        self.archivo_config = archivo_config
        self.ruta_config = Path(archivo_config)
        
        # Cargar configuración inicial
        self.config = self._cargar_configuracion()
        
        # Estado interno
        self.espacio_nombres = None
        self.estado_guardado = {}
        self.en_ejecucion = False
        self.contador_backups = 0
        self.errores = 0
        self.hilo_backup = None
        self.evento_detener = threading.Event()
        
        # Mostrar configuración cargada
        self._mostrar_configuracion()
        
        # Tiempo de última modificación del archivo de configuración
        self.ultima_modificacion_config = self._obtener_tiempo_modificacion()
    
    def _obtener_tiempo_modificacion(self) -> float:
        """Obtiene tiempo de última modificación del archivo de configuración"""
        if self.ruta_config.exists():
            return self.ruta_config.stat().st_mtime
        return 0
    
    def _config_ha_cambiado(self) -> bool:
        """Verifica si el archivo de configuración ha cambiado"""
        if not self.ruta_config.exists():
            return False
        
        tiempo_actual = self.ruta_config.stat().st_mtime
        if tiempo_actual > self.ultima_modificacion_config:
            self.ultima_modificacion_config = tiempo_actual
            return True
        return False
    
    def _actualizar_config_si_cambio(self):
        """Actualiza configuración si el archivo ha cambiado"""
        if self._config_ha_cambiado():
            print("🔄 [Backup] Archivo de configuración modificado, recargando...")
            
            # Guardar configuración anterior para comparar
            intervalo_anterior = self.intervalo_backup
            variables_anteriores = set(self.variables_a_respaldar)
            
            # Recargar configuración
            self.config = self._cargar_configuracion()
            
            # Extraer parámetros actualizados
            self._extraer_parametros_config()
            
            # Verificar cambios
            cambios = []
            
            # Cambio en intervalo
            if self.intervalo_backup != intervalo_anterior:
                cambios.append(f"Intervalo: {intervalo_anterior} → {self.intervalo_backup} min")
            
            # Cambios en variables
            variables_actuales = set(self.variables_a_respaldar)
            añadidas = variables_actuales - variables_anteriores
            eliminadas = variables_anteriores - variables_actuales
            
            if añadidas:
                cambios.append(f"+{len(añadidas)} variables")
            if eliminadas:
                cambios.append(f"-{len(eliminadas)} variables")
            
            if cambios:
                print(f"   Cambios aplicados: {', '.join(cambios)}")
            else:
                print("   (Sin cambios relevantes)")
            
            return True
        return False
    
    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Carga configuración desde archivo Python"""
        if not self.ruta_config.exists():
            print(f"⚠️  [Backup] Archivo {self.archivo_config} no encontrado")
            return self._configuracion_por_defecto()
        
        try:
            # Crear módulo dinámico desde archivo
            especificacion = importlib.util.spec_from_file_location("modulo_config", self.ruta_config)
            modulo = importlib.util.module_from_spec(especificacion)
            
            # Necesitamos definir d_ para evitar errores durante la carga
            modulo.d_ = {}  # Diccionario vacío temporal
            
            especificacion.loader.exec_module(modulo)
            
            # Recoger variables de configuración
            configuracion = {}
            for nombre_atributo in dir(modulo):
                if not nombre_atributo.startswith("__"):
                    configuracion[nombre_atributo] = getattr(modulo, nombre_atributo)
            
            # Limpiar la variable temporal d_
            if 'd_' in configuracion:
                del configuracion['d_']
            
            return configuracion
            
        except Exception as e:
            print(f"❌ [Backup] Error cargando {self.archivo_config}: {e}")
            return self._configuracion_por_defecto()
    
    def _extraer_parametros_config(self):
        """Extrae parámetros de configuración del diccionario config"""
        # Extraer parámetros de backup
        self.variables_a_respaldar = self.config.get("VARIABLES_BACKUP", [])
        self.intervalo_backup = self.config.get("INTERVALO_BACKUP_MINUTOS", 5)
        nombre_archivo_backup = self.config.get("ARCHIVO_BACKUP", "backup_estado_fv.json")
        self.archivo_backup = Path(nombre_archivo_backup)
        
        # Obtener variables del diccionario 'sensores' si existe
        self.diccionario_sensores = self.config.get("sensores", {})
        
        # Si no hay VARIABLES_BACKUP definidas, usar las claves de 'sensores'
        if not self.variables_a_respaldar and self.diccionario_sensores:
            self.variables_a_respaldar = list(self.diccionario_sensores.keys())
    
    def _configuracion_por_defecto(self) -> Dict[str, Any]:
        """Configuración por defecto si hay error"""
        return {
            "VARIABLES_BACKUP": [],
            "INTERVALO_BACKUP_MINUTOS": 5,
            "ARCHIVO_BACKUP": "backup_estado_fv.json",
            "sensores": {}
        }
    
    def _mostrar_configuracion(self):
        """Muestra la configuración cargada"""
        # Primero extraer parámetros
        self._extraer_parametros_config()
        
        print(f"\n{'='*50}")
        print("CONFIGURACIÓN BACKUP CARGADA:")
        print(f"  Archivo: {self.archivo_config}")
        
        # Mostrar origen de las variables
        if self.diccionario_sensores and not self.config.get("VARIABLES_BACKUP"):
            print(f"  Variables desde 'sensores': {len(self.variables_a_respaldar)}")
        else:
            print(f"  Variables desde 'VARIABLES_BACKUP': {len(self.variables_a_respaldar)}")
        
        # Mostrar algunas variables como ejemplo
        if len(self.variables_a_respaldar) <= 15:
            for variable in self.variables_a_respaldar[:15]:
                print(f"    • {variable}")
            if len(self.variables_a_respaldar) > 15:
                print(f"    • ... y {len(self.variables_a_respaldar) - 15} más")
        else:
            print(f"    • {len(self.variables_a_respaldar)} variables definidas")
        
        print(f"  Intervalo: {self.intervalo_backup} minutos")
        print(f"  Archivo backup: {self.archivo_backup}")
        print(f"  Actualización en caliente: ACTIVADA")
        print(f"{'='*50}")
    
    def iniciar(self, espacio_nombres: Dict[str, Any] = None):
        """
        Inicia el sistema de backup.
        
        Args:
            espacio_nombres: Diccionario donde buscar variables (opcional).
                           Si es None, usa globals() del llamador.
        """
        # Determinar espacio de nombres
        if espacio_nombres is not None:
            self.espacio_nombres = espacio_nombres
        else:
            # Usar globals() del frame que llamó a este método
            marco = sys._getframe(1)
            self.espacio_nombres = marco.f_globals
        
        print(f"🔗 [Backup] Espacio de nombres conectado")
        
        # Cargar estado previo si existe
        if self.cargar_estado():
            # Restaurar variables
            restauradas = self.restaurar_variables()
            print(f"🔄 [Backup] {len(restauradas)} variables restauradas desde backup")
            
            # Mostrar algunas variables restauradas importantes
            variables_mostrar = ['Vbat', 'Ibat', 'Iplaca', 'SOC', 'Wh_MPPT1', 'contador_ciclos']
            for var in variables_mostrar:
                if var in restauradas and restauradas[var] is not None:
                    print(f"   • {var} = {restauradas[var]}")
        else:
            print("📭 [Backup] No hay backup previo, iniciando desde cero")
        
        # Iniciar backup automático
        self._iniciar_backup_automatico()
        
        self.en_ejecucion = True
        print("✅ [Backup] Sistema iniciado correctamente")
    
    def guardar_estado(self, mostrar_mensaje: bool = False) -> bool:
        """
        Guarda el estado actual de las variables configuradas.
        
        Args:
            mostrar_mensaje: Si True, muestra mensaje incluso si no hay cambios
            
        Returns:
            True si se guardó correctamente
        """
        # Verificar si la configuración ha cambiado
        self._actualizar_config_si_cambio()
        
        if not self.variables_a_respaldar:
            if mostrar_mensaje:
                print("⚠️  [Backup] No hay variables configuradas para backup")
            return False
        
        try:
            estado_actual = {}
            variables_encontradas = 0
            variables_faltantes = []
            
            for nombre_variable in self.variables_a_respaldar:
                if nombre_variable in self.espacio_nombres:
                    valor = self.espacio_nombres[nombre_variable]
                    estado_actual[nombre_variable] = self._serializar_valor(valor)
                    variables_encontradas += 1
                else:
                    # Variable no existe aún (puede ser normal en tu sistema dinámico)
                    estado_actual[nombre_variable] = None
                    variables_faltantes.append(nombre_variable)
            
            # Crear estructura de backup
            datos_backup = {
                'marca_temporal': datetime.now().isoformat(),
                'variables': estado_actual,
                'metadatos': {
                    'numero_backup': self.contador_backups + 1,
                    'total_variables': len(self.variables_a_respaldar),
                    'variables_encontradas': variables_encontradas,
                    'variables_faltantes': variables_faltantes,
                    'origen': 'sensores' if self.diccionario_sensores else 'VARIABLES_BACKUP',
                    'intervalo_config': self.intervalo_backup
                },
                'configuracion': {
                    'variables_lista': self.variables_a_respaldar,
                    'intervalo_minutos': self.intervalo_backup,
                    'archivo_config': self.archivo_config
                }
            }
            
            # Guardar en archivo temporal primero
            archivo_temporal = self.archivo_backup.with_suffix('.tmp')
            
            with open(archivo_temporal, 'w', encoding='utf-8') as archivo:
                json.dump(datos_backup, archivo, indent=2, ensure_ascii=False)
            
            # Renombrar (operación atómica)
            archivo_temporal.replace(self.archivo_backup)
            
            # Actualizar estado interno
            self.estado_guardado = estado_actual
            self.contador_backups += 1
            
            if mostrar_mensaje:
                print(f"💾 [Backup] Guardadas {variables_encontradas}/{len(self.variables_a_respaldar)} variables "
                      f"(backup #{self.contador_backups}) - Intervalo: {self.intervalo_backup} min")
                
                # Mostrar algunas variables importantes guardadas
                if variables_encontradas > 0:
                    variables_importantes = ['Vbat', 'Ibat', 'Iplaca', 'Wh_MPPT1', 'SOC']
                    print(f"   Ejemplos: ", end="")
                    ejemplos = []
                    for var in variables_importantes:
                        if var in estado_actual and estado_actual[var] is not None:
                            ejemplos.append(f"{var}={estado_actual[var]}")
                    if ejemplos:
                        print(", ".join(ejemplos[:3]))
            
            return True
            
        except Exception as e:
            print(f"❌ [Backup] Error guardando estado: {e}")
            self.errores += 1
            return False
    
    def _serializar_valor(self, valor: Any) -> Any:
        """Convierte valores complejos a serializables"""
        if valor is None:
            return None
        
        try:
            # Intentar serialización JSON directa
            json.dumps(valor)
            return valor
        except (TypeError, ValueError):
            # Conversiones para tipos comunes
            if isinstance(valor, datetime):
                return valor.isoformat()
            elif hasattr(valor, 'isoformat'):
                # Para objetos con método isoformat()
                return valor.isoformat()
            elif isinstance(valor, (int, float)):
                # Para números, redondear si es float
                if isinstance(valor, float):
                    return round(valor, 6)
                return valor
            elif hasattr(valor, '__dict__'):
                # Para objetos con atributos
                try:
                    return {k: self._serializar_valor(v) for k, v in valor.__dict__.items()}
                except:
                    return str(valor)
            else:
                return str(valor)
    
    def cargar_estado(self) -> bool:
        """Carga el estado guardado desde archivo"""
        if not self.archivo_backup.exists():
            return False
        
        try:
            with open(self.archivo_backup, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
            
            self.estado_guardado = datos.get('variables', {})
            
            marca_temporal = datos.get('marca_temporal', 'desconocido')
            metadatos = datos.get('metadatos', {})
            
            print(f"📂 [Backup] Estado cargado desde {marca_temporal}")
            print(f"   Variables en backup: {metadatos.get('variables_encontradas', 0)}/"
                  f"{metadatos.get('total_variables', 0)}")
            
            # Restaurar intervalo si estaba guardado
            intervalo_guardado = metadatos.get('intervalo_config')
            if intervalo_guardado:
                print(f"   Intervalo en backup: {intervalo_guardado} min")
            
            return True
            
        except Exception as e:
            print(f"❌ [Backup] Error cargando backup: {e}")
            return False
    
    def restaurar_variables(self) -> Dict[str, Any]:
        """
        Restaura variables desde el estado guardado al espacio de nombres actual.
        
        Returns:
            Diccionario con variables restauradas
        """
        if not self.estado_guardado:
            return {}
        
        restauradas = {}
        
        for nombre_variable, valor in self.estado_guardado.items():
            if nombre_variable in self.variables_a_respaldar and valor is not None:
                # Restaurar el valor
                self.espacio_nombres[nombre_variable] = valor
                restauradas[nombre_variable] = valor
        
        return restauradas
    
    def _iniciar_backup_automatico(self):
        """Inicia backup automático en segundo plano con chequeo dinámico de intervalo"""
        def bucle_backup():
            # Intervalo inicial
            intervalo_actual = self.intervalo_backup
            tiempo_proximo_backup = time.time() + (intervalo_actual * 60)
            
            while not self.evento_detener.is_set():
                tiempo_actual = time.time()
                
                # Verificar si es tiempo de hacer backup
                if tiempo_actual >= tiempo_proximo_backup:
                    # Hacer backup
                    if self.en_ejecucion:
                        self.guardar_estado(mostrar_mensaje=True)
                    
                    # Recalcular próximo backup con intervalo actualizado
                    self._actualizar_config_si_cambio()  # Chequear cambios
                    intervalo_actual = self.intervalo_backup
                    tiempo_proximo_backup = time.time() + (intervalo_actual * 60)
                
                # Dormir un tiempo corto para ser responsivo
                time.sleep(1)  # Chequear cada segundo
                
                # Chequear cambios de configuración periódicamente
                if tiempo_actual % 30 < 1:  # Cada ~30 segundos
                    if self._actualizar_config_si_cambio():
                        # Si cambió el intervalo, recalcular próximo backup
                        if intervalo_actual != self.intervalo_backup:
                            print(f"🔄 [Backup] Intervalo cambiado: {intervalo_actual} → {self.intervalo_backup} min")
                            intervalo_actual = self.intervalo_backup
                            tiempo_proximo_backup = time.time() + (intervalo_actual * 60)
        
        self.hilo_backup = threading.Thread(target=bucle_backup, daemon=True)
        self.hilo_backup.start()
        
        print(f"⏰ [Backup] Auto-backup cada {self.intervalo_backup} minutos (actualizable en caliente)")
    
    def detener(self):
        """Detiene el sistema de backup"""
        print("\n💾 [Backup] Guardando estado final...")
        self.guardar_estado(mostrar_mensaje=True)
        self.en_ejecucion = False
        self.evento_detener.set()
        
        # Esperar a que el hilo termine (máximo 2 segundos)
        if self.hilo_backup and self.hilo_backup.is_alive():
            self.hilo_backup.join(timeout=2)
        
        print("🛑 [Backup] Sistema detenido")
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de backup"""
        return {
            'en_ejecucion': self.en_ejecucion,
            'contador_backups': self.contador_backups,
            'errores': self.errores,
            'variables_configuradas': len(self.variables_a_respaldar),
            'intervalo_actual': self.intervalo_backup,
            'archivo_backup': str(self.archivo_backup),
            'ultimo_backup': self.estado_guardado.get('_marca_temporal') if self.estado_guardado else None,
            'actualizacion_caliente': True
        }
    
    def forzar_backup_ahora(self):
        """Fuerza un backup inmediato"""
        print("💾 [Backup] Backup manual solicitado...")
        exito = self.guardar_estado(mostrar_mensaje=True)
        if exito:
            print("✅ [Backup] Backup manual completado")
        return exito
    
    def actualizar_lista_variables(self, nuevas_variables: List[str]):
        """
        Actualiza dinámicamente la lista de variables a respaldar.
        
        Args:
            nuevas_variables: Nueva lista de variables
        """
        antiguas = set(self.variables_a_respaldar)
        nuevas = set(nuevas_variables)
        
        añadidas = nuevas - antiguas
        eliminadas = antiguas - nuevas
        
        self.variables_a_respaldar = nuevas_variables
        
        if añadidas:
            print(f"➕ [Backup] {len(añadidas)} variables añadidas")
        if eliminadas:
            print(f"➖ [Backup] {len(eliminadas)} variables eliminadas")
        
        print(f"📊 [Backup] Total variables a respaldar: {len(self.variables_a_respaldar)}")
    
    def verificar_y_actualizar_config(self) -> bool:
        """
        Verifica y actualiza configuración manualmente.
        Útil para llamar desde tu bucle principal.
        
        Returns:
            True si hubo cambios
        """
        return self._actualizar_config_si_cambio()

# Función de conveniencia
def configurar_backup(archivo_config: str = "/home/pi/PVControl+/Parametros_FV.py") -> BackupVariables:
    """
    Crea e inicia un gestor de backup.
    
    Args:
        archivo_config: Archivo de configuración
        
    Returns:
        Instancia de BackupVariables iniciada
    """
    backup = BackupVariables(archivo_config)
    backup.iniciar()
    return backup