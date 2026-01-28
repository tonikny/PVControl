<?php
session_start();
require_once __DIR__ . '/includes/cabecera.php';
$seguridad = include __DIR__ . '/includes/seguridad.php';

// 1. Procesar formulario de autenticación
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['password'])) {
    if (password_verify($_POST['password'], $seguridad['clave_hash'])) {
        $_SESSION['modo_edicion'] = true;
        header("Location: reles.php");
        exit;
    } else {
        $error_clave = "Clave incorrecta";
    }
}

// 2. Procesar cierre de sesión
if (isset($_GET['cerrar_edicion'])) {
    unset($_SESSION['modo_edicion']);
    header("Location: reles.php");
    exit;
}
?>

<script src="https://code.jquery.com/jquery.js"></script>
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/themes/grid.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<script src="/script/ejemplos_condiciones_avanzadas.js"></script>
<script src="/Parametros_Web_DIST.js"></script>
<script src="/Parametros_Web.js"></script> 



<div class="container mt-3" style="position: relative; z-index: 1;">
    <!-- -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
        <?php if (!isset($_SESSION['modo_edicion'])): ?>
            <button class="btn btn-primary" id="btnLoginManual">
                <i class="bi bi-lock-fill"></i> Editar Tablas
            </button>
        <?php else: ?>
            <div>
                <a href="?cerrar_edicion=1" class="btn btn-danger">
                    <i class="bi bi-unlock-fill"></i> Cerrar edición
                </a>
            </div>
        <?php endif; ?>
    </div>

    <?php if (isset($_SESSION['modo_edicion'])): ?>
        <div class="alert alert-success mb-3">
            <i class="bi bi-check-circle-fill"></i> Modo edición habilitado
        </div>
    <?php endif; ?>
    
    <!-- Modal de Login Personalizado -->
    <div id="customModal" class="custom-modal">
        <div class="custom-modal-content">
            <div class="custom-modal-header">
                <h5>Autenticación requerida</h5>
                <button type="button" class="custom-modal-close">&times;</button>
            </div>
            <div class="custom-modal-body">
                <?php if(isset($error_clave)): ?>
                    <div class="custom-alert-danger"><?= $error_clave ?></div>
                <?php endif; ?>
                <form method="post">
                    <div class="custom-form-group">
                        <label>Contraseña:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="custom-btn-primary">Acceder</button>
                </form>
            </div>
        </div>
    </div>


    <!-- Grafico Reles -->
    <div id="container_reles" style="width: 90%; height: 250px; margin-left: 1%;"></div>


    <!-- Tabla reles -->
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2><i class="bi bi-plug"></i> Gestión de Relés</h2>
        <?php if (isset($_SESSION['modo_edicion'])): ?>
            <button class="btn btn-success me-2" onclick="abrirModalEditar()">
                <i class="bi bi-plus-circle"></i> Nuevo Relé
            </button>
        <?php endif; ?>
    </div>

    <table class="table table-striped table-hover align-middle tabla-reles">
        
        <thead class="table-dark">
            <tr>
                <th>
                    ID
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                       title="Identificador del relé en la base de datos (3 digitos):"                       
                       data-bs-content="
                           <b>1XX</b>: Relés personalizados en Parametros_FV.py<br>
                           <b>2XX</b>: Reles via WiFi (ESP32 con micropython por MQTT)<br>
                           <b>3XX</b>: Relés asociados a PCF8574 ( bus I2C)<br>
                           <b>4XX</b>: Relés asociados a puertos GPIO de la Raspberry<br>
                           <b>5XX</b>: Relés via WiFI (TASMOTA por MQTT tipo ON/OFF)<br>
                           <b>6XX</b>: Relés via WiFi (TASMOTA por MQTT con control de potencia)<br>
                           <b>8XX</b>: Relés via WiFi (TUYA)">
                    </i>
                </th>
                <th>
                    Nombre
                    <i class="bi bi-question-circle text-white"
                        tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                        data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                        title="Nombre relé."
                        data-bs-content="Nombre descriptivo del relé">
                    </i>
                </th>
                <th>
                    Modo
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                       title="Modo de funcionamiento del Relé:"                      
                       data-bs-content="
                            <b>ON</b> : El relé en ON siempre independientemente de las Condiciones<br>
                            <b>OFF</b>: El relé en OFF siempre independientemente de las Condiciones<br>
                            <b>PRG</b>: El relé en ON u OFF dependiendo de las Condiciones<br>
                            <b>MAN</b>: El relé en ON u OFF dependiendo de las Condiciones pero no realizara refresco">
                    </i>
                </th>
                <th>
                    Estado
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                       title="Estado de encendido del Relé:"                      
                       data-bs-content="
                            <b>0</b>: Relé totalmente apagado<br>
                            ...<br>
                            <b>30</b>: Relé al 30% de potencia ( aplicable a reles SSR)<br>
                            ...<br>
                            <b>100</b>: Relé totalmente encendido" >
                    </i>
                </th>
                <th>
                    Grab.
                    <i class="bi bi-question-circle text-white" 
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                       title="Graba datos de conmutaciones en Base de datos">
                    </i>
                </th>
                <th>
                    Salto
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                       title="Incremento de Estado con el que se realiza el control de potencia.">
                    </i>
                </th>
                <th>
                    Prior.
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"
                       title="Prioridad en la asignación de excedentes"
                       data-bs-content="
                            <b>0</b>: Relé sin asignación de excedentes<br>
                            <b>1</b>: Máxima prioridad para asignación de excedentes<br>
                            <b>2</b>: Cuando los relés con prioridad 1 estén al 100% se asignará los excedentes a prioridad 2.<br>
                            <b>3</b>: ...">
                    </i>
                </th>
                <th>
                    Pot.
                    <i class="bi bi-question-circle text-white" 
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                       title="Potencia asociada al relé, en vatios. (dato solo usado a título informativo)">
                    </i>
                </th>
                <th>
                    Ret.
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                       title="Tiempo mínimo que estará el relé en cada estado ON/OFF.">
                    </i>
                </th>
                <th>
                    Calib.
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                       title="Calibración para control de potencia en SSR por ángulo de fase."></i>
                </th>

                <?php if (isset($_SESSION['modo_edicion'])): ?>
                    <th class="text-center">
                        Modo
                        <i class="bi bi-question-circle text-white"
                           tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                           data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                           title="Permite cambiar entre modos de funcionamiento del relé.">
                        </i>
                    </th>
                    <th class="text-center">
                        Acciones
                        <i class="bi bi-question-circle text-white" 
                           tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                           data-bs-trigger="focus" data-bs-custom-class="popover-custom" 
                           title="Botones para editar o eliminar el relé.">
                        </i>
                    </th>
                <?php endif; ?>

                <th>
                    Condiciones
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"                    
                       title="Condiciones que definen el comportamiento del relé.">
                    </i>
                </th>
                <th>
                    Gráfico
                    <i class="bi bi-question-circle text-white"
                       tabindex="0" style="cursor: help;" data-bs-toggle="popover" data-bs-html="true"
                       data-bs-trigger="focus" data-bs-custom-class="popover-custom"                    
                       title="Gráficos del comportamiento del relé.">
                    </i>
                </th>
            </tr>

        </thead>
        <tbody>
        <?php
        $q = "SELECT r.*, 
                (SELECT COUNT(*) FROM reles_c WHERE id_rele=r.id_rele) AS cnt_c,
                (SELECT COUNT(*) FROM reles_h WHERE id_rele=r.id_rele) AS cnt_h
            FROM reles r ORDER BY r.id_rele";
        $res = mysqli_query($link, $q);
        while ($row = mysqli_fetch_assoc($res)):
            $id = $row['id_rele'];
            $hasCond = ($row['cnt_c'] + $row['cnt_h'] > 0);
            $btnColor = $hasCond ? 'btn-success' : 'btn-secondary';
        ?>
            <tr>
                <td><strong><?= $id ?></strong></td>
                <td><strong><?= htmlspecialchars($row['nombre']) ?></strong></td>               
                <?php
                $modo = $row['modo'];
                $estado = $row['estado'];

                $img = match(true) {
                    $modo === 'ON' => 'botonon.png',
                    $modo === 'OFF' => 'botonoff.png',
                    $modo === 'PRG' => 'botonprg.png',
                    $modo === 'MAN' && $estado > 0 => 'botonmanualon.png',  // MAN con estado > 0
                    $modo === 'MAN' => 'botonmanualoff.png',  // MAN con estado = 0
                    default => '',
                };
                ?>
                <td>
                    <img src="img/<?= $img ?>" alt="<?= $modo ?>" style="height: 40px;">
                </td>
                
                <!-- <td><?= $row['estado'] ?></td> -->
                <td>
                    <?php 
                    $estado = (int)$row['estado'];
                    // Asegurarnos que el valor esté entre 0 y 100
                    $estado = max(0, min(100, $estado));
                    $color = ($estado == 100) ? 'dc3545' : (($estado == 0) ? '6c757d' : 'ffa500');
                    $claseTexto = ($estado == 100) ? 'text-danger' : (($estado == 0) ? 'text-secondary' : 'text-warning');
                    ?>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1" style="height: 20px;">
                            <div class="progress-bar" 
                                 role="progressbar" 
                                 style="width: <?= $estado ?>%; background-color: #<?= $color ?>;" 
                                 aria-valuenow="<?= $estado ?>" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                            </div>
                        </div>
                        <span class="ms-2 fw-bold <?= $claseTexto ?>">
                            <?= $estado ?>%
                        </span>
                    </div>
                </td>
                              
                <td class="text-center"><?= htmlspecialchars($row['grabacion']) ?></td>
                <td class="text-center"><?= $row['salto'] ?></td>
                <td class="text-center"><?= $row['prioridad'] ?></td>
                <td class="text-center"><?= $row['potencia'] ?></td>
                <td class="text-center"><?= $row['retardo'] ?></td>
                <td class="text-truncate" style="max-width:50px;"><?= htmlspecialchars($row['calibracion']) ?></td>

                <?php if (isset($_SESSION['modo_edicion'])): ?>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm">
                            <button class="btn p-1" onclick="actualizarModo(<?= $id ?>,'PRG')" title="Programado">
                                <img src="img/botonprg.png" style="width:40px;">
                            </button>
                            <button class="btn p-1" onclick="actualizarModo(<?= $id ?>,'ON')" title="Encender">
                                <img src="img/botonon.png" style="width:40px;">
                            </button>
                            <button class="btn p-1" onclick="actualizarModo(<?= $id ?>,'OFF')" title="Apagar">
                                <img src="img/botonoff.png" style="width:40px;">
                            </button> 
                            <button class="btn p-1" onclick="actualizarModo(<?= $id ?>,'MAN_ON')" title="Manual ON">
                                <img src="img/botonmanualon.png" style="width:40px;">
                            </button>
                            <button class="btn p-1" onclick="actualizarModo(<?= $id ?>,'MAN_OFF')" title="Manual_OFF">
                                <img src="img/botonmanualoff.png" style="width:40px;">
                            </button>
                            
                            
                        </div>
                    </td>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm">
                            <button class="btn p-1" onclick="abrirModalEditar(<?= $id ?>)" title="Editar">
                                <img src="img/edit.png" style="width:40px;">
                            </button>
                            <button class="btn p-1" onclick="confirmarBorrado(<?= $id ?>)" title="Borrar">
                                <img src="img/delete.png" style="width:40px;">
                            </button>
                        </div>
                    </td>
                <?php endif; ?>

                <td class="text-center">
                    <button class="btn btn-sm <?= $btnColor ?>" onclick="toggleCond(<?= $id ?>)" title="Ver condiciones" data-rele-id="<?= $id ?>">
                        <i class="bi bi-list-check"></i>
                        <?= $hasCond ? '' : '' ?>
                    </button>
                </td>
                <td class="text-center">
                    <button class="btn btn-sm btn-info" 
                            onclick="mostrarGraficos(<?= $id ?>, '<?= htmlspecialchars($row['nombre']) ?>')" 
                            title="Ver gráficos">
                        <i class="bi bi-graph-up"></i>
                    </button>
                </td>                
                
            </tr>
            <!-- Fila condiciones combinadas -->
            <tr id="cond_<?= $id ?>" style="display:none;">
                <td colspan="<?= isset($_SESSION['modo_edicion']) ? 14 : 12 ?>">
                    <div class="card p-2 border">
                        
                        <?php
                        // reles_c
                        $qc = mysqli_query($link, "SELECT * FROM reles_c WHERE id_rele=$id");
                        $hay_condiciones = mysqli_num_rows($qc) > 0;
                        ?>

                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">
                                Condiciones FV
                                <i class="bi bi-question-circle text-muted" style="cursor: help;"
                                   title="Condiciones para poner en ON u OFF el relé. 
            Si hay multiples condiciones de ON u OFF la lógica es: 
                - Para pasar a ON es necesario que se cumplan TODAS las condiciones de ON, 
                - Para OFF solo es necesario que se cumpla una de las condiciones de OFF">
                                </i>
                            </h6>

                            <?php if (isset($_SESSION['modo_edicion'])): ?>
                                <button class="btn btn-sm btn-success" onclick="abrirModalNuevaCond(<?= $id ?>)">
                                    <i class="bi bi-plus-circle"></i> Nueva Condición FV
                                </button>
                            <?php endif; ?>
                        </div>

                        <?php if ($hay_condiciones): ?>
                            <table class="table table-sm table-bordered mb-3">
                                <thead>
                                    <tr>
                                        <th class="text-center">Id</th>
                                        <th class="text-center">Operación</th>
                                        <th class="text-center">Parámetro</th>
                                        <th class="text-center">Condición</th>
                                        <th class="text-center">Valor</th>
                                        <?php if (isset($_SESSION['modo_edicion'])): ?>
                                            <th class="text-center">Acciones</th>
                                        <?php endif; ?>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php while ($c = mysqli_fetch_assoc($qc)): ?>
                                        <tr>
                                            <td class="text-center"><?= htmlspecialchars($c['id_reles_c']) ?></td>
                                            <td class="text-center"><?= htmlspecialchars($c['operacion']) ?></td>
                                            <td class="text-center"><?= htmlspecialchars($c['parametro']) ?></td>
                                            <td class="text-center"><?= htmlspecialchars($c['condicion']) ?></td>
                                            <td class="text-center"><?= $c['valor'] ?></td>
                                            <?php if (isset($_SESSION['modo_edicion'])): ?>
                                                <td class="text-center">
                                                    <button class="btn btn-sm btn-outline-primary me-1 p-0 px-2" 
                                                        onclick="abrirModalEditarCond(<?= $c['id_reles_c'] ?>)">
                                                        Editar
                                                    </button>
                                                    <button class="btn btn-sm btn-outline-danger p-0 px-2" 
                                                        onclick="borrarCond(<?= $c['id_reles_c'] ?>)">
                                                        Borrar
                                                    </button>
                                                </td>
                                            <?php endif; ?>
                                        </tr>
                                    <?php endwhile; ?>
                                </tbody>
                            </table>
                        <?php endif; 

                        // reles_h
                        $qh = mysqli_query($link, "SELECT * FROM reles_h WHERE id_rele=$id");
                        $hay_horarias = mysqli_num_rows($qh) > 0;
                        ?>

                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">
                                Condiciones Horarias
                                <i class="bi bi-question-circle text-muted" style="cursor: help;"
                                   title="Franjas horarias donde funcionan las condiciones FV. 
        Fuera de estas franjas horarias el relé se pondrá en OFF. 
        Para que el relé se ponga en ON dentro de una franja horaria es necesario que exista y se cumpla las condiciones FV de ON establecidas">
                                </i>
                            </h6>
                            <?php if (isset($_SESSION['modo_edicion'])): ?>
                                <button class="btn btn-sm btn-success" onclick="abrirModalNuevaHor(<?= $id ?>)">
                                    <i class="bi bi-plus-circle"></i> Nueva Condición Horaria
                                </button>
                            <?php endif; ?>
                        </div>

                        <?php if ($hay_horarias): ?>
                            <table class="table table-sm table-bordered mb-0">
                                <thead>
                                    <tr>
                                        <th class="text-center">Id</th>
                                        <th class="text-center">Parámetro</th>
                                        <th class="text-center">Hora ON</th>
                                        <th class="text-center">Hora OFF</th>
                                        <?php if (isset($_SESSION['modo_edicion'])): ?>
                                            <th class="text-center">Acciones</th>
                                        <?php endif; ?>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php while ($h = mysqli_fetch_assoc($qh)): ?>
                                        <tr>
                                            <td class="text-center"><?= htmlspecialchars($h['id_reles_h']) ?></td>
                                            <td class="text-center"><?= htmlspecialchars($h['parametro_h']) ?></td>
                                            <td class="text-center"><?= $h['valor_h_ON'] ?></td>
                                            <td class="text-center"><?= $h['valor_h_OFF'] ?></td>
                                            <?php if (isset($_SESSION['modo_edicion'])): ?>
                                                <td class="text-center">
                                                    <button class="btn btn-sm btn-outline-primary me-1 p-0 px-2" 
                                                        onclick="abrirModalEditarHor(<?= $h['id_reles_h'] ?>)">
                                                        Editar
                                                    </button>
                                                    <button class="btn btn-sm btn-outline-danger p-0 px-2" 
                                                        onclick="borrarHor(<?= $h['id_reles_h'] ?>)">
                                                        Borrar
                                                    </button>
                                                </td>
                                            <?php endif; ?>
                                        </tr>
                                    <?php endwhile; ?>
                                </tbody>
                            </table>
                        <?php endif; ?>
                    </div>
                </td>
            </tr>
        <?php endwhile; ?>
        </tbody>
    </table>

    <div class="section-divider mt-5 mb-4">
        <hr class="border-2 border-top border-primary">
        <div class="d-flex justify-content-center">
            <div class="px-3 bg-white text-primary fs-4">
                <i class="bi bi-cpu"></i> Configuración Avanzada
            </div>
        </div>
        <hr class="border-2 border-top border-primary">
    </div>
 
 
 
    <!-- Tabla de Condiciones -->
    <div class="mt-5">
    
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2><i class="bi bi-cpu"></i> Condiciones Avanzadas</h2>
            <div> <!-- Contenedor para los botones -->
                <?php if (isset($_SESSION['modo_edicion'])): ?>
                    <button class="btn btn-success me-2" onclick="abrirModalNuevaCondicionGeneral()">
                        <i class="bi bi-plus-circle"></i> Nueva Condición
                    </button>
                <?php endif; ?>
                <button id="btnHelp" class="btn btn-info btn-sm">
                    <i class="bi bi-question-circle"></i> Ejemplos Condiciones
                </button>
                
                
            </div>
        </div>
        
        <table class="table table-striped table-hover align-middle">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th class="text-center">Activado</th>
                    <th>Condición 1</th>
                    <th>Condición 2</th>
                    <th>Acción</th>
                    <th>Descripción</th>
                    <?php if (isset($_SESSION['modo_edicion'])): ?>
                        <th class="text-center">Acciones</th>
                    <?php endif; ?>
                </tr>
            </thead>
            <tbody>
                <?php
                $query = "SELECT * FROM condiciones ORDER BY id_condicion";
                $result = mysqli_query($link, $query);
                
                while ($condicion = mysqli_fetch_assoc($result)):
                ?>
                    <tr>
                        <td><?= $condicion['id_condicion'] ?></td>
                        <td class="text-center">
                            <?php if (isset($_SESSION['modo_edicion'])): ?>
                                <div class="form-check form-switch d-flex justify-content-center">
                                    <input class="form-check-input" type="checkbox" role="switch" 
                                        id="activado_<?= $condicion['id_condicion'] ?>" 
                                        <?= $condicion['activado'] ? 'checked' : '' ?>
                                        onchange="actualizarActivado(<?= $condicion['id_condicion'] ?>, this.checked)">
                                </div>
                            <?php else: ?>
                                <?= $condicion['activado'] ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-x-circle-fill text-danger"></i>' ?>
                            <?php endif; ?>
                        </td>
                        <td class="texto-ajustable"><?= nl2br(htmlspecialchars($condicion['condicion1'])) ?></td>
                        <td class="texto-ajustable"><?= nl2br(htmlspecialchars($condicion['condicion2'])) ?></td>                       
                        <td class="texto-ajustable"><?= nl2br(htmlspecialchars($condicion['accion'])) ?></td>
                        <td class="texto-ajustable"><?= nl2br(htmlspecialchars($condicion['descripcion'])) ?></td>

                        <?php if (isset($_SESSION['modo_edicion'])): ?>
                            <td class="text-center">
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary" 
                                        onclick="abrirModalEditarCondicionGeneral(<?= $condicion['id_condicion'] ?>)">
                                        <i class="bi bi-pencil-fill"></i> Editar
                                    </button>
                                    <button class="btn btn-outline-danger" 
                                        onclick="confirmarBorradoCondicion(<?= $condicion['id_condicion'] ?>)">
                                        <i class="bi bi-trash-fill"></i> Borrar
                                    </button>
                                </div>
                            </td>
                        <?php endif; ?>
                    </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>

