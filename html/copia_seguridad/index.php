<?php
session_start();

// ==============================================
// LIMPIAR SESIÓN ANTERIOR AL CARGAR INDEX.PHP
// ==============================================
if (isset($_SESSION['preview_data'])) {
    if (isset($_SESSION['preview_data']['temp_zip']) && 
        file_exists($_SESSION['preview_data']['temp_zip'])) {
        @unlink($_SESSION['preview_data']['temp_zip']);
    }
    unset($_SESSION['preview_data']);
}

require_once 'lib/database.php';
require_once 'lib/gestion_copias.php';

// Configurar zona horaria del sistema
require_once 'lib/system_info.php';
$system_timezone = setupSystemTimezone();
$current_time = date('Y-m-d H:i:s T');
$current_date = date('d/m/Y');
$day_of_week = date('l');
$spanish_days = [
    'Monday' => 'Lunes',
    'Tuesday' => 'Martes',
    'Wednesday' => 'Miércoles',
    'Thursday' => 'Jueves',
    'Friday' => 'Viernes',
    'Saturday' => 'Sábado',
    'Sunday' => 'Domingo'
];
$day_name = $spanish_days[$day_of_week] ?? $day_of_week;

// Obtener lista de tablas disponibles
$all_tables = [];
try {
    $db = getDatabaseConnection();
    $result = $db->query("SHOW TABLES");
    while ($row = $result->fetch_array()) {
        $all_tables[] = $row[0];
    }
} catch (Exception $e) {
    $all_tables = ['diario', 'reles', 'reles_c', 'reles_h', 'condiciones', 'parametros'];
}

// Tablas seleccionadas por defecto
$default_tables = ['diario', 'reles', 'reles_c', 'reles_h', 'condiciones','parametros'];

// Archivos preferentes
$preferred_files = [
    'Parametros_FV.py',
    'html/Parametros_Web.js', 
    'html/version.inc',
    'html/configuracion_activa.txt',
    'html/configuraciones/'
];

// Obtener límites de PHP
$php_limits = [
    'upload_max' => ini_get('upload_max_filesize'),
    'post_max' => ini_get('post_max_size'),
    'memory_limit' => ini_get('memory_limit'),
    'max_execution_time' => ini_get('max_execution_time')
];

// Convertir límites a MB para comparación
function toMB($valor) {
    $valor = trim($valor);
    $num = (float) $valor;
    $unit = strtoupper(substr($valor, -1));
    
    switch ($unit) {
        case 'G': return $num * 1024;
        case 'M': return $num;
        case 'K': return $num / 1024;
        default: return $num / (1024 * 1024); // asumir bytes
    }
}

