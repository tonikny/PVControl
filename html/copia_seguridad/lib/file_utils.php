<?php

/**
 * Verifica los permisos de los directorios críticos
 */
function checkDirectoryPermissions() {
    $critical_dirs = [
        '/home/pi/PVControl+/',
        '/home/pi/PVControl+/html/',
        '/home/pi/PVControl+/html/configuraciones/'
    ];
    
    $results = [];
    foreach ($critical_dirs as $dir) {
        if (!is_dir($dir)) {
            $results[$dir] = 'NO EXISTE';
        } else if (!is_readable($dir)) {
            $results[$dir] = 'NO LEGIBLE';
        } else if (!is_writable($dir)) {
            $results[$dir] = 'NO ESCRIBIBLE';
        } else {
            $results[$dir] = 'OK';
        }
    }
    
    return $results;
}

/**
 * Obtiene información del sistema
 */
function getSystemInfo() {
    return [
        'php_version' => PHP_VERSION,
        'zip_enabled' => extension_loaded('zip'),
        'mysqli_enabled' => extension_loaded('mysqli'),
        'max_upload_size' => ini_get('upload_max_filesize'),
        'max_post_size' => ini_get('post_max_size'),
        'memory_limit' => ini_get('memory_limit')
    ];
}

/**
 * Formatea bytes a formato legible
 */
function formatBytes($bytes, $precision = 2) {
    $units = ['B', 'KB', 'MB', 'GB', 'TB'];
    $bytes = max($bytes, 0);
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
    $pow = min($pow, count($units) - 1);
    $bytes /= pow(1024, $pow);
    
    return round($bytes, $precision) . ' ' . $units[$pow];
}
?>