import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# --- Configuração da Página ---
st.set_page_config(page_title="ColdMail AI - SaaS", page_icon="💎", layout="wide")

# --- Link da Assinatura (Mercado Pago) ---
LINK_ASSINATURA = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=SEU_LINK_AQUI"

# --- Gestão de Acesso (Banco de Dados Simplificado) ---
# Pega a chave da API e a lista de clientes permitidos dos Segredos
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    # A lista virá como uma string única separada por vírgulas. Ex: "joao@gmail.com,maria@hotmail.com"
    CLIENTES_ATIVOS = st.secrets["CLIENTES_ATIVOS"].split(",")
    # Remove espaços em branco que podem ter ficado
    CLIENTES_ATIVOS = [email.strip() for email in CLIENTES_ATIVOS]
except Exception:
    st.error("🚨 Configuração incompleta nos Secrets.")
    st.stop()

# --- Funções Backend (Iguais) ---
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
    Aja como um Copywriter B2B Sênior. Crie 3 Cold Emails curtos para vender meus serviços.
    Contexto do Cliente: {context}
    Regras: Tom casual, foco em dor/solução, português do Brasil. Sem "Prezados".
    """
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
    return chat.choices[0].message.content

# --- INTERFACE ---

st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 0;'>💎 ColdMail AI <span style='font-size: 1.5rem; color: #28a745; vertical-align: middle; border: 1px solid #28a745; padding: 4px 10px; border-radius: 20px;'>PRO</span></h1>
        <p style='font-size: 1.2rem; color: #666;'>Sua máquina de vendas recorrente.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# COLUNA 2: Login / Assinatura
with col2:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; color: #333;'>
        <h3 style='color: #333; margin-top:0;'>👤 Área do Assinante</h3>
        <p style='color: #555; font-size: 0.9rem;'>Para acessar, digite o e-mail cadastrado na sua assinatura.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input de Login
    email_login = st.text_input("Seu E-mail de Acesso", placeholder="exemplo@email.com").lower().strip()
    
    # Botão de Login
    if st.button("Entrar / Validar Acesso", use_container_width=True):
        if email_login in CLIENTES_ATIVOS:
            st.session_state.logado = True
            st.session_state.email_usuario = email_login
            st.toast(f"Bem-vindo de volta, {email_login.split('@')[0]}! 🚀")
        else:
            st.session_state.logado = False
            st.error("🚫 E-mail não encontrado ou assinatura inativa.")

    # Status do Login
    if "logado" in st.session_state and st.session_state.logado:
        st.success("✅ Acesso Ativo")
    else:
        st.markdown("---")
        st.markdown("#### 🚀 Ainda não é membro?")
        st.markdown("Tenha e-mails ilimitados e suporte prioritário.")
        st.link_button(f"👉 Assinar por R$ 29,90/mês", LINK_ASSINATURA, use_container_width=True)
        st.caption("Cancele quando quiser. Acesso liberado após confirmação.")

# COLUNA 1: A Ferramenta (Só aparece se logado)
with col1:
    st.subheader("Gerador de Oportunidades")
    
    # Bloqueio Visual
    if "logado" not in st.session_state or not st.session_state.logado:
        st.info("🔒 **Ferramenta Bloqueada.** Faça login ao lado ou assine para começar.")
        st.markdown("---")
        # Blur effect (simulado)
        st.image("https://placehold.co/600x300/eeeeee/cccccc?text=Conteudo+Exclusivo+para+Assinantes", use_column_width=True)
    else:
        # Ferramenta Liberada
        target_url = st.text_input("Cole o site da empresa alvo:")
        
        if st.button("✨ Gerar Cold Mail", type="primary"):
            if not target_url:
                st.warning("Preciso de um site para ler!")
            else:
                with st.spinner("Lendo o site e pensando em estratégias..."):
                    res = scrape_website(target_url)
                    if res:
                        email_final = generate_cold_email(res)
                        st.markdown("### 🎯 Estratégia Gerada:")
                        st.markdown(email_final)
                    else:
                        st.error("Não consegui ler este site.")

st.divider()
st.caption("Painel Administrativo do SaaS v1.0")
