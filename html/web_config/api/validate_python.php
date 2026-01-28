<?php
// api/validate_python.php
header('Content-Type: 'application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $code = $data['code'] ?? '';
    $path = $data['path'] ?? '';
    
    error_log("Validando código Python para: $path");
    
    try {
        // Crear un contexto de prueba más realista
        $testCode = "#!/usr/bin/env python3\n# Prueba de sintaxis para: $path\n\n";
        
        // Para objetos/diccionarios, probar la asignación
        if (strpos($path, 'CONFIG.') === 0) {
            $testCode .= "CONFIG = {}\n\n";
            // Extraer la parte después de CONFIG.
            $configPath = substr($path, 7); // Remover "CONFIG."
            $pathParts = explode('.', $configPath);
            
            // Construir la asignación paso a paso
            $currentPath = 'CONFIG';
            foreach ($pathParts as $part) {
                $testCode .= "# Nivel: $part\n";
                $currentPath .= "['$part']";
            }
            
            $testCode .= "$currentPath = $code\n";
        } else {
            $testCode .= "test_value = $code\n";
        }
        
        $testCode .= "\n# Validación completada\nprint('OK')";
        
        // Crear archivo temporal
        $tempFile = tempnam(sys_get_temp_dir(), 'python_val_') . '.py';
        file_put_contents($tempFile, $testCode);
        
        // Ejecutar Python
        $command = "python3 " . escapeshellarg($tempFile) . " 2>&1";
        $output = shell_exec($command);
        
        // Limpiar
        unlink($tempFile);
        
        if ($output && trim($output) === 'OK') {
            echo json_encode([
                'valid' => true,
                'message' => 'Sintaxis Python válida'
            ]);
        } else {
            // Extraer solo el error relevante
            $errorOutput = $output ?: 'Error desconocido';
            
            // Limpiar el output para mostrar solo el error
            $errorLines = explode("\n", $errorOutput);
            $cleanError = array_filter($errorLines, function($line) {
                return strpos($line, 'File') === false || 
                       strpos($line, 'line') !== false ||
                       trim($line) === '' ||
                       strpos($line, 'Error') !== false ||
                       strpos($line, 'SyntaxError') !== false ||
                       strpos($line, 'NameError') !== false;
            });
            
            echo json_encode([
                'valid' => false,
                'error' => implode("\n", $cleanError)
            ]);
        }
        
    } catch (Exception $e) {
        echo json_encode([
            'valid' => false,
            'error' => $e->getMessage()
        ]);
    }
} else {
    echo json_encode([
        'valid' => false,
        'error' => 'Método no permitido'
    ]);
}
?>