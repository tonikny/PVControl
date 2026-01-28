<?php
// services.php - VERSIÓN SIMPLIFICADA (3 CATEGORÍAS)
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

$servicesDir = '/home/pi/PVControl+/etc/systemd/system';

function listOurServices() {
    global $servicesDir;
    
    $services = [
        'active' => [],      // Activos y corriendo
        'stopped' => [],     // En systemd pero parados
        'disabled' => []     // No en systemd (no creados o deshabilitados)
    ];
    
    if (!is_dir($servicesDir)) {
        mkdir($servicesDir, 0755, true);
    }
    
    $serviceFiles = glob($servicesDir . '/*.service');
    
    foreach ($serviceFiles as $serviceFile) {
        $serviceName = basename($serviceFile);
        $baseName = str_replace('.service', '', $serviceName);
        
        $description = getServiceDescription($serviceFile);
        $modified = date('Y-m-d H:i:s', filemtime($serviceFile));
        
        // Verificar estado actual
        $state = checkServiceState($serviceName);
        
        $serviceInfo = [
            'name' => $baseName,
            'filename' => $serviceName,
            'description' => $description,
            'modified' => $modified,
            'state' => $state
        ];
        
        // 3 CATEGORÍAS SIMPLES:
        if ($state['in_systemd']) {
            // Está en systemd
            if ($state['active']) {
                $services['active'][] = $serviceInfo;      // Activo
            } else {
                $services['stopped'][] = $serviceInfo;     // Parado
            }
        } else {
            // No está en systemd
            $services['disabled'][] = $serviceInfo;        // No creado/Deshabilitado
        }
    }
    
    // Ordenar alfabéticamente
    foreach ($services as $key => $serviceList) {
        usort($services[$key], function($a, $b) {
            return strcmp($a['name'], $b['name']);
        });
    }
    
    $total = array_sum(array_map('count', $services));
    
    return [
        'success' => true,
        'data' => $services,
        'total' => $total
    ];
}

function checkServiceState($serviceName) {
    $state = [
        'in_systemd' => false,
        'enabled' => false,
        'active' => false
    ];
    
    // Verificar si systemd conoce el servicio
    exec("systemctl cat '$serviceName' 2>&1", $output, $code);
    
    if ($code === 0) {
        $state['in_systemd'] = true;
        
        // Verificar si está habilitado
        exec("systemctl is-enabled '$serviceName' 2>&1", $enabledOutput, $enabledCode);
        $enabledStr = trim(implode('', $enabledOutput));
        $state['enabled'] = ($enabledCode === 0 && in_array($enabledStr, ['enabled', 'linked', 'static', 'runtime']));
        
        // Verificar si está activo
        exec("systemctl is-active '$serviceName' 2>&1", $activeOutput, $activeCode);
        $activeStr = trim(implode('', $activeOutput));
        $state['active'] = ($activeCode === 0 && $activeStr === 'active');
    }
    
    return $state;
}

function controlService($serviceName, $action) {
    $fullServiceName = $serviceName . '.service';
    
    error_log("=== Control Service: $action en $serviceName ===");
    
    switch ($action) {
        case 'create':
            return createService($serviceName, false);
            
        case 'create-start':
            return createService($serviceName, true);
            
        case 'enable':
        case 'disable':
        case 'start':
        case 'stop':
        case 'restart':
            $command = "sudo systemctl $action '$fullServiceName' 2>&1";
            return executeCommand($command, $action);
            
        default:
            return ['success' => false, 'message' => 'Acción no válida'];
    }
}

function createService($serviceName, $startAfter = false) {
    $fullServiceName = $serviceName . '.service';
    $sourceFile = '/home/pi/PVControl+/etc/systemd/system/' . $fullServiceName;
    $targetLink = '/etc/systemd/system/' . $fullServiceName;
    
    error_log("=== Creando servicio: $serviceName ===");
    
    // Verificar archivo fuente
    if (!file_exists($sourceFile)) {
        return ['success' => false, 'message' => "Archivo $fullServiceName no existe"];
    }
    
    // Verificar si ya está en systemd
    exec("systemctl cat '$fullServiceName' 2>&1", $output, $code);
    if ($code === 0) {
        return ['success' => false, 'message' => 'El servicio ya está en systemd'];
    }
    
    // Crear enlace simbólico
    exec("sudo ln -sf '$sourceFile' '$targetLink' 2>&1", $lnOutput, $lnCode);
    
    if ($lnCode !== 0) {
        return ['success' => false, 'message' => 'Error creando enlace: ' . implode("\n", $lnOutput)];
    }
    
    // Recargar systemd
    exec('sudo systemctl daemon-reload 2>&1');
    sleep(1);
    
    // Habilitar el servicio
    exec("sudo systemctl enable '$fullServiceName' 2>&1", $enableOutput, $enableCode);
    
    $message = 'Servicio creado';
    
    if ($enableCode === 0) {
        $message .= ' y habilitado';
    }
    
    // Iniciar si se solicitó
    if ($startAfter) {
        sleep(1);
        exec("sudo systemctl start '$fullServiceName' 2>&1", $startOutput, $startCode);
        
        if ($startCode === 0) {
            $message .= ' e iniciado';
        } else {
            $message .= ' pero no se pudo iniciar';
        }
    }
    
    return ['success' => true, 'message' => $message];
}

function executeCommand($command, $action) {
    error_log("Ejecutando: $command");
    
    exec($command, $output, $code);
    $outputStr = implode("\n", $output);
    
    error_log("Resultado: Código=$code, Salida=$outputStr");
    
    if ($code === 0) {
        $messages = [
            'start' => 'Servicio iniciado',
            'stop' => 'Servicio detenido',
            'restart' => 'Servicio reiniciado',
            'enable' => 'Servicio habilitado',
            'disable' => 'Servicio deshabilitado'
        ];
        
        return ['success' => true, 'message' => $messages[$action] ?? 'Acción completada'];
    } else {
        // Manejo de errores comunes
        if ($action === 'disable') {
            if (strpos($outputStr, 'No such file') !== false) {
                return ['success' => false, 'message' => 'El servicio no existe en systemd'];
            }
            // Si ya está deshabilitado (enlace eliminado), es básicamente lo mismo
            return ['success' => true, 'message' => 'Servicio ya no está en systemd'];
        }
        
        if ($action === 'enable') {
            if (strpos($outputStr, 'enabled') !== false) {
                return ['success' => true, 'message' => 'El servicio ya estaba habilitado'];
            }
        }
        
        return ['success' => false, 'message' => "Error: $outputStr"];
    }
}

function getServiceDescription($serviceFile) {
    if (file_exists($serviceFile)) {
        $content = file_get_contents($serviceFile);
        if (preg_match('/Description\s*=\s*(.+)/', $content, $matches)) {
            return trim($matches[1]);
        }
    }
    return 'Servicio PVControl+';
}

ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', '/tmp/pvcontrol_3cat.log');

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET' && isset($_GET['action']) && $_GET['action'] === 'list') {
    echo json_encode(listOurServices());
    exit;
}

if ($method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['action']) || !isset($input['service'])) {
        echo json_encode(['success' => false, 'message' => 'Parámetros incompletos']);
        exit;
    }
    
    echo json_encode(controlService($input['service'], $input['action']));
    exit;
}

echo json_encode(['success' => false, 'message' => 'Método no soportado']);