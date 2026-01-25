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
st.set_page_config(page_title="RSL Data Extract Monitor", layout="wide", page_icon="📊")

# CSS customizado para melhorar a estética
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
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
if 'logs_extract' not in st.session_state:
    st.session_state.logs_extract = []
if 'processed_count_extract' not in st.session_state:
    st.session_state.processed_count_extract = 0
if 'failed_count_extract' not in st.session_state:
    st.session_state.failed_count_extract = 0
if 'is_processing_extract' not in st.session_state:
    st.session_state.is_processing_extract = False
if 'start_time_extract' not in st.session_state:
    st.session_state.start_time_extract = None

# --- Constantes do Langflow (Data Extraction) ---
API_URL = "http://localhost:7860/api/v1/run/90c125b1-8478-4073-aef2-835a0e757065"
COMPONENT_ID = "CustomComponent-pm20y"
API_KEY = os.getenv("LANGFLOW_API_KEY")

# --- Funções Auxiliares ---
def sanitize_filename(filename):
    name = Path(filename).stem
    name = name.lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return f"{name}.json"

def check_langflow_connectivity(url):
    try:
        base_url = "/".join(url.split("/")[:3])
        response = requests.get(base_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def process_file_logic(file_path, output_folder, api_key):
    file_name = Path(file_path).name
    logging.info(f"📊 Iniciando extração: {file_name}")
    
    abs_path = str(Path(file_path).resolve())
    headers = {"x-api-key": api_key}
    payload = {
        "output_type": "text",
        "input_type": "text",
        "input_value": "Extrair dados do artigo",
        "session_id": str(uuid.uuid4()),
        "tweaks": {COMPONENT_ID: {"path": abs_path}}
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=400)
        response.raise_for_status()
        
        result_data = response.json()
        
        # Extração flexível
        raw_text = None
        try:
            raw_text = result_data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
        except (KeyError, IndexError):
            try:
                raw_text = result_data['outputs'][0]['outputs'][0]['results']['message']['text']
            except (KeyError, IndexError):
                raw_text = str(result_data)
        
        # Tenta sanitizar JSON se vier com blocos de código markdown
        processed_dict = None
        if isinstance(raw_text, str):
            raw_text_clean = re.sub(r'```json\n?|\n?```', '', raw_text).strip()
            try:
                processed_dict = json.loads(raw_text_clean)
            except:
                # Tenta encontrar o JSON dentro da string
                json_match = re.search(r'\{.*\}', raw_text_clean, re.DOTALL)
                if json_match:
                    try:
                        processed_dict = json.loads(json_match.group())
                    except:
                        processed_dict = {"dados_extraidos": raw_text}
                else:
                    processed_dict = {"dados_extraidos": raw_text}
        else:
            processed_dict = raw_text

        # Envolve os dados extraídos e adiciona a fonte
        final_output = {
            "dados_extraidos": processed_dict,
            "file_source": abs_path
        }
        
        output_filename = sanitize_filename(file_path)
        output_path = Path(output_folder) / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
            
        logging.info(f"✅ Sucesso: {file_name}")
        return {"file": file_name, "status": "✅ Sucesso", "time": time.strftime("%H:%M:%S")}
    
    except Exception as e:
        error_msg = str(e)
        logging.error(f"❌ Erro em {file_name}: {error_msg}")
        with open("erros_dataextract.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR - {file_path}: {error_msg}\n")
        return {"file": file_name, "status": "❌ Erro", "error": error_msg, "time": time.strftime("%H:%M:%S")}

# --- Sidebar ---
st.sidebar.title("🛠️ Configurações de Extração")
batch_size = st.sidebar.number_input("BATCH_SIZE", min_value=1, max_value=10, value=3)
input_folder_val = st.sidebar.text_input("Pasta de Entrada", value="artigos_baixados")
output_folder_val = st.sidebar.text_input("Pasta de Saída", value="data_extraction")

input_folder_path = Path(input_folder_val).resolve()
output_folder_path = Path(output_folder_val).resolve()

if not input_folder_path.exists():
    st.sidebar.error(f"❌ Pasta '{input_folder_val}' não encontrada!")
    total_files_list = []
else:
    total_files_list = list(input_folder_path.glob("*.pdf"))

total_files = len(total_files_list)

start_btn = st.sidebar.button("📊 Iniciar Extração", 
                               disabled=st.session_state.is_processing_extract or not API_KEY or total_files == 0)

# --- Cabeçalho ---
st.title("📊 Monitor de Extração de Dados (RSL)")

# --- Métricas ---
metric_cols = st.columns(5)
m1 = metric_cols[0].empty()
m2 = metric_cols[1].empty()
m3 = metric_cols[2].empty()
m4 = metric_cols[3].empty()
m5 = metric_cols[4].empty()

def update_metrics():
    processed = st.session_state.processed_count_extract + st.session_state.failed_count_extract
    remaining = total_files - processed
    m1.metric("Total PDFs", total_files)
    m2.metric("Processados", processed)
    m3.metric("Restantes", max(0, remaining))
    m4.metric("Sucessos", st.session_state.processed_count_extract)
    m5.metric("Falhas", st.session_state.failed_count_extract)
    return processed / total_files if total_files > 0 else 0

pct = update_metrics()
progress_bar = st.progress(pct)
status_text = st.empty()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Monitoramento", "🔍 Ver Extrações", "⚠️ Erros"])

with tab1:
    log_container = st.empty()
    if st.session_state.logs_extract:
        log_container.table(pd.DataFrame(st.session_state.logs_extract))

with tab2:
    if output_folder_path.exists():
        json_files = list(output_folder_path.glob("*.json"))
        if json_files:
            selected_json = st.selectbox("Selecione uma extração", options=[f.name for f in json_files])
            if selected_json:
                with open(output_folder_path / selected_json, 'r', encoding='utf-8') as f:
                    st.json(json.load(f))
        else:
            st.info("Nenhuma extração gerada ainda.")

with tab3:
    if Path("erros_dataextract.log").exists():
        with open("erros_dataextract.log", "r", encoding="utf-8") as f:
            errors = f.readlines()
            for err in reversed(errors):
                st.text(err.strip())
    else:
        st.success("Tudo limpo!")

# --- Lógica ---
if start_btn:
    if not check_langflow_connectivity(API_URL):
        st.error(f"❌ Langflow Offline em {API_URL}")
    else:
        st.session_state.is_processing_extract = True
        st.session_state.start_time_extract = time.time()
        st.session_state.processed_count_extract = 0
        st.session_state.failed_count_extract = 0
        st.session_state.logs_extract = []
        
        output_folder_path.mkdir(exist_ok=True)
        
        for i in range(0, total_files, batch_size):
            batch = total_files_list[i:i + batch_size]
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
                futures = [executor.submit(process_file_logic, f, output_folder_path, API_KEY) for f in batch]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    st.session_state.logs_extract.insert(0, result)
                    if result["status"] == "✅ Sucesso":
                        st.session_state.processed_count_extract += 1
                    else:
                        st.session_state.failed_count_extract += 1
                    
                    update_metrics()
                    progress_bar.progress((st.session_state.processed_count_extract + st.session_state.failed_count_extract)/total_files)
                    log_container.table(pd.DataFrame(st.session_state.logs_extract))
        
        st.session_state.is_processing_extract = False
        st.success("Concluído!")
        st.balloons()
