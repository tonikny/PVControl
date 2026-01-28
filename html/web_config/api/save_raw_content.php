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
    
    // Leer el contenido actual
    $currentContent = file_get_contents($filePath);
    
    // Actualizar la sección específica
    $newContent = updateSectionInPython($currentContent, $path, $content);
    
    // Guardar el archivo
    if (file_put_contents($filePath, $newContent) !== false) {
        echo json_encode([
            'success' => true,
            'message' => 'Contenido guardado correctamente'
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

function updateSectionInPython($content, $path, $newContent) {
    $parts = explode('.', $path);
    array_shift($parts); // Remover 'CONFIG'
    
    if (empty($parts)) {
        return $newContent;
    }
    
    // Implementar lógica para actualizar la sección específica
    // Esto es un ejemplo básico - necesitarías adaptarlo a tu estructura real
    $pattern = '/CONFIG\s*=\s*\{([^}]+)\}/s';
    
    // Por ahora, simplemente reemplazar todo el CONFIG
    // En una implementación real, necesitarías una lógica más sofisticada
    return preg_replace($pattern, "CONFIG = {\n$newContent\n}", $content);
}
?>