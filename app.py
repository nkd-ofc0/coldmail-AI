import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from datetime import datetime


st.set_page_config(page_title="ColdMail AI - Pro", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    /* Título Principal */
    .hero-title { 
        font-size: 3.5rem; 
        font-weight: 800; 
        text-align: center; 
        background: -webkit-linear-gradient(45deg, #1E88E5, #00C853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    /* Subtítulo */
    .hero-sub { 
        font-size: 1.2rem; 
        text-align: center; 
        color: #888; 
        margin-bottom: 30px; 
    }
    /* Rodapé */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #888;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)


try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    
    lista_bruta = st.secrets["CLIENTES_ATIVOS"]
    CLIENTES_ATIVOS = [email.strip().lower() for email in lista_bruta.split(",")]
except Exception:
    CLIENTES_ATIVOS = []
    GROQ_API_KEY = ""

LINK_ASSINATURA = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=ced44fcee7874a52a0ab583c6adec25d"


def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if not url.startswith('http'): url = 'https://' + url
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = " ".join([t.get_text() for t in soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])])
        return text[:5000]
    except: return None

def generate_cold_email(context):
    if not GROQ_API_KEY: return "Erro: Chave de API não configurada."
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Aja como um Especialista em Vendas B2B. Escreva um Cold Email curto e impossível de ignorar.
    DADOS DO PROSPECTO: {context}
    ESTRUTURA: Assunto Curto -> Conexão (li sobre vocês) -> Dor -> Convite.
    Tom: Profissional e direto. Português BR.
    """
    try:
        chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        return chat.choices[0].message.content
    except Exception as e: return f"Erro na IA: {str(e)}"


st.markdown("<h1 class='hero-title'>ColdMail AI 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>A Inteligência Artificial que prospecta por você enquanto você dorme.</p>", unsafe_allow_html=True)


c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("### ⚡ Velocidade")
        st.caption("A IA lê o site do cliente e escreve o e-mail perfeito em 3 segundos.")
with c2:
    with st.container(border=True):
        st.markdown("### 🎯 Personalização")
        st.caption("Chega de Ctrl+C Ctrl+V. Cada e-mail é único e focado na dor do cliente.")
with c3:
    with st.container(border=True):
        st.markdown("### 💰 Mais Vendas")
        st.caption("Quem responde rápido e com qualidade, fecha 3x mais contratos.")

st.divider()


col_app, col_login = st.columns([2, 1])


with col_app:
    st.subheader("Gerador de Oportunidades")
    
    
    if "email_usuario" not in st.session_state: st.session_state.email_usuario = None
    logado = st.session_state.email_usuario in CLIENTES_ATIVOS

    if logado:
        st.success(f"🟢 Acesso Ativo: {st.session_state.email_usuario}")
        url = st.text_input("Site do Cliente:", placeholder="Ex: www.tesla.com")
        
        if st.button("✨ Gerar Estratégia", type="primary"):
            if not url: st.warning("Cole um site primeiro.")
            else:
                with st.spinner("Analisando negócio..."):
                    txt = scrape_website(url)
                    if txt:
                        email = generate_cold_email(txt)
                        st.markdown("### 📧 Resultado:")
                        st.info(email)
                    else: st.error("Site inacessível.")
    else:
        
        st.markdown("""
        <div style='filter: blur(4px); pointer-events: none; opacity: 0.5;'>
            <p>Cole o site aqui...</p>
            <input type='text' style='width:100%; padding:10px; margin-bottom:10px;'>
            <button style='width:100%; background:grey; color:white; border:none; padding:10px;'>Gerar</button>
            <br><br>
            <div style='height:150px; background:#eee;'></div>
        </div>
        """, unsafe_allow_html=True)
        st.warning("🔒 Ferramenta exclusiva para assinantes.")


with col_login:
    
    with st.container(border=True):
        st.markdown("### 🔐 Área do Membro")
        email_input = st.text_input("E-mail de Acesso", key="login_email").strip().lower()
        
        if st.button("Entrar", use_container_width=True):
            if email_input in CLIENTES_ATIVOS:
                st.session_state.email_usuario = email_input
                st.rerun()
            else:
                st.error("Assinatura não encontrada.")
        
        st.markdown("---")
        
        
        st.markdown("#### 🚀 Aumente suas vendas hoje")
        st.caption("Tenha acesso ilimitado à IA mais poderosa de vendas do mercado.")
        
        
        st.markdown("<h2 style='text-align:center; color:#00C853; margin:0;'>R$ 29,90<span style='font-size:1rem; color:#888'>/mês</span></h2>", unsafe_allow_html=True)
        
        st.link_button("👉 ASSINAR AGORA", LINK_ASSINATURA, type="primary", use_container_width=True)
        st.caption("Cancela quando quiser. Acesso imediato.")


st.markdown("<br><br><br>", unsafe_allow_html=True) # Espaço extra
st.markdown(f"""
<div class='footer'>
    ColdMail AI © {datetime.now().year} • Desenvolvido para Vendedores de Elite • <a href='#' style='color:#888;'>Termos de Uso</a>
</div>
""", unsafe_allow_html=True)

