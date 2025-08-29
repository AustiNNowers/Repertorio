<?php
header('Content-Type: application/json; charset=utf-8');

$serverName = "Confidencial";
$database = "Confidencial";
$username = "Confidencial";
$password = "Confidencial";

try {
    $conn = new PDO("sqlsrv:server=$serverName;Database=$database", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $method = $_SERVER['REQUEST_METHOD'];

    switch ($method) {
        case 'POST':
            handlePost($conn);
            break;
        case 'GET':
            handleGet($conn);
            break;
        default:
            http_response_code(405);
            echo json_encode(["error" => "Método não permitido."]);
            break;
    }
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(["error" => "Erro fatal: " . $e->getMessage()]);
}

?>