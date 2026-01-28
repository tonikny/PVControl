// js/editor.js
class ConfigEditor {
    constructor(app) {
        this.app = app;
        this.currentPath = null;
        this.currentValue = null;
        this.setupEditor();
    }

    setupEditor() {
        // Esto se llamará una vez al inicializar
        console.log('Editor inicializado');
    }

    showForPath(path, value) {
        this.currentPath = path;
        this.currentValue = value;
        
        console.log(`Editor: mostrando ${path} =`, value);
        
        this.updateEditorHeader(path);
        this.updateEditorContent(value);
        this.showEditorPanel();
    }

    updateEditorHeader(path) {
        const titleEl = document.getElementById('section-title');
        const breadcrumbEl = document.getElementById('breadcrumb');
        
        if (titleEl) {
            const pathParts = path.split('.');
            titleEl.textContent = pathParts[pathParts.length - 1] || 'CONFIG';
        }
        
        if (breadcrumbEl) {
            const parts = path.split('.');
            const breadcrumbHTML = parts.map((part, index) => {
                const partialPath = parts.slice(0, index + 1).join('.');
                return `<span class="breadcrumb-item" data-path="${partialPath}">${part}</span>`;
            }).join(' <i class="fas fa-chevron-right" style="margin: 0 0.5rem;"></i> ');
            
            breadcrumbEl.innerHTML = breadcrumbHTML;
            
            // Añadir event listeners a los breadcrumbs
            breadcrumbEl.querySelectorAll('.breadcrumb-item').forEach(item => {
                item.addEventListener('click', () => {
                    const path = item.dataset.path;
                    this.app.selectPathInTree(path);
                });
            });
        }
    }

    updateEditorContent(value) {
        const editorEl = document.getElementById('config-editor');
        if (!editorEl) return;
        
        const valueType = typeof value;
        const isObject = value !== null && typeof value === 'object';
        const isArray = Array.isArray(value);
        
        let contentHTML = '';
        
        if (isObject || isArray) {
            // Mostrar objeto/array como tabla de propiedades
            contentHTML = this.renderObjectEditor(value);
        } else {
            // Mostrar valor simple
            contentHTML = this.renderSimpleEditor(value, valueType);
        }
        
        editorEl.innerHTML = contentHTML;
        this.setupEditorEvents();
    }

    renderObjectEditor(obj) {
        const isArray = Array.isArray(obj);
        const entries = isArray ? 
            obj.map((value, index) => [index, value]) : 
            Object.entries(obj);
        
        const rows = entries.map(([key, value]) => {
            const valueType = typeof value;
            const valuePreview = this.getValuePreview(value);
            const isComplex = value !== null && typeof value === 'object';
            
            return `
                <tr class="object-row ${isComplex ? 'has-children' : ''}">
                    <td class="key-cell">
                        <span class="key-label">${key}</span>
                    </td>
                    <td class="type-cell">
                        <span class="type-badge ${valueType}">${isArray ? 'array' : valueType}</span>
                    </td>
                    <td class="value-cell">
                        <span class="value-preview">${valuePreview}</span>
                    </td>
                    <td class="action-cell">
                        ${isComplex ? 
                            `<button class="btn-icon navigate-to" data-key="${key}" title="Navegar">
                                <i class="fas fa-arrow-right"></i>
                            </button>` :
                            `<button class="btn-icon edit-value" data-key="${key}" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>`
                        }
                    </td>
                </tr>
            `;
        }).join('');
        
        return `
            <div class="editor-section">
                <h3>${isArray ? 'Elementos del Array' : 'Propiedades del Objeto'}</h3>
                <div class="object-table-container">
                    <table class="object-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Tipo</th>
                                <th>Valor</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderSimpleEditor(value, valueType) {
        return `
            <div class="editor-section">
                <h3>Editor de Valor</h3>
                <div class="simple-editor">
                    <div class="form-group">
                        <label>Tipo:</label>
                        <span class="value-type-badge ${valueType}">${valueType}</span>
                    </div>
                    <div class="form-group">
                        <label>Valor actual:</label>
                        <div class="current-value">${value}</div>
                    </div>
                    <div class="form-group">
                        <label>Nuevo valor:</label>
                        <input type="text" class="value-input" value="${value}" placeholder="Ingrese nuevo valor...">
                    </div>
                    <div class="editor-actions">
                        <button class="btn btn-primary save-value">Guardar Cambios</button>
                        <button class="btn btn-secondary reset-value">Restablecer</button>
                    </div>
                </div>
            </div>
        `;
    }

    getValuePreview(value) {
        if (value === null) return 'null';
        if (value === undefined) return 'undefined';
        
        if (typeof value === 'object') {
            if (Array.isArray(value)) {
                return `[${value.length} elementos]`;
            } else {
                return `{${Object.keys(value).length} propiedades}`;
            }
        }
        
        const str = String(value);
        return str.length > 50 ? str.substring(0, 50) + '...' : str;
    }

    setupEditorEvents() {
        // Navegar a objetos hijos
        document.querySelectorAll('.navigate-to').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const key = e.target.closest('.navigate-to').dataset.key;
                const newPath = this.currentPath + '.' + key;
                this.app.selectPathInTree(newPath);
            });
        });

        // Editar valores simples
        document.querySelectorAll('.edit-value').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const key = e.target.closest('.edit-value').dataset.key;
                const newPath = this.currentPath + '.' + key;
                this.app.selectPathInTree(newPath);
            });
        });

        // Guardar cambios
        const saveBtn = document.querySelector('.save-value');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveValue();
            });
        }
    }

    showEditorPanel() {
        const emptyState = document.getElementById('empty-state');
        const editorEl = document.getElementById('config-editor');
        
        if (emptyState) emptyState.style.display = 'none';
        if (editorEl) editorEl.style.display = 'block';
    }

    saveValue() {
        // Por implementar - guardar cambios en la configuración
        this.app.showStatus('Funcionalidad de guardado pendiente', 'warning');
    }
}
