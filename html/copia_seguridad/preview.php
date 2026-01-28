<?php
// ==============================================
// INICIALIZACIÓN
// ==============================================
session_start();

// Manejo de errores
error_reporting(E_ALL);
ini_set('display_errors', 0); // Ocultar errores en producción

// Determinar si mostrar debug
$show_debug = isset($_GET['debug']) || isset($_SESSION['show_debug']);

try {
    require_once 'lib/database.php';
    require_once 'lib/gestion_copias.php';
    require_once 'lib/system_info.php';
    
    // Configurar zona horaria
    $system_timezone = setupSystemTimezone();

} catch (Exception $e) {
    error_log("❌ Error cargando librerías: " . $e->getMessage());
    $_SESSION['message'] = "❌ Error inicializando el sistema: " . $e->getMessage();
    $_SESSION['message_type'] = 'error';
    header('Location: index.php');
    exit;
}

// Función para formatear bytes
function formatBytes($bytes) {
    if ($bytes === 0) return '0 Bytes';
    $k = 1024;
    $sizes = ['Bytes', 'KB', 'MB', 'GB'];
    $i = floor(log($bytes) / log($k));
    return round($bytes / pow($k, $i), 2) . ' ' . $sizes[$i];
}

// ==============================================
// FUNCIONES AUXILIARES
// ==============================================

function listBackupFilesRecursive($dir, $relative_path = '') {
    $files = [];
    
    if (!is_dir($dir)) {
        return $files;
    }
    
    $items = scandir($dir);
    if ($items === false) {
        return $files;
    }
    
    foreach ($items as $item) {
        if ($item == '.' || $item == '..') continue;
        
        $full_path = $dir . '/' . $item;
        $current_relative_path = $relative_path ? $relative_path . '/' . $item : $item;
        
        if (is_dir($full_path)) {
            $sub_files = listBackupFilesRecursive($full_path, $current_relative_path);
            $files = array_merge($files, $sub_files);
        } else {
            $original_path = '/home/pi/PVControl+/' . $current_relative_path;
            $files[] = [
                'path' => $current_relative_path,
                'original_path' => $original_path,
                'size' => filesize($full_path),
                'exists' => file_exists($original_path)
            ];
        }
    }
    
    return $files;
}

function parseConfigFile($config_file) {
    $config = [];
    if (!file_exists($config_file)) {
        return $config;
    }
    
    $content = file_get_contents($config_file);
    if ($content === false) {
        return $config;
    }
    
    if (preg_match('/Fecha:\s*(.+)/', $content, $matches)) {
        $config['date'] = trim($matches[1]);
    }
    
    if (preg_match('/Archivos incluidos\s*\((\d+)\):/', $content, $matches)) {
        $config['file_count'] = intval($matches[1]);
    }
    
    if (preg_match('/Tablas incluidas\s*\((\d+)\):/', $content, $matches)) {
        $config['table_count'] = intval($matches[1]);
    }
    
    return $config;
}

// ==============================================
// PROCESAR RESTAURACIÓN CONFIRMADA
// ==============================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['restore_confirmed'])) {
    error_log("🔨 Procesando restauración confirmada");
    
    if (!isset($_SESSION['preview_data'])) {
        $_SESSION['message'] = "❌ Error: Sesión de previsualización expirada.";
        $_SESSION['message_type'] = 'error';
        header('Location: index.php');
        exit;
    }

    $preview_data = $_SESSION['preview_data'];
    $temp_zip = $preview_data['temp_zip'];
    
    $selected_files = $_POST['restore_files'] ?? [];
    $selected_tables = $_POST['restore_tables'] ?? [];
    
    try {
        if (empty($selected_files) && empty($selected_tables)) {
            throw new Exception("Debes seleccionar al menos un archivo o tabla");
        }
        
        restoreBackupWithSelection($temp_zip, $selected_files, $selected_tables);
        
        // Limpiar
        if (file_exists($temp_zip)) {
            unlink($temp_zip);
        }
        unset($_SESSION['preview_data']);
        
        $_SESSION['message'] = "✅ Restauración completada! " . 
                              count($selected_files) . " archivos y " . 
                              count($selected_tables) . " tablas restauradas.";
        $_SESSION['message_type'] = 'success';
        
        header('Location: index.php');
        exit;
        
    } catch (Exception $e) {
        error_log("❌ Error en restauración: " . $e->getMessage());
        
        if (isset($temp_zip) && file_exists($temp_zip)) {
            unlink($temp_zip);
        }
        unset($_SESSION['preview_data']);
        
        $_SESSION['message'] = "❌ Error en restauración: " . $e->getMessage();
        $_SESSION['message_type'] = 'error';
        header('Location: index.php');
        exit;
    }
}

