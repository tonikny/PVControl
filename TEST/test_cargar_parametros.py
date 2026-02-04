#!/usr/bin/env python3
"""
Test script para verificar la funcionalidad de cargar_parametros.py
Este script usa archivos temporales en lugar de las rutas fijas de producción.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio raíz al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent))

import cargar_parametros


def crear_archivos_test(temp_dir):
    """Crea archivos de parámetros de prueba en un directorio temporal"""
    
    # Contenido del archivo DIST (por defecto)
    contenido_dist = """
# Archivo de distribución con parámetros por defecto
servidor = "localhost"
usuario = "rpi_dist"
clave = "fv_dist"
basedatos = "control_solar"
puerto = 3306

# Variable que solo existe en DIST
variable_dist_only = "valor_solo_en_dist"

# Variable que será sobreescrita
variable_sobreescrita = "valor_original_dist"

# Variables numéricas
simular = 0
simular_reles = 0
t_muestra_max = 6
"""
    
    # Contenido del archivo USER (personalizado por usuario)
    contenido_user = """
# Archivo de usuario con parámetros personalizados
usuario = "rpi_custom"
clave = "fv_custom"

# Sobreescribir variable
variable_sobreescrita = "valor_custom_user"

# Variable que solo existe en USER
variable_user_only = "valor_solo_en_user"

# Sobreescribir variable numérica
simular = 1
"""
    
    # Crear archivos
    dist_path = Path(temp_dir) / "Parametros_FV_DIST.py"
    user_path = Path(temp_dir) / "Parametros_FV.py"
    
    dist_path.write_text(contenido_dist)
    user_path.write_text(contenido_user)
    
    return str(dist_path), str(user_path)


def test_cargar_parametros():
    """Ejecuta las pruebas del módulo cargar_parametros"""
    
    print("=" * 70)
    print("TEST: Verificación de cargar_parametros.py")
    print("=" * 70)
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="pvcontrol_test_")
    print(f"\n[INFO] Directorio temporal creado: {temp_dir}")
    
    try:
        # Crear archivos de prueba
        dist_path, user_path = crear_archivos_test(temp_dir)
        print(f"[INFO] Archivo DIST creado: {dist_path}")
        print(f"[INFO] Archivo USER creado: {user_path}")
        
        # Modificar las rutas del módulo para usar archivos temporales
        cargar_parametros.RUTA_DIST = dist_path
        cargar_parametros.RUTA_USER = user_path
        
        print("\n" + "-" * 70)
        print("TEST 1: Cargar un solo parámetro que existe en DIST")
        print("-" * 70)
        servidor = cargar_parametros.cargar_parametros('servidor')
        print(f"Resultado: servidor = '{servidor}'")
        assert servidor == "localhost", f"Error: esperado 'localhost', obtenido '{servidor}'"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 2: Cargar parámetro que existe en ambos (USER debe prevalecer)")
        print("-" * 70)
        usuario = cargar_parametros.cargar_parametros('usuario')
        print(f"Resultado: usuario = '{usuario}'")
        assert usuario == "rpi_custom", f"Error: esperado 'rpi_custom', obtenido '{usuario}'"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 3: Cargar múltiples parámetros (debe devolver tupla)")
        print("-" * 70)
        servidor, usuario, clave = cargar_parametros.cargar_parametros('servidor', 'usuario', 'clave')
        print(f"Resultado: servidor='{servidor}', usuario='{usuario}', clave='{clave}'")
        assert servidor == "localhost", f"Error en servidor"
        assert usuario == "rpi_custom", f"Error en usuario"
        assert clave == "fv_custom", f"Error en clave"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 4: Cargar variable que solo existe en DIST")
        print("-" * 70)
        var_dist = cargar_parametros.cargar_parametros('variable_dist_only')
        print(f"Resultado: variable_dist_only = '{var_dist}'")
        assert var_dist == "valor_solo_en_dist", f"Error: valor incorrecto"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 5: Cargar variable que solo existe en USER")
        print("-" * 70)
        var_user = cargar_parametros.cargar_parametros('variable_user_only')
        print(f"Resultado: variable_user_only = '{var_user}'")
        assert var_user == "valor_solo_en_user", f"Error: valor incorrecto"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 6: Verificar sobreescritura de variable")
        print("-" * 70)
        var_sobre = cargar_parametros.cargar_parametros('variable_sobreescrita')
        print(f"Resultado: variable_sobreescrita = '{var_sobre}'")
        assert var_sobre == "valor_custom_user", f"Error: USER no sobreescribió DIST"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 7: Cargar variable que no existe (debe devolver None)")
        print("-" * 70)
        var_none = cargar_parametros.cargar_parametros('variable_inexistente')
        print(f"Resultado: variable_inexistente = {var_none}")
        assert var_none is None, f"Error: esperado None, obtenido {var_none}"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 8: Verificar variables numéricas")
        print("-" * 70)
        simular, simular_reles, t_muestra = cargar_parametros.cargar_parametros(
            'simular', 'simular_reles', 't_muestra_max'
        )
        print(f"Resultado: simular={simular}, simular_reles={simular_reles}, t_muestra_max={t_muestra}")
        assert simular == 1, f"Error: USER no sobreescribió simular"
        assert simular_reles == 0, f"Error: simular_reles incorrecto"
        assert t_muestra == 6, f"Error: t_muestra_max incorrecto"
        print("✓ PASADO")
        
        print("\n" + "-" * 70)
        print("TEST 9: Funcionamiento sin archivo USER (solo DIST)")
        print("-" * 70)
        # Eliminar archivo USER
        os.remove(user_path)
        print(f"[INFO] Archivo USER eliminado: {user_path}")
        
        # Cargar variable que estaba en USER (ahora debe tomar valor de DIST)
        var_sobre = cargar_parametros.cargar_parametros('variable_sobreescrita')
        print(f"Resultado: variable_sobreescrita = '{var_sobre}'")
        assert var_sobre == "valor_original_dist", f"Error: debería usar valor de DIST"
        
        usuario = cargar_parametros.cargar_parametros('usuario')
        print(f"Resultado: usuario = '{usuario}'")
        assert usuario == "rpi_dist", f"Error: debería usar valor de DIST"
        print("✓ PASADO")
        
        print("\n" + "=" * 70)
        print("✓✓✓ TODOS LOS TESTS PASARON CORRECTAMENTE ✓✓✓")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗✗✗ ERROR EN TEST ✗✗✗")
        print(f"Excepción: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Limpiar directorio temporal
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n[INFO] Directorio temporal eliminado: {temp_dir}")
    
    return True


if __name__ == "__main__":
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     TEST SUITE: cargar_parametros.py                             ║")
    print("║     PVControl+ - Sistema de Control Fotovoltaico                 ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    resultado = test_cargar_parametros()
    
    print("\n")
    sys.exit(0 if resultado else 1)