</div>

<!-- Modal -->
<div class="modal fade" id="modalEditar"><div class="modal-dialog"><div class="modal-content">
    <div class="modal-body" id="contenidoModal"></div>
</div></div></div>

<!-- Modal para gráficos -->
<div class="modal fade" id="modalGraficos" tabindex="-1" aria-labelledby="modalGraficosLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalGraficosLabel"></h5> <!-- Se actualizará con JS -->
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <!-- Gráfico 1 - Tiempo ON con conmutaciones -->
                <div id="grafico1" style="height: 300px; margin-bottom: 30px;"></div>
                
                <!-- Gráfico 2 - Potencia -->
                <div id="grafico2" style="height: 300px;"></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        </div>
    </div>
</div>


<!-- Modal de ayuda condiciones avanzadas -->
<div class="modal fade modal-condiciones" id="helpModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">
                    <i class="bi bi-code-square"></i> Ayuda de Condiciones Avanzadas
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" id="modalHelpContent">
                <!-- Contenido se cargará aquí dinámicamente -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle"></i> Cerrar
                </button>
            </div>
        </div>
    </div>
</div>


<style>
    
    .highlight {
        background-color: #fff3cd;
        transition: background-color 0.5s ease;
    }
    
    .modal-condiciones .modal-dialog {
        max-width: 90%;
        width: 1500px;
    }
