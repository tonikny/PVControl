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
    
    // Extraer la sección específica basada en la ruta
    $rawContent = extractSectionFromPython($content, $path);
    
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

function extractSectionFromPython($content, $path) {
    $parts = explode('.', $path);
    array_shift($parts); // Remover 'CONFIG'
    
    if (empty($parts)) {
        return $content;
    }
    
    // Buscar la sección en el contenido Python
    $pattern = '/CONFIG\s*=\s*\{([^}]+)\}/s';
    preg_match($pattern, $content, $matches);
    
    if (empty($matches)) {
        return '// No se pudo extraer la sección';
    }
    
    $configContent = $matches[1];
    
    // Implementar lógica para extraer la subsección específica
    // Esto es un ejemplo básico - necesitarías adaptarlo a tu estructura real
    $currentLevel = $configContent;
    foreach ($parts as $part) {
        $pattern = "/'$part'\s*:\s*([^,]+)/";
        preg_match($pattern, $currentLevel, $matches);
        
        if (empty($matches)) {
            return '// Sección no encontrada';
        }
        
        $currentLevel = $matches[1];
    }
    
    return trim($currentLevel);
}
?>