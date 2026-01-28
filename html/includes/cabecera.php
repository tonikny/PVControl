 <?php
require_once __DIR__ . '/conexion.php';
$tituloPagina = "";
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <link rel="icon" href="/img/favicon.ico" type="image/x-icon">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($tituloPagina); ?></title>

    <!-- Cargar Bootstrap CSS primero 
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
   -->
    <!-- Nuestros estilos después -->
    <link rel="stylesheet" href="css/menu_2025.css">
    <script src="script/menu.js"></script>
</head>
<body>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Menú principal -->
    <div id="navbar"></div>

    <!-- Contenido -->
    <div class="contenido-principal">