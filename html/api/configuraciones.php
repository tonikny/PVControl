<?php
// configuraciones.php
header("Access-Control-Allow-Origin: localhost");
header("Content-Type: application/json; charset=UTF-8");

$configuracionesPath = '../configuraciones/';

$verb = strtolower(@$_SERVER['REQUEST_METHOD']);

if ($verb == "post") {
    $body = json_decode(file_get_contents("php://input"), true);
    
    if (isset($body['action'])) {
        switch ($body['action']) {
            case 'create':
                createConfigFile($body);
                break;
                
            case 'delete':
                deleteConfigFile($body);
                break;
                
            case 'list':
                listConfigFiles();
                break;
                
            case 'save':
                saveConfigFile($body);
                break;
                
            case 'get':
                getConfigFile($body);
                break;

            default:
                http_response_code(400);
                echo json_encode(array("success" => false, "message" => "Acción no válida"));
                break;
        }
    } else {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Acción no especificada"));
    }
} else {
    http_response_code(405);
    echo json_encode(array("success" => false, "message" => "Método no permitido"));
}

function createConfigFile($body) {
    global $configuracionesPath;
    
    if (!isset($body['filename']) || !isset($body['content'])) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Datos incompletos"));
        return;
    }
    
    $filename = $body['filename'];
    $content = $body['content'];
    
    // Validar que el archivo tenga extensión .js
    if (!preg_match('/\.js$/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "El archivo debe tener extensión .js"));
        return;
    }
    
    // Validar nombre de archivo (evitar path traversal)
    if (preg_match('/\.\.|\/|\\\\/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Nombre de archivo no válido"));
        return;
    }
    
    $fullPath = $configuracionesPath . $filename;
    
    // Validar que no exista el archivo
    if (file_exists($fullPath)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "El archivo ya existe"));
        return;
    }
    
    // Crear el archivo
    $result = file_put_contents($fullPath, $content);
    
    if ($result !== false) {
        // Cambiar permisos para asegurar que sea escribible
        shell_exec("sudo chmod 666 " . escapeshellarg($fullPath) . " 2>/dev/null");
        
        echo json_encode(array(
            "success" => true, 
            "message" => "Archivo creado correctamente",
            "filename" => $filename
        ));
    } else {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Error al crear el archivo"));
    }
}

function deleteConfigFile($body) {
    global $configuracionesPath;
    
    if (!isset($body['filename'])) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Nombre de archivo no especificado"));
        return;
    }
    
    $filename = $body['filename'];
    $fullPath = $configuracionesPath . $filename;
    
    // Validaciones de seguridad
    if (!file_exists($fullPath)) {
        http_response_code(404);
        echo json_encode(array("success" => false, "message" => "El archivo no existe"));
        return;
    }
    
    // No permitir eliminar archivos fuera del directorio configuraciones
    if (realpath(dirname($fullPath)) !== realpath($configuracionesPath)) {
        http_response_code(403);
        echo json_encode(array("success" => false, "message" => "Operación no permitida"));
        return;
    }
    
    // Eliminar el archivo
    if (unlink($fullPath)) {
        echo json_encode(array("success" => true, "message" => "Archivo eliminado correctamente"));
    } else {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Error al eliminar el archivo"));
    }
}

function listConfigFiles() {
    global $configuracionesPath;
    
    $files = [];
    
    if (is_dir($configuracionesPath)) {
        $items = scandir($configuracionesPath);
        
        foreach ($items as $item) {
            if ($item !== '.' && $item !== '..' && is_file($configuracionesPath . $item) && preg_match('/\.js$/', $item)) {
                $files[] = $item;
            }
        }
        
        echo json_encode(array(
            "success" => true,
            "files" => $files
        ));
    } else {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Directorio de configuraciones no encontrado"));
    }
}

function getConfigFile($body) {
    global $configuracionesPath;
    
    if (!isset($body['filename'])) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Nombre de archivo no especificado"));
        return;
    }
    
    $filename = $body['filename'];
    
    // Validar nombre de archivo (evitar path traversal)
    if (preg_match('/\.\.|\/|\\\\/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Nombre de archivo no válido"));
        return;
    }
    
    $fullPath = $configuracionesPath . $filename;
    
    // Validar que el archivo exista
    if (!file_exists($fullPath)) {
        http_response_code(404);
        echo json_encode(array("success" => false, "message" => "El archivo no existe"));
        return;
    }
    
    // Validar que es un archivo .js
    if (!preg_match('/\.js$/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "El archivo debe ser .js"));
        return;
    }
    
    // Leer el contenido del archivo
    $content = file_get_contents($fullPath);
    
    if ($content !== false) {
        echo json_encode(array(
            "success" => true,
            "filename" => $filename,
            "content" => $content,
            "size" => filesize($fullPath)
        ));
    } else {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Error al leer el archivo"));
    }
}

function saveConfigFile($body) {
    global $configuracionesPath;
    
    if (!isset($body['filename']) || !isset($body['content'])) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Datos incompletos"));
        return;
    }
    
    $filename = $body['filename'];
    $content = $body['content'];
    
    // Validar que el archivo tenga extensión .js
    if (!preg_match('/\.js$/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "El archivo debe tener extensión .js"));
        return;
    }
    
    // Validar nombre de archivo (evitar path traversal)
    if (preg_match('/\.\.|\/|\\\\/', $filename)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Nombre de archivo no válido"));
        return;
    }
    
    $fullPath = $configuracionesPath . $filename;
    
    // Validar que el archivo exista
    if (!file_exists($fullPath)) {
        http_response_code(404);
        echo json_encode(array("success" => false, "message" => "El archivo no existe"));
        return;
    }
    
    // Guardar el archivo
    $result = file_put_contents($fullPath, $content);
    
    if ($result !== false) {
        echo json_encode(array(
            "success" => true, 
            "message" => "Archivo guardado correctamente",
            "filename" => $filename
        ));
    } else {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Error al guardar el archivo"));
    }
}

// Función auxiliar para logging (útil para debug)
function logMessage($message) {
    file_put_contents('../debug.log', date('Y-m-d H:i:s') . ' - ' . $message . "\n", FILE_APPEND);
}

?>