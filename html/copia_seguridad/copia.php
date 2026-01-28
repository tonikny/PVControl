<?php
set_time_limit(600); // 10 minutos
ini_set('max_execution_time', 600);
ini_set('memory_limit', '256M'); // Por si acaso

session_start();
require_once 'lib/database.php';
require_once 'lib/gestion_copias.php';

// Configurar zona horaria del sistema
require_once 'lib/system_info.php';
$system_timezone = setupSystemTimezone();


// Verificar que el script se está ejecutando desde el navegador
if (php_sapi_name() === 'cli') {
    die("Este script solo puede ejecutarse desde el navegador web.");
}

// Validar método
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    $_SESSION['message'] = "Método no permitido";
    $_SESSION['message_type'] = 'error';
    header('Location: index.php');
    exit;
}

try {
    // Obtener selección del usuario 
    $selected_tables = $_POST['tables'] ?? [];
    $backup_name = $_POST['backup_name'] ?? ''; // ✅ NUEVO: Nombre personalizado


    // Validar que al menos hay una selección
    if (empty($selected_files) && empty($selected_tables)) {
        throw new Exception("Debes seleccionar al menos un archivo o tabla para el backup");
    }

    // Crear directorio temporal único
    $temp_dir = sys_get_temp_dir() . '/backup_pvcontrol_' . uniqid();
    if (!mkdir($temp_dir, 0755, true)) {
        throw new Exception("No se pudo crear directorio temporal para el backup");
    }

    // 1. Copiar archivos seleccionados al directorio temporal - SOLO SI HAY SELECCIÓN
    $root_path = '/home/pi/PVControl+/';
    $files_copied = 0;
    
    // ✅ COMBINAR archivos preferentes y adicionales
    $selected_files = array_merge(
        $_POST['preferred_files'] ?? [],
        $_POST['additional_files'] ?? []
    );

    if (!empty($selected_files)) {
        foreach ($selected_files as $file) {
            $source = $root_path . $file;
            $destination = $temp_dir . '/files/' . $file;
            
            error_log("🔍 Procesando archivo: $source");
            
            // Crear directorios padres si es necesario
            $dest_dir = dirname($destination);
            if (!is_dir($dest_dir)) {
                mkdir($dest_dir, 0755, true);
            }
            
            if (is_dir($source)) {
                error_log("📂 Copiando directorio: $source");        
                copyDirectory($source, $destination);
                $files_copied++;
            } else if (file_exists($source)) {
                error_log("📄 Copiando archivo: $source");
                if (copyFile($source, $destination)) {
                    $files_copied++;
                }
            } else {
                error_log("⚠️ Archivo no encontrado: $source");
            }
        }
        error_log("✅ Total de archivos copiados: $files_copied");
    }
    
    // 2. Exportar tablas seleccionadas de la base de datos - NUEVA VERSIÓN
    $db_backup_dir = $temp_dir . '/database';
    if (!mkdir($db_backup_dir, 0755, true)) {
        throw new Exception("No se pudo crear directorio para backup de BD");
    }

    if (!empty($selected_tables)) {
        if (!exportDatabaseTables('control_solar', $selected_tables, $db_backup_dir)) {
            throw new Exception("Error exportando tablas de la base de datos");
        }
        error_log("✅ Tablas exportadas: " . count($selected_tables));
    }

    // 3. Crear archivo de configuración con la selección REAL
    $config_content = "Backup PVControl+ - Selección Personalizada\n";
    $config_content .= "Fecha: " . date('Y-m-d H:i:s') . "\n";
    if (!empty($backup_name)) {
        $config_content .= "Nombre personalizado: " . htmlspecialchars($backup_name) . "\n";
    }
    $config_content .= "Archivos incluidos (" . count($selected_files) . "):\n";
    foreach ($selected_files as $file) {
        $config_content .= "- $file\n";
    }
    $config_content .= "\nTablas incluidas (" . count($selected_tables) . "):\n";
    foreach ($selected_tables as $table) {
        $config_content .= "- $table\n";
    }
    file_put_contents($temp_dir . '/backup_config.txt', $config_content);
    // 4. Crear archivo ZIP temporal
    $timestamp = date('Y-m-d_His');
    
    // ✅ GENERAR NOMBRE DEL ARCHIVO
    if (!empty($backup_name) && preg_match('/^[a-zA-Z0-9_-]+$/', $backup_name)) {
        // Nombre personalizado válido
        $clean_name = preg_replace('/[^a-zA-Z0-9_-]/', '_', $backup_name);
        $zip_filename = "backup_{$clean_name}_{$timestamp}.zip";
    } else {
        // Nombre por defecto
        $zip_filename = "backup_pvcontrol_{$timestamp}.zip";
    }
       
    $temp_zip = sys_get_temp_dir() . '/pvcontrol_backup_' . uniqid() . '.zip';
 
    $config_content .= "Archivo generado: " . $zip_filename . "\n"; // ✅ NUEVO
    
    error_log("🎯 Iniciando compresión final del backup...");
    
    // Intentar con método rápido del sistema primero
    if (!createZipSystem($temp_dir, $temp_zip)) {
        error_log("🔄 Falló compresión system, usando método PHP...");
        if (!createZip($temp_dir, $temp_zip)) {
            throw new Exception("Error creando archivo ZIP del backup");
        }
    }

    // Verificar que el ZIP se creó correctamente
    if (!file_exists($temp_zip) || filesize($temp_zip) === 0) {
        throw new Exception("El archivo ZIP generado está vacío o no existe");
    }

    $zip_size_mb = round(filesize($temp_zip) / 1024 / 1024, 2);
    error_log("✅ ZIP final creado: {$zip_size_mb} MB");

    // ✅ IMPORTANTE: TODO EL PROCESO TERMINA ANTES DE ENVIAR LA DESCARGA
    
    // 5. Enviar ZIP al cliente para descarga
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
    
    // ✅ ENVIAR ARCHIVO - esto debería ser lo ÚLTIMO
    readfile($temp_zip);
    
    // 6. Limpiar archivos temporales DESPUÉS de enviar el archivo
    deleteDirectory($temp_dir);
    unlink($temp_zip);
    
    error_log("🎉 Backup completado y descargado exitosamente: $files_copied archivos, " . count($selected_tables) . " tablas");
    exit;


} catch (Exception $e) {
    // Limpiar en caso de error
    if (isset($temp_dir) && is_dir($temp_dir)) {
        deleteDirectory($temp_dir);
    }
    if (isset($temp_zip) && file_exists($temp_zip)) {
        unlink($temp_zip);
    }
    
    // Registrar error y redirigir
    error_log("❌ Error en backup PVControl+: " . $e->getMessage());
    $_SESSION['message'] = "❌ Error generando backup: " . $e->getMessage();
    $_SESSION['message_type'] = 'error';
    header('Location: index.php');
    exit;
}
?>