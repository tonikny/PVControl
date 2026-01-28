class PVConfigApp {
    constructor() {
        this.currentConfig = null;
        this.currentFile = 'Parametros_FV_DIST_NUEVO.py';  // ← CAMBIADO
        this.currentPath = [];
        
        console.log('PVConfigApp inicializando...');
        console.log('Archivo por defecto:', this.currentFile);
        this.init();
    }

    async init() {
        console.log('Iniciando aplicación...');
        await this.loadConfig();
        this.setupEventListeners();
        this.renderTree();
    }

    async loadConfig(filePath = null) {
        try {
            const targetFile = filePath || this.currentFile;
            this.showStatus(`Cargando configuración desde: ${targetFile}`, 'info');
            console.log('Cargando configuración desde:', targetFile);
            
            const response = await fetch('api/load_config_debug.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file: targetFile })
            });
            
            console.log('Respuesta del servidor status:', response.status);
            
            const data = await response.json();
            console.log('Datos recibidos:', data);
            
            if (data.success) {
                if (data.debug) {
                    // Modo debug - mostrar información en consola
                    console.log('=== DEBUG INFO ===');
                    console.log('Archivo:', data.file);
                    console.log('Tamaño:', data.file_size, 'bytes');
                    console.log('Líneas totales:', data.total_lines);
                    console.log('CONFIG encontrado:', data.config_found);
                    console.log('Posición CONFIG:', data.config_position);
                    console.log('Primeras líneas:', data.first_lines);
                    console.log('Muestra de contenido:', data.raw_content_sample);
                    
                    if (data.config_found) {
                        this.showStatus('CONFIG encontrado en el archivo, cargando configuración...', 'success');
                        // Ahora intenta cargar la configuración real
                        await this.loadConfigReal(targetFile);
                    } else {
                        this.showStatus('ERROR: CONFIG no encontrado en el archivo', 'error');
                    }
                } else {
                    // Configuración cargada normalmente
                    this.handleConfigLoaded(data);
                }
            } else {
                console.error('Error del servidor:', data.error);
                throw new Error(data.error || 'Error cargando configuración');
            }
        } catch (error) {
            console.error('Error en loadConfig:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async loadConfigReal(filePath) {
        try {
            console.log('Cargando configuración real para:', filePath);
            const response = await fetch('api/load_config_simple.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file: filePath })
            });
            
            console.log('Respuesta configuración real status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Datos configuración real:', data);
            
            if (data.success) {
                this.handleConfigLoaded(data);
            } else {
                throw new Error(data.error || 'Error cargando configuración real');
            }
        } catch (error) {
            console.error('Error cargando configuración real:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    handleConfigLoaded(data) {
        console.log('Configuración cargada correctamente, tipo config:', typeof data.config);
        console.log('Config keys:', Object.keys(data.config));
        
        this.currentConfig = data.config;
        this.currentFile = data.file;
        this.updateFilePath();
        this.renderTree();
        this.showStatus(`Configuración cargada correctamente desde ${this.currentFile}`, 'success');
        this.updateStats();
    }

    async loadConfig2(filePath = null) {
        try {
            const targetFile = filePath || this.currentFile;
            this.showStatus(`Cargando configuración desde: ${targetFile}`, 'info');
            console.log('Cargando configuración desde:', targetFile);
            
            const response = await fetch('api/load_config_debug.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file: targetFile })
            });
            
            console.log('Respuesta del servidor status:', response.status);
            
            const data = await response.json();
            console.log('Datos recibidos - success:', data.success);
            
            if (data.success) {
                console.log('Configuración cargada correctamente, tamaño:', Object.keys(data.config).length);
                this.currentConfig = data.config;
                this.currentFile = data.file;
                this.updateFilePath();
                this.renderTree();
                this.showStatus(`Configuración cargada correctamente desde ${this.currentFile}`, 'success');
                this.updateStats();
            } else {
                console.error('Error del servidor:', data.error);
                throw new Error(data.error || 'Error cargando configuración');
            }
        } catch (error) {
            console.error('Error en loadConfig:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }


    async loadConfig1(filePath = null) {
        try {
            this.showStatus('Cargando configuración...', 'info');
            
            const response = await fetch('api/load_config.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file: filePath || this.currentFile })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentConfig = data.config;
                this.currentFile = data.file;
                this.updateFilePath();
                this.renderTree();
                this.showStatus('Configuración cargada correctamente', 'success');
                this.updateStats();
            } else {
                throw new Error(data.error || 'Error cargando configuración');
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
            console.error('Error loading config:', error);
        }
    }

    async saveConfig() {
        try {
            this.showStatus('Guardando configuración...', 'info');
            
            const response = await fetch('api/save_config.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file: this.currentFile,
                    config: this.currentConfig
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showStatus('Configuración guardada correctamente', 'success');
            } else {
                throw new Error(data.error || 'Error guardando configuración');
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async validateConfig() {
        try {
            this.showStatus('Validando configuración...', 'info');
            
            const response = await fetch('api/validate_config.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ config: this.currentConfig })
            });
            
            const data = await response.json();
            
            if (data.valid) {
                this.showStatus('Configuración válida', 'success');
            } else {
                this.showStatus(`Errores encontrados: ${data.errors.join(', ')}`, 'warning');
            }
        } catch (error) {
            this.showStatus(`Error validando: ${error.message}`, 'error');
        }
    }

    renderTree() {
        const treeContainer = document.getElementById('config-tree');
        
        if (!this.currentConfig) {
            treeContainer.innerHTML = '<div class="tree-empty">No hay configuración cargada</div>';
            return;
        }

        treeContainer.innerHTML = this.buildTreeHTML(this.currentConfig, 'CONFIG');
    }

    buildTreeHTML(config, name, path = []) {
        const currentPath = [...path, name];
        const pathKey = currentPath.join('.');
        
        // Si es el nodo raíz CONFIG, empezar desde ahí
        if (name === 'CONFIG' && typeof config === 'object') {
            const children = Object.entries(config)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => this.buildTreeHTML(value, key, [])); // Reset path para empezar desde CONFIG
            
            return `
                <div class="tree-node expanded">
                    <div class="tree-item" data-path="CONFIG">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-down"></i>
                        </span>
                        <i class="tree-icon fas fa-database"></i>
                        <span class="tree-label">CONFIG</span>
                        <span class="tree-badge">${Object.keys(config).length} secciones</span>
                    </div>
                    <div class="tree-children">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        if (typeof config === 'object' && config !== null) {
            const isArray = Array.isArray(config);
            const children = Object.entries(config)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => this.buildTreeHTML(value, key, currentPath));
            
            return `
                <div class="tree-node">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-right"></i>
                        </span>
                        <i class="tree-icon ${isArray ? 'fas fa-list' : 'fas fa-folder'}"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${isArray ? `${config.length} items` : `${Object.keys(config).length} campos`}</span>
                    </div>
                    <div class="tree-children">
                        ${children.join('')}
                    </div>
                </div>
            `;
        } else {
            const valueType = typeof config;
            const valuePreview = String(config).substring(0, 30) + (String(config).length > 30 ? '...' : '');
            
            return `
                <div class="tree-node">
                    <div class="tree-item leaf" data-path="${pathKey}" data-value="${config}">
                        <i class="tree-icon ${this.getValueIcon(valueType)}"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-value">${valuePreview}</span>
                    </div>
                </div>
            `;
        }
    }


    buildTreeHTML_XXX(config, name, path = []) {
        const currentPath = [...path, name];
        const pathKey = currentPath.join('.');
        
        if (typeof config === 'object' && config !== null) {
            const isArray = Array.isArray(config);
            const children = Object.entries(config)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => this.buildTreeHTML(value, key, currentPath));
            
            return `
                <div class="tree-node">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-right"></i>
                        </span>
                        <i class="tree-icon ${isArray ? 'fas fa-list' : 'fas fa-folder'}"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${isArray ? `${config.length} items` : `${Object.keys(config).length} campos`}</span>
                    </div>
                    <div class="tree-children">
                        ${children.join('')}
                    </div>
                </div>
            `;
        } else {
            const valueType = typeof config;
            const valuePreview = String(config).substring(0, 30) + (String(config).length > 30 ? '...' : '');
            
            return `
                <div class="tree-node">
                    <div class="tree-item leaf" data-path="${pathKey}" data-value="${config}">
                        <i class="tree-icon ${this.getValueIcon(valueType)}"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-value">${valuePreview}</span>
                    </div>
                </div>
            `;
        }
    }

    getValueIcon(type) {
        const icons = {
            'number': 'fas fa-hashtag',
            'string': 'fas fa-font',
            'boolean': 'fas fa-toggle-on',
            'undefined': 'fas fa-question',
            'object': 'fas fa-cube'
        };
        return icons[type] || 'fas fa-code';
    }

    setupEventListeners() {
        // Botones principales
        document.getElementById('btn-save').addEventListener('click', () => this.saveConfig());
        document.getElementById('btn-validate').addEventListener('click', () => this.validateConfig());
        document.getElementById('btn-open').addEventListener('click', () => this.showFileModal());
        
        // Búsqueda en árbol
        document.getElementById('tree-search').addEventListener('input', (e) => {
            this.filterTree(e.target.value);
        });

        // Delegación de eventos para el árbol
        document.getElementById('config-tree').addEventListener('click', (e) => {
            const treeItem = e.target.closest('.tree-item');
            if (treeItem) {
                this.handleTreeItemClick(treeItem, e);
            }
        });

        // Modal
        document.querySelector('.modal-close').addEventListener('click', () => this.hideFileModal());
        document.addEventListener('click', (e) => {
            if (e.target.id === 'file-modal') {
                this.hideFileModal();
            }
        });

        // Items del modal
        document.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', () => {
                const file = item.dataset.file;
                this.loadConfig(file);
                this.hideFileModal();
            });
        });
    }

    handleTreeItemClick(treeItem, event) {
        if (event.target.closest('.tree-toggle')) {
            this.toggleTreeNode(treeItem);
            return;
        }

        const path = treeItem.dataset.path;
        this.selectTreeItem(treeItem, path);
    }

    toggleTreeNode(treeItem) {
        const node = treeItem.closest('.tree-node');
        const children = node.querySelector('.tree-children');
        const toggleIcon = treeItem.querySelector('.tree-toggle i');
        
        node.classList.toggle('expanded');
        toggleIcon.classList.toggle('fa-chevron-right');
        toggleIcon.classList.toggle('fa-chevron-down');
    }

    selectTreeItem(treeItem, path) {
        // Remover selección anterior
        document.querySelectorAll('.tree-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Seleccionar nuevo item
        treeItem.classList.add('selected');
        
        // Actualizar editor
        this.showEditorForPath(path);
    }

    selectPathInTree(path) {
        const treeItem = document.querySelector(`.tree-item[data-path="${path}"]`);
        if (treeItem) {
            this.selectTreeItem(treeItem, path);
            
            // Expandir todos los padres
            let parent = treeItem.closest('.tree-node');
            while (parent) {
                parent.classList.add('expanded');
                const toggleIcon = parent.querySelector('.tree-toggle i');
                if (toggleIcon) {
                    toggleIcon.classList.remove('fa-chevron-right');
                    toggleIcon.classList.add('fa-chevron-down');
                }
                parent = parent.parentElement?.closest('.tree-node');
            }
            
            // Scroll a elemento
            treeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }


    showEditorForPath(path) {
        const value = this.getValueByPath(this.currentConfig, path);
        const editor = new ConfigEditor(this, path, value);
        editor.render();
        
        // Actualizar breadcrumb
        this.updateBreadcrumb(path);
    }

    updateBreadcrumb(path) {
        const breadcrumbEl = document.getElementById('breadcrumb');
        const parts = path.split('.');
        
        const breadcrumbHTML = parts.map((part, index) => {
            const partialPath = parts.slice(0, index + 1).join('.');
            return `<span class="breadcrumb-item" data-path="${partialPath}">${part}</span>`;
        }).join(' <i class="fas fa-chevron-right"></i> ');
        
        breadcrumbEl.innerHTML = breadcrumbHTML;
        
        // Añadir event listeners a los breadcrumb items
        breadcrumbEl.querySelectorAll('.breadcrumb-item').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                this.selectPathInTree(path);
            });
        });
    }


    getValueByPath(obj, path) {
        const keys = path.split('.');
        // Si el path empieza con CONFIG, lo removemos ya que obj ya es CONFIG
        if (keys[0] === 'CONFIG') {
            keys.shift();
        }
        return keys.reduce((current, key) => current?.[key], obj);
    }

    showFileModal() {
        document.getElementById('file-modal').classList.add('show');
    }

    hideFileModal() {
        document.getElementById('file-modal').classList.remove('show');
    }

    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.className = `status-message ${type}`;
    }

    updateFilePath() {
        document.getElementById('file-path').textContent = `/home/pi/PVControl+/${this.currentFile}`;
    }

    updateStats() {
        const stats = this.countConfigElements(this.currentConfig);
        document.getElementById('config-stats').textContent = 
            `${stats.fields} campos, ${stats.sections} secciones`;
    }

    countConfigElements(config) {
        let fields = 0;
        let sections = 0;
        
        function count(obj) {
            if (typeof obj === 'object' && obj !== null) {
                sections++;
                Object.values(obj).forEach(value => {
                    if (typeof value === 'object' && value !== null) {
                        count(value);
                    } else {
                        fields++;
                    }
                });
            } else {
                fields++;
            }
        }
        
        count(config);
        return { fields, sections };
    }

    filterTree(searchTerm) {
        const treeItems = document.querySelectorAll('.tree-item');
        const searchLower = searchTerm.toLowerCase();
        
        treeItems.forEach(item => {
            const label = item.querySelector('.tree-label').textContent.toLowerCase();
            const isMatch = label.includes(searchLower);
            
            if (isMatch) {
                item.style.display = '';
                // Expandir padres
                let parent = item.closest('.tree-node');
                while (parent) {
                    parent.classList.add('expanded');
                    const toggleIcon = parent.querySelector('.tree-toggle i');
                    if (toggleIcon) {
                        toggleIcon.classList.remove('fa-chevron-right');
                        toggleIcon.classList.add('fa-chevron-down');
                    }
                    parent = parent.parentElement?.closest('.tree-node');
                }
            } else {
                item.style.display = 'none';
            }
        });
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.pvConfigApp = new PVConfigApp();
});