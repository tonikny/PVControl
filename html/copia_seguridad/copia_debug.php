<?php
// backup_debug.php - Versión con debug completo 
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Log inicial
error_log("=== INICIANDO BACKUP DEBUG ===");

try {
    // Incluir librerías
    require_once 'lib/database.php';
    require_once 'lib/backup_manager.php';
    error_log("✅ Librerías incluidas");

    // Verificar que el script se está ejecutando desde el navegador
    if (php_sapi_name() === 'cli') {
        die("Este script solo puede ejecutarse desde el navegador web.");
    }

    // Crear directorio temporal único
    $temp_dir = sys_get_temp_dir() . '/backup_pvcontrol_' . uniqid();
    error_log("🔧 Intentando crear directorio temporal: " . $temp_dir);
    
    if (!mkdir($temp_dir, 0755, true)) {
        throw new Exception("No se pudo crear directorio temporal para el backup");
    }
    error_log("✅ Directorio temporal creado: " . $temp_dir);

    // Definir archivos a incluir en el backup
    $root_path = '/home/pi/PVControl+/';
    $files_to_backup = [
        'Parametros_FV.py',
        'html/Parametros_Web.js',
        'html/version.inc',
        'html/configuracion_activa.txt',
        'html/configuraciones/'
    ];

    error_log("📁 Copiando archivos...");
    
    // 1. Copiar archivos al directorio temporal
    foreach ($files_to_backup as $file) {
        $source = $root_path . $file;
        $destination = $temp_dir . '/files/' . $file;
        
        error_log("🔍 Procesando: " . $source);
        
        if (is_dir($source)) {
            error_log("📂 Es directorio: " . $source);
            copyDirectory($source, $destination);
        } else if (file_exists($source)) {
            error_log("📄 Es archivo: " . $source);
            copyFile($source, $destination);
        } else {
            error_log("⚠️ Archivo no encontrado: " . $source);
        }
    }
    error_log("✅ Archivos copiados");

    // 2. Exportar tablas de la base de datos
    error_log("🗄️ Exportando base de datos...");
    $tables = ['diario', 'reles', 'reles_c', 'reles_h', 'condiciones'];
    $db_backup_file = $temp_dir . '/database_backup.sql';
    exportDatabaseTables('control_solar', $tables, $db_backup_file);
    error_log("✅ Base de datos exportada");

    // 3. Crear archivo README
    error_log("📝 Creando README...");
    $readme_content = "Backup PVControl+\n";
    $readme_content .= "Fecha: " . date('Y-m-d H:i:s') . "\n";
    file_put_contents($temp_dir . '/README.txt', $readme_content);
    error_log("✅ README creado");

    // 4. Crear archivo ZIP temporal
    error_log("🗜️ Creando ZIP...");
    $zip_filename = 'backup_pvcontrol_' . date('Y-m-d_H-i-s') . '.zip';
    $temp_zip = sys_get_temp_dir() . '/pvcontrol_backup_' . uniqid() . '.zip';
    
    if (!createZip($temp_dir, $temp_zip)) {
        throw new Exception("Error creando archivo ZIP del backup");
    }
    error_log("✅ ZIP creado: " . $temp_zip);

    // 5. Verificar que el ZIP se creó correctamente
    if (!file_exists($temp_zip) || filesize($temp_zip) === 0) {
        throw new Exception("El archivo ZIP generado está vacío o no existe");
    }
    error_log("✅ ZIP verificado, tamaño: " . filesize($temp_zip) . " bytes");

    // 6. Enviar ZIP al cliente para descarga
    error_log("📤 Enviando archivo al cliente...");
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="' . $zip_filename . '"');
    header('Content-Length: ' . filesize($temp_zip));
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');
    header('Content-Transfer-Encoding: binary');
    
    // Limpiar buffer de salida
    if (ob_get_level()) {
        ob_end_clean();
    }
    
    readfile($temp_zip);
    error_log("✅ Archivo enviado al cliente");
    
    // 7. Limpiar archivos temporales
    error_log("🧹 Limpiando archivos temporales...");
    deleteDirectory($temp_dir);
    unlink($temp_zip);
    error_log("✅ Limpieza completada");
    
    exit;

} catch (Exception $e) {
    error_log("❌ ERROR CRÍTICO: " . $e->getMessage());
    error_log("📍 Archivo: " . $e->getFile() . " Línea: " . $e->getLine());
    
    // Limpiar en caso de error
    if (isset($temp_dir) && is_dir($temp_dir)) {
        deleteDirectory($temp_dir);
    }
    if (isset($temp_zip) && file_exists($temp_zip)) {
        unlink($temp_zip);
    }
    
    // Mostrar error en pantalla para debug
    die("❌ ERROR: " . $e->getMessage() . " (Ver logs para más detalles)");
}
?>