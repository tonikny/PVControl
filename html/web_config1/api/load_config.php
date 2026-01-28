<?php
// api/load_config.php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    $file = $data['file'] ?? 'Parametros_FV_DIST_NUEVO.py';
    
    error_log("=== LOAD_CONFIG START ===");
    error_log("Requested file: " . $file);
    
    try {
        $filePath = '/home/pi/PVControl+/' . $file;
        
        if (!file_exists($filePath)) {
            throw new Exception("Archivo no encontrado: $filePath");
        }
        
        // Comando Python que maneja sets
        $command = "cd /home/pi/PVControl+ && python3 -c \"\n" .
                   "import json\n" .
                   "\n" .
                   "def convert_sets(obj):\n" .
                   "    if isinstance(obj, set):\n" .
                   "        return list(obj)  # Convertir set a lista\n" .
                   "    elif isinstance(obj, dict):\n" .
                   "        return {k: convert_sets(v) for k, v in obj.items()}\n" .
                   "    elif isinstance(obj, list):\n" .
                   "        return [convert_sets(item) for item in obj]\n" .
                   "    else:\n" .
                   "        return obj\n" .
                   "\n" .
                   "try:\n" .
                   "    with open('$file', 'r') as f:\n" .
                   "        exec(f.read())\n" .
                   "    \n" .
                   "    # Convertir sets a listas antes de serializar a JSON\n" .
                   "    config_converted = convert_sets(CONFIG)\n" .
                   "    print(json.dumps(config_converted))\n" .
                   "    \n" .
                   "except Exception as e:\n" .
                   "    print('PYTHON_ERROR: ' + str(e))\n" .
                   "    exit(1)\n" .
                   "\"";
        
        error_log("Executing Python command");
        $output = shell_exec($command . " 2>&1");
        error_log("Python output length: " . strlen($output));
        
        if ($output && strpos($output, 'PYTHON_ERROR:') === false) {
            $config = json_decode($output, true);
            if ($config !== null) {
                error_log("CONFIG loaded successfully, elements: " . count($config));
                
                echo json_encode([
                    'success' => true,
                    'config' => $config,
                    'file' => $file
                ]);
                exit;
            } else {
                error_log("JSON decode failed. Output sample: " . substr($output, 0, 200));
                throw new Exception("Error decodificando JSON de Python");
            }
        } else {
            throw new Exception("Error ejecutando Python: " . ($output ?: 'Sin salida'));
        }
        
    } catch (Exception $e) {
        error_log("ERROR: " . $e->getMessage());
        echo json_encode([
            'success' => false,
            'error' => $e->getMessage()
        ]);
        exit;
    }
}
?>