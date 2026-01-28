<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';

// Verificar permisos y método de solicitud
if (!isset($_SESSION['modo_edicion']) || $_SERVER['REQUEST_METHOD'] !== 'GET') {
    header("HTTP/1.1 403 Forbidden");
    exit("Acceso no autorizado");
}

// Obtener y validar ID
$id_rele = isset($_GET['id']) ? intval($_GET['id']) : null;

if (!$id_rele || $id_rele <= 0) {
    header("HTTP/1.1 400 Bad Request");
    exit("ID de relé no válido");
}

// Iniciar transacción para eliminar en cascada
mysqli_begin_transaction($link);

try {
    // 1. Eliminar condiciones asociadas (reles_c)
    $query = "DELETE FROM reles_c WHERE id_rele = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id_rele);
    mysqli_stmt_execute($stmt);
    
    // 2. Eliminar horarios asociados (reles_h)
    $query = "DELETE FROM reles_h WHERE id_rele = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id_rele);
    mysqli_stmt_execute($stmt);
    
    // 3. Eliminar el relé principal
    $query = "DELETE FROM reles WHERE id_rele = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id_rele);
    mysqli_stmt_execute($stmt);
    
    // Confirmar transacción si todo fue bien
    mysqli_commit($link);
    
    // Redireccionar con mensaje de éxito
    header("Location: reles.php?success=1&deleted=1");
    exit;

} catch (Exception $e) {
    // Revertir transacción en caso de error
    mysqli_rollback($link);
    
    // Registrar error (opcional)
    error_log("Error al borrar relé: " . $e->getMessage());
    
    // Redireccionar con mensaje de error
    header("Location: reles.php?error=1");
    exit;
}