#  Transparência Preditiva: Gastos Parlamentares (SC x PR)

> Pipeline de dados *End-to-End* para extração, automação em nuvem, modelagem preditiva de séries temporais e visualização de gastos públicos dos estados de Santa Catarina e Paraná.

---

##  Links Úteis
*  [Acessar Dashboard Interativo no Looker Studio] https://datastudio.google.com/reporting/31a35358-376c-4afa-89d6-4e634918434c
*  [Post de Apresentação no LinkedIn](SEU_LINK_AQUI)

---

##  Arquitetura do Projeto


1. **Ingestão Serverless:** Script Python (`src/main.py`) responsável por coletar os dados brutos e carregar no BigQuery.
2. **Infraestrutura como Código (IaC):** Recursos provisionados via Terraform (`terraform/main.tf`), incluindo Cloud Function e políticas de acesso na GCP.
3. **Data Warehouse (SQL):** Criação de VIEWs no BigQuery para unificar o histórico consolidado e as projeções futuras.
4. **Machine Learning:** Modelo preditivo de Séries Temporais para projetar o comportamento dos gastos nos próximos meses.
5. **Data Visualization:** Dashboard executivo construído no Looker Studio (Dark Mode).

---

##  Principais Insights do Painel
* **Tendência de Variação:** Identificação da variação média esperada entre o histórico e a projeção futura.
* **Análise Comparativa:** Leitura lado a lado das despesas de Santa Catarina e Paraná.
* **Gráfico Heroico:** Acompanhamento contínuo da linha temporal real integrada à projeção futura com margem de incerteza (limites mínimo e máximo).

---

##  Tecnologias Utilizadas
* **Linguagens:** Python, SQL, HCL (Terraform)
* **Cloud Platform:** Google Cloud Platform (Cloud Functions, BigQuery, Cloud Storage)
* **Infraestrutura:** Terraform
* **BI & Visualização:** Looker Studio

---

## 👤 Autor
Desenvolvido por **Luiz Wolfgang Stoeberl**  
📫 Entre em contato: [LinkedIn] www.linkedin.com/in/luiz-wolfgang-stoeberl-aa56aa261 | [E-mail] luizstoeberl21@gmail.com