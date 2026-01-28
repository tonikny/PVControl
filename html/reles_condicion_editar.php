<?php
session_start();
if (!isset($_SESSION['modo_edicion'])) {
    die('Acceso no autorizado');
}

require_once __DIR__ . '/includes/conexion.php';

$id_cond = $_GET['id'] ?? 'nuevo';
$id_rele = $_GET['id_rele'] ?? null;

$cond = [];
$nombre_rele = '';

// Si no es nueva, cargamos la condición
if ($id_cond !== 'nuevo') {
    $query = "SELECT c.*, r.nombre AS nombre_rele 
              FROM reles_c c 
              LEFT JOIN reles r ON c.id_rele = r.id_rele 
              WHERE c.id_reles_c = ?";
    $stmt = mysqli_prepare($link, $query);
    mysqli_stmt_bind_param($stmt, "i", $id_cond);
    mysqli_stmt_execute($stmt);
    $cond = mysqli_stmt_get_result($stmt)->fetch_assoc();
    $nombre_rele = $cond['nombre_rele'] ?? '';
    $id_rele = $cond['id_rele'] ?? '';
}
?>

<div class="modal-header">
    <h5 class="modal-title">
        <?= ($id_cond === 'nuevo') 
            ? 'Nueva Condición de Relé: '. htmlspecialchars($id_rele)
            : 'Editando Rele'. $id_rele. ' -> Condición FV ID: ' . htmlspecialchars($id_cond) . 
              ($nombre_rele ? ' del Relé: ' . htmlspecialchars($nombre_rele) : '') ?>
    </h5>
    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
</div>

<div class="modal-body">
    <form action="reles_condicion_guardar.php" method="post" id="formCondicion">
        <input type="hidden" name="id" value="<?= $cond['id_reles_c'] ?? '' ?>">
        <input type="hidden" name="id_rele" value="<?= $id_rele ?>">
        <input type="hidden" id="openRelaysState" name="open_relays" value="">

        <div class="mb-3">
            <label class="form-label">ID de Condición FV</label>
            <input type="number" name="id_condicion" class="form-control" required
                   value="<?= htmlspecialchars($cond['id_reles_c'] ?? '') ?>">
            <small class="text-muted">Introduce id unico --> ejemplo: 51101 (condicion 01 del rele 511)</small>         
        </div>

        <div class="mb-3">
            <label class="form-label">Operación</label>
            <select name="modo" class="form-select">
                <option value="ON" <?= ($cond['operacion'] ?? '') === 'ON' ? 'selected' : '' ?>>ON</option>
                <option value="OFF" <?= ($cond['operacion'] ?? '') === 'OFF' ? 'selected' : '' ?>>OFF</option>
            </select>
        </div>

        <div class="mb-3">
            <label class="form-label">Parámetro</label>
            <input list="parametros" name="variable" class="form-control" required
                   value="<?= htmlspecialchars($cond['parametro'] ?? '') ?>">
 
            <datalist id="parametros">
                <option value="SOC" label="Estado de carga (%)">
                <option value="Vbat" label="Voltaje de Batería (V)">
                <option value="Ibat" label="Corriente de Batería (A)">
                <option value="Iplaca" label="Corriente de Placas (A)">
                <option value="Vplaca" label="Voltaje en Placas (V)">
                <option value="Wplaca" label="Potencia de Placas (W)">
                <option value="PWM" label="Nivel de excedentes">
                <option value="Temp" label="Temperatura (°C)">
                <option value="Wconsumo" label="Potencia de Consumo (W)">
                <option value="Whn_bat" label="Energía descargada baterías (Wh)">
                <option value="Whp_bat" label="Energía cargada baterías(Wh)">
                <option value="Wh_bat" label="Energía neta batería (Wh)">
                <option value="Wbat" label="Potencia neta a batería (W)">
                <option value="Vred" label="Voltaje de Red (V)">
                <option value="Ired" label="Corriente de Red (A)">
                <option value="EFF" label="Eficiencia (%)">
                <option value="Whn_red" label="Energía importada de red (Wh)">
                <option value="Whp_red" label="Energía exportada a red (Wh)">
                <option value="Wh_red" label="Energía neta red (Wh)">
                <option value="Wred" label="Potencia neta red (W)">
                <option value="Aux1" label="Sensor auxiliar 1">
                <option value="Aux2" label="Sensor auxiliar 2">
            </datalist>
            <small class="text-muted">Variable que se evalúa → ejemplos: Vbat, Vplaca, PWM… o cualquier otro valor</small>
        </div>

        <div class="mb-3">
            <label class="form-label">Condición</label>
            <select name="condicion" class="form-control" required>
                <option value="">-- Selecciona una condición --</option>
                <option value=">" <?= ($cond['condicion'] ?? '') == '>' ? 'selected' : '' ?>>Mayor que</option>
                <option value=">=" <?= ($cond['condicion'] ?? '') == '>=' ? 'selected' : '' ?>>Mayor o igual que</option>
                <option value="<" <?= ($cond['condicion'] ?? '') == '<' ? 'selected' : '' ?>>Menor que</option>
                <option value="<=" <?= ($cond['condicion'] ?? '') == '<=' ? 'selected' : '' ?>>Menor o igual que</option>
                <option value="==" <?= ($cond['condicion'] ?? '') == '==' ? 'selected' : '' ?>>Igual a</option>
                <option value="!=" <?= ($cond['condicion'] ?? '') == '!=' ? 'selected' : '' ?>>Diferente de</option>
            </select>
            <small class="text-muted">Solo se permiten operadores válidos: >, >=, <, <=, ==, !=</small>
        </div>

        <div class="mb-3">
            <label class="form-label">Valor</label>
            <input type="number" name="valor" class="form-control" step="any" required
                   value="<?= htmlspecialchars($cond['valor'] ?? '') ?>">
        </div>

        <!-- Asistente de Condiciones Mejorado -->
        <div class="mb-3 border p-3 rounded">
            <h6><i class="bi bi-robot"></i> Asistente Inteligente de Condiciones</h6>
            <div class="input-group mb-2">
                <input type="text" id="textoCondicion" class="form-control" 
                       placeholder="Ej: 'Activar si SOC > 80%' o 'Apagar cuando Temp > 45°C'">
                <button class="btn btn-primary" type="button" id="btnGenerarCondicion">
                    <i class="bi bi-magic"></i> Generar
                </button>                
            </div>
            
            <div class="mb-2">
                <small class="text-muted">Ejemplos: 
                    <span class="condicion-ejemplo" onclick="document.getElementById('textoCondicion').value='enciende con SOC > 80'">ON-> SOC > 80%</span>
                    <span class="condicion-ejemplo" onclick="document.getElementById('textoCondicion').value='enciende con Wplaca mayor de 1000'">ON-> Wplaca > 1000W</span>
                    <span class="condicion-ejemplo" onclick="document.getElementById('textoCondicion').value='apagar si temperatura < 45'">OFF-> Temp < 45°C</span>
                </small>
            </div>
            
            <div id="resultadoCondicion" class="mt-2" style="display:none;"></div>
        </div>
    </form>
