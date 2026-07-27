import requests
import time
import os
from datetime import datetime
from google.cloud import bigquery

def main(request):

    # 1. PEGA O ESTADO DA URL DO NAVEGADOR (Se não passar nada, o padrão é SC)
    estado = request.args.get('estado', 'SC')
    
    print(f"===== PROCESSANDO ESTADO: {estado} =====")

    client = bigquery.Client()

    project_id = os.environ.get("PROJECT_ID", "projeto-transparencia-496822")
    dataset_id = os.environ.get("DATASET_ID", "dados_camara")
    table_id = os.environ.get("TABLE_ID", "raw_gastos")

    tabela = f"{project_id}.{dataset_id}.{table_id}"

    ano = datetime.now().year

    todos_deputados = []
    pagina = 1

    # ==========================================
    # Busca deputados do estado escolhido dinamicamente
    # ==========================================
    while True:
        # Passamos a variável {estado} que veio da sua URL
        url = (
            "https://dadosabertos.camara.leg.br/api/v2/deputados"
            f"?siglaUf={estado}&itens=100&pagina={pagina}"
        )

        resposta = requests.get(url)

        if resposta.status_code != 200:
            return f"Erro ao consultar deputados: {resposta.status_code}", 500

        dados = resposta.json()["dados"]

        if len(dados) == 0:
            break

        todos_deputados.extend(dados)
        pagina += 1

    print(f"TOTAL DEPUTADOS FILTRADOS EM {estado}: {len(todos_deputados)}")

    linhas = []

    # ==========================
    # Busca despesas
    # ==========================
    for deputado in todos_deputados:

        id_dep = deputado["id"]
        nome_dep = deputado["nome"]

        pagina = 1

        while True:
            url_despesas = (
                f"https://dadosabertos.camara.leg.br/api/v2/"
                f"deputados/{id_dep}/despesas?"
                f"ano={ano}&itens=100&pagina={pagina}"
            )

            resposta = requests.get(url_despesas)

            if resposta.status_code != 200:
                break

            despesas = resposta.json()["dados"]

            if len(despesas) == 0:
                break

            for despesa in despesas:
                linhas.append({
                    "id_registro": int(
                        f"{id_dep}{despesa.get('mes', 0)}"
                    ),
                    "id_deputado": id_dep,
                    "nome_deputado": nome_dep,
                    "estado": estado,
                    "ano": ano,
                    "mes": despesa.get("mes"),
                    "tipo_despesa": despesa.get("tipoDespesa"),
                    "valor": float(
                        despesa.get("valorDocumento", 0)
                    )
                })

            pagina += 1
            time.sleep(0.2)

        print(f"{nome_dep} concluído")

    # ==========================
    # Insere no BigQuery
    # ==========================
    if len(linhas) > 0:
        erros = client.insert_rows_json(
            tabela,
            linhas
        )

        if erros:
            return f"Erro ao inserir dados no BigQuery: {erros}", 500
        
        return f"{len(linhas)} registros inseridos com sucesso do estado {estado}.", 200
    else:
        return f"Nenhum registro de despesa encontrado para o estado {estado}.", 200