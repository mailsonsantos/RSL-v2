# 🚀 RSL-AI Governance Accelerator

O **RSL-AI Governance Accelerator** é um sistema avançado desenvolvido para acelerar e automatizar as etapas de **Avaliação de Qualidade (Quality Assessment - QA)** e **Resumo Automático (Automatic Summarization)** em Revisões Sistemáticas de Literatura (RSL). 

Este acelerador foi projetado para transformar o processo manual de análise de artigos acadêmicos em uma operação automatizada, auditável e escalável, utilizando o poder da Inteligência Artificial Generativa através do framework **Langflow**.

---

## 📋 Visão Geral do Sistema

O sistema opera em uma **Arquitetura Cliente-Servidor** otimizada para eficiência e baixo consumo de recursos no cliente:

*   **Servidor (Langflow)**: Camada de processamento pesado. Utiliza o componente **Docling** para extração de texto de PDFs e modelos como **GPT-4o-mini** ou outros configurados no Langflow para análise semântica e resumo.
*   **Cliente (Python Local)**: Camada de orquestração. Gerencia o envio dos arquivos, controle de lotes (batch processing), persistência local e interface de monitoramento via Streamlit.

---

## 🛠️ Artefatos Principais (Core)

O sistema é dividido em dois fluxos principais:

### 1. Fluxo de Análise (QA)
*   **[dashboard.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/dashboard.py)**: Interface visual em Streamlit para monitoramento da análise de QA.
*   **[rsl_paper_analyzer.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/rsl_paper_analyzer.py)**: CLI para execução da análise de QA em segundo plano.

### 2. Fluxo de Resumo (Resumer) [NOVO]
*   **[dashboard_resumer.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/dashboard_resumer.py)**: Interface visual dedicada ao monitoramento do processo de resumo dos artigos.
*   **[rsl_paper_resumer.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/rsl_paper_resumer.py)**: CLI para geração de resumos em lote via terminal.

### 📂 Estrutura de Pastas e Dados
*   **`artigos_baixados/`**: Diretório de entrada onde devem ser depositados os artigos PDF.
*   **`arquivos_processados/`**: Resultados da análise de QA (JSON).
*   **`resumos/`**: Resultados do processo de resumo automático (JSON).
*   **[.env](file:///Users/mailsonsantos/Documents/git/RSL-v2/.env)**: Chaves de API e URLs de endpoint.
*   **[requirements.txt](file:///Users/mailsonsantos/Documents/git/RSL-v2/requirements.txt)**: Dependências Python do cliente.

---

## ⚖️ Critérios de Análise e Resumo

### Avaliação de Qualidade (QA)
A análise segue critérios fundamentais de Governança de Dados para IA, classificando cada artigo como **SIM**, **PARCIALMENTE** ou **NÃO** em dimensões como Framework de Governança, Ética, Rigor Metodológico e Validação.

### Resumo Automático
O fluxo de resumo processa o texto completo extraído pelo Docling para gerar resumos executivos focados nos pontos chave da pesquisa, facilitando a triagem e leitura rápida.

---

## ⚙️ Configuração e Instalação

1.  **Ambiente Virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Variáveis de Ambiente:** Configure seu `.env` com a `LANGFLOW_API_KEY`.

3.  **Dependência de Servidor:** O Langflow deve estar ativo com os fluxos configurados nos endpoints especificados nos scripts.

---

## 🚀 Como Executar

### Para Análise de QA:
```bash
streamlit run dashboard.py
# OU via CLI
python rsl_paper_analyzer.py
```

### Para Resumo de Artigos:
```bash
streamlit run dashboard_resumer.py
# OU via CLI
python rsl_paper_resumer.py
```

---

## 🛠️ Ferramentas de Apoio

| Arquivo | Função |
| :--- | :--- |
| **[cleanup_approved.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/cleanup_approved.py)** | Filtra a pasta de entrada mantendo apenas artigos aprovados. |
| **[match_articles.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/match_articles.py)** | Cruza lista oficial com arquivos físicos. |
| **[cleanup_artigos.py](file:///Users/mailsonsantos/Documents/git/RSL-v2/cleanup_artigos.py)** | Utilitário de limpeza de pastas de PDFs. |
| **[erros.log](file:///Users/mailsonsantos/Documents/git/RSL-v2/erros.log)** | Logs do motor de análise. |
| **[erros_resumo.log](file:///Users/mailsonsantos/Documents/git/RSL-v2/erros_resumo.log)** | Logs do motor de resumo. |

---
*Este projeto integra a pesquisa de doutorado focada em Governança de Dados aplicada à Inteligência Artificial.*

