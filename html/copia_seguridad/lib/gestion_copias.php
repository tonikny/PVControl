<?php
// =============================================================================
// FUNCIONES DE BACKUP (EXPORTACIÓN)
// =============================================================================

/**
 * Exporta tablas usando mysqldump
 */
function exportDatabaseTables($database, $tables, $output_dir) {
    $db_config = getDatabaseConfig();
    
    error_log("📤 Exportando tablas con mysqldump: " . implode(', ', $tables));
    
    $exported_tables = [];
    
    foreach ($tables as $table) {
        $table_file = $output_dir . '/' . $table . '.sql';
        
        // Verificar que la tabla existe
        $db = getDatabaseConnection();
        $result = $db->query("SHOW TABLES LIKE '$table'");
        if (!$result || $result->num_rows === 0) {
            error_log("⚠️ Tabla $table no existe, se omite");
            continue;
        }
        
        // Comando mysqldump para exportar la tabla
        $command = sprintf(
            'mysqldump -h %s -u %s -p%s --quick --single-transaction --skip-comments %s %s > %s 2>&1',

            escapeshellarg($db_config['host']),
            escapeshellarg($db_config['username']),
            escapeshellarg($db_config['password']),
            escapeshellarg($database),
            escapeshellarg($table),
            escapeshellarg($table_file)
        );
        
        error_log("⚡ Ejecutando: mysqldump $database $table");
        
        // Ejecutar comando
        $output = [];
        $return_var = 0;
        exec($command, $output, $return_var);
        
        if ($return_var === 0 && file_exists($table_file) && filesize($table_file) > 0) {
            $exported_tables[] = $table;
            
            // Solo mostrar tamaño - NO CONTAR LÍNEAS
            $file_size_mb = round(filesize($table_file) / 1024 / 1024, 2);
            error_log("✅ Tabla $table exportada: $table_file ({$file_size_mb} MB)");
                        
        } else {
            error_log("❌ Error exportando tabla $table: " . implode("\n", $output));
        }
    }
    
    error_log("📊 Exportación completada: " . count($exported_tables) . " tablas exportadas");
    return $exported_tables;

}

// =============================================================================
// FUNCIONES DE RESTAURACIÓN
// =============================================================================

/**
 * Restaura un backup desde un archivo ZIP - VERSIÓN COHERENTE
 */
function restoreBackup($zip_file) {
    $temp_dir = sys_get_temp_dir() . '/restore_pvcontrol_' . uniqid();
    if (!mkdir($temp_dir, 0755, true)) {
        throw new Exception("No se pudo crear directorio temporal para restauración");
    }
    
    try {
        // Extraer ZIP
        $zip = new ZipArchive();
        if ($zip->open($zip_file) !== TRUE) {
            throw new Exception("No se pudo abrir archivo ZIP para extracción");
        }
        
        $zip->extractTo($temp_dir);
        $zip->close();
        
        // Restaurar archivos
        $files_dir = $temp_dir . '/files';
        $root_path = '/home/pi/PVControl+';
        
        if (is_dir($files_dir)) {
            // Crear backup de seguridad
            try {
                createPreRestoreBackup();
            } catch (Exception $e) {
                error_log("⚠️ Backup de seguridad falló: " . $e->getMessage());
            }
            
            // Restaurar archivos
            restoreFilesFromBackup($files_dir, $root_path);
        }
        
        // Restaurar base de datos
        $db_file = $temp_dir . '/database_backup.sql';
        if (file_exists($db_file)) {
            restoreDatabase($db_file);
        }
        
    } finally {
        // Siempre limpiar el directorio temporal
        deleteDirectory($temp_dir);
    }
}

/**
 * Restaura la base de datos desde un archivo SQL - VERSIÓN QUERY POR QUERY
 */
