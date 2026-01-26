import streamlit as st
import pandas as pd
import time
import os
import json
from pathlib import Path
from q3_fase1 import run_process_batch_mode_q3, DEFAULT_API_URL

# Configuração da Página
st.set_page_config(page_title="RSL Processor Q3-F1: Questão 3", layout="wide", page_icon="📊")

# CSS personalizado para estética premium
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        border-color: #FF4B4B;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        margin-bottom: 20px;
        border-left: 5px solid #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# Estado da Sessão
if 'logs_batch_q3' not in st.session_state:
    st.session_state.logs_batch_q3 = []
if 'is_running_q3' not in st.session_state:
    st.session_state.is_running_q3 = False

# Sidebar de Configurações
st.sidebar.title("⚙️ Configurações Q3")
st.sidebar.markdown("Questão 3: Análise em Batch")
api_url = st.sidebar.text_input("Endpoint do Langflow (Q3)", value=DEFAULT_API_URL)
batch_size = st.sidebar.number_input("Tamanho do Batch", min_value=1, max_value=50, value=15)

# Verificação de arquivos unificados
input_folder = "./unificados/"
input_files = list(Path(input_folder).glob("*.json")) if Path(input_folder).exists() else []
total_files = len(input_files)

st.sidebar.markdown(f"**Total de arquivos unificados:** {total_files}")
if total_files == 0:
    st.sidebar.warning("Nenhum arquivo JSON encontrado em `./unificados/`")

# Verificação de resultados Fase 1 Q3
output_f1_folder = "./q3-f1/"
f1_files = list(Path(output_f1_folder).glob("batch*.json")) if Path(output_f1_folder).exists() else []
total_f1 = len(f1_files)
st.sidebar.markdown(f"**Batches processados (Q3-F1):** {total_f1}")

# Interface Principal
st.title("📊 RSL Batch Processor - Q3 Fase 1")
st.markdown("Análise da **Questão 3** em Lote utilizando Langflow")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Arquivos", total_files)
with col2:
    st.metric("Batches Estimados", (total_files + batch_size - 1) // batch_size if total_files > 0 else 0)
with col3:
    st.metric("Status", "Parado" if not st.session_state.is_running_q3 else "Processando...")

start_btn = st.button("▶️ Executar Q3 - Fase 1", disabled=st.session_state.is_running_q3 or total_files == 0)

# Componentes de Monitoramento
progress_bar = st.progress(0)
status_text = st.empty()
log_container = st.container()

def update_progress(current, total, batch_ids):
    pct = current / total
    progress_bar.progress(pct)
    msg = f"Processando Batch {current} de {total}... (IDs: {batch_ids})"
    status_text.info(msg)
    
    # Adiciona ao log da sessão
    log_entry = {
        "Horário": time.strftime("%H:%M:%S"),
        "Batch": current,
        "IDs": str(batch_ids),
        "Status": "⏳ Processando"
    }
    st.session_state.logs_batch_q3.insert(0, log_entry)

# Lógica de Execução
if start_btn:
    st.session_state.is_running_q3 = True
    st.session_state.logs_batch_q3 = []
    
    st.info("Iniciando o processamento Q3... Aguarde.")
    
    try:
        # Chama a função principal do script de processamento
        results = run_process_batch_mode_q3(
            batch_size=batch_size, 
            api_url=api_url, 
            progress_callback=update_progress
        )
        
        st.session_state.is_running_q3 = False
        
        # Verifica se houve erro em algum batch
        has_error = any(res["status"] == "error" for res in results) if results else False
        
        if results and not has_error:
            st.success("✅ Processamento Q3 - Fase 1 finalizado com sucesso!")
            st.balloons()
        elif has_error:
            st.error("❌ O processamento foi interrompido devido a um erro na API.")
        else:
            st.warning("Nenhum arquivo processado.")
        
    except Exception as e:
        st.session_state.is_running_q3 = False
        st.error(f"❌ Ocorreu um erro inesperado: {e}")

# Exibição de Logs Real-time
with log_container:
    st.subheader("📋 Fluxo de Processamento Q3")
    if st.session_state.logs_batch_q3:
        df_logs = pd.DataFrame(st.session_state.logs_batch_q3)
        st.table(df_logs)
    else:
        st.info("Aguardando início do processamento...")

# Aba de Visualização de Resultados
with st.expander("📂 Ver Arquivos Gerados em `./q3-f1/`"):
    output_folder = Path("./q3-f1/")
    if output_folder.exists():
        output_files = sorted(list(output_folder.glob("*.json")), key=lambda x: int(x.stem.replace('batch', '')) if x.stem.replace('batch', '').isdigit() else 0)
        if output_files:
            selected_file = st.selectbox("Selecione um batch para ver a resposta bruta:", [f.name for f in output_files])
            with open(output_folder / selected_file, 'r', encoding='utf-8') as f:
                st.json(json.load(f))
        else:
            st.write("Nenhum arquivo gerado ainda.")
    else:
        st.write("Pasta `./q3-f1/` não existe.")