</style>


<script>

// Función para guardar el estado de la página
function savePageState() {
    sessionStorage.setItem('scrollPosition', window.scrollY);
    const openRelays = [];
    document.querySelectorAll('tr[id^="cond_"]').forEach(row => {
        if(row.style.display !== 'none') {
            const id = row.id.split('_')[1];
            openRelays.push(id);
        }
    });
    sessionStorage.setItem('openRelays', JSON.stringify(openRelays));
}

// Configuración inicial cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // 1. Restaurar estado de la página
    restoreOpenRelays();
    
    // 2. Restaurar posición de scroll
    const urlParams = new URLSearchParams(window.location.search);
    if(urlParams.has('keep_scroll')) {
        const savedPosition = sessionStorage.getItem('scrollPosition');
        if(savedPosition) {
            setTimeout(() => {
                window.scrollTo({ top: savedPosition, behavior: 'instant' });
            }, 0);
        }
    }
    
    // 3. Limpiar storage
    sessionStorage.removeItem('scrollPosition');
    
    // 4. Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });
    
    // 5. Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function(el) {
        new bootstrap.Popover(el, {
            customClass: 'popover-custom'
        });
    });
    
    // 6. Configurar el modal de login
    const btnLogin = document.getElementById('btnLogin');
    const modalLogin = document.getElementById('modalLogin');
    
    if (btnLogin && modalLogin) {
        const myModal = new bootstrap.Modal(modalLogin);
        
        btnLogin.addEventListener('click', function(e) {
            e.preventDefault();
            myModal.show();
            
            // Enfocar el campo de contraseña después de que el modal se muestre
            modalLogin.addEventListener('shown.bs.modal', function() {
                const input = modalLogin.querySelector('input[name="password"]');
                if (input) input.focus();
            }, { once: true });
        });
    }
    
    // 7. Configurar evento antes de cerrar la página
    window.addEventListener('beforeunload', savePageState);
});

