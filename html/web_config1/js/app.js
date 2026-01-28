// app.js - versión simplificada
class PVConfigApp {
    constructor() {
        this.currentConfig = null;
        this.currentFile = 'Parametros_FV_DIST_NUEVO.py';
        this.currentPath = [];
        this.treeManager = null;
        this.editor = null; // ← Añadir editor
        
        console.log('PVConfigApp inicializando...');
        this.init();
    }

    async init() {
        console.log('Iniciando aplicación...');
        await this.loadConfig();
        this.setupEventListeners();
        this.renderTree();
        this.treeManager = new TreeManager(this);
        this.editor = new ConfigEditor(this); // ← Inicializar editor
    }

    // Método para seleccionar path desde breadcrumbs
    selectPathInTree(path) {
        const treeItem = document.querySelector(`.tree-item[data-path="${path}"]`);
        if (treeItem) {
            this.treeManager.selectTreeItem(treeItem);
            
            // Scroll a elemento
            treeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }


    onTreeItemSelected(path, value, treeItem) {
        console.log(`Item seleccionado: ${path} =`, value);
        this.showStatus(`Seleccionado: ${path}`, 'info');
        
        // Pasar al editor
        if (this.editor) {
            const configValue = this.getValueByPath(this.currentConfig, path);
            this.editor.showForPath(path, configValue);
        }
    }
    
    async loadConfig(filePath = null) {
        try {
            const targetFile = filePath || this.currentFile;
            this.showStatus(`Cargando configuración desde: ${targetFile}`, 'info');
            console.log('Cargando configuración desde:', targetFile);
            
            const response = await fetch('api/load_config.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file: targetFile })
            });
            
            console.log('Respuesta del servidor status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Datos recibidos - success:', data.success);
            
            if (data.success) {
                console.log('Configuración cargada correctamente');
                console.log('Debug info:', data.debug_info);
                console.log('Config keys:', Object.keys(data.config));
                
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

    renderTree() {
        const treeContainer = document.getElementById('config-tree');
        console.log('Renderizando árbol, currentConfig:', this.currentConfig);
        
        if (!this.currentConfig) {
            console.log('No hay configuración para renderizar');
            treeContainer.innerHTML = '<div class="tree-empty">No hay configuración cargada</div>';
            return;
        }

        treeContainer.innerHTML = this.buildTreeHTML(this.currentConfig, 'CONFIG');
        console.log('Árbol renderizado');
    }

    buildTreeHTML(config, name, path = []) {
        const currentPath = [...path, name];
        const pathKey = currentPath.join('.');
        
        const isRoot = (name === 'CONFIG');
        const isObject = typeof config === 'object' && config !== null && !Array.isArray(config);
        const isArray = Array.isArray(config);
        const isLeaf = !isObject && !isArray;
        
        // Solo el nodo raíz empieza expandido
        const startsExpanded = isRoot;
        
        if (isRoot) {
            const children = Object.entries(config)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => this.buildTreeHTML(value, key, currentPath));
            
            return `
                <div class="tree-node ${startsExpanded ? 'expanded' : ''} has-children">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-${startsExpanded ? 'down' : 'right'}"></i>
                        </span>
                        <i class="tree-icon fas fa-database"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${Object.keys(config).length} secciones</span>
                    </div>
                    <div class="tree-children" style="${startsExpanded ? '' : 'display: none;'}">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        if (isObject) {
            const children = Object.entries(config)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([key, value]) => this.buildTreeHTML(value, key, currentPath));
            
            return `
                <div class="tree-node has-children">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-right"></i>
                        </span>
                        <i class="tree-icon fas fa-folder"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${Object.keys(config).length} campos</span>
                    </div>
                    <div class="tree-children">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        if (isArray) {
            const children = config.map((value, index) => 
                this.buildTreeHTML(value, `[${index}]`, currentPath)
            );
            
            return `
                <div class="tree-node has-children">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-right"></i>
                        </span>
                        <i class="tree-icon fas fa-list"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${config.length} elementos</span>
                    </div>
                    <div class="tree-children">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        // Es un valor simple (leaf)
        const valueType = typeof config;
        const valuePreview = String(config);
        const truncatedValue = valuePreview.length > 30 ? 
            valuePreview.substring(0, 30) + '...' : valuePreview;
        
        return `
            <div class="tree-node leaf-node">
                <div class="tree-item leaf" data-path="${pathKey}" data-value="${config}">
                    <i class="tree-icon ${this.getValueIcon(valueType)}"></i>
                    <span class="tree-label">${name}</span>
                    <span class="tree-value" title="${valuePreview}">${truncatedValue}</span>
                </div>
            </div>
        `;
    }
    
    getValueIcon(type) {
        const icons = {
            'number': 'fas fa-hashtag',
            'string': 'fas fa-font',
            'boolean': 'fas fa-toggle-on',
            'undefined': 'fas fa-question-circle',
            'object': 'fas fa-cube',
            'null': 'fas fa-ban'
        };
        return icons[type] || 'fas fa-code';
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
        if (!this.currentConfig) return;
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
        document.querySelectorAll('.tree-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        treeItem.classList.add('selected');
        this.showEditorForPath(path);
    }

    showEditorForPath(path) {
        const value = this.getValueByPath(this.currentConfig, path);
        // Por ahora solo mostrar en consola
        console.log(`Seleccionado: ${path} =`, value);
        this.showStatus(`Seleccionado: ${path}`, 'info');
    }

    getValueByPath(obj, path) {
        const keys = path.split('.');
        if (keys[0] === 'CONFIG') {
            keys.shift();
        }
        return keys.reduce((current, key) => current?.[key], obj);
    }

    showFileModal() {
        // Implementación básica por ahora
        alert('Funcionalidad de abrir archivo pendiente');
    }

    async saveConfig() {
        this.showStatus('Guardar - pendiente de implementar', 'warning');
    }

    async validateConfig() {
        this.showStatus('Validar - pendiente de implementar', 'warning');
    }

    filterTree(searchTerm) {
        const treeItems = document.querySelectorAll('.tree-item');
        const searchLower = searchTerm.toLowerCase();
        
        treeItems.forEach(item => {
            const label = item.querySelector('.tree-label').textContent.toLowerCase();
            const isMatch = label.includes(searchLower);
            item.style.display = isMatch ? '' : 'none';
        });
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado, inicializando PVConfigApp...');
    window.pvConfigApp = new PVConfigApp();
});