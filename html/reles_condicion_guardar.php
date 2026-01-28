<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';

if (!isset($_SESSION['modo_edicion']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("Location: reles.php");
    exit;
}

// Sanitizar todos los campos
$id_condicion = isset($_POST['id_condicion']) ? intval($_POST['id_condicion']) : null;
$id_rele = isset($_POST['id_rele']) ? intval($_POST['id_rele']) : null;
$operacion = mysqli_real_escape_string($link, $_POST['modo'] ?? '');
$parametro = mysqli_real_escape_string($link, $_POST['variable'] ?? '');
$condicion = mysqli_real_escape_string($link, $_POST['condicion'] ?? '');
$valor = floatval($_POST['valor'] ?? 0);
$open_relays = isset($_POST['open_relays']) ? json_decode($_POST['open_relays'], true) : [];

// Validación básica
if (empty($id_condicion) || empty($parametro) || empty($condicion)) {
    die("Datos incompletos");
}

// Usar INSERT ... ON DUPLICATE KEY UPDATE
$query = "INSERT INTO reles_c (
         id_reles_c, id_rele, operacion, parametro, condicion, valor)
         VALUES (?, ?, ?, ?, ?, ?)
         ON DUPLICATE KEY UPDATE
         id_rele = VALUES(id_rele),
         operacion = VALUES(operacion),
         parametro = VALUES(parametro),
         condicion = VALUES(condicion),
         valor = VALUES(valor)";

$stmt = mysqli_prepare($link, $query);
mysqli_stmt_bind_param($stmt, "iisssd", 
    $id_condicion, $id_rele, $operacion, $parametro, $condicion, $valor);

if (mysqli_stmt_execute($stmt)) {
    header("Location: reles.php?success=1&show_rele=".$id_rele."&keep_scroll=1");
    // Redirigir manteniendo los relés abiertos
} else {
    die("Error al guardar: " . mysqli_error($link));
}