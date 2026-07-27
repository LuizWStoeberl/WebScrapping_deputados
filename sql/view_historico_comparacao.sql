CREATE OR REPLACE VIEW `projeto-transparencia-496822.dados_camara.vw_grafico_comparativo` AS

SELECT '1. Junho (Atual Real)' AS mes, estado, SUM(valor_gasto) AS total 
FROM `projeto-transparencia-496822.dados_camara.gastos_consolidados`
WHERE data_despesa >= '2026-06-01' AND data_despesa < '2026-07-01'
GROUP BY estado

UNION ALL

SELECT '2. Julho (Previsto)' AS mes, estado, SUM(valor_previsto) AS total 
FROM `projeto-transparencia-496822.dados_camara.previsao_colab_python`
WHERE data_despesa >= '2026-07-01' AND data_despesa < '2026-08-01'
GROUP BY estado;