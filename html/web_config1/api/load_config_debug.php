<?php
// api/load_config_debug.php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';
    
    error_log("=== DEBUG MODE ===");
    error_log("Requested file: " . $file);
    
    try {
        $filePath = '/home/pi/PVControl+/' . $file;
        error_log("Full path: " . $filePath);
        
        if (!file_exists($filePath)) {
            error_log("FILE NOT EXISTS");
            throw new Exception("Archivo no encontrado: $filePath");
        }
        
        error_log("FILE EXISTS");
        
        // Leer el archivo completo
        $content = file_get_contents($filePath);
        error_log("File size: " . strlen($content) . " bytes");
        
        // Mostrar primeras y últimas líneas
        $lines = explode("\n", $content);
        error_log("Total lines: " . count($lines));
        
        // Primeras 10 líneas
        error_log("=== FIRST 10 LINES ===");
        for ($i = 0; $i < min(10, count($lines)); $i++) {
            error_log("Line " . ($i + 1) . ": " . trim($lines[$i]));
        }
        
        // Últimas 5 líneas  
        error_log("=== LAST 5 LINES ===");
        for ($i = max(0, count($lines) - 5); $i < count($lines); $i++) {
            error_log("Line " . ($i + 1) . ": " . trim($lines[$i]));
        }
        
        // Buscar CONFIG
        error_log("=== SEARCHING FOR CONFIG ===");
        $configPos = strpos($content, 'CONFIG');
        if ($configPos !== false) {
            error_log("CONFIG found at position: " . $configPos);
            
            // Mostrar contexto alrededor de CONFIG
            $context = substr($content, max(0, $configPos - 50), 200);
            error_log("Context around CONFIG: " . $context);
        } else {
            error_log("CONFIG NOT FOUND IN FILE");
        }
        
        // Devolver el contenido completo para debugging en el navegador
        echo json_encode([
            'success' => true,
            'debug' => true,
            'file' => $file,
            'file_exists' => true,
            'file_size' => strlen($content),
            'total_lines' => count($lines),
            'config_found' => ($configPos !== false),
            'config_position' => $configPos,
            'first_lines' => array_slice($lines, 0, 10),
            'last_lines' => array_slice($lines, -5),
            'raw_content_sample' => substr($content, 0, 1000) . (strlen($content) > 1000 ? '...' : '')
        ]);
        
    } catch (Exception $e) {
        error_log("ERROR: " . $e->getMessage());
        echo json_encode([
            'success' => false,
            'error' => $e->getMessage(),
            'debug' => true
        ]);
    }
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Method not allowed'
    ]);
}
?>