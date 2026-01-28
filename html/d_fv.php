<?php
// Habilitar compresión Gzip si el cliente lo soporta
if (substr_count($_SERVER['HTTP_ACCEPT_ENCODING'], 'gzip')) {
    ob_start("ob_gzhandler");
} else {
    ob_start();
}

header('Content-Type: application/json');

$servername = "localhost";
$username = "rpi";
$password = "fv";
$dbname = "control_solar";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT id_equipo, tiempo, sensores FROM equipos";
$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $data[$row['id_equipo']] = json_decode($row['sensores'], true);
		$data[$row['id_equipo']]["tiempo"]=$row['tiempo'];
    }
}

$conn->close();

echo json_encode($data);
?>
