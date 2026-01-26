import os
import json
from pathlib import Path

def unificar():
    resumos_dir = Path("resumos")
    extração_dir = Path("data_extraction")
    unificados_dir = Path("unificados")

    # Criar diretório unificados se não existir
    unificados_dir.mkdir(exist_ok=True)

    # Dicionário para agrupar dados por file_source
    dados_unificados = {}

    # Lendo resumos
    print("Lendo arquivos da pasta resumos...")
    for file_path in resumos_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            file_source = data.get("file_source")
            if file_source:
                if file_source not in dados_unificados:
                    dados_unificados[file_source] = {}
                dados_unificados[file_source]["resumo"] = data.get("resposta")

    # Lendo extrações
    print("Lendo arquivos da pasta data_extraction...")
    for file_path in extração_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            file_source = data.get("file_source")
            if file_source:
                if file_source not in dados_unificados:
                    dados_unificados[file_source] = {}
                dados_unificados[file_source]["data_extraction"] = data.get("dados_extraidos")

    # Salvando arquivos unificados
    print(f"Salvando resultados na pasta {unificados_dir}...")
    idx = 1
    for file_source, conteudo in dados_unificados.items():
        # Gerar um nome de arquivo amigável a partir do file_source
        file_name = Path(file_source).stem.replace(" ", "_").lower() + ".json"
        
        resultado = {
            "id": idx,
            "file_source": file_source,
            "resumo": conteudo.get("resumo"),
            "data_extraction": conteudo.get("data_extraction")
        }

        output_path = unificados_dir / file_name
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
        
        idx += 1

    print(f"Processo concluído! {idx - 1} arquivos unificados gerados.")

if __name__ == "__main__":
    unificar()
