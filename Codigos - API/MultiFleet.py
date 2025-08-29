import requests
import urllib3
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import re
import math
import time
import json
import sys
import subprocess

url_php = "Confidencial"
base_url = "Confidencial"

header_php = {
    "Content-Type": "application/json; charset=utf-8"
}

campos_referencias = {
    "matricula_operador" : "MATRICULA DO OPERADOR",
    "matricula_comboista" : ["MATRÍCULA DO COMBOISTA", "INFORME A MATRÍCULA"],
    "matricula_mecanico" : "MATRÍCULA DO MECÂNICO",
    "tipo_falha" : "TIPO DE FALHA",
    "atividade_anterior_apropriacao" : "ATIVIDADE(S) ANTES DA APROPRIAÇÃO",
    "avaliacao" : "AVALIAÇÃO",
    "tipo_avaliacao" : ["INSPEÇÃO VISUAL", "CHECK LIST"],
    "equipamento_disponivel" : ["DISPONIBILIDADE DO EQUIPAMENTO", "EQUIPAMENTO DISPONÍVEL?"],
    "motivo_indisponibilidade" : "MOTIVO DA INDISPONIBILIDADE",
    "horimetro_motor" : "HORIMETRO DO MOTOR",
    "tipo_oleo" : "TIPO DE ÓLEO",
    "quantidade_abastecida" : "QUANTIDADE ABASTECIDA",
    "volume_carga_caminhao" : "VOLUME DA CARGA DO CAMINHÃO",
    "frota_caminhao" : "FROTA DO CAMINHÃO",
    "balanca" : "BALANÇA",
    "box_descarga" : "BOX",
    "motivo" : "MOTIVO",
    "status_inicio_abastecimento" : "STATUS",
    "tipo_operacao" : "TIPO DE OPERAÇÃO",
    "talhao_operacao" : "TALHÃO",
    "tipo_produto" : "TIPO DE PRODUTO",
    "quantidade_arvores_cortadas" : "QUANTIDADE DE ÁRVORES CORTADAS",
    "informe_producao" : "INFORME A PRODUÇÃO",
    "volume_caixa_carga" : "VOLUME DA CAIXA DE CARGA",
    "tipo_servico" : "TIPO DE SERVIÇO",
    "quantidade_toco" : "QUANTIDADE DE TOCOS",
    "hectares" : "HECTÁRES",
    "parada" : "CÓDIGO DA PARADA"
}

