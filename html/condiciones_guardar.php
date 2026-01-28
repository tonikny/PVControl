<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';
require_once __DIR__ . '/includes/seguridad.php';

// Verificar modo edición
if (!isset($_SESSION['modo_edicion'])) {
    header("Location: reles.php");
    exit;
}

// Obtener datos del formulario
$id = isset($_POST['id']) ? intval($_POST['id']) : 0;
$id_condicion = isset($_POST['id_condicion']) ? intval($_POST['id_condicion']) : 0;
$activado = isset($_POST['activado']) ? 1 : 0;
$condicion1 = mysqli_real_escape_string($link, $_POST['condicion1'] ?? '');
$condicion2 = mysqli_real_escape_string($link, $_POST['condicion2'] ?? '');
$accion = mysqli_real_escape_string($link, $_POST['accion'] ?? '');
$descripcion = mysqli_real_escape_string($link, $_POST['descripcion'] ?? '');
$scroll_position = isset($_POST['scroll_position']) ? intval($_POST['scroll_position']) : 0;

// Validar datos requeridos
if (empty($accion)) {
    $_SESSION['error'] = "El campo Acción es obligatorio";
    header("Location: condiciones_editar.php?id=".$id."&scroll=".$scroll_position);
    exit;
}

// Verificar si el ID condición ya existe (para nuevos registros)
if ($id === 0) {
    $check_query = "SELECT id_condicion FROM condiciones WHERE id_condicion = $id_condicion";
    $check_result = mysqli_query($link, $check_query);
    if (mysqli_num_rows($check_result) > 0) {
        $_SESSION['error'] = "El ID de condición ya existe";
        header("Location: condiciones_editar.php?scroll=".$scroll_position);
        exit;
    }
}

try {
    if ($id > 0) {
        // Verificar si estamos cambiando el ID
        if ($id !== $id_condicion) {
            // Comprobar que el nuevo ID no existe
            $check_query = "SELECT id_condicion FROM condiciones WHERE id_condicion = $id_condicion";
            $check_result = mysqli_query($link, $check_query);
            if (mysqli_num_rows($check_result) > 0) {
                throw new Exception("El nuevo ID de condición ya existe");
            }
        }
        
        // Actualizar registro existente
        $query = "UPDATE condiciones SET 
                  id_condicion = $id_condicion,
                  activado = $activado,
                  condicion1 = '$condicion1',
                  condicion2 = '$condicion2',
                  accion = '$accion',
                  descripcion = '$descripcion'
                  WHERE id_condicion = $id";
    } else {
        // Crear nuevo registro
        $query = "INSERT INTO condiciones 
                  (id_condicion, activado, condicion1, condicion2, accion, descripcion)
                  VALUES ($id_condicion, $activado, '$condicion1', '$condicion2', '$accion', '$descripcion')";
    }

    if (mysqli_query($link, $query)) {
        // Redirigir manteniendo la posición del scroll
        $_SESSION['mensaje'] = $id === 0 ? "Condición creada exitosamente" : "Condición actualizada exitosamente";
        header("Location: reles.php?keep_scroll=1&scroll=".$scroll_position);
    } else {
        throw new Exception("Error en la base de datos: " . mysqli_error($link));
    }
} catch (Exception $e) {
    $_SESSION['error'] = $e->getMessage();
    header("Location: condiciones_editar.php?id=".$id."&scroll=".$scroll_position);
    exit;
}