//JavaScript para manejar el modal personalizado
document.addEventListener('DOMContentLoaded', function() {
    // Modal personalizado
    const btnLogin = document.getElementById('btnLoginManual');
    const modal = document.getElementById('customModal');
    const closeBtn = document.querySelector('.custom-modal-close');
    
    if (btnLogin && modal) {
        // Abrir modal
        btnLogin.addEventListener('click', function() {
            modal.style.display = 'flex';
            document.querySelector('#customModal input[name="password"]').focus();
        });
        
        // Cerrar modal
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        // Cerrar al hacer clic fuera
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // Cerrar con ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
        });
    }
});


// Almacenar estado de los relés desplegados
function saveOpenRelays() {
    const openRelays = [];
    document.querySelectorAll('tr[id^="cond_"]').forEach(row => {
        if(row.style.display !== 'none') {
            const id = row.id.split('_')[1];
            openRelays.push(id);
        }
    });
    sessionStorage.setItem('openRelays', JSON.stringify(openRelays));
}

// Restaurar estado condiciones reles al cargar la página
function restoreOpenRelays() {
    const openRelays = JSON.parse(sessionStorage.getItem('openRelays') || '[]');
    openRelays.forEach(id => {
        const row = document.getElementById('cond_' + id);
        if(row) row.style.display = '';
    });
}