end_urls = [
    "counters?", "forms?", "points?", "notes?", "new_production?", "new_production_products?"
]
#
def criar_token():
    url_auth = "Confidencial"
    payload = {
        "grant_type": "Confidencial",
        "username": "Confidencial",
        "password": "Confidencial",
        "client_id": "Confidencial",
        "client_secret": "Confidencial"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resposta = requests.post(url_auth, data=payload, headers=headers, verify=False)
         
        if resposta.status_code == 200:
            token = resposta.json().get("access_token")
            print("Token criado com sucesso!")
            salvar_token(token)
        else:
            print("Erro ao criar token!")
            print(f"Código: {resposta.status_code}")
            print(f"Erro: {resposta.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar à API para criar token: {e}")

def salvar_token(token):
    with open("token.txt", "w") as f:
        f.write(token)
    print("Token salvo com sucesso!")
    carregar_token()

def carregar_token():
    global token
    try:
        with open("token.txt", "r") as f:
            token = f.read()
        print("Token carregado com sucesso!")

        if not token:
            print("Token está vazio, criando um novo token...")
            criar_token()

    except FileNotFoundError:
        print("Arquivo token.txt não encontrado!")
        criar_token()
    
def gerenciar_funcoes():
    for end_url in end_urls:
        data_retornada = verificar_dados_existentes(end_url)

        if data_retornada:
            buscar_dados(data_retornada, end_url)
        else:
            print(f"Não foi possível verificar dados existentes para {end_url}.")
    
def verificar_dados_existentes(end_url):
    try:
        if end_url == "counters?":
            nome_tabela = "TimberFleet_Contadores"
        elif end_url == "forms?":
            nome_tabela = "TimberFleet_Formulario"
        elif end_url == "points?":
            nome_tabela = "TimberFleet_Localizacao"
        elif end_url == "notes?":
            nome_tabela = "TimberFleet_Apontamentos"
        elif end_url == "new_production?":
            nome_tabela = "TimberFleet_Producao"
        elif end_url == "new_production_products?":
            nome_tabela = "TimberFleet_Produtos_producao"

        url = f"{url_php}?tabela={nome_tabela}&ultimaData=true"

        resposta = requests.get(url, headers=header_php)
        print(resposta.status_code, resposta.text)
        dados = resposta.json()
        print("Dados recebidos:",dados)
        data_retornada = datetime(2025, 1, 1)

        if isinstance(dados, dict):
            for chave, valor in dados.items():
                print(f"Chave: {chave} | Valor: {valor}")
                if valor:
                    try:
                        data_retornada = datetime.strptime(valor, "%Y-%m-%d")
                    except ValueError:
                        print(f"Formato inválido de data: {valor}")
        elif isinstance(dados, list):
            if not dados:
                print("A resposta é uma lista vazia.")
            else:
                print(f"A resposta é uma lista com valor: {dados[0]}")
                try:
                    data_retornada = datetime.strptime(dados[0], "%Y-%m-%d")
                except ValueError:
                    print(f"Formato inválido de data: {dados[0]}")
        else:
            print(f"Tipo de resposta: {type(dados)}")
            print("Conteúdo da resposta:", dados)

        print("Data retornada:", data_retornada)
        return data_retornada
    
    except Exception as e:
        print(f"Erro ao verificar última página da tabela {end_url}: {e}")
        return datetime(2025, 1, 1)

def buscar_dados(data, end_url):
    print("Iniciou a busca de dados")

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {
        "authorization": f"Bearer {token}",
        "cache-control": "no-cache"
    }

    data_inicial = data
    data_final = datetime.now()
    tentativas = 0

    print("Entrou no loop para atualizar")
    while data_inicial <= data_final:
        start_exec = time.time()

        start_date = data_inicial.strftime("%Y-%m-%d 00:00:00")
        end_date = data_inicial.strftime("%Y-%m-%d 23:59:59")

        params = {
            "start_date": start_date,
            "end_date": end_date
        }

        try:
            resposta = requests.get(base_url + end_url, headers=headers, params=params, verify=False, allow_redirects=False)
            print(f"Resposta: {resposta.status_code} - {resposta.text}")

            if resposta.status_code == 200:
                try:
                    dados = resposta.json()
                except ValueError:
                    print("Erro ao decodificar JSON")
                    continue

                if isinstance(dados, str) and "Excesso de consulta" in dados:
                    tempo_espera = re.findall(r"Aguarde (\d+) segundos", dados)
                    if tempo_espera:
                        time.sleep(int(tempo_espera[0]) + 1)
                    continue

                if isinstance(dados, list) and len(dados) > 0:
                    for item in dados:
                        item["data_registro"] = data_inicial.strftime("%Y-%m-%d")
                    df = pd.DataFrame(dados)

                    try:
                        dados_tratados = tratar_dados(df, end_url)
                        try:
                            for linha in dados_tratados:
                                json = criar_json(linha, end_url)
                                json_limpo = limpar_vazios(json)
                                enviar_para_php(json_limpo)

                        except Exception as e:
                            print(f"Erro ao criar/enviar JSON: {e}")
                            data_inicial -= timedelta(days=1)

                    except Exception as e:
                        print(f"Erro ao tratar: {e}")
                        data_inicial -= timedelta(days=1)
                else:
                    print(f"Nenhum dado encontrado para {end_url} na data {data_inicial.strftime('%Y-%m-%d')}")
                    if tentativas < 1:
                        data_inicial -= timedelta(days=1)
                        tentativas += 1
                    else:
                        print("Tentativas excedidas, encerrando busca.")
                        tentativas = 0
                        data_inicial += timedelta(days=1)
                        continue
            elif resposta.status_code == 302:
                print("Token expirou!")
                criar_token()
                data_inicial -= timedelta(days=1)
                gerenciar_funcoes()
                break

            else:
                print(f"Erro na resposta da API: {resposta.status_code} - {resposta.text}")
                data_inicial -= timedelta(days=1)

        except Exception as e:
            print(f"Erro na requisição: {e}")

        tempo_passado = time.time() - start_exec
        tempo_restante = max(0, 70 - tempo_passado)
        print(f"Aguardando {tempo_restante:.2f} segundos para a próxima requisição...")
        time.sleep(tempo_restante)

        if data_inicial.date() == datetime.now().date():
            break
        else:
            data_inicial += timedelta(days=1)

def limpar_vazios(dados):
    if isinstance(dados, dict):
        return {k: limpar_vazios(v) for k, v in dados.items()}
    elif isinstance(dados, list):
        return [limpar_vazios(item) for item in dados]
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
        data = parser.parse(data_iso)
        data_sem_fuso = data.replace(tzinfo=None)
        data_formatada = datetime.strftime(data_sem_fuso, "%d-%m-%Y %H:%M:%S")
        
        return data_formatada
    
    except Exception as e:
        print(f"Erro ao converter data: {data_iso} - {e}")
        return None

def tratar_dados(df, end_url):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

    print("Tratando dados...")

    if end_url == "counters?":
        print("Separar colunas")
        df[['odometer_motor', 'odometer_operation', 'odometer_implement', 'odometer_travel', 'odometro_nao_usado']] = df['odometer'].str.split(';', expand=True).astype(float)
        df[['moving_time_motor', 'moving_time_operation', 'moving_time_implement', 'moving_time_travel', 'tempo_movimentacao_nao_usado']] = df['moving_time'].str.split(';', expand=True).astype(float)
        
        df[['odometer_motor_diff', 'odometer_operation_diff', 'odometer_implement_diff', 'odometer_travel_diff', 'odometro_nao_usado_diff']] = df['odometer_diff'].str.split(';', expand=True).astype(float)
        df[['moving_time_motor_diff', 'moving_time_operation_diff', 'moving_time_implement_diff', 'moving_time_travel_diff', 'tempo_movimentacao_nao_usado_diff']] = df['moving_time_diff'].str.split(';', expand=True).astype(float)

    elif end_url in ["forms?", "notes?"]:
        print("Separando form_content em form_title e form_content...")
        df[["form_title", "form_content"]] = df["form_content"].apply(lambda x: pd.Series(formatar_json(x)))
        df["form_content"] = df["form_content"].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else x)

        print("Removendo aspas duplas extras do form_content...")
        df_campos = dados_formularios(df["form_content"].replace('""', '', regex=True))
        df_novo = pd.concat([df, df_campos], axis=1)
        df = df_novo.drop(columns=["form_content"])

    elif end_url == "points?":
        print("Desfazer o lation para latitude e longitude")
        df[['latitude', 'longitude']] = df['latlon'].str.split(' ', expand=True).astype(float)

    elif end_url == "new_production?":
        print("Dividir por 10.000")
        df['volume_total'] = df['volume_total'].apply(lambda x: x / 10000 if isinstance(x, (int, float)) else x)
    
    elif end_url == "new_production_products?":
        print("Dividir por 10.000")
        df['volume'] = df['volume'].apply(lambda x: x / 10000 if isinstance(x, (int, float)) else x)

    if 'vehicle_desc' in df.columns:
        print("Removendo colchetes de vehicle_desc e vehicle_name")
        df['vehicle_desc'] = df['vehicle_desc'].str.replace(r'[\[\]]', ' ', regex=True).str.strip()

    if "vehicle_name" in df.columns:
        print("Removendo colchetes de vehicle_desc e vehicle_name")
        df['vehicle_name'] = df['vehicle_name'].str.replace(r'[\[\]]', ' ', regex=True).str.strip()
    
    print("Removendo duplicados...")
    df = df.drop_duplicates()
    df = df.to_dict(orient="records")

    return df

