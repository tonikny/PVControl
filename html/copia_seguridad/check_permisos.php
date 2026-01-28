<?php
// check_permisos.php - Verificar permisos
header('Content-Type: text/plain; charset=utf-8');

echo "=== VERIFICACIÓN DE PERMISOS ===\n\n";

$paths_to_check = [
    '/home/pi/PVControl+/',
    '/home/pi/PVControl+/html/',
    '/home/pi/PVControl+/html/configuraciones/',
    '/home/pi/PVControl+/backups/',
    '/home/pi/PVControl+/backups/pre_restore/'
];

foreach ($paths_to_check as $path) {
    echo "📁 $path\n";
    
    if (!file_exists($path)) {
        echo "   ❌ NO EXISTE\n";
        continue;
    }
    
    $perms = fileperms($path);
    $readable = is_readable($path) ? '✅ SÍ' : '❌ NO';
    $writable = is_writable($path) ? '✅ SÍ' : '❌ NO';
    $executable = is_executable($path) ? '✅ SÍ' : '❌ NO';
    
    echo "   Permisos: " . substr(sprintf('%o', $perms), -4) . "\n";
    echo "   Legible: $readable\n";
    echo "   Escribible: $writable\n";
    echo "   Ejecutable: $executable\n";
    
    // Mostrar propietario y grupo
    $owner = fileowner($path);
    $group = filegroup($path);
    echo "   Propietario: " . (function_exists('posix_getpwuid') ? posix_getpwuid($owner)['name'] : $owner) . "\n";
    echo "   Grupo: " . (function_exists('posix_getgrgid') ? posix_getgrgid($group)['name'] : $group) . "\n";
    echo "\n";
}

// Verificar usuario actual
echo "=== INFORMACIÓN DEL SERVIDOR ===\n";
echo "Usuario PHP: " . get_current_user() . "\n";
echo "Usuario del proceso: " . (function_exists('posix_getpwuid') ? posix_getpwuid(posix_geteuid())['name'] : 'Desconocido') . "\n";
echo "Grupo del proceso: " . (function_exists('posix_getgrgid') ? posix_getgrgid(posix_getegid())['name'] : 'Desconocido') . "\n";

// Verificar archivos específicos
echo "\n=== ARCHIVOS CRÍTICOS ===\n";
$critical_files = [
    '/home/pi/PVControl+/html/configuracion_activa.txt',
    '/home/pi/PVControl+/html/Parametros_Web.js',
    '/home/pi/PVControl+/html/version.inc',
    '/home/pi/PVControl+/Parametros_FV.py'
];

foreach ($critical_files as $file) {
    echo "📄 $file\n";
    
    if (!file_exists($file)) {
        echo "   ❌ NO EXISTE\n";
        continue;
    }
    
    $readable = is_readable($file) ? '✅ SÍ' : '❌ NO';
    $writable = is_writable($file) ? '✅ SÍ' : '❌ NO';
    
    echo "   Legible: $readable\n";
    echo "   Escribible: $writable\n";
    echo "\n";
}
?>