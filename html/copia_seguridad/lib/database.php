<?php

// Configuración en variables - UNA SOLA FUENTE
$db_host = 'localhost';
$db_username = 'rpi';
$db_password = 'fv';
$db_database = 'control_solar';

function getDatabaseConnection() {
    global $db_host, $db_username, $db_password, $db_database;
    
    static $db = null;
    
    if ($db === null) {
        $db = new mysqli($db_host, $db_username, $db_password, $db_database);
        
        if ($db->connect_error) {
            throw new Exception("Error conectando a la base de datos: " . $db->connect_error);
        }
        
        $db->set_charset('utf8mb4');
    }
    
    return $db;
}

/**
 * Obtiene la configuración de la base de datos para uso externo
 * Usa las mismas variables que getDatabaseConnection()
 */
function getDatabaseConfig() {
    global $db_host, $db_username, $db_password, $db_database;
    
    return [
        'host' => $db_host,
        'username' => $db_username,
        'password' => $db_password,
        'database' => $db_database
    ];
}

function testDatabaseConnection() {
    try {
        $db = getDatabaseConnection();
        return $db->ping();
    } catch (Exception $e) {
        return false;
    }
}
?>