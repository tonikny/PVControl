<?php
// menu_debug.php - ARCHIVO COMPLETO
require_once __DIR__ . '/includes/cabecera.php';
?>

<main class="contenido-principal container">
    <h1 class="my-4">Prueba de Menú Móvil</h1>
    
    <div class="alert alert-info">
        <strong>Pruebas en móvil:</strong>
        <ul>
            <li>El botón ☰ debe mostrar/ocultar menú</li>
            <li>Click en dropdowns debe mostrar submenús</li>
            <li>Click fuera debe cerrar menús</li>
        </ul>
    </div>
</main>

<script>
// Verificador manual
document.addEventListener("DOMContentLoaded", function() {
    const checkMenu = setInterval(function() {
        if (typeof setupMobileMenu === 'function') {
            console.log("Soporte móvil activado");
            clearInterval(checkMenu);
        }
    }, 500);
});
</script>