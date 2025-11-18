import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# --- Configuração da Página ---
st.set_page_config(page_title="ColdMail AI - Vendas Automáticas", page_icon="🚀", layout="wide")

# --- Segredos (Cofre) ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    SENHA_MESTRA = st.secrets["SENHA_DO_CLIENTE"]
except Exception:
    st.error("🚨 Erro de Configuração: Chaves não encontradas nos Secrets.")
    st.stop()

# --- Link de Pagamento (Vamos configurar isso jajá) ---
LINK_CHECKOUT = "https://link.mercadopago.com.br/SEU_LINK_AQUI" 

# --- Funções Backend ---
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if not url.startswith('http'): url = 'https://' + url
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = " ".join([t.get_text() for t in soup.find_all(['h1', 'h2', 'p', 'li'])])
        return text[:6000]
    except: return None

def generate_cold_email(context):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Aja como um Copywriter Sênior B2B. Crie 3 Cold Emails curtos e persuasivos para vender meus serviços para a empresa descrita abaixo.
    Dados: {context}
    Regras: Tom casual, foco em dor/solução, português do Brasil.
    """
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
    return chat.choices[0].message.content

# --- INTERFACE COM DESIGN DE VENDAS ---

# 1. Hero Section (A Promessa)
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0;'>🚀 Chega de ser Ignorado no LinkedIn</h1>
        <p style='font-size: 1.2rem; color: #666;'>
            A Inteligência Artificial que lê o site do seu cliente e escreve a abordagem perfeita em 3 segundos.
        </p>
    </div>
""", unsafe_allow_html=True)

# 2. Demonstração de Valor (Benefícios)
col_a, col_b, col_c = st.columns(3)
col_a.info("⚡ **Economize 40h/mês**\n\nPare de ler sites manualmente. A IA faz a pesquisa pesada por você.")
col_b.success("🎯 **Hiper-Personalização**\n\nGere e-mails que provam que você conhece a empresa do cliente.")
col_c.warning("💰 **Aumente suas Vendas**\n\nQuem responde mais rápido e melhor, fecha mais contratos.")

st.divider()

# 3. O Produto (Com Bloqueio)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Gerador Automático")
    target_url = st.text_input("Cole o site da empresa alvo:", placeholder="Ex: www.nubank.com.br")
    
    if st.button("✨ Gerar E-mails Agora", type="primary", use_container_width=True):
        # Verifica se tem senha na sessão
        if "acesso_liberado" not in st.session_state:
            st.session_state.acesso_liberado = False
            
        if not st.session_state.acesso_liberado:
            st.toast("🔒 Recurso bloqueado para visitantes.")
        else:
            if not target_url:
                st.warning("Coloque uma URL primeiro.")
            else:
                with st.spinner("A IA está lendo o site e escrevendo..."):
                    content = scrape_website(target_url)
                    if content:
                        email_text = generate_cold_email(content)
                        st.markdown(email_text)
                    else:
                        st.error("Erro ao ler site.")

with col2:
    # A "Caixa de Pagamento"
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: #333;'>
        <h3 style='color: #333;'>🔐 Acesso Pro</h3>
        <p style='color: #333;'>Desbloqueie gerações ilimitadas e venda todos os dias.</p>
    </div>
    """, unsafe_allow_html=True)
    
    senha_input = st.text_input("Tem a senha?", type="password", placeholder="Digite aqui")
    
    if senha_input == SENHA_MESTRA:
        st.session_state.acesso_liberado = True
        st.success("✅ Acesso Liberado!")
    elif senha_input:
        st.error("Senha incorreta.")
    
    st.markdown("---")
    st.markdown("Ainda não tem acesso?")
    # Botão que leva para o pagamento
    st.link_button("💳 Comprar Acesso Vitalício (R$ 29,90)", LINK_CHECKOUT, use_container_width=True)
    st.caption("Pagamento via Pix/Cartão. Liberação imediata no WhatsApp.")

# Rodapé
st.markdown("<br><br><p style='text-align: center; color: #aaa;'>ColdMail AI © 2025 • Feito para Vendedores de Elite</p>", unsafe_allow_html=True)
