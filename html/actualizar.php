<?php
if (isset($_POST['ejecutar'])) {
    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: no-cache');
    
    $directory_path = '/home/pi/PVControl+';
    $git_path = $directory_path . '/.git';
    
    echo "🔄 ACTUALIZACIÓN PVControl+ - MODO SEGURO\n";
    echo "========================================\n\n";
    
    // Verificar si Git está configurado correctamente
    echo "⚙️ Verificando configuración Git...\n";
    echo "----------------------------------------\n";
    
    $git_check_output = array();
    $git_check_return = 0;
    exec('git config --system --get-all safe.directory 2>&1', $git_check_output, $git_check_return);
    
    $git_configured = false;
    if ($git_check_return === 0) {
        foreach ($git_check_output as $line) {
            if (trim($line) === $directory_path) {
                $git_configured = true;
                break;
            }
        }
    }
    
    if ($git_configured) {
        echo "✅ Git configurado correctamente\n";
    } else {
        echo "❌ ERROR: Git no está configurado\n";
        echo "   Para solucionar este problema permanentemente,\n";
        echo "   ejecuta ESTE COMANDO UNA VEZ en la terminal:\n\n";
        echo "   sudo git config --system --add safe.directory /home/pi/PVControl+\n\n";
        echo "   Luego vuelve a intentar la actualización web.\n";
        echo "========================================\n";
        exit;
    }
    
    // Verificar permisos de escritura en .git
    echo "🔒 Verificando permisos de escritura...\n";
    if (!is_writable($git_path)) {
        echo "❌ ERROR: Sin permisos de escritura en .git\n";
        echo "   Ejecuta estos comandos en la terminal:\n\n";
        echo "   sudo chown -R pi:www-data /home/pi/PVControl+/.git\n";
        echo "   sudo chmod -R 775 /home/pi/PVControl+/.git\n";
        echo "   sudo chmod 775 /home/pi/PVControl+\n\n";
        echo "   Luego vuelve a intentar.\n";
        echo "========================================\n";
        exit;
    } else {
        echo "✅ Permisos de escritura OK\n";
    }
    
    echo "\n";
    
    // Ejecutar git pull
    echo "📥 Ejecutando actualización desde Git...\n";
    echo "----------------------------------------\n";
    
    $command = 'cd ' . escapeshellarg($directory_path) . ' && git pull 2>&1';
    $handle = popen($command, 'r');
    
    if ($handle) {
        while (!feof($handle)) {
            $buffer = fgets($handle, 1024);
            if ($buffer !== false) {
                echo $buffer;
                flush();
            }
        }
        $return_code = pclose($handle);
        
        echo "\n----------------------------------------\n";
        
        if ($return_code === 0) {
            echo "✅ Actualización Git completada con éxito\n\n";
            echo "💡 INFORMACIÓN IMPORTANTE:\n";
            echo "   La actualización Git se ha completado, pero para una\n";
            echo "   actualización completa del sistema que incluya:\n";
            echo "   - Scripts Python con privilegios sudo\n";
            echo "   - Configuraciones del sistema\n";
            echo "   - Actualización de dependencias\n";
            echo "   - Verificación de servicios\n\n";
            echo "   Ejecuta manualmente en la terminal:\n";
            echo "   cd /home/pi/PVControl+ && ./actualizar\n";
        } else {
            echo "❌ Error en la actualización Git\n";
            echo "   Código de error: $return_code\n";
            
            // Mensaje específico para error de permisos
            echo "\n🔧 SOLUCIÓN PARA PERMISOS:\n";
            echo "   Ejecuta estos comandos en la terminal:\n";
            echo "   sudo chown -R pi:www-data /home/pi/PVControl+/.git\n";
            echo "   sudo chmod -R 775 /home/pi/PVControl+/.git\n";
        }
    } else {
        echo "❌ No se pudo ejecutar git pull\n";
    }
    
    echo "\n========================================\n";
    exit;
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Actualizador PVControl+</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f5f5f5; 
            color: #333; 
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 20px;
        }
        #terminal { 
            background: #1e1e1e; 
            color: #00ff00; 
            padding: 15px; 
            height: 400px; 
            overflow-y: auto;
            border: 1px solid #ddd;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            border-radius: 5px;
            margin: 15px 0;
        }
        button { 
            padding: 12px 30px; 
            background: #3498db; 
            color: white; 
            border: none; 
            cursor: pointer;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover { background: #2980b9; }
        button:disabled { 
            background: #95a5a6; 
            cursor: not-allowed; 
        }
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-left: 4px solid #f39c12;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .info-box {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .error-box {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-left: 4px solid #dc3545;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .status { 
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }
        .loading { 
            background: #fff3cd; 
            color: #856404; 
            border-left: 4px solid #ffc107;
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border-left: 4px solid #28a745;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border-left: 4px solid #dc3545;
        }
        .code {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Actualizador PVControl+</h1>
            <p>Actualización segura desde la interfaz web</p>
        </div>
        
        <div class="content">
            <div class="warning-box">
                <strong>🔧 CONFIGURACIÓN REQUERIDA</strong><br>
                Para que la actualización web funcione, necesitas ejecutar ./actualizar previamente o manualmente estos comandos:
                <div class="code">
                    # 1. Configurar Git (una vez)<br>
                    sudo git config --system --add safe.directory /home/pi/PVControl+<br><br>
                    # 2. Dar permisos de escritura (una vez)<br>
                    sudo chown -R pi:www-data /home/pi/PVControl+/.git<br>
                    sudo chmod -R 775 /home/pi/PVControl+/.git<br>
                    sudo chmod 775 /home/pi/PVControl+
                </div>
            </div>
            
            <div class="info-box">
                <strong>💡 INFORMACIÓN</strong><br>
                <strong>Actualización web (parcial):</strong> Solo descarga cambios desde Git<br>
                <strong>Actualización completa (terminal):</strong> Incluye scripts Python, configuraciones y servicios
            </div>
            
            <div class="status" id="status">
                Listo para ejecutar actualización Git...
            </div>
            
            <button onclick="ejecutarScript()" id="runBtn">📥 Ejecutar Actualización Git</button>
            
            <div id="terminal">
╔══════════════════════════════════════════════╗
║            ACTUALIZADOR PVControl+           ║
║                 MODO SEGURO                  ║
╚══════════════════════════════════════════════╝

📋 Esta herramienta verificará:
├─ ✅ Configuración Git del sistema
├─ 🔒 Permisos de escritura en .git
├─ 📥 git pull (si todo está OK)
└─ 🔄 Actualizar código del repositorio

            </div>
            
        </div>
    </div>

    <script>
    function ejecutarScript() {
        const terminal = document.getElementById('terminal');
        const runBtn = document.getElementById('runBtn');
        const status = document.getElementById('status');
        
        runBtn.disabled = true;
        runBtn.textContent = '⏳ Verificando...';
        status.className = 'status loading';
        status.innerHTML = '⏳ Verificando configuración y permisos...';
        
        terminal.innerHTML = '🔄 INICIANDO VERIFICACIÓN\n';
        terminal.innerHTML += '══════════════════════════════════════════════\n';
        terminal.innerHTML += '📁 Repositorio: /home/pi/PVControl+\n';
        terminal.innerHTML += '🎯 Verificación: Configuración + Permisos\n';
        terminal.innerHTML += '⏰ Hora: ' + new Date().toLocaleString() + '\n';
        terminal.innerHTML += '══════════════════════════════════════════════\n\n';
        
        fetch('actualizar.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'ejecutar=1'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error del servidor: ' + response.status);
            }
            return response.text();
        })
        .then(data => {
            terminal.innerHTML += data;
            terminal.scrollTop = terminal.scrollHeight;
            
            if (data.includes('✅ Actualización Git completada con éxito')) {
                status.className = 'status success';
                status.innerHTML = '✅ Actualización completada';
            } else if (data.includes('✅ Git configurado correctamente') && data.includes('✅ Permisos de escritura OK')) {
                status.className = 'status success';
                status.innerHTML = '✅ Configuración OK - Ejecutando actualización';
            } else {
                status.className = 'status error';
                status.innerHTML = '❌ Configuración requerida';
            }
        })
        .catch(error => {
            terminal.innerHTML += '\n❌ ERROR: ' + error.message + '\n';
            status.className = 'status error';
            status.innerHTML = '❌ Error en la ejecución';
        })
        .finally(() => {
            runBtn.disabled = false;
            runBtn.textContent = '📥 Ejecutar Actualización Git';
        });
    }
    
    // Auto-scroll
    const terminal = document.getElementById('terminal');
    const observer = new MutationObserver(function() {
        terminal.scrollTop = terminal.scrollHeight;
    });
    observer.observe(terminal, { childList: true, subtree: true });
    </script>
</body>
</html>