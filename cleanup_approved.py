import pandas as pd
import os
import shutil

# Configurações
EXCEL_FILE = 'articles_preenchido_comQA.xlsx'
SHEET_NAME = 'Folha1'
FOLDER_PATH = 'artigos_baixados'
STATUS_COL = 'STATUS_SELECAO'
TITLE_COL = 'title'  # Assumindo que a coluna se chama 'title' com base no pedido
BACKUP_FOLDER = 'artigos_nao_aprovados_backup'

import re

def normalize_string(s):
    """Remove tudo que não é letra ou número e converte para minúsculas."""
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

def run_cleanup(dry_run=True):
    print(f"{'[DRY RUN] ' if dry_run else ''}Iniciando a limpeza dos artigos...")
    
    # 1. Ler a planilha
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
        return

    # 2. Filtrar aprovados
    aprovados_df = df[df[STATUS_COL] == 'APROVADO']
    print(f"Total de aprovados na planilha: {len(aprovados_df)}")
    
    # 3. Criar lista de nomes normalizados dos aprovados
    aprovados_titles = aprovados_df[TITLE_COL].astype(str).tolist()
    aprovados_normalized = {normalize_string(t): t for t in aprovados_titles}
    
    # 4. Listar arquivos locais
    if not os.path.exists(FOLDER_PATH):
        print(f"Pasta {FOLDER_PATH} não encontrada.")
        return
        
    arquivos_locais = os.listdir(FOLDER_PATH)
    arquivos_pdf = [f for f in arquivos_locais if f.lower().endswith('.pdf')]
    print(f"Total de arquivos PDF locais: {len(arquivos_pdf)}")

    # 5. Identificar o que manter e o que remover
    a_manter = []
    a_remover = []
    econtrados_set = {} # norm_expected -> list of local files

    for f in arquivos_pdf:
        # Remover a extensão e normalizar
        name_no_ext = f.rsplit('.', 1)[0]
        norm_file = normalize_string(name_no_ext)
        
        found_target = None
        # Tentativa 1: Match exato na string normalizada
        if norm_file in aprovados_normalized:
            found_target = norm_file
        else:
            # Tentativa 2: Match por substring (truncamento)
            for norm_expected in aprovados_normalized:
                if (len(norm_file) > 15 and norm_expected.startswith(norm_file)) or \
                   (len(norm_expected) > 15 and norm_file.startswith(norm_expected[:len(norm_file)])):
                    found_target = norm_expected
                    break
        
        if found_target:
            a_manter.append(f)
            if found_target not in econtrados_set:
                econtrados_set[found_target] = []
            econtrados_set[found_target].append(f)
        else:
            a_remover.append(f)

    print(f"Artigos que serão MANTIDOS: {len(a_manter)}")
    print(f"Artigos que serão REMOVIDOS: {len(a_remover)}")
    
    # Verificar duplicatas (múltiplos arquivos para o mesmo artigo)
    duplicatas = {k: v for k, v in econtrados_set.items() if len(v) > 1}
    if duplicatas:
        print(f"\n--- {len(duplicatas)} artigos possuem DUPLICATAS (múltiplos arquivos) ---")
        for norm, files in list(duplicatas.items())[:5]:
            print(f"- Artigo: {aprovados_normalized[norm]}")
            print(f"  Arquivos: {files}")
            
    # Verificar quais dos 207 não foram encontrados
    nao_encontrados = []
    for norm_exp, orig in aprovados_normalized.items():
        if norm_exp not in econtrados_set:
            nao_encontrados.append(orig)
            
    if nao_encontrados:
        print(f"\n--- {len(nao_encontrados)} artigos aprovados NÃO encontrados na pasta ---")
        for t in nao_encontrados[:10]: # Mostrar só os 10 primeiros
            print(f"- {t}")
        if len(nao_encontrados) > 10:
            print("...")

    print(f"Artigos que serão MANTIDOS: {len(a_manter)}")
    print(f"Artigos que serão REMOVIDOS: {len(a_remover)}")

    if not dry_run and a_remover:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
            print(f"Criada pasta de backup: {BACKUP_FOLDER}")

        for f in a_remover:
            src = os.path.join(FOLDER_PATH, f)
            dst = os.path.join(BACKUP_FOLDER, f)
            shutil.move(src, dst)
        print("Remoção (movimentação para backup) concluída.")
    elif dry_run:
        print("Nenhum arquivo foi removido (modo dry-run).")

if __name__ == "__main__":
    # Agora executamos a limpeza real
    run_cleanup(dry_run=False)