$upload_max_mb = toMB($php_limits['upload_max']);
$post_max_mb = toMB($php_limits['post_max']);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Backup - PVControl+</title>
    <link rel="stylesheet" href="assets/style.css">
    <style>
        .tabs { display: flex; border-bottom: 2px solid #e0e0e0; margin-bottom: 20px; background: #f8f9fa; border-radius: 8px 8px 0 0; }
        .tab { padding: 15px 30px; cursor: pointer; border: none; background: transparent; font-size: 16px; font-weight: 500; color: #666; 
               transition: all 0.3s ease; border-bottom: 3px solid transparent; display: flex; align-items: center; gap: 8px; }
        .tab:hover { background: #e9ecef; color: #333; }
        .tab.active { color: #007bff; border-bottom-color: #007bff; background: #fff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .tab-icon { font-size: 18px; }
        
        .back-button { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: #6c757d; color: white; 
                      text-decoration: none; border-radius: 5px; font-weight: 500; transition: all 0.3s ease; border: none; 
                      cursor: pointer; margin-bottom: 20px; }
        .back-button:hover { background: #5a6268; transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.2); color: white; text-decoration: none; }
        
        .header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
        .page-title { flex-grow: 1; }
        
        @media (max-width: 768px) {
            .header-actions { flex-direction: column; align-items: flex-start; }
            .back-button { align-self: flex-start; }
        }
        
        .php-limits-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 12px 15px;
            margin: 15px 0;
            font-size: 14px;
        }
        .php-limits-info h4 { margin-top: 0; margin-bottom: 8px; color: #495057; }
        .limits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .limit-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; }
        .limit-label { font-weight: 500; color: #6c757d; }
        .limit-value { font-weight: 600; color: #28a745; }
        .limit-warning { color: #dc3545; font-size: 12px; margin-top: 5px; }
        
        .debug-panel {
            background: #f8f9fa;
            border: 1px solid #dc3545;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            display: none;
            font-family: monospace;
            font-size: 12px;
        }
        .debug-panel.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-top">
                <div class="header-brand">
                    <div class="logo">🔄</div>
                    <div class="brand-text">
                        <h1>Sistema de Backup PVControl+</h1>
                        <p>Gestión de copias de seguridad</p>
                    </div>
                </div>
                <div class="header-time">
                    <div class="time-display">
                        <div class="time-main"><?php echo date('H:i:s'); ?></div>
                        <div class="time-details">
                            <span class="date"><?php echo $day_name . ', ' . $current_date; ?></span>
                            <span class="timezone"><?php echo $system_timezone; ?></span>
                        </div>
                    </div>
                    <div class="time-icon">⏰</div>
                </div>
            </div>
            
            <div class="system-status">
                <div class="status-item">
                    <span class="status-icon">🖥️</span>
                    <span class="status-label">Servidor:</span>
                    <span class="status-value"><?php echo htmlspecialchars(gethostname()); ?></span>
                </div>
                <div class="status-item">
                    <span class="status-icon">🌐</span>
                    <span class="status-label">Zona Horaria:</span>
                    <span class="status-value"><?php echo htmlspecialchars($system_timezone); ?></span>
                </div>
                <div class="status-item">
                    <span class="status-icon">📅</span>
                    <span class="status-label">Última Actualización:</span>
                    <span class="status-value" id="live-time"><?php echo $current_time; ?></span>
                </div>
            </div>
        </div>

        <div class="content">
            <?php if (isset($_SESSION['message'])): ?>
                <div class="alert alert-<?php echo $_SESSION['message_type']; ?>">
                    <?php 
                    echo $_SESSION['message']; 
                    unset($_SESSION['message']);
                    unset($_SESSION['message_type']);
                    ?>
                </div>
            <?php endif; ?>

            <div class="header-actions">
                <div class="page-title">
                    <h2>Gestión de Copias de Seguridad</h2>
                    <p>Realiza backups de ficheros y tablas de Base de datos y restaura desde copias anteriores</p>
                </div>
                <a href="/" class="back-button">
                    <span>←</span>
                    Volver al Menú Principal
                </a>
            </div>

            <!-- Información de límites PHP -->
            <div class="php-limits-info">
                <h4>📊 Límites del Sistema PHP</h4>
                <div class="limits-grid">
                    <div class="limit-item">
                        <span class="limit-label">Máximo archivo:</span>
                        <span class="limit-value"><?php echo $php_limits['upload_max']; ?></span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Máximo POST:</span>
                        <span class="limit-value"><?php echo $php_limits['post_max']; ?></span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Memoria PHP:</span>
                        <span class="limit-value"><?php echo $php_limits['memory_limit']; ?></span>
                    </div>
                    <div class="limit-item">
                        <span class="limit-label">Tiempo ejecución:</span>
                        <span class="limit-value"><?php echo $php_limits['max_execution_time']; ?>s</span>
                    </div>
                </div>
                <?php if ($upload_max_mb < 50): ?>
                <div class="limit-warning">
                    ⚠️ Límite bajo. Para backups grandes (>50MB) aumentar en php.ini:<br>
                    <code>upload_max_filesize = 200M</code> y <code>post_max_size = 210M</code>
                </div>
                <?php endif; ?>
                <button type="button" class="btn-small" onclick="toggleDebug()" style="margin-top: 10px;">
                    🐛 Mostrar Debug
                </button>
            </div>

            <!-- Panel de Debug (oculto) -->
            <div class="debug-panel" id="debugPanel">
                <h4>🐛 Información de Debug</h4>
                <p><strong>Session ID:</strong> <?php echo session_id(); ?></p>
                <p><strong>PHP Version:</strong> <?php echo phpversion(); ?></p>
                <p><strong>upload_max_filesize bytes:</strong> <?php echo $upload_max_mb; ?> MB</p>
                <p><strong>post_max_size bytes:</strong> <?php echo $post_max_mb; ?> MB</p>
                <p><strong>memory_limit bytes:</strong> <?php echo toMB($php_limits['memory_limit']); ?> MB</p>
                <p><strong>Recomendado práctico:</strong> <?php echo floor(min($upload_max_mb, $post_max_mb) * 0.9); ?> MB (90% del límite)</p>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="switchTab('backup')">
                    <span class="tab-icon">📦</span>
                    Copia de Seguridad
                </button>
                <button class="tab" onclick="switchTab('restore')">
                    <span class="tab-icon">🔄</span>
                    Restauración
                </button>
            </div>

            <!-- Pestaña de Copia de Seguridad -->
            <div id="backup-tab" class="tab-content active">
                <div class="card">
                    <h2>📦 Crear Nuevo Backup</h2>
                    <p>Selecciona los archivos y tablas que quieres incluir en el backup:</p>
                    
                    <form id="backupForm" action="copia.php" method="post">
                        <!-- ... (mantener todo el contenido original del formulario de backup) ... -->
                        <!-- Selección de Archivos Preferentes -->
                        <div class="selection-section">
                            <h3>⭐ Archivos Importantes (Recomendados)</h3>
                            <div class="selection-actions">
                                <button type="button" class="btn-small" onclick="selectAllPreferred()">Seleccionar Todos</button>
                                <button type="button" class="btn-small" onclick="deselectAllPreferred()">Deseleccionar Todos</button>
                            </div>
                            <div class="file-selection preferred-selection">
                                <?php foreach ($preferred_files as $file): ?>
                                <label class="checkbox-item preferred-item">
                                    <input type="checkbox" name="preferred_files[]" value="<?php echo htmlspecialchars($file); ?>" checked>
                                    <span class="checkmark"></span>
                                    <span class="file-info">
                                        <span class="file-path"><?php echo htmlspecialchars($file); ?></span>
                                        <?php 
                                        $full_path = '/home/pi/PVControl+/' . $file;
                                        if (is_dir($full_path)): 
                                        ?>
                                        <span class="file-badge folder">📁 Carpeta</span>
                                        <?php else: ?>
                                        <span class="file-badge file">📄 Archivo</span>
                                        <?php endif; ?>
                                    </span>
                                </label>
                                <?php endforeach; ?>
                            </div>
                        </div>

                        <!-- Explorador de Archivos Adicionales -->
                        <div class="selection-section">
                            <h3>🔍 Añadir Más Archivos/Carpetas</h3>
                            <p>Explora y selecciona archivos adicionales del sistema:</p>
                            
                            <div class="file-explorer-controls">
                                <button type="button" class="btn-small" onclick="selectAllVisible()">Seleccionar Visibles</button>
                                <button type="button" class="btn-small" onclick="deselectAllAdditional()">Deseleccionar Todos</button>
                                <button type="button" class="btn-small" onclick="refreshFileList()">🔄 Actualizar</button>
                                <div class="current-path">
                                    <strong>Ruta actual:</strong> 
                                    <span id="currentPath">/home/pi/PVControl+/</span>
                                </div>
                            </div>

                            <div class="breadcrumb" id="breadcrumb">
                                <button type="button" class="breadcrumb-item" onclick="navigateTo('/home/pi/PVControl+/')">PVControl+</button>
                            </div>

                            <div class="file-explorer" id="fileExplorer">
                                <div class="explorer-loading" id="explorerLoading">
                                    <div class="spinner small"></div>
                                    Cargando archivos...
                                </div>
                                <div class="file-list" id="fileList"></div>
                            </div>

                            <div class="selected-additional-section">
                                <h4>📋 Archivos Adicionales Seleccionados (<span id="additionalCount">0</span>)</h4>
                                <div class="selected-additional-list" id="selectedAdditionalList">
                                    <div class="empty-state">No hay archivos adicionales seleccionados</div>
                                </div>
                            </div>
                        </div>

                        <!-- Selección de Tablas -->
                        <div class="selection-section">
                            <h3>🗄️ Tablas de Base de Datos</h3>
                            <div class="selection-actions">
                                <button type="button" class="btn-small" onclick="selectAllTables()">Seleccionar Todos</button>
                                <button type="button" class="btn-small" onclick="deselectAllTables()">Deseleccionar Todos</button>
                            </div>
                            <div class="table-selection">
                                <?php foreach ($all_tables as $table): ?>
                                <label class="checkbox-item">
                                    <input type="checkbox" name="tables[]" value="<?php echo htmlspecialchars($table); ?>" 
                                        <?php echo in_array($table, $default_tables) ? 'checked' : ''; ?>>
                                    <span class="checkmark"></span>
                                    <?php echo htmlspecialchars($table); ?>
                                </label>
                                <?php endforeach; ?>
                            </div>
                        </div>

                        <!-- Nombre personalizado -->
                        <div class="selection-section">
                            <h3>📝 Nombre del Archivo de Backup</h3>
                            <div class="file-naming">
                                <label for="backup_name" class="file-label">Nombre personalizado (opcional):</label>
                                <input type="text" name="backup_name" id="backup_name" placeholder="Ej: backup_octubre_2024" maxlength="100" pattern="[a-zA-Z0-9_-]+" title="Solo letras, números, guiones y guiones bajos">
                                <div class="naming-help"><small>Se usarán solo letras, números, guiones y guiones bajos. Se añadirá automáticamente la fecha.</small></div>
                                <div class="filename-preview">
                                    <strong>Vista previa:</strong> 
                                    <span id="filenamePreview">backup_pvcontrol_<?php echo date('Y-m-d_His'); ?>.zip</span>
                                </div>
                            </div>
                        </div>

                        <!-- Resumen -->
                        <div class="selection-summary">
                            <h3>📊 Resumen de la Selección</h3>
                            <div class="summary-stats">
                                <div class="stat-item">
                                    <span class="stat-label">Archivos preferentes:</span>
                                    <span class="stat-value" id="preferredCount"><?php echo count($preferred_files); ?></span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Archivos adicionales:</span>
                                    <span class="stat-value" id="additionalTotalCount">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Tablas de BD:</span>
                                    <span class="stat-value" id="tableCount"><?php echo count($default_tables); ?></span>
                                </div>
                                <div class="stat-item total">
                                    <span class="stat-label">Total elementos:</span>
                                    <span class="stat-value" id="totalCount"><?php echo count($preferred_files) + count($default_tables); ?></span>
                                </div>
                            </div>
                        </div>

                        <!-- Loading -->
                        <div class="loading" id="loadingBackup">
                            <div class="spinner"></div>
                            <p>Generando backup, por favor espera...</p>
                            <div id="progressInfo">
                                <div class="progress-text">Preparando backup...</div>
                                <div class="progress-time" id="elapsedTime">Tiempo transcurrido: 0s</div>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn" id="backupBtn">
                            📥 Crear y Descargar Backup
                        </button>
                        
                        <div id="additionalFilesHidden"></div>
                    </form>
                </div>
            </div>

            <!-- Pestaña de Restauración -->
            <div id="restore-tab" class="tab-content">
                <div class="card">
                    <h2>🔄 Restaurar Sistema</h2>
                    <p>Sube un archivo ZIP de backup para previsualizar y seleccionar qué elementos restaurar:</p>
                    
                    <form action="preview.php" method="post" enctype="multipart/form-data" id="restoreForm">
                        <div class="file-input-container">
                            <label for="backup_file" class="file-label">
                                📁 Seleccionar archivo ZIP de backup
                                <span id="sizeWarning" style="color: red; display: none; font-size: 12px;"></span>
                            </label>
                            <input type="file" name="backup_file" id="backup_file" accept=".zip" required>
                            <div id="file-name" class="file-name-display">Ningún archivo seleccionado</div>
                            <div style="font-size: 12px; color: #666; margin-top: 5px;">
                                <strong>Límite máximo:</strong> <?php echo $php_limits['upload_max']; ?> 
                                (<?php echo floor(min($upload_max_mb, $post_max_mb) * 0.9); ?>MB recomendado práctico)
                            </div>
                        </div>

                        <div class="form-actions">
                            <button type="submit" class="btn btn-preview" id="previewBtn" disabled>
                                👁️ Previsualizar y Restaurar
                            </button>
                        </div>
                        
                        <div class="restore-notice">
                            <p>⚠️ <strong>Proceso seguro:</strong> Siempre verificarás el contenido del backup antes de restaurar.</p>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Información del Sistema -->
            <div class="backup-info">
                <h3>📋 Información del Sistema</h3>
                <p><strong>Total de tablas en la base de datos:</strong> <?php echo count($all_tables); ?></p>
                <p><strong>Tablas seleccionadas por defecto:</strong> <?php echo count($default_tables); ?></p>
                <p><strong>Archivos preferentes disponibles:</strong> <?php echo count($preferred_files); ?></p>
            </div>
        </div>
    </div>

    <script src="assets/script.js"></script>
    <script>
        // Función para cambiar pestañas
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(button => button.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.currentTarget.classList.add('active');
        }
        
        // Toggle debug panel
        function toggleDebug() {
            const panel = document.getElementById('debugPanel');
            panel.classList.toggle('active');
        }
        
        // Manejo del formulario de restauración
        document.addEventListener('DOMContentLoaded', function() {
            const fileInput = document.getElementById('backup_file');
            const previewBtn = document.getElementById('previewBtn');
            const fileNameDisplay = document.getElementById('file-name');
            const sizeWarning = document.getElementById('sizeWarning');
            
            // Límites de PHP desde variables PHP
            const phpLimits = {
                uploadMaxMB: <?php echo $upload_max_mb; ?>,
                postMaxMB: <?php echo $post_max_mb; ?>,
                uploadMax: '<?php echo $php_limits['upload_max']; ?>',
                postMax: '<?php echo $php_limits['post_max']; ?>'
            };
            
            // Convertir tamaño humano a MB
            function humanToMB(sizeStr) {
                const match = sizeStr.match(/(\d+(\.\d+)?)\s*([KMG])?B?/i);
                if (!match) return 0;
                
                const num = parseFloat(match[1]);
                const unit = match[3] ? match[3].toUpperCase() : '';
                
                switch(unit) {
                    case 'G': return num * 1024;
                    case 'M': return num;
                    case 'K': return num / 1024;
                    default: return num / (1024 * 1024); // bytes
                }
            }
            
            // Verificar tamaño de archivo
            function checkFileSize(file) {
                const fileMB = file.size / 1024 / 1024;
                const maxAllowed = Math.min(phpLimits.uploadMaxMB, phpLimits.postMaxMB) * 0.9; // 90% margen seguro
                
                if (fileMB > phpLimits.uploadMaxMB) {
                    return {
                        valid: false,
                        message: `❌ El archivo (${fileMB.toFixed(2)}MB) excede el límite máximo (${phpLimits.uploadMax})`
                    };
                }
                
                if (fileMB > maxAllowed) {
                    return {
                        valid: false,
                        message: `⚠️ El archivo (${fileMB.toFixed(2)}MB) está cerca del límite. Máximo recomendado: ${maxAllowed.toFixed(2)}MB`
                    };
                }
                
                return { valid: true };
            }
            
            // Evento change en input file
            if (fileInput && previewBtn) {
                fileInput.addEventListener('change', function() {
                    if (this.files && this.files.length > 0) {
                        const file = this.files[0];
                        const validation = checkFileSize(file);
                        
                        if (validation.valid) {
                            previewBtn.disabled = false;
                            const sizeMB = (file.size / 1024 / 1024).toFixed(2);
                            fileNameDisplay.textContent = `📄 ${file.name} (${sizeMB} MB)`;
                            fileNameDisplay.style.color = 'green';
                            sizeWarning.style.display = 'none';
                        } else {
                            previewBtn.disabled = true;
                            fileNameDisplay.textContent = `❌ ${file.name}`;
                            fileNameDisplay.style.color = 'red';
                            sizeWarning.textContent = validation.message;
                            sizeWarning.style.display = 'block';
                        }
                    } else {
                        previewBtn.disabled = true;
                        fileNameDisplay.textContent = 'Ningún archivo seleccionado';
                        fileNameDisplay.style.color = 'inherit';
                        sizeWarning.style.display = 'none';
                    }
                });
                
                // Validar formulario antes de enviar
                const restoreForm = document.getElementById('restoreForm');
                if (restoreForm) {
                    restoreForm.addEventListener('submit', function(e) {
                        if (!fileInput.files || fileInput.files.length === 0) {
                            e.preventDefault();
                            alert('❌ Por favor, selecciona un archivo ZIP primero');
                            return false;
                        }
                        
                        const file = fileInput.files[0];
                        const validation = checkFileSize(file);
                        if (!validation.valid) {
                            e.preventDefault();
                            alert(validation.message);
                            return false;
                        }
                        
                        // Mostrar loading
                        previewBtn.disabled = true;
                        previewBtn.innerHTML = '⏳ Procesando...';
                        
                        return true;
                    });
                }
            }
        });
    </script>
</body>
</html>