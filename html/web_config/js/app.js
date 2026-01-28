class PVConfigApp {
    constructor() {
        this.currentConfig = null;
        this.currentFile = 'Parametros_FV_DIST_NUEVO.py';
        this.currentPath = [];
        this.treeManager = null;
        this.editor = null;
        this.lineMap = null;
        this.fullContent = null;
        this.configOrder = []; // Para mantener el orden original
        
        console.log('PVConfigApp inicializando...');
        this.init();
    }

    async init() {
        console.log('Iniciando aplicación...');
        await this.loadConfig();
        this.setupEventListeners();
        this.renderTree();
        this.treeManager = new TreeManager(this);
        this.editor = new ConfigEditor(this);
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
                console.log('Config keys:', Object.keys(data.config));
                console.log('LineMap keys:', Object.keys(data.lineMap || {}));
                
                this.currentConfig = data.config;
                this.lineMap = data.lineMap;
                this.fullContent = data.fullContent;
                this.currentFile = data.file;
                
                // Mantener el orden original de las claves
                this.configOrder = this.extractConfigOrder(data.fullContent);
                
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

    extractConfigOrder(fullContent) {
        const order = [];
        const lines = fullContent.split('\n');
        let inConfig = false;
        
        for (let line of lines) {
            const trimmed = line.trim();
            
            if (trimmed === 'CONFIG = {') {
                inConfig = true;
                continue;
            }
            
            if (inConfig) {
                if (trimmed === '}') {
                    break;
                }
                
                // Buscar patrones de clave
                const keyMatch = trimmed.match(/^['"]([^'"]+)['"]\s*:/);
                if (keyMatch) {
                    order.push(keyMatch[1]);
                }
            }
        }
        
        return order;
    }

    renderTree() {
        const treeContainer = document.getElementById('config-tree');
        console.log('Renderizando árbol, currentConfig:', this.currentConfig);
        
        if (!this.currentConfig) {
            console.log('No hay configuración para renderizar');
            treeContainer.innerHTML = '<div class="tree-empty">No hay configuración cargada</div>';
            return;
        }

        treeContainer.innerHTML = this.buildTreeHTML(this.currentConfig, 'CONFIG', [], 0);
        console.log('Árbol renderizado');
    }

    buildTreeHTML(config, name, path = [], level = 0) {
        const currentPath = [...path, name];
        const pathKey = currentPath.join('.');
        
        const isRoot = (name === 'CONFIG');
        const isObject = typeof config === 'object' && config !== null && !Array.isArray(config);
        const isArray = Array.isArray(config);
        const isLeaf = !isObject && !isArray;
        
        // Solo expandir hasta nivel 3 (CONFIG = 0, secciones principales = 1, subsecciones = 2, campos = 3)
        const maxLevel = 3;
        const startsExpanded = isRoot || level < maxLevel;
        
        if (isRoot) {
            // Usar el orden original en lugar de orden alfabético
            const children = this.getOrderedChildren(config).map(([key, value]) => 
                this.buildTreeHTML(value, key, currentPath, level + 1)
            );
            
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
                .map(([key, value]) => this.buildTreeHTML(value, key, currentPath, level + 1));
            
            return `
                <div class="tree-node ${startsExpanded ? 'expanded' : ''} has-children">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-${startsExpanded ? 'down' : 'right'}"></i>
                        </span>
                        <i class="tree-icon fas fa-folder"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${Object.keys(config).length} campos</span>
                    </div>
                    <div class="tree-children" style="${startsExpanded ? '' : 'display: none;'}">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        if (isArray) {
            const children = config.map((value, index) => 
                this.buildTreeHTML(value, `[${index}]`, currentPath, level + 1)
            );
            
            return `
                <div class="tree-node ${startsExpanded ? 'expanded' : ''} has-children">
                    <div class="tree-item" data-path="${pathKey}">
                        <span class="tree-toggle">
                            <i class="fas fa-chevron-${startsExpanded ? 'down' : 'right'}"></i>
                        </span>
                        <i class="tree-icon fas fa-list"></i>
                        <span class="tree-label">${name}</span>
                        <span class="tree-badge">${config.length} elementos</span>
                    </div>
                    <div class="tree-children" style="${startsExpanded ? '' : 'display: none;'}">
                        ${children.join('')}
                    </div>
                </div>
            `;
        }
        
        // Es un valor simple (leaf) - SOLO MOSTRAR EL TÍTULO, NO EL VALOR
        return `
            <div class="tree-node leaf-node">
                <div class="tree-item leaf" data-path="${pathKey}">
                    <i class="tree-icon ${this.getValueIcon(typeof config)}"></i>
                    <span class="tree-label">${name}</span>
                </div>
            </div>
        `;
    }

    getOrderedChildren(config) {
        if (!this.configOrder || this.configOrder.length === 0) {
            return Object.entries(config);
        }
        
        const orderedEntries = [];
        const usedKeys = new Set();
        
        // Primero agregar en el orden original
        for (const key of this.configOrder) {
            if (config.hasOwnProperty(key)) {
                orderedEntries.push([key, config[key]]);
                usedKeys.add(key);
            }
        }
        
        // Luego agregar cualquier clave que no esté en el orden original
        for (const [key, value] of Object.entries(config)) {
            if (!usedKeys.has(key)) {
                orderedEntries.push([key, value]);
            }
        }
        
        return orderedEntries;
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

    setupEventListeners() {
        document.getElementById('btn-save').addEventListener('click', () => this.saveConfig());
        document.getElementById('btn-validate').addEventListener('click', () => this.validateConfig());
        document.getElementById('btn-open').addEventListener('click', () => this.showFileModal());
        
        document.getElementById('tree-search').addEventListener('input', (e) => {
            this.filterTree(e.target.value);
        });

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
        if (!node) return;
        
        const children = node.querySelector('.tree-children');
        const toggleIcon = treeItem.querySelector('.tree-toggle i');
        
        if (!children || !toggleIcon) return;
        
        if (node.classList.contains('expanded')) {
            node.classList.remove('expanded');
            children.style.display = 'none';
            toggleIcon.classList.remove('fa-chevron-down');
            toggleIcon.classList.add('fa-chevron-right');
        } else {
            node.classList.add('expanded');
            children.style.display = 'block';
            toggleIcon.classList.remove('fa-chevron-right');
            toggleIcon.classList.add('fa-chevron-down');
        }
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
        console.log(`Seleccionado: ${path} =`, value);
        this.showStatus(`Seleccionado: ${path}`, 'info');
        
        if (this.editor) {
            this.editor.showForPath(path, value);
        }
    }

    getValueByPath(obj, path) {
        const keys = path.split('.');
        if (keys[0] === 'CONFIG') {
            keys.shift();
        }
        return keys.reduce((current, key) => current?.[key], obj);
    }

    selectPathInTree(path) {
        const treeItem = document.querySelector(`.tree-item[data-path="${path}"]`);
        if (treeItem) {
            this.selectTreeItem(treeItem, path);
            treeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    onTreeItemSelected(path, value, treeItem) {
        console.log(`Item seleccionado: ${path} =`, value);
        this.showStatus(`Seleccionado: ${path}`, 'info');
        
        if (this.editor) {
            const configValue = this.getValueByPath(this.currentConfig, path);
            this.editor.showForPath(path, configValue);
        }
    }

    showFileModal() {
        alert('Funcionalidad de abrir archivo pendiente');
    }

    async saveConfig() {
        if (!this.editor.currentPath) {
            this.showStatus('No hay sección seleccionada para guardar', 'error');
            return;
        }

        try {
            // Obtener el texto exacto del editor
            const rawContent = this.editor.getCurrentValue();
            const path = this.editor.currentPath;
            
            console.log('Guardando contenido raw para:', path);
            
            // Enviar el contenido raw al servidor
            const response = await fetch('api/save_raw_section.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    path: path,
                    content: rawContent,
                    file: this.currentFile
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.editor.clearModifiedState();
                this.showStatus('Sección guardada correctamente', 'success');
                
                // Recargar la configuración completa para actualizar el árbol
                await this.loadConfig();
            } else {
                throw new Error(data.error || 'Error al guardar');
            }
            
        } catch (error) {
            console.error('Error guardando sección:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async validateConfig() {
        this.showStatus('Validar - pendiente de implementar', 'warning');
    }

    filterTree(searchTerm) {
        const treeItems = document.querySelectorAll('.tree-item');
        const searchLower = searchTerm.toLowerCase();
        
        treeItems.forEach(item => {
            const label = item.querySelector('.tree-label');
            if (!label) return;
            
            const labelText = label.textContent.toLowerCase();
            const isMatch = labelText.includes(searchLower);
            item.style.display = isMatch ? '' : 'none';
        });
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.pvConfigApp = new PVConfigApp();
});