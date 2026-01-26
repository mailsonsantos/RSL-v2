import os
import json
import re
import requests

# Tenta carregar variáveis de ambiente do .env se a lib estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Variáveis de ambiente carregadas do arquivo .env")
except ImportError:
    print("Aviso: 'python-dotenv' não instalado. Usando apenas variáveis de sistema.")

# Configurações da API
FLOW_ID = "dd52c326-4e86-4780-8d3f-d7157b667e1c"
ENDPOINT = f"http://localhost:7860/api/v1/run/{FLOW_ID}"
TEXT_INPUT_ID = "TextInput-jWrfr"
TIMEOUT = 180
# Tenta pegar do ambiente, se não encontrar usa o valor visto no .env
API_KEY = os.getenv("LANGFLOW_API_KEY") or "sk-OpxTBweQJbknbFn4iG-Yjt-caRiigzAFpsCUdV2cjSU"

def natural_sort_key(s):
    """Gera uma chave para ordenação natural (ex: batch1, batch2... batch10)."""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def clean_markdown_json(text):
    """Remove blocos de código markdown (```json ... ``` ou ``` ... ```)."""
    # Remove ```json no início e ``` no fim, lidando com possíveis espaços/quebras
    cleaned = re.sub(r'^```(?:json)?\s*', '', text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned.strip())
    return cleaned.strip()

def process_q2_fase2():
    input_dir = "./q2-f1/"
    output_dir = "./q2-f2/"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Pasta {output_dir} criada.")

    # Listar e ordenar arquivos json
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    files.sort(key=natural_sort_key)
    
    if not files:
        print(f"Nenhum arquivo JSON encontrado em {input_dir}")
        return

    consolidated_texts = []
    
    print(f"Lendo {len(files)} arquivos de {input_dir}...")
    
    for filename in files:
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extração conforme caminho: outputs[0]['outputs'][0]['results']['text']['data']['text']
            raw_text = data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
            
            # Limpeza
            clean_text = clean_markdown_json(raw_text)
            consolidated_texts.append(clean_text)
            print(f"  [OK] {filename}")
            
        except Exception as e:
            print(f"  [ERRO] Falha ao processar {filename}: {str(e)}")

    if not consolidated_texts:
        print("Falha ao extrair textos. Abortando.")
        return

    # Consolidação
    final_input = "\n\n--- SEÇÃO DE DADOS ---\n\n".join(consolidated_texts)
    
    print("\nEnviando dados consolidados para a API (Fase 2)...")
    
    # Adicionando tratamento para o erro 403 do Langflow 1.5+
    payload = {
        "input_value": final_input,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            TEXT_INPUT_ID: {"input_value": final_input}
        }
    }

    # Cabeçalhos com API Key se disponível
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
        print("Usando API Key para autenticação.")

    try:
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"Resposta bruta da API recebida (tamanho: {len(str(result_data))} caracteres)")
            
            # Tentar extrair o texto de diferentes caminhos possíveis
            final_analysis = None
            
            # Caminho 1: Padrão Langflow
            try:
                final_analysis = result_data['outputs'][0]['outputs'][0]['results']['text']['data']['text']
                print("Texto extraído via Caminho 1 (Langflow Standard)")
            except (KeyError, IndexError):
                pass

            # Caminho 2: Se vier direto no result
            if not final_analysis:
                try:
                    final_analysis = result_data['result']
                    print("Texto extraído via Caminho 2 ('result')")
                except KeyError:
                    pass

            # Caminho 3: Se vier como mensagem
            if not final_analysis:
                try:
                    final_analysis = result_data['message']
                    print("Texto extraído via Caminho 3 ('message')")
                except KeyError:
                    pass

            # Fallback: Salvar bruto se nada funcionar
            if not final_analysis:
                final_analysis = json.dumps(result_data, indent=2, ensure_ascii=False)
                print("Aviso: Formato de resposta inesperado, salvando JSON bruto.")

            output_file = os.path.join(output_dir, "analise_final_q2.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_analysis)
            
            print(f"\n[SUCESSO] Análise final salva em {output_file}")
            return True
        else:
            print(f"\n[ERRO] API retornou status {response.status_code}")
            print(f"Detalhes: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n[ERRO] Timeout de {TIMEOUT}s atingido ao chamar a API.")
        return False
    except Exception as e:
        print(f"\n[ERRO] Falha na requisição: {str(e)}")
        return False

if __name__ == "__main__":
    process_q2_fase2()
