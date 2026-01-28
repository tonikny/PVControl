<?php
// api/save_config.php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $file = $data['file'] ?? 'Parametros_FV.py';
    $config = $data['config'] ?? [];
    
    try {
        $filePath = '/home/pi/PVControl+/' . $file;
        
        // Crear backup
        if (file_exists($filePath)) {
            $backupPath = '/home/pi/PVControl+/backups/' . $file . '.' . date('Y-m-d-His');
            copy($filePath, $backupPath);
        }
        
        // Generar contenido del archivo con solo el diccionario CONFIG
        $content = generate_config_file($config);
        
        // Guardar archivo
        if (file_put_contents($filePath, $content) === false) {
            throw new Exception("Error guardando el archivo");
        }
        
        echo json_encode([
            'success' => true,
            'message' => 'Configuración guardada correctamente'
        ]);
        
    } catch (Exception $e) {
        echo json_encode([
            'success' => false,
            'error' => $e->getMessage()
        ]);
    }
}

function generate_config_file($config) {
    $header = "# ------------------------------------------------------------------\n";
    $header .= "# PARAMETROS INSTALACION PVControl+ - Generado desde interfaz web\n";
    $header .= "# ------------------------------------------------------------------\n\n";
    
    // Convertir array PHP a string Python
    $config_str = php_to_python_dict($config);
    
    return $header . "CONFIG = " . $config_str . "\n";
}

function php_to_python_dict($data, $indent = 0) {
    $spaces = str_repeat('    ', $indent);
    
    if (is_array($data)) {
        if (empty($data)) {
            return '{}';
        }
        
        $is_assoc = array_keys($data) !== range(0, count($data) - 1);
        
        if ($is_assoc) {
            $items = [];
            foreach ($data as $key => $value) {
                $items[] = $spaces . "    '" . $key . "': " . php_to_python_dict($value, $indent + 1);
            }
            return "{\n" . implode(",\n", $items) . "\n" . $spaces . "}";
        } else {
            $items = [];
            foreach ($data as $value) {
                $items[] = php_to_python_dict($value, $indent);
            }
            return "[" . implode(", ", $items) . "]";
        }
    } elseif (is_bool($data)) {
        return $data ? 'True' : 'False';
    } elseif (is_null($data)) {
        return 'None';
    } elseif (is_numeric($data)) {
        return $data;
    } else {
        return "'" . addslashes($data) . "'";
    }
}
?>