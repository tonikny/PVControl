<?php
header('Content-Type: application/json');

$data = json_decode(file_get_contents('php://input'), true);
$path = $data['path'] ?? '';
$file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';

try {
    $filePath = '/home/pi/PVControl+/' . $file;
    
    if (!file_exists($filePath)) {
        throw new Exception("Archivo no encontrado: $filePath");
    }
    
    // Leer el contenido completo del archivo
    $content = file_get_contents($filePath);
    
    if ($path === 'CONFIG') {
        // Para CONFIG, devolver el archivo completo
        $rawContent = $content;
    } else {
        // Para subsecciones, extraer la sección específica
        $rawContent = extractRawSection($content, $path);
    }
    
    echo json_encode([
        'success' => true,
        'content' => $rawContent
    ]);
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}

function extractRawSection($content, $path) {
    $parts = explode('.', $path);
    array_shift($parts); // Remover 'CONFIG'
    
    if (empty($parts)) {
        return $content;
    }
    
    $targetKey = end($parts);
    $lines = explode("\n", $content);
    $inConfig = false;
    $inTargetSection = false;
    $sectionContent = '';
    $found = false;
    $indentLevel = 0;
    $targetIndent = 0;
    
    foreach ($lines as $line) {
        $trimmed = trim($line);
        
        // Detectar cuando estamos en CONFIG
        if (strpos($trimmed, 'CONFIG = {') === 0) {
            $inConfig = true;
            continue;
        }
        
        if ($inConfig && $trimmed === '}') {
            $inConfig = false;
            continue;
        }
        
        if ($inConfig && !$found) {
            // Buscar la clave objetivo
            if (preg_match("/^['\"]" . preg_quote($targetKey, '/') . "['\"]\s*:/", $trimmed)) {
                $inTargetSection = true;
                $found = true;
                $sectionContent = $line;
                
                // Calcular el nivel de indentación de la clave objetivo
                $indentLevel = strlen($line) - strlen(ltrim($line));
                $targetIndent = $indentLevel;
                continue;
            }
        }
        
        if ($inTargetSection) {
            // Calcular indentación actual
            $currentIndent = strlen($line) - strlen(ltrim($line));
            
            // Si encontramos una línea con igual o menor indentación que la clave objetivo
            // Y no es la línea actual de la clave, podría ser el final
            if ($currentIndent <= $targetIndent && $line !== $sectionContent) {
                // Verificar si es otra clave al mismo nivel
                if (preg_match("/^['\"]([^'\"]+)['\"]\s*:/", $trimmed)) {
                    break;
                }
                
                // Verificar si es el cierre del nivel padre
                if ($trimmed === '}' || $trimmed === '},') {
                    // Agregar esta línea y terminar
                    $sectionContent .= "\n" . $line;
                    break;
                }
            }
            
            // Agregar la línea al contenido
            $sectionContent .= "\n" . $line;
            
            // Si encontramos el cierre de CONFIG, terminar
            if ($trimmed === '}') {
                break;
            }
        }
    }
    
    if (!$found) {
        return "# Sección '$path' no encontrada en el archivo\n\n" .
               "# Buscando clave: '$targetKey'\n" .
               "# Path completo: $path\n" .
               "# Contenido CONFIG disponible:\n" .
               extractConfigKeys($content);
    }
    
    return $sectionContent;
}

function extractConfigKeys($content) {
    $lines = explode("\n", $content);
    $inConfig = false;
    $keys = [];
    
    foreach ($lines as $line) {
        $trimmed = trim($line);
        
        if (strpos($trimmed, 'CONFIG = {') === 0) {
            $inConfig = true;
            continue;
        }
        
        if ($inConfig && $trimmed === '}') {
            break;
        }
        
        if ($inConfig) {
            if (preg_match("/^['\"]([^'\"]+)['\"]\s*:/", $trimmed, $matches)) {
                $keys[] = "  - " . $matches[1];
            }
        }
    }
    
    return implode("\n", $keys);
}
?>