<?php

header("Access-Control-Allow-Origin: localhost");
header("Content-Type: application/json; charset=UTF-8");

$files['FV'] = '../../Parametros_FV.py';
$files['Web'] = '../Parametros_Web.js';
$files['Version'] = '../version.inc';
$files['Config'] = '../configuracion_activa.txt';

// Lee el contenido de configuracion_activa.txt para el archivo Dib
$configFile = file_get_contents('../configuracion_activa.txt');
$configFile = trim($configFile);
$files['Dib'] = "../configuraciones/$configFile";

$verb = strtolower(@$_SERVER['REQUEST_METHOD']);
if ($verb == "get") {
    $queries = array();
    parse_str($_SERVER['QUERY_STRING'], $queries);
    $logged = $queries['logged'];
    
    $data = array();
    foreach ($files as $key => $file) {
        if ($logged) {
            $data[$key] = read_file($file);
        } else {
            $data[$key] = read_file_secure($file);
        }
    }
    
    if ($data) {
        http_response_code(200);
        echo json_encode(array("success" => true, "data" => $data));
    } else {
        http_response_code(404);
        echo json_encode(
            array("success" => false, "message" => "Files not found.")
        );
    }
}

if ($verb == "post") {
    $body = json_decode(file_get_contents("php://input"), true);
    
    // Mapear las claves a los archivos correspondientes
    $fileMap = [
        'FV' => 'FV',
        'Web' => 'Web', 
        'version' => 'Version',
        'config' => 'Config'
    ];
    
    if (isset($fileMap[$body['file']])) {
        $fileKey = $fileMap[$body['file']];
        $result = write_file($files[$fileKey], $body['data']);
        echo json_encode($result);
    } else {
        http_response_code(400);
        echo json_encode(
            array("success" => false, "message" => "Invalid file type.")
        );
    }
}

function read_file($file)
{
    $content = @file_get_contents($file);
    return $content;
}

function read_file_secure($file)
{
    $content = @file_get_contents($file);
    $rows = explode("\n", $content);
    $secure = "";
    foreach ($rows as $row) {
        $pos = strpos($row, "***");
        if ($pos === false) {
            $secure .= $row . "\n";
        } else {
            $secure .= hiddenString($row) . "\n";
        }
    }
    return $secure;
}

function write_file($file, $data)
{
    if (is_writable($file)) {
        shell_exec("sudo cp -a " . $file . " " . $file . ".back && echo 0 || echo 1");
        $result = file_put_contents($file, $data);
        return array("success" => true, "message" => $result);
    } else {
        return array("success" => false, "message" => 'Error: File not writable');
    }
}

function hiddenString($str)
{
    if (strpos($str, '=') !== false) {
        $arr = explode('=', $str, 2);
        return $arr[0] . ' = ***';
    } elseif (strpos($str, ':') !== false) {
        $arr = explode(':', $str, 2);
        return $arr[0] . ' : ***';
    }
    return $str;
}