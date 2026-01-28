<?php
//$titulo = "Parametros";

session_start();
require_once __DIR__ . '/includes/cabecera.php';
require_once __DIR__ . '/includes/conexion.php';
$seguridad = include __DIR__ . '/includes/seguridad.php';

// 1. Procesar formulario de autenticación
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['password'])) {
    if (password_verify($_POST['password'], $seguridad['clave_hash'])) {
        $_SESSION['modo_edicion'] = true;
        header("Location: parametros.php");
        exit;
    } else {
        $error_clave = "Clave incorrecta";
    }
}

// 2. Procesar cierre de sesión
if (isset($_GET['cerrar_edicion'])) {
    unset($_SESSION['modo_edicion']);
    header("Location: parametros.php");
    exit;
}
?>

<div class="container mt-3" style="position: relative; z-index: 1;">
    <!-- -->
    
    <div class="d-flex justify-content-between align-items-center mb-4">
        <?php if (!isset($_SESSION['modo_edicion'])): ?>
            <button class="btn btn-primary" id="btnLoginManual">
                <i class="bi bi-lock-fill"></i> Editar Configuración
            </button>
        <?php else: ?>
            <div>
                <a href="?cerrar_edicion=1" class="btn btn-danger">
                    <i class="bi bi-unlock-fill"></i> Cerrar edición
                </a>
            </div>
        <?php endif; ?>
    </div>
    
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
</div>

<h2 style="margin-left: 5px;">Archivos de configuración</h2>
<?php if (isset ($_SESSION['modo_edicion'])) { ?>
  <div style="font-size: small; font-style: italic">
    Para poder guardar los cambios hay que poner los archivos en el grupo www-data
    y tener permiso de escritura al grupo:
    <br>
    <strong>chmod 664 archivo</strong> <br>
    <strong>sudo chown pi:www-data archivo</strong>
  </div>
<?php } ?>
<br />
<h3 style="margin-left: 10px;">Parametros_FV.py</h3>
<div id="fv" style="height: 400px; width: 70%; margin-left: 20px;"></div>
<?php if (isset ($_SESSION['modo_edicion'])) { ?><button onclick="send('FV',fv.session.getValue())">Guardar</button>
<?php } ?><br />
<h3 style="margin-left: 10px;">Parametros_Web.js</h3>
<div id="web" style="height: 400px; width: 70%; margin-left: 20px;"></div>
<?php if (isset ($_SESSION['modo_edicion'])) { ?><button onclick="send('Web',web.session.getValue())">Guardar</button>
<?php } ?>


<h3 style="margin-left: 10px;">Configuracion Dibujo - Archivo activo ==>
<?php
// Lee el contenido de configuracion_activa.txt
$configFile = file_get_contents('configuracion_activa.txt');

// Asegúrate de eliminar cualquier espacio o salto de línea no deseado
$configFile = trim($configFile);
echo $configFile;
?>
</h3>
<div id="dib" style="height: 400px; width: 70%; margin-left: 20px;"></div>
<?php if (isset ($_SESSION['modo_edicion'])) { ?><button onclick="send('Dib',dib.session.getValue())">Guardar</button>
<?php } ?>





<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.8/ace.min.js" type="text/javascript"
  charset="utf-8"></script>
<script>

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




  const logged = "<?php echo isset ($_SESSION['modo_edicion']); ?>" ? true : false;

  const fv = ace.edit("fv");
  fv.setTheme("ace/theme/monokai");
  fv.session.setMode("ace/mode/python");
  
  const web = ace.edit("web");
  web.setTheme("ace/theme/monokai");
  web.session.setMode("ace/mode/javascript");
  
  const dib = ace.edit("dib");
  dib.setTheme("ace/theme/monokai");
  dib.session.setMode("ace/mode/javascript");
  
  if (!logged) {
    fv.setReadOnly(true);
    web.setReadOnly(true);
	dib.setReadOnly(true);
	
  }

  (async function () {
    const endpoint = (logged) ? "/api/parametros.php?logged=true" : "/api/parametros.php";
    const response = await fetch(endpoint);
    const result = await response.json();
    if (result.success) {
      fv.setValue(result.data.FV);
      web.setValue(result.data.Web);
	  dib.setValue(result.data.Dib);
	  
    }
  }())

  function send(file, data) {
    fetch('/api/parametros.php', {
      method: 'POST',
      body: JSON.stringify({ file, data }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }
</script>

<br /><br />
<?php include __DIR__ . '/includes/footer.php'; ?>