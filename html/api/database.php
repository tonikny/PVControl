<?php
// /html/api/database.php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// Ruta CORRECTA: ../includes/conexion.php
$conexionPath = dirname(__FILE__) . '/../includes/conexion.php';

// Verificar que el archivo existe
if (!file_exists($conexionPath)) {
    http_response_code(500);
    echo json_encode(array(
        "success" => false, 
        "message" => "Archivo de conexión no encontrado",
        "path_tested" => $conexionPath
    ));
    exit;
}

include($conexionPath);

// Resto del código...
if (!isset($link) || !$link) {
    http_response_code(500);
    echo json_encode(array("success" => false, "message" => "Error en la conexión a la base de datos"));
    exit;
}

$verb = strtolower($_SERVER['REQUEST_METHOD']);

if ($verb == "get") {
    getParametros($link);
} elseif ($verb == "post") {
    $input = file_get_contents("php://input");
    $body = json_decode($input, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "JSON inválido"));
        exit;
    }
    
    updateParametros($link, $body);
} else {
    http_response_code(405);
    echo json_encode(array("success" => false, "message" => "Método no permitido"));
}

function getParametros($link) {
    $query = "SELECT * FROM parametros LIMIT 1";
    $result = mysqli_query($link, $query);
    
    if (!$result) {
        http_response_code(500);
        echo json_encode(array("success" => false, "message" => "Error en la consulta: " . mysqli_error($link)));
        return;
    }
    
    if (mysqli_num_rows($result) > 0) {
        $row = mysqli_fetch_assoc($result);
        
        $logged = isset($_GET['logged']) ? $_GET['logged'] : false;
        
        if (!$logged) {
            $sensitiveFields = ['password', 'token', 'secret', 'key', 'clave', 'api_key', 'private_key'];
            foreach ($sensitiveFields as $field) {
                if (isset($row[$field])) {
                    $row[$field] = '***';
                }
            }
        }
        
        // Definir grupos de campos
        $grupos = array(
            "Control Excedentes" => array(
                'sensor_PID' => 'Variable que controla los excedentes..Vbat, SOC, Wred, etc.... ',
                'objetivo_PID' => 'Valor de sensor_PID al que empiezan a actuar los excedentes', 
                'Kp' => 'Coeficiente proporcional del control PID',
                'Kd' => 'Coeficiente derivativo del control PID',
                'Ki' => 'Coeficiente integral del control PID'
            ),
            "Captura tabla datos" => array(
                't_muestra' => 'Tiempo en segindos del bucle de captura de fv.py',
                'n_muestras_grab' => 'Numero de bucles necesarios para grabar registro en tabla datos',
                'grabar_datos' => 'permite grabar o no en tabla datos... dejar a S',
                'grabar_reles' => 'permite grabar o no en tabla reles... dejar a S'
            ),
            "Control Carga Bateria" => array(
                'Mod_bat' => 'Modo de carga ABS, FLOT ....no tocar',
                'Vabs' => 'Valor voltaje objetivo de Absorcion',
                'Vflot' => 'Valor voltaje objetivo de Flotacion', 
                'Vequ' => 'Valor voltaje objetivo de Ecualizacion',
                'Tabs' => 'Tiempo de Absorcion',
                'Tequ' => 'Tiempo de ecualizacion - no implementado aun',
                'Icola' => 'Valor de Intensidad de cola -- no implementado aun',
                'coef_temp' => 'Coeficiente de temperatira para calculo de Vabs, Vflot',
                'nuevo_soc' => 'introducir un valor para actualizar el SOC....se pondra a 0 de nuevo tras actualizar en el siguiente bucle de fv.py'
            )
        );
        
        echo json_encode(array(
            "success" => true, 
            "data" => $row,
            "grupos" => $grupos
        ));
    } else {
        http_response_code(404);
        echo json_encode(array(
            "success" => false, 
            "message" => "No se encontraron parámetros en la tabla"
        ));
    }
}

function updateParametros($link, $body) {
    if (!isset($body['data']) || !is_array($body['data'])) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "Datos no proporcionados o formato incorrecto"));
        return;
    }
    
    $data = $body['data'];
    
    if (empty($data)) {
        http_response_code(400);
        echo json_encode(array("success" => false, "message" => "No hay datos para actualizar"));
        return;
    }
    
    $updates = [];
    foreach ($data as $key => $value) {
        if (!preg_match('/^[a-zA-Z0-9_]+$/', $key)) {
            http_response_code(400);
            echo json_encode(array("success" => false, "message" => "Nombre de campo inválido: " . $key));
            return;
        }
        
        $escapedValue = mysqli_real_escape_string($link, $value);
        $updates[] = "`$key` = '$escapedValue'";
    }
    
    $query = "UPDATE parametros SET " . implode(', ', $updates) . " LIMIT 1";
    
    $result = mysqli_query($link, $query);
    
    if ($result) {
        echo json_encode(array(
            "success" => true, 
            "message" => "Parámetros actualizados correctamente"
        ));
    } else {
        http_response_code(500);
        echo json_encode(array(
            "success" => false, 
            "message" => "Error al actualizar: " . mysqli_error($link)
        ));
    }
}

if (isset($link)) {
    mysqli_close($link);
}
?>