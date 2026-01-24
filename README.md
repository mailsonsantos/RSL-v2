# 🚀 RSL-AI Governance Accelerator

O **RSL-AI Governance Accelerator** é um sistema avançado desenvolvido para acelerar e automatizar a etapa de **Avaliação de Qualidade (Quality Assessment - QA)** em Revisões Sistemáticas de Literatura (RSL). 

Este acelerador foi projetado especificamente para lidar com o volume massivo de dados acadêmicos (neste caso, **370 artigos**) sobre a temática de **Governança de Dados para Sistemas de IA**, transformando um processo que levaria semanas de esforço manual em uma operação automatizada, auditável e rápida.

---

## 📋 Visão Geral

O sistema utiliza uma **Arquitetura Cliente-Servidor** para garantir eficiência em hardware modesto (ex: Beelink):

*   **Servidor (Langflow)**: Responsável pelas tarefas pesadas de extração de texto (via **Docling**), orquestração de fluxos de IA e interface com o LLM (**GPT-4o-mini** da OpenAI).
*   **Cliente (Python Scripts/Dashboard)**: Atua apenas como orquestrador leve de chamadas de API, monitoramento e persistência de resultados.

### Pilares do Projeto:
*   **Automação Inteligente**: Extração de texto via servidor e análise semântica estruturada.
*   **Escalabilidade**: Processamento em lote (Batch Processing) para otimização de recursos.
*   **Monitoramento em Tempo Real**: Interface Streamlit para acompanhamento do progresso.

---

## 🛠️ Processo de Instalação

### Requisitos Prévios
*   **Python 3.10+** (Ambiente Cliente leve).
*   **Langflow** rodando em um servidor/local (deve ter o componente **Docling** instalado internamente).
*   Chave de API da OpenAI configurada no Langflow.

### Passo a Passo

1. **Clonar o repositório e criar ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. **Instalar dependências do cliente:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuração do Langflow (Servidor):**
   > [!IMPORTANT]
   > O Langflow deve estar rodando com o componente `Docling` configurado. A extração de PDF ocorre no servidor, não no cliente Python. Certifique-se de que o componente ID no script corresponde ao do seu flow (ex: `DoclingInline-jzcAF`).

---

## ⚙️ Processo de Configuração

### 1. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com a seguinte chave:
```env
LANGFLOW_API_KEY=your_api_key_here
```

### 2. Integração com Langflow
O sistema se comunica com o endpoint local do Langflow. Verifique no script `rsl_paper_analyzer.py` ou `dashboard.py` se a constante `API_URL` aponta para o ID correto do seu fluxo carregado no Langflow (ex: `http://localhost:7860/api/v1/run/...`).

### 3. Estrutura de Pastas
O projeto espera a seguinte organização de arquivos:
*   `arquivos_baixados/`: Pasta contendo os PDFs originais do levantamento (Input).
*   `arquivos_processados/`: Pasta onde serão salvos os JSONs gerados após a análise (Output).

---

## 🚀 Processo de Execução

### Modo 1: Dashboard de Monitoramento (Recomendado)
Para uma experiência visual com métricas, logs e inspeção de resultados:
```bash
streamlit run dashboard.py
```
**Fluxo no Dashboard:**
1. Verifique se o Langflow está ativo.
2. Defina o **Batch Size** (Lote) na barra lateral (Padrão: 3).
3. Clique em `Iniciar Processamento`.
4. Monitore o progresso, tempo decorrido e eventuais falhas.

### Modo 2: Script de Automação (CLI)
Para execução direta via terminal:
```bash
python rsl_paper_analyzer.py
```

---

## ⚖️ Regras de Negócio (Critérios de Qualidade)

A inteligência do acelerador avalia cada artigo com base em **5 critérios fundamentais** de governança e rigor metodológico. O LLM deve responder obrigatoriamente para cada item: **SIM**, **PARCIALMENTE** ou **NÃO**.

1.  **Framework de Governança**: O estudo define claramente um framework ou modelo de governança de dados?
2.  **Ética e Regulação**: Aborda explicitamente desafios éticos ou regulatórios da IA?
3.  **Rigor Metodológico**: A metodologia de pesquisa está descrita de forma adequada e reproduzível?
4.  **Validação de Resultados**: Houve validação por especialistas ou aplicação em ambiente real/experimental?
5.  **Lacunas e Limitações**: O artigo identifica limitações ou lacunas específicas na gestão de dados para IA?

> [!IMPORTANT]
> **Regra de Processamento em Lote**: Devido às restrições de CPU (foco em máquinas locais tipo Beelink), o sistema processa os artigos em lotes de 3. Isso garante estabilidade e evita gargalos na conversão de PDF via Docling.

---

## 📄 Formato de Saída

Cada artigo processado gera um arquivo `.json` enriquecido. Abaixo um exemplo da estrutura gerada:

```json
{
    "criterio_1": "SIM",
    "criterio_2": "PARCIALMENTE",
    "criterio_3": "SIM",
    "criterio_4": "NÂO",
    "criterio_5": "SIM",
    "justificativa": "O artigo apresenta um modelo robusto, mas falha em detalhar a fase de validação experimental.",
    "file_source": "/caminho/completo/do/arquivo/artigo_01.pdf"
}
```

*   **justificativa**: Limitada a no máximo 5 linhas para manter a concisão.
*   **file_source**: Chave inserida via script para rastreabilidade total da fonte original.

---
*Desenvolvido como parte de pesquisa de doutorado em Governança de Dados aplicada à Inteligência Artificial.*
