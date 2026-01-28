<?php
session_start();
if (!isset($_SESSION['modo_edicion'])) {
    die('Acceso no autorizado');
}

require_once __DIR__ . '/includes/conexion.php';

$id_horario = $_GET['id'] ?? 'nuevo';
$id_rele = $_GET['id_rele'] ?? null;

$horario = [];
$nombre_rele = '';

// Cargar datos si es edición
if ($id_horario !== 'nuevo') {
    $query = "SELECT h.*, r.nombre AS nombre_rele 
              FROM reles_h h 
              LEFT JOIN reles r ON h.id_rele = r.id_rele 
              WHERE h.id_reles_h = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id_horario);
    mysqli_stmt_execute($stmt);
    $horario = mysqli_stmt_get_result($stmt)->fetch_assoc();
    $nombre_rele = $horario['nombre_rele'] ?? '';
    $id_rele = $horario['id_rele'] ?? '';
    
}

?>


<div class="modal-header">
    <h5 class="modal-title">
        <?= ($id_horario === 'nuevo') 
            ? 'Nuevo Horario para Relé ' . htmlspecialchars($id_rele)
            : 'Editando Rele'. $id_rele.' -> Horario ID: ' . htmlspecialchars($id_horario) . 
              ($nombre_rele ? ' del Relé: ' . htmlspecialchars($nombre_rele) : '') ?>
    </h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
</div>

<div class="modal-body">
    <form action="reles_horario_guardar.php" method="post" id="formHorario">
        <input type="hidden" name="id" value="<?= $horario['id_reles_h'] ?? '' ?>">
        <input type="hidden" name="id_rele" value="<?= $id_rele ?>">
        <input type="hidden" id="openRelaysState" name="open_relays" value="">

        <div class="mb-3">
            <label class="form-label">ID de Condición Horaria</label>
            <input type="number" name="id_horario" class="form-control" required
                   value="<?= htmlspecialchars($horario['id_reles_h'] ?? '') ?>">
            <small class="text-muted">Introduce id unico --> ejemplo: 51101 (condicion 01 del rele 511)</small>
        </div>        
        
        <div class="mb-3">
            <label class="form-label">Días de aplicación</label>
            <?php
            // Inicializar variables
            $parametro_h = $horario['parametro_h'] ?? '';
            $dias_actuales = $parametro_h !== '' ? str_split($parametro_h) : [];
            
            // Definir días de la semana
            $dias_semana = [
                'L' => 'Lunes',
                'M' => 'Martes',
                'X' => 'Miércoles',
                'J' => 'Jueves',
                'V' => 'Viernes',
                'S' => 'Sábado',
                'D' => 'Domingo',
                'T' => 'Todos los días'
            ];
            
            // Generar checkboxes
            foreach ($dias_semana as $letra => $nombre) {
                $checked = '';
                
                // Verificar si está seleccionado
                if ($parametro_h === 'T' || in_array($letra, $dias_actuales)) {
                    $checked = 'checked';
                }
                
                echo '<div class="form-check">
                        <input class="form-check-input" type="checkbox" 
                               name="dias[]" 
                               value="'.$letra.'" 
                               id="dia_'.$letra.'"
                               '.$checked.'>
                        <label class="form-check-label" for="dia_'.$letra.'">
                            '.$nombre.'
                        </label>
                      </div>';
            }
            ?>
        </div>
        
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Hora de Activación (ON)</label>
                <input type="time" name="hora_on" class="form-control" required
                       value="<?= htmlspecialchars($horario['valor_h_ON'] ?? '08:00') ?>">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">Hora de Desactivación (OFF)</label>
                <input type="time" name="hora_off" class="form-control" required
                       value="<?= htmlspecialchars($horario['valor_h_OFF'] ?? '20:00') ?>">
            </div>
        </div>

    </form>
</div>

<div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
    <button type="submit" form="formHorario" class="btn btn-primary" onclick="saveOpenRelaysState()">Guardar</button>

</div>

<script>
// Guardar estado de relés abiertos
function saveOpenRelaysState() {
    const openRelays = JSON.parse(sessionStorage.getItem('openRelays') || '[]');
    document.getElementById('openRelaysState').value = JSON.stringify(openRelays);
}

// Restaurar estado al abrir el modal
document.addEventListener('DOMContentLoaded', function() {
    const openRelays = JSON.parse(sessionStorage.getItem('openRelays') || '[]');
    if(openRelays.length > 0) {
        const input = document.getElementById('openRelaysState');
        if(input) input.value = JSON.stringify(openRelays);
    }
});

</script>