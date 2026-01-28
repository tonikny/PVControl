<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';
require_once __DIR__ . '/includes/seguridad.php';

// Verificar modo edición y solicitud AJAX
if (!isset($_SESSION['modo_edicion']) || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(403);
    exit('Acceso denegado');
}

// Obtener datos del POST
$id = isset($_POST['id']) ? intval($_POST['id']) : 0;
$activado = isset($_POST['activado']) ? intval($_POST['activado']) : 0;

if ($id <= 0) {
    http_response_code(400);
    exit('ID de condición inválido');
}

// Actualizar el estado en la base de datos
$query = "UPDATE condiciones SET activado = $activado WHERE id_condicion = $id";
if (mysqli_query($link, $query)) {
    // Verificar si realmente se actualizó
    $check_query = "SELECT activado FROM condiciones WHERE id_condicion = $id";
    $result = mysqli_query($link, $check_query);
    $row = mysqli_fetch_assoc($result);
    
    if ($row && $row['activado'] == $activado) {
        echo json_encode(['success' => true, 'activado' => $activado]);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => 'No se pudo verificar el cambio']);
    }
} else {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => mysqli_error($link)]);
}