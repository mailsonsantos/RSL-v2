import requests
import os
import json
import re
import logging
import uuid
import concurrent.futures
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = "http://localhost:7860/api/v1/run/cab4734e-9d31-4c61-89f9-3315a939185a"
INPUT_FOLDER = "arquivos_baixados"
OUTPUT_FOLDER = "arquivos_processados"
LOG_FILE = "erros.log"
COMPONENT_ID = "DoclingInline-jzcAF"
BATCH_SIZE = 3

# Retrieve API Key
API_KEY = os.getenv("LANGFLOW_API_KEY")

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def sanitize_filename(filename):
    """
    Sanitizes the filename: lowercase, underscores instead of spaces, 
    removes special characters, keeps extension (.json).
    """
    name = Path(filename).stem
    # Lowercase
    name = name.lower()
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove special characters (keep only alphanumeric and underscores)
    name = re.sub(r'[^a-z0-9_]', '', name)
    return f"{name}.json"

def process_file(file_path):
    """
    Extrai o conteúdo seguindo o caminho: outputs > 0 > outputs > 0 > results > text > data > text
    Salva no JSON final como 'resposta' e inclui o 'file_source'.
    """
    abs_path = str(Path(file_path).resolve())
    
    headers = {"x-api-key": API_KEY}
    
    payload = {
        "output_type": "text",
        "input_type": "text",
        "input_value": "Iniciando análise",
        "session_id": str(uuid.uuid4()),
        "tweaks": {
            COMPONENT_ID: {
                "path": abs_path
            }
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=320)
        response.raise_for_status()
        
        result_data = response.json()
        
        # --- EXTRAÇÃO PELO CAMINHO ESPECÍFICO ---
        try:
            # Navega exatamente no caminho indicado
            raw_text = result_data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
            
            # Tenta converter a string JSON interna para objeto (para evitar \n e escapes no arquivo final)
            try:
                conteudo_final = json.loads(raw_text)
            except (json.JSONDecodeError, TypeError):
                conteudo_final = raw_text
                
            # Monta o dicionário de saída conforme solicitado
            output_dict = {
                "resposta": conteudo_final,
                "file_source": abs_path
            }
            
        except (KeyError, IndexError) as e:
            logging.error(f"Erro ao acessar caminho no JSON de {file_path}: {str(e)}")
            return False

        # --- SALVAMENTO ---
        output_filename = sanitize_filename(file_path)
        output_path = Path(OUTPUT_FOLDER) / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Salva o JSON limpo
            json.dump(output_dict, f, ensure_ascii=False, indent=4)
            
        return True
    
    except Exception as e:
        logging.error(f"Erro na comunicação com a API para {file_path}: {str(e)}")
        return False

def main():
    # Ensure folders exist
    input_dir = Path(INPUT_FOLDER)
    output_dir = Path(OUTPUT_FOLDER)
    output_dir.mkdir(exist_ok=True)
    
    if not API_KEY:
        print(f"Erro: LANGFLOW_API_KEY não encontrada no arquivo .env.")
        return

    if not input_dir.exists():
        print(f"Erro: Pasta de entrada '{INPUT_FOLDER}' não encontrada.")
        return

    # List all PDF files
    api_files = list(input_dir.glob("*.pdf"))
    
    if not api_files:
        print(f"Nenhum arquivo PDF encontrado em '{INPUT_FOLDER}'.")
        return

    print(f"Encontrados {len(api_files)} arquivos para processar. Lote: {BATCH_SIZE}")
    
    # Process with progress bar and batch control
    with tqdm(total=len(api_files), desc="Processando Artigos") as pbar:
        for i in range(0, len(api_files), BATCH_SIZE):
            batch = api_files[i:i + BATCH_SIZE]
            
            # Use ThreadPoolExecutor for concurrent processing within the batch
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
                # Submit all tasks in the current batch
                future_to_file = {executor.submit(process_file, f): f for f in batch}
                
                # Wait for all tasks in this batch to finish before moving to the next
                for future in concurrent.futures.as_completed(future_to_file):
                    future.result()
                    pbar.update(1)

if __name__ == "__main__":
    main()

