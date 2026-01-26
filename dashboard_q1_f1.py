import streamlit as st
import pandas as pd
import time
import os
from pathlib import Path
from q1_fase1 import run_process_batch_mode, DEFAULT_API_URL
import json
from q1_fase2 import consolidar_e_enviar

# Configuração da Página
st.set_page_config(page_title="RSL Batch Processor Q1-F1", layout="wide", page_icon="🚀")

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
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        margin-bottom: 20px;
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Estado da Sessão
if 'logs_batch' not in st.session_state:
    st.session_state.logs_batch = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Sidebar de Configurações
st.sidebar.title("⚙️ Configurações")
api_url = st.sidebar.text_input("Endpoint do Langflow", value=DEFAULT_API_URL)
batch_size = st.sidebar.number_input("Tamanho do Batch", min_value=1, max_value=50, value=15)

# Verificação de arquivos unificados
input_folder = "./unificados/"
input_files = list(Path(input_folder).glob("*.json")) if Path(input_folder).exists() else []
total_files = len(input_files)

st.sidebar.markdown(f"**Total de arquivos unificados:** {total_files}")
if total_files == 0:
    st.sidebar.warning("Nenhum arquivo JSON encontrado em `./unificados/`")

# Verificação de resultados Fase 1
output_f1_folder = "./q1-f1/"
f1_files = list(Path(output_f1_folder).glob("batch*.json")) if Path(output_f1_folder).exists() else []
total_f1 = len(f1_files)
st.sidebar.markdown(f"**Batches processados (Fase 1):** {total_f1}")

# Interface Principal
st.title("🚀 RSL Batch Processor - Q1 Fase 1")
st.markdown("Revisão de Qualidade em Lote utilizando Langflow")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Arquivos", total_files)
with col2:
    st.metric("Batches Estimados", (total_files + batch_size - 1) // batch_size if total_files > 0 else 0)
with col3:
    st.metric("Status", "Parado" if not st.session_state.is_running else "Processando...")

col_btns_1, col_btns_2 = st.columns(2)
with col_btns_1:
    start_btn = st.button("▶️ Iniciar Fase 1 (Batch)", disabled=st.session_state.is_running or total_files == 0)

with col_btns_2:
    f2_btn = st.button("🏁 Gerar Consolidação Final (Fase 2)", disabled=st.session_state.is_running or total_f1 == 0)

# Componentes de Monitoramento
progress_bar = st.progress(0)
status_text = st.empty()
log_container = st.container()

def update_progress(current, total, batch_ids):
    pct = current / total
    progress_bar.progress(pct)
    msg = f"Processando Batch {current} de {total}... (Artigos: {batch_ids})"
    status_text.write(msg)
    
    # Adiciona ao log da sessão
    log_entry = {
        "Horário": time.strftime("%H:%M:%S"),
        "Batch": current,
        "IDs": str(batch_ids),
        "Status": "⏳ Processando"
    }
    st.session_state.logs_batch.insert(0, log_entry)

# Lógica de Execução
if start_btn:
    st.session_state.is_running = True
    st.session_state.logs_batch = []
    
    st.info("Iniciando o processamento pesado... Aguarde.")
    
    try:
        # Chama a função principal do script de processamento
        results = run_process_batch_mode(
            batch_size=batch_size, 
            api_url=api_url, 
            progress_callback=update_progress
        )
        
        st.session_state.is_running = False
        st.success("✅ Processamento em Batch finalizado com sucesso!")
        st.balloons()
        
    except Exception as e:
        st.session_state.is_running = False
        st.error(f"❌ Ocorreu um erro durante o processamento: {e}")

# Lógica Fase 2
if f2_btn:
    st.session_state.is_running = True
    status_text.info("Iniciando Consolidação Final...")
    def f2_callback(msg):
        with log_container:
            st.info(f"🔄 {msg}")
    
    try:
        success, msg = consolidar_e_enviar(progress_callback=f2_callback)
        st.session_state.is_running = False
        if success:
            st.success(msg)
            st.balloons()
        else:
            st.error(msg)
    except Exception as e:
        st.session_state.is_running = False
        st.error(f"❌ Erro na Fase 2: {e}")

# Exibição de Logs Real-time
with log_container:
    st.subheader("📋 Fluxo de Processamento")
    if st.session_state.logs_batch:
        df_logs = pd.DataFrame(st.session_state.logs_batch)
        st.table(df_logs)
    else:
        st.info("Aguardando início do processamento...")

# Aba de Visualização de Resultados
with st.expander("📂 Ver Arquivos Gerados em `./q1-f1/`"):
    output_folder = Path("./q1-f1/")
    if output_folder.exists():
        output_files = sorted(list(output_folder.glob("*.json")))
        if output_files:
            selected_file = st.selectbox("Selecione um batch para ver a resposta bruta:", [f.name for f in output_files])
            with open(output_folder / selected_file, 'r', encoding='utf-8') as f:
                st.json(json.load(f))
        else:
            st.write("Nenhum arquivo gerado ainda.")
    else:
        st.write("Pasta `./q1-f1/` não existe.")
