import os
import json
import pandas as pd
import re
import unicodedata
import difflib

def normalizar_texto(texto):
    if not texto:
        return ""
    # Garantir minúsculo e remover espaços extras
    texto = str(texto).lower().strip()
    return texto

def vincular_referencias():
    # Configurações e Filtros
    pasta_unificados = "unificados"
    planilha_path = "articles_preenchido_comQA.xlsx"
    saida_path = "id_referencias.json"
    
    # Lista de IDs permitidos (conforme solicitado pelo usuário)
    IDS_PERMITIDOS = [1, 3, 4, 5, 6, 10, 13, 15, 16, 19, 21, 25, 31, 32, 35, 36, 37, 40, 45, 46, 54, 63, 65, 69, 70, 71, 72, 78, 79, 84, 85, 91, 95, 99, 100, 107, 111, 112, 114, 116, 118, 123, 126, 127]

    print(f"Lendo planilha: {planilha_path}")
    try:
        df = pd.read_excel(planilha_path)
    except Exception as e:
        print(f"Erro ao ler a planilha: {e}")
        return

    # Criar mapeamento: {titulo_normalizado: {"referencia": ref, "id_rsl": id_rsl}}
    referencias_map = {}
    for _, row in df.iterrows():
        title_orig = str(row['title'])
        title_norm = normalizar_texto(title_orig)
        ref = row.get('Referencia')
        id_rsl = row.get('id_rsl')
        if title_norm:
            referencias_map[title_norm] = {
                "referencia": ref,
                "id_rsl": id_rsl
            }

    resultados = []
    nao_encontrados = []
    arquivos_json = [f for f in os.listdir(pasta_unificados) if f.endswith('.json')]
    
    print(f"Processando arquivos JSON filtrados (IDs específicos)...")

    for filename in arquivos_json:
        filepath = os.path.join(pasta_unificados, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                article_id = data.get('id')
                
                # FILTRO DE ID: Ignorar se não estiver na lista
                if article_id not in IDS_PERMITIDOS:
                    continue

                title_in_json = data.get('data_extraction', {}).get('titulo', '')
                title_json_norm = normalizar_texto(title_in_json)
                
                # 1. Tentar match exato (em minúsculo)
                match_data = referencias_map.get(title_json_norm)
                
                # 2. Se não encontrou, tentar Lógica Fuzzy
                if not match_data:
                    possiveis_titulos = list(referencias_map.keys())
                    matches = difflib.get_close_matches(title_json_norm, possiveis_titulos, n=1, cutoff=0.7)
                    if matches:
                        match_data = referencias_map[matches[0]]
                        print(f"Match Fuzzy: '{title_json_norm[:30]}...' -> '{matches[0][:30]}...' (ID: {article_id})")

                if match_data:
                    # Garantir que id_rsl seja um inteiro se possível (evitar .0)
                    id_rsl_val = match_data["id_rsl"]
                    try:
                        if pd.notna(id_rsl_val):
                            id_rsl_val = int(id_rsl_val)
                    except:
                        pass

                    resultados.append({
                        "id": article_id, # ID do arquivo JSON base
                        "referencia": match_data["referencia"], # Da planilha
                        "id_rsl": id_rsl_val # Da planilha (agora sem decimais)
                    })
                else:
                    print(f"Aviso: Referência não encontrada para: '{title_in_json[:50]}...' ({filename})")
                    nao_encontrados.append(data)

            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

    # Ordenar resultados por ID
    resultados.sort(key=lambda x: x.get('id', 0))

    # Salvar o resultado principal
    with open(saida_path, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    # Salvar os não encontrados (apenas se estiverem na lista de IDs permitidos)
    with open("nao_encontrados.json", 'w', encoding='utf-8') as f:
        json.dump(nao_encontrados, f, indent=4, ensure_ascii=False)

    print(f"\nBusca Finalizada!")
    print(f"- Total esperado: {len(IDS_PERMITIDOS)} IDs.")
    print(f"- Encontrados: {len(resultados)}")
    print(f"- Não encontrados (da lista): {len(nao_encontrados)}")
    print(f"Arquivos gerados: {saida_path} e nao_encontrados.json")

if __name__ == "__main__":
    vincular_referencias()