// Función para mostrar/ocultar condiciones
function toggleCond(id) {
    const r = document.getElementById('cond_' + id);
    r.style.display = (r.style.display === 'none') ? '' : 'none';
    saveOpenRelays();
}

// Función para mostrar los gráficos
function mostrarGraficos(id, nombre) {
    // Actualizar el título del modal
    document.getElementById('modalGraficosLabel').textContent = `Gráficos del Relé ${id}: ${nombre}`;
    
    // Mostrar el modal
    var modal = new bootstrap.Modal(document.getElementById('modalGraficos'));
    modal.show();
    
    // Cargar datos y crear gráficos
    cargarDatosGraficos(id);
}

// Función para cargar datos y crear gráficos
function cargarDatosGraficos(id_rele) {
    // Obtener datos para ambos gráficos
    fetch(`reles_graficos.php?id_rele=${id_rele}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                crearGraficoTiempoON(data.grafico1, id_rele);
                crearGraficoPotencia(data.grafico2, id_rele); 
            } else {
                console.error('Error del servidor:', data.error);
                mostrarErrorGrafico(data.error);
            }
        })
        .catch(error => {
            console.error('Error al cargar datos:', error);
            mostrarErrorGrafico(error.message);
        });
}

// Función para crear el gráfico de tiempo ON
function crearGraficoTiempoON(datos, id_rele) {
    
    Highcharts.chart('grafico1', {        
        
        chart: {
            type: 'column'
        },
        title: {
            text: 'Tiempo ON y Conmutaciones - Relé ' + id_rele
        },
        subtitle: {
            text: 'Últimos 7 días'
        },
        credits: {
            enabled: false
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { day: '%e %b' }
        },
        yAxis: {
            title: { text: 'Horas' },
            min: 0,
            maxPadding: 0.2,
            labels: {enabled: false},
            dateTimeLabelFormats: {
                second: '%H:%M:%S',
                minute: '%H:%M:%S',
                hour: '%H:%M:%S',
                day: '%H:%M:%S',
                week: '%H:%M:%S',
                month: '%H:%M:%S',
                year: '%H:%M:%S'
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            column: {
                colorByPoint: true,
                dataLabels: {
                    enabled: true,
                    align: 'center',
                    verticalAlign: 'top',
                    y: -40,
                    style: {
                        color: '#333',
                        textOutline: '1px contrast',
                        fontSize: '11px',
                        fontWeight: 'bold'
                    },
                    formatter: function() {
                        return `<span style="color:#0056b3">${secondsTimeSpanToHMS(this.y/1000)}</span><br>
                                <span style="color:#555">${this.point.nconmutaciones} conmut.</span>`;
                    }
                }
            }
        },
        tooltip: {
            formatter: function() {
                const fecha = Highcharts.dateFormat('%A %e %b %Y', this.point.x);
                return `<div style="min-width:150px">
                          <b>${fecha}</b><br>
                          <hr style="margin:5px 0">
                          Tiempo ON: <b>${secondsTimeSpanToHMS(this.point.y/1000)}</b><br>
                          Conmutaciones: <b>${this.point.nconmutaciones}</b>
                        </div>`;
            },
            useHTML: true,
            style: {
                padding: '10px'
            }
        },

        series: [{
            name: 'Tiempo ON',
            data: datos.map(item => ({
                x: new Date(item.Fecha).getTime(),
                y: item.segundos*1000,
                nconmutaciones: item.nconmutaciones
            }))
        }]
    });
}

// Función para crear el gráfico de cambio de estado
function crearGraficoPotencia(datos, id_rele) {
    // Procesar datos para mantener el valor hasta el siguiente cambio
    let processedData = [];
    
    if (datos.length === 0) {
        Highcharts.chart('grafico2', {
            title: {
                text: 'No hay datos de potencia para el relé ' + id_rele
            }
        });
        return;
    }

    // Ordenar por tiempo por si acaso
    datos.sort((a, b) => new Date(a.Tiempo) - new Date(b.Tiempo));

    // Agregar punto inicial (comenzamos en 0 si no hay datos anteriores)
    const primerPunto = new Date(datos[0].Tiempo);
    primerPunto.setHours(0, 0, 0, 0);
    processedData.push([primerPunto.getTime(), 0]);

    // Procesar cada punto de datos
    for (let i = 0; i < datos.length; i++) {
        const tiempo = new Date(datos[i].Tiempo).getTime();
        const valor = datos[i].valor_rele;
        
        // Agregar punto de transición (valor anterior hasta este momento)
        if (i > 0) {
            const valorAnterior = datos[i-1].valor_rele;
            processedData.push([tiempo, valorAnterior]);
        }
        
        // Agregar nuevo valor
        processedData.push([tiempo, valor]);
    }

    // Agregar punto final (extender hasta ahora)
    const ahora = new Date().getTime();
    const ultimoValor = datos.length > 0 ? datos[datos.length-1].valor_rele : 0;
    processedData.push([ahora, ultimoValor]);

    // Crear el gráfico

    Highcharts.setOptions({
        global: {
          useUTC: false
          },
          
        time: {
            timezone: zona_horaria
        },

        lang: {
          months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
          weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
          shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
          rangeSelectorFrom: "Desde",
          rangeSelectorTo: "A",
          printChart: "Imprimir gráfico",
          loading: "Cargando..."
          }
    });

        

    Highcharts.chart('grafico2', {
      
        chart: {
            type: 'line',
            zoomType: 'x'
        },
        title: {
            text: 'Control de Potencia - Relé ' + id_rele
        },
        subtitle: {
            text: 'Últimos 7 días'
        },
        credits: {
            enabled: false
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e %b',
                hour: '%H:%M'
            }
        },
        yAxis: {
            title: {
                text: 'Potencia (%)'
            },
            min: 0,
            max: 120,
            tickInterval: 10,
            labels: {
                format: '{value}%'
            }
        },
        tooltip: {
            formatter: function() {
                return '<b>Relé ' + id_rele + '</b><br/>' +
                    Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                    'Potencia: <b>' + this.y + '%</b>';
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                step: 'left', // Esto crea el efecto de escalón
                marker: {
                    enabled: true,
                    radius: 3
                }
            }
        },
        series: [{
            name: 'Potencia',
            color: Highcharts.getOptions().colors[0],
            data: processedData
        }]
    });
}

// Función para formatear segundos a HH:MM:SS
function secondsTimeSpanToHMS(s) {
    var h = Math.floor(s / 3600);
    s -= h * 3600;
    var m = Math.floor(s / 60);
    s -= m * 60;
    return h + ":" + (m < 10 ? '0' + m : m) + ":" + (s < 10 ? '0' + s : s);
}



// Funciones formularios reles
function actualizarModo(id, cmd) {
    fetch(`reles_comando.php?comando=${cmd}&id=${id}`).then(r => r.ok && location.reload());
}

function abrirModalEditar(id) {
    fetch(id?'reles_editar.php?id='+id:'reles_editar.php')
        .then(r => r.text()).then(html=>{
            document.getElementById('contenidoModal').innerHTML=html;
            new bootstrap.Modal(document.getElementById('modalEditar')).show();
        });
}

function confirmarBorrado(id) {
    if(confirm('¿Borrar rele ' + id + '?')) {  
        fetch('reles_borrar.php?id='+id).then(()=>location.reload());
    }
}

function abrirModalEditarCond(id) {
    fetch('reles_condicion_editar.php?id='+id)
        .then(r => r.text())
        .then(html => {
            const modalContent = document.getElementById('contenidoModal');
            modalContent.innerHTML = html;
            new bootstrap.Modal(document.getElementById('modalEditar')).show();
        });
}

function abrirModalNuevaCond(id_rele) {
    fetch('reles_condicion_editar.php?id_rele='+id_rele).then(r=>r.text()).then(html=>{
        document.getElementById('contenidoModal').innerHTML=html;
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    });
}

function borrarCond(id) {
    if(confirm('¿Borrar condición FV ' + id + '?')) {
        fetch('reles_condicion_borrar.php?id='+id).then(()=>location.reload());
    }
}

function abrirModalEditarHor(id) {
    fetch('reles_horario_editar.php?id='+id).then(r=>r.text()).then(html=>{
        document.getElementById('contenidoModal').innerHTML=html;
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    });
}

function abrirModalNuevaHor(id_rele) {
    fetch('reles_horario_editar.php?id_rele='+id_rele).then(r=>r.text()).then(html=>{
        document.getElementById('contenidoModal').innerHTML=html;
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    });
}

function borrarHor(id) {
    if(confirm('¿Borrar horario ' + id + '?')) {
        fetch('reles_horario_borrar.php?id='+id).then(()=>location.reload());
    }
}

// Funciones para la tabla de condiciones avanzadas
function abrirModalNuevaCondicionGeneral() {
    fetch('condiciones_editar.php').then(r=>r.text()).then(html=>{
        document.getElementById('contenidoModal').innerHTML=html;
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    });
}

function abrirModalEditarCondicionGeneral(id) {
    fetch('condiciones_editar.php?id='+id).then(r=>r.text()).then(html=>{
        document.getElementById('contenidoModal').innerHTML=html;
        new bootstrap.Modal(document.getElementById('modalEditar')).show();
    });
}

function confirmarBorradoCondicion(id) {
    if (confirm('¿Estás seguro de querer eliminar la condición '+id+'?')) {
        fetch(`condiciones_borrar.php?id=${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la red');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Recargar la página o actualizar la tabla
                    location.reload();
                } else {
                    alert(data.error || 'Error al eliminar la condición '+ id);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al eliminar la condición');
            });
    }
}