def formatar_json(content):
    try:
        texto_semi_corrigido = re.sub(r',\s*}', '}', content)
        texto_corrigido = re.sub(r',\s*\]', ']', texto_semi_corrigido)
        parsed = json.loads(texto_corrigido)
        return parsed.get("title", ""), parsed.get("form", "")
    except Exception as e:
        print(f"Erro ao parsear form_content: {e}")
        return "", ""

def dados_formularios(series):
    print("Mapeando dados do formulário...")
    mapeados = []
    for item in series:
        try:
            dados = json.loads(item)

        except Exception:
            mapeados.append({})
            continue    

        novo_dict = {}
        for chave, valor in dados.items():
            for nome_interno, nome_possivel in campos_referencias.items():
                if not isinstance(nome_possivel, list):
                    nome_possivel = [nome_possivel]
                
                if chave in nome_possivel:
                    if chave in {"informe_producao", "horimetro_motor"}:
                        print("Entrou no if do informe_producao")
                        novo_dict[nome_interno] = formatar_valor_float(limpar_valor(valor))
                        break
                    else:
                        novo_dict[nome_interno] = limpar_valor(valor)      
                        break

        mapeados.append(novo_dict)

    return pd.DataFrame(mapeados)

def formatar_valor_float(x):
    if x is None:
        return None
    
    s = str(x).strip().replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return x

