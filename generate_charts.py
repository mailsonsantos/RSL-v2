import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Set scientific style
plt.style.use('seaborn-v0_8-paper')
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": 'tight'
})

# Path configuration
INPUT_DIR = "/home/mailson/Documentos/Doutorado/RSL-v2/unificados_final"
OUTPUT_DIR = "/home/mailson/Documentos/Doutorado/RSL-v2/imagens_artigo"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data():
    all_data = []
    files = glob.glob(os.path.join(INPUT_DIR, "*.json"))
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if "data_extraction" in data:
                all_data.append(data["data_extraction"])
    return all_data

def save_plot(name):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved: {path}")

def generate_charts():
    data = load_data()
    df = pd.DataFrame(data)

    # 1. Total de artigos por ano
    plt.figure(figsize=(10, 6))
    year_counts = df['ano_publicacao'].value_counts().sort_index()
    sns.barplot(x=year_counts.index, y=year_counts.values, color='skyblue', edgecolor='black')
    plt.title('Total de Artigos por Ano de Publicação')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade de Artigos')
    save_plot('artigos_por_ano')

    # 2. Total de artigos por país de origem (Top 10)
    plt.figure(figsize=(10, 6))
    country_counts = df['pais_origem'].value_counts().head(10)
    sns.barplot(x=country_counts.values, y=country_counts.index, palette='viridis', edgecolor='black')
    plt.title('Top 10 Países de Origem dos Artigos')
    plt.xlabel('Quantidade de Artigos')
    plt.ylabel('País')
    save_plot('artigos_por_pais')

    # 3. Total de artigos por componente de governança
    # This is a list field
    all_components = []
    for comps in df['componentes_governanca'].dropna():
        if isinstance(comps, list):
            all_components.extend(comps)
        else:
            all_components.append(comps)
    
    comp_counts = Counter(all_components)
    comp_df = pd.DataFrame.from_dict(comp_counts, orient='index', columns=['count']).sort_values('count', ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(x=comp_df['count'], y=comp_df.index, palette='magma', edgecolor='black')
    plt.title('Artigos por Componente de Governança')
    plt.xlabel('Quantidade de Artigos')
    plt.ylabel('Componente')
    save_plot('artigos_por_componente')

    # 4. Total de artigos por dimensoes_eticas_abordadas
    # This is also a list field
    all_ethics = []
    for ethics in df['dimensoes_eticas_abordadas'].dropna():
        if isinstance(ethics, list):
            all_ethics.extend(ethics)
        else:
            all_ethics.append(ethics)
            
    ethics_counts = Counter(all_ethics)
    ethics_df = pd.DataFrame.from_dict(ethics_counts, orient='index', columns=['count']).sort_values('count', ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=ethics_df['count'], y=ethics_df.index, palette='rocket', edgecolor='black')
    plt.title('Artigos por Dimensões Éticas Abordadas')
    plt.xlabel('Quantidade de Artigos')
    plt.ylabel('Dimensão Ética')
    save_plot('artigos_por_dimensoes_eticas')

    # 5. Total de artigos por nivel_maturidade_ia
    plt.figure(figsize=(10, 6))
    maturidade_order = ['Conceitual', 'Desenvolvimento', 'Implementação', 'Produção', 'Maturidade']
    # Filter only those that exist in order or show all if not match
    sns.countplot(data=df, y='nivel_maturidade_ia', order=df['nivel_maturidade_ia'].value_counts().index, palette='mako', edgecolor='black')
    plt.title('Total de Artigos por Nível de Maturidade de IA')
    plt.xlabel('Quantidade de Artigos')
    plt.ylabel('Nível de Maturidade')
    save_plot('artigos_por_nivel_maturidade')

if __name__ == "__main__":
    generate_charts()