function actualizarActivado(id, activado) {
    fetch('condiciones_activar.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `id=${id}&activado=${activado ? 1 : 0}`
    }).then(response => {
        if(!response.ok) {
            alert('Error al actualizar el estado');
        }
    });
}

// IA
function generarCondicion() {
    const texto = document.getElementById('textoCondicion').value;
    const idRele = document.querySelector('input[name="id_rele"]').value;
    
    if (!texto) {
        alert('Por favor, describe la condición');
        return;
    }

    fetch('reles_condicion_generar.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `texto=${encodeURIComponent(texto)}&id_rele=${idRele}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('resultadoCondicion').innerHTML = 
                `<div class="alert alert-danger">${data.error}</div>`;
            document.getElementById('resultadoCondicion').style.display = 'block';
        } else {
            aplicarCondicion(data.parametro, data.condicion, data.valor, data.modo);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('resultadoCondicion').innerHTML = 
            `<div class="alert alert-danger">Error al procesar la condición</div>`;
        document.getElementById('resultadoCondicion').style.display = 'block';
    });
}


function aplicarCondicion(parametro, condicion, valor, modo) {
    // Rellena los campos del formulario
    document.querySelector('input[name="variable"]').value = parametro;
    document.querySelector('select[name="condicion"]').value = condicion;
    document.querySelector('input[name="valor"]').value = valor;
    
    // Establecer el modo (ON/OFF) basado en lo detectado
    if (modo) {
        document.querySelector('select[name="modo"]').value = modo;
    } else {
        // Lógica alternativa si no se detectó modo explícito
        document.querySelector('select[name="modo"]').value = 
            condicion.includes('>') ? 'ON' : 'OFF';
    }
    
    // Mostrar resultado
    const resultadoDiv = document.getElementById('resultadoCondicion');
    resultadoDiv.innerHTML = `
        <div class="alert alert-success">
            Condición aplicada: ${parametro} ${condicion} ${valor} (Modo: ${modo || 'auto'})
        </div>
    `;
    resultadoDiv.style.display = 'block';
    
    // Enfocar el campo de valor para posibles ajustes
    document.querySelector('input[name="valor"]').focus();
    
    // En aplicarCondicion()
    const modoSelect = document.querySelector('select[name="modo"]');
    modoSelect.classList.add('highlight');
    setTimeout(() => {
        modoSelect.classList.remove('highlight');
    }, 2000);

}

