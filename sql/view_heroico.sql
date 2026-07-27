CREATE OR REPLACE VIEW `projeto-transparencia-496822.dados_camara.vw_heroico_previsao` AS

-- 1. Dados Reais Históricos (até Junho/2026)
SELECT 
  DATE(data_despesa) AS data_despesa,
  SUM(valor_gasto) AS valor_real,
  CAST(NULL AS FLOAT64) AS valor_previsto,
  CAST(NULL AS FLOAT64) AS limite_minimo,
  CAST(NULL AS FLOAT64) AS limite_maximo
FROM 
  `projeto-transparencia-496822.dados_camara.gastos_consolidados`
WHERE 
  estado IN ('SC', 'PR')
GROUP BY 
  data_despesa

UNION ALL

-- 2. Dados de Previsão Futura (Julho em diante)
SELECT 
  DATE(data_despesa) AS data_despesa,
  CAST(NULL AS FLOAT64) AS valor_real,
  SUM(valor_previsto) AS valor_previsto,
  SUM(limite_minimo) AS limite_minimo,
  SUM(limite_maximo) AS limite_maximo
FROM 
  `projeto-transparencia-496822.dados_camara.previsao_colab_python`
GROUP BY 
  data_despesa;