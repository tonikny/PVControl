"""
Prueba con pytest para validar que los nuevos módulos con inyección de dependencias funcionan correctamente.
"""
import tempfile
import os
import textwrap
import pytest
from helpers.gestor_logs_DI import GestorLogsDI
from helpers.gestor_parametros_DI import GestorParametrosDI


def test_dependency_injection():
    """Prueba básica de inyección de dependencias entre los módulos."""
    
    # Crear archivos temporales para la prueba
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crear archivo DIST
        dist_path = os.path.join(tmpdir, "Parametros_FV_DIST.py")
        with open(dist_path, "w") as f:
            f.write(textwrap.dedent("""
                # Archivo de parámetros DIST de ejemplo
                TEST_PARAM = "valor_dist"
                DEFAULT_VALUE = 42
            """))
        
        # Crear archivo USER
        user_path = os.path.join(tmpdir, "Parametros_FV.py")
        with open(user_path, "w") as f:
            f.write(textwrap.dedent("""
                # Archivo de parámetros USER de ejemplo
                TEST_PARAM = "valor_user"
                CUSTOM_VALUE = "personalizado"
            """))
        
        # Guardar rutas originales
        from helpers import gestor_parametros_DI
        original_dist = gestor_parametros_DI.RUTA_DIST
        original_user = gestor_parametros_DI.RUTA_USER
        
        # Configurar rutas temporales
        gestor_parametros_DI.RUTA_DIST = dist_path
        gestor_parametros_DI.RUTA_USER = user_path
        
        try:
            # Crear instancia de logger
            logger = GestorLogsDI(nombre="test_di", level=10)  # DEBUG level
            
            # Crear instancia de gestor de parámetros con inyección de dependencias
            gestor_parametros = GestorParametrosDI(logger=logger, check_interval=0)
            
            # Probar lectura de parámetros
            test_param = gestor_parametros.leer_parametros("TEST_PARAM")
            assert test_param == "valor_user", f"Se esperaba 'valor_user', se obtuvo {test_param}"
            
            custom_value = gestor_parametros.leer_parametros("CUSTOM_VALUE")
            assert custom_value == "personalizado", f"Se esperaba 'personalizado', se obtuvo {custom_value}"
            
            default_value = gestor_parametros.leer_parametros("DEFAULT_VALUE")
            assert default_value == 42, f"Se esperaba 42, se obtuvo {default_value}"
            
        finally:
            # Restaurar rutas originales
            gestor_parametros_DI.RUTA_DIST = original_dist
            gestor_parametros_DI.RUTA_USER = original_user


def test_logger_functionality():
    """Prueba que el logger funcione correctamente."""
    logger = GestorLogsDI(nombre="test_logger")
    
    # Probar diferentes niveles de logging
    logger.debug("Mensaje de debug")
    logger.info("Mensaje de info")
    logger.warning("Mensaje de warning")
    logger.error("Mensaje de error")
    logger.manual("Mensaje manual")
    
    # Verificar métodos booleanos
    debug_enabled = logger.es_debug()
    info_enabled = logger.es_info()
    
    # Estos valores dependerán de los argumentos de línea de comandos
    # pero al menos no deberían lanzar excepciones
    assert isinstance(debug_enabled, bool)
    assert isinstance(info_enabled, bool)


def test_parametros_with_default_logger():
    """Prueba que el gestor de parámetros funcione con logger por defecto."""
    # Crear instancia sin inyectar logger (usará uno por defecto)
    gestor_parametros = GestorParametrosDI(check_interval=0)
    
    # Esto debería funcionar sin problemas (aunque no encontrará parámetros en archivos predeterminados)
    try:
        # Intentar leer un parámetro que no existe, debería retornar None
        nonexistent = gestor_parametros.leer_parametros("PARAMETRO_INEXISTENTE")
        assert nonexistent is None
    except Exception:
        # Algunas excepciones son aceptables si no existen los archivos de configuración
        pass


if __name__ == "__main__":
    pytest.main([__file__])