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


function handlePost($conn) {
    $input = json_decode(file_get_contents('php://input'), true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        http_response_code(400);
        echo json_encode(["error" => "JSON inválido."]);
        return;
    }

    if (!isset($input['tabela']) || !isset($input['dados']) || !is_array($input['dados'])) {
        http_response_code(400);
        echo json_encode(["error" => "Formato inválido."]);
        exit;
    }

    $tabela = preg_replace('/[^a-zA-Z0-9_]/', '', $input['tabela']);
    $dados = $input['dados'];

    if (registroExiste($conn, $tabela, $dados["id_ident"])) {
        atualizarRegistro($conn, $tabela, $dados);
    } else {
        inserirRegistro($conn, $tabela, $dados);
    }
}

function handleGet($conn){
    if (!isset($_GET['tabela'])) {
        http_response_code(400);
        echo json_encode(["error" => "Tabela não especificada."]);
        return;
    }

    $tabela = preg_replace('/[^a-zA-Z0-9_]/', '', $_GET['tabela']);

    if (isset($_GET['ultimaData'])) {
        $sql = "SELECT TOP 1 data_registro FROM $tabela ORDER BY data_registro DESC";
        $stmt = $conn->prepare($sql);
        $stmt->execute();
    }

    $resultado = $stmt->fetch(PDO::FETCH_ASSOC);
    echo json_encode(["Ultima_data_registrada" => $resultado ? $resultado['data_registro'] : null]);
    return;
}

function registroExiste($conn, $tabela, $id){
    $sql = "SELECT COUNT(1) FROM $tabela WHERE id_ident = :id";
    $stmt = $conn->prepare($sql);
    $stmt->execute([':id' => $id]);
    return $stmt->fetchColumn() > 0;
}

function atualizarRegistro($conn, $tabela, $dados){
    if (!isset($dados['id_ident'])) return;
    
    $set = [];
    foreach ($dados as $coluna => $valor){
        if ($coluna !== 'id_ident') {
            $set[] = "$coluna = :$coluna";
        }
    }

    if (empty($set)) return;

    $sql = "UPDATE $tabela SET " . implode(", ", $set) . " WHERE id_ident = :id_ident";
    $stmt = $conn->prepare($sql);
    error_log("SQL: $sql");
    error_log("PARAMS: " . json_encode($dados));
    $stmt->execute($dados);    
}

function inserirRegistro($conn, $tabela, $dados){
    $campos = implode(", ", array_keys($dados));
    $placeholders = ":" . implode(", :", array_keys($dados));

    $sql = "INSERT INTO $tabela ($campos) VALUES ($placeholders)";

    try {
        $stmt = $conn->prepare($sql);
        $stmt->execute($dados);
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(["error" => $e->getMessage()]);
        echo json_encode(["SQL: $sql\n"]);
        echo json_encode([print_r($dados)]);
        exit;
    }
}

?>