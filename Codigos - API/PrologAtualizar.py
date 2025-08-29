import pandas as pd
from datetime import datetime, timedelta
import asyncio
import aiohttp
import time
import requests
import math
import subprocess
import sys

ids_enviados = {
    "Prolog_Layout_veiculo": set(),
    "Prolog_Tipo_veiculo": set(),
    "Prolog_Veiculo_Fabricante": set(),
    "Prolog_Veiculos_acoplados": set(),
    "Prolog_Acoplados": set(),
    "Prolog_Veiculos": set(),
    "Prolog_Usuarios": set(),
    "Prolog_Checklist": set(),
    "Prolog_Ordem_de_Servico": set(),
    "Prolog_Item_OS": set()
}

url_php = "Confidencial"
base_url_prolog = "Confidencial"
end_url = {
            "Tipo_veiculo" : "vehicles/types/paginated?",
            "Veiculo_Fabricante" : "vehicles/makes/paginated?",
            "Veiculos" : "vehicles?",
            "Usuarios" : "users?",
            "Checklist" : "checklists?",
            "Ordem_de_Servico" : "work-orders?"
           }    

token = "Confidencial"

headers_prolog = {
    "x-prolog-api-token" : token,
    "Content-Type" : "application/json"
}

headers_php = {
    'Content-Type': 'application/json',
    'charset': 'utf-8'
}

unidades = {988: "Transporte", 2083: "Florestal"}

startDate = "2025-01-01"
endDate = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")

class Limite_Requisicoes:
    def __init__(self, requisicoes=40, tempo=60):
        self.requisicoes = requisicoes
        self.tempo = tempo
        self.tokens = requisicoes
        self.lock = asyncio.Lock()
        self.ultimo_reset = time.monotonic()

    async def requisicao(self):
        async with self.lock:
            tempo_atual = time.monotonic()
            lapso = tempo_atual - self.ultimo_reset
            self.ultimo_reset = tempo_atual
            self.tokens += lapso * (self.tempo / self.requisicoes)
            if self.tokens > self.requisicoes:
                self.tokens = self.requisicoes
            if self.tokens < 1:
                espere = (1 - self.tokens) * (self.tempo / self.requisicoes)
                await asyncio.sleep(espere)
                self.tokens = 0
            else:
                self.tokens -= 1

limite_requisicoes = Limite_Requisicoes(requisicoes = 40, tempo = 60)

async def gerenciar_loops():
    print("Gerenciando funções...")
    async with aiohttp.ClientSession(headers=headers_prolog) as session:

        for nome, endpoint in end_url.items():
            tarefas = []
            tarefas.append(gerenciar_tarefas(endpoint, nome, session))
            await asyncio.gather(*tarefas)

async def gerenciar_tarefas(end_url, nome, session):
    todos_dados = []
    for unidade_id, nome_unidade in unidades.items():
        print(f"Unidade: {nome_unidade} - Endpoint: {end_url}")

        if end_url == "Tipo_veiculo" or end_url == "Veiculo_Fabricante": 
            paginaAtual = verificarPaginaAtual(nome)
        else:
            paginaAtual = verificarPaginaAtual(nome, nome_unidade)

        todos_dados.append(await buscar_dados(end_url, unidade_id, paginaAtual, session))

    await salvar_dados(todos_dados, nome)

def verificarPaginaAtual(nomeTabela, nomeUnidade=None):
    try:
        url = f"{url_php}?tabela=Prolog_{nomeTabela}&ultimo=1"
        if nomeUnidade:
            url += f"&unidade={nomeUnidade}"

        resposta = requests.get(url)
        print(resposta.status_code, resposta.text)
        dados = resposta.json()

        for _, ultimaPagina in dados.items():
            print(f"Última página da tabela {nomeTabela} para unidade {nomeUnidade}: {ultimaPagina}")
            return int(ultimaPagina or 0)
    except Exception as e:
        print(f"Erro ao verificar última página da tabela {nomeTabela}: {e}")
        return 0

