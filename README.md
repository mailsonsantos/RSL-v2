# 🚀 RSL-AI Governance Accelerator

O **RSL-AI Governance Accelerator** é um sistema avançado desenvolvido para acelerar e automatizar a etapa de **Avaliação de Qualidade (Quality Assessment - QA)** em Revisões Sistemáticas de Literatura (RSL). 

Este acelerador foi projetado para transformar o processo manual de análise de artigos acadêmicos em uma operação automatizada, auditável e escalável, utilizando o poder da Inteligência Artificial Generativa através do framework **Langflow**.

---

## 📋 Visão Geral do Sistema

O sistema opera em uma **Arquitetura Cliente-Servidor** otimizada para eficiência e baixo consumo de recursos no cliente:

*   **Servidor (Langflow)**: Camada de processamento pesado. Utiliza o componente **Docling** para extração de texto de PDFs e o modelo **GPT-4o-mini** da OpenAI para análise semântica.
*   **Cliente (Python Local)**: Camada de orquestração. Gerencia o envio dos arquivos, controle de lotes (batch processing), persistência local e interface de monitoramento.

---

## 🛠️ Artefatos Principais (Core)

Estes são os componentes essenciais para a execução do fluxo de análise:

### 🎮 Interface e Orquestração
*   **[dashboard.py](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/dashboard.py)**: Interface visual em Streamlit. Oferece monitoramento em tempo real, métricas de progresso, logs ao vivo e inspeção dos JSONs gerados.
*   **[rsl_paper_analyzer.py](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/rsl_paper_analyzer.py)**: Versão CLI (Command Line Interface) do motor de processamento. Ideal para execuções em segundo plano ou automações simples via terminal.

### 📂 Estrutura de Dados
*   **`arquivos_baixados/`**: Diretório de entrada (Input) onde devem ser depositados os artigos em formato PDF.
*   **`arquivos_processados/`**: Diretório de saída (Output) onde o sistema salva os resultados individuais em formato JSON.
*   **[.env](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/.env)**: Arquivo de configuração para chaves de API e URLs de endpoint.
*   **[requirements.txt](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/requirements.txt)**: Lista de dependências Python necessárias para rodar o cliente.

---

## ⚖️ Regras de Negócio e Critérios de Qualidade (QA)

A análise realizada pelo LLM segue **5 critérios fundamentais** definidos para o domínio de Governança de Dados para IA. Cada artigo é avaliado individualmente, gerando respostas estruturadas:

1.  **Framework de Governança**: Define claramente um framework ou modelo de governança de dados?
2.  **Ética e Regulação**: Aborda desafios éticos ou regulatórios da IA?
3.  **Rigor Metodológico**: A metodologia de pesquisa é adequada e reproduzível?
4.  **Validação de Resultados**: Houve validação por especialistas ou aplicação experimental?
5.  **Lacunas e Limitações**: Identifica limitações específicas na gestão de dados para IA?

> [!NOTE]
> Cada critério recebe uma classificação: **SIM**, **PARCIALMENTE** ou **NÃO**, acompanhada de uma justificativa concisa de até 5 linhas.

---

## ⚙️ Configuração e Instalação

1.  **Ambiente Virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Variáveis de Ambiente:** Configure seu `.env` com a `LANGFLOW_API_KEY`.

3.  **Dependência de Servidor:** O Langflow deve estar ativo e com o fluxo devidamente configurado (utilizando o componente `Docling` para leitura de arquivos).

---

## 🚀 Como Executar

O fluxo recomendado é através do Dashboard Visual:

```bash
streamlit run dashboard.py
```

No painel, você poderá ajustar o **Batch Size** (quantidade de arquivos processados simultaneamente) para otimizar o uso da CPU do servidor.

---

## 🛠️ Ferramentas de Apoio e Transformação

Estes arquivos **não fazem parte do fluxo principal de execução**, mas foram criados para apoiar a preparação dos dados, limpeza do ambiente e validações pontuais.

| Arquivo | Função |
| :--- | :--- |
| **[match_articles.py](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/match_articles.py)** | Cruza a lista oficial de artigos (`.xls`) com os arquivos físicos na pasta `artigos_baixados`, identificando faltas e sobras. |
| **[cleanup_artigos.py](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/cleanup_artigos.py)** | Utilitário para limpar a pasta de PDFs, mantendo apenas os arquivos validados em listas de controle. |
| **[teste.py](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/teste.py)** | Script de teste rápido para validar conexões e pequenos trechos de lógica. |
| **[erros.log](file:///home/mailson/Documentos/Doutorado/RSL_FINDER/erros.log)** | Arquivo gerado automaticamente para rastrear falhas de comunicação ou processamento durante a execução. |

### Ativos de Dados (Suporte)
*   **`articles.xls`**: Lista original de artigos exportada das bases de dados.
*   **`articles_preenchido_comQA.xlsx`**: Resultado consolidado (XLS) após o cruzamento de dados.
*   **`artigos_nao_listados.txt`**: Relatório de arquivos PDF encontrados que não constam na lista oficial.

---
*Este projeto integra a pesquisa de doutorado focada em Governança de Dados aplicada à Inteligência Artificial.*

