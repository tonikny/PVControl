<?php
session_start();
if (!isset($_SESSION['modo_edicion'])) {
    die('Acceso no autorizado');
}

require_once __DIR__ . '/includes/conexion.php';

$comando = $_GET['comando'] ?? '';
$id_rele = $_GET['id'] ?? 0;

if (in_array($comando, ['ON', 'OFF', 'PRG', 'MAN_ON', 'MAN_OFF'])) {
    if ($comando === 'MAN_ON') {
        $query = "UPDATE reles SET modo = 'MAN', estado = 100 WHERE id_rele = ?";
        $stmt = mysqli_prepare($link, $query);
        mysqli_stmt_bind_param($stmt, "i", $id_rele);
    } elseif ($comando === 'MAN_OFF') {
        $query = "UPDATE reles SET modo = 'MAN', estado = 0 WHERE id_rele = ?";
        $stmt = mysqli_prepare($link, $query);
        mysqli_stmt_bind_param($stmt, "i", $id_rele);
    } elseif ($comando === 'ON') {
        $query = "UPDATE reles SET modo = 'ON', estado = 100 WHERE id_rele = ?";
        $stmt = mysqli_prepare($link, $query);
        mysqli_stmt_bind_param($stmt, "i", $id_rele);
    } elseif ($comando === 'OFF') {
        $query = "UPDATE reles SET modo = 'OFF', estado = 0 WHERE id_rele = ?";
        $stmt = mysqli_prepare($link, $query);
        mysqli_stmt_bind_param($stmt, "i", $id_rele);
    } elseif ($comando === 'PRG') {  // Aquí estaba el error principal
        $query = "UPDATE reles SET modo = 'PRG' WHERE id_rele = ?";
        $stmt = mysqli_prepare($link, $query);
        mysqli_stmt_bind_param($stmt, "i", $id_rele);
    }
    
    if (isset($stmt)) {  // Verificación adicional por seguridad
        mysqli_stmt_execute($stmt);
    }
}

header("Location: " . $_SERVER['HTTP_REFERER']); // Redirige de vuelta