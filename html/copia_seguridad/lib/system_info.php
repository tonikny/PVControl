<?php
/**
 * system_info.php - Detección simple de zona horaria
 */

/**
 * Detecta la zona horaria del sistema de forma simple
 */
function detectSystemTimezone() {
    // Método 1: timedatectl (el más fiable en Raspberry Pi)
    $timezone = shell_exec('timedatectl show --property=Timezone --value 2>/dev/null');
    if ($timezone) {
        return trim($timezone);
    }
    
    // Método 2: /etc/timezone
    if (file_exists('/etc/timezone')) {
        $timezone = file_get_contents('/etc/timezone');
        if ($timezone) {
            return trim($timezone);
        }
    }
    
    // Método 3: Enlace simbólico
    if (is_link('/etc/localtime')) {
        $link = readlink('/etc/localtime');
        if (preg_match('#/usr/share/zoneinfo/(.+)$#', $link, $matches)) {
            return $matches[1];
        }
    }
    
    // Por defecto, usar UTC
    return 'UTC';
}

/**
 * Configura la zona horaria para PHP
 */
function setupSystemTimezone() {
    $timezone = detectSystemTimezone();
    date_default_timezone_set($timezone);
    return $timezone;
}
?>