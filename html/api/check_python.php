<?php
header("Content-Type: application/json; charset=UTF-8");

$pythonScriptPath = '/home/pi/PVControl+/Parametros_FV.py';

// Verificar si el archivo existe
if (!file_exists($pythonScriptPath)) {
    echo json_encode([
        "success" => false, 
        "error" => "Archivo no encontrado: $pythonScriptPath"
    ]);
    exit;
}

// Leer el contenido COMPLETO del archivo (sin ofuscación)
$content = file_get_contents($pythonScriptPath);

// Crear archivo temporal para verificación
$tempFile = tempnam(sys_get_temp_dir(), 'python_check_');
file_put_contents($tempFile, $content);

// Verificar sintaxis con python -m py_compile
$command = "python3 -m py_compile " . escapeshellarg($tempFile) . " 2>&1";
$output = shell_exec($command);

// Limpiar archivo .pyc si se creó
$pycFile = $tempFile . 'c';
if (file_exists($pycFile)) {
    unlink($pycFile);
}

// Limpiar archivo temporal
unlink($tempFile);

if (empty(trim($output))) {
    echo json_encode([
        "success" => true,
        "message" => "✅ Sintaxis Python correcta",
        "output" => ""
    ]);
} else {
    // Limpiar mensaje de error
    $cleanOutput = trim($output);
    $cleanOutput = str_replace($pythonScriptPath, 'Parametros_FV.py', $cleanOutput);
    
    echo json_encode([
        "success" => false,
        "error" => "❌ Error de sintaxis",
        "output" => $cleanOutput
    ]);
}
?>