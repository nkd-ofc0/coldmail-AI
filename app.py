import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# --- 1. Configuração da Página (Visual mais largo e bonito) ---
st.set_page_config(page_title="ColdMail AI", page_icon="🚀", layout="centered")

# --- 2. Área de Segurança (Sua API Key fica aqui por enquanto) ---
# IMPORTANTE: Quando formos subir para o GitHub, vou te ensinar a tirar ela daqui para não vazar.
# Cole sua chave gsk_... dentro das aspas abaixo:
# Pega a chave dos "Segredos" do sistema (Configuraremos isso na nuvem)

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("🚨 Chave da API não encontrada! Configure os 'Secrets' no Streamlit Cloud.")
    st.stop()

# Agora a senha vem do Cofre, ninguém vê no código
try:
    SENHA_MESTRA = st.secrets["SENHA_DO_CLIENTE"]
except Exception:
    st.error("🚨 Configuração incompleta: Senha não definida nos Secrets.")
    st.stop()

# --- 3. Funções do Backend ---
def scrape_website(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Pega apenas texto relevante, ignorando menus e rodapés grandes
        text_elements = soup.find_all(['h1', 'h2', 'p', 'li', 'h3'])
        text = " ".join([t.get_text() for t in text_elements])
        return text[:6000] # Aumentei um pouco o limite de leitura
    except Exception:
        return None

def generate_cold_email(context_text):
    client = Groq(api_key=GROQ_API_KEY)
    
    # PROMPT AVANÇADO (Engenharia de Prompt)
    prompt = f"""
    Você é um especialista em Copywriting B2B e Vendas Consultivas.
    Analise os dados da empresa prospecto abaixo e crie 3 abordagens de e-mail frio (Cold Mail).
    
    DADOS DA EMPRESA ALVO:
    {context_text}
    
    DIRETRIZES OBRIGATÓRIAS:
    1. Tom de voz: Profissional, porém conversacional (nada de "Prezados", "Venho por meio desta").
    2. Foco: Use a estrutura "Gancho Personalizado -> Dor Possível -> Convite para conversa".
    3. Tamanho: Mantenha curto (máximo 4 parágrafos curtos).
    4. Idioma: Português do Brasil.
    
    SAÍDA ESPERADA (3 OPÇÕES):
    Opção 1: Focada em uma novidade ou conquista recente da empresa (ou missão deles).
    Opção 2: Focada em eficiência operacional (redução de custos/tempo).
    Opção 3: Uma abordagem "soft" (pergunta curiosa sobre o mercado deles).
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Modelo mais inteligente
            temperature=0.7 # Criatividade calibrada
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"

# --- 4. Interface (Frontend) ---

# Cabeçalho Estiloso
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🚀 ColdMail AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Transforme qualquer site em uma oportunidade de venda em segundos.</p>", unsafe_allow_html=True)
st.divider()

# Barra Lateral (Login)
with st.sidebar:
    st.header("🔐 Acesso Restrito")
    senha = st.text_input("Digite sua chave de acesso", type="password")
    st.info("Dúvidas? Suporte no WhatsApp: (21) 97740-2510")

# Trava de Segurança
if senha != SENHA_MESTRA:
    st.warning("⚠️ Por favor, insira a senha para desbloquear a ferramenta.")
    st.stop()

# Área Principal (Só aparece se a senha estiver certa)
col1, col2 = st.columns([3, 1])
with col1:
    target_url = st.text_input("Site da Empresa (URL)", placeholder="ex: www.ambev.com.br")
with col2:
    st.write("") # Espaço vazio para alinhar
    st.write("") 
    btn_gerar = st.button("✨ Gerar E-mails", use_container_width=True)

if btn_gerar:
    if not target_url:
        st.toast("❌ Digite uma URL primeiro!")
    elif "COLE_SUA_CHAVE" in GROQ_API_KEY:
         st.error("🚨 ERRO: O dono do software esqueceu de configurar a API Key no código.")
    else:
        with st.spinner("🕵️‍♂️ Lendo o site e criando estratégias..."):
            site_content = scrape_website(target_url)
            
            if site_content:
                result = generate_cold_email(site_content)
                
                st.success("Análise concluída! Aqui estão suas opções:")
                st.markdown("---")
                
                # Caixa bonita para o resultado
                with st.container(border=True):
                    st.markdown(result)
            else:
                st.error("Não consegui ler o site. Verifique se o endereço está correto ou se o site tem bloqueios de segurança.")

# Rodapé
st.markdown("---")

st.caption("Desenvolvido para Alavancagem de Vendas B2B. Todos os direitos reservados.")
