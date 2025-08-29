
DROP TABLE IF EXISTS Item_OS;
DROP TABLE IF EXISTS Ordem_de_Servico;
DROP TABLE IF EXISTS Checklist;
DROP TABLE IF EXISTS Veiculos;
DROP TABLE IF EXISTS Acoplados;
DROP TABLE IF EXISTS Veiculos_acoplados;
DROP TABLE IF EXISTS Tipo_veiculo;
DROP TABLE IF EXISTS Layout_veiculo;
DROP TABLE IF EXISTS Veiculo_Fabricante;
DROP TABLE IF EXISTS Usuarios;

CREATE TABLE Layout_veiculo (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_layout INT NOT NULL UNIQUE,
    nome NVARCHAR(100),
    tem_motor BIT,
    quant_eixos_frontais NVARCHAR(MAX),
    quant_eixos_traseiros NVARCHAR(MAX),
	pagina_origem SMALLINT
);

CREATE TABLE Tipo_veiculo (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_tipo_veiculo INT NOT NULL UNIQUE,
    id_layout INT NOT NULL,
    nome_veiculo NVARCHAR(MAX),
    ativo BIT,
	pagina_origem SMALLINT
);

CREATE TABLE Veiculo_Fabricante (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_fabricante INT NOT NULL UNIQUE,
    nome_fabricante NVARCHAR(50),
    nome_modelo NVARCHAR(50),
	pagina_origem SMALLINT
);

CREATE TABLE Veiculos_acoplados (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_veiculo_acoplado INT NOT NULL UNIQUE,
    placa NVARCHAR(10) NOT NULL,
    tipo NVARCHAR(50),
    id_frota NVARCHAR(20) NOT NULL,
    motorizada BIT,
    tem_hubodometro BIT,
    posicao_do_acoplada NVARCHAR(MAX),
	pagina_origem SMALLINT
);

CREATE TABLE Acoplados (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_acoplamento INT NOT NULL UNIQUE,
    id_veiculos_acoplados INT,
    posicao_do_acoplamento NVARCHAR(MAX),
	pagina_origem SMALLINT
);


CREATE TABLE Veiculos (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_veiculo INT NOT NULL UNIQUE,
    id_acoplado INT,
    id_tipo_veiculo INT NOT NULL,
    id_fabricante INT NOT NULL,
    placa_veiculo NVARCHAR(20) NOT NULL,
    id_frota NVARCHAR(20),
    tem_hubodometro BIT DEFAULT 1,
    unidade NVARCHAR(20),
    ativo BIT DEFAULT 1,
    acoplado BIT,
	pagina_origem SMALLINT
);

CREATE TABLE Usuarios (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    nome_usuario NVARCHAR(200) NOT NULL,
    unidade NVARCHAR(20),
    ativo BIT NOT NULL DEFAULT 1,
    nome_da_funcao NVARCHAR(50),
    nome_do_setor NVARCHAR(50),
    nome_da_equipe NVARCHAR(50),
	pagina_origem SMALLINT
);

CREATE TABLE Checklist (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_checklist INT NOT NULL UNIQUE,
    id_usuario INT NOT NULL,
    id_veiculo INT NOT NULL,
	unidade CHAR(50) NOT NULL,
    odometro INT,
    tipo_checklist NVARCHAR(20),
    data_submissao DATETIME,
    duracao_checklist INT,
    teve_assinatura_eletronica BIT,
    total_ok SMALLINT,
    total_nok SMALLINT,
    total_ok_alternativas SMALLINT,
    total_nok_alternativas SMALLINT,
	pagina_origem SMALLINT
);

CREATE TABLE Ordem_de_Servico (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_ordem_servico INT NOT NULL UNIQUE,
    id_veiculo INT NOT NULL,
    id_usuario INT NOT NULL,
    id_checklist INT,
    unidade NVARCHAR(50),
    data_de_criacao DATETIME NOT NULL,
    data_de_abertura DATETIME NOT NULL,
    odometro INT,
    status_ordem CHAR(7) DEFAULT 1,
    origem NVARCHAR(50),
    tipo_de_fonte NVARCHAR(10),
    quant_de_prioridades_critico NVARCHAR(MAX),
    quant_de_prioridades_alta NVARCHAR(MAX),
    quant_de_prioridades_baixa NVARCHAR(MAX),
    notas NVARCHAR(250),
	pagina_origem SMALLINT
);

CREATE TABLE Item_OS (
    id_interno INT IDENTITY(1,1) PRIMARY KEY,
    id_item INT NOT NULL UNIQUE,
    id_ordem_de_servico INT NOT NULL,
    usuario_finalizador NVARCHAR(100),
    item_nome NVARCHAR(150),
    item_descricao NVARCHAR(500),
    prioridade NVARCHAR(25),
    tipo_de_manutencao NVARCHAR(25),
    tipo_de_origem NVARCHAR(20),
    status_item NVARCHAR(20),
    data_inicio_de_finalizacao DATETIME,
    data_fim_de_finalizacao DATETIME,
    duracao_da_conclusao INT,
	pagina_origem SMALLINT
);

ALTER TABLE Tipo_veiculo ADD CONSTRAINT FK_Tipo_veiculo_Layout FOREIGN KEY (id_layout) REFERENCES Layout_veiculo(id_layout);
ALTER TABLE Veiculos ADD CONSTRAINT FK_Veiculos_Acoplados FOREIGN KEY (id_acoplado) REFERENCES Acoplados(id_acoplamento);
ALTER TABLE Veiculos ADD CONSTRAINT FK_Veiculos_Tipo FOREIGN KEY (id_tipo_veiculo) REFERENCES Tipo_veiculo(id_tipo_veiculo);
ALTER TABLE Veiculos ADD CONSTRAINT FK_Veiculos_Fabricante FOREIGN KEY (id_fabricante) REFERENCES Veiculo_Fabricante(id_fabricante);
ALTER TABLE Acoplados ADD CONSTRAINT FK_Acoplados_Veiculos_Acoplados FOREIGN KEY (id_veiculos_acoplados) REFERENCES Veiculos_acoplados(id_veiculo_acoplado);
ALTER TABLE Checklist ADD CONSTRAINT FK_Checklist_Usuarios FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario);
ALTER TABLE Checklist ADD CONSTRAINT FK_Checklist_Veiculos FOREIGN KEY (id_veiculo) REFERENCES Veiculos(id_veiculo);
ALTER TABLE Ordem_de_Servico ADD CONSTRAINT FK_Veiculos FOREIGN KEY (id_veiculo) REFERENCES Veiculos(id_veiculo);
ALTER TABLE Ordem_de_Servico ADD CONSTRAINT FK_Usuarios FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario);
ALTER TABLE Item_OS ADD CONSTRAINT FK_Item_OS FOREIGN KEY (id_ordem_de_servico) REFERENCES Ordem_de_Servico(id_ordem_servico);