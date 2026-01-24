import os

# Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LISTA_PATH = os.path.join(ROOT_DIR, 'lista_problematicos.txt')
ARTIGOS_DIR = os.path.join(ROOT_DIR, 'artigos_baixados')

def cleanup():
    if not os.path.exists(LISTA_PATH):
        print(f"Erro: {LISTA_PATH} não encontrado.")
        return

    if not os.path.exists(ARTIGOS_DIR):
        print(f"Erro: {ARTIGOS_DIR} não encontrado.")
        return

    # Read the list of files to keep
    with open(LISTA_PATH, 'r', encoding='utf-8') as f:
        # Expected format: "- Filename.pdf"
        files_to_keep = set()
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Remove the "- " prefix if it exists
            if line.startswith("- "):
                line = line[2:].strip()
            files_to_keep.add(line)

    print(f"Total de arquivos na lista para manter: {len(files_to_keep)}")

    # List all files in the directory
    all_files = os.listdir(ARTIGOS_DIR)
    
    removed_count = 0
    kept_count = 0

    for filename in all_files:
        if filename in files_to_keep:
            kept_count += 1
            continue
        
        file_path = os.path.join(ARTIGOS_DIR, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                print(f"Erro ao remover {filename}: {e}")

    print("-" * 30)
    print(f"Limpeza concluída!")
    print(f"Arquivos mantidos: {kept_count}")
    print(f"Arquivos removidos: {removed_count}")
    
    if kept_count != len(files_to_keep):
        missing = files_to_keep - set(all_files)
        if missing:
            print("\nAVISO: Alguns arquivos da lista não foram encontrados na pasta:")
            for m in missing:
                print(f"  - {m}")

if __name__ == "__main__":
    cleanup()
