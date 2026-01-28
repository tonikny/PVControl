<?php
require_once __DIR__ . '/includes/conexion.php';

// Limpiar buffer de salida
ob_clean();

header('Content-Type: application/json');
date_default_timezone_set("UTC");

try {
    if (!isset($_GET['id_rele'])) {
        throw new Exception('ID de relé no especificado');
    }

    $id_rele = (int)$_GET['id_rele'];
    
    if (!$link) {
        throw new Exception('No hay conexión a la base de datos');
    }

    // Gráfico 1: Tiempo activo por día (se mantiene igual)
    $sql_grafico1 = "SELECT r.nombre, 
                    rs.fecha as Fecha, 
                    ROUND(rs.segundos_on,0) as segundos,
                    rs.nconmutaciones
                    FROM reles_segundos_on rs
                    JOIN reles r ON rs.id_rele = r.id_rele
                    WHERE rs.id_rele = ? 
                    AND rs.fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) 
                    GROUP BY rs.fecha";

    $stmt1 = mysqli_prepare($link, $sql_grafico1);
    mysqli_stmt_bind_param($stmt1, 'i', $id_rele);
    mysqli_stmt_execute($stmt1);
    $result_grafico1 = mysqli_stmt_get_result($stmt1);

    $grafico1 = [];
    $nombre_rele = '';
    while ($row = mysqli_fetch_assoc($result_grafico1)) {
        $grafico1[] = $row;
        $nombre_rele = $row['nombre']; // Obtenemos el nombre del relé
    }    
    
    // Gráfico 2: Datos de potencia con lógica de persistencia
    $sql_grafico2 = "SELECT Tiempo, valor_rele 
                    FROM reles_grab 
                    WHERE id_rele = ? 
                    AND DATE(Tiempo) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    ORDER BY Tiempo";
    $stmt2 = mysqli_prepare($link, $sql_grafico2);
    mysqli_stmt_bind_param($stmt2, 'i', $id_rele);
    mysqli_stmt_execute($stmt2);
    $result_grafico2 = mysqli_stmt_get_result($stmt2);
    
    $grafico2 = [];
    while ($row = mysqli_fetch_assoc($result_grafico2)) {
        $grafico2[] = [
            'Tiempo' => $row['Tiempo'],
            'valor_rele' => (int)$row['valor_rele']
        ];
    }

    echo json_encode([
        'success' => true,
        'grafico1' => $grafico1,
        'grafico2' => $grafico2
    ]);
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}

mysqli_close($link);
exit;
?>