# -*- coding: utf-8 -*-
from google.colab import auth
from google.cloud import bigquery
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


# 1. AUTENTICAÇÃO E EXTRAÇÃO DOS DADOS

auth.authenticate_user()

project_id = 'projeto-transparencia-496822'
client = bigquery.Client(project=project_id)

query = """
SELECT
    data_despesa,
    estado,
    tipo_despesa,
    SUM(valor_gasto) AS total_gasto
FROM
    `projeto-transparencia-496822.dados_camara.gastos_consolidados`
GROUP BY
    data_despesa,
    estado,
    tipo_despesa
ORDER BY
    estado,
    tipo_despesa,
    data_despesa
"""

df_raw = client.query(query).to_dataframe()

df_raw["data_despesa"] = pd.to_datetime(df_raw["data_despesa"])


# 2. PREVISÃO POR ESTADO + TIPO DE DESPESA


resultado_final = []


grupos = (
    df_raw[["estado", "tipo_despesa"]]
    .drop_duplicates()
    .sort_values(["estado", "tipo_despesa"])
)

for _, grupo in grupos.iterrows():

    estado = grupo["estado"]
    tipo_despesa = grupo["tipo_despesa"]

    print(f"Processando: {estado} - {tipo_despesa}")

    df_grupo = df_raw[
        (df_raw["estado"] == estado) &
        (df_raw["tipo_despesa"] == tipo_despesa)
    ].copy()


    df_serie = (
        df_grupo
        .groupby(pd.Grouper(key="data_despesa", freq="MS"))["total_gasto"]
        .sum()
        .reset_index()
        .sort_values("data_despesa")
    )


    if len(df_serie) < 4:
        print("Histórico insuficiente.")
        continue


    df_fechado = df_serie.iloc[:-1].copy()

    if len(df_fechado) < 3:
        continue


    df_fechado["mes_num"] = np.arange(len(df_fechado))

    X = df_fechado[["mes_num"]]
    y = df_fechado["total_gasto"]


    modelo = LinearRegression()
    modelo.fit(X, y)

    ultima_data = df_fechado["data_despesa"].max()

    datas_futuras = pd.date_range(
        start=ultima_data + pd.DateOffset(months=1),
        periods=6,
        freq="MS"
    )

    proximos_meses = np.arange(
        len(df_fechado),
        len(df_fechado) + 6
    ).reshape(-1, 1)

    previsoes = modelo.predict(proximos_meses)


    piso = df_fechado["total_gasto"].min()

    resultado = pd.DataFrame({
        "estado": estado,
        "tipo_despesa": tipo_despesa,
        "data_despesa": datas_futuras,
        "valor_previsto": previsoes,
        "limite_minimo": previsoes * 0.90,
        "limite_maximo": previsoes * 1.10
    })

    for coluna in [
        "valor_previsto",
        "limite_minimo",
        "limite_maximo"
    ]:
        resultado[coluna] = resultado[coluna].clip(lower=piso)

    resultado_final.append(resultado)


resultado_futuro = pd.concat(resultado_final, ignore_index=True)


# 3. EXPORTAÇÃO PARA O BIGQUERY


dataset_destino = "dados_camara"
tabela_destino = "previsao_colab_python"

table_id = f"{project_id}.{dataset_destino}.{tabela_destino}"

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE"
)

job = client.load_table_from_dataframe(
    resultado_futuro,
    table_id,
    job_config=job_config
)

job.result()

print(f"\nTabela exportada com sucesso para:")
print(table_id)


# 4. VISUALIZAÇÃO


df_visualizacao = resultado_futuro.copy()

df_visualizacao["data_despesa"] = (
    df_visualizacao["data_despesa"]
    .dt.strftime("%Y-%m")
)

for coluna in [
    "valor_previsto",
    "limite_minimo",
    "limite_maximo"
]:
    df_visualizacao[coluna] = df_visualizacao[coluna].map(
        lambda x: f"R$ {x:,.2f}"
    )

print("\n=== PREVISÃO POR ESTADO E TIPO DE DESPESA ===")

display(
    df_visualizacao.sort_values(
        ["estado", "tipo_despesa", "data_despesa"]
    )
)

from google.cloud import bigquery

# 1. Define o nome do Dataset e da Tabela no seu BigQuery
dataset_destino = "dados_camara"
tabela_destino = "previsao_colab_python"

# Monta o caminho completo (ID do projeto . dataset . tabela)
table_id = f"{project_id}.{dataset_destino}.{tabela_destino}"

# 2. Configura o comportamento da carga
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE"
)

# 3. Envia o DataFrame do Pandas direto para o BigQuery
print(f"Enviando o DataFrame para o BigQuery em: {table_id}...")
job = client.load_table_from_dataframe(
    resultado_futuro,
    table_id,
    job_config=job_config
)

# 4. Aguarda a finalização do processo
job.result()
