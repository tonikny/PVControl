class TreeManager {
    constructor(app) {
        this.app = app;
        this.setupTreeEvents();
    }

    setupTreeEvents() {
        const treeContainer = document.getElementById('config-tree');
        
        if (!treeContainer) {
            console.error('Tree container not found');
            return;
        }

        // Usar event delegation para manejar clics en el árbol
        treeContainer.addEventListener('click', (e) => {
            const treeToggle = e.target.closest('.tree-toggle');
            const treeItem = e.target.closest('.tree-item');
            
            if (treeToggle && treeItem) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleTreeNode(treeItem);
            } else if (treeItem) {
                this.selectTreeItem(treeItem);
            }
        });

        const searchInput = document.getElementById('tree-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTree(e.target.value);
            });
        }

        const collapseBtn = document.getElementById('btn-collapse-all');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                this.collapseAll();
            });
        }
    }

    toggleTreeNode(treeItem) {
        const node = treeItem.closest('.tree-node');
        if (!node) return;
        
        const children = node.querySelector('.tree-children');
        const toggleIcon = treeItem.querySelector('.tree-toggle i');
        
        if (!children || !toggleIcon) return;
        
        if (node.classList.contains('expanded')) {
            // Colapsar
            node.classList.remove('expanded');
            children.style.display = 'none';
            toggleIcon.classList.remove('fa-chevron-down');
            toggleIcon.classList.add('fa-chevron-right');
        } else {
            // Expandir
            node.classList.add('expanded');
            children.style.display = 'block';
            toggleIcon.classList.remove('fa-chevron-right');
            toggleIcon.classList.add('fa-chevron-down');
        }
    }

    selectTreeItem(treeItem) {
        // Remover selección anterior
        document.querySelectorAll('.tree-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Seleccionar nuevo item
        treeItem.classList.add('selected');
        
        const path = treeItem.dataset.path;
        
        if (this.app && typeof this.app.onTreeItemSelected === 'function') {
            this.app.onTreeItemSelected(path, null, treeItem);
        }
    }

    filterTree(searchTerm) {
        const treeItems = document.querySelectorAll('.tree-item');
        const searchLower = searchTerm.toLowerCase().trim();
        
        if (searchLower === '') {
            // Mostrar todos los items
            treeItems.forEach(item => {
                item.style.display = '';
                this.showParentNodes(item);
            });
            return;
        }
        
        let hasMatches = false;
        treeItems.forEach(item => {
            const label = item.querySelector('.tree-label');
            if (!label) return;
            
            const labelText = label.textContent.toLowerCase();
            const isMatch = labelText.includes(searchLower);
            
            if (isMatch) {
                item.style.display = '';
                this.expandParents(item);
                hasMatches = true;
            } else {
                item.style.display = 'none';
            }
        });
        
        if (!hasMatches) {
            this.app.showStatus('No se encontraron resultados', 'warning');
        }
    }

    expandParents(treeItem) {
        let parent = treeItem.closest('.tree-node');
        while (parent) {
            parent.classList.add('expanded');
            const children = parent.querySelector('.tree-children');
            const toggleIcon = parent.querySelector('.tree-toggle i');
            if (children) children.style.display = 'block';
            if (toggleIcon) {
                toggleIcon.classList.remove('fa-chevron-right');
                toggleIcon.classList.add('fa-chevron-down');
            }
            parent = parent.parentElement?.closest('.tree-node');
        }
    }

    showParentNodes(treeItem) {
        let parent = treeItem.closest('.tree-node');
        while (parent) {
            parent.style.display = '';
            parent = parent.parentElement?.closest('.tree-node');
        }
    }

    collapseAll() {
        document.querySelectorAll('.tree-node.expanded').forEach(node => {
            node.classList.remove('expanded');
            const children = node.querySelector('.tree-children');
            const toggleIcon = node.querySelector('.tree-toggle i');
            if (children) children.style.display = 'none';
            if (toggleIcon) {
                toggleIcon.classList.remove('fa-chevron-down');
                toggleIcon.classList.add('fa-chevron-right');
            }
        });
        this.app.showStatus('Todos los nodos colapsados', 'info');
    }
}