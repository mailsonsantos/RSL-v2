import requests
import os
import json
import logging
import re
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações Técnicas da API (Fase 2 - Q3)
FLOW_ID = "121924d9-99f9-42a9-b0bc-2e08e70ba18b"
API_URL = f"http://localhost:7860/api/v1/run/{FLOW_ID}"
COMPONENT_ID = "TextInput-jWrfr"
API_KEY = os.getenv("LANGFLOW_API_KEY")

INPUT_FOLDER = "./q3-f1/"
OUTPUT_FOLDER = "./q3-f2/"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def natural_sort_key(s):
    """
    Chave para ordenação natural (ex: batch1.json, batch2.json, batch10.json).
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', str(s))]

def clean_markdown_tags(text):
    """
    Remove tags de bloco de código Markdown.
    """
    if not text:
        return ""
    # Remove ```json e ```
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return text.strip()

def process_q3_fase2(progress_callback=None):
    """
    Lógica de processamento da Fase 2 da Questão 3.
    """
    input_path = Path(INPUT_FOLDER)
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        logging.error(f"Pasta de entrada {INPUT_FOLDER} não encontrada.")
        return {"status": "error", "message": f"Pasta {INPUT_FOLDER} não encontrada."}

    # Busca arquivos batch*.json e ordena naturalmente
    files = sorted(input_path.glob("batch*.json"), key=natural_sort_key)
    
    if not files:
        logging.warning("Nenhum arquivo batch encontrado para processar.")
        return {"status": "error", "message": "Nenhum arquivo encontrado em ./q3-f1/"}

    consolidated_text = ""
    processed_files = []

    for idx, file_path in enumerate(files, 1):
        try:
            logging.info(f"Lendo {file_path.name}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extração conforme caminho especificado
            # outputs[0]['outputs'][0]['results']['text']['data']['text']
            try:
                raw_text = data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
            except (KeyError, IndexError, TypeError) as e:
                logging.warning(f"Caminho de dados não encontrado em {file_path.name}: {e}")
                continue

            # Limpeza de tags
            clean_text = clean_markdown_tags(raw_text)
            
            # Adiciona separador se não for o primeiro
            if consolidated_text:
                consolidated_text += f"\n\n--- SEÇÃO DE DADOS (LOTE {idx}) ---\n\n"
            
            consolidated_text += clean_text
            processed_files.append(file_path.name)
            
            if progress_callback:
                progress_callback(f"Lido e limpo: {file_path.name}")

        except Exception as e:
            logging.error(f"Erro ao processar {file_path.name}: {e}")

    if not consolidated_text:
        return {"status": "error", "message": "Falha ao extrair conteúdo dos arquivos."}

    # Envio para API
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    payload = {
        "input_value": consolidated_text,
        "input_type": "chat",
        "tweaks": {
            COMPONENT_ID: {
                "input_value": consolidated_text
            }
        }
    }

    try:
        logging.info(f"Enviando consolidação final para API (Flow ID: {FLOW_ID})...")
        if progress_callback:
            progress_callback("Enviando para API (isso pode levar alguns minutos)...")

        response = requests.post(API_URL, json=payload, headers=headers, timeout=180)
        
        if response.status_code != 200:
            error_msg = f"Erro na API (Status {response.status_code}): {response.text}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        result_data = response.json()
        
        # Extrai a síntese final (assumindo o mesmo caminho de resposta)
        try:
            final_synthesis = result_data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
        except (KeyError, IndexError, TypeError):
            # Se não encontrar o texto no caminho padrão, salva o JSON bruto para inspeção
            final_synthesis = json.dumps(result_data, indent=4, ensure_ascii=False)
            logging.warning("Não foi possível extrair o texto limpo da resposta. Salvando JSON bruto.")

        # Armazenamento final
        output_file = output_path / "analise_final_q3.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_synthesis)
        
        logging.info(f"✅ Consolidação concluída! Resultado salvo em {output_file}")
        return {
            "status": "success", 
            "message": "Consolidação concluída com sucesso!", 
            "file": str(output_file),
            "content": final_synthesis
        }

    except requests.exceptions.Timeout:
        error_msg = "Timeout de 180s atingido ao aguardar resposta da API."
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Erro inesperado durante a chamada da API: {e}"
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}

if __name__ == "__main__":
    # Execução CLI
    process_q3_fase2()
