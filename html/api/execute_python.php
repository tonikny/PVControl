<?php
header("Content-Type: application/json; charset=UTF-8");

$pythonScriptPath = '/home/pi/PVControl+/Parametros_FV.py';

// Leer datos POST
$input = json_decode(file_get_contents("php://input"), true);
$logged = isset($input['logged']) ? $input['logged'] : false;

// SOLO ejecutar si está logueado
if (!$logged) {
    echo json_encode([
        "success" => false, 
        "error" => "No autenticado",
        "message" => "Debes estar en modo edición para ejecutar scripts. Haz clic en 'Editar Configuración' e ingresa la contraseña."
    ]);
    exit;
}

// Verificar archivo
if (!file_exists($pythonScriptPath)) {
    echo json_encode([
        "success" => false, 
        "error" => "Archivo no encontrado"
    ]);
    exit;
}

// Ejecutar script
set_time_limit(10);
$command = "cd /home/pi/PVControl+ && python3 " . escapeshellarg($pythonScriptPath) . " 2>&1";
$output = shell_exec($command);

// Procesar salida
if ($output === null || trim($output) === '') {
    $output = "(El script se ejecutó sin generar salida)";
    $success = true;
} else {
    $output = trim($output);
    // Determinar éxito basado en contenido de salida
    $success = (strpos($output, 'Traceback') === false && 
                strpos($output, 'Error:') === false &&
                strpos($output, 'SyntaxError') === false);
}

echo json_encode([
    "success" => $success,
    "output" => $output,
    "message" => $success ? "✅ Script ejecutado correctamente" : "❌ Error en la ejecución"
]);
?>