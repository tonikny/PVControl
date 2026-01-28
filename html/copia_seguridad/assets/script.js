// ? Variables globales para el explorador
let currentExplorerPath = '/home/pi/PVControl+/';
let additionalFiles = new Set();

document.addEventListener('DOMContentLoaded', function() {
    console.log('? Inicializando sistema de backup...');
    
    // =============================================================================
    // 1. MANEJO DE ARCHIVOS DE BACKUP (RESTAURACION)
    // =============================================================================
    const fileInput = document.getElementById('backup_file');
    const fileNameDisplay = document.getElementById('file-name');
    const previewBtnElement = document.getElementById('previewBtn');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2);
                fileNameDisplay.textContent = ` ${fileName} (${fileSize} MB)`;
                fileNameDisplay.className = 'file-name-display has-file';
                
                if (previewBtnElement) {
                    previewBtnElement.disabled = false;
                }
            } else {
                fileNameDisplay.textContent = 'Ningun archivo seleccionado';
                fileNameDisplay.className = 'file-name-display';
                
                if (previewBtnElement) {
                    previewBtnElement.disabled = true;
                }
            }
        });
    }

    // =============================================================================
    // 2. INICIALIZAR EXPLORADOR Y CONTADORES
    // =============================================================================
    loadFileList();
    updateSelectionCounters(); // ? Actualizar contadores al cargar
    
    // ? ESCUCHAR CAMBIOS EN ARCHIVOS PREFERENTES
    const preferredCheckboxes = document.querySelectorAll('input[name="preferred_files[]"]');
    preferredCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionCounters);
    });
    
    // ? ESCUCHAR CAMBIOS EN TABLAS - ESTO ES LO QUE FALTABA
    const tableCheckboxes = document.querySelectorAll('input[name="tables[]"]');
    tableCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionCounters);
    });

    // =============================================================================
    // 3. MANEJO DEL FORMULARIO DE BACKUP
    // =============================================================================
    const backupForm = document.getElementById('backupForm');
    if (backupForm) {
        backupForm.addEventListener('submit', function(e) {
            // ? VALIDACION CORREGIDA
            const preferredFilesSelected = document.querySelectorAll('input[name="preferred_files[]"]:checked').length;
            const additionalFilesSelected = additionalFiles.size;
            const tablesSelected = document.querySelectorAll('input[name="tables[]"]:checked').length;
            const totalSelected = preferredFilesSelected + additionalFilesSelected + tablesSelected;
            
            console.log(`Validacion: Preferentes=${preferredFilesSelected}, Adicionales=${additionalFilesSelected}, Tablas=${tablesSelected}, Total=${totalSelected}`);
            
            if (totalSelected === 0) {
                e.preventDefault();
                alert('Debes seleccionar al menos un archivo o tabla para el backup.');
                return false;
            }
            
            // ? Anadir archivos adicionales al formulario
            additionalFiles.forEach(filePath => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'additional_files[]';
                input.value = filePath;
                backupForm.appendChild(input);
            });
            
            // Mostrar loading
            const loadingElement = document.getElementById('loadingBackup');
            const backupBtn = document.getElementById('backupBtn');
            
            if (loadingElement && backupBtn) {
                loadingElement.style.display = 'block';
                backupBtn.disabled = true;
                backupBtn.innerHTML = ' Generando...';
                
                const progressText = document.querySelector('.progress-text');
                const elapsedTime = document.getElementById('elapsedTime');
                
                let seconds = 0;
                const timer = setInterval(() => {
                    seconds++;
                    
                    if (elapsedTime) {
                        elapsedTime.textContent = `Tiempo transcurrido: ${seconds}s`;
                    }
                    
                    if (progressText) {
                        if (seconds < 10) {
                            progressText.textContent = 'Preparando backup...';
                        } else if (seconds < 30) {
                            progressText.textContent = 'Exportando base de datos...';
                        } else if (seconds < 60) {
                            progressText.textContent = 'Comprimiendo archivos...';
                        } else {
                            progressText.textContent = 'Procesando archivos grandes, por favor espere...';
                        }
                    }
                }, 1000);
                
                backupBtn.dataset.timer = timer;
            }
            
            return true;
        });
    }
    
    // =============================================================================
    // 4. BOTON DE PREVISUALIZACION
    // =============================================================================
    const previewButton = document.getElementById('previewBtn');
    if (previewButton) {
        previewButton.addEventListener('click', function(e) {
            e.preventDefault();
            const fileInputElement = document.getElementById('backup_file');
            
            if (!fileInputElement.files.length) {
                alert('Por favor, selecciona un archivo ZIP de backup primero.');
                return;
            }
            
            const tempForm = document.createElement('form');
            tempForm.method = 'post';
            tempForm.action = 'preview.php';
            tempForm.enctype = 'multipart/form-data';
            tempForm.style.display = 'none';
            
            const tempInput = document.createElement('input');
            tempInput.type = 'file';
            tempInput.name = 'backup_file';
            
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(fileInputElement.files[0]);
            tempInput.files = dataTransfer.files;
            
            tempForm.appendChild(tempInput);
            document.body.appendChild(tempForm);
            tempForm.submit();
        });
    }
    
    // =============================================================================
    // 5. CONFIRMACIONES DE RESTAURACION
    // =============================================================================
    const restoreForm = document.getElementById('restoreForm');
    if (restoreForm) {
        restoreForm.addEventListener('submit', function(e) {
            const fileInputRestore = document.getElementById('backup_file');
            if (!fileInputRestore.files.length) {
                e.preventDefault();
                alert('Por favor, selecciona un archivo ZIP de backup primero.');
                return false;
            }
            
            return confirm(' ESTAS SEGURO DE QUERER RESTAURAR ESTE BACKUP?\n\nEsta accion sobreescribira archivos y datos de la base de datos.\n\nRecomendamos usar la previsualizacion primero.');
        });
    }
    
    const restoreSelectionForm = document.getElementById('restoreSelectionForm');
    if (restoreSelectionForm) {
        restoreSelectionForm.addEventListener('submit', function(e) {
            const filesSelected = document.querySelectorAll('input[name="restore_files[]"]:checked').length;
            const tablesSelected = document.querySelectorAll('input[name="restore_tables[]"]:checked').length;
            
            if (filesSelected === 0 && tablesSelected === 0) {
                e.preventDefault();
                alert('Debes seleccionar al menos un archivo o tabla para restaurar.');
                return false;
            }
            
            let message = ' ESTAS SEGURO DE QUERER RESTAURAR LOS ELEMENTOS SELECCIONADOS?\n\n';
            message += `Archivos a restaurar: ${filesSelected}\n`;
            message += `Tablas a restaurar: ${tablesSelected}\n\n`;
            message += 'Los archivos existentes seran sobreescritos.';
            
            return confirm(message);
        });
    }

    // =============================================================================
    // 6. VISTA PREVIA DEL NOMBRE DEL BACKUP
    // =============================================================================
    const nameInput = document.getElementById('backup_name');
    if (nameInput) {
        nameInput.addEventListener('input', updateFilenamePreview);
        nameInput.addEventListener('change', updateFilenamePreview);
        updateFilenamePreview();
    }

    // =============================================================================
    // 7. MONITOREO DE DESCARGAS
    // =============================================================================
    console.log(' Verificando estado de backup...');
    checkDownloadStatus();
    setInterval(checkDownloadStatus, 5000);
});