def limpar_valor(valor):
    if valor is None:
        return None
    
    valor = str(valor).strip()
    valor = re.sub(r"^\d+-\s*", "", valor) 
    valor = re.sub(r';\s*$', '', valor)

    if valor in {'', ' -- '}:
        valor = '--'
    return valor

def criar_json(linha, end_url):
    print("Criando JSON...")
    print(linha)
    if end_url == "counters?":
        json_data = {
            "tabela": "TimberFleet_Contadores",
            "dados": {
                "id_ident" : "_".join([linha['vehicle_desc'], linha['operator_name'], linha['equip_date']]),
                "prefixo" : linha['vehicle_desc'].replace("VT-", ""), 
                "nome_operador" : linha['operator_name'],
                "data_contadores" : converter_data(linha['equip_date']),
                "operacao_status" : linha['vehicle_status_desc'],
                "odometro_motor" : round(linha['odometer_motor'], 2),
                "odometro_operacao" : round(linha['odometer_operation'], 2),
                "odometro_implemento" : round(linha['odometer_implement'], 2),
                "odometro_rodante" : round(linha['odometer_travel'], 2),
                "horimetro_motor" : linha['operation_hourmeter'],
                "horimetro_operacao" : linha['engine_hourmeter'],
                "horimetro_implemento" : linha['implement_hourmeter'],
                "horimetro_rodante" : linha['travel_hourmeter'],
                "ativacao_motor" : linha['engine_activation'],
                "ativacao_operacao" : linha['operation_activation'],
                "ativacao_implemento" : linha['implement_activation'],
                "ativacao_rodante" : linha['travel_activation'],
                "tempo_movimentacao_motor" : linha['moving_time_motor'],
                "tempo_movimentacao_operacao" : linha['moving_time_operation'],
                "tempo_movimentacao_implemento" : linha['moving_time_implement'],
                "tempo_movimentacao_rodante" : linha['moving_time_travel'],
                "diferenca_odometro_motor" : linha['odometer_motor_diff'],
                "diferenca_odometro_operacao" : linha['odometer_operation_diff'],
                "diferenca_odometro_implemento" : linha['odometer_implement_diff'],
                "diferenca_odometro_rodante" : linha['odometer_travel_diff'],
                "diferenca_horimetro_motor" : linha['operation_hourmeter_diff'],
                "diferenca_horimetro_operacao" : linha['engine_hourmeter_diff'],
                "diferenca_horimetro_implemento" : linha['implement_hourmeter_diff'],
                "diferenca_horimetro_rodante" : linha['travel_hourmeter_diff'],
                "diferenca_ativacao_motor" : linha['engine_activation_diff'],
                "diferenca_ativacao_operacao" : linha['operation_activation_diff'],
                "diferenca_ativacao_implemento" : linha['implement_activation_diff'],
                "diferenca_ativacao_rodante" : linha['travel_activation_diff'],
                "diferenca_tempo_movimentacao_motor" : linha['moving_time_motor_diff'],
                "diferenca_tempo_movimentacao_operacao" : linha['moving_time_operation_diff'],
                "diferenca_tempo_movimentacao_implemento" : linha['moving_time_implement_diff'],
                "diferenca_tempo_movimentacao_rodante" : linha['moving_time_travel_diff'],
                "data_registro" : linha['data_registro']
            }
        }
    elif end_url == "forms?":
        json_data = {
            "tabela": "TimberFleet_Formulario",
            "dados": {
                "id_ident" : "_".join([linha['vehicle_desc'], linha['operator_name'], linha['equip_date']]),
                "prefixo" : linha['vehicle_desc'].replace("VT-", "").replace("[", "").replace("]", ""),
                "data_formulario" : converter_data(linha['equip_date']),
                "nome_operador" : linha['operator_name'],
                "codigo_operador" : linha['operator_code'],
                "operacao_status" : linha['status_desc'],
                "titulo_formulario" : linha['form_title'],
                "matricula_operador" : linha.get('matricula_operador'),
                "matricula_comboista" : linha.get('matricula_comboista'),
                "matricula_mecanico" : linha.get('matricula_mecanico'),
                "tipo_falha" : linha.get('tipo_falha'),
                "atividade_anterior_apropriacao" : linha.get('atividade_anterior_apropriacao'),
                "avaliacao" : linha.get('tipo_avaliacao'),
                "equipamento_disponivel" : linha.get('equipamento_disponivel'),
                "motivo_indisponibilidade" : linha.get('motivo_indisponibilidade'),
                "horimetro_motor" : linha.get('horimetro_motor'),
                "tipo_oleo" : linha.get('tipo_oleo'),
                "quantidade_abastecida" : linha.get('quantidade_abastecida'),
                "volume_carga_caminhao" : linha.get('volume_carga_caminhao'),
                "frota_caminhao" : linha.get('frota_caminhao'),
                "balanca" : linha.get('balanca'),
                "box_descarga" : linha.get('box_descarga'),
                "motivo" : linha.get('motivo'),
                "status_inicio_abastecimento" : linha.get('status_inicio_abastecimento'),
                "tipo_operacao" : linha.get('tipo_operacao'),
                "talhao_operacao" : linha.get('talhao_operacao'),
                "tipo_produto" : linha.get('tipo_produto'),
                "quantidade_arvores_cortadas" : linha.get('quantidade_arvores_cortadas'),
                "informe_producao" : linha.get('informe_producao'),
                "volume_caixa_carga" : linha.get('volume_caixa_carga'),
                "tipo_servico" : linha.get('tipo_servico'),
                "quantidade_toco" : linha.get('quantidade_toco'),
                "hectares" : linha.get('hectares'),
                "parada" : linha.get('parada'),
                "data_registro" : linha['data_registro']
            }
        }

    elif end_url == "points?":
        json_data = {
            "tabela": "TimberFleet_Localizacao",
            "dados": {
                "id_ident" : "_".join([linha['vehicle_desc'], linha['operator_name'], linha['equip_date']]),
                "nome_operador" : linha['operator_name'],
                "prefixo" : linha['vehicle_desc'].replace("VT-", ""),
                "data_localizacao" : converter_data(linha['equip_date']),
                "latitude" : linha['latitude'],
                "longitude" : linha['longitude'],
                "operacao_status" : linha['status_desc'],
                "data_registro" : linha['data_registro']
            }
        }
    elif end_url == "notes?":
        json_data = {
            "tabela": "TimberFleet_Apontamentos",
            "dados": {
                "id_ident" : "_".join(str(linha.get(k, "")) for k in ['vehicle_desc', 'operator_name', 'start_date']),
                "prefixo" : linha['vehicle_desc'].replace("VT-", ""),
                "nome_operador" : linha['operator_name'],
                "codigo_operador" : linha['operator_code'],
                "data_inicio" : converter_data(linha['start_date']),
                "data_final" : converter_data(linha['final_date']),
                "inicio_horimetro_motor" : linha['start_engine_hourmeter'],
                "final_horimetro_motor" : linha['final_engine_hourmeter'],
                "operacao_status" : linha['status_desc'],
                "titulo_formulario" : linha['form_title'],
                "matricula_operador" : linha.get('matricula_operador'),
                "matricula_comboista" : linha.get('matricula_comboista'),
                "matricula_mecanico" : linha.get('matricula_mecanico'),
                "tipo_falha" : linha.get('tipo_falha'),
                "atividade_anterior_apropriacao" : linha.get('atividade_anterior_apropriacao'),
                "avaliacao" : linha.get('tipo_avaliacao'),
                "equipamento_disponivel" : linha.get('equipamento_disponivel'),
                "motivo_indisponibilidade" : linha.get('motivo_indisponibilidade'),
                "horimetro_motor" : linha.get('horimetro_motor'),
                "tipo_oleo" : linha.get('tipo_oleo'),
                "quantidade_abastecida" : linha.get('quantidade_abastecida'),
                "volume_carga_caminhao" : linha.get('volume_carga_caminhao'),
                "frota_caminhao" : linha.get('frota_caminhao'),
                "balanca" : linha.get('balanca'),
                "box_descarga" : linha.get('box_descarga'),
                "motivo" : linha.get('motivo'),
                "status_inicio_abastecimento" : linha.get('status_inicio_abastecimento'),
                "tipo_operacao" : linha.get('tipo_operacao'),
                "talhao_operacao" : linha.get('talhao_operacao'),
                "tipo_produto" : linha.get('tipo_produto'),
                "quantidade_arvores_cortadas" : linha.get('quantidade_arvores_cortadas'),
                "informe_producao" : linha.get('informe_producao'),
                "volume_caixa_carga" : linha.get('volume_caixa_carga'),
                "tipo_servico" : linha.get('tipo_servico'),
                "quantidade_toco" : linha.get('quantidade_toco'),
                "hectares" : linha.get('hectares'),
                "parada" : linha.get('parada'),
                "data_registro" : linha['data_registro']
            }
        }
    elif end_url == "new_production?":
        json_data = {
            "tabela": "TimberFleet_Producao",
            "dados": {
                "id_ident" : "_".join([linha['vehicle_name'], linha['operator_name'], linha['equip_date']]),
                "tipo_arquivo" : linha['file_type'],
                "prefixo" : linha['vehicle_name'].replace("VT-", ""),
                "nome_operador" : linha['operator_name'],
                "data_producao" : converter_data(linha['equip_date']),
                "contagem_arvores" : linha['tree_amount'],
                "volume_total" : linha['volume_total'],
                "data_registro" : linha['data_registro']
            }
        }
    elif end_url == "new_production_products?":
        json_data = {
            "tabela": "TimberFleet_Produtos_producao",
            "dados": {
                "id_ident" : "_".join([linha['vehicle_name'], linha['equip_date']]),
                "prefixo" : linha['vehicle_name'].replace("VT-", ""),
                "data_producao" : converter_data(linha['equip_date']),
                "quantidade_toras" : linha['amount'],
                "volume_toras" : linha['volume'],
                "comprimento_minimo" : linha['min_length'],
                "comprimento_maximo" : linha['max_length'],
                "comprimento_medio" : float(linha['avg_length']),
                "data_registro" : linha['data_registro']
            }
        }

    return json_data

