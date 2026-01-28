<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Código backend para manejar el escaneo de IPs
    $data = json_decode(file_get_contents('php://input'), true);
    $start_ip = $data['start_ip'];
    $end_ip = $data['end_ip'];

    list($s1, $s2, $s3, $s4) = explode('.', $start_ip);
    list($e1, $e2, $e3, $e4) = explode('.', $end_ip);

    $results = [];

    for ($i = $s4; $i <= $e4; $i++) {
        $ip = "$s1.$s2.$s3.$i";
        $url = "http://$ip";
        
        // Verifica si el puerto 80 está abierto y si responde con una página
        $context = stream_context_create(['http' => ['timeout' => 2]]);
        $content = @file_get_contents($url, false, $context);

        if ($content !== false) {
            $results[] = ['ip' => $ip, 'content' => htmlspecialchars($content)];
        }
    }

    header('Content-Type: application/json');
    echo json_encode($results);
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Range Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .result { margin-top: 20px; }
        .iframe-container { margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>IP Range Scanner</h1>
    <label>Start IP: <input type="text" id="start_ip" placeholder="192.168.1.100"></label>
    <label>End IP: <input type="text" id="end_ip" placeholder="192.168.1.150"></label>
    <button onclick="scan()">Scan IP Range</button>

    <div id="results" class="result"></div>

    <script>
        async function scan() {
            const start_ip = document.getElementById('start_ip').value;
            const end_ip = document.getElementById('end_ip').value;
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = 'Scanning...';

            const response = await fetch('', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_ip, end_ip })
            });

            const results = await response.json();
            resultsDiv.innerHTML = '';

            if (results.length === 0) {
                resultsDiv.innerHTML = 'No IPs found with open port 80.';
            } else {
                results.forEach(result => {
                    const container = document.createElement('div');
                    container.className = 'iframe-container';
                    container.innerHTML = `
                        <h3>${result.ip}</h3>
                        <iframe srcdoc="${result.content}" width="800" height="600"></iframe>
                    `;
                    resultsDiv.appendChild(container);
                });
            }
        }
    </script>
</body>
</html>