// ==============================================
// PROCESAR SUBIDA DE ARCHIVO PARA PREVISUALIZACIÓN
// ==============================================
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['backup_file'])) {
    error_log("📤 Procesando subida de archivo");
    
    $uploaded_file = $_FILES['backup_file'];
    $temp_zip = null;
    $temp_dir = null;

    try {
        // Validaciones básicas
        if ($uploaded_file['error'] !== UPLOAD_ERR_OK) {
            throw new Exception("Error en la subida del archivo");
        }
        
        $file_extension = strtolower(pathinfo($uploaded_file['name'], PATHINFO_EXTENSION));
        if ($file_extension !== 'zip') {
            throw new Exception("Solo se permiten archivos ZIP");
        }

        // Mover archivo a temporal
        $temp_zip = sys_get_temp_dir() . '/preview_pvcontrol_' . uniqid() . '.zip';
        if (!move_uploaded_file($uploaded_file['tmp_name'], $temp_zip)) {
            throw new Exception("Error moviendo archivo temporal");
        }

        // Extraer ZIP
        $temp_dir = sys_get_temp_dir() . '/preview_' . uniqid();
        if (!mkdir($temp_dir, 0755, true)) {
            throw new Exception("No se pudo crear directorio temporal");
        }

        $zip = new ZipArchive();
        if ($zip->open($temp_zip) !== TRUE) {
            throw new Exception("El archivo ZIP está corrupto o no se puede leer");
        }
        
        if (!$zip->extractTo($temp_dir)) {
            throw new Exception("Error extrayendo archivo ZIP");
        }
        $zip->close();

        // Analizar contenido
        $backup_files = [];
        $files_dir = $temp_dir . '/files';
        if (is_dir($files_dir)) {
            $backup_files = listBackupFilesRecursive($files_dir, '');
        }

        // Verificar base de datos
        $backup_tables = [];
        $db_dir = $temp_dir . '/database';
        if (is_dir($db_dir)) {
            $backup_tables = getTablesFromDatabaseDir($db_dir);
        }

        // Leer configuración
        $backup_info = [
            'date' => date('Y-m-d H:i:s', filemtime($temp_zip)),
            'file_count' => count($backup_files),
            'table_count' => count($backup_tables),
            'filename' => $uploaded_file['name'],
            'size' => $uploaded_file['size']
        ];
        
        $config_file = $temp_dir . '/backup_config.txt';
        if (file_exists($config_file)) {
            $backup_info = array_merge($backup_info, parseConfigFile($config_file));
        }

        // Guardar en sesión
        $_SESSION['preview_data'] = [
            'temp_zip' => $temp_zip,
            'files' => $backup_files,
            'tables' => $backup_tables,
            'info' => $backup_info
        ];
        
        // Limpiar directorio temporal
        if ($temp_dir && is_dir($temp_dir)) {
            deleteDirectory($temp_dir);
        }
        
        // Redirigir a sí mismo
        header('Location: preview.php');
        exit;

    } catch (Exception $e) {
        error_log("❌ Error en previsualización: " . $e->getMessage());
        
        // Limpiar
        if ($temp_zip && file_exists($temp_zip)) {
            unlink($temp_zip);
        }
        if ($temp_dir && is_dir($temp_dir)) {
            deleteDirectory($temp_dir);
        }
        
        $_SESSION['message'] = "❌ Error en previsualización: " . $e->getMessage();
        $_SESSION['message_type'] = 'error';
        header('Location: index.php');
        exit;
    }
}

