<?php
session_start();
require_once __DIR__ . '/includes/conexion.php';
require_once __DIR__ . '/includes/seguridad.php';

// Verificar modo edición
if (!isset($_SESSION['modo_edicion'])) {
    header("Location: reles.php");
    exit;
}

// Procesar ID (para edición) o nuevo registro
$id = isset($_GET['id']) ? intval($_GET['id']) : 0;
$nuevo = ($id === 0);

// Inicializar datos del registro
$registro = [
    'id_condicion' => $nuevo ? '' : $id,
    'activado' => 0,
    'condicion1' => '',
    'condicion2' => '',
    'accion' => '',
    'descripcion' => ''
];

// Cargar datos si es edición
if (!$nuevo) {
    $query = "SELECT * FROM condiciones WHERE id_condicion = $id";
    $result = mysqli_query($link, $query);
    if ($result && mysqli_num_rows($result) > 0) {
        $registro = mysqli_fetch_assoc($result);
    } else {
        header("Location: reles.php?error=condicion_no_encontrada");
        exit;
    }
}

// Mostrar mensajes de sesión
$error = $_SESSION['error'] ?? '';
$mensaje = $_SESSION['mensaje'] ?? '';
unset($_SESSION['error'], $_SESSION['mensaje']);

function mostrarTexto($texto) {
    return htmlspecialchars($texto ?? '', ENT_QUOTES, 'UTF-8');
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $nuevo ? 'Nueva Condición' : 'Editar Condición' ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        textarea.form-control {
            min-height: 120px;
            white-space: pre;
            font-family: monospace;
        }
        .form-check-input {
            transform: scale(1.5);
        }
    </style>
</head>
<body>
<div class="modal-dialog modal-lg">
    <div class="modal-content">
        <div class="modal-header bg-dark text-white">
            <h5 class="modal-title">
                <i class="bi bi-list-check"></i> 
                <?= $nuevo ? 'Nueva Condición' : 'Editar Condición' ?>
            </h5>
        </div>
        
        <div class="modal-body">
            <?php /*
            <?php if ($error): ?>
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill"></i> <?= $error ?>
                </div>
            <?php elseif ($mensaje): ?>
                <div class="alert alert-success">
                    <i class="bi bi-check-circle-fill"></i> <?= $mensaje ?>
                </div>
            <?php endif; ?>
            */ ?>
            
            <form method="post" action="condiciones_guardar.php">
                <input type="hidden" name="id" value="<?= $id ?>">
                <input type="hidden" name="scroll_position" id="scroll_position" value="<?= $_GET['scroll'] ?? 0 ?>">
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="id_condicion" class="form-label fw-bold">ID Condición:</label>
                        <input type="number" class="form-control" name="id_condicion" id="id_condicion" 
                               value="<?= mostrarTexto($registro['id_condicion']) ?>" required>
                    </div>
                    <div class="col-md-6">
                        <div class="form-check form-switch mt-4 pt-3">
                            <input class="form-check-input" type="checkbox" role="switch" 
                                   name="activado" id="activado" value="1" 
                                   <?= $registro['activado'] ? 'checked' : '' ?>>
                            <label class="form-check-label fw-bold" for="activado">
                                Condición activada
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="condicion1" class="form-label fw-bold">Condición 1:</label>
                    <textarea class="form-control" name="condicion1" id="condicion1" 
                              rows="4"><?= mostrarTexto($registro['condicion1']) ?></textarea>
                </div>
                
                <div class="mb-3">
                    <label for="condicion2" class="form-label fw-bold">Condición 2:</label>
                    <textarea class="form-control" name="condicion2" id="condicion2" 
                              rows="4"><?= mostrarTexto($registro['condicion2']) ?></textarea>
                </div>
                
                <div class="mb-3">
                    <label for="accion" class="form-label fw-bold">Acción a realizar:</label>
                    <textarea class="form-control" name="accion" id="accion" 
                              rows="4" required><?= mostrarTexto($registro['accion']) ?></textarea>
                    <div class="form-text">Este campo es obligatorio</div>
                </div>
                
                <div class="mb-4">
                    <label for="descripcion" class="form-label fw-bold">Descripción (Opcional):</label>
                    <textarea class="form-control" name="descripcion" id="descripcion" 
                              rows="3"><?= mostrarTexto($registro['descripcion']) ?></textarea>
                </div>
                
                <div class="d-flex justify-content-between">
                    <button type="button" class="btn btn-secondary" onclick="window.history.back()">
                        <i class="bi bi-arrow-left"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-save"></i> Guardar Cambios
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
// Restaurar posición del scroll al cargar
document.addEventListener('DOMContentLoaded', function() {
    const scrollPos = <?= json_encode($_GET['scroll'] ?? 0) ?>;
    if (scrollPos > 0) {
        setTimeout(() => {
            window.scrollTo(0, scrollPos);
        }, 100);
    }
});

// Guardar posición del scroll antes de enviar el formulario
document.querySelector('form').addEventListener('submit', function() {
    document.getElementById('scroll_position').value = window.scrollY;
});
</script>
</body>
</html>