async def buscar_dados(endpoint, unidade_id, paginaAtual, session):
    pageNumberBackup = 0
    print(f"Dados salvos do {endpoint} da unidade {unidade_id} vão até á: {paginaAtual}")
    if paginaAtual <= 1:
        pageNumber = paginaAtual
    else:
        pageNumber = paginaAtual - 2
        
    todos_dados = []

    while True:
        if pageNumberBackup != 0:
            pageNumber = pageNumberBackup
            pageNumberBackup = 0

        params = parametros(endpoint, unidade_id, pageNumber)
        print("Endpoint: ", endpoint)
        print("Unidade ID: ", unidade_id)

        try:
            await limite_requisicoes.requisicao()
            async with session.get(base_url_prolog + endpoint, params=params) as resposta:
                if resposta.status == 200:
                    dados = await resposta.json()
                    print("Dados recebidos com sucesso!")
                elif resposta.status == 429:
                    tentar_novamente = int(resposta.headers_prolog.get("x-rate-limit-retry-after-seconds", 10))
                    print(f"Rate limit atingido. Aguardando {tentar_novamente} segundos.")
                    await asyncio.sleep(tentar_novamente)
                elif resposta.status in [502, 500]:
                    print(f"Erro {resposta.status}: Bad Gateway. Tentando novamente...")
                    await asyncio.sleep(10)
                    pageNumberBackup = pageNumber
                    continue
                else:
                    print(f"Erro {resposta.status}: {resposta.text}")
                    break

                for item in dados.get("content", []):
                    item["pagina_origem"] = pageNumber

                    if endpoint == "checklists?":
                        if unidade_id == 988:
                            item["unidade"] = "Transporte"
                        elif unidade_id == 2083:
                            item["unidade"] = "Florestal"

                    if endpoint == "work-orders?" and "checklistId" not in item:
                        item["checklistId"] = None

                todos_dados.extend(dados.get("content", []))

                if dados.get("lastPage", True):
                    print(f"Chegou na ultima pagina: {pageNumber}")
                    break

                print("Pagina atual: ", pageNumber)
                pageNumber += 1
                print("Próxima página: ", pageNumber)

        except aiohttp.ClientError as e:
            print(f"Erro de conexão com a API: {e}")
            break
    
    print("Retornando os dados coletados da unidade: ", unidade_id)
    df = pd.DataFrame(todos_dados) if todos_dados else pd.DataFrame()
        
    return df

def parametros(endpoint, unidade_id, pageNumber):
    params = {}

    if endpoint == "checklists?":
        params = {
            "branchOfficesId" : unidade_id,
            "startDate" : startDate,
            "endDate" : endDate,
            "includeAnswers" : "True",
            "pageSize" : 100,
            "pageNumber" : pageNumber
        }
    elif endpoint == "work-orders?":
        params = {
            "branchOfficesId" : unidade_id,
            "includeItems" : "True",
            "pageSize" : 100,
            "pageNumber" : pageNumber
        }
    elif endpoint == "vehicles?":
        params = {
            "branchOfficesId" : unidade_id,
            "includeInactive" : "True",
            "pageSize" : 100,
            "pageNumber" : pageNumber
        }
    elif endpoint == "vehicles/types/paginated?":
        params = {
                "companyId" : 247,
                "pageSize" : 100,
                "pageNumber" : pageNumber
            }
    elif endpoint == "vehicles/makes/paginated?":
        params = {
            "companyId" : 247,
            "pageSize" : 100,
            "pageNumber" : pageNumber,
            "includeInactive" : "True",
            "includeInactiveModels" : "True"
        }
    elif endpoint == "users?":
        params = {
            "branchOfficesId" : unidade_id,
            "pageSize" : 100,
            "pageNumber" : pageNumber
        }

    return params

