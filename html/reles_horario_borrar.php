<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';

// 1. Validar autenticación y método de solicitud
if (!isset($_SESSION['modo_edicion']) || $_SERVER['REQUEST_METHOD'] !== 'GET') {
    header("HTTP/1.1 403 Forbidden");
    exit("Acceso no autorizado");
}

// 2. Obtener y validar ID de condición
$id_horario = isset($_GET['id']) ? intval($_GET['id']) : null;
if (!$id_horario || $id_horario <= 0) {
    header("HTTP/1.1 400 Bad Request");
    exit("ID de condición no válido");
}

// 3. Obtener el id_rele asociado para mantener el estado de visualización
$id_rele = null;
$query = "SELECT id_rele FROM reles_h WHERE id_reles_h = ?";
$stmt = mysqli_prepare($link, $query);
mysqli_stmt_bind_param($stmt, "i", $id_horario);
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);

if ($row = mysqli_fetch_assoc($result)) {
    $id_rele = $row['id_rele'];
} else {
    header("Location: reles.php?error=horario_no_encontrado");
    exit;
}

// 4. Eliminar la condición
$query = "DELETE FROM reles_h WHERE id_reles_h = ?";
$stmt = mysqli_prepare($link, $query);
mysqli_stmt_bind_param($stmt, "i", $id_horario);

if (mysqli_stmt_execute($stmt)) {
    // Redirigir manteniendo abierta la sección del relé
    header("Location: reles.php?success=1&show_rele=" . $id_rele);
} else {
    // Registrar error en logs
    error_log("Error al borrar horario: " . mysqli_error($link));
    header("Location: reles.php?error=1&show_rele=" . $id_rele);
}
exit;