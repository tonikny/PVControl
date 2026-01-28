<?php
/**
 * ARCHIVO DE CONFIGURACIÓN DE SEGURIDAD (BCRYPT)
 * 
 * Permisos recomendados: 600 (solo accesible por el usuario del servidor)
 */

return [
    // Hash generado con password_hash(). Para regenerar:
    // php -r 'echo password_hash("tu_clave", PASSWORD_BCRYPT, ["cost" => 12]);'
    'clave_hash' => '$2y$12$BwoszgS3pPdtqsFP6CniWuajLJS830NeKxO//41aHu0sZiYUjtIAG',
    
    // Configuración de seguridad adicional
    'seguridad' => [
        'max_intentos' => 3,    // Intentos fallidos permitidos
        'tiempo_bloqueo' => 300 // Tiempo de bloqueo en segundos (5 minutos)
    ]
];

