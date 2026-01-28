<?php
// api/load_config_simple.php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';
    
    try {
        $filePath = '/home/pi/PVControl+/' . $file;
        
        if (!file_exists($filePath)) {
            throw new Exception("Archivo no encontrado");
        }
        
        // Comando simple
        $command = "cd /home/pi/PVControl+ && python3 -c "\"
try:
    with open('$file', 'r') as f:
        content = f.read()
    exec(content)
    if 'CONFIG' in locals():
        import json
        print(json.dumps(CONFIG))
    else:
        print('ERROR: CONFIG not found')
except Exception as e:
    print('ERROR: ' + str(e))
\"";
        
        $output = shell_exec($command . " 2>&1");
        
        if ($output && strpos($output, 'ERROR:') === false) {
            $config = json_decode($output, true);
            if ($config) {
                echo json_encode(['success' => true, 'config' => $config, 'file' => $file]);
                exit;
            }
        }
        
        throw new Exception("Error: " . ($output ?: 'No output from Python'));
        
    } catch (Exception $e) {
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        exit;
    }
}
?>