</div>

<div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
    <button type="submit" form="formCondicion" class="btn btn-primary" onclick="saveOpenRelaysState()">Guardar</button>
</div>

<style>
    .condicion-ejemplo {
        cursor: pointer;
        color: #0d6efd;
        text-decoration: underline;
        margin-right: 10px;
        font-weight: 500;
    }
    .condicion-ejemplo:hover {
        color: #0a58ca;
    }
    
    .highlight {
        background-color: #fff3cd;
        transition: background-color 0.5s ease;
    }
    
    #resultadoCondicion {
        transition: all 0.3s ease;
    }
    
</style>

<script>
// Guardar estado de relés abiertos antes de enviar el formulario
function saveOpenRelaysState() {
    const openRelays = JSON.parse(sessionStorage.getItem('openRelays') || '[]');
    document.getElementById('openRelaysState').value = JSON.stringify(openRelays);
}



// Validación del formulario
document.getElementById('formCondicion').addEventListener('submit', function(e) {
    const valor = parseFloat(this.elements['valor'].value);
    const parametro = this.elements['variable'].value;
    
    if (isNaN(valor)) {
        alert('El valor debe ser un número válido');
        e.preventDefault();
        return false;
    }
    
    // Validaciones específicas por parámetro
    if (parametro === 'SOC' && (valor < 0 || valor > 100)) {
        alert('El SOC debe estar entre 0 y 100');
        e.preventDefault();
        return false;
    }
    
    if (parametro === 'Temp' && valor < -20) {
        alert('La temperatura no puede ser menor a -20°C');
        e.preventDefault();
        return false;
    }
    
    return true;
});

// Restaurar estado al abrir el modal
document.addEventListener('DOMContentLoaded', function() {
    const openRelays = JSON.parse(sessionStorage.getItem('openRelays') || '[]');
    if(openRelays.length > 0) {
        const input = document.getElementById('openRelaysState');
        if(input) input.value = JSON.stringify(openRelays);
    }
    
    // Enfocar el campo de texto del asistente al abrir el modal
    setTimeout(() => {
        document.getElementById('textoCondicion').focus();
    }, 300);
});
</script>