document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'btnGenerarCondicion') {
        generarCondicion();
    }
});

// Actualizar grafico principal estado reles
$(function () {
	recibirDatosFV(); 
    
	Highcharts.setOptions({

	global: {
	   useUTC: false
	   },
	lang: {
	    months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
	    weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
	    shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
	    rangeSelectorFrom: "Desde",
	    rangeSelectorTo: "A",
	    printChart: "Imprimir gráfico",
	    loading: "Cargando..."
	    } 
	});

	chart_reles =new Highcharts.Chart({
	chart: {
	    renderTo: 'container_reles',
	    backgroundColor: null,//'#ffffff',//'#f2f2f2',
	    borderColor: null,
	    type: 'column',
	    shadow: false,
	    options3d: {
		enabled: true,
		alpha: 0,
		beta: 10,
		depth: 100,
		viewDistance: 25,
	    //backgroundColor: null,//'#ffffff',//'#f2f2f2',
	    //borderColor: null,
	   
	    },
	},

	plotOptions: {
	  column: {
	    dataLabels: {
		enabled: true,
		inside: true, //valor de la columna en el interior
		crop: false,
		overflow: 'none',
		//borderWidth: null,
		//borderColor: 'red',
	    },
	    enableMouseTracking: false
	  }
	},

	credits: {
	     enabled: false
	     },
	title: {
	      y:20,
	      text: 'SITUACION RELES'
	     },
	subtitle: {
	      text: null
	     },
	xAxis: {
	     categories: [] //Nombre_Reles()
	       },
	yAxis: {
	      gridLineWidth: 0,
	      minorGridLineWidth: 0,
	      gridLineColor: 'transparent',
	      min: 0,
	      max: 100,
	      //minPadding:0,
	      //maxPadding:0,
	      tickInterval: 10,
	      allowDecimals: false,
	      visible: true, //desactivar grid i resta
	      labels: {
		    enabled: true
	       },
	      title: {
		    enabled: false
	       }
	     },

	series: [{
		name: 'Estado Relés',
		colorByPoint: false,//Color aleatorio para cada columna de un rele
		color : '#2b5dc7',
		borderColor: '#303030',
		data: [],
		
		dataLabels: {
		    enabled: true, 
		    formatter: function() {
			return Highcharts.numberFormat(this.y,0) + " %"
		    }
		}
		}],

	navigation: {
	      buttonOptions: {
		enabled: false
	       }
	     },
	legend: {
	      enabled: false,
	      layout: 'vertical',
	      floating: true,
	      align: 'center',
	      verticalAlign: 'center',
	      //x: -100,
	      y: 30,
	      borderWidth: 0
	     },
	tooltip: {
	      formatter: function () {
		return '<b>' + this.series.name + '</b><br/>' +
		    this.point.y + ' ' + this.point.name.toLowerCase();
	       }
	     }

	});

	function recibirDatosFV() {
    // Solo actualizar si la pestaña está visible
    if (document.hidden) {
        setTimeout(recibirDatosFV, 3000);
        return;
    }

	$.ajax({
	url: 'datos_fv.php',
	success: function(data) {
	  try {             
	    // tiempo_sg, "%d-%B-%Y -- %H:%M:%S"
	    fecha = data['FV']['tiempo'];
            
	    chart_reles.setTitle({
              text: 'SITUACION RELES  - '+ fecha
                });
            
	    // Actualizacion Reles     
	    var t_Datos_Reles = [];
            
            for (var i in data['RELES']) {
                n= data['RELES'][i]['nombre']+'</br>'+data['RELES'][i]['modo']+'-P'+ data['RELES'][i]['prioridad']+'-'+
                  data['RELES'][i]['potencia']+'w-'+data['RELES'][i]['retardo']+'sg('+data['RELES'][i]['espera']+')';
                t_Datos_Reles.push([n,data['RELES'][i]['estado']]);
            }
            t_Datos_Reles.pop(); // quito el ultimo elemento dado que es la fecha
            
            chart_reles.series[0].setData(t_Datos_Reles);
            
            var tCategories = []; // se cambian los nombres en funcion de los datos recibidos
            for (i = 0; i < chart_reles.series[0].data.length; i++) {
                tCategories.push(chart_reles.series[0].data[i].name); 
            }
            chart_reles.xAxis[0].setCategories(tCategories);
            
	  }
	   
	  catch (e) {
	    var d = new Date();
	    s = d.getSeconds()
	    t = d.getHours() + ':' + d.getMinutes() + ':' + s;
		
	    grafica_t_real.setTitle({
		text: 'SIN RESPUESTA - Hora=' + t,
		 });      
	    }       
	  },
	  
	// código a ejecutar sin importar si la petición falló o no
	complete : function(xhr, status) {
	    setTimeout(recibirDatosFV, 3000);
	   },
	  
	cache: false
	});
	}

	function round(value, precision) {
		var multiplier = Math.pow(10, precision || 0);
		return Math.round(value * multiplier) / multiplier;
	}
});

