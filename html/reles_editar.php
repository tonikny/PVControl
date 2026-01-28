<?php
session_start();
if (!isset($_SESSION['modo_edicion'])) {
    die('Acceso no autorizado');
}

require_once __DIR__ . '/includes/conexion.php';

$id = $_GET['id'] ?? 'nuevo';
$rele = [];

if ($id !== 'nuevo') {
    $query = "SELECT * FROM reles WHERE id_rele = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id);
    mysqli_stmt_execute($stmt);
    $rele = mysqli_stmt_get_result($stmt)->fetch_assoc();
}
?>

<div class="modal-header">
    <h5 class="modal-title">
        <?= ($id === 'nuevo') ? 'Nuevo Relé' : 'Editando Relé ID: '.htmlspecialchars($rele['id_rele']) ?>
    </h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
</div>

<div class="modal-body">
    <form action="reles_guardar.php" method="post" id="formRele">
        <?php if ($id === 'nuevo'): ?>
            <div class="mb-3">
                <label class="form-label">ID Relé</label>
                <input type="number" name="id_rele" class="form-control" min="1" required>
                <small class="text-muted">Introduce un número XXX único para el nuevo relé</small>
                
            </div>
        <?php else: ?>
            <input type="hidden" name="id_rele" value="<?= $rele['id_rele'] ?? '' ?>">
        <?php endif; ?>

        <div class="mb-3">
            <label class="form-label">Nombre</label>
            <input type="text" name="nombre" class="form-control" 
                   value="<?= htmlspecialchars($rele['nombre'] ?? '') ?>" required>
        </div>

        <div class="mb-3">
            <label class="form-label">Modo</label>
            <select name="modo" class="form-select">
                <option value="ON" <?= ($rele['modo'] ?? '') === 'ON' ? 'selected' : '' ?>>ON</option>
                <option value="OFF" <?= ($rele['modo'] ?? '') === 'OFF' ? 'selected' : '' ?>>OFF</option>
                <option value="PRG" <?= ($rele['modo'] ?? 'PRG') === 'PRG' ? 'selected' : '' ?>>PRG</option>
                <option value="MAN" <?= ($rele['modo'] ?? '') === 'MAN' ? 'selected' : '' ?>>MAN</option>                
            </select>
            <small class="text-muted">ON: siempre encendido - OFF: siempre apagado - PRG: controlado por condiciones - MAN: controlado manualmente</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Estado (0-100)</label>
            <input type="number" name="estado" class="form-control" 
                   min="0" max="100" step="0.01"
                   value="<?= $rele['estado'] ?? 0 ?>">
            <small class="text-muted">Estado actual del relé (de 0 a 100)</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Grabación</label>
            <select name="grabacion" class="form-select">
                <option value="S" <?= ($rele['grabacion'] ?? '') === 'S' ? 'selected' : '' ?>>Sí</option>
                <option value="N" <?= ($rele['grabacion'] ?? 'N') === 'N' ? 'selected' : '' ?>>No</option>
            </select>
            <small class="text-muted">Graba en Base de datos los cambos de estado del relé</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Salto (0-100)</label>
            <input type="number" name="salto" class="form-control" 
                   min="0" max="100" step="0.01"
                   value="<?= $rele['salto'] ?? 100 ?>">
            <small class="text-muted">Incremento que se utilizará en gestion de excedentes para ir ajustando el valor de Estado</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Prioridad</label>
            <input type="number" name="prioridad" class="form-control" 
                   min="0" step="1"
                   value="<?= $rele['prioridad'] ?? 0 ?>">
            <small class="text-muted">Prioridad para control de excedentes -- 0 desactiva excedentes para el relé</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Potencia</label>
            <input type="number" name="potencia" class="form-control" 
                   value="<?= $rele['potencia'] ?? 0 ?>">
        </div>

        <div class="mb-3">
            <label class="form-label">Retardo</label>
            <input type="number" name="retardo" class="form-control" 
                   min="0" step="1"
                   value="<?= $rele['retardo'] ?? 0 ?>">
            <small class="text-muted">Tiempo minimo que debe transcurrir entre cada conmutacion del relé</small>

        </div>

        <div class="mb-3">
            <label class="form-label">Calibración</label>
            <textarea name="calibracion" class="form-control" rows="3"><?= htmlspecialchars($rele['calibracion'] ?? '') ?></textarea>
        </div>
    </form>
</div>

<div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
    <button type="submit" form="formRele" class="btn btn-primary">Guardar</button>
</div>

<script>
// Validación adicional antes de enviar
document.getElementById('formRele').addEventListener('submit', function(e) {
    const estado = parseFloat(this.elements['estado'].value);
    const salto = parseFloat(this.elements['salto'].value);
    
    if (estado < 0 || estado > 100) {
        alert('El estado debe estar entre 0 y 100');
        e.preventDefault();
        return false;
    }
    
    if (salto < 0 || salto > 100) {
        alert('El salto debe estar entre 0 y 100');
        e.preventDefault();
        return false;
    }
    
    <?php if ($id === 'nuevo'): ?>
    // Validar que el ID no esté vacío para nuevos registros
    const idRele = parseInt(this.elements['id_rele'].value);
    if (isNaN(idRele) || idRele <= 0) {
        alert('El ID del relé debe ser un número positivo');
        e.preventDefault();
        return false;
    }
    <?php endif; ?>
    
    return true;
});
</script>