function restoreDatabase($sql_file) {
    $db = getDatabaseConnection();
    
    error_log("🗄️ Iniciando restauración de base de datos desde: " . $sql_file);
    
    // Leer archivo SQL
    $sql = file_get_contents($sql_file);
    if ($sql === false) {
        throw new Exception("No se pudo leer archivo SQL de backup");
    }
    
    // Desactivar claves foráneas
    $db->query("SET FOREIGN_KEY_CHECKS = 0");
    $db->query("SET AUTOCOMMIT = 0");
    $db->query("START TRANSACTION");
    
    try {
        // Dividir en queries individuales y ejecutar una por una
        $queries = array_filter(array_map('trim', explode(';', $sql)));
        $executed_count = 0;
        $error_count = 0;
        
        error_log("🔍 Ejecutando " . count($queries) . " queries individualmente");
        
        foreach ($queries as $index => $query) {
            if (empty($query) || substr($query, 0, 2) === '--') {
                continue;
            }
            
            $query_short = strlen($query) > 100 ? substr($query, 0, 100) . "..." : $query;
            error_log("⚡ Ejecutando query $index: $query_short");
            
            if ($db->query($query)) {
                $executed_count++;
                error_log("✅ Query $index ejecutada correctamente");
            } else {
                $error_msg = "Error en query $index: " . $db->error;
                error_log("❌ " . $error_msg);
                $error_count++;
                
                // Para errores de "table already exists", es normal después de DROP TABLE IF EXISTS
                if (strpos($db->error, 'already exists') !== false) {
                    error_log("⚠️ Tabla ya existe, continuando...");
                    continue;
                }
                
                throw new Exception($error_msg);
            }
        }
        
        $db->query("COMMIT");
        $db->query("SET FOREIGN_KEY_CHECKS = 1");
        
        error_log("✅ Restauración completada: $executed_count queries ejecutadas, $error_count errores");
        
    } catch (Exception $e) {
        $db->query("ROLLBACK");
        $db->query("SET FOREIGN_KEY_CHECKS = 1");
        throw $e;
    }
}

/**
 * Restaura tablas usando mysql CLI - VERSIÓN CONFIABLE
 */
function restoreSelectedTablesSimple($backup_dir, $selected_tables) {
    $db_config = getDatabaseConfig();
    
    error_log("🗄️ Restaurando tablas con mysql CLI: " . implode(', ', $selected_tables));
    
    $restored_count = 0;
    $error_count = 0;
    
    foreach ($selected_tables as $table) {
        $table_file = $backup_dir . '/' . $table . '.sql';
        
        if (!file_exists($table_file)) {
            error_log("⚠️ Archivo no encontrado: $table_file");
            $error_count++;
            continue;
        }
        
        error_log("🔍 Restaurando tabla $table desde: $table_file");
        
        // Comando mysql para importar
        $command = sprintf(
            'mysql -h %s -u %s -p%s %s < %s 2>&1',
            escapeshellarg($db_config['host']),
            escapeshellarg($db_config['username']),
            escapeshellarg($db_config['password']),
            escapeshellarg($db_config['database']),
            escapeshellarg($table_file)
        );
        
        error_log("⚡ Ejecutando: mysql < $table_file");
        
        // Ejecutar comando
        $output = [];
        $return_var = 0;
        exec($command, $output, $return_var);
        
        if ($return_var === 0) {
            $restored_count++;
            
            // Verificar que se restauró correctamente
            $db = getDatabaseConnection();
            $result = $db->query("SELECT COUNT(*) as count FROM `$table`");
            $count = $result ? $result->fetch_assoc()['count'] : 0;
            
            error_log("✅ Tabla $table restaurada - $count registros");
        } else {
            $error_count++;
            $error_msg = implode("\n", $output);
            error_log("❌ Error restaurando $table: $error_msg");
            
            // Fallback: método PHP
            error_log("🔄 Intentando con método PHP...");
            if (restoreTableWithPHP($table_file)) {
                $restored_count++;
                error_log("✅ Tabla $table restaurada con método PHP");
            }
        }
    }
    
    error_log("🎯 RESTAURACIÓN FINALIZADA: $restored_count tablas, $error_count errores");
}

/**
 * Método PHP como fallback para restauración
 */
function restoreTableWithPHP($table_file) {
    try {
        $db = getDatabaseConnection();
        $sql_content = file_get_contents($table_file);
        
        if ($db->multi_query($sql_content)) {
            do {
                if ($result = $db->store_result()) {
                    $result->free();
                }
            } while ($db->more_results() && $db->next_result());
            return true;
        }
        return false;
    } catch (Exception $e) {
        error_log("❌ Error en método PHP: " . $e->getMessage());
        return false;
    }
}

/**
 * Función de diagnóstico para verificar el estado de las tablas
 */
