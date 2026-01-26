import requests
import os
import json
import logging
import uuid
import time
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Variáveis de Controle de Concorrência
MAX_CONCURRENT_BATCHES = 1

# Configuração Padrão (pode ser sobrescrita pelo dashboard)
DEFAULT_API_URL = "http://localhost:7860/api/v1/run/8b177d69-ac78-4bcb-8eb8-6815d4348e1f"
INPUT_FOLDER = "./unificados/"
OUTPUT_FOLDER = "./q1-f1/"
COMPONENT_ID = "TextInput-jWrfr"
API_KEY = os.getenv("LANGFLOW_API_KEY")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_and_sort_files(input_folder):
    """
    Lê todos os arquivos .json na pasta e ordena pelo campo 'id'.
    """
    folder = Path(input_folder)
    if not folder.exists():
        logging.error(f"Pasta de entrada {input_folder} não existe.")
        return []

    files_data = []
    for file_path in folder.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'id' in data:
                    files_data.append({"path": file_path, "data": data, "id": data['id']})
                else:
                    logging.warning(f"Arquivo {file_path.name} não possui campo 'id'.")
        except Exception as e:
            logging.error(f"Erro ao ler {file_path.name}: {e}")

    # Ordenação por ID de forma crescente
    files_data.sort(key=lambda x: x['id'])
    return files_data

def process_batch(batch, batch_number, api_url, output_folder, api_key):
    """
    Processa um lote de arquivos, concatena o conteúdo e envia para a API.
    """
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Concatenação do conteúdo dos JSONs
    concatenated_content = ""
    ids_in_batch = []
    for item in batch:
        concatenated_content += json.dumps(item['data'], ensure_ascii=False) + "\n"
        ids_in_batch.append(item['id'])

    headers = {"x-api-key": api_key} if api_key else {}
    
    payload = {
        "input_value": concatenated_content,
        "input_type": "chat",
        "tweaks": {
            COMPONENT_ID: {
                "input_value": concatenated_content
            }
        }
    }

    try:
        logging.info(f"Enviando Batch {batch_number} (IDs: {ids_in_batch}) para API...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=600)
        
        if response.status_code != 200:
            logging.error(f"❌ Erro na API (Status {response.status_code}): {response.text}")
            response.raise_for_status()
        
        result_data = response.json()
        
        # Salva a resposta bruta do modelo
        output_filename = f"batch{batch_number}.json"
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
        
        logging.info(f"✅ Batch {batch_number} concluído e salvo em {output_filename}")
        return {"status": "success", "batch": batch_number, "ids": ids_in_batch}
    
    except Exception as e:
        logging.error(f"❌ Erro no Batch {batch_number}: {e}")
        return {"status": "error", "batch": batch_number, "ids": ids_in_batch, "error": str(e)}

def run_process_batch_mode(batch_size=15, api_url=DEFAULT_API_URL, progress_callback=None):
    """
    Função principal para ser chamada pelo dashboard ou CLI.
    """
    api_key = os.getenv("LANGFLOW_API_KEY")
    files_data = load_and_sort_files(INPUT_FOLDER)
    
    if not files_data:
        logging.error("Nenhum arquivo encontrado para processar.")
        return

    total_files = len(files_data)
    batches = [files_data[i:i + batch_size] for i in range(0, total_files, batch_size)]
    total_batches = len(batches)
    
    logging.info(f"Iniciando processamento de {total_files} arquivos em {total_batches} batches.")

    results = []
    for idx, batch in enumerate(batches, 1):
        if progress_callback:
            progress_callback(idx, total_batches, [item['id'] for item in batch])
        
        res = process_batch(batch, idx, api_url, OUTPUT_FOLDER, api_key)
        results.append(res)
        
        if res["status"] == "error":
            logging.error(f"⚠️ Processamento interrompido devido a erro no Batch {idx}.")
            break
            
        # Delay entre requisições para estabilidade (3 segundos)
        if idx < total_batches:
            logging.info(f"Aguardando 3 segundos para o próximo lote...")
            time.sleep(3)
    
    return results

if __name__ == "__main__":
    # Execução via CLI para teste simples
    run_process_batch_mode()
