<?php
/**
 * manuales.php
 * Visualizador de manuales PDF con exploración dinámica de directorios
 */

// Configuración
$MANUALES_PATH = $_SERVER['DOCUMENT_ROOT'] . '/Manuales';

/**
 * Función recursiva para explorar directorios y generar estructura de árbol
 */
function scanDirectory($path) {
    $result = [];
    
    // Verificar si el directorio existe y es legible
    if (!is_dir($path) || !is_readable($path)) {
        return $result;
    }
    
    // Obtener elementos del directorio
    $items = scandir($path);
    
    foreach ($items as $item) {
        // Ignorar directorios especiales
        if ($item === '.' || $item === '..') {
            continue;
        }
        
        $fullPath = $path . '/' . $item;
        $relativePath = str_replace($_SERVER['DOCUMENT_ROOT'], '', $fullPath);
        
        if (is_dir($fullPath)) {
            // Es un directorio
            $result[$item] = [
                'type' => 'folder',
                'children' => scanDirectory($fullPath)
            ];
        } else {
            // Es un archivo - solo incluir PDFs
            $extension = strtolower(pathinfo($item, PATHINFO_EXTENSION));
            if ($extension === 'pdf') {
                $result[$item] = [
                    'type' => 'file',
                    'path' => $relativePath
                ];
            }
        }
    }
    
    // Ordenar: primero carpetas, luego archivos, ambos alfabéticamente
    uksort($result, function($a, $b) use ($result) {
        $aIsDir = $result[$a]['type'] === 'folder';
        $bIsDir = $result[$b]['type'] === 'folder';
        
        if ($aIsDir && !$bIsDir) {
            return -1;
        } elseif (!$aIsDir && $bIsDir) {
            return 1;
        } else {
            return strcasecmp($a, $b);
        }
    });
    
    return $result;
}