// ==============================================
// MOSTRAR PREVISUALIZACIÓN
// ==============================================
if (!isset($_SESSION['preview_data'])) {
    $_SESSION['message'] = "❌ No hay datos de previsualización. Sube un archivo primero.";
    $_SESSION['message_type'] = 'error';
    header('Location: index.php');
    exit;
}

$preview_data = $_SESSION['preview_data'];
$backup_files = $preview_data['files'];
$backup_tables = $preview_data['tables'];
$backup_info = $preview_data['info'];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Previsualizar Backup - PVControl+</title>
    <link rel="stylesheet" href="assets/style.css">
    <style>
        .debug-panel {
            background: #f8f9fa;
            border: 2px solid #dc3545;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            font-family: monospace;
            font-size: 12px;
            display: <?php echo $show_debug ? 'block' : 'none'; ?>;
        }
        .debug-title {
            color: #dc3545;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .debug-line {
            margin: 5px 0;
            padding: 3px;
            border-bottom: 1px solid #eee;
        }
        .debug-toggle {
            background: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11px;
            margin: 5px 0;
        }
        .debug-toggle:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Panel de Debug (oculto por defecto) -->
        <div class="debug-panel" id="debugPanel">
            <div class="debug-title">🐛 DEBUG PANEL</div>
            <div class="debug-line"><strong>Método HTTP:</strong> <?php echo $_SERVER['REQUEST_METHOD']; ?></div>
            <div class="debug-line"><strong>Session ID:</strong> <?php echo session_id(); ?></div>
            <div class="debug-line"><strong>¿Preview data?:</strong> <?php echo isset($_SESSION['preview_data']) ? 'SÍ' : 'NO'; ?></div>
            <div class="debug-line"><strong>Archivos en sesión:</strong> <?php echo count($backup_files); ?></div>
            <div class="debug-line"><strong>Tablas en sesión:</strong> <?php echo count($backup_tables); ?></div>
            <div class="debug-line"><strong>Nombre archivo:</strong> <?php echo htmlspecialchars($backup_info['filename']); ?></div>
            <div class="debug-line"><strong>Tamaño archivo:</strong> <?php echo $backup_info['size']; ?> bytes</div>
            <div class="debug-line"><a href="?debug=1" style="color: #dc3545;">🔗 Enlace permanente debug</a></div>
        </div>

        <div class="header">
            <h1>👁️ Previsualizar Backup</h1>
            <p>Selecciona qué elementos quieres restaurar</p>
            
            <!-- Botón para mostrar/ocultar debug -->
            <button type="button" class="debug-toggle" onclick="toggleDebug()">
                🐛 <?php echo $show_debug ? 'Ocultar' : 'Mostrar'; ?> Debug
            </button>
            
            <a href="index.php" class="btn-small" style="margin-left: 10px;">
                ← Volver
            </a>
        </div>
        
        <div class="content">
            <!-- Información del Backup -->
            <div class="card">
                <h2>📋 Información del Backup</h2>
                <div class="backup-meta">
                    <p><strong>Archivo:</strong> <?php echo htmlspecialchars($backup_info['filename']); ?></p>
                    <p><strong>Tamaño:</strong> <?php echo formatBytes($backup_info['size']); ?></p>
                    <p><strong>Fecha del backup:</strong> <?php echo htmlspecialchars($backup_info['date']); ?></p>
                    <p><strong>Archivos detectados:</strong> <?php echo count($backup_files); ?></p>
                    <p><strong>Tablas detectadas:</strong> <?php echo count($backup_tables); ?></p>
                </div>
            </div>

            <form action="preview.php" method="post" id="restoreSelectionForm">
                <input type="hidden" name="restore_confirmed" value="1">
                
                <!-- Selección de Archivos -->
                <?php if (!empty($backup_files)): ?>
                <div class="card">
                    <h3>📁 Archivos en el Backup (<?php echo count($backup_files); ?>)</h3>
                    <div class="selection-actions">
                        <button type="button" class="btn-small" onclick="selectAll('files')">Seleccionar Todos</button>
                        <button type="button" class="btn-small" onclick="deselectAll('files')">Deseleccionar Todos</button>
                    </div>
                    <div class="preview-container">
                        <?php foreach ($backup_files as $file): ?>
                        <label class="checkbox-item file-item <?php echo !$file['exists'] ? 'new-file' : ''; ?>">
                            <input type="checkbox" name="restore_files[]" value="<?php echo htmlspecialchars($file['path']); ?>" checked>
                            <span class="checkmark"></span>
                            <span class="file-info">
                                <span class="file-path"><?php echo htmlspecialchars($file['path']); ?></span>
                                <span class="file-size">(<?php echo formatBytes($file['size']); ?>)</span>
                                <?php if (!$file['exists']): ?>
                                <span class="file-status new">NUEVO</span>
                                <?php else: ?>
                                <span class="file-status exists">EXISTE</span>
                                <?php endif; ?>
                            </span>
                        </label>
                        <?php endforeach; ?>
                    </div>
                </div>
                <?php else: ?>
                <div class="card">
                    <h3>📁 Archivos en el Backup</h3>
                    <p class="no-data">No se encontraron archivos en el backup</p>
                </div>
                <?php endif; ?>

                <!-- Selección de Tablas -->
                <?php if (!empty($backup_tables)): ?>
                <div class="card">
                    <h3>🗄️ Tablas en el Backup (<?php echo count($backup_tables); ?>)</h3>
                    <div class="selection-actions">
                        <button type="button" class="btn-small" onclick="selectAll('tables')">Seleccionar Todos</button>
                        <button type="button" class="btn-small" onclick="deselectAll('tables')">Deseleccionar Todos</button>
                    </div>
                    <div class="preview-container">
                        <?php foreach ($backup_tables as $table): ?>
                        <label class="checkbox-item">
                            <input type="checkbox" name="restore_tables[]" value="<?php echo htmlspecialchars($table); ?>" checked>
                            <span class="checkmark"></span>
                            <?php echo htmlspecialchars($table); ?>
                        </label>
                        <?php endforeach; ?>
                    </div>
                </div>
                <?php else: ?>
                <div class="card">
                    <h3>🗄️ Tablas en el Backup</h3>
                    <p class="no-data">No se encontraron tablas en el backup</p>
                </div>
                <?php endif; ?>

                <!-- Botones fijos -->
                <div class="sticky-actions">
                    <div class="form-actions">
                        <button type="submit" class="btn btn-restore">⚡ Confirmar y Restaurar</button>
                        <a href="index.php" class="btn btn-cancel">← Cancelar</a>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <script>
    function selectAll(type) {
        document.querySelectorAll(`input[name="restore_${type}[]"]`).forEach(cb => cb.checked = true);
    }

    function deselectAll(type) {
        document.querySelectorAll(`input[name="restore_${type}[]"]`).forEach(cb => cb.checked = false);
    }

    function toggleDebug() {
        const panel = document.getElementById('debugPanel');
        const isVisible = panel.style.display === 'block';
        panel.style.display = isVisible ? 'none' : 'block';
        
        // Actualizar texto del botón
        const button = document.querySelector('.debug-toggle');
        button.textContent = isVisible ? '🐛 Mostrar Debug' : '🐛 Ocultar Debug';
        
        // Guardar preferencia en URL
        const url = new URL(window.location);
        if (isVisible) {
            url.searchParams.delete('debug');
        } else {
            url.searchParams.set('debug', '1');
        }
        window.history.replaceState({}, '', url);
    }

    document.getElementById('restoreSelectionForm').addEventListener('submit', function(e) {
        const filesSelected = document.querySelectorAll('input[name="restore_files[]"]:checked').length;
        const tablesSelected = document.querySelectorAll('input[name="restore_tables[]"]:checked').length;
        
        if (filesSelected === 0 && tablesSelected === 0) {
            e.preventDefault();
            alert('Debes seleccionar al menos un archivo o tabla para restaurar.');
            return false;
        }
        
        return confirm('⚠️ ¿ESTÁS SEGURO DE QUERER RESTAURAR LOS ELEMENTOS SELECCIONADOS?\n\n' +
                     `Archivos: ${filesSelected}\n` +
                     `Tablas: ${tablesSelected}\n\n` +
                     'Los archivos existentes serán sobreescritos.\n\n' +
                     'Esta acción no se puede deshacer.');
    });
    </script>
</body>
</html>