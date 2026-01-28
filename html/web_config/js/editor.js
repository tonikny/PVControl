// js/editor.js - Versión corregida para mostrar contenido raw
class ConfigEditor {
    constructor(app) {
        this.app = app;
        this.currentPath = null;
        this.currentValue = null;
        this.aceEditor = null;
        this.setupAceEditor();
    }

    setupAceEditor() {
        // Inicializar Ace Editor
        this.aceEditor = ace.edit("config-editor");
        this.aceEditor.setTheme("ace/theme/chrome");
        this.aceEditor.session.setMode("ace/mode/python");
        this.aceEditor.setOptions({
            fontSize: "14px",
            showPrintMargin: false,
            wrap: true,
            enableBasicAutocompletion: false,
            enableLiveAutocompletion: false,
            showGutter: true,
            highlightActiveLine: true,
            tabSize: 4,
            useSoftTabs: true
        });

        // Detectar cambios en el editor
        this.aceEditor.session.on('change', () => {
            this.onContentChange();
        });

        console.log('Ace Editor inicializado');
    }

    async showForPath(path, value) {
        this.currentPath = path;
        this.currentValue = value;
        
        console.log(`Editor: mostrando ${path}`, value);
        
        this.updateEditorHeader(path);
        await this.loadRawContent(path);
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
            
            breadcrumbEl.querySelectorAll('.breadcrumb-item').forEach(item => {
                item.addEventListener('click', () => {
                    const path = item.dataset.path;
                    this.app.selectPathInTree(path);
                });
            });
        }
    }

    async loadRawContent(path) {
        try {
            this.app.showStatus('Cargando contenido raw...', 'info');
            
            const response = await fetch('api/get_raw_section.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    path: path,
                    file: this.app.currentFile
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Mostrar el contenido exacto del archivo
                this.aceEditor.setValue(data.content, -1);
                this.aceEditor.session.setUndoManager(new ace.UndoManager());
                this.app.showStatus('Contenido raw cargado', 'success');
            } else {
                throw new Error(data.error || 'Error cargando contenido');
            }
        } catch (error) {
            console.error('Error cargando contenido raw:', error);
            this.app.showStatus(`Error: ${error.message}`, 'error');
            
            // Fallback para cuando no hay endpoint get_raw_section.php
            // Si es CONFIG, mostrar el contenido completo
            if (path === 'CONFIG' && this.app.fullContent) {
                this.aceEditor.setValue(this.app.fullContent, -1);
            } else {
                // Para otras secciones, intentar usar el lineMap
                const content = this.getContentFromLineMap(path);
                this.aceEditor.setValue(content, -1);
            }
        }
    }

    getContentFromLineMap(path) {
        if (this.app.lineMap && this.app.lineMap[path]) {
            return this.app.lineMap[path].content;
        }
        
        // Fallback final: convertir el valor a string
        if (this.currentValue !== null && this.currentValue !== undefined) {
            if (typeof this.currentValue === 'object') {
                return JSON.stringify(this.currentValue, null, 2);
            }
            return String(this.currentValue);
        }
        
        return '# Contenido no disponible';
    }

    showEditorPanel() {
        const emptyState = document.getElementById('empty-state');
        const editorEl = document.getElementById('config-editor');
        
        if (emptyState) emptyState.style.display = 'none';
        if (editorEl) editorEl.style.display = 'block';
        
        // Enfocar el editor
        setTimeout(() => {
            if (this.aceEditor) {
                this.aceEditor.focus();
            }
        }, 100);
    }

    onContentChange() {
        // Marcar como modificado
        const saveBtn = document.getElementById('btn-save');
        if (saveBtn) {
            saveBtn.classList.add('btn-modified');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar*';
        }
        
        // Actualizar estado
        this.app.showStatus('Modificado - Presiona Guardar para aplicar cambios', 'warning');
    }

    getCurrentValue() {
        // Devolver el texto exacto del editor
        return this.aceEditor.getValue();
    }

    clearModifiedState() {
        const saveBtn = document.getElementById('btn-save');
        if (saveBtn) {
            saveBtn.classList.remove('btn-modified');
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar';
        }
    }

    hide() {
        const emptyState = document.getElementById('empty-state');
        const editorEl = document.getElementById('config-editor');
        
        if (emptyState) emptyState.style.display = 'flex';
        if (editorEl) editorEl.style.display = 'none';
        
        this.currentPath = null;
        this.currentValue = null;
        this.clearModifiedState();
    }
}