async def salvar_dados(planilha, nome):
    print("Começando a entregar os dados...")

    planilha = [df for df in planilha if not df.empty]
    if not planilha:
        print(f"Nenhum dado encontrado para a tabela {nome}.")
        return

    df_novo = pd.concat(planilha, ignore_index=True)

    if df_novo.empty:
        print(f"Nenhum dado encontrado para a tabela {nome}.")
        return
    
    print(f"Quantidade de registros coletados para {nome}: {len(df_novo)}")
    
    df_novo = tratar_dados(df_novo, nome)
    linhas = df_novo.to_dict(orient="records")

    print("Planilhas tratadas com sucesso!")

    json_para_envio = {
        "Prolog_Layout_veiculo": [],
        "Prolog_Tipo_veiculo": [],
        "Prolog_Veiculo_Fabricante": [],
        "Prolog_Veiculos_acoplados": [],
        "Prolog_Acoplados": [],
        "Prolog_Veiculos": [],
        "Prolog_Usuarios": [],
        "Prolog_Checklist": [],
        "Prolog_Ordem_de_Servico": [],
        "Prolog_Item_OS": []
    }

    for linha in linhas:
        json_gerados = await criar_json(linha, nome)
        if json_gerados:
            for j in json_gerados:
                tabela = j["tabela"]
                json_para_envio[tabela].append(j)

    ordem_de_envio = [
        "Prolog_Layout_veiculo",
        "Prolog_Tipo_veiculo",
        "Prolog_Veiculo_Fabricante",
        "Prolog_Veiculos_acoplados",
        "Prolog_Acoplados",
        "Prolog_Veiculos",
        "Prolog_Usuarios",
        "Prolog_Checklist",
        "Prolog_Ordem_de_Servico",
        "Prolog_Item_OS"
    ]
    
    print(f"Total de JSONs gerados para envio ({nome}): {len(json_para_envio[tabela])}")

    async with aiohttp.ClientSession() as session:
        for tabela in ordem_de_envio:
            if json_para_envio[tabela]:
                print(f"Enviando dados para a tabela: {tabela}")
                if tabela in ["Prolog_Checklist", "Prolog_Ordem_de_Servico", "Prolog_Item_OS"]:
                    for lote in dividir_em_lotes(json_para_envio[tabela], tamanho_lote=50):
                        tarefas = [enviar_para_php(session, j) for j in lote]
                        await asyncio.gather(*tarefas)
                        await asyncio.sleep(0.5)
                else:
                    tarefas = [enviar_para_php(session, j) for j in json_para_envio[tabela]]
                    await asyncio.gather(*tarefas)

def dividir_em_lotes(lista, tamanho_lote):
    for i in range(0, len(lista), tamanho_lote):
        yield lista[i:i + tamanho_lote]

def tratar_dados(df, nome):
    if df.empty:
        print("Nenhum dado encontrado para salvar.")
        return pd.DataFrame()

    if nome == "Checklist":
        df = df.explode("formItemsAnswers")

    elif nome == "Veiculos":
        df = pd.json_normalize(df.to_dict(orient="records"))
        df = df.explode("coupling.coupledVehicles")

    elif nome == "Veiculo_Fabricante":
        df = df.explode("models")

    elif nome == "Ordem_de_Servico":
        df = pd.json_normalize(df.to_dict(orient="records"))
        df = df.explode("workOrderItems")
        df = pd.json_normalize(df.to_dict(orient="records"))
        df = df.explode("workOrderItems.itemServices")
        df = df.explode("workOrderItems.itemProducts")
        df = df.explode("workOrderItems.openingAttachments")
        df = df.explode("workOrderItems.resolutionAttachments")

    df = pd.json_normalize(df.to_dict(orient="records"))
    return df

def clean_nans(dados):
    if isinstance(dados, dict):
        return {k: clean_nans(v) for k, v in dados.items()}
    elif isinstance(dados, list):
        return [clean_nans(item) for item in dados]
    elif isinstance(dados, float) and math.isnan(dados):
        return None
    elif pd.isna(dados):
        return None
    else:
        return dados