// Procesar solicitud AJAX para obtener estructura de archivos
if (isset($_GET['action']) && $_GET['action'] === 'get_structure') {
    header('Content-Type: application/json');
    $fileStructure = scanDirectory($MANUALES_PATH);
    echo json_encode($fileStructure, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

// Si no es una solicitud AJAX, mostrar la página HTML
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manuales - PVControl+</title>
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #1abc9c;
            --light-color: #ecf0f1;
            --dark-color: #34495e;
            --border-color: #bdc3c7;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            display: flex;
            height: 100vh;
            background-color: #f5f7fa;
            color: #333;
        }
        
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: var(--primary-color);
            color: white;
            padding: 15px 20px;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.5rem;
            margin-right: auto;
        }
        
        .logo {
            height: 40px;
            margin-right: 15px;
        }
        
        .container {
            display: flex;
            width: 100%;
            margin-top: 70px;
            height: calc(100vh - 70px);
        }
        
        .sidebar {
            width: 300px;
            background-color: white;
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .sidebar h2 {
            font-size: 1.2rem;
            color: var(--primary-color);
            margin: 0;
        }
        
        .back-button {
            background-color: var(--secondary-color);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .back-button:hover {
            background-color: var(--dark-color);
        }
        
        .file-tree {
            list-style-type: none;
            flex: 1;
            overflow-y: auto;
        }
        
        .file-tree li {
            margin: 5px 0;
        }
        
        .folder, .file {
            padding: 8px 10px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: background-color 0.2s;
        }
        
        .folder:hover, .file:hover {
            background-color: var(--light-color);
        }
        
        .folder.active, .file.active {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .folder::before {
            content: "📁";
            margin-right: 8px;
            font-size: 1.1rem;
        }
        
        .file::before {
            content: "📄";
            margin-right: 8px;
            font-size: 1.1rem;
        }
        
        .folder.expanded::before {
            content: "📂";
        }
        
        .sub-tree {
            list-style-type: none;
            margin-left: 20px;
            display: none;
        }
        
        .sub-tree.expanded {
            display: block;
        }
        
        .content {
            flex: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
            background-color: white;
            margin: 0 20px 20px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .content-header {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .content-header h2 {
            color: var(--primary-color);
            font-size: 1.4rem;
        }
        
        .viewer {
            flex: 1;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .pdf-viewer {
            width: 100%;
            height: 100%;
            border: none;
        }
        
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: #7f8c8d;
            text-align: center;
        }
        
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 15px;
            color: var(--border-color);
        }
        
        .search-box {
            margin-bottom: 20px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .search-box i {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--border-color);
        }
        
        .loading {
            padding: 10px;
            text-align: center;
            color: #7f8c8d;
        }
        
        .error {
            padding: 10px;
            text-align: center;
            color: #e74c3c;
            background-color: #fadbd8;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: 40%;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            
            .content {
                height: 60%;
                margin: 0;
            }
            
            .sidebar-header {
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }
            
            .back-button {
                align-self: stretch;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡</div>
        <h1>Manuales - PVControl+</h1>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Documentación</h2>
                <a href="/" class="back-button">← VOLVER AL INICIO</a>
            </div>
            
            <div class="search-box">
                <input type="text" placeholder="Buscar manuales..." id="searchInput">
                <i>🔍</i>
            </div>
            
            <ul class="file-tree" id="fileTree">
                <div class="loading" id="loadingIndicator">Cargando estructura de archivos...</div>
            </ul>
        </div>
        
        <div class="content">
            <div class="content-header">
                <h2 id="documentTitle">Seleccione un documento</h2>
            </div>
            
            <div class="viewer" id="viewer">
                <div class="empty-state">
                    <i>📄</i>
                    <p>Seleccione un documento de la lista para visualizarlo</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Función para cargar la estructura de archivos desde el mismo archivo PHP
        async function loadFileStructure() {
            try {
                const response = await fetch('<?php echo basename(__FILE__); ?>?action=get_structure');
                if (!response.ok) {
                    throw new Error('Error al cargar la estructura de archivos');
                }
                const fileStructure = await response.json();
                return fileStructure;
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loadingIndicator').className = 'error';
                document.getElementById('loadingIndicator').textContent = 'Error al cargar la estructura de archivos';
                return {};
            }
        }

        // Función para generar el árbol de archivos
        function generateFileTree(structure, parentElement) {
            // Limpiar el indicador de carga
            const loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
            
            // Si no hay estructura, mostrar mensaje
            if (Object.keys(structure).length === 0) {
                parentElement.innerHTML = '<div class="error">No se encontraron archivos PDF en el directorio Manuales/</div>';
                return;
            }
            
            for (const key in structure) {
                const item = structure[key];
                const li = document.createElement('li');
                
                if (item.type === 'folder') {
                    li.innerHTML = `
                        <div class="folder">${key}</div>
                        <ul class="sub-tree"></ul>
                    `;
                    
                    const folderElement = li.querySelector('.folder');
                    const subTree = li.querySelector('.sub-tree');
                    
                    folderElement.addEventListener('click', function(e) {
                        e.stopPropagation();
                        folderElement.classList.toggle('expanded');
                        subTree.classList.toggle('expanded');
                    });
                    
                    generateFileTree(item.children, subTree);
                } else {
                    li.innerHTML = `<div class="file" data-path="${item.path}">${key}</div>`;
                    
                    const fileElement = li.querySelector('.file');
                    fileElement.addEventListener('click', function() {
                        // Quitar clase activa de todos los elementos
                        document.querySelectorAll('.file, .folder').forEach(el => {
                            el.classList.remove('active');
                        });
                        
                        // Añadir clase activa al elemento seleccionado
                        fileElement.classList.add('active');
                        
                        // Cargar el PDF en el visor
                        loadPDF(item.path, key);
                    });
                }
                
                parentElement.appendChild(li);
            }
        }

        // Función para cargar el PDF en el visor
        function loadPDF(path, title) {
            const viewer = document.getElementById('viewer');
            const documentTitle = document.getElementById('documentTitle');
            
            // Actualizar el título
            documentTitle.textContent = title;
            
            // Crear el visor de PDF
            viewer.innerHTML = `
                <iframe class="pdf-viewer" src="${path}" frameborder="0"></iframe>
            `;
        }

        // Inicializar la aplicación cuando se carga la página
        document.addEventListener('DOMContentLoaded', async function() {
            const fileTree = document.getElementById('fileTree');
            
            // Cargar la estructura de archivos
            const fileStructure = await loadFileStructure();
            
            // Generar el árbol de archivos
            generateFileTree(fileStructure, fileTree);
            
            // Añadir funcionalidad de búsqueda
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const allFiles = document.querySelectorAll('.file, .folder');
                
                allFiles.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        item.style.display = 'flex';
                        
                        // Expandir carpetas padre si hay coincidencias
                        let parent = item.closest('.sub-tree');
                        while (parent) {
                            parent.classList.add('expanded');
                            const folder = parent.previousElementSibling;
                            if (folder && folder.classList.contains('folder')) {
                                folder.classList.add('expanded');
                            }
                            parent = parent.parentElement.closest('.sub-tree');
                        }
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>