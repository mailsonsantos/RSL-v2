import streamlit as st
import os
import subprocess
import time

# Configurações de layout
st.set_page_config(page_title="RSL Q2 - Fase 2", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🛡️ Síntese Final de Ética e Regulação (Q2)")
    st.subheader("Fase 2: Consolidação e Análise Final")

    # Sidebar com informações
    st.sidebar.info("""
    **Fluxo de Trabalho:**
    1. Lê arquivos de `./q2-f1/`
    2. Consolida extrações
    3. Envia para a API de síntese
    4. Gera `./q2-f2/analise_final_q2.md`
    """)

    # Validação inicial
    input_dir = "./q2-f1/"
    q2_f2_script = "q2_fase2.py"
    output_file = "./q2-f2/analise_final_q2.md"

    if not os.path.exists(input_dir):
        st.error(f"❌ Pasta de entrada `{input_dir}` não encontrada.")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    if not files:
        st.warning(f"⚠️ Nenhum arquivo JSON encontrado em `{input_dir}`. Execute a Fase 1 primeiro.")
        return

    st.success(f"✅ {len(files)} arquivos de lote detectados prontos para processamento.")

    # Botão de ação
    if st.button("🚀 Gerar Síntese Final"):
        with st.status("Processando Consolidação de Dados...", expanded=True) as status:
            st.write("Executando script de processamento...")
            
            # Executa o script q2_fase2.py
            try:
                process = subprocess.Popen(
                    ["python3", q2_f2_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Exibe logs em tempo real
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        st.write(f"`{output.strip()}`")
                
                rc = process.poll()
                if rc == 0:
                    status.update(label="✅ Processamento concluído com sucesso!", state="complete", expanded=False)
                    st.balloons()
                else:
                    err = process.stderr.read()
                    st.error(f"Erro na execução: {err}")
                    status.update(label="❌ Falha no processamento", state="error")
            except Exception as e:
                st.error(f"Falha ao iniciar o script: {str(e)}")
                status.update(label="❌ Erro fatal", state="error")

    # Área de visualização do resultado
    st.divider()
    if os.path.exists(output_file):
        st.header("📄 Prévia da Análise Final")
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        st.markdown(content)
        
        st.download_button(
            label="📥 Baixar Análise Final (.md)",
            data=content,
            file_name="analise_final_q2.md",
            mime="text/markdown"
        )
    else:
        st.info("Aguardando geração do resultado final...")

if __name__ == "__main__":
    main()
