#!/home/pi/PVControl+/env/bin/python3
"""
Editor Profesional Multi-Archivo para PVControl+
PVControl+ - Editor de Configuración Avanzado con Multi-Pestañas
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import subprocess
import re
import difflib
from datetime import datetime
import shutil
import MySQLdb
import json

class EditorConfigProfesional:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PVControl+ - Editor Multi-Archivo")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f5f5f5')
        
        # Configuración de archivos
        self.archivos_config = {
            'Parametros_FV.py': {
                'ruta': '/home/pi/PVControl+/Parametros_FV.py',
                'tipo': 'python',
                'contenido_original': ''
            },
            'Parametros_Web.js': {
                'ruta': '/home/pi/PVControl+/html/Parametros_Web.js',
                'tipo': 'javascript', 
                'contenido_original': ''
            },
            'version.inc': {  # NUEVO
                'ruta': '/home/pi/PVControl+/html/version.inc',
                'tipo': 'php',
                'contenido_original': ''
            },
            'configuracion_activa.txt': {
                'ruta': '/home/pi/PVControl+/html/configuracion_activa.txt',
                'tipo': 'texto',
                'contenido_original': ''
            }
        }
        
        self.archivo_actual = 'Parametros_FV.py'
        self.contenido_original_actual = ""
        
        # Configuración de BD
        self.config_bd = {
            'servidor': 'localhost',
            'usuario': 'rpi',
            'clave': 'fv',
            'basedatos': 'control_solar'
        }
        
        # Configuración de resaltado
        self.colors = {
            'python_keyword': '#0000FF',
            'python_string': '#008000',
            'python_comment': '#808080',
            'python_number': '#FF00FF',
            'python_variable': '#000080',
            'python_function': '#008080',
            'js_keyword': '#0000FF',
            'js_string': '#008000',
            'js_comment': '#808080',
            'js_number': '#FF00FF',
            'js_variable': '#800080',
            'js_function': '#008080'
        }
        
        self.python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        
        self.javascript_keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
            'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
            'if', 'import', 'in', 'instanceof', 'new', 'return', 'super', 'switch',
            'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',
            'let', 'static', 'await', 'async', 'true', 'false', 'null', 'undefined'
        ]
        
        self.setup_ui()
        self.cargar_config_bd_desde_archivo()
        self.cargar_archivo_actual()
    
    def setup_ui(self):
        # Crear menú
        self.crear_menu()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de herramientas
        self.crear_barra_herramientas(main_frame)
        
        # Selector de archivos
        self.crear_selector_archivos(main_frame)
        
        # Panel de edición
        self.crear_panel_edicion(main_frame)
        
        # Panel de búsqueda/reemplazo (inicialmente oculto)
        self.crear_panel_busqueda(main_frame)
        
        # Barra de estado
        self.crear_barra_estado(main_frame)
    
    def crear_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo", command=self.nuevo_archivo)
        menu_archivo.add_command(label="Abrir...", command=self.abrir_archivo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo_actual, accelerator="Ctrl+S")
        menu_archivo.add_command(label="Guardar como...", command=self.guardar_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.salir)
        
        # Menú Editar
        menu_editar = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=menu_editar)
        menu_editar.add_command(label="Deshacer", command=self.deshacer, accelerator="Ctrl+Z")
        menu_editar.add_command(label="Rehacer", command=self.rehacer, accelerator="Ctrl+Y")
        menu_editar.add_separator()
        menu_editar.add_command(label="Buscar", command=self.mostrar_busqueda, accelerator="Ctrl+F")
        menu_editar.add_command(label="Reemplazar", command=self.mostrar_reemplazar, accelerator="Ctrl+H")
        
        # Menú Archivos de Configuración - ACTUALIZADO con version.inc
        menu_configs = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configuraciones", menu=menu_configs)
        menu_configs.add_command(label="📄 Parametros_FV.py", 
                               command=lambda: self.cambiar_archivo('Parametros_FV.py'))
        menu_configs.add_command(label="🌐 Parametros_Web.js", 
                               command=lambda: self.cambiar_archivo('Parametros_Web.js'))
        menu_configs.add_command(label="ℹ️ version.inc",  # NUEVO
                               command=lambda: self.cambiar_archivo('version.inc'))
        menu_configs.add_command(label="⚙️ configuracion_activa.txt", 
                               command=lambda: self.cambiar_archivo('configuracion_activa.txt'))
        menu_configs.add_separator()
        menu_configs.add_command(label="📂 Configuraciones JS", 
                               command=self.mostrar_selector_configuraciones)
        menu_configs.add_command(label="🔍 Configuración Activa Actual", 
                               command=self.mostrar_configuracion_activa)
        
        # Menú Base de Datos
        menu_bd = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Base de Datos", menu=menu_bd)
        menu_bd.add_command(label="📊 Ver Tabla Equipos", command=self.ver_tabla_equipos)
        menu_bd.add_command(label="🔧 Probar Conexión BD", command=self.probar_conexion_bd)
        menu_bd.add_command(label="📋 Configurar Conexión BD", command=self.configurar_conexion_bd)
        
        # Menú Ver
        menu_ver = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=menu_ver)
        menu_ver.add_command(label="Vista Previa Cambios", command=self.vista_previa_cambios)
        
        # Atajos de teclado
        self.root.bind('<Control-s>', lambda e: self.guardar_archivo_actual())
        self.root.bind('<Control-f>', lambda e: self.mostrar_busqueda())
        self.root.bind('<Control-h>', lambda e: self.mostrar_reemplazar())
        self.root.bind('<Control-z>', lambda e: self.deshacer())

    def mostrar_configuracion_activa(self):
        """Muestra información sobre la configuración activa actual"""
        config_activa = self.obtener_configuracion_activa()
        
        if config_activa:
            ruta_completa = f"/home/pi/PVControl+/html/configuraciones/{config_activa}"
            existe = "✅ EXISTE" if os.path.exists(ruta_completa) else "❌ NO EXISTE"
            
            mensaje = f"""
    📋 CONFIGURACIÓN ACTIVA ACTUAL

    Archivo: {config_activa}
    Ruta: {ruta_completa}
    Estado: {existe}

    ¿Quieres abrir este archivo?
    """
            respuesta = messagebox.askyesno("Configuración Activa", mensaje)
            if respuesta:
                self.abrir_archivo_configuracion_js(ruta_completa, config_activa)
        else:
            messagebox.showinfo("Configuración Activa", 
                              "No hay configuración activa establecida.\n\n"
                              "Usa el selector de configuraciones JS para establecer una.")
    
    def crear_barra_herramientas(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        buttons = [
            ("💾 Guardar", self.guardar_archivo_actual),
            ("🔄 Recargar", self.cargar_archivo_actual),
            ("📋 Backup", self.crear_backup_actual),
            ("⚙️ Validar", self.validar_sintaxis_actual),
            ("🔍 Buscar", self.mostrar_busqueda),
            ("📊 Vista Previa", self.vista_previa_cambios),
            ("🎨 Resaltar", self.resaltar_sintaxis_actual),
            ("📊 BD Equipos", self.ver_tabla_equipos)
        ]
        
        for text, command in buttons:
            ttk.Button(toolbar, text=text, command=command).pack(side=tk.LEFT, padx=2)

    def crear_selector_archivos(self, parent):
        """Crea el selector de archivos de configuración"""
        selector_frame = ttk.Frame(parent)
        selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(selector_frame, text="Archivo de Configuración:", 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Botones para cada archivo principal - ACTUALIZADO con version.inc
        archivos_principales = [
            ("📄 Parametros_FV.py", 'Parametros_FV.py'),
            ("🌐 Parametros_Web.js", 'Parametros_Web.js'),
            ("ℹ️ version.inc", 'version.inc'),  # NUEVO
            ("⚙️ config_activa.txt", 'configuracion_activa.txt')
        ]
        
        for texto, archivo in archivos_principales:
            btn = ttk.Button(selector_frame, text=texto, 
                           command=lambda a=archivo: self.cambiar_archivo(a))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Separador
        ttk.Separator(selector_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Botón para configuraciones JS
        ttk.Button(selector_frame, text="📂 Configuraciones JS", 
                  command=self.mostrar_selector_configuraciones).pack(side=tk.LEFT, padx=2)
        
        # Indicador del archivo actual
        self.indicador_archivo = tk.StringVar()
        self.actualizar_indicador_archivo()
        
        indicador_label = tk.Label(selector_frame, textvariable=self.indicador_archivo,
                                 font=("Arial", 9, "italic"), foreground="#666666")
        indicador_label.pack(side=tk.RIGHT, padx=10)

    def mostrar_selector_configuraciones(self):
        """Muestra un diálogo para seleccionar archivos de configuración JS - VERSIÓN CORREGIDA"""
        # Obtener lista de archivos JS en la carpeta configuraciones
        configuraciones_dir = "/home/pi/PVControl+/html/configuraciones"
        archivos_js = []
        
        try:
            if os.path.exists(configuraciones_dir):
                for archivo in os.listdir(configuraciones_dir):
                    if archivo.endswith('.js'):
                        archivos_js.append(archivo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer configuraciones: {e}")
            return
        
        if not archivos_js:
            messagebox.showinfo("Configuraciones", "No se encontraron archivos .js en configuraciones/")
            return
        
        # Crear ventana de selección CORREGIDA
        selector_window = tk.Toplevel(self.root)
        selector_window.title("Seleccionar Configuración JS")
        selector_window.geometry("500x400")
        selector_window.transient(self.root)  # IMPORTANTE: Hacerla hija de la ventana principal
        selector_window.grab_set()  # IMPORTANTE: Hacerla modal
        
        # Forzar el foco
        selector_window.focus_force()
        
        main_frame = ttk.Frame(selector_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Selecciona un archivo de configuración:", 
                font=("Arial", 11, "bold")).pack(pady=(0, 10))
        
        # Frame para la lista
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Listbox con scroll
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_configuraciones = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set, 
            font=("Arial", 10),
            selectmode=tk.SINGLE  # Asegurar modo selección simple
        )
        self.lista_configuraciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_configuraciones.yview)
        
        # Insertar archivos en la lista
        for archivo in sorted(archivos_js):
            self.lista_configuraciones.insert(tk.END, archivo)
        
        # Seleccionar el primer elemento por defecto
        if archivos_js:
            self.lista_configuraciones.selection_set(0)
            self.lista_configuraciones.activate(0)
        
        # Información adicional
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Obtener configuración activa actual
        config_activa = self.obtener_configuracion_activa()
        if config_activa:
            tk.Label(info_frame, text=f"Configuración activa actual: {config_activa}",
                    font=("Arial", 9, "bold"), foreground="#2c3e50").pack(anchor=tk.W)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📝 Abrir Seleccionado", 
                  command=lambda: self.abrir_configuracion_js(selector_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⭐ Establecer como Activa", 
                  command=lambda: self.establecer_configuracion_activa(selector_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cerrar", 
                  command=selector_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Doble click para abrir rápido
        self.lista_configuraciones.bind('<Double-1>', lambda e: self.abrir_configuracion_js(selector_window))
        
        # Enter para abrir
        self.lista_configuraciones.bind('<Return>', lambda e: self.abrir_configuracion_js(selector_window))
        
        # Forzar actualización y foco
        selector_window.update()
        self.lista_configuraciones.focus_set()
        
    def obtener_configuracion_activa(self):
        """Obtiene la configuración activa actual del archivo configuracion_activa.txt"""
        try:
            ruta_config_activa = self.archivos_config['configuracion_activa.txt']['ruta']
            if os.path.exists(ruta_config_activa):
                with open(ruta_config_activa, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except:
            pass
        return None

    def abrir_configuracion_js(self, ventana_parent=None):
        """Abre el archivo de configuración JS seleccionado - VERSIÓN CORREGIDA"""
        seleccion = self.lista_configuraciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Por favor selecciona un archivo de la lista")
            return
        
        nombre_archivo = self.lista_configuraciones.get(seleccion[0])
        ruta_completa = f"/home/pi/PVControl+/html/configuraciones/{nombre_archivo}"
        
        # Cerrar ventana de selección si existe
        if ventana_parent:
            ventana_parent.grab_release()  # IMPORTANTE: Liberar el grab
            ventana_parent.destroy()
        
        # Abrir el archivo JS
        self.abrir_archivo_configuracion_js(ruta_completa, nombre_archivo)

    def abrir_archivo_configuracion_js(self, ruta_archivo, nombre_mostrar):
        """Abre un archivo de configuración JS en el editor"""
        if self.hay_cambios_sin_guardar():
            respuesta = messagebox.askyesnocancel(
                "Abrir archivo", 
                f"Tienes cambios sin guardar en {self.archivo_actual}. ¿Quieres guardarlos antes de abrir otro archivo?",
                icon=messagebox.WARNING
            )
            
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí
                self.guardar_archivo_actual()
        
        try:
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Actualizar el editor con el nuevo contenido
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, contenido)
                
                # Actualizar estado para este archivo temporal
                self.archivo_actual = f"configuraciones/{nombre_mostrar}"
                self.contenido_original_actual = contenido
                
                self.resaltar_sintaxis_javascript()
                self.actualizar_posicion_cursor()
                self.actualizar_indicador_archivo_personalizado(nombre_mostrar, ruta_archivo)
                self.status_text.set(f"Archivo cargado: {nombre_mostrar}")
                
            else:
                messagebox.showerror("Error", f"No se encuentra el archivo:\n{ruta_archivo}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar {nombre_mostrar}:\n{e}")

    def establecer_configuracion_activa(self, ventana_parent=None):
        """Establece la configuración seleccionada como activa"""
        seleccion = self.lista_configuraciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Por favor selecciona un archivo de la lista")
            return
        
        nombre_archivo = self.lista_configuraciones.get(seleccion[0])
        
        try:
            ruta_config_activa = self.archivos_config['configuracion_activa.txt']['ruta']
            
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_config_activa)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Escribir el nombre del archivo en configuracion_activa.txt
            with open(ruta_config_activa, 'w', encoding='utf-8') as f:
                f.write(nombre_archivo)
            
            # Actualizar el contenido original en memoria
            self.archivos_config['configuracion_activa.txt']['contenido_original'] = nombre_archivo
            
            messagebox.showinfo("Configuración Activa", 
                              f"✅ Configuración activa establecida:\n{nombre_archivo}")
            
            # Cerrar ventana si se proporcionó
            if ventana_parent:
                ventana_parent.grab_release()
                ventana_parent.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo establecer configuración activa:\n{e}")

    def actualizar_indicador_archivo_personalizado(self, nombre_archivo, ruta_completa):
        """Actualiza el indicador para archivos personalizados"""
        self.indicador_archivo.set(f"Editando: {nombre_archivo} (javascript)")
        self.archivo_info.set(ruta_completa)

    def guardar_archivo_configuracion_js(self):
        """Guarda un archivo de configuración JS temporal"""
        if not self.archivo_actual.startswith('configuraciones/'):
            self.guardar_archivo_actual()
            return
        
        # Extraer nombre de archivo de la ruta temporal
        nombre_archivo = self.archivo_actual.replace('configuraciones/', '')
        ruta_completa = f"/home/pi/PVControl+/html/configuraciones/{nombre_archivo}"
        
        try:
            contenido = self.text_area.get(1.0, tk.END)
            
            # Remover newline extra de tkinter
            if contenido and contenido.endswith('\n'):
                contenido = contenido[:-1]
            
            # Crear directorio si no existe
            directorio = os.path.dirname(ruta_completa)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Actualizar contenido original
            self.contenido_original_actual = contenido
            
            self.status_text.set(f"✅ {nombre_archivo} guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar {nombre_archivo}:\n{e}")
 
    def crear_panel_edicion(self, parent):
        # Frame para editor
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto principal
        self.text_area = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            width=85,
            height=35,
            font=("Courier New", 10),
            undo=True,
            maxundo=-1
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area.configure(xscrollcommand=h_scrollbar.set)
        
        # Configurar eventos
        self.text_area.bind('<KeyRelease>', self.actualizar_posicion_cursor)
        self.text_area.bind('<Button-1>', self.actualizar_posicion_cursor)
        self.text_area.bind('<KeyRelease>', lambda e: self.resaltar_sintaxis_actual())
    
    def crear_panel_busqueda(self, parent):
        self.panel_busqueda = ttk.Frame(parent)
        
        # Buscar
        ttk.Label(self.panel_busqueda, text="Buscar:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_buscar = ttk.Entry(self.panel_busqueda, width=30)
        self.entry_buscar.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(self.panel_busqueda, text="Buscar", 
                  command=self.buscar_siguiente).grid(row=0, column=2, padx=2, pady=2)
        ttk.Button(self.panel_busqueda, text="Buscar Todos", 
                  command=self.buscar_todos).grid(row=0, column=3, padx=2, pady=2)
        
        # Reemplazar
        ttk.Label(self.panel_busqueda, text="Reemplazar:").grid(row=1, column=0, padx=5, pady=2)
        self.entry_reemplazar = ttk.Entry(self.panel_busqueda, width=30)
        self.entry_reemplazar.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(self.panel_busqueda, text="Reemplazar", 
                  command=self.reemplazar).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(self.panel_busqueda, text="Reemplazar Todos", 
                  command=self.reemplazar_todos).grid(row=1, column=3, padx=2, pady=2)
        
        ttk.Button(self.panel_busqueda, text="❌", 
                  command=self.ocultar_busqueda).grid(row=0, column=4, rowspan=2, padx=5, pady=2)
    
    def crear_barra_estado(self, parent):
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Estado general
        self.status_text = tk.StringVar()
        self.status_text.set("Listo")
        ttk.Label(self.status_bar, textvariable=self.status_text).pack(side=tk.LEFT)
        
        # Información de archivo actual
        self.archivo_info = tk.StringVar()
        self.actualizar_info_archivo()
        ttk.Label(self.status_bar, textvariable=self.archivo_info, 
                 font=("Courier New", 8)).pack(side=tk.LEFT, padx=20)
        
        # Información de posición del cursor
        self.cursor_pos = tk.StringVar()
        self.cursor_pos.set("Línea: 1, Columna: 1")
        ttk.Label(self.status_bar, textvariable=self.cursor_pos, 
                 font=("Courier New", 9, "bold"),
                 foreground="#2c3e50").pack(side=tk.RIGHT, padx=10)
    
    # ========== MÉTODOS DE GESTIÓN DE ARCHIVOS ==========
    
    def cambiar_archivo(self, nombre_archivo):
        """Cambia al archivo especificado"""
        if self.hay_cambios_sin_guardar():
            respuesta = messagebox.askyesnocancel(
                "Cambiar archivo", 
                f"Tienes cambios sin guardar en {self.archivo_actual}. ¿Quieres guardarlos antes de cambiar?",
                icon=messagebox.WARNING
            )
            
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí
                self.guardar_archivo_actual()
        
        self.archivo_actual = nombre_archivo
        self.cargar_archivo_actual()
        self.actualizar_indicador_archivo()
        self.actualizar_info_archivo()
    
    def cargar_archivo_actual(self):
        """Carga el archivo actualmente seleccionado"""
        archivo_info = self.archivos_config[self.archivo_actual]
        
        try:
            if os.path.exists(archivo_info['ruta']):
                with open(archivo_info['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                archivo_info['contenido_original'] = contenido
                self.contenido_original_actual = contenido
                
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, contenido)
                self.resaltar_sintaxis_actual()
                self.actualizar_posicion_cursor()
                self.status_text.set(f"Archivo cargado: {self.archivo_actual}")
            else:
                # Si el archivo no existe, crear uno vacío
                archivo_info['contenido_original'] = ""
                self.contenido_original_actual = ""
                self.text_area.delete(1.0, tk.END)
                self.status_text.set(f"Archivo creado: {self.archivo_actual}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar {self.archivo_actual}:\n{e}")
    
    def guardar_archivo_actual(self):
        """Guarda el archivo actualmente seleccionado"""
        if self.archivo_actual.startswith('configuraciones/'):
            self.guardar_archivo_configuracion_js()
            return
        
        # ... el resto del método original permanece igual
        archivo_info = self.archivos_config[self.archivo_actual]
        
        try:
            contenido = self.text_area.get(1.0, tk.END)
            
            # CORRECCIÓN: Remover newline extra de tkinter
            if contenido and contenido.endswith('\n'):
                contenido = contenido[:-1]
            
            # Crear directorio si no existe
            directorio = os.path.dirname(archivo_info['ruta'])
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            with open(archivo_info['ruta'], 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Actualizar contenido original
            archivo_info['contenido_original'] = contenido
            self.contenido_original_actual = contenido
            
            self.status_text.set(f"✅ {self.archivo_actual} guardado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar {self.archivo_actual}:\n{e}")
            
    def hay_cambios_sin_guardar(self):
        """Verifica si hay cambios sin guardar en el archivo actual - VERSIÓN CORREGIDA"""
        if self.archivo_actual not in self.archivos_config:
            return False
        
        contenido_actual = self.text_area.get(1.0, tk.END)
        
        # CORRECCIÓN: tkinter siempre agrega un newline final, así que lo removemos
        if contenido_actual and contenido_actual.endswith('\n'):
            contenido_actual = contenido_actual[:-1]
        
        return contenido_actual != self.contenido_original_actual
    
    def abrir_configuracion_activa(self):
        """Abre el archivo de configuración activa referenciado en configuracion_activa.txt"""
        try:
            # Leer el archivo configuracion_activa.txt
            ruta_config_activa = self.archivos_config['configuracion_activa.txt']['ruta']
            
            if os.path.exists(ruta_config_activa):
                with open(ruta_config_activa, 'r', encoding='utf-8') as f:
                    nombre_config = f.read().strip()
                
                if nombre_config:
                    # Construir la ruta completa
                    ruta_config = f"/home/pi/PVControl+/html/configuraciones/{nombre_config}"
                    
                    if os.path.exists(ruta_config):
                        # Abrir en una nueva ventana o en el editor actual
                        self.abrir_archivo_externo(ruta_config)
                    else:
                        messagebox.showerror("Error", f"No se encuentra el archivo:\n{ruta_config}")
                else:
                    messagebox.showinfo("Info", "El archivo configuracion_activa.txt está vacío")
            else:
                messagebox.showerror("Error", "No se encuentra configuracion_activa.txt")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir configuración activa:\n{e}")
    
    def abrir_archivo_externo(self, ruta_archivo):
        """Abre un archivo externo en una nueva ventana"""
        messagebox.showinfo("Abrir Archivo", 
                          f"Archivo de configuración activa:\n{ruta_archivo}\n\n"
                          f"Esta funcionalidad permitiría abrir el archivo referenciado.")
    
    def actualizar_indicador_archivo(self):
        """Actualiza el indicador del archivo actual"""
        archivo_info = self.archivos_config[self.archivo_actual]
        self.indicador_archivo.set(f"Editando: {self.archivo_actual} ({archivo_info['tipo']})")
    
    def actualizar_info_archivo(self):
        """Actualiza la información del archivo en la barra de estado"""
        archivo_info = self.archivos_config[self.archivo_actual]
        self.archivo_info.set(f"{archivo_info['ruta']}")
    
    # ========== MÉTODOS DE EDICIÓN ==========
    
    def actualizar_posicion_cursor(self, event=None):
        """Actualiza la posición del cursor en la barra de estado"""
        try:
            cursor_pos = self.text_area.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos.set(f"Línea: {line}, Columna: {int(col)+1}")
        except:
            pass
    
    def resaltar_sintaxis_actual(self):
        """Aplica resaltado de sintaxis según el tipo de archivo actual"""
        tipo_archivo = self.obtener_tipo_archivo_actual()
        
        if tipo_archivo == 'python':
            self.resaltar_sintaxis_python()
        elif tipo_archivo == 'javascript':
            self.resaltar_sintaxis_javascript()
        elif tipo_archivo == 'php':
            self.resaltar_sintaxis_php()
        # Para texto plano no aplicamos resaltado
    
    def resaltar_sintaxis_python(self):
        """Aplica resaltado de sintaxis Python"""
        content = self.text_area.get(1.0, tk.END)
        
        # Limpiar resaltado anterior
        for tag in self.text_area.tag_names():
            if tag not in ["sel", "busqueda"]:  # No remover selección y búsqueda
                self.text_area.tag_delete(tag)
        
        # Definir patrones para Python
        patterns = [
            (r'#.*$', 'python_comment'),
            (r'\b(' + '|'.join(self.python_keywords) + r')\b', 'python_keyword'),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'python_string'),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'python_string'),
            (r'\b[+-]?\d+\.?\d*\b', 'python_number'),
            (r'\b[A-Z_][A-Z0_9_]*\b', 'python_variable'),
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(', 'python_function')
        ]
        
        # Aplicar resaltado
        for pattern, tag in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_area.tag_add(tag, start, end)
                self.text_area.tag_config(tag, foreground=self.colors[tag])
    
    def resaltar_sintaxis_javascript(self):
        """Aplica resaltado de sintaxis JavaScript"""
        content = self.text_area.get(1.0, tk.END)
        
        # Limpiar resaltado anterior
        for tag in self.text_area.tag_names():
            if tag not in ["sel", "busqueda"]:
                self.text_area.tag_delete(tag)
        
        # Definir patrones para JavaScript
        patterns = [
            (r'//.*$', 'js_comment'),
            (r'/\*.*?\*/', 'js_comment'),
            (r'\b(' + '|'.join(self.javascript_keywords) + r')\b', 'js_keyword'),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'js_string'),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'js_string'),
            (r'\b[+-]?\d+\.?\d*\b', 'js_number'),
            (r'\b(var|let|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'js_variable'),
            (r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'js_function'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*function', 'js_function')
        ]
        
        # Aplicar resaltado
        for pattern, tag in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_area.tag_add(tag, start, end)
                self.text_area.tag_config(tag, foreground=self.colors[tag])

    def resaltar_sintaxis_php(self):
        """Aplica resaltado de sintaxis PHP"""
        content = self.text_area.get(1.0, tk.END)
        
        # Limpiar resaltado anterior
        for tag in self.text_area.tag_names():
            if tag not in ["sel", "busqueda"]:
                self.text_area.tag_delete(tag)
        
        # Palabras clave de PHP
        php_keywords = [
            'echo', 'print', 'if', 'else', 'elseif', 'while', 'for', 'foreach', 
            'function', 'return', 'class', 'public', 'private', 'protected', 
            'static', 'const', 'array', 'isset', 'empty', 'null', 'true', 'false'
        ]
        
        # Definir patrones para PHP
        patterns = [
            (r'//.*$', 'php_comment'),
            (r'#.*$', 'php_comment'),
            (r'/\*.*?\*/', 'php_comment'),
            (r'\b(' + '|'.join(php_keywords) + r')\b', 'php_keyword'),
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*', 'php_variable'),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 'php_string'),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 'php_string'),
            (r'\b[+-]?\d+\.?\d*\b', 'php_number'),
        ]
        
        # Configurar colores para PHP (puedes ajustarlos)
        php_colors = {
            'php_comment': '#808080',
            'php_keyword': '#0000FF', 
            'php_variable': '#800080',
            'php_string': '#008000',
            'php_number': '#FF00FF'
        }
        
        # Aplicar resaltado
        for pattern, tag in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_area.tag_add(tag, start, end)
                self.text_area.tag_config(tag, foreground=php_colors.get(tag, '#000000'))

    def obtener_tipo_archivo_actual(self):
        """Determina el tipo de archivo actual - maneja archivos temporales de configuraciones"""
        # Si es un archivo del diccionario principal
        if self.archivo_actual in self.archivos_config:
            return self.archivos_config[self.archivo_actual]['tipo']
        
        # Si es un archivo temporal de configuraciones JS
        if self.archivo_actual.startswith('configuraciones/') and self.archivo_actual.endswith('.js'):
            return 'javascript'
        
        # Determinar por extensión
        if self.archivo_actual.endswith('.py'):
            return 'python'
        elif self.archivo_actual.endswith('.js'):
            return 'javascript'
        elif self.archivo_actual.endswith('.php') or self.archivo_actual.endswith('.inc'):
            return 'php'
        else:
            return 'texto'

    
    def validar_sintaxis_actual(self):
        """Valida la sintaxis según el tipo de archivo actual - VERSIÓN CORREGIDA"""
        # Determinar el tipo de archivo actual
        tipo_archivo = self.obtener_tipo_archivo_actual()
        
        if tipo_archivo == 'python':
            self.validar_sintaxis_python()
        elif tipo_archivo == 'javascript':
            self.validar_sintaxis_javascript()
        elif tipo_archivo == 'php':
            self.validar_sintaxis_php()
        else:
            messagebox.showinfo("Validación", "No hay validación de sintaxis para este tipo de archivo")

    
    def validar_sintaxis_python(self):
        """Valida sintaxis Python"""
        try:
            contenido = self.text_area.get(1.0, tk.END)
            lineas = contenido.split('\n')
            
            # Guardar temporalmente para validar
            temp_file = "/tmp/pvconfig_temp.py"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Validar sintaxis con Python
            result = subprocess.run(
                ['python', '-m', 'py_compile', temp_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.status_text.set("✅ Sintaxis Python válida")
                messagebox.showinfo("Validación Python", "✅ La sintaxis Python es correcta")
            else:
                # Procesar el error para mostrar información útil
                error_info = self.procesar_error_sintaxis(result.stderr, lineas)
                self.mostrar_error_detallado(error_info, lineas)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_file + 'c'):
                os.remove(temp_file + 'c')
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo validar la sintaxis Python: {e}")

    
    def validar_sintaxis_javascript(self):
        """Valida sintaxis JavaScript básica"""
        contenido = self.text_area.get(1.0, tk.END)
        
        # Validaciones básicas de JavaScript
        errores = []
        
        # Verificar paréntesis balanceados
        if contenido.count('(') != contenido.count(')'):
            errores.append("Paréntesis no balanceados")
        
        # Verificar llaves balanceadas
        if contenido.count('{') != contenido.count('}'):
            errores.append("Llaves no balanceadas")
        
        # Verificar corchetes balanceados
        if contenido.count('[') != contenido.count(']'):
            errores.append("Corchetes no balanceados")
        
        if errores:
            mensaje = "Errores de sintaxis JavaScript:\n\n" + "\n".join(f"• {error}" for error in errores)
            messagebox.showerror("Error de Sintaxis JavaScript", mensaje)
        else:
            messagebox.showinfo("Validación JavaScript", "✅ Sintaxis JavaScript básica correcta")

    def validar_sintaxis_php(self):
        """Valida sintaxis PHP básica"""
        contenido = self.text_area.get(1.0, tk.END)
        
        # Validaciones básicas de PHP
        errores = []
        
        # Verificar que las etiquetas PHP estén balanceadas
        abiertas = contenido.count('<?php')
        cerradas = contenido.count('?>')
        
        if abiertas > cerradas:
            errores.append("Etiquetas PHP no balanceadas - faltan cierres '?>'")
        elif cerradas > abiertas:
            errores.append("Etiquetas PHP no balanceadas - faltan aperturas '<?php'")
        
        # Verificar paréntesis balanceados
        if contenido.count('(') != contenido.count(')'):
            errores.append("Paréntesis no balanceados")
        
        # Verificar llaves balanceadas
        if contenido.count('{') != contenido.count('}'):
            errores.append("Llaves no balanceadas")
        
        # Verificar corchetes balanceados
        if contenido.count('[') != contenido.count(']'):
            errores.append("Corchetes no balanceados")
        
        if errores:
            mensaje = "Posibles errores de sintaxis PHP:\n\n" + "\n".join(f"• {error}" for error in errores)
            messagebox.showerror("Validación PHP", mensaje)
        else:
            messagebox.showinfo("Validación PHP", "✅ Sintaxis PHP básica correcta")
    
    def procesar_error_sintaxis(self, error_output, lineas):
        """Procesa la salida de error para extraer información útil"""
        error_info = {
            'linea': 1,
            'mensaje': 'Error de sintaxis',
            'contexto': '',
            'tipo_error': 'SyntaxError'
        }
        
        # Patrones comunes de errores de sintaxis
        patterns = [
            r'File "[^"]+", line (\d+)',
            r'SyntaxError: (.+)',
            r'IndentationError: (.+)',
            r'NameError: (.+)'
        ]
        
        # Buscar número de línea
        for pattern in patterns:
            match = re.search(pattern, error_output)
            if match:
                if pattern.startswith('File'):
                    error_info['linea'] = int(match.group(1))
                else:
                    error_info['mensaje'] = match.group(1)
                    if 'Indentation' in error_output:
                        error_info['tipo_error'] = 'IndentationError'
                    elif 'NameError' in error_output:
                        error_info['tipo_error'] = 'NameError'
        
        # Obtener contexto alrededor de la línea con error
        linea_error = error_info['linea'] - 1
        inicio = max(0, linea_error - 2)
        fin = min(len(lineas), linea_error + 3)
        
        contexto = []
        for i in range(inicio, fin):
            prefix = ">>> " if i == linea_error else "    "
            contexto.append(f"{prefix}Línea {i+1}: {lineas[i]}")
        
        error_info['contexto'] = '\n'.join(contexto)
        
        return error_info
    
    def mostrar_error_detallado(self, error_info, lineas):
        """Muestra un diálogo con información detallada del error"""
        mensaje_detallado = f"""
{error_info['tipo_error']}: {error_info['mensaje']}

