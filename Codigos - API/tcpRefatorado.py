import time
import re
import xmltodict

usuario = "Confidencial"
senha = "Confidencial"
caminho = r"C:\Users\LUIS.BRANCO\TCP"

wsdl_url = {
    #"ConsultaPublica" : "Confidencial",
    "MovimentacaoExpo" : "Confidencial"  
    #"MovimentacaoImpo" : "Confidencial"
}

def Gerenciador():
    try:
        print("Iniciando o gerenciador...")
        for nome, link in wsdl_url.items():
            print(f"Processando {nome} com WSDL: {link}")
            Buscar_Dados(nome, link)
            print(f"Processamento de {nome} concluído.")

        print("Gerenciador iniciado com sucesso!")
    except Exception as e:
        print(f"Erro no gerenciador: {e}")

def Buscar_Dados(nome, link):
    soap_action = _definir_SoapAction(nome)
    print("Ação definida:", soap_action)

    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "soapAction": soap_action
    }

    expo_linhas = []

def _pick(d, key):
    return d.get(key) or d.get(f"wsc:{key}")

def _empilha_mov(xml_texto, nome, tipo_operacao=None):
    expo_linhas = []
    impo_linhas = []

    movs = Transpor_Xml(xml_texto)

    for mov in movs:
        if not isinstance(mov, dict):
            continue

        if nome == "MovimentacaoExpo":
            base = mov.copy()
            nfs = None

            nfs_node = _pick(base, 'NotasFiscais')
            if isinstance(nfs_node, dict):
                nfs = _pick(nfs_node, 'NotaFiscal')

            for k in ("NotasFiscais", "wsc:NotasFiscais"):
                if k in base:
                    base.pop(k, None)
            
            base_desaninhada = _desaninhar(base)

            if isinstance(nfs, list):
                for nf in nfs:
                    nf_desaninhado = _desaninhar(nf) if isinstance(nf, dict) else {}
                    linha = base_desaninhada.copy()
                    linha["NF_Numero"] = nf_desaninhado.get("Numero") or nf_desaninhado.get("wsc:Numero")
                    linha["NF_Serie"] = nf_desaninhado.get("Serie") or nf_desaninhado.get("wsc:Serie")
                    linha["NF_NCM"] = nf_desaninhado.get("NCM") or nf_desaninhado.get("wsc:NCM")
                    expo_linhas.append(linha)
                
            elif isinstance(nfs, dict):
                nf_desaninhado = _desaninhar(nfs)
                linha = base_desaninhada.copy()
                linha["NF_Numero"] = nf_desaninhado.get("Numero") or nf_desaninhado.get("wsc:Numero")
                linha["NF_Serie"] = nf_desaninhado.get("Serie") or nf_desaninhado.get("wsc:Serie")
                linha["NF_NCM"] = nf_desaninhado.get("NCM") or nf_desaninhado.get("wsc:NCM")
                expo_linhas.append(linha)

            else:
                linha = base_desaninhada.copy()
                linha["NF_Numero"] = None
                linha["NF_Serie"] = None
                linha["NF_NCM"] = None
                expo_linhas.append(linha)
            
        else:
            base = mov.copy()
            blocos = ("BL", "Conteineres", "Armazem", "Faturamentos")

            nfs_node = _pick(base, 'NotasFiscais')
            if isinstance(nfs_node, dict):
                nfs = _pick(nfs_node, 'NotaFiscal')

            for k in ("NotasFiscais", "wsc:NotasFiscais"):
                if k in base:
                    base.pop(k, None)

            base_desaninhada = _desaninhar(base)
            if tipo_operacao is not None:
                if tipo_operacao == 1:
                    base_desaninhada['TipoOperacao'] = 'Importação'
                elif tipo_operacao == 2:
                    base_desaninhada['TipoOperacao'] = 'Importação Full'
                elif tipo_operacao == 3:
                    base_desaninhada['TipoOperacao'] = 'Carga Solta'
                elif tipo_operacao == 4:
                    base_desaninhada['TipoOperacao'] = 'Cross Docking'


def _desaninhar(d, parent_key='', sep='.'):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(k, str) and k.startswith('@'):
                continue
            key_clean = k.split(':', 1)[-1] if isinstance(k, str) else k
            new_key = f"{parent_key}{sep}{key_clean}" if parent_key else key_clean
            items.extend(_desaninhar(v, new_key, sep=sep).items())
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(_desaninhar(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)

def Transpor_Xml(xml_texto):
    xml_texto = xml_texto.lstrip('\ufeff').lstrip()

    ini = xml_texto.find('<soapenv:Envelope')
    fim = xml_texto.find('</soapenv:Envelope>')
    if ini != -1 and fim != -1:
        xml_texto = xml_texto[ini:fim + len('</soapenv:Envelope>')]

    xml_texto = re.sub(r'<([A-Za-z0-9]+):[^:>\s]+:([^>\s/]+)>', r'<\1:\2>', xml_texto)
    xml_texto = re.sub(r'</([A-Za-z0-9]+):[^:>\s]+:([^>\s/]+)>', r'</\1:\2>', xml_texto)

    parsed = xmltodict.parse(xml_texto, process_namespaces=False)

    envelope = _encontrar_sufixo(parsed, 'Envelope') or parsed
    body = _encontrar_sufixo(envelope, 'Body') or envelope
    resposta = None

    movs = _encontrar_sufixo(resposta, 'Movimentacao')
    if not movs:
        return []
    if isinstance(movs, dict):
        movs = [movs]
    return movs

def _encontrar_sufixo(d, sufixo):
    for k, v in d.items():
        if isinstance(k, str) and k.endswith(sufixo):
            return v
    return {}

def _definir_SoapAction(nome):
    if nome == "ConsultaPublica":
        return "ConsultaNavio"
    elif nome == "MovimentacaoExpo" or nome == "MovimentacaoImpo":
        return "ConsultarMovimentacao"
    else:
        raise ValueError(f"Ação SOAP não definida para {nome}")

if __name__ == "__main__":
    tempo_inicial = time.perf_counter()
    try:
        print("Iniciando o script...")
        Gerenciador()
        print("Script executado com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    tempo_final = time.time()
    tempo_total = tempo_final - tempo_inicial
    print(f"Tempo total de execução: {tempo_total:.2f} segundos")