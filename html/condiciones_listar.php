<?php
session_start();
include 'conexion.php';

$seguridad = include 'seguridad.php'; // Archivo con el hash de seguridad

// Procesar eliminación (solo si está en modo edición)
if(isset($_GET['eliminar']) && isset($_SESSION['modo_edicion'])) {
    $id = intval($_GET['eliminar']);
    mysqli_query($link, "DELETE FROM condiciones WHERE id_condicion = $id");
    header("Location: condiciones_listar.php");
    exit;
}

// Procesar activación del modo edición
if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['password'])) {
    // DEBUG: Verifica qué se está comparando
    var_dump($_POST['password']);
    var_dump($seguridad['clave_hash']);
    
    if(password_verify($_POST['password'], $seguridad['clave_hash'])) {
        $_SESSION['modo_edicion'] = true;
        // Recarga para evitar reenvío del formulario
        header("Location: condiciones_listar.php");
        exit;
    } else {
        $error_clave = "Clave incorrecta";
    }
}

// Cerrar modo edición
if(isset($_GET['cerrar_edicion'])) {
    unset($_SESSION['modo_edicion']);
    header("Location: condiciones_listar.php");
    exit;
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Listado de Condiciones</title>
    <link rel="stylesheet" href="css/menu_2025.css">
    <style>
        /* ESTILOS DEL MENÚ (se mantienen igual) */
        
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        
        /* CONTENEDOR PRINCIPAL */
        .contenido-principal {
            margin-top: 80px;
            padding: 20px;
        }
        
        /* TABLA CON SOMBREADO ALTERNO Y TEXTO COLPASADO */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 10px; 
            text-align: left; 
        }
        th { 
            background-color: #4a6fa5; 
            color: white;
            position: sticky; 
            top: 80px;
            font-weight: normal;
        }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:nth-child(odd) { background-color: #ffffff; }
        tr:hover { background-color: #f1f1f1; }
        
        /* TEXTO LARGO COLPASADO CON PUNTOS SUSPENSIVOS */
        .texto-largo { 
            max-width: 300px; 
            overflow: hidden;
            text-overflow: ellipsis; 
            white-space: nowrap;
        }
        
        /* DETALLES EXPANDIBLES */
        .detalles { 
            display: none;
        }
        .ver-detalles { 
            color: #17a2b8; 
            cursor: pointer;
            font-weight: 500;
        }
        .contenedor-detalles {
            padding: 15px;
            background-color: #f8fafc;
            border-left: 4px solid #4a6fa5;
        }
        .texto-con-saltos {
            white-space: pre-wrap;
            word-break: break-word;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border: 1px solid #e1e5eb;
        }
        
        /* BOTONES Y ACCIONES */
        .acciones a { 
            margin-right: 12px; 
            text-decoration: none;
            color: #2c5e9e;
            font-weight: 500;
        }
        .btn-agregar {
            display: inline-block;
            padding: 8px 16px;
            background: #4a6fa5;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
        }
        .activo { color: #28a745; font-weight: bold; }
        .inactivo { color: #dc3545; }
        
        /* MODO EDICIÓN */
        .modo-edicion-banner {
            position: fixed;
            top: 80px;
            left: 0;
            right: 0;
            background-color: #ffc107;
            color: #856404;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            z-index: 1000;
        }
        .btn-cerrar-edicion {
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            text-decoration: none;
            margin-left: 10px;
        }
        .form-clave-edicion {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
            border: 1px solid #ddd;
            max-width: 500px;
        }
    </style>
</head>
<body>
    <!-- MENÚ PRINCIPAL -->
    <div id="navbar"></div>

    <!-- BANNER MODO EDICIÓN -->
    <?php if(isset($_SESSION['modo_edicion'])): ?>
        <div class="modo-edicion-banner">
            MODO EDICIÓN ACTIVADO
            <a href="?cerrar_edicion=1" class="btn-cerrar-edicion">Cerrar modo edición</a>
        </div>
    <?php endif; ?>

    <!-- CONTENIDO PRINCIPAL -->
    <div class="contenido-principal">
        <h1 style="color: #2c3e50;">Listado de Condiciones Avanzadas</h1>
        
        <!-- FORMULARIO DE CLAVE (solo visible sin sesión) -->
        <?php if(!isset($_SESSION['modo_edicion'])): ?>
            <div class="form-clave-edicion">
                <form method="post" autocomplete="off">
                    <label for="password">Clave de edición:</label>
                    <input type="password" name="password" id="password" required>
                    <button type="submit" class="btn-agregar">Activar edición</button>
                    <?php if(isset($error_clave)): ?>
                        <span style="color: #dc3545; margin-left: 10px;"><?php echo $error_clave; ?></span>
                    <?php endif; ?>
                </form>
            </div>
        <?php else: ?>
            <a href="condiciones_agregar.php" class="btn-agregar">➕ Agregar Nueva Condición</a>
        <?php endif; ?>
        
        <br><br>
        
        <!-- TABLA -->
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Estado</th>
                    <th>Condición 1</th>
                    <th>Condición 2</th>
                    <th>Acción</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                <?php
                $result = mysqli_query($link, "SELECT * FROM condiciones ORDER BY id_condicion");
                while($row = mysqli_fetch_assoc($result)):
                    $estado = $row['activado'] ? '<span class="activo">Activado</span>' : '<span class="inactivo">Desactivado</span>';
                ?>
                <tr class="<?php echo ($i++ % 2 == 0) ? 'fila-par' : 'fila-impar'; ?>">
                    <td><?= $row['id_condicion'] ?></td>
                    <td><?= $estado ?></td>
                    <td class="texto-largo" title="<?= htmlspecialchars($row['condicion1']) ?>">
                        <?= htmlspecialchars($row['condicion1']) ?>
                    </td>
                    <td class="texto-largo" title="<?= htmlspecialchars($row['condicion2']) ?>">
                        <?= htmlspecialchars($row['condicion2']) ?>
                    </td>
                    <td class="texto-largo" title="<?= htmlspecialchars($row['accion']) ?>">
                        <?= htmlspecialchars($row['accion']) ?>
                    </td>
                    <td class="acciones">
                        <?php if(isset($_SESSION['modo_edicion'])): ?>
                            <a href="condiciones_editar.php?id=<?= $row['id_condicion'] ?>">✏️ Editar</a>
                            <a href="condiciones_listar.php?eliminar=<?= $row['id_condicion'] ?>" 
                               onclick="return confirm('¿Eliminar este registro?')">🗑️ Eliminar</a>
                        <?php endif; ?>
                        <span class="ver-detalles" onclick="mostrarDetalles(<?= $row['id_condicion'] ?>)">🔍 Detalles</span>
                    </td>
                </tr>
                <tr class="detalles" id="detalles-<?= $row['id_condicion'] ?>">
                    <td colspan="6">
                        <div class="contenedor-detalles">
                            <div>
                                <strong>Descripción:</strong>
                                <div class="texto-con-saltos"><?= htmlspecialchars($row['descripcion']) ?></div>
                            </div>
                            <div>
                                <strong>Condición 1 completa:</strong>
                                <div class="texto-con-saltos"><?= htmlspecialchars($row['condicion1']) ?></div>
                            </div>
                            <div>
                                <strong>Condición 2 completa:</strong>
                                <div class="texto-con-saltos"><?= htmlspecialchars($row['condicion2']) ?></div>
                            </div>
                            <div>
                                <strong>Acción completa:</strong>
                                <div class="texto-con-saltos"><?= htmlspecialchars($row['accion']) ?></div>
                            </div>
                        </div>
                    </td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>

    <!-- SCRIPTS -->
    <script src="script/menu.js"></script>
    <script>
        // Función para mostrar/ocultar detalles (MANTENIDA IGUAL)
        function mostrarDetalles(id) {
            const detalles = document.getElementById(`detalles-${id}`);
            detalles.style.display = detalles.style.display === 'none' ? 'table-row' : 'none';
            
            // Desplazamiento suave
            if(detalles.style.display === 'table-row') {
                setTimeout(() => {
                    detalles.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 50);
            }
        }
    </script>
</body>
</html>