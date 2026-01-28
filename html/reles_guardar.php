<?php
require_once __DIR__ . '/includes/conexion.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Sanitizar todos los campos
    $id_rele = isset($_POST['id_rele']) ? intval($_POST['id_rele']) : null;
    $nombre = mysqli_real_escape_string($link, $_POST['nombre'] ?? '');
    $modo = mysqli_real_escape_string($link, $_POST['modo'] ?? 'PRG');
    $estado = floatval($_POST['estado'] ?? 0);
    $grabacion = mysqli_real_escape_string($link, $_POST['grabacion'] ?? 'N');
    $salto = floatval($_POST['salto'] ?? 100);
    $prioridad = intval($_POST['prioridad'] ?? 0);
    $potencia = intval($_POST['potencia'] ?? 0);
    $retardo = intval($_POST['retardo'] ?? 0);
    $calibracion = mysqli_real_escape_string($link, $_POST['calibracion'] ?? '');

    // Usar INSERT ... ON DUPLICATE KEY UPDATE para manejar ambos casos
    $query = "INSERT INTO reles (
             id_rele, nombre, modo, estado, grabacion, 
             salto, prioridad, potencia, retardo, calibracion)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE
             nombre = VALUES(nombre),
             modo = VALUES(modo),
             estado = VALUES(estado),
             grabacion = VALUES(grabacion),
             salto = VALUES(salto),
             prioridad = VALUES(prioridad),
             potencia = VALUES(potencia),
             retardo = VALUES(retardo),
             calibracion = VALUES(calibracion)";
    
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "issdsdddds", 
        $id_rele, $nombre, $modo, $estado, $grabacion,
        $salto, $prioridad, $potencia, $retardo, $calibracion);

    if (mysqli_stmt_execute($stmt)) {
        header("Location: reles.php?success=1");
    } else {
        die("Error al guardar: " . mysqli_error($link));
    }
} else {
    header("Location: reles.php");
}