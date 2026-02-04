# cargar_parametros.py - Módulo de Carga de Parámetros

## Descripción

El módulo `cargar_parametros.py` proporciona una interfaz unificada para cargar parámetros de configuración del sistema PVControl+. Permite fusionar configuraciones de dos archivos:

1. **Parametros_FV_DIST.py**: Archivo de distribución con valores por defecto
2. **Parametros_FV.py**: Archivo de usuario (opcional) con personalizaciones

El archivo de usuario tiene **prioridad** sobre el de distribución, permitiendo sobreescribir valores específicos sin modificar el archivo original.

## Ubicación de Archivos

Por defecto, el módulo busca los archivos de parámetros en:
- `/home/pi/PVControl+/Parametros_FV_DIST.py` (obligatorio)
- `/home/pi/PVControl+/Parametros_FV.py` (opcional)

## Uso

### Importar el Módulo

```python
from cargar_parametros import cargar_parametros
```

### Cargar un Solo Parámetro

```python
servidor = cargar_parametros('servidor')
# servidor = "localhost"
```

### Cargar Múltiples Parámetros

```python
servidor, usuario, clave = cargar_parametros('servidor', 'usuario', 'clave')
# servidor = "localhost"
# usuario = "rpi"
# clave = "fv"
```

### Parámetro No Existente

Si se solicita un parámetro que no existe en ninguno de los archivos, se devuelve `None`:

```python
param = cargar_parametros('parametro_inexistente')
# param = None
```

## Comportamiento

1. **Carga DIST primero**: Se leen todos los parámetros del archivo de distribución
2. **Carga USER (si existe)**: Se leen los parámetros del archivo de usuario
3. **Fusión con prioridad USER**: Los valores del archivo de usuario sobreescriben los del archivo de distribución
4. **Retorno selectivo**: Solo se devuelven las variables solicitadas

### Tipos de Retorno

- **Un parámetro**: Devuelve el valor directamente (cualquier tipo: str, int, dict, etc.)
- **Múltiples parámetros**: Devuelve una tupla con los valores en el mismo orden solicitado
- **Parámetro inexistente**: Devuelve `None`

## Ejemplo Práctico

### Archivo Parametros_FV_DIST.py

```python
servidor = "localhost"
usuario = "rpi"
clave = "fv"
basedatos = "control_solar"
puerto = 3306
simular = 0
```

### Archivo Parametros_FV.py (personalización del usuario)

```python
usuario = "rpi_custom"
clave = "mi_clave_segura"
simular = 1
```

### Código de Uso

```python
from cargar_parametros import cargar_parametros

# Cargar configuración de base de datos
servidor, usuario, clave, basedatos = cargar_parametros(
    'servidor', 'usuario', 'clave', 'basedatos'
)

# Resultado:
# servidor = "localhost"         # De DIST
# usuario = "rpi_custom"          # De USER (sobreescrito)
# clave = "mi_clave_segura"       # De USER (sobreescrito)
# basedatos = "control_solar"     # De DIST

# Cargar parámetro individual
simular = cargar_parametros('simular')
# simular = 1  # De USER (sobreescrito)

# Cargar parámetro que solo existe en DIST
puerto = cargar_parametros('puerto')
# puerto = 3306  # De DIST
```

## Ventajas

1. **Separación de configuración**: Los usuarios pueden personalizar sin modificar el archivo de distribución
2. **Actualizaciones simples**: Las actualizaciones del sistema solo tocan Parametros_FV_DIST.py
3. **Carga dinámica**: Los archivos se cargan en tiempo de ejecución
4. **Seguridad**: El archivo Parametros_FV.py está en .gitignore (credenciales privadas)
5. **Flexibilidad**: Soporta cualquier tipo de variable Python (strings, números, diccionarios, listas, etc.)

## Testing

El módulo incluye un suite completo de tests en `TEST/test_cargar_parametros.py` que verifica:

- Carga de parámetros individuales
- Carga de múltiples parámetros
- Prioridad USER sobre DIST
- Manejo de parámetros inexistentes
- Funcionamiento sin archivo USER (opcional)
- Soporte de variables de diferentes tipos

### Ejecutar Tests

```bash
cd /home/pi/PVControl+
python3 TEST/test_cargar_parametros.py
```

O directamente:

```bash
./TEST/test_cargar_parametros.py
```

## Notas Técnicas

- Utiliza `importlib.util` para carga dinámica de módulos
- El archivo USER es completamente opcional
- No lanza excepciones si USER no existe
- Lanza `FileNotFoundError` si DIST no existe
- Los parámetros se extraen usando `vars()` del módulo cargado
