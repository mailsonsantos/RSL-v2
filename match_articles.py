import os
import pandas as pd
import re

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower()
    # Remove extension if any
    if text.endswith('.pdf'):
        text = text[:-4]
    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z0-9]', '', text)
    return text

def main():
    xls_path = 'articles.xls'
    output_xls_path = 'articles_preenchido.xlsx'
    folder_path = 'artigos_baixados'
    orphans_path = 'artigos_nao_listados.txt'

    print(f"Lendo {xls_path}...")
    df = pd.read_excel(xls_path)

    if 'title' not in df.columns:
        print("Erro: Coluna 'title' não encontrada no arquivo XLS.")
        return

    print(f"Listando arquivos em {folder_path}...")
    folder_files = os.listdir(folder_path)
    
    # Pre-calculate normalized filenames
    normalized_files = {}
    for filename in folder_files:
        norm = normalize_text(filename)
        if norm:
            normalized_files[norm] = filename

    print("Cruzando dados...")
    
    matched_files = set()
    identificado_col = []

    for index, row in df.iterrows():
        title = row['title']
        norm_title = normalize_text(title)
        
        found = False
        if norm_title in normalized_files:
            found = True
            matched_files.add(normalized_files[norm_title])
        else:
            # Secondary check: fuzzy/partial match for long titles that might be truncated in filename
            for norm_file, original_filename in normalized_files.items():
                if (len(norm_title) > 20 and len(norm_file) > 20) and (norm_title[:50] in norm_file or norm_file[:50] in norm_title):
                    found = True
                    matched_files.add(original_filename)
                    break
        
        identificado_col.append("Sim" if found else "Não")

    df['identificado'] = identificado_col

    print(f"Salvando {output_xls_path}...")
    df.to_excel(output_xls_path, index=False)

    # Find orphans (files in folder NOT in XLS)
    orphans = [f for f in folder_files if f not in matched_files]

    if orphans:
        print(f"Encontrados {len(orphans)} artigos não listados. Salvando em {orphans_path}...")
        with open(orphans_path, 'w', encoding='utf-8') as f:
            for orphan in sorted(orphans):
                f.write(f"{orphan}\n")
    else:
        print("Todos os artigos da pasta foram identificados na lista.")
        if os.path.exists(orphans_path):
            os.remove(orphans_path)

    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
