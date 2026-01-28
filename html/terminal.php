<?php
// terminal_simple.php - Versión final operativa
header('Content-Type: application/json; charset=utf-8');

// Configurar locale para caracteres
setlocale(LC_ALL, 'es_ES.UTF-8');

// Verificar que estamos en el directorio correcto
chdir('/home/pi/PVControl+');

// Obtener datos del request
$command = $_POST['command'] ?? '';
$working_dir = $_POST['working_dir'] ?? '/home/pi/PVControl+';
$action = $_POST['action'] ?? 'execute';

// Validar
if (empty($command) && $action === 'execute') {
    echo json_encode(['error' => 'Comando vacío'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Cambiar al directorio de trabajo si es seguro
$safe_dirs = [
    '/home/pi/PVControl+',
    '/home/pi', 
    '/var/www/html',
    '/tmp'
];

if (in_array($working_dir, $safe_dirs) && is_dir($working_dir)) {
    chdir($working_dir);
}

if ($action === 'kill') {
    // PARAR PROCESO
    $pid = $_POST['pid'] ?? '';
    
    if (empty($pid)) {
        echo json_encode(['success' => false, 'error' => 'PID no especificado'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    $output = [];
    $return_code = 0;
    
    // Enviar SIGINT (CTRL+C)
    exec("sudo -u pi kill -2 " . escapeshellarg($pid) . " 2>&1", $output, $return_code);
    
    // Si no funciona, intentar con SIGTERM
    if ($return_code !== 0) {
        exec("sudo -u pi kill -15 " . escapeshellarg($pid) . " 2>&1", $output, $return_code);
    }
    
    // Si aún no funciona, forzar con SIGKILL
    if ($return_code !== 0) {
        exec("sudo -u pi kill -9 " . escapeshellarg($pid) . " 2>&1", $output, $return_code);
    }
    
    echo json_encode([
        'success' => $return_code === 0,
        'action' => 'kill',
        'pid' => $pid,
        'output' => $output,
        'return_code' => $return_code
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($action === 'processes') {
    // OBTENER LISTA DE PROCESOS
    exec("sudo -u pi ps -eo pid,user,etime,cmd --forest | grep python | grep -v grep", $output, $return_code);
    
    echo json_encode([
        'success' => true,
        'action' => 'processes',
        'processes' => $output,
        'count' => count($output)
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// EJECUTAR COMANDO NORMAL
$output = [];
$return_var = 0;

// Preparar comando con entorno virtual
$env_activate = 'source /home/pi/PVControl+/env/bin/activate';
$full_command = $command;

// Si el comando es de Python, ejecutar con el Python del entorno virtual
if (strpos($command, 'python') === 0 || 
    strpos($command, 'pip') === 0 ||
    strpos($command, 'python3') === 0 ||
    strpos($command, 'pip3') === 0) {
    
    // Reemplazar python/pip por las versiones del entorno virtual
    $full_command = preg_replace('/^python3?/', '/home/pi/PVControl+/env/bin/python', $command);
    $full_command = preg_replace('/^pip3?/', '/home/pi/PVControl+/env/bin/pip', $full_command);
    
} else {
    // Para otros comandos, activar el entorno y luego ejecutar
    $full_command = $env_activate . ' && ' . $command;
}

// Ejecutar comando como usuario pi
exec("sudo -u pi bash -c " . escapeshellarg($full_command) . " 2>&1", $output, $return_var);

// Obtener información del sistema
$current_dir = getcwd();
$user = trim(shell_exec('whoami'));
$hostname = trim(shell_exec('hostname'));

// Verificar si el entorno virtual está activo en este contexto
$python_path = '';
exec("sudo -u pi bash -c " . escapeshellarg("$env_activate && which python") . " 2>&1", $python_output, $python_return);
if ($python_return === 0 && !empty($python_output)) {
    $python_path = $python_output[0];
}

// Respuesta
echo json_encode([
    'success' => true,
    'command' => $command,
    'full_command' => $full_command,
    'output' => $output,
    'return_code' => $return_var,
    'current_dir' => $current_dir,
    'user' => $user,
    'hostname' => $hostname,
    'python_path' => $python_path,
    'timestamp' => date('Y-m-d H:i:s')
], JSON_UNESCAPED_UNICODE);
?>