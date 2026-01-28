<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';

// 1. Validar autenticación y método de solicitud
if (!isset($_SESSION['modo_edicion']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("HTTP/1.1 403 Forbidden");
    exit("Acceso no autorizado");
}

// 2. Sanitizar y validar datos básicos
$id_horario = isset($_POST['id_horario']) ? intval($_POST['id_horario']) : null;
$id_rele = isset($_POST['id_rele']) ? intval($_POST['id_rele']) : null;
$hora_on = isset($_POST['hora_on']) ? mysqli_real_escape_string($link, $_POST['hora_on']) : '';
$hora_off = isset($_POST['hora_off']) ? mysqli_real_escape_string($link, $_POST['hora_off']) : '';

// 3. Validación estricta del ID
if (!$id_horario || $id_horario <= 0) {
    header("Location: reles.php?error=id_invalido&show_rele=".$id_rele);
    exit;
}

// 4. Procesar días seleccionados
$dias_seleccionados = $_POST['dias'] ?? [];
$parametro_h = '';

// Validar que haya al menos un día seleccionado
if (empty($dias_seleccionados)) {
    header("Location: reles.php?error=no_dias&show_rele=".$id_rele);
    exit;
}

// Procesar selección de días
if (in_array('T', $dias_seleccionados)) {
    $parametro_h = 'T';
} else {
    $orden_dias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    $dias_filtrados = array_unique($dias_seleccionados);
    $dias_ordenados = array_intersect($orden_dias, $dias_filtrados);
    $parametro_h = implode('', $dias_ordenados);
}

// 5. Validaciones finales
if (empty($id_rele) || empty($hora_on) || empty($hora_off) || empty($parametro_h)) {
    header("Location: reles.php?error=datos_incompletos&show_rele=".$id_rele);
    exit;
}

// 6. Preparar consulta UPSERT
$query = "INSERT INTO reles_h (
         id_reles_h, id_rele, parametro_h, valor_h_ON, valor_h_OFF)
         VALUES (?, ?, ?, ?, ?)
         ON DUPLICATE KEY UPDATE
         id_rele = VALUES(id_rele),
         parametro_h = VALUES(parametro_h),
         valor_h_ON = VALUES(valor_h_ON),
         valor_h_OFF = VALUES(valor_h_OFF)";

$stmt = mysqli_prepare($link, $query);
if (!$stmt) {
    error_log("Error al preparar consulta: " . mysqli_error($link));
    header("Location: reles.php?error=db_error&show_rele=".$id_rele);
    exit;
}

// 7. Enlazar parámetros
mysqli_stmt_bind_param($stmt, "iisss",
    $id_horario, $id_rele, $parametro_h, $hora_on, $hora_off);

// 8. Ejecutar y manejar resultados
if (mysqli_stmt_execute($stmt)) {
    // Éxito - redirigir manteniendo el rele abierto
    header("Location: reles.php?success=1&show_rele=".$id_rele."&keep_scroll=1");

} else {
    error_log("Error al guardar horario: " . mysqli_error($link));
    header("Location: reles.php?error=db_error&show_rele=".$id_rele);
}

// Antes de redirigir, guarda el estado de scroll

mysqli_stmt_close($stmt);
exit;