// Funciones para seleccion
function selectAllFiles() {
    const checkboxes = document.querySelectorAll('input[name="files[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

function deselectAllFiles() {
    const checkboxes = document.querySelectorAll('input[name="files[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

function selectAllTables() {
    const checkboxes = document.querySelectorAll('input[name="tables[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

function deselectAllTables() {
    const checkboxes = document.querySelectorAll('input[name="tables[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

// Funciones auxiliares para previsualizacion
function selectAll(type) {
    const checkboxes = document.querySelectorAll(`input[name="restore_${type}[]"]`);
    checkboxes.forEach(checkbox => checkbox.checked = true);
}

function deselectAll(type) {
    const checkboxes = document.querySelectorAll(`input[name="restore_${type}[]"]`);
    checkboxes.forEach(checkbox => checkbox.checked = false);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ? funcion para verificar si la descarga se completo
function checkDownloadStatus() {
    const backupBtn = document.getElementById('backupBtn');
    if (backupBtn && backupBtn.innerHTML.includes('Generando')) {
        console.log(' Backup en progreso, monitoreando...');
        
        // Verificar cada segundo durante 10 minutos maximo
        let checks = 0;
        const maxChecks = 600; // 10 minutos
        
        const checkInterval = setInterval(() => {
            checks++;
            
            // Si el boton sigue en estado "Generando" despues de mucho tiempo, resetear
            if (checks > 30 && backupBtn.innerHTML.includes('Generando')) {
                console.log(' Reset automatico tras espera prolongada');
                resetBackupButton();
                clearInterval(checkInterval);
            }
            
            // Limite maximo
            if (checks >= maxChecks) {
                console.log('? Limite de tiempo alcanzado, forzando reset');
                resetBackupButton();
                clearInterval(checkInterval);
            }
        }, 1000);
        
        // Guardar el intervalo para limpiarlo si es necesario
        backupBtn.dataset.checkInterval = checkInterval;
    }
}

// ? Funcion para resetear el boton
function resetBackupButton() {
    const backupBtn = document.getElementById('backupBtn');
    const loadingElement = document.getElementById('loadingBackup');
    
    if (backupBtn) {
        console.log(' Reseteando boton de backup');
        
        // Limpiar timers si existen
        if (backupBtn.dataset.timer) {
            clearInterval(parseInt(backupBtn.dataset.timer));
        }
        if (backupBtn.dataset.checkInterval) {
            clearInterval(parseInt(backupBtn.dataset.checkInterval));
        }
        
        // Cambiar a boton de regenerar
        backupBtn.disabled = false;
        backupBtn.innerHTML = 'Generar Nuevo Backup';
        backupBtn.classList.add('regenerate-btn');
        
        // Ocultar loading
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Anadir funcionalidad al nuevo boton
        backupBtn.onclick = function() {
            console.log(' Recargando pagina...');
            location.reload();
        };
        
        // Mostrar notificacion de exito
        showNotification('? Backup completado y descargado', 'success');
    }
}

// ? Mostrar notificacion
function showNotification(message, type) {
    // Evitar notificaciones duplicadas
    const existingNotification = document.querySelector('.notification-fixed');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-fixed`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    document.body.appendChild(notification);
    
    // Auto-eliminar despues de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// ? Funcion para actualizar la vista previa del nombre de archivo
function updateFilenamePreview() {
    const nameInput = document.getElementById('backup_name');
    const previewElement = document.getElementById('filenamePreview');
    
    if (nameInput && previewElement) {
        const customName = nameInput.value.trim();
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-').replace(' ', '_');
        
        let finalFilename;
        if (customName) {
            // Limpiar el nombre personalizado (solo letras, numeros, guiones y guiones bajos)
            const cleanName = customName.replace(/[^a-zA-Z0-9_-]/g, '_');
            finalFilename = `backup_${cleanName}_${timestamp}.zip`;
        } else {
            finalFilename = `backup_pvcontrol_${timestamp}.zip`;
        }
        
        previewElement.textContent = finalFilename;
    }
}


// ? Cargar lista de archivos
function loadFileList(path = null) {
    if (path) {
        currentExplorerPath = path;
    }
    
    const fileList = document.getElementById('fileList');
    const loading = document.getElementById('explorerLoading');
    const currentPath = document.getElementById('currentPath');
    
    if (fileList && loading && currentPath) {
        fileList.innerHTML = '';
        loading.style.display = 'flex';
        currentPath.textContent = currentExplorerPath;
        
        // Actualizar breadcrumb
        updateBreadcrumb();
        
        // Hacer peticion AJAX al servidor
        fetch('list_files.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'path=' + encodeURIComponent(currentExplorerPath)
        })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            
            if (data.success && data.items) {
                displayFileList(data.items);
            } else {
                fileList.innerHTML = '<div class="empty-state">Error cargando archivos</div>';
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            fileList.innerHTML = '<div class="empty-state">Error de conexion</div>';
            console.error('Error:', error);
        });
    }
}

// ? Mostrar lista de archivos en el DOM
function displayFileList(items) {
    const fileList = document.getElementById('fileList');
    if (!fileList) return;
    
    fileList.innerHTML = '';
    
    if (items.length === 0) {
        fileList.innerHTML = '<div class="empty-state">Directorio vacio</div>';
        return;
    }
    
    items.forEach(item => {
        const fileItem = createFileItem(item);
        fileList.appendChild(fileItem);
    });
}

//  Crear elemento de archivo MEJORADO
function createFileItem(item) {
    const div = document.createElement('div');
    const isSelected = additionalFiles.has(item.path);
    div.className = `file-item-explorer ${isSelected ? 'selected' : ''} ${item.is_dir ? 'is-directory' : 'is-file'}`;
    
    const size = item.is_dir ? '' : formatBytes(item.size);
    
    //  INDICADORES DE TEXTO EN LUGAR DE EMOJIS
    const typeBadge = item.is_dir ? 'CARPETA' : 'ARCHIVO';
    const selectionBadge = isSelected ? '<span class="file-selected-indicator">SELECCIONADO</span>' : '';
    
    div.innerHTML = `
        <span class="file-type-badge">${typeBadge}</span>
        <span class="file-name" title="${item.name}">${escapeHtml(item.name)}</span>
        <span class="file-size">${size}</span>
        ${!item.readable ? '<span class="file-permission-warning">SIN ACCESO</span>' : ''}
        ${selectionBadge}
    `;
    
    div.setAttribute('data-path', item.path);
    div.setAttribute('data-fullpath', item.full_path);
    div.setAttribute('data-isdir', item.is_dir);
    
    div.onclick = (e) => {
        e.stopPropagation();
        
        if (item.is_dir) {
            loadFileList(item.full_path);
        } else if (item.readable) {
            toggleAdditionalFileSelection(item);
        } else {
            alert('No tienes permisos para acceder a este archivo');
        }
    };
    
    return div;
}

// ? Toggle seleccion de archivo
function toggleAdditionalFileSelection(item) {
    if (!item.readable) {
        alert('No tienes permisos para leer este archivo');
        return;
    }
    
    if (additionalFiles.has(item.path)) {
        additionalFiles.delete(item.path);
    } else {
        additionalFiles.add(item.path);
    }
    
    updateAdditionalFilesList();
    updateSelectionCounters();
    
    // Actualizar estilos visuales
    const allItems = document.querySelectorAll('.file-item-explorer');
    allItems.forEach(el => {
        const path = el.getAttribute('data-path');
        if (path === item.path) {
            el.classList.toggle('selected', additionalFiles.has(item.path));
        }
    });
}

// ? Actualizar breadcrumb
function updateBreadcrumb() {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    // Obtener la ruta relativa desde PVControl+
    const basePath = '/home/pi/PVControl+/';
    let relativePath = currentExplorerPath.replace(basePath, '');
    
    // Si esta en la raiz de PVControl+
    if (relativePath === '' || relativePath === '/') {
        breadcrumb.innerHTML = '<span class="breadcrumb-current">PVControl+</span>';
        return;
    }
    
    // Dividir la ruta relativa
    const parts = relativePath.split('/').filter(p => p);
    
    let html = '';
    let accumulatedPath = basePath;
    
    // Siempre empezar con PVControl+ clickeable
    html += `<button type="button" class="breadcrumb-item" onclick="navigateTo('${basePath}')">PVControl+</button>`;
    
    // Construir el resto del breadcrumb
    parts.forEach((part, index) => {
        accumulatedPath += part + '/';
        
        if (index === parts.length - 1) {
            // Ultima parte - no clickeable
            html += `<span class="breadcrumb-separator">/</span><span class="breadcrumb-current">${part}</span>`;
        } else {
            // Partes intermedias - clickeables
            html += `<span class="breadcrumb-separator">/</span><button type="button" class="breadcrumb-item" onclick="navigateTo('${accumulatedPath}')">${part}</button>`;
        }
    });
    
    breadcrumb.innerHTML = html;
}


// ? Navegar a directorio
function navigateTo(path) {
    console.log(' Navegando a:', path);
    
    // Asegurar que la ruta termina con /
    if (!path.endsWith('/')) {
        path = path + '/';
    }
    
    // Verificar que es una ruta valida dentro de PVControl+
    const basePath = '/home/pi/PVControl+/';
    if (!path.startsWith(basePath)) {
        console.error('? Intento de navegar fuera de PVControl+:', path);
        return;
    }
    
    currentExplorerPath = path;
    loadFileList(path);
}

//  Refrescar lista
function refreshFileList() {
    loadFileList(currentExplorerPath);
}

//  Simular carga de archivos (REMPLAZAR con llamada real al servidor)
function simulateFileListLoad() {
    const fileList = document.getElementById('fileList');
    if (!fileList) return;
    
    // Ejemplo de datos - en produccion esto vendria del servidor
    const sampleFiles = [
        { name: 'configuraciones', is_dir: true, path: 'configuraciones/', size: 0 },
        { name: 'logs', is_dir: true, path: 'logs/', size: 0 },
        { name: 'Parametros_FV.py', is_dir: false, path: 'Parametros_FV.py', size: 1024 },
        { name: 'main.py', is_dir: false, path: 'main.py', size: 2048 }
    ];
    
    fileList.innerHTML = '';
    sampleFiles.forEach(item => {
        const fileItem = createFileItem(item);
        fileList.appendChild(fileItem);
    });
}

//  Funcion para escapar HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ? Actualizar contadores
function updateSelectionCounters() {
    try {
        // Archivos preferentes seleccionados
        const preferredCheckboxes = document.querySelectorAll('input[name="preferred_files[]"]:checked');
        const preferredCount = preferredCheckboxes.length;
        
        // Archivos adicionales seleccionados
        const additionalCount = additionalFiles.size;
        
        // Tablas seleccionadas - ? IMPORTANTE: Usar el selector correcto
        const tableCheckboxes = document.querySelectorAll('input[name="tables[]"]:checked');
        const tableCount = tableCheckboxes.length;
        
        // Total
        const totalCount = preferredCount + additionalCount + tableCount;
        
        console.log(` updateSelectionCounters: Preferentes=${preferredCount}, Adicionales=${additionalCount}, Tablas=${tableCount}, Total=${totalCount}`);
        
        // Actualizar DOM
        const elements = {
            'preferredCount': preferredCount,
            'additionalCount': additionalCount,
            'additionalTotalCount': additionalCount,
            'tableCount': tableCount,
            'totalCount': totalCount
        };
        
        for (const [id, value] of Object.entries(elements)) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            } else {
                console.warn(`? Elemento no encontrado: ${id}`);
            }
        }
        
    } catch (error) {
        console.error('? Error en updateSelectionCounters:', error);
    }
}

//  Seleccionar/deseleccionar archivo adicional
function toggleAdditionalFileSelection(item) {
    if (additionalFiles.has(item.path)) {
        additionalFiles.delete(item.path);
    } else {
        additionalFiles.add(item.path);
    }
    
    updateAdditionalFilesList();
    updateSelectionCounters();
    loadFileList(currentExplorerPath); // Recargar para actualizar estilos
}

//  Actualizar lista de archivos adicionales seleccionados
function updateAdditionalFilesList() {
    const container = document.getElementById('selectedAdditionalList');
    if (!container) {
        console.error('? No se encuentra el contenedor selectedAdditionalList');
        return;
    }
    
    if (additionalFiles.size === 0) {
        container.innerHTML = '<div class="empty-state">No hay archivos adicionales seleccionados</div>';
        return;
    }
    
    container.innerHTML = '';
    additionalFiles.forEach(filePath => {
        const item = document.createElement('div');
        item.className = 'selected-additional-item';
        item.innerHTML = `
            <span class="selected-file-path">${escapeHtml(filePath)}</span>
            <button type="button" class="remove-additional-file" 
                    onclick="removeAdditionalFile('${escapeHtml(filePath)}')" title="Quitar archivo">QUITAR</button>
        `;
        container.appendChild(item);
    });
    
    console.log(` Lista actualizada: ${additionalFiles.size} archivos adicionales`);
}

//  Eliminar archivo adicional de la seleccion
function removeAdditionalFile(filePath) {
    if (additionalFiles.has(filePath)) {
        additionalFiles.delete(filePath);
        console.log(` Eliminado archivo adicional: ${filePath}`);
        
        updateAdditionalFilesList();
        updateSelectionCounters();
        
        // Actualizar estilos en el explorador
        const allItems = document.querySelectorAll('.file-item-explorer');
        allItems.forEach(el => {
            const itemPath = el.getAttribute('data-path');
            if (itemPath === filePath) {
                el.classList.remove('selected');
            }
        });
        
        // Recargar la lista para reflejar cambios visuales
        loadFileList(currentExplorerPath);
    }
}

//  Funciones de seleccion masiva
function selectAllPreferred() {
    const checkboxes = document.querySelectorAll('input[name="preferred_files[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
    updateSelectionCounters();
}

function deselectAllPreferred() {
    const checkboxes = document.querySelectorAll('input[name="preferred_files[]"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
    updateSelectionCounters();
}

function selectAllVisible() {
    const fileItems = document.querySelectorAll('.file-item-explorer');
    fileItems.forEach(item => {
        const filePath = item.querySelector('.file-path').textContent;
        if (filePath & !item.querySelector('.file-icon').textContent.includes('??')) {
            additionalFiles.add(filePath);
        }
    });
    updateAdditionalFilesList();
    updateSelectionCounters();
    loadFileList(currentExplorerPath);
}

function deselectAllAdditional() {
    additionalFiles.clear();
    updateAdditionalFilesList();
    updateSelectionCounters();
    loadFileList(currentExplorerPath);
}


//  Modificar el envio del formulario para incluir archivos adicionales
document.getElementById('backupForm').addEventListener('submit', function(e) {
    // Anadir archivos adicionales como campos hidden
    const hiddenContainer = document.getElementById('additionalFilesHidden');
    if (hiddenContainer) {
        hiddenContainer.innerHTML = ''; // Limpiar primero
        
        additionalFiles.forEach(filePath => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'additional_files[]';
            input.value = filePath;
            hiddenContainer.appendChild(input);
        });
    }
    
    // Continuar con validacion normal...
});