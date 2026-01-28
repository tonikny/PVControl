<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';
require_once __DIR__ . '/includes/seguridad.php';

// Verificar modo edición
if (!isset($_SESSION['modo_edicion'])) {
    http_response_code(403);
    exit(json_encode(['success' => false, 'error' => 'Acceso denegado']));
}

// Obtener ID de la condición a borrar
$id = isset($_GET['id']) ? intval($_GET['id']) : 0;

if ($id <= 0) {
    http_response_code(400);
    exit(json_encode(['success' => false, 'error' => 'ID inválido']));
}

try {
    // Verificar que la condición existe
    $check_query = "SELECT id_condicion FROM condiciones WHERE id_condicion = $id";
    $check_result = mysqli_query($link, $check_query);
    
    if (!$check_result || mysqli_num_rows($check_result) === 0) {
        http_response_code(404);
        exit(json_encode(['success' => false, 'error' => 'Condición no encontrada']));
    }

    // Eliminar la condición
    $delete_query = "DELETE FROM condiciones WHERE id_condicion = $id";
    
    if (mysqli_query($link, $delete_query)) {
        // Verificar que se eliminó correctamente
        $verify_query = "SELECT id_condicion FROM condiciones WHERE id_condicion = $id";
        $verify_result = mysqli_query($link, $verify_query);
        
        if (!$verify_result || mysqli_num_rows($verify_result) === 0) {
            echo json_encode(['success' => true]);
        } else {
            throw new Exception("No se pudo verificar la eliminación");
        }
    } else {
        throw new Exception("Error al eliminar: " . mysqli_error($link));
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}