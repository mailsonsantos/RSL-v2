import streamlit as st
import requests
import json
import re
import uuid
import time
import pandas as pd
import concurrent.futures
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

# Configuração de Logging para Terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Load environment variables
load_dotenv()

# --- Configurações Iniciais ---
st.set_page_config(page_title="RSL Finder Monitor", layout="wide", page_icon="🚀")

# CSS customizado para melhorar a estética
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    /* Estilo para garantir visibilidade das métricas em qualquer tema */
    [data-testid="stMetricValue"] {
        font-weight: bold;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Estado da Sessão ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'processed_count' not in st.session_state:
    st.session_state.processed_count = 0
if 'failed_count' not in st.session_state:
    st.session_state.failed_count = 0
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Constantes do Langflow ---
API_URL = os.getenv("LANGFLOW_API_URL", "http://localhost:7860/api/v1/run/cab4734e-9d31-4c61-89f9-3315a939185a")
COMPONENT_ID = "DoclingInline-jzcAF"
API_KEY = os.getenv("LANGFLOW_API_KEY")

# --- Funções Auxiliares ---
def sanitize_filename(filename):
    name = Path(filename).stem
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return f"{name}.json"

def check_langflow_connectivity(url):
    """Verifica se o servidor Langflow está respondendo."""
    try:
        # Tenta um GET simples no host ou uma requisição curta
        base_url = "/".join(url.split("/")[:3])
        response = requests.get(base_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def process_file_logic(file_path, output_folder, api_key):
    file_name = Path(file_path).name
    logging.info(f"🚀 Iniciando processamento: {file_name}")
    
    abs_path = str(Path(file_path).resolve())
    headers = {"x-api-key": api_key}
    payload = {
        "output_type": "text",
        "input_type": "text",
        "input_value": "Iniciando análise",
        "session_id": str(uuid.uuid4()),
        "tweaks": {COMPONENT_ID: {"path": abs_path}}
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        response.raise_for_status()
        
        result_data = response.json()
        if not result_data:
            raise ValueError("Resposta da API vazia")
            
        try:
            output_text = result_data['outputs'][0]['outputs'][0]['results']['message']['text']
            processed_dict = json.loads(output_text) if isinstance(output_text, str) else output_text
        except (KeyError, IndexError, json.JSONDecodeError, TypeError) as e:
            logging.warning(f"⚠️ Estrutura JSON inesperada para {file_name}: {str(e)}")
            processed_dict = result_data
            
        if isinstance(processed_dict, dict):
            processed_dict["file_source"] = abs_path
        
        output_filename = sanitize_filename(file_path)
        output_path = Path(output_folder) / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_dict, f, ensure_ascii=False, indent=4)
            
        logging.info(f"✅ Sucesso: {file_name}")
        return {"file": file_name, "status": "✅ Sucesso", "time": time.strftime("%H:%M:%S")}
    
    except requests.exceptions.Timeout:
        error_msg = "Timeout na API (Docling pode estar demorando)"
        logging.error(f"❌ Erro em {file_name}: {error_msg}")
        return {"file": file_name, "status": "❌ Erro", "error": error_msg, "time": time.strftime("%H:%M:%S")}
    except Exception as e:
        error_msg = str(e)
        logging.error(f"❌ Erro em {file_name}: {error_msg}")
        with open("erros.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR - {file_path}: {error_msg}\n")
        return {"file": file_name, "status": "❌ Erro", "error": error_msg, "time": time.strftime("%H:%M:%S")}

# --- Sidebar ---
st.sidebar.title("🛠️ Painel de Controle")
batch_size = st.sidebar.number_input("BATCH_SIZE (Simultâneos)", min_value=1, max_value=10, value=3)
# Ajustado para o nome real da pasta encontrada no sistema
input_folder_val = st.sidebar.text_input("Pasta de Entrada (PDFs)", value="artigos_baixados")
output_folder_val = st.sidebar.text_input("Pasta de Saída (JSONs)", value="arquivos_processados")

input_folder_path = Path(input_folder_val).resolve()
output_folder_path = Path(output_folder_val).resolve()

# Validação imediata na UI
if not input_folder_path.exists():
    st.sidebar.error(f"❌ Pasta '{input_folder_val}' não encontrada!")
    total_files_list = []
else:
    total_files_list = list(input_folder_path.glob("*.pdf"))
    if not total_files_list:
        st.sidebar.warning(f"⚠️ Nenhum PDF encontrado em '{input_folder_val}'")

total_files = len(total_files_list)

if not API_KEY:
    st.error("⚠️ API_KEY não encontrada no .env")

start_btn = st.sidebar.button("🚀 Iniciar Processamento", 
                              disabled=st.session_state.is_processing or not API_KEY or total_files == 0)

# --- Cabeçalho ---
st.title("📚 Monitor de Revisão Sistemática (RSL)")

# --- Métricas com Placeholders para Reatividade ---
metric_cols = st.columns(5)
m1 = metric_cols[0].empty()
m2 = metric_cols[1].empty()
m3 = metric_cols[2].empty()
m4 = metric_cols[3].empty()
m5 = metric_cols[4].empty()

def update_metrics():
    processed = st.session_state.processed_count + st.session_state.failed_count
    remaining = total_files - processed
    
    m1.metric("Total", total_files)
    m2.metric("Processados", processed)
    m3.metric("Restantes", max(0, remaining))
    m4.metric("Sucesso", st.session_state.processed_count)
    m5.metric("Falhas", st.session_state.failed_count)
    
    completion_pct = processed / total_files if total_files > 0 else 0
    return completion_pct

def get_eta_string(elapsed, processed_count, remaining_count):
    if processed_count == 0:
        return "--:--:--"
    avg_time = elapsed / processed_count
    eta_seconds = avg_time * remaining_count
    return time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

completion_pct = update_metrics()
progress_info = st.empty()
progress_bar = st.progress(completion_pct)
status_text = st.empty()

def update_ui():
    pct = update_metrics()
    processed = st.session_state.processed_count + st.session_state.failed_count
    remaining = total_files - processed
    
    progress_info.markdown(f"**Processando arquivo {min(processed + 1, total_files)} de {total_files}...**")
    progress_bar.progress(pct)
    
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        eta_str = get_eta_string(elapsed, processed, remaining)
        status_text.write(f"⏱️ Tempo Decorrido: {time.strftime('%H:%M:%S', time.gmtime(elapsed))} | ⏳ ETA: {eta_str}")

update_ui()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Monitoramento", "🔍 Inspeção", "⚠️ Erros"])

with tab1:
    st.subheader("Logs em Tempo Real")
    log_container = st.empty()
    if st.session_state.logs:
        log_container.table(pd.DataFrame(st.session_state.logs))

with tab2:
    st.subheader("Inspecionar JSONs Gerados")
    if output_folder_path.exists():
        json_files = list(output_folder_path.glob("*.json"))
        if json_files:
            selected_json = st.selectbox("Selecione um arquivo", options=[f.name for f in json_files])
            if selected_json:
                with open(output_folder_path / selected_json, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    st.json(content)
        else:
            st.info("Nenhum arquivo JSON processado ainda.")
    else:
        st.info("Pasta de saída ainda não existe.")

with tab3:
    st.subheader("Histórico de Erros")
    if Path("erros.log").exists():
        with open("erros.log", "r", encoding="utf-8") as f:
            errors = f.readlines()
            if errors:
                for err in reversed(errors):
                    st.text(err.strip())
            else:
                st.success("Nenhum erro registrado.")
    else:
        st.success("Arquivo de log de erros não encontrado.")

# --- Lógica de Processamento ---
if start_btn:
    # 1. Teste de Conectividade
    status_text.info("🔍 Verificando conexão com Langflow...")
    if not check_langflow_connectivity(API_URL):
        st.error(f"❌ Não foi possível conectar ao Langflow em {API_URL}. Certifique-se de que o servidor está rodando.")
    else:
        st.session_state.is_processing = True
        st.session_state.start_time = time.time()
        st.session_state.processed_count = 0
        st.session_state.failed_count = 0
        st.session_state.logs = []
        
        output_folder_path.mkdir(exist_ok=True)
        logging.info(f"📂 Iniciando lote de {total_files} arquivos. Pasta: {input_folder_path}")
        
        files_to_process = total_files_list
        
        for i in range(0, len(files_to_process), batch_size):
            batch = files_to_process[i:i + batch_size]
            logging.info(f"📦 Processando lote: {i//batch_size + 1}")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
                futures = [executor.submit(process_file_logic, f, output_folder_path, API_KEY) for f in batch]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    st.session_state.logs.insert(0, result)
                    
                    if result["status"] == "✅ Sucesso":
                        st.session_state.processed_count += 1
                    else:
                        st.session_state.failed_count += 1
                    
                    # Atualiza UI em tempo real
                    update_ui()
                    
                    with tab1:
                        log_container.table(pd.DataFrame(st.session_state.logs))
            
            # Garante sincronização física do lote
            logging.info(f"✔ Lote finalizado.")

        st.session_state.is_processing = False
        status_text.success(f"✅ Processamento Finalizado! Total: {total_files} | Sucessos: {st.session_state.processed_count} | Falhas: {st.session_state.failed_count}")
        st.balloons()
        # st.rerun() removido para manter estado final na tela