function diagnoseTableRestorationNew($db_backup_dir, $selected_tables) {
    $db = getDatabaseConnection();
    
    error_log("🔍 DIAGNÓSTICO NUEVA ESTRUCTURA:");
    
    // Verificar estado actual de las tablas seleccionadas
    foreach ($selected_tables as $table) {
        $result = $db->query("SHOW TABLES LIKE '$table'");
        $exists = $result && $result->num_rows > 0;
        
        if ($exists) {
            $count_result = $db->query("SELECT COUNT(*) as count FROM `$table`");
            $count = $count_result ? $count_result->fetch_assoc()['count'] : 0;
            error_log("📊 Tabla '$table': EXISTE con $count registros");
        } else {
            error_log("📊 Tabla '$table': NO EXISTE");
        }
        
        // Verificar archivos de backup
        $table_file = $db_backup_dir . '/' . $table . '.sql';
        if (file_exists($table_file)) {
            $file_size = filesize($table_file);
            $file_size_mb = round($file_size / 1024 / 1024, 2);
            
            // ✅ CAMBIO MÍNIMO: Solo mostrar tamaño, NO contar líneas
            error_log("📁 Archivo '$table.sql': EXISTE ($file_size bytes, {$file_size_mb} MB)");
            
            // Verificar contenido con método seguro
            $has_insert = fileHasStringSafe($table_file, 'INSERT INTO');
            $has_create = fileHasStringSafe($table_file, 'CREATE TABLE');
            error_log("   - Contiene CREATE: " . ($has_create ? 'SÍ' : 'NO'));
            error_log("   - Contiene INSERT: " . ($has_insert ? 'SÍ' : 'NO'));
        } else {
            error_log("📁 Archivo '$table.sql': NO EXISTE");
        }
    }
    
    // Listar todos los archivos en el directorio de database
    $all_files = scandir($db_backup_dir);
    $sql_files = array_filter($all_files, function($file) {
        return pathinfo($file, PATHINFO_EXTENSION) === 'sql';
    });
    error_log("📊 Archivos SQL en backup: " . implode(', ', $sql_files));
}

/**
 * Verifica si un archivo contiene un string SIN cargarlo completamente en memoria
 */
function fileHasStringSafe($filename, $search_string) {
    $file = fopen($filename, 'r');
    if (!$file) {
        return false;
    }
    
    $found = false;
    // Leer solo los primeros 64KB para buscar las cabeceras SQL
    $content = fread($file, 65536);
    if (strpos($content, $search_string) !== false) {
        $found = true;
    }
    
    fclose($file);
    return $found;
}

// =============================================================================
// FUNCIONES AUXILIARES
// =============================================================================

/**
 * Filtra el SQL para incluir solo las tablas seleccionadas
 */
function filterSQLForTables($sql, $selected_tables) {
    $queries = array_filter(array_map('trim', explode(';', $sql)));
    $filtered_queries = [];
    
    foreach ($queries as $query) {
        if (empty($query) || substr($query, 0, 2) === '--') {
            continue;
        }
        
        $include_query = false;
        
        foreach ($selected_tables as $table) {
            // CORRECCIÓN: Buscar la tabla en diferentes contextos
            $table_pattern = '`?' . preg_quote($table, '/') . '`?';
            
            // Buscar en CREATE TABLE, DROP TABLE, INSERT INTO
            if (preg_match('/(CREATE TABLE|DROP TABLE|INSERT INTO)\s+(?:IF NOT EXISTS\s+|IF EXISTS\s+)?' . $table_pattern . '/i', $query)) {
                $include_query = true;
                break;
            }
            
            // También incluir comentarios que mencionen la tabla (para mantener contexto)
            if (preg_match('/--.*\b' . preg_quote($table, '/') . '\b/i', $query)) {
                $include_query = true;
                break;
            }
        }
        
        if ($include_query) {
            $filtered_queries[] = $query;
            error_log("✅ Query incluida para filtrado: " . substr($query, 0, 100));
        } else {
            error_log("❌ Query excluida: " . substr($query, 0, 100));
        }
    }
    
    $result = implode(";\n", $filtered_queries) . ';';
    error_log("📊 SQL filtrado: " . count($filtered_queries) . " queries, longitud: " . strlen($result));
    
    return $result;
}

/**
 * Copiar archivo individual
 */
function copyFile($source, $destination) {
    $dir = dirname($destination);
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
    }
    
    if (!copy($source, $destination)) {
        throw new Exception("No se pudo copiar el archivo: $source");
    }
}

/**
 * Copia un directorio recursivamente
 */
function copyDirectory($source, $destination) {
    if (!is_dir($source)) {
        throw new Exception("El directorio fuente no existe: $source");
    }
    
    if (!is_dir($destination)) {
        if (!mkdir($destination, 0755, true)) {
            throw new Exception("No se pudo crear directorio destino: $destination");
        }
    }
    
    $dir = opendir($source);
    if (!$dir) {
        throw new Exception("No se pudo abrir directorio: $source");
    }
    
    while (($file = readdir($dir)) !== false) {
        if ($file == '.' || $file == '..') {
            continue;
        }
        
        $srcFile = $source . '/' . $file;
        $destFile = $destination . '/' . $file;
        
        if (is_dir($srcFile)) {
            copyDirectory($srcFile, $destFile);
        } else {
            copyFile($srcFile, $destFile);
        }
    }
    closedir($dir);
}

