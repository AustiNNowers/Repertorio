<?php
header('Content-Type: application/json; charset=utf-8');

$serverName = "Confidencial";
$database = "Confidencial";
$username = "Confidencial";
$password = "Confidencial";

try {
    $conn = new PDO("sqlsrv:server=$serverName;Database=$database", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $input = json_decode(file_get_contents('php://input'), true);

    if (!isset($input['tabela']) || !isset($input['dados']) || !is_array($input['dados'])) {
        http_response_code(400);
        echo json_encode(["error" => "Formato inválido."]);
        exit;
    }

    $tabela = preg_replace('/[^a-zA-Z0-9_]/', '', $input['tabela']);
    $dados = $input['dados'];

    if (empty($dados)) {
        http_response_code(400);
        echo json_encode(["error" => "Nenhum campo de dados enviado."]);
        exit;
    }

    $tabelas_permitidas = ["Usuarios", "Ordem_de_Servico", "Item_OS", "Veiculos", "Acoplados", "Veiculos_acoplados", "Tipo_veiculo", "Layout_veiculo", "Veiculo_Fabricante", "Checklist"];
    if (!in_array($tabela, $tabelas_permitidas)) {
        http_response_code(400);
        echo json_encode(["error" => "Tabela não permitida."]);
        exit;
    }

    $campos = implode(", ", array_keys($dados));
    $placeholders = ":" . implode(", :", array_keys($dados));

    $sql = "INSERT INTO $tabela ($campos) VALUES ($placeholders)";
    $stmt = $conn->prepare($sql);
    $stmt->execute($dados);

    http_response_code(200);
    echo json_encode(["success" => true, "message" => "Dados inseridos com sucesso."]);

} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(["error" => $e->getMessage()]);
}
?>