📝 **Contexto del error:**
{error_info['contexto']}

💡 **Sugerencias:**
- Revisa la línea resaltada con '>>>'
- Verifica paréntesis, comillas y corchetes
- Comprueba la indentación
- Revisa nombres de variables y funciones
"""
        
        # Crear ventana de error personalizada
        error_window = tk.Toplevel(self.root)
        error_window.title("Error de Sintaxis")
        error_window.geometry("600x400")
        error_window.configure(bg='#ffebee')
        
        # Frame principal
        main_frame = ttk.Frame(error_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono y título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, 
                text="❌ Error de Sintaxis Python",
                font=("Arial", 12, "bold"),
                fg="#d32f2f",
                bg='#ffebee').pack(anchor=tk.W)
        
        # Área de texto para el error
        error_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=("Courier New", 9),
            background="#fff3e0"
        )
        error_text.pack(fill=tk.BOTH, expand=True, pady=10)
        error_text.insert(1.0, mensaje_detallado)
        error_text.config(state=tk.DISABLED)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, 
                  text="🔍 Ir al Error", 
                  command=lambda: self.resaltar_linea(error_info['linea'])).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, 
                  text="❌ Cerrar", 
                  command=error_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.status_text.set(f"❌ Error en línea {error_info['linea']}")
    
    def resaltar_linea(self, numero_linea):
        """Resalta y lleva a la línea con error"""
        # Convertir línea a posición en el widget de texto
        pos_inicio = f"{numero_linea}.0"
        pos_fin = f"{numero_linea}.end"
        
        # Remover resaltado anterior
        self.text_area.tag_remove("error", "1.0", tk.END)
        
        # Aplicar resaltado
        self.text_area.tag_add("error", pos_inicio, pos_fin)
        self.text_area.tag_config("error", background="#ffcdd2", foreground="#000000")
        
        # Mover el cursor a la línea con error
        self.text_area.mark_set("insert", pos_inicio)
        self.text_area.see(pos_inicio)
        self.text_area.focus_set()
        self.actualizar_posicion_cursor()
    
    # ========== MÉTODOS DE BÚSQUEDA Y REEMPLAZO ==========
    
    def mostrar_busqueda(self):
        """Muestra el panel de búsqueda"""
        self.panel_busqueda.pack(fill=tk.X, pady=5)
        self.entry_buscar.focus_set()
    
    def mostrar_reemplazar(self):
        """Muestra el panel de búsqueda/reemplazo"""
        self.panel_busqueda.pack(fill=tk.X, pady=5)
        self.entry_buscar.focus_set()
    
    def ocultar_busqueda(self):
        """Oculta el panel de búsqueda"""
        self.panel_busqueda.pack_forget()
        self.text_area.focus_set()
    
    def buscar_siguiente(self):
        """Busca la siguiente ocurrencia del texto"""
        texto = self.entry_buscar.get()
        if not texto:
            return
        
        # Buscar desde la posición actual del cursor
        start_pos = self.text_area.index(tk.INSERT)
        pos = self.text_area.search(texto, start_pos, tk.END)
        
        if not pos:
            # Buscar desde el inicio si no se encuentra
            pos = self.text_area.search(texto, "1.0", tk.END)
        
        if pos:
            end_pos = f"{pos}+{len(texto)}c"
            self.text_area.tag_remove("sel", "1.0", tk.END)
            self.text_area.tag_add("sel", pos, end_pos)
            self.text_area.mark_set(tk.INSERT, pos)
            self.text_area.see(pos)
            self.actualizar_posicion_cursor()
        else:
            messagebox.showinfo("Buscar", f"Texto '{texto}' no encontrado")
    
    def buscar_todos(self):
        """Resalta todas las ocurrencias del texto"""
        texto = self.entry_buscar.get()
        if not texto:
            return
        
        self.text_area.tag_remove("busqueda", "1.0", tk.END)
        
        pos = "1.0"
        count = 0
        while True:
            pos = self.text_area.search(texto, pos, tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(texto)}c"
            self.text_area.tag_add("busqueda", pos, end_pos)
            pos = end_pos
            count += 1
        
        self.text_area.tag_config("busqueda", background="#fff9c4")
        self.status_text.set(f"Encontradas {count} ocurrencias de '{texto}'")
    
    def reemplazar(self):
        """Reemplaza la siguiente ocurrencia"""
        buscar = self.entry_buscar.get()
        reemplazar = self.entry_reemplazar.get()
        
        if not buscar:
            return
        
        # Buscar la selección actual
        try:
            sel_start, sel_end = self.text_area.tag_ranges("sel")
            selected_text = self.text_area.get(sel_start, sel_end)
            
            if selected_text == buscar:
                self.text_area.delete(sel_start, sel_end)
                self.text_area.insert(sel_start, reemplazar)
        except:
            # Si no hay selección, buscar siguiente
            self.buscar_siguiente()
            try:
                sel_start, sel_end = self.text_area.tag_ranges("sel")
                selected_text = self.text_area.get(sel_start, sel_end)
                
                if selected_text == buscar:
                    self.text_area.delete(sel_start, sel_end)
                    self.text_area.insert(sel_start, reemplazar)
            except:
                messagebox.showinfo("Reemplazar", "No se encontró texto para reemplazar")
    
    def reemplazar_todos(self):
        """Reemplaza todas las ocurrencias"""
        buscar = self.entry_buscar.get()
        reemplazar = self.entry_reemplazar.get()
        
        if not buscar:
            return
        
        contenido = self.text_area.get(1.0, tk.END)
        nuevo_contenido = contenido.replace(buscar, reemplazar)
        
        if contenido != nuevo_contenido:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, nuevo_contenido)
            self.status_text.set(f"Reemplazadas todas las ocurrencias de '{buscar}'")
        else:
            messagebox.showinfo("Reemplazar", f"No se encontró '{buscar}' para reemplazar")
    
    # ========== MÉTODOS DE ARCHIVO ==========
    
    def nuevo_archivo(self):
        """Crea un nuevo archivo"""
        if messagebox.askyesno("Nuevo", "¿Crear nuevo archivo? Se perderán los cambios no guardados."):
            self.text_area.delete(1.0, tk.END)
            self.contenido_original_actual = ""
            self.status_text.set("Nuevo archivo creado")
    
    def abrir_archivo(self):
        """Abre un archivo diferente"""
        file_path = filedialog.askopenfilename(
            title="Abrir archivo de configuración",
            filetypes=[("Python files", "*.py"), ("JavaScript files", "*.js"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            # Aquí podrías implementar la lógica para abrir archivos externos
            messagebox.showinfo("Abrir", f"Archivo seleccionado:\n{file_path}")
    
    def guardar_como(self):
        """Guarda el archivo con otro nombre"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("JavaScript files", "*.js"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                contenido = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                messagebox.showinfo("Guardar como", f"Archivo guardado como:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
    
    def deshacer(self):
        """Deshace la última acción"""
        try:
            self.text_area.edit_undo()
        except:
            pass
    
    def rehacer(self):
        """Rehace la última acción deshecha"""
        try:
            self.text_area.edit_redo()
        except:
            pass
    
    def crear_backup_actual(self):
        """Crea backup del archivo actual"""
        archivo_info = self.archivos_config[self.archivo_actual]
        
        try:
            if os.path.exists(archivo_info['ruta']):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{archivo_info['ruta']}.backup_{timestamp}"
                shutil.copy2(archivo_info['ruta'], backup_file)
                
                self.status_text.set(f"✅ Backup creado: {os.path.basename(backup_file)}")
                messagebox.showinfo("Backup", f"Backup creado:\n{backup_file}")
            else:
                messagebox.showerror("Error", "No existe el archivo para hacer backup")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear backup: {e}")
    
    def vista_previa_cambios(self):
        """Muestra una vista previa de los cambios realizados"""
        if not self.contenido_original_actual:
            messagebox.showinfo("Vista Previa", "No hay cambios para mostrar")
            return
        
        contenido_actual = self.text_area.get(1.0, tk.END)
        
        if contenido_actual == self.contenido_original_actual:
            messagebox.showinfo("Vista Previa", "No se han realizado cambios")
            return
        
        # Crear ventana de vista previa
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Vista Previa de Cambios")
        preview_window.geometry("900x600")
        
        # Frame principal
        main_frame = ttk.Frame(preview_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Vista Previa de Cambios", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Área de texto para diff
        diff_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            font=("Courier New", 9)
        )
        diff_text.pack(fill=tk.BOTH, expand=True)
        
        # Generar diff
        diff = difflib.unified_diff(
            self.contenido_original_actual.splitlines(keepends=True),
            contenido_actual.splitlines(keepends=True),
            fromfile='Original',
            tofile='Modificado',
            n=3
        )
        
        diff_content = ''.join(diff)
        
        if not diff_content:
            diff_text.insert(1.0, "No hay cambios significativos")
        else:
            diff_text.insert(1.0, diff_content)
        
        diff_text.config(state=tk.DISABLED)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Cerrar", 
                  command=preview_window.destroy).pack(side=tk.RIGHT)
    
    def salir(self):
        """Sale de la aplicación"""
        if self.hay_cambios_sin_guardar():
            respuesta = messagebox.askyesnocancel(
                "Salir", 
                "Tienes cambios sin guardar. ¿Quieres guardarlos antes de salir?",
                icon=messagebox.WARNING
            )
            
            if respuesta is None:
                return
            elif respuesta:
                self.guardar_archivo_actual()
        
        self.root.quit()
    
    # ========== MÉTODOS DE BASE DE DATOS ==========
    
    def cargar_config_bd_desde_archivo(self):
        """Carga la configuración de BD desde Parametros_FV.py"""
        try:
            archivo_info = self.archivos_config['Parametros_FV.py']
            if os.path.exists(archivo_info['ruta']):
                with open(archivo_info['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Buscar patrones en el archivo
                patrones = {
                    'servidor': r'servidor\s*=\s*["\']([^"\']+)["\']',
                    'usuario': r'usuario\s*=\s*["\']([^"\']+)["\']',
                    'clave': r'clave\s*=\s*["\']([^"\']+)["\']',
                    'basedatos': r'basedatos\s*=\s*["\']([^"\']+)["\']'
                }
                
                for clave, patron in patrones.items():
                    match = re.search(patron, contenido)
                    if match:
                        self.config_bd[clave] = match.group(1)
                        
        except Exception as e:
            print(f"Advertencia: No se pudo cargar configuración BD: {e}")
    
    def conectar_bd(self):
        """Intenta conectar a la base de datos"""
        try:
            conexion = MySQLdb.connect(
                host=self.config_bd['servidor'],
                user=self.config_bd['usuario'],
                passwd=self.config_bd['clave'],
                db=self.config_bd['basedatos']
            )
            return conexion
        except Exception as e:
            raise Exception(f"Error conectando a BD: {e}")
    
    def ver_tabla_equipos(self):
        """Muestra los registros de la tabla equipos"""
        try:
            conexion = self.conectar_bd()
            cursor = conexion.cursor()
            
            # Obtener registros de la tabla equipos
            cursor.execute("SELECT id_equipo, tiempo, sensores FROM equipos ORDER BY tiempo DESC LIMIT 100")
            registros = cursor.fetchall()
            
            # Crear ventana de visualización
            self.crear_ventana_tabla_equipos(registros)
            
            cursor.close()
            conexion.close()
            
        except Exception as e:
            messagebox.showerror("Error BD", f"No se pudo acceder a la tabla equipos:\n{e}")
    
    def crear_ventana_tabla_equipos(self, registros):
        """Crea una ventana para mostrar la tabla equipos"""
        ventana = tk.Toplevel(self.root)
        ventana.title("PVControl+ - Tabla 'equipos'")
        ventana.geometry("1200x700")
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(titulo_frame, 
                text=f"Tabla 'equipos' - {len(registros)} registros encontrados",
                font=("Arial", 12, "bold")).pack()
        
        # Frame para controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controles_frame, text="🔄 Actualizar", 
                  command=self.ver_tabla_equipos).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="📊 Estadísticas", 
                  command=lambda: self.mostrar_estadisticas(registros)).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="💾 Exportar CSV", 
                  command=lambda: self.exportar_csv(registros)).pack(side=tk.LEFT, padx=5)
        ttk.Button(controles_frame, text="❌ Cerrar", 
                  command=ventana.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para mostrar datos en tabla
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        tree = ttk.Treeview(tree_frame, 
                           columns=('ID', 'Tiempo', 'Sensores'),
                           show='headings',
                           yscrollcommand=v_scrollbar.set,
                           xscrollcommand=h_scrollbar.set)
        
        tree.heading('ID', text='ID Equipo')
        tree.heading('Tiempo', text='Fecha/Hora')
        tree.heading('Sensores', text='Datos Sensores')
        
        tree.column('ID', width=150)
        tree.column('Tiempo', width=150)
        tree.column('Sensores', width=800)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)
        
        # Insertar datos
        for registro in registros:
            id_equipo, tiempo, sensores = registro
            
            # Formatear tiempo
            if tiempo:
                tiempo_str = tiempo.strftime("%Y-%m-%d %H:%M:%S")
            else:
                tiempo_str = "N/A"
            
            # Acortar sensores si es muy largo
            if sensores and len(sensores) > 100:
                sensores_str = sensores[:100] + "..."
            else:
                sensores_str = sensores or "Sin datos"
            
            tree.insert('', tk.END, values=(id_equipo, tiempo_str, sensores_str))
        
        # Doble click para ver detalles
        tree.bind('<Double-1>', lambda e: self.mostrar_detalles_registro(tree, registros))
    
    def mostrar_detalles_registro(self, tree, registros):
        """Muestra los detalles completos de un registro"""
        seleccion = tree.selection()
        if not seleccion:
            return
        
        item = seleccion[0]
        valores = tree.item(item, 'values')
        indice = tree.index(item)
        
        if indice < len(registros):
            id_equipo, tiempo, sensores = registros[indice]
            
            # Crear ventana de detalles
            detalle_ventana = tk.Toplevel(self.root)
            detalle_ventana.title(f"Detalles - {id_equipo}")
            detalle_ventana.geometry("800x600")
            
            main_frame = ttk.Frame(detalle_ventana, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Información básica
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(info_frame, text=f"ID Equipo: {id_equipo}", 
                    font=("Arial", 11, "bold")).pack(anchor=tk.W)
            
            if tiempo:
                tk.Label(info_frame, text=f"Fecha/Hora: {tiempo}", 
                        font=("Arial", 10)).pack(anchor=tk.W)
            
            # Sensores en formato JSON si es posible
            sensores_frame = ttk.Frame(main_frame)
            sensores_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(sensores_frame, text="Datos de Sensores:", 
                    font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            sensores_text = scrolledtext.ScrolledText(
                sensores_frame,
                wrap=tk.WORD,
                width=80,
                height=20,
                font=("Courier New", 9)
            )
            sensores_text.pack(fill=tk.BOTH, expand=True)
            
            if sensores:
                try:
                    # Intentar formatear como JSON
                    datos_json = json.loads(sensores)
                    sensores_formateados = json.dumps(datos_json, indent=2, ensure_ascii=False)
                    sensores_text.insert(1.0, sensores_formateados)
                except:
                    # Si no es JSON, mostrar tal cual
                    sensores_text.insert(1.0, sensores)
            else:
                sensores_text.insert(1.0, "Sin datos de sensores")
            
            sensores_text.config(state=tk.DISABLED)
    
    def mostrar_estadisticas(self, registros):
        """Muestra estadísticas de la tabla equipos"""
        if not registros:
            messagebox.showinfo("Estadísticas", "No hay registros para analizar")
            return
        
        # Calcular estadísticas
        equipos_unicos = set(reg[0] for reg in registros)
        fechas = [reg[1] for reg in registros if reg[1]]
        
        estadisticas = f"""
📊 ESTADÍSTICAS TABLA 'equipos'

• Total de registros: {len(registros)}
• Equipos únicos: {len(equipos_unicos)}
• Lista de equipos: {', '.join(sorted(equipos_unicos))}

📅 Rango temporal:
{min(fechas) if fechas else 'N/A'} - {max(fechas) if fechas else 'N/A'}

Últimos 5 equipos:
"""
        
        for i, equipo in enumerate(sorted(equipos_unicos)[:5]):
            estadisticas += f"  {i+1}. {equipo}\n"
        
        messagebox.showinfo("Estadísticas", estadisticas)
    
    def exportar_csv(self, registros):
        """Exporta los registros a CSV"""
        try:
            filename = f"equipos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ID_EQUIPO;TIEMPO;SENSORES\n")
                for registro in registros:
                    id_equipo, tiempo, sensores = registro
                    tiempo_str = tiempo.strftime("%Y-%m-%d %H:%M:%S") if tiempo else ""
                    # Escapar comillas en sensores
                    sensores_esc = str(sensores).replace('"', '""') if sensores else ""
                    f.write(f'"{id_equipo}";"{tiempo_str}";"{sensores_esc}"\n')
            
            messagebox.showinfo("Exportar", f"Datos exportados a:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
    
    def probar_conexion_bd(self):
        """Prueba la conexión a la base de datos"""
        try:
            conexion = self.conectar_bd()
            cursor = conexion.cursor()
            
            # Obtener información de la BD
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM equipos")
            total_registros = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT id_equipo) FROM equipos")
            equipos_unicos = cursor.fetchone()[0]
            
            cursor.close()
            conexion.close()
            
            info = f"""
✅ CONEXIÓN EXITOSA

• Servidor: {self.config_bd['servidor']}
• Base de datos: {self.config_bd['basedatos']}
• Versión MySQL: {version}
• Registros en 'equipos': {total_registros}
• Equipos únicos: {equipos_unicos}
"""
            messagebox.showinfo("Prueba de Conexión", info)
            
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la BD:\n{e}")
    
    def configurar_conexion_bd(self):
        """Permite configurar los parámetros de conexión a BD"""
        messagebox.showinfo("Configuración BD", 
                          f"Configuración actual:\n"
                          f"Servidor: {self.config_bd['servidor']}\n"
                          f"Usuario: {self.config_bd['usuario']}\n"
                          f"Base de datos: {self.config_bd['basedatos']}\n\n"
                          f"Para modificar, edita los valores en Parametros_FV.py")
    
    def ejecutar(self):
        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

if __name__ == "__main__":
    print("Iniciando Editor Multi-Archivo PVControl+...")
    app = EditorConfigProfesional()
    app.ejecutar()