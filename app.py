import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# --- Configuração da Página (Aba do Navegador) ---
st.set_page_config(page_title="ColdMail AI - Pro", page_icon="🚀", layout="wide")

# --- CSS Personalizado (Para ficar bonito em qualquer tema) ---
st.markdown("""
<style>
    .hero-title { font-size: 3.5rem !important; font-weight: 800; text-align: center; color: #1E88E5; margin-bottom: 0; }
    .hero-sub { font-size: 1.3rem; text-align: center; color: #666; margin-bottom: 2rem; }
    .feature-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-bottom: 10px; }
    .feature-title { font-weight: bold; color: #333; font-size: 1.1rem; }
    .feature-text { color: #555; font-size: 0.9rem; }
    .login-box { background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #eee; }
    .price-tag { font-size: 1.8rem; font-weight: bold; color: #28a745; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- Configuração dos Segredos (Backend) ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    # Lista de clientes permitidos (separados por vírgula nos Secrets)
    lista_bruta = st.secrets["CLIENTES_ATIVOS"]
    CLIENTES_ATIVOS = [email.strip().lower() for email in lista_bruta.split(",")]
except Exception:
    # Fallback para não quebrar se esquecer de configurar
    CLIENTES_ATIVOS = [] 
    GROQ_API_KEY = ""

# --- Link do Plano de Assinatura (Mercado Pago) ---
LINK_ASSINATURA = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=SEU_LINK_AQUI"

# --- Funções da Ferramenta ---
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if not url.startswith('http'): url = 'https://' + url
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Limpa e pega só o texto relevante
        text = " ".join([t.get_text() for t in soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])])
        return text[:5000]
    except: return None

def generate_cold_email(context):
    if not GROQ_API_KEY: return "Erro: Chave de API não configurada."
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Aja como um Especialista em Vendas B2B. Escreva uma abordagem de Cold Email (E-mail Frio) para um potencial cliente.
    
    DADOS DO PROSPECTO (Extraídos do site):
    {context}
    
    OBJETIVO: Vender serviços de marketing/tecnologia.
    ESTRUTURA:
    1. Assunto: Curto e intrigante (sem cara de spam).
    2. Corpo: Gancho personalizado (mostre que leu o site) -> Dor possível -> Convite suave para conversa.
    3. Tom: Profissional mas acessível. Português do Brasil.
    
    Gere apenas 1 opção perfeita.
    """
    try:
        chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        return chat.choices[0].message.content
    except Exception as e: return f"Erro na IA: {str(e)}"

# ================= INTERFACE VISUAL =================

# 1. HERO SECTION (A Promessa)
st.markdown("<div class='hero-title'>🚀 ColdMail AI</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Pare de mandar spam. Use I.A. para escrever e-mails que <b>vendem</b>.</div>", unsafe_allow_html=True)

st.divider()

# 2. ÁREA PRINCIPAL (Dividida em 2 Colunas: Ferramenta vs Login)
col_app, col_login = st.columns([1.8, 1])

# --- LADO ESQUERDO: A FERRAMENTA ---
with col_app:
    st.subheader("🎯 Gerador de Oportunidades")
    
    # Verifica Login
    if "email_usuario" not in st.session_state:
        st.session_state.email_usuario = None
    
    usuario_logado = st.session_state.email_usuario in CLIENTES_ATIVOS

    if usuario_logado:
        # --- MODO LOGADO (Ferramenta Ativa) ---
        st.success(f"✅ Logado como: {st.session_state.email_usuario}")
        
        url_alvo = st.text_input("Site do Cliente Alvo:", placeholder="Ex: www.empresa.com.br")
        if st.button("✨ Gerar E-mail Vendedor", type="primary", use_container_width=True):
            if not url_alvo:
                st.warning("Por favor, digite uma URL.")
            else:
                with st.spinner("🤖 A IA está lendo o site e criando a estratégia..."):
                    texto_site = scrape_website(url_alvo)
                    if texto_site:
                        email_pronto = generate_cold_email(texto_site)
                        st.markdown("### 📧 Rascunho Gerado:")
                        st.info(email_pronto)
                        st.caption("Dica: Copie, ajuste os detalhes finais e envie.")
                    else:
                        st.error("Não consegui acessar esse site. Tente outro.")
        
        if st.button("Sair / Logout"):
            st.session_state.email_usuario = None
            st.rerun()
            
    else:
        # --- MODO BLOQUEADO (Visitante) ---
        st.markdown("""
        <div style='filter: blur(3px); opacity: 0.6; pointer-events: none; user-select: none;'>
            <p>Cole o site aqui...</p>
            <div style='background:#eee; height: 40px; margin-bottom:10px; border-radius:5px;'></div>
            <button style='background:#ccc; border:none; color:white; padding:10px; width:100%; border-radius:5px;'>Gerar E-mail</button>
            <br><br>
            <h3>Resultado:</h3>
            <div style='background:#f9f9f9; height: 200px; border-radius:5px;'></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("🔒 **Ferramenta Bloqueada.** Faça login ou assine para desbloquear a IA.")

# --- LADO DIREITO: LOGIN E VENDA ---
with col_login:
    # Caixa de Login com Design
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center; color:#333;'>Área do Assinante 👤</h3>", unsafe_allow_html=True)
    
    email_input = st.text_input("Seu E-mail de Acesso", key="input_email").strip().lower()
    
    if st.button("Entrar", use_container_width=True):
        if email_input in CLIENTES_ATIVOS:
            st.session_state.email_usuario = email_input
            st.toast("Login realizado com sucesso!", icon="🎉")
            st.rerun()
        else:
            st.error("E-mail não encontrado ou assinatura inativa.")
    
    st.markdown("---")
    
    # Área de Venda (Copywriting)
    st.markdown("<h4 style='text-align:center; color:#1E88E5;'>Ainda não tem acesso?</h4>", unsafe_allow_html=True)
    
    # Benefícios Rápidos
    st.markdown("""
    <div style='margin-bottom: 15px;'>
        <span style='color:green'>✔</span> Gerações Ilimitadas<br>
        <span style='color:green'>✔</span> Acesso Imediato<br>
        <span style='color:green'>✔</span> Cancele quando quiser
    </div>
    """, unsafe_allow_html=True)
    
    # Preço
    st.markdown("<div class='price-tag'>R$ 29,90<small style='font-size:1rem; color:#666'>/mês</small></div>", unsafe_allow_html=True)
    
    # Botão de Compra
    st.link_button("👉 Assinar Agora (Liberação Rápida)", LINK_ASSINATURA, type="primary", use_container_width=True)
    
    st.caption("Pagamento seguro via Mercado Pago. Acesso liberado após confirmação.")
    
    st.markdown("</div>", unsafe_allow_html=True) # Fecha login-box

st.divider()

# 3. RODAPÉ COM PROVA SOCIAL (Design de 3 Colunas)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='feature-box'><div class='feature-title'>⚡ Velocidade</div><div class='feature-text'>Economize horas de pesquisa manual. A IA lê o site em segundos.</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='feature-box'><div class='feature-title'>🎯 Precisão</div><div class='feature-text'>Ganchos personalizados que provam que você conhece o cliente.</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='feature-box'><div class='feature-title'>💰 ROI Alto</div><div class='feature-text'>Uma venda fechada paga a ferramenta por anos.</div></div>", unsafe_allow_html=True)
