import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def consolidate_data(input_folder):
    input_dir = Path(input_folder)
    consolidated_data = []

    for file_path in sorted(input_dir.glob("*.json")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extração conforme solicitado
                extracted = {
                    "id": data.get("id"),
                    "titulo": data.get("data_extraction", {}).get("titulo"),
                    "resumo": data.get("resumo"),
                    "lacunas_identificadas": data.get("data_extraction", {}).get("lacunas_identificadas"),
                    "mecanismos_conformidade": data.get("data_extraction", {}).get("mecanismos_conformidade"),
                    "referencia": data.get("referencia")
                }
                consolidated_data.append(extracted)
        except Exception as e:
            print(f"Erro ao processar {file_path.name}: {e}")

    return consolidated_data

def generate_introduction(data):
    token = os.getenv("TOKEN")
    if not token:
        print("Erro: Variável de ambiente TOKEN não encontrada.")
        return

    client = OpenAI(api_key=token)

    # Formata os dados para o prompt
    formatted_data = json.dumps(data, indent=2, ensure_ascii=False)

    system_prompt = """Você é um especialista em escrita acadêmica. Com base nos dados fornecidos, redija uma Introdução de alto nível para uma RSL.

Estrutura da Introdução:
1. Contextualização: Fale sobre a importância da IA e Big Data na atualidade e como a governança de Dados se relaciona com esse processo.
2. Problematização: Use os dados das 'lacunas_identificadas' para mostrar que a falta de frameworks de governança é um problema real.
3. Objetivo: Declare que esta RSL mapeia as soluções existentes.

Regras Cruciais:
- Use o formato de citação academia, exemplo "Além disso, Serdrakyan et al. (2020) [<id>], propõe uma...", o id é o id do artigo utilizado, imediatamente após cada afirmação baseada em um artigo.
- Mantenha um tom formal e acadêmico.
- Conecte as ideias dos autores de forma fluida (não faça apenas uma lista de resumos)."""

    user_prompt = f"Aqui estão os dados consolidados dos artigos:\n\n{formatted_data}"

    try:
        print("Enviando solicitação ao GPT-4o-mini...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return None

if __name__ == "__main__":
    input_folder = "/home/mailson/Documentos/Doutorado/RSL-v2/unificados_final"
    output_file = "introducao_rsl.txt"

    print("Consolidando dados...")
    data = consolidate_data(input_folder)
    print(f"Consolidado data de {len(data)} arquivos.")

    if data:
        intro_text = generate_introduction(data)
        if intro_text:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(intro_text)
            print(f"Introdução gerada com sucesso e salva em {output_file}")
        else:
            print("Falha ao gerar a introdução.")
    else:
        print("Nenhum dado consolidado.")
