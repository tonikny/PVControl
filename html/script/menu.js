// menu.js - Versión completa con carga de configuración y soporte móvil

document.addEventListener("DOMContentLoaded", function() {
    console.log("Iniciando sistema de menú mejorado...");

    // 1. Elementos del DOM
    const navbar = document.getElementById('navbar');
    if (!navbar) {
        console.error("Error: No se encontró el elemento #navbar");
        showError("Error de configuración del menú");
        return;
    }

    // 2. Configuración por defecto (para desarrollo)
    const defaultConfig = {
        menu_web: {
            "Inicio": "index.php",
            "Relés": "reles.php",
            "Configuración": {
                "General": "config_general.php",
                "Avanzada": "config_avanzada.php"
            },
            "Informes": "informes.php",
            "Ayuda": "ayuda.php"
        }
    };

    // ================= FUNCIONES PRINCIPALES =================

    function generateMenu(menuData) {
        try {
            // Limpiar navbar
            navbar.innerHTML = '';

            // Logo
            const logo = document.createElement('div');
            logo.className = 'logo';
            logo.innerHTML = '<img src="img/fvcontrol.png" alt="Logo">';
            navbar.appendChild(logo);

            // Contenedor principal
            const menuItems = document.createElement('div');
            menuItems.className = 'menu-items';
            navbar.appendChild(menuItems);

            // Botón hamburguesa
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'menu-toggle';
            toggleBtn.innerHTML = '☰';
            navbar.appendChild(toggleBtn);

            // Generar items
            Object.keys(menuData).forEach(key => {
                if (typeof menuData[key] === 'string') {
                    // Item simple
                    const link = document.createElement('a');
                    link.className = 'menu-item';
                    link.href = menuData[key];
                    link.textContent = key;
                    menuItems.appendChild(link);
                } else {
                    // Item con submenú
                    const dropdown = document.createElement('div');
                    dropdown.className = 'menu-dropdown';
                    
                    const btn = document.createElement('button');
                    btn.className = 'dropbtn';
                    btn.textContent = key;
                    
                    const content = document.createElement('div');
                    content.className = 'dropdown-content';
                    
                    Object.keys(menuData[key]).forEach(subKey => {
                        const subLink = document.createElement('a');
                        subLink.href = menuData[key][subKey];
                        subLink.textContent = subKey;
                        content.appendChild(subLink);
                    });
                    
                    dropdown.appendChild(btn);
                    dropdown.appendChild(content);
                    menuItems.appendChild(dropdown);
                }
            });

            console.log("Menú generado correctamente");
            setupMobileMenu();

        } catch (error) {
            console.error("Error al generar menú:", error);
            showError("Error al crear el menú");
        }
    }

    // ================= SISTEMA DE CARGA DE CONFIGURACIÓN =================

    function loadConfig() {
        // 1. Intentar cargar configuración activa
        fetch('configuracion_activa.txt?t=' + new Date().getTime())
            .then(response => {
                if (!response.ok) throw new Error("Error al cargar configuración");
                return response.text();
            })
            .then(configFile => {
                console.log("Archivo de configuración encontrado:", configFile);
                loadConfigFile(configFile.trim());
            })
            .catch(error => {
                console.warn("Usando configuración local:", error.message);
                generateMenu(defaultConfig.menu_web);
            });
    }

    function loadConfigFile(configFile) {
        // Eliminar scripts antiguos
        document.querySelectorAll('script[data-config]').forEach(script => {
            script.remove();
        });

        // Crear nuevo script de configuración
        const script = document.createElement('script');
        script.src = 'configuraciones/' + configFile;
        script.setAttribute('data-config', configFile);
        
        script.onload = function() {
            if (typeof config !== 'undefined' && config.menu_web) {
                console.log("Configuración externa cargada correctamente");
                generateMenu(config.menu_web);
            } else {
                throw new Error("Configuración no válida en el archivo");
            }
        };
        
        script.onerror = function() {
            throw new Error("Error al cargar el archivo de configuración");
        };
        
        document.head.appendChild(script);
    }

    // ================= SOPORTE MÓVIL MEJORADO =================

    function setupMobileMenu() {
        const menuItems = document.querySelector('.menu-items');
        const toggleBtn = document.querySelector('.menu-toggle');
        let touchStartTime = 0;

        // 1. Botón hamburguesa
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            menuItems.classList.toggle('show');
            closeAllDropdowns();
        });

        // 2. Eventos táctiles mejorados
        document.querySelectorAll('.dropbtn').forEach(btn => {
            btn.addEventListener('touchstart', function() {
                touchStartTime = Date.now();
            });
            
            btn.addEventListener('click', handleMobileClick);
            btn.addEventListener('touchend', handleMobileClick);
        });

        // 3. Cerrar menús al tocar fuera
        document.addEventListener('click', closeAllMenus);
        document.addEventListener('touchend', closeAllMenus);
    }

    function handleMobileClick(e) {
        if (window.innerWidth > 768) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = this.closest('.menu-dropdown');
        const content = dropdown.querySelector('.dropdown-content');
        
        // Cerrar otros dropdowns primero
        document.querySelectorAll('.dropdown-content').forEach(item => {
            if (item !== content) item.classList.remove('show-mobile');
        });
        
        // Alternar el actual
        content.classList.toggle('show-mobile');
    }

    function closeAllMenus(e) {
        if (!e.target.closest('#navbar')) {
            document.querySelector('.menu-items').classList.remove('show');
            closeAllDropdowns();
        }
    }

    function closeAllDropdowns() {
        document.querySelectorAll('.dropdown-content').forEach(item => {
            item.classList.remove('show-mobile');
        });
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'menu-error alert alert-danger';
        errorDiv.innerHTML = `
            <strong>Error:</strong> ${message}
            <button onclick="location.reload()" class="btn btn-sm btn-warning">Reintentar</button>
        `;
        document.body.prepend(errorDiv);
    }

    // ================= INICIALIZACIÓN =================

    // Primero intentar cargar configuración externa
    loadConfig();
});