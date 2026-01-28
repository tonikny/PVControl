<?php
// list_files.php
header('Content-Type: text/html; charset=utf-8');
session_start();

function listDirectory($path) {
    if (!is_dir($path)) {
        return ['error' => 'Directorio no existe'];
    }
    
    $items = [];
    $files = scandir($path);
    
    foreach ($files as $file) {
        if ($file == '.' || $file == '..') continue;
        
        $full_path = $path . '/' . $file;
        $relative_path = str_replace('/home/pi/PVControl+/', '', $full_path);
        
        $item = [
            'name' => $file,
            'path' => $relative_path,
            'full_path' => $full_path,
            'is_dir' => is_dir($full_path),
            'size' => is_dir($full_path) ? 0 : filesize($full_path),
            'readable' => is_readable($full_path)
        ];
        
        $items[] = $item;
    }
    
    // Ordenar: directorios primero, luego archivos
    usort($items, function($a, $b) {
        if ($a['is_dir'] && !$b['is_dir']) return -1;
        if (!$a['is_dir'] && $b['is_dir']) return 1;
        return strcmp($a['name'], $b['name']);
    });
    
    return $items;
}

// Obtener path desde la petición
$request_path = $_POST['path'] ?? '/home/pi/PVControl+/';
$request_path = rtrim($request_path, '/') . '/';

// Validar que el path está dentro del directorio permitido
$base_path = '/home/pi/PVControl+/';
if (strpos($request_path, $base_path) !== 0) {
    $request_path = $base_path;
}

// Listar directorio
$result = [
    'success' => true,
    'path' => $request_path,
    'items' => listDirectory($request_path)
];

header('Content-Type: application/json');
echo json_encode($result);
?>