<?php

header("Access-Control-Allow-Origin: localhost");
header("Content-Type: application/json; charset=UTF-8");

function status()
{
    $results = array();
    $files = scandir('../../etc/systemd/system');
    foreach ($files as $file) {
        if ($file == '.' || $file == '..')
            continue;
        $name = substr($file, 0, strpos($file, '.'));
        $state = shell_exec("systemctl show -p ActiveState --value  $file");
        $substate = shell_exec("systemctl show -p SubState --value  $file");
        $date = date_create(shell_exec("systemctl show -p ActiveEnterTimestamp --value  $file"));
        $uptime = date_format($date, 'Y-m-d H:i:s');
        $is_enabled = shell_exec("systemctl is-enabled $file");

        $results[] = array(
            "name" => $name,
            "state" => trim($state),
            "substate" => trim($substate),
            "is_enabled" => trim($is_enabled),
            "uptime" => trim($uptime),
        );
    }
    usort($results, function ($a, $b) {
        return
            $a["state"] > $b["state"] || $a["state"] == $b["state"]
            && $a["uptime"] <= $b["uptime"];
    });
    return $results;
}

function start_stop($name)
{
    try {
        if (trim(shell_exec("systemctl is-active " . $name)) == "active") {
            $res = shell_exec("sudo systemctl stop " . $name);
            return array("success" => true, "message" => $name . ": Service stopped");
        } else {
            $res = shell_exec("sudo systemctl start " . $name);
            return array("success" => true, "message" => $name . ": Service started");
        }
    } catch (Exception $e) {
        return array("success" => false, "message" => $e->getMessage());
    }
}

$verb = strtolower(@$_SERVER['REQUEST_METHOD']);
if ($verb == "get") {
    $result = status();
    if ($result) {
        http_response_code(200);
        echo json_encode(array("success" => true, "data" => $result));
    } else {
        http_response_code(404);
        echo json_encode(
            array("success" => false, "message" => "Service not found.")
        );
    }
}
if ($verb == "post") {
    $data = json_decode(file_get_contents("php://input"));
    $result = start_stop($data->name);
    echo json_encode($result);
}