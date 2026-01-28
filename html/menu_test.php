<?php
// test_menu.php - Página de prueba para el menú

// 1. Cabecera común
require_once __DIR__ . '/includes/cabecera.php';

// Definir título específico para esta página
$tituloPagina = "Prueba de Menú";
?>

<!-- Contenido específico de la página -->
<main class="contenido-principal container">
    <h1 class="my-4">TEST - Página de Prueba</h1>
    <div class="alert alert-info">
        Esta página solo muestra el menú y este contenido de prueba.
    </div>
</main>

<!-- Scripts específicos -->

<?php
// Pie de página común (si existe)
if (file_exists(__DIR__ . '/includes/pie.php')) {
    require_once __DIR__ . '/includes/pie.php';
}
?>