def enviar_para_php(json_data):
    dados = json_data.get("dados")

    if isinstance(dados, dict):
        dados = [dados]
    elif not isinstance(dados, list):
        print("Formato inesperado no campo 'dados':", json_data)
        return

    try:
        tabela = json_data.get("tabela")
        url_completa = f"{url_php}?tabela={tabela}"

        print(dados)

        resposta = requests.post(url_completa, headers=header_php, json=json_data)

        if resposta.status_code == 200:
            print(f"Dados enviados com sucesso para {tabela}")
            print(f"Resposta do php: {resposta.text}")
        else:
            print(f"Erro ao enviar dados para {tabela}: {resposta.status_code} - {resposta.text}")

    except Exception as e:
        print(f"Erro ao enviar dados para {tabela}: {e}")

if __name__ == "__main__":
    try:
        start = time.perf_counter()
        print("Iniciando o processo...")

        carregar_token()
        print("Token carregado com sucesso!")

        gerenciar_funcoes()

        print("Processo concluído!")
        end = time.perf_counter()
        print(f"Tempo de execução: {end - start:.2f} segundos")

        subprocess.run(r"Confidencial")
        sys.exit()

    except Exception as e:
        print(f"Erro durante execução: {e}")
        if "name 'token' is not defined" in str(e):
            print("Token não encontrado, criando um novo token...")
            criar_token()

        subprocess.run(r"Confidencial")
        sys.exit()