document.querySelectorAll('.texto-ajustable').forEach(td => {
    const length = td.textContent.length;
    if (length > 100) td.style.fontSize = '0.8rem';
    if (length > 200) td.style.fontSize = '0.7rem';
});


// Panel de ayuda condiciones avanzadas

document.addEventListener('DOMContentLoaded', function() {
    const helpModal = new bootstrap.Modal('#helpModal');
    
    // Configurar botón de ayuda
    document.getElementById('btnHelp').addEventListener('click', function() {
        cargarEjemplosJson()
            .then(html => {
                document.getElementById('modalHelpContent').innerHTML = html;
                helpModal.show();
                
            });
    });
    
});

async function cargarEjemplosJson() {
    try {
        const response = await fetch('/ayuda/ejemplos_condiciones_avanzadas.json');
        if (!response.ok) throw new Error(`Error HTTP! estado: ${response.status}`);
        const data = await response.json();
        return generarTablaHTML(data.ejemplos);
    } catch (error) {
        console.error("Error al cargar ejemplos:", error);
        return generarMensajeError(error);
    }
}

function generarTablaHTML(ejemplos) {
    const columnas = [
        { nombre: 'condicion1', ancho: '25%', titulo: 'Condición 1', clase: 'condicion-cell' },
        { nombre: 'condicion2', ancho: '25%', titulo: 'Condición 2', clase: 'condicion-cell' },
        { nombre: 'accion', ancho: '25%', titulo: 'Acción', clase: 'accion-cell' },
        { nombre: 'descripcion', ancho: '25%', titulo: 'Descripción', clase: 'descripcion-cell' }
    ];

    return `
    <div class="table-responsive">
        <table class="table table-condiciones table-hover mb-0">
            <colgroup>
                ${columnas.map(col => `<col style="width: ${col.ancho}">`).join('')}
            </colgroup>
            <thead class="table-dark">
                <tr>
                    ${columnas.map(col => `<th>${col.titulo}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${ejemplos.map(ejemplo => generarFila(ejemplo, columnas)).join('')}
            </tbody>
        </table>
    </div>
    <div class="mt-3 p-3 bg-light border rounded">
        <h5><i class="bi bi-info-circle"></i> Uso avanzado</h5>
        <ul>
            <li>Ejemplos de condiciones avanzadas</li>
            <li>Puedes desplazarte verticalmente si el contenido es largo</li>
        </ul>
    </div>`;
}

function generarFila(ejemplo, columnas) {
    return `
    <tr>
        ${columnas.map(col => `
        <td class="${col.clase}">
            ${formatearContenido(ejemplo[col.nombre], col.nombre)}
        </td>`).join('')}
    </tr>`;
}

function formatearContenido(texto, tipo) {
    if (!texto || texto.trim() === '') return '<span class="text-muted">-</span>';
    
    const textoConSaltos = texto.replace(/\\n/g, '\n');
    
    switch(tipo) {
        case 'condicion1':
        case 'condicion2':
            return `
            <div class="position-relative">
                <code>${escapeHtml(textoConSaltos)}</code>
            </div>`;
            
        case 'accion':
            return `
            <div class="position-relative">
                <pre>${escapeHtml(textoConSaltos)}</pre>
            </div>`;
            
        case 'descripcion':
            return textoConSaltos.split('\n')
                .filter(p => p.trim())
                .map(p => `<p class="mb-2">${escapeHtml(p)}</p>`)
                .join('');
            
        default:
            return escapeHtml(textoConSaltos);
    }
}

function generarMensajeError(error) {
    return `
    <div class="alert alert-danger">
        <h5><i class="bi bi-exclamation-triangle"></i> Error al cargar los ejemplos</h5>
        <p>${escapeHtml(error.message)}</p>
        <pre class="mt-3">${escapeHtml(error.stack || 'No hay detalles adicionales')}</pre>
        <p class="mt-2">Verifica que el archivo <code>ejemplos_condiciones.json</code> exista y tenga el formato correcto.</p>
    </div>`;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

</script>

<?php include __DIR__ . '/includes/footer.php'; ?>