def converter_data(data_iso):
    if pd.isnull(data_iso):
        return None
    try:
        if "." in data_iso:
            data_obj = datetime.strptime(data_iso, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            data_obj = datetime.strptime(data_iso, "%Y-%m-%dT%H:%M:%SZ")
        return data_obj.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        print(f"Erro ao converter data: {data_iso} - {e}")
        return None

async def criar_json(linha, nome):
    json_gerados = []

    if nome == "Checklist":
        id_checklist = linha['id']

        if pd.notnull(id_checklist):
            if id_checklist not in ids_enviados["Prolog_Checklist"]:
                json_data = {
                    "tabela": "Prolog_Checklist",
                    "dados": {
                        "id_checklist": id_checklist,
                        "id_usuario": linha['submittedBy.id'],
                        "id_veiculo": linha['vehicle.id'],
                        "unidade" : linha['unidade'],
                        "odometro": linha['odometerReading'],
                        "tipo_checklist": linha['checklistType'],
                        "data_submissao": converter_data(linha['submittedAt']),
                        "duracao_checklist": linha['checklistDuration'],
                        "teve_assinatura_eletronica": linha['hasElectronicSignature'],
                        "total_ok": linha['totalOkItems'],
                        "total_nok": linha['totalNokItems'],
                        "total_ok_alternativas": linha['totalOkAlternatives'],
                        "total_nok_alternativas": linha['totalNokAlternatives'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Checklist"].add(id_checklist)

    elif nome == "Veiculos":
        id_veiculo_acoplado = linha['coupling.coupledVehicles.id']
        id_acoplamento = linha['coupling.couplingProcessId']
        id_veiculo = linha['id']

        if pd.notnull(id_veiculo_acoplado):
            if id_veiculo_acoplado not in ids_enviados["Prolog_Veiculos_acoplados"]:
                json_vei_acoplados = {
                    "tabela": "Prolog_Veiculos_acoplados",
                    "dados": {
                        "id_veiculo_acoplado": id_veiculo_acoplado,
                        "placa": linha['coupling.coupledVehicles.licensePlate'],
                        "tipo": linha['coupling.coupledVehicles.type'],
                        "id_frota": linha['coupling.coupledVehicles.fleetId'],
                        "motorizada": linha['coupling.coupledVehicles.motorized'],
                        "tem_hubodometro": linha['coupling.coupledVehicles.hasHubodometer'],
                        "posicao_do_acoplada": linha['coupling.coupledVehicles.coupledAtPosition'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_vei_acoplados)
                ids_enviados["Prolog_Veiculos_acoplados"].add(id_veiculo_acoplado)

        if pd.notnull(id_acoplamento):
            if id_acoplamento not in ids_enviados["Prolog_Acoplados"]:
                json_acoplados = {
                    "tabela": "Prolog_Acoplados",
                    "dados": {
                        "id_acoplamento": id_acoplamento,
                        "id_veiculos_acoplados": id_veiculo_acoplado,
                        "posicao_do_acoplamento": linha['coupling.coupledAtPosition'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_acoplados)
                ids_enviados["Prolog_Acoplados"].add(id_acoplamento)

        if pd.notnull(id_veiculo):
            if id_veiculo not in ids_enviados["Prolog_Veiculos"]:
                json_data = {
                    "tabela": "Prolog_Veiculos",
                    "dados": {
                        "id_veiculo": id_veiculo,
                        "id_acoplado": id_acoplamento,
                        "id_tipo_veiculo": linha['type.id'],
                        "id_fabricante": linha['make.id'],
                        "placa_veiculo": linha['licensePlate'],
                        "id_frota": linha['fleetId'],
                        "tem_hubodometro": linha['hasHubodometer'],
                        "unidade": linha['branchOfficeName'],
                        "ativo": linha['active'],
                        "acoplado": linha['coupled'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Veiculos"].add(id_veiculo)

    elif nome == "Tipo_veiculo":
        id_layout = linha['vehicleLayout.id']
        id_tipo_veiculo = linha['id']

        if pd.notnull(id_layout):
            if id_layout not in ids_enviados["Prolog_Layout_veiculo"]:
                json_layout = {
                    "tabela": "Prolog_Layout_veiculo",
                    "dados": {
                        "id_layout": id_layout,
                        "nome": linha['vehicleLayout.name'],
                        "tem_motor": linha['vehicleLayout.hasEngine'],
                        "quant_eixos_frontais": linha['vehicleLayout.frontAxleQuantity'],
                        "quant_eixos_traseiros": linha['vehicleLayout.rearAxleQuantity'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_layout)
                ids_enviados["Prolog_Layout_veiculo"].add(id_layout)

        if pd.notnull(id_tipo_veiculo):
            if id_tipo_veiculo not in ids_enviados["Prolog_Tipo_veiculo"]:
                json_data = {
                    "tabela": "Prolog_Tipo_veiculo",
                    "dados": {
                        "id_tipo_veiculo": id_tipo_veiculo,
                        "id_layout": id_layout,
                        "nome_veiculo": linha['name'],
                        "ativo": linha['isActive'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Tipo_veiculo"].add(id_tipo_veiculo)


    elif nome == "Veiculo_Fabricante":
        id_fabricante = linha['id']
        if pd.notnull(id_fabricante):
            if id_fabricante not in ids_enviados["Prolog_Veiculo_Fabricante"]:
                json_data = {
                    "tabela": "Prolog_Veiculo_Fabricante",
                    "dados": {
                        "id_fabricante": id_fabricante,
                        "nome_fabricante": linha['name'],
                        "nome_modelo": linha['models.name'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Veiculo_Fabricante"].add(id_fabricante)

    elif nome == "Ordem_de_Servico":
        id_ordem_servico = linha['workOrderId']

        if pd.notnull(id_ordem_servico):
            if id_ordem_servico not in ids_enviados["Prolog_Ordem_de_Servico"]:
                json_data = {
                    "tabela": "Prolog_Ordem_de_Servico",
                    "dados": {
                        "id_ordem_servico": id_ordem_servico,
                        "id_veiculo": linha['vehicle.id'],
                        "id_usuario": linha['createdBy.id'],
                        "id_checklist": linha.get('checklistId'),
                        "unidade": linha.get('branchOfficeName'),
                        "data_de_criacao": converter_data(linha.get('createdAt')),
                        "data_de_abertura": converter_data(linha.get('openingDate')),
                        "odometro": linha.get('odometerReading'),
                        "status_ordem": linha.get('workOrderStatus'),
                        "origem": linha.get('originType'),
                        "tipo_de_fonte": linha.get('sourceType'),
                        "quant_de_prioridades_critico": linha.get('criticalPriorityQuantity'),
                        "quant_de_prioridades_alta": linha.get('highPriorityQuantity'),
                        "quant_de_prioridades_baixa": linha.get('lowPriorityQuantity'),
                        "notas": linha.get('notes'),
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Ordem_de_Servico"].add(id_ordem_servico)

        id_item = linha['workOrderItems.itemId']
        
        if pd.notnull(id_item):
            if id_item not in ids_enviados["Prolog_Item_OS"]:
                json_item_os = {
                    "tabela": "Prolog_Item_OS",
                    "dados": {
                        "id_item": id_item,
                        "id_ordem_de_servico": id_ordem_servico,
                        "usuario_finalizador": linha['workOrderItems.completionBy.name'],
                        "item_nome": linha['workOrderItems.itemName'],
                        "item_descricao": linha['workOrderItems.itemDescription'],
                        "prioridade": linha['workOrderItems.priority'],
                        "tipo_de_manutencao": linha['workOrderItems.itemMaintenanceType'],
                        "tipo_de_origem": linha['workOrderItems.itemOriginType'],
                        "item_status": linha['workOrderItems.resolutionItemStatus'],
                        "data_inicio_de_finalizacao": converter_data(linha['workOrderItems.completionStartedAt']),
                        "data_fim_de_finalizacao": converter_data(linha['workOrderItems.completionFinishedAt']),
                        "duracao_da_conclusao": linha['workOrderItems.completionDuration'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_item_os)
                ids_enviados["Prolog_Item_OS"].add(id_item)

    elif nome == "Usuarios":
        id_usuario = linha['id']
        if pd.notnull(id_usuario):
            if id_usuario not in ids_enviados["Prolog_Usuarios"]:
                json_data = {
                    "tabela": "Prolog_Usuarios",
                    "dados": {
                        "id_usuario": id_usuario,
                        "nome_usuario": linha['name'],
                        "unidade": linha['branchOfficeName'],
                        "ativo": linha['status'],
                        "nome_da_funcao": linha['roleName'],
                        "nome_do_setor": linha['sectorName'],
                        "nome_da_equipe": linha['teamName'],
                        "pagina_origem": linha['pagina_origem']
                    }
                }
                json_gerados.append(json_data)
                ids_enviados["Prolog_Usuarios"].add(id_usuario)

    else:
        print(f"Nome de planilha desconhecido: {nome}")

    return json_gerados

async def enviar_para_php(session, json_obj):
    if isinstance(json_obj.get('dados'), dict):
        json_obj['dados'] = clean_nans(json_obj['dados'])
    else:
        print("Formato inesperado no campo 'dados':", json_obj)
        return

    try:
        async with session.post(url_php, headers=headers_php, json=json_obj) as response:
            if response.status == 200:
                print(f"Dados enviados com sucesso para a tabela: {json_obj['tabela']}")
            else:
                print(f"Erro ao enviar dados: {response.status} - {await response.text()}")
    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    try:
        start = time.perf_counter()
        print("Iniciando o processo...")
        asyncio.run(gerenciar_loops())
        print("Processo concluído!")
        end = time.perf_counter()
        print(f"Tempo de execução: {end - start:.2f} segundos")
        subprocess.run(r"C:\Users\Administrator.VALE\Documents\API's\Executaveis\PrologAtualizar.exe")
        sys.exit()
    except Exception as e:
        print(f"Erro durante execução: {e}")
        subprocess.run(r"C:\Users\Administrator.VALE\Documents\API's\Executaveis\PrologAtualizar.exe")
        sys.exit()