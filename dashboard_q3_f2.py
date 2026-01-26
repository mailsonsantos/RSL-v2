import streamlit as st
import os
from pathlib import Path
from q3_fase2 import process_q3_fase2

# Configuração da página
st.set_page_config(
    page_title="RSL - Consolidação Final Q3",
    page_icon="📊",
    layout="wide"
)

# Estilização Customizada (Aesthetics)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e2130;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📊 Consolidação Final da Questão 3")
    st.markdown("---")
    
    st.info("""
    **Objetivo:** Este módulo realiza a síntese final (Fase 2) da Questão 3, 
    unificando os resultados dos lotes processados na Fase 1.
    """)

    # Verificação de arquivos existentes
    input_folder = Path("./q3-f1/")
    batch_files = list(input_folder.glob("batch*.json")) if input_folder.exists() else []

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Status dos Dados")
        if not input_folder.exists():
            st.error("❌ Pasta `./q3-f1/` não encontrada.")
        elif not batch_files:
            st.warning("⚠️ Nenhum arquivo `batch*.json` encontrado em `./q3-f1/`.")
        else:
            st.success(f"✅ {len(batch_files)} arquivos de batch prontos para consolidação.")
            for f in sorted([f.name for f in batch_files]):
                st.text(f"  - {f}")

    with col2:
        st.subheader("⚙️ Execução")
        
        # Botão desabilitado se não houver arquivos
        run_btn = st.button(
            "🚀 Gerar Consolidação Final (Q3 - Fase 2)", 
            disabled=not batch_files
        )

        if run_btn:
            log_container = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner("Processando..."):
                def update_log(msg):
                    log_container.code(msg)
                
                result = process_q3_fase2(progress_callback=update_log)
                
                if result["status"] == "success":
                    st.balloons()
                    st.success(result["message"])
                    st.markdown("### 📝 Resultado da Síntese Final")
                    st.markdown(result["content"])
                    
                    # Opção de download
                    st.download_button(
                        label="📥 Baixar Análise Final (.md)",
                        data=result["content"],
                        file_name="analise_final_q3.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(f"❌ Erro: {result['message']}")

    # Rodapé
    st.markdown("---")
    st.caption("RSL-v2 - Sistema de Revisão Sistemática de Literatura")

if __name__ == "__main__":
    main()
