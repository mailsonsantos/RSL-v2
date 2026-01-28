import os
import json
from pathlib import Path

def update_article_ids():
    # Caminhos
    pasta_origem = "unificados"
    pasta_destino = "unificados_final"
    arquivo_mapeamento = "id_referencias_total.json"

    # Criar pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)

    # Carregar o mapeamento
    print(f"Carregando mapeamento de {arquivo_mapeamento}...")
    try:
        with open(arquivo_mapeamento, "r", encoding="utf-8") as f:
            mapeamento_raw = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o mapeamento: {e}")
        return

    # Criar um dicionário para busca rápida: {id_antigo: {"id_rsl": id_rsl, "referencia": ref}}
    id_map = {
        item["id"]: {
            "id_rsl": item["id_rsl"],
            "referencia": item.get("referencia", "")
        } 
        for item in mapeamento_raw if "id" in item and "id_rsl" in item
    }
    print(f"Mapeamento carregado: {len(id_map)} entradas encontradas.")

    # Listar arquivos na pasta unificados
    arquivos = [f for f in os.listdir(pasta_origem) if f.endswith(".json")]
    print(f"Processando {len(arquivos)} arquivos em '{pasta_origem}'...")

    processados = 0
    nao_mapeados = 0

    for nome_arquivo in arquivos:
        caminho_entrada = os.path.join(pasta_origem, nome_arquivo)
        caminho_saida = os.path.join(pasta_destino, nome_arquivo)

        try:
            with open(caminho_entrada, "r", encoding="utf-8") as f:
                data = json.load(f)

            old_id = data.get("id")
            if old_id in id_map:
                map_data = id_map[old_id]
                new_id = map_data["id_rsl"]
                referencia = map_data["referencia"]
                
                # Atualizar os campos
                data["id_original"] = old_id
                data["id"] = new_id
                data["referencia"] = referencia
                
                with open(caminho_saida, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                processados += 1
            else:
                # Se não houver mapeamento
                data["id_original"] = old_id
                with open(caminho_saida, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                print(f"Aviso: ID {old_id} não encontrado no mapeamento para o arquivo '{nome_arquivo}'.")
                nao_mapeados += 1

        except Exception as e:
            print(f"Erro ao processar '{nome_arquivo}': {e}")

    print(f"\nConcluído!")
    print(f"- Sucesso: {processados}")
    print(f"- Sem mapeamento (mas copiados): {nao_mapeados}")
    print(f"- Total processado: {processados + nao_mapeados}")
    print(f"Arquivos salvos em: '{pasta_destino}'")

if __name__ == "__main__":
    update_article_ids()
