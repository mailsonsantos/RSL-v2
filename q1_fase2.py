import os
import json
import requests
import re
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configurações do Endpoint Fase 2
FASE2_API_URL = "http://localhost:7860/api/v1/run/18e83fea-d08c-4501-81b2-c3ed9e5e421e"
COMPONENT_ID = "TextInput-jWrfr"
TIMEOUT = 180
API_KEY = os.getenv("LANGFLOW_API_KEY")

def natural_sort_key(s):
    """Chave para ordenação natural (ex: batch1, batch2, ..., batch10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

def extrair_texto_do_json(file_path):
    """Extrai o texto processado do JSON do Langflow (Fase 1)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Caminho especificado: outputs[0]['outputs'][0]['results']['text']['data']['text']
            return data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return ""

def consolidar_e_enviar(input_dir="./q1-f1/", output_dir="./q1-f2/", progress_callback=None):
    """Lê batches, consolida texto e envia para Fase 2."""
    
    # 1. Garantir diretórios
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 2. Listar e ordenar arquivos
    input_path = Path(input_dir)
    if not input_path.exists():
        return False, "Pasta de entrada não encontrada."
    
    files = sorted(list(input_path.glob("batch*.json")), key=natural_sort_key)
    if not files:
        return False, "Nenhum arquivo batch encontrado."
    
    # 3. Concatenar conteúdo
    textos_extraidos = []
    for f in files:
        if progress_callback:
            progress_callback(f"Lendo {f.name}...")
        texto = extrair_texto_do_json(f)
        if texto:
            textos_extraidos.append(texto)
    
    consolidado = "\n\n============\n\n".join(textos_extraidos)
    total_chars = len(consolidado)
    
    if progress_callback:
        progress_callback(f"Consolidação completa. Tamanho total: {total_chars} caracteres.")
    
    # 4. Enviar para API
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    
    payload = {
        "input_value": consolidado,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            COMPONENT_ID: {"input_value": consolidado}
        }
    }
    
    try:
        if progress_callback:
            progress_callback(f"Enviando para Langflow Fase 2... (Autenticado: {'Sim' if API_KEY else 'Não'})")
        
        response = requests.post(FASE2_API_URL, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        
        result_json = response.json()
        
        # 5. Salvar resultado final
        # Tenta extrair a resposta da Fase 2 para salvar em markdown
        try:
            final_text = result_json['outputs'][0]['outputs'][0]['results']['text']['data']['text']
        except:
            final_text = json.dumps(result_json, indent=2, ensure_ascii=False)
            
        output_file = Path(output_dir) / "analise_final_q1.md"
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(final_text)
            
        return True, f"Sucesso! Resultado salvo em {output_file}"
        
    except requests.exceptions.RequestException as e:
        return False, f"Erro na requisição: {str(e)}"
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"

if __name__ == "__main__":
    print("Iniciando Consolidação Final (Q1 Fase 2)...")
    success, msg = consolidar_e_enviar()
    print(msg)
