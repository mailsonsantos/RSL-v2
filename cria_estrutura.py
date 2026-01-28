import pandas as pd
import numpy as np
import os

# 1. Carregar os dados
file_path = 'articles_preenchido_comQA.xlsx'
df = pd.read_excel(file_path)

# 2. Filtrar apenas aprovados
if 'STATUS_SELECAO' in df.columns:
    df_filtered = df[df['STATUS_SELECAO'] == 'APROVADO'].copy()
else:
    df_filtered = df.copy()

# 3. Selecionar colunas e tratar nulos
cols_to_keep = ['author', 'title', 'journal', 'volume', 'pages', 'year', 'doi', 'url']
df_filtered = df_filtered[cols_to_keep].fillna('')

total_esperado = len(df_filtered)
print(f"Total de artigos aprovados encontrados: {total_esperado}")

# 4. Configurar blocos de 25
block_size = 25
num_arquivos = int(np.ceil(total_esperado / block_size))

total_processado = 0
created_files = []

for i in range(num_arquivos):
    # Cálculo preciso do intervalo para não pular nem repetir linhas
    inicio = i * block_size
    fim = (i + 1) * block_size
    chunk = df_filtered.iloc[inicio:fim]

    if not chunk.empty:
        filename = f'referencias_bloco_{i+1}.csv'
        chunk.to_csv(filename, index=False, encoding='utf-8')
        created_files.append(filename)
        
        count_chunk = len(chunk)
        total_processado += count_chunk
        print(f"Gerado {filename}: Itens {inicio+1} a {min(fim, total_esperado)} (Total no arquivo: {count_chunk})")

# 5. Validação final
if total_processado == total_esperado:
    print(f"\n✅ VALIDAÇÃO SUCESSO: Todos os {total_esperado} artigos foram incluídos nos arquivos.")
else:
    dif = total_esperado - total_processado
    print(f"\n❌ ERRO DE VALIDAÇÃO: Faltam {dif} artigos no processamento!")