/**
 * Crea un archivo ZIP desde un directorio
 */
function createZip($source, $destination) {
    if (!extension_loaded('zip')) {
        throw new Exception("Extensión ZIP no está habilitada en PHP");
    }
    
    $zip = new ZipArchive();
    if ($zip->open($destination, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== TRUE) {
        throw new Exception("No se pudo crear archivo ZIP: $destination");
    }
    
    $source = realpath($source);
    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($source, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::SELF_FIRST
    );
    
    foreach ($files as $file) {
        if ($file->isDir()) {
            continue;
        }
        
        $filePath = $file->getRealPath();
        
        // ✅ CORRECCIÓN: Usar ruta relativa desde $source, no incluir la carpeta temporal
        $relativePath = substr($filePath, strlen($source) + 1);
        
        if (!$zip->addFile($filePath, $relativePath)) {
            error_log("⚠️ No se pudo agregar archivo al ZIP: $filePath");
        }
    }
    
    return $zip->close();
}

/**
 * Crea ZIP usando comando del sistema - MÁS RÁPIDO Y SIN TIMEOUT
 */
function createZipSystem($source, $destination) {
    error_log("📦 Creando ZIP con comando system: $source -> $destination");
    
    $source = realpath($source);
    
    // ✅ SOLUCIÓN: Comprimir solo el contenido de la carpeta, no la carpeta misma
    $command = sprintf(
        'cd %s && zip -rq %s . -i "*" 2>&1',
        escapeshellarg($source),
        escapeshellarg($destination)
    );
    
    error_log("⚡ Ejecutando: $command");
    
    $output = [];
    $return_var = 0;
    exec($command, $output, $return_var);
    
    if ($return_var === 0 && file_exists($destination)) {
        $file_size_mb = round(filesize($destination) / 1024 / 1024, 2);
        error_log("✅ ZIP creado exitosamente: $destination ({$file_size_mb} MB)");
        
        // ✅ Verificar la estructura del ZIP
        $check_command = sprintf('unzip -l %s | head -10', escapeshellarg($destination));
        exec($check_command, $zip_content, $check_return);
        if ($check_return === 0) {
            error_log("📁 Estructura del ZIP:");
            foreach ($zip_content as $line) {
                error_log("   $line");
            }
        }
        
        return true;
    } else {
        $error_msg = implode("\n", $output);
        error_log("❌ Error creando ZIP: $error_msg");
        return false;
    }
}

/**
 * Restaura archivos desde el backup
 */
function restoreFilesFromBackup($source_dir, $destination_dir) {
    if (!is_dir($source_dir)) {
        throw new Exception("Directorio fuente no existe: $source_dir");
    }
    
    if (!is_dir($destination_dir)) {
        if (!mkdir($destination_dir, 0755, true)) {
            throw new Exception("No se pudo crear directorio destino: $destination_dir");
        }
    }
    
    $items = scandir($source_dir);
    foreach ($items as $item) {
        if ($item == '.' || $item == '..') {
            continue;
        }
        
        $source_path = $source_dir . '/' . $item;
        $dest_path = $destination_dir . '/' . $item;
        
        if (is_dir($source_path)) {
            restoreFilesFromBackup($source_path, $dest_path);
        } else {
            copyBackupFile($source_path, $dest_path);
        }
    }
}



/**
 * Copiar archivo individual con manejo de errores
 */
function copyBackupFile($source, $destination) {
    // Crear directorio destino si no existe
    $dest_dir = dirname($destination);
    if (!is_dir($dest_dir)) {
        if (!mkdir($dest_dir, 0755, true)) {
            throw new Exception("No se pudo crear directorio: $dest_dir");
        }
    }
    
    if (!file_exists($source)) {
        throw new Exception("Archivo fuente no existe: $source");
    }
    
    if (!copy($source, $destination)) {
        throw new Exception("No se pudo copiar archivo: $source → $destination");
    }
    
    // Establecer permisos adecuados
    chmod($destination, 0644);
}

/**
 * Crea un mini-backup de seguridad antes de restaurar
 */
function createPreRestoreBackup() {
    $backup_dir = '/home/pi/PVControl+/backups/pre_restore/';
    
    if (!is_dir($backup_dir)) {
        if (!mkdir($backup_dir, 0755, true)) {
            error_log("⚠️ No se pudo crear directorio de backup pre_restore");
            return;
        }
    }
    
    $timestamp = date('Y-m-d_H-i-s');
    $critical_files = [
        'Parametros_FV.py',
        'html/Parametros_Web.js',
        'html/version.inc',
        'html/configuracion_activa.txt'
    ];
    
    foreach ($critical_files as $file) {
        $source = '/home/pi/PVControl+/' . $file;
        if (file_exists($source)) {
            $backup_file = $backup_dir . $timestamp . '_' . basename($file);
            copy($source, $backup_file);
        }
    }
}

/**
 * Elimina un directorio recursivamente
 */
function deleteDirectory($dir) {
    if (!is_dir($dir)) {
        return;
    }
    
    $files = array_diff(scandir($dir), array('.', '..'));
    foreach ($files as $file) {
        $path = $dir . '/' . $file;
        is_dir($path) ? deleteDirectory($path) : unlink($path);
    }
    
    rmdir($dir);
}

/**
 * Restaura backup con selección específica de archivos y tablas
 */
function restoreBackupWithSelection($zip_file, $selected_files, $selected_tables) {
    $temp_dir = sys_get_temp_dir() . '/restore_pvcontrol_' . uniqid();
    if (!mkdir($temp_dir, 0755, true)) {
        throw new Exception("No se pudo crear directorio temporal para restauración");
    }
    
    try {
        // Extraer ZIP
        $zip = new ZipArchive();
        if ($zip->open($zip_file) !== TRUE) {
            throw new Exception("No se pudo abrir archivo ZIP para extracción");
        }
        
        $zip->extractTo($temp_dir);
        $zip->close();
        
        // DIAGNÓSTICO ANTES DE RESTAURAR
        error_log("🎯 INICIANDO DIAGNÓSTICO PRE-RESTAURACIÓN");
        $db_backup_dir = $temp_dir . '/database';
        if (is_dir($db_backup_dir) && !empty($selected_tables)) {
            diagnoseTableRestorationNew($db_backup_dir, $selected_tables);
        }
        
        // Restaurar archivos seleccionados
        $files_dir = $temp_dir . '/files';
        $root_path = '/home/pi/PVControl+';
        
        if (is_dir($files_dir) && !empty($selected_files)) {
            // Crear backup de seguridad
            try {
                createPreRestoreBackup();
            } catch (Exception $e) {
                error_log("⚠️ Backup de seguridad falló: " . $e->getMessage());
            }
            
            // Restaurar solo archivos seleccionados
            restoreSelectedFiles($files_dir, $root_path, $selected_files);
        }
        
        // Restaurar tablas seleccionadas - NUEVA VERSIÓN
        if (is_dir($db_backup_dir) && !empty($selected_tables)) {
            restoreSelectedTablesSimple($db_backup_dir, $selected_tables);
        }
        
    } finally {
        // Limpiar directorio temporal
        deleteDirectory($temp_dir);
    }
}

/**
 * Restaura solo los archivos seleccionados
 */
function restoreSelectedFiles($source_dir, $destination_dir, $selected_files) {
    $restored_count = 0;
    
    foreach ($selected_files as $file_path) {
        $source_file = $source_dir . '/' . $file_path;
        $dest_file = $destination_dir . '/' . $file_path;
        
        if (file_exists($source_file)) {
            copyBackupFile($source_file, $dest_file);
            $restored_count++;
        }
    }
    
    error_log("📊 Archivos restaurados: $restored_count");
}

/**
 * Obtiene las tablas desde el directorio de database (para preview.php)
 */
function getTablesFromDatabaseDir($db_dir) {
    $tables = [];
    
    if (!is_dir($db_dir)) {
        return $tables;
    }
    
    $files = scandir($db_dir);
    
    foreach ($files as $file) {
        if ($file == '.' || $file == '..') continue;
        
        $file_path = $db_dir . '/' . $file;
        $file_extension = pathinfo($file, PATHINFO_EXTENSION);
        
        // Solo procesar archivos .sql
        if ($file_extension === 'sql' && is_file($file_path)) {
            $table_name = pathinfo($file, PATHINFO_FILENAME);
            $tables[] = $table_name;
            
            // Log para debugging
            error_log("📁 Tabla detectada en backup: $table_name");
        }
    }
    
    error_log("📊 Total de tablas detectadas: " . count($tables));
    return $tables;
}


?>