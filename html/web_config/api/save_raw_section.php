<?php
header('Content-Type: application/json');

$data = json_decode(file_get_contents('php://input'), true);
$path = $data['path'] ?? '';
$content = $data['content'] ?? '';
$file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';

try {
    $filePath = '/home/pi/PVControl+/' . $file;
    
    if (!file_exists($filePath)) {
        throw new Exception("Archivo no encontrado: $filePath");
    }
    
    // Leer el contenido actual del archivo
    $currentContent = file_get_contents($filePath);
    
    // Hacer backup del archivo original
    $backupPath = $filePath . '.backup_' . date('Y-m-d_H-i-s');
    copy($filePath, $backupPath);
    
    if ($path === 'CONFIG') {
        // Para CONFIG, el contenido ya debe ser el archivo completo
        $newContent = $content;
    } else {
        // Para subsecciones, necesitamos reemplazar solo esa sección
        $newContent = replaceConfigSection($currentContent, $path, $content);
    }
    
    // Guardar el nuevo contenido
    if (file_put_contents($filePath, $newContent) !== false) {
        echo json_encode([
            'success' => true,
            'message' => 'Configuración guardada correctamente',
            'backup' => $backupPath
        ]);
    } else {
        throw new Exception("Error al guardar el archivo");
    }
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}

function replaceConfigSection($pythonContent, $path, $newContent) {
    $parts = explode('.', $path);
    array_shift($parts); // Remover 'CONFIG'
    
    if (empty($parts)) {
        return $pythonContent;
    }
    
    $targetKey = end($parts);
    $lines = explode("\n", $pythonContent);
    $newLines = [];
    $inTargetSection = false;
    $sectionReplaced = false;
    $currentDepth = 0;
    $targetDepth = 0;
    $inConfig = false;
    
    foreach ($lines as $line) {
        $trimmed = trim($line);
        
        // Detectar cuando estamos en CONFIG
        if (strpos($trimmed, 'CONFIG = {') === 0) {
            $inConfig = true;
            $newLines[] = $line;
            continue;
        }
        
        if ($inConfig && $trimmed === '}') {
            $inConfig = false;
            $newLines[] = $line;
            continue;
        }
        
        if (!$sectionReplaced && $inConfig) {
            // Buscar la clave objetivo
            if (preg_match("/^['\"]" . preg_quote($targetKey, '/') . "['\"]\s*:/", $trimmed)) {
                $inTargetSection = true;
                $sectionReplaced = true;
                
                // Agregar la nueva sección
                $newLines[] = "    '" . $targetKey . "': " . $newContent;
                
                // Saltar las líneas originales de esta sección
                $currentDepth = substr_count($line, '{') + substr_count($line, '[');
                $currentDepth -= substr_count($line, '}') + substr_count($line, ']');
                $targetDepth = $currentDepth;
                continue;
            }
        }
        
        if ($inTargetSection) {
            // Continuar saltando líneas hasta que termine la sección original
            $currentDepth += substr_count($line, '{') + substr_count($line, '[');
            $currentDepth -= substr_count($line, '}') + substr_count($line, ']');
            
            if ($currentDepth <= $targetDepth && $trimmed !== '') {
                $inTargetSection = false;
                // No agregar esta línea (ya fue reemplazada)
                continue;
            }
        } else {
            // Agregar línea normal
            $newLines[] = $line;
        }
    }
    
    // Si no se encontró la sección, agregarla al final de CONFIG
    if (!$sectionReplaced && $inConfig) {
        // Encontrar la última línea antes del cierre de CONFIG
        $lastConfigLine = count($newLines) - 1;
        while ($lastConfigLine >= 0 && trim($newLines[$lastConfigLine]) !== '}') {
            $lastConfigLine--;
        }
        
        if ($lastConfigLine >= 0) {
            // Insertar antes del cierre
            array_splice($newLines, $lastConfigLine, 0, "    '" . $targetKey . "': " . $newContent);
        }
    }
    
    return implode("\n", $newLines);
}
?>