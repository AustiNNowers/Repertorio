CREATE TABLE mov_expo (
	id_interno int IDENTITY(1,1) NOT NULL UNIQUE,
	nome_navio nvarchar(30),
	navio_viagem nvarchar(30),
	viagem nvarchar(20),
	data_atracacao datetime,
	armador nvarchar(50),
	booking int,
	data_deadline datetime,
	conteiner nvarchar(15),
	data_chegada datetime,
	data_recepcao datetime,
	data_de_ordem_embarque datetime,
	data_entrega_cct datetime,
	tara float(53),
	PRIMARY KEY (id_interno)
);

CREATE TABLE mov_impo (
	id_interno int IDENTITY(1,1) NOT NULL UNIQUE,
	tipo_operacao nvarchar(20),
	armador nvarchar(50),
	nome_navio nvarchar(20),
	data_chegada datetime,
	data_liberacao datetime,
	conteiner_tipo_operacao nvarchar(20),
	codigo_conteiner nvarchar(20),
	tipo_conteiner nvarchar(30),
	data_descarga datetime,
	data_desova datetime,
	armazem_avaria nvarchar(10),
	armazem_peso float(53),
	armazem_volume float(53),
	PRIMARY KEY (id_interno)
);

CREATE TABLE consulta_navio (
	id_interno int IDENTITY(1,1) NOT NULL UNIQUE,
	nome_navio nvarchar(20),
	viagem_carga nvarchar(10),
	viagem_descarga nvarchar(10),
	status_navio nvarchar(20),
	data_deadline datetime,
	data_atracacao_prevista datetime,
	data_desatracacao_prevista datetime,
	data_atracacao_realizada datetime,
	data_desatracacao_realizada datetime,
	PRIMARY KEY (id_interno)
);