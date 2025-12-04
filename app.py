import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import PyPDF2
import pdfplumber
import io
import urllib.parse
import os
import random
from datetime import datetime, timedelta
import base64
import tempfile
import re
from openai import OpenAI
from helpers.loader import load_data
from graphs.graphs import criar_grafico_velocimetro, criar_grafico_conteudos_prioritarios
from gamefic.game import inicializar_sistema_gamificacao, verificar_conquistas, atualizar_pontuacao, exibir_widget_gamificacao  


# =============================================================================
# INITIAL CONFIGURATION
# =============================================================================

# Streamlit page configuration
st.set_page_config(
    page_title="Learning Platform - 3rd Grade",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def setup_openai():
    """Detects OpenAI API key availability from 3 sources"""
    try:
        # Priority: Secrets > Env > Session
        if 'OPENAI_API_KEY' in st.secrets:
            return True, "Configured via Streamlit Secrets"
        
        if os.getenv('OPENAI_API_KEY'):
            return True, "Configured via environment variable"
        
        if st.session_state.get('openai_api_key'):
            return True, "Configured via manual input"
        
        return False, "No API key configured"
    except Exception as e:
        return False, f"Configuration error: {str(e)}"

OPENAI_AVAILABLE, OPENAI_STATUS = setup_openai()

# =============================================================================
# THEMES AND COLORS
# =============================================================================

COLORS = {
    'primary': '#4f46e5',
    'secondary': '#7c3aed',
    'success': '#10b981',
    'info': '#3b82f6',
    'warning': '#ffc107',
    'danger': '#ff6b6b',
    'green_dark': '#2e7d32',
    'green_light': '#4caf50',
    'bg_light': "#d8dbdf",
    'bg_white': '#ffffff',
    'text_dark': "#000000",
    'text_light': '#ffffff',
    'border_light': "#ffffff",
}

# =============================================================================
# OPTIMIZED CUSTOM CSS
# =============================================================================

CSS_STYLES = f'''
<style>
    /* ===== VARIABLES AND RESET ===== */
    :root {{
        --primary: {COLORS['primary']};
        --secondary: {COLORS['secondary']};
        --success: {COLORS['success']};
        --info: {COLORS['info']};
        --warning: {COLORS['warning']};
        --danger: {COLORS['danger']};
        --text-dark: {COLORS['text_dark']};
        --bg-light: {COLORS['bg_light']};
    }}
    
    .main {{ background: {COLORS['bg_light']}; }}
    .stApp {{ background: {COLORS['bg_white']}; }}
    
    .main * {{ color: {COLORS['text_dark']} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, li {{ color: {COLORS['text_dark']} !important; }}
    div {{ color: {COLORS['bg_light']} !important; }}
    h1, h2, h3 {{ font-weight: 700 !important; }}

    /* ===== DARK CONTAINERS ===== */
    .ra-input-container, .ra-input-container *,
    .questionario-card, .questionario-card *,
    .meta-card, .meta-card * {{ color: {COLORS['text_dark']} !important; }}

    /* ===== INPUTS ON DARK BACKGROUNDS ===== */
    .ra-input-container .stTextInput input, .ra-input-container input,
    .questionario-card .stTextInput input, .questionario-card input,
    .meta-card .stTextInput input, .meta-card input {{
        background: rgba(255,255,255,0.12) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        padding: 6px 10px !important;
        border-radius: 6px !important;
        caret-color: white !important;
    }}

    .ra-input-container .stTextInput input::placeholder,
    .questionario-card .stTextInput input::placeholder,
    .meta-card .stTextInput input::placeholder {{
        color: {COLORS['text_light']} !important;
    }}

    /* ===== CARDS ===== */
    .main-card {{
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin: 15px 0;
        border-left: 5px solid var(--primary); border: 1px solid {COLORS['border_light']};
    }}
    
    .metric-card {{
        background: white; padding: 20px; border-radius: 10px; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid {COLORS['border_light']};
    }}
    
    .subject-card {{
        background: white; padding: 20px; border-radius: 10px; margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid {COLORS['border_light']};
        border-top: 4px solid;
    }}
    
    .portuguese-card {{ border-top-color: {COLORS['success']}; }}
    .math-card {{ border-top-color: {COLORS['info']}; }}

    /* ===== HEADERS ===== */
    .welcome-header {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important; padding: 30px; border-radius: 15px;
        margin-bottom: 20px; text-align: center;
    }}
    .welcome-header h1, .welcome-header p {{ color: white !important; }}

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 5px; background: {COLORS['bg_light']};
        padding: 10px; border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: white; border-radius: 8px; padding: 12px 20px;
        border: 1px solid {COLORS['text_dark']}; font-weight: 600;
        color: {COLORS['text_dark']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: var(--primary) !important; color: white !important;
        border-color: var(--primary) !important;
    }}

    /* ===== BUTTONS AND INPUTS ===== */
    .stButton>button {{
        background: var(--primary); color: white; border: none;
        border-radius: 8px; padding: 10px 20px; font-weight: 600;
    }}
    
    .stTextInput>div>div>input {{
        border-radius: 8px; border: 2px solid {COLORS['border_light']};
        padding: 12px; color: {COLORS['bg_light']} !important;
    }}

    /* ===== CHAT ===== */
    .user-message {{
        background: var(--primary); color: white !important; padding: 15px;
        border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%;
        margin-left: auto;
    }}
    
    .lu-message, .professor-message {{
        padding: 15px; border-radius: 18px 18px 18px 0; margin: 10px 0;
        max-width: 80%; margin-right: auto; position: relative;
    }}
    
    .lu-message {{
        background: #f1f5f9; color: {COLORS['text_dark']} !important;
        border: 1px solid #e2e8f0;
    }}
    
    .professor-message {{
        background: #e8f5e8; color: {COLORS['text_dark']} !important;
        border: 1px solid #c8e6c9;
    }}

    /* ===== AVATARS ===== */
    .lu-avatar, .professor-avatar {{
        display: flex; align-items: center; margin-bottom: 8px;
    }}
    
    .lu-name {{ font-weight: bold; color: var(--secondary) !important; margin-left: 8px; }}
    .professor-name {{ font-weight: bold; color: {COLORS['green_dark']} !important; margin-left: 8px; }}

    .lu-avatar-img, .professor-avatar-img {{
        width: 40px; height: 40px; border-radius: 50%; object-fit: cover;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: bold; font-size: 16px;
    }}
    
    .lu-avatar-img {{
        border: 2px solid var(--secondary);
        background: linear-gradient(135deg, var(--secondary), var(--primary));
    }}
    
    .professor-avatar-img {{
        border: 2px solid {COLORS['green_dark']};
        background: linear-gradient(135deg, {COLORS['green_light']}, {COLORS['green_dark']});
    }}

    /* ===== SECTIONS ===== */
    .professor-section {{
        background: #f1f8e9; padding: 20px; border-radius: 12px;
        margin: 20px 0; border-left: 5px solid {COLORS['green_light']};
    }}
    
    .professor-question {{
        background: #e8f5e8; padding: 15px; border-radius: 10px;
        margin: 10px 0; border-left: 4px solid {COLORS['green_light']};
    }}

    /* ===== SPECIAL CARDS ===== */
    .meta-card {{
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important; padding: 20px; border-radius: 10px; margin: 10px 0;
    }}
    
    .meta-card h4, .meta-card p {{ color: white !important; }}
    
    .dica-card {{ background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {COLORS['green_light']}; }}
    .estrategia-card {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid var(--warning); }}
    .prioridade-card {{ background: #ffeaa7; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #fdcb6e; }}
    .conteudo-prioritario {{ background: {COLORS['bg_light']}; padding: 15px; border-radius: 8px; margin: 8px 0; border-left: 4px solid var(--danger); }}
    .estrategia-item {{ background: {COLORS['bg_light']}; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid var(--primary); }}

    /* ===== GRAPHS ===== */
    .plotly-graph-div, .js-plotly-plot .plotly {{ height: 400px !important; }}

    /* ===== ANIMATIONS ===== */
    @keyframes dots {{
        0%, 20% {{ content: ''; }} 40% {{ content: '.'; }} 60% {{ content: '..'; }} 80%, 100% {{ content: '...'; }}
    }}
    
    @keyframes flutuando {{
        0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }}
    }}

    /* ===== FIXED AVATAR ===== */
    .lu-avatar-fixed {{
        position: fixed; right: 20px; top: 50%; transform: translateY(-50%); z-index: 9999;
        display: flex; flex-direction: column; align-items: center; gap: 10px;
        background: white; padding: 15px; border-radius: 15px; cursor: pointer;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.3); border: 2px solid var(--secondary);
        animation: flutuando 3s ease-in-out infinite; transition: all 0.3s ease;
    }}
    
    .lu-avatar-fixed:hover {{
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.5); transform: translateY(-50%) scale(1.05);
    }}
    
    .lu-avatar-fixed-inner {{
        width: 100px; height: 100px; border-radius: 50%;
        background: linear-gradient(135deg, var(--secondary), var(--primary));
        display: flex; align-items: center; justify-content: center;
        border: 3px solid var(--secondary); color: white;
        font-size: 2.5em; font-weight: bold;
    }}
    
    .lu-avatar-label {{
        font-size: 0.85em; font-weight: bold; color: var(--secondary) !important;
        text-align: center; white-space: nowrap;
    }}

    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {{
        .lu-avatar-fixed {{ right: 10px; top: auto; bottom: 10px; transform: translateY(0); }}
        .lu-avatar-fixed:hover {{ transform: scale(1.05); }}
        .lu-avatar-fixed-inner {{ width: 80px; height: 80px; font-size: 1.8em; }}
    }}
</style>
'''

st.markdown(CSS_STYLES, unsafe_allow_html=True)
@st.cache_data

# =============================================================================
# NEW SYSTEM: AI PROFESSOR WITH SPECIFIC COMMENTED ANSWERS
# =============================================================================

def extrair_file_id_gdrive(url):
    """Robustly extracts file ID from Google Drive URL"""
    
    patterns = [
        r"/d/([a-zA-Z0-9_-]{33,44})",
        r"id=([a-zA-Z0-9_-]{33,44})",
        r"open\?id=([a-zA-Z0-9_-]{33,44})",
        r"file/d/([a-zA-Z0-9_-]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def ler_pdf_gdrive_direto(url):
    """Reads PDF directly from Google Drive with improved method"""
    try:
        file_id = extrair_file_id_gdrive(url)
        if not file_id:
            print("❌ Could not extract file ID")
            return None
        
        # URL for direct download
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        # Download with longer timeout
        response = requests.get(download_url, headers=headers, timeout=45)
        response.raise_for_status()
        
        # Check if it's PDF
        content_type = response.headers.get('content-type', '').lower()
        is_pdf = 'pdf' in content_type or response.content[:4] == b'%PDF'
        
        if not is_pdf:
            # Might be an HTML page (Google Drive asking for confirmation)
            if 'text/html' in content_type and 'google' in response.text.lower():
                # Try to extract real download link
                match = re.search(r'confirm=([^&]+)', response.text)
                if match:
                    confirm_code = match.group(1)
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_code}"
                    response = requests.get(download_url, headers=headers, timeout=45)
                    response.raise_for_status()
        
        # Process in memory
        pdf_file = io.BytesIO(response.content)
        
        # First try with pdfplumber (more robust)
        try:
            with pdfplumber.open(pdf_file) as pdf:
                texto = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        texto += f"--- Page {i+1} ---\n{page_text}\n\n"
                
                if texto.strip():
                    return texto
        except:
            pass
        
        # Fallback to PyPDF2
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            texto = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    texto += f"--- Page {i+1} ---\n{page_text}\n\n"
            
            return texto if texto.strip() else None
        except:
            return None
            
    except Exception as e:
        print(f"❌ Error reading PDF from Google Drive: {e}")
        return None

def extrair_conteudo_pedagogico_avancado(texto_pdf):
    """Extracts pedagogical sections from PDF in advanced way"""
    
    if not texto_pdf:
        return None
    
    conteudo_estruturado = {
        "habilidade": "",
        "conteudo": "",
        "passo_1": "",
        "passo_2": "",
        "passo_3": "",
        "texto_completo": texto_pdf[:3000],  # Limit size
        "resposta_comentada": "",
        "explicacao": ""
    }
    
    texto_lower = texto_pdf.lower()
    
    # 1. Extract SKILL (common patterns)
    padroes_habilidade = [
        r"(?i)habilidade\s*[:\-]\s*(.*?)(?=\n|\.|$)",
        r"(?i)compet[êe]ncia\s*[:\-]\s*(.*?)(?=\n|\.|$)",
        r"(?i)h[aá]bil\s*[:\-]\s*(.*?)(?=\n|\.|$)",
        r"(?i)\(EM\d+MAT\d+\)\s*(.*?)(?=\n|\.|$)",
        r"(?i)\(EM\d+L[P]?T\d+\)\s*(.*?)(?=\n|\.|$)"
    ]
    
    for padrao in padroes_habilidade:
        match = re.search(padrao, texto_pdf, re.IGNORECASE | re.DOTALL)
        if match:
            conteudo_estruturado["habilidade"] = match.group(1).strip()
            break
    
    # 2. Extract COMMENTED ANSWER (main)
    padroes_resposta = [
        r"(?i)resposta\s+comentada\s*(.*?)(?=\n[A-ZÀ-Ÿ]{3,}|$|\n\d+\.|\nQuestão|\nExercício)",
        r"(?i)coment[áa]rios\s*(.*?)(?=\n[A-ZÀ-Ÿ]{3,}|$|\n\d+\.|\nQuestão)",
        r"(?i)resolu[çc][ãa]o\s*(.*?)(?=\n[A-ZÀ-Ÿ]{3,}|$|\n\d+\.|\nQuestão)",
        r"(?i)explica[çc][ãa]o\s*(.*?)(?=\n[A-ZÀ-Ÿ]{3,}|$|\n\d+\.|\nQuestão)"
    ]
    
    for padrao in padroes_resposta:
        match = re.search(padrao, texto_pdf, re.DOTALL | re.IGNORECASE)
        if match:
            conteudo_estruturado["resposta_comentada"] = match.group(1).strip()[:2000]
            break
    
    # 3. Extract CONTENT
    padroes_conteudo = [
        r"(?i)conte[úu]do\s*[:\-]\s*(.*?)(?=\n|\.|$)",
        r"(?i)t[óo]pico\s*[:\-]\s*(.*?)(?=\n|\.|$)",
        r"(?i)assunto\s*[:\-]\s*(.*?)(?=\n|\.|$)"
    ]
    
    for padrao in padroes_conteudo:
        match = re.search(padrao, texto_pdf, re.IGNORECASE)
        if match:
            conteudo_estruturado["conteudo"] = match.group(1).strip()
            break
    
    # 4. Extract steps (if any)
    for i in range(1, 4):
        padrao_passo = rf"(?i)passo\s*{i}[:\-\.]\s*(.*?)(?=Passo\s*{i+1}|$|\n[A-Z])"
        match = re.search(padrao_passo, texto_pdf, re.DOTALL | re.IGNORECASE)
        if match:
            conteudo_estruturado[f"passo_{i}"] = match.group(1).strip()[:500]
    
    # 5. Extract general explanation (fallback)
    if not conteudo_estruturado["resposta_comentada"]:
        # Get explanatory passages
        explicacoes = re.findall(r'(?i)(?:explica[çc][ãa]o|resolu[çc][ãa]o|como resolver|passo a passo).*?(?=\n[A-Z]|$)', 
                                texto_pdf, re.DOTALL)
        if explicacoes:
            conteudo_estruturado["explicacao"] = ' '.join(explicacoes)[:1500]
    
    return conteudo_estruturado

def criar_prompt_professor_ia(conteudo_estruturado, pergunta_aluno, disciplina, numero_questao):
    """Creates specialized prompt for AI Professor"""
    
    prompt = f"""YOU ARE: FABI, a high school {disciplina.upper()} specialist teacher

⚠️ CRITICAL CONTEXT - READ CAREFULLY:
You are helping with QUESTION {numero_questao} of {disciplina.upper()}
IGNORE any content from other subjects or questions in the attached material
FOCUS SOLELY on this specific question: Question {numero_questao} of {disciplina.upper()}

KNOWLEDGE BASE - QUESTION {numero_questao} ({disciplina.upper()}):
• Skill assessed: {conteudo_estruturado.get('habilidade', 'Not specified')}
• Main content: {conteudo_estruturado.get('conteudo', 'Not specified')}
• Commented solution: {conteudo_estruturado.get('resposta_comentada', '')[:1000]}
• Pedagogical explanation: {conteudo_estruturado.get('explicacao', '')[:800]}

MANDATORY INSTRUCTIONS - FOLLOW STRICTLY:
1. ✅ ANSWER ABOUT QUESTION {numero_questao} OF {disciplina.upper()} ONLY
2. ✅ DO NOT answer about other subjects or unrelated formulas
3. ✅ If the question mentions concepts from another subject, redirect to {disciplina.upper()}
4. ✅ USE THE OFFICIAL material of the question as main source
5. ✅ ANSWER DIRECTLY - without preliminaries or introductions
6. ✅ BE COMPLETE but CONCISE - all necessary information at once
7. ✅ EXPLAIN AS A TEACHER - clear, step by step, with examples
8. ✅ GIVE PRACTICAL TIPS - avoid common mistakes
9. ✅ SHOW THE COMPLETE reasoning
10. ✅ MANDATORY: Use UNICODE SYMBOLS in ALL mathematical formulas

FORMATTING FOR ANSWERS - MANDATORY:
📐 Mathematics: ALWAYS use UNICODE SYMBOLS - NEVER use LaTeX or $:
   • Multiplication: use × (example: 3 × 4 = 12)
   • Division: use ÷ (example: 12 ÷ 3 = 4)
   • Power: use ² ³ ⁴ (example: 5² = 25, 2³ = 8)
   • Square root: use √ (example: √16 = 4)
   • Pi: use π (example: 2πr for circumference)
   • Degrees: use ° (example: 90°)
   • Approximately: use ≈ (example: π ≈ 3.14)
   • Plus/Minus: use ± (example: x = 5 ± 2)
   • Inequalities: use ≤ ≥ (example: x ≤ 10)
📝 Portuguese: Use clear structure with numbered topics
🔢 Examples: With real numbers/words
💡 Tips: For memorization or avoiding mistakes

SUBJECT OF THIS ANSWER: {disciplina.upper()}
QUESTION: {numero_questao}
STUDENT'S QUESTION: {pergunta_aluno}

Answer as a {disciplina.upper()} teacher - WITHOUT LEAVING THE SCOPE OF QUESTION {numero_questao}:
"""
    
    return prompt

def perguntar_ao_professor_ia(pergunta, url_pdf_questao, disciplina, numero_questao):
    """Asks a specific question to AI Professor about a question"""
    
    if not OPENAI_AVAILABLE:
        return "⚠️ AI Professor is temporarily unavailable. Configure OpenAI to use this functionality."
    
    try:
        from openai import OpenAI
        
        # Get API key
        api_key = None
        if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
            api_key = st.session_state.openai_api_key
        elif 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
        else:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return "❌ OpenAI API key not configured."
        
        client = OpenAI(api_key=api_key)
        
        # 1. Read specific PDF of the question
        with st.spinner(f"📚 Reading material for question {numero_questao}..."):
            texto_pdf = ler_pdf_gdrive_direto(url_pdf_questao)
            
            if not texto_pdf:
                return f"❌ Could not access material for question {numero_questao}. The PDF may be unavailable."
        
        # 2. Extract pedagogical content
        with st.spinner("🔍 Analyzing commented answer..."):
            conteudo_estruturado = extrair_conteudo_pedagogico_avancado(texto_pdf)
            
            if not conteudo_estruturado or not any(conteudo_estruturado.values()):
                # Fallback: use complete text
                conteudo_estruturado = {
                    "texto_completo": texto_pdf[:2000],
                    "habilidade": f"Question {numero_questao} of {disciplina}",
                    "resposta_comentada": texto_pdf[:1500]
                }
        
        # 3. Create specialized prompt
        prompt = criar_prompt_professor_ia(conteudo_estruturado, pergunta, disciplina, numero_questao)
        
        # 4. Call OpenAI
        with st.spinner("👩‍🏫 Professor FABI is thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a high school {disciplina} specialist teacher. Be direct, complete and pedagogical. ALWAYS answer about {disciplina} questions. Use official material as main reference. If the question is about another subject, redirect to {disciplina}."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            resposta = response.choices[0].message.content.strip()
            
            # 5. VALIDATION: Check if answer is in correct subject
            palavras_chave_port = ['português', 'texto', 'leitura', 'interpretação', 'gramática', 'redação', 'literatura', 'sintaxe', 'semantica', 'semântica', 'coesão', 'coerência']
            palavras_chave_mat = ['matemática', 'fórmula', 'cálculo', 'equação', 'função', 'número', 'álgebra', 'geometria', 'trigonometria', 'estatística', 'probabilidade', 'área', 'perímetro']
            
            resposta_lower = resposta.lower()
            
            # If it's Portuguese question, validate answer doesn't focus on math
            if disciplina.lower() == 'português':
                palavras_mat_na_resp = sum(1 for p in palavras_chave_mat if p in resposta_lower)
                palavras_port_na_resp = sum(1 for p in palavras_chave_port if p in resposta_lower)
                
                # If has too much math and little Portuguese, might be error
                if palavras_mat_na_resp >= 3 and palavras_port_na_resp < 2:
                    st.warning("⚠️ Detected answer might be focusing on another subject. Trying again...")
                    # Try a second time with even more focused prompt
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": f"CRITICAL: You must answer ONLY about PORTUGUESE. Completely ignore any mathematical formula. Focus on: {', '.join(palavras_chave_port[:5])}"
                            },
                            {"role": "user", "content": f"Answering about QUESTION {numero_questao} of PORTUGUESE:\n{prompt}"}
                        ],
                        temperature=0.5,
                        max_tokens=800
                    )
                    resposta = response.choices[0].message.content.strip()
            
            # Add to AI Professor conversation history
            if 'professor_history' not in st.session_state:
                st.session_state.professor_history = []
            
            st.session_state.professor_history.append({
                "questao": numero_questao,
                "disciplina": disciplina,
                "pergunta": pergunta,
                "resposta": resposta,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            return resposta
            
    except Exception as e:
        print(f"❌ Error in AI Professor: {e}")
        return f"⚠️ There was an error processing your question. Details: {str(e)[:200]}"

def exibir_interface_professor_ia(numero_questao, disciplina, url_pdf, conteudo, unique_id=""):
    """Interface to ask questions to AI Professor about a specific question"""
    
    st.markdown(f'''
    <div class="professor-section">
        <h3>👩‍🏫 Professor FABI - Question {numero_questao}</h3>
        <p><strong>{conteudo}</strong> | {disciplina}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize history for this question
    questao_key = f"professor_q{numero_questao}_{unique_id}"
    if questao_key not in st.session_state:
        st.session_state[questao_key] = []
    
    # Show previous questions/answers for this question
    if st.session_state[questao_key]:
        st.markdown("#### 📝 Previous Conversation")
        for i, msg in enumerate(st.session_state[questao_key][-3:]):  # Show last 3
            if msg["role"] == "user":
                st.markdown(f'''
                <div class="user-message">
                    <strong>You:</strong> {msg["content"]}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="professor-message">
                    <div class="professor-avatar">
                        <div class="professor-avatar-img">P</div>
                        <span class="professor-name">AI Professor</span>
                    </div>
                ''', unsafe_allow_html=True)
                # Render answer with LaTeX support
                st.markdown(msg["content"])
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Input for new question
    st.markdown("#### 💭 Ask a question about this question")
    
    col_perg1, col_perg2 = st.columns([3, 1])
    
    with col_perg1:
        pergunta = st.text_input(
            f"Ask AI Professor about question {numero_questao}:",
            placeholder=f"Ex: How to solve step by step? Why was my answer wrong? Explain the concept of {conteudo.split(',')[0] if conteudo else '...'}",
            key=f"pergunta_q{numero_questao}_{unique_id}",
            label_visibility="collapsed"
        )
    
    with col_perg2:
        if st.button("🎯 Ask", key=f"btn_q{numero_questao}_{unique_id}", use_container_width=True):
            if pergunta.strip():
                # Add question to history
                st.session_state[questao_key].append({
                    "role": "user",
                    "content": pergunta,
                    "time": datetime.now().strftime("%H:%M")
                })
                
                # Get answer from AI Professor
                resposta = perguntar_ao_professor_ia(pergunta, url_pdf, disciplina, numero_questao)
                
                # Add answer to history
                st.session_state[questao_key].append({
                    "role": "assistant",
                    "content": resposta,
                    "time": datetime.now().strftime("%H:%M")
                })
                
                # 🎮 Update gamification score
                atualizar_pontuacao('pergunta_professor', st=st)
                
                # Show answer IMMEDIATELY (outside render loop)
                st.markdown("---")
                st.markdown("### ✅ FABI's Answer")
                st.markdown(resposta)
            else:
                st.warning("Type a question first!")
    
    # Question suggestions
    st.markdown("""
    <div class="professor-question">
        <p><strong>💡 Question suggestions:</strong></p>
        <ul style="margin: 5px 0; padding-left: 20px;">
            <li>How to solve this question step by step?</li>
            <li>What is the main concept being tested?</li>
            <li>Why are the wrong alternatives incorrect?</li>
            <li>Give a similar example for me to practice</li>
            <li>Explain the formula/method used in the solution</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PERSONALIZED STUDY PLAN SYSTEM
# =============================================================================

def inicializar_sistema_plano_estudos():
    """Initializes study plan system in session"""
    if 'plano_estudos' not in st.session_state:
        st.session_state.plano_estudos = {
            'status': 'nao_criado',
            'dados_perfil': {},
            'plano_gerado': {},
            'data_criacao': None,
            'etapa_questionario': 1
        }

def coletar_respostas_questionario(aluno_nome):
    """Interface to collect answers from study plan questionnaire"""
    
    st.markdown(f'''
    <div class="main-card">
        <h2>📋 Questionnaire for Personalized Plan</h2>
        <p>Let's create a perfect plan for you, {aluno_nome}!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if 'etapa_questionario' not in st.session_state:
        st.session_state.etapa_questionario = 1
    
    etapa = st.session_state.etapa_questionario
    progresso = etapa / 5
    st.progress(progresso, text=f"Step {etapa} of 5")
    
    respostas = {}
    
    # STEP 1: AVAILABILITY
    if etapa == 1:
        st.markdown('<div class="plano-section"><h3>⏰ Your Availability</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            horas = st.slider("Hours/week for studying:", 1, 40, 10)
            dias = st.multiselect("Study days:", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], ["Mon", "Wed", "Fri"])
        with col2:
            horario = st.selectbox("Best time:", ["Morning", "Afternoon", "Evening", "Night"])
            tipo = st.selectbox("Duration:", ["Long (2-3h)", "Medium (1h)", "Pomodoros (25min)"])
        
        respostas = {'horas': horas, 'dias': dias, 'horario': horario, 'tipo': tipo}
    
    # STEP 2: GOALS
    elif etapa == 2:
        st.markdown('<div class="plano-section"><h3>🎯 Your Goals</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            tempo = st.selectbox("Preparation time:", ["1 month", "3 months", "6 months", "1 year"])
            disciplinas = st.multiselect("Priority subjects:", ["Portuguese", "Mathematics", "Writing"], ["Portuguese", "Mathematics"])
        with col2:
            nota = st.slider("Score goal:", 450, 1000, 650, 10)
            objetivo = st.text_input("Specific objective:", placeholder="Ex: Pass in Medicine...")
        
        respostas = {'tempo': tempo, 'disciplinas': disciplinas, 'nota': nota, 'objetivo': objetivo}
    
    # STEP 3: LEARNING STYLE
    elif etapa == 3:
        st.markdown('<div class="plano-section"><h3>🧠 Your Learning Style</h3></div>', unsafe_allow_html=True)
        estilo = st.radio("How do you learn best:", ["Videos", "Reading", "Exercises", "Groups", "Mind maps"])
        conc = st.slider("Concentration difficulty (1-10):", 1, 10, 5)
        ansiedade = st.select_slider("Test anxiety:", ["Confident", "Normal", "Anxious", "Very anxious"])
        respostas = {'estilo': estilo, 'conc': conc, 'ansiedade': ansiedade}
    
    # STEP 4: DIFFICULTIES
    elif etapa == 4:
        st.markdown('<div class="plano-section"><h3>⚠️ Your Difficulties</h3></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            dif_port = st.multiselect("Portuguese difficulties:", ["Interpretation", "Grammar", "Literature", "Writing"])
        with col2:
            dif_mat = st.multiselect("Mathematics difficulties:", ["Algebra", "Geometry", "Functions", "Statistics"])
        
        outras = st.text_area("Other difficulties:", placeholder="Describe...")
        respostas = {'dif_port': dif_port, 'dif_mat': dif_mat, 'outras': outras}
    
    # STEP 5: MOTIVATION
    elif etapa == 5:
        st.markdown('<div class="plano-section"><h3>💪 Motivation and Preferences</h3></div>', unsafe_allow_html=True)
        motivacao = st.slider("Motivation level (1-10):", 1, 10, 7)
        recompensa = st.selectbox("What motivates you:", ["Progress", "Rewards", "Competition", "Learning", "Deadlines"])
        recursos = st.multiselect("Preferred resources:", ["YouTube", "Booklets", "Apps", "Groups", "Mock tests"])
        respostas = {'motivacao': motivacao, 'recompensa': recompensa, 'recursos': recursos}
    
    # Navigation buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn1:
        if etapa > 1 and st.button("⬅️ Back", key=f"btn_voltar_{etapa}"):
            st.session_state.etapa_questionario -= 1
    
    with col_btn3:
        if etapa < 5:
            if st.button("Continue ➡️", type="primary", use_container_width=True, key=f"btn_continuar_{etapa}"):
                st.session_state.etapa_questionario += 1
        else:
            if st.button("✨ Generate Plan!", type="primary", use_container_width=True, key="btn_gerar_plano"):
                st.session_state.plano_estudos['status'] = 'criado'
                st.session_state.etapa_questionario = 1
                st.success("✅ Plan created successfully!")
    
    return respostas

def exibir_plano_estudos_gerado(aluno_data):
    """Displays generated study plan"""
    
    st.markdown('''
    <div class="main-card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
        <h2 style="color: white;">✨ Your Personalized Study Plan</h2>
    </div>
    ''', unsafe_allow_html=True)
    
    # Hour distribution
    st.markdown("### 📊 Weekly Hour Distribution")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📚 Portuguese", "4h")
    with col2:
        st.metric("🧮 Mathematics", "4h")
    with col3:
        st.metric("✍️ Writing", "2h")
    with col4:
        st.metric("🔁 Review", "3h")
    with col5:
        st.metric("📝 Mock tests", "2h")
    with col6:
        st.metric("📈 Total", "15h")
    
    # Immediate focus
    st.markdown("### 🎯 Immediate Focus (Next 2 Weeks)")
    
    col_foco1, col_foco2 = st.columns(2)
    
    with col_foco1:
        st.markdown('''
        <div class="conteudo-prioritario">
            <h4>📚 Portuguese</h4>
            <ul>
                <li>Text interpretation</li>
                <li>Figures of speech</li>
                <li>Commas and punctuation</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_foco2:
        st.markdown('''
        <div class="conteudo-prioritario">
            <h4>🧮 Mathematics</h4>
            <ul>
                <li>1st and 2nd degree functions</li>
                <li>Arithmetic progressions</li>
                <li>Plane geometry</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    # Goals
    st.markdown("### 🏆 Plan Goals")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="passo-plano">
            <h5>Short Term (1 month)</h5>
            <ul>
                <li>✅ Review 3 Portuguese contents</li>
                <li>✅ Review 3 Mathematics contents</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="passo-plano">
            <h5>Medium Term (3 months)</h5>
            <ul>
                <li>🎯 Increase 6 correct in Portuguese</li>
                <li>🎯 Increase 6 correct in Mathematics</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="passo-plano">
            <h5>Long Term (6 months)</h5>
            <ul>
                <li>🚀 Reach 800+ points</li>
                <li>🚀 Master main contents</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    # Weekly schedule
    st.markdown("### 📅 Suggested Weekly Schedule")
    
    dias = {
        "Monday": {"foco": "Portuguese", "horas": 3},
        "Wednesday": {"foco": "Mathematics", "horas": 3},
        "Friday": {"foco": "Mixed", "horas": 3}
    }
    
    for dia, info in dias.items():
        st.markdown(f'''
        <div class="dia-plano">
            <h5>📌 {dia} - {info['horas']}h</h5>
            <p><strong>Focus:</strong> {info['foco']}</p>
            <p><strong>Activities:</strong> Theory (1h) → Exercises (1h) → Review (1h)</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Strategies
    st.markdown("### 💡 Study Strategies")
    
    estrategias = [
        "Watch video lessons about contents with difficulty",
        "Use mind maps to organize knowledge",
        "Solve exercises similar to those you got wrong",
        "Practice with weekly mock tests"
    ]
    
    for est in estrategias:
        st.markdown(f'<div class="estrategia-item"><p>✨ {est}</p></div>', unsafe_allow_html=True)
    
    # Resources
    st.markdown("### 📚 Recommended Resources")
    
    recursos = [
        "**YouTube:** Professor Ferretto (Mathematics), Professor Noslen (Portuguese)",
        "**Booklets:** Poliedro, Bernoulli, Etapa",
        "**Mock tests:** Previous ENEM exams",
        "**Platform:** Use AI Professor for specific doubts"
    ]
    
    for rec in recursos:
        st.markdown(f'<div class="dica-card"><p>{rec}</p></div>', unsafe_allow_html=True)
    
    # Checkpoints
    st.markdown("### 🗓️ Progress Checkpoints")
    
    checkpoints = [4, 8, 12, 16, 24]
    
    for semana in checkpoints:
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"**Week {semana}**")
        
        with col2:
            st.markdown(f"Review progress and adjust plan")
        
        with col3:
            if st.button("✅ Complete", key=f"chk_{semana}", use_container_width=True):
                atualizar_pontuacao('checkpoint_plano', st=st)
                st.success(f"Week {semana} checkpoint completed!")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Update Plan", use_container_width=True, key="btn_atualizar_plano"):
            st.session_state.plano_estudos['status'] = 'nao_criado'
    
    with col2:
        if st.button("📥 Save (PDF)", use_container_width=True, key="btn_salvar_pdf"):
            st.info("📥 Export functionality in development!")
    
    with col3:
        if st.button("🎮 View Dashboard", use_container_width=True, key="btn_ver_dashboard"):
            # Go back to tab 1 (Dashboard)
            pass

def exibir_aba_plano_estudos(aluno_data):
    """Displays complete Study Plan tab"""
    
    inicializar_sistema_plano_estudos()
    
    status = st.session_state.plano_estudos['status']
    
    if status == 'nao_criado':
        # Initial screen
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f'''
            <div class="plano-section">
                <h3>✨ Hello, {aluno_data['nome']}!</h3>
                <p>A personalized study plan can increase your efficiency by <strong>up to 40%</strong>!</p>
                <h4>🎯 Benefits:</h4>
                <ul>
                    <li>✅ Focus on your real needs</li>
                    <li>✅ Achievable and adapted goals</li>
                    <li>✅ Strategies for your style</li>
                    <li>✅ Progress checkpoints</li>
                    <li>✅ +25 gamification points!</li>
                </ul>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="meta-card" style="text-align: center;">
                <h2 style="color: white;">🎯</h2>
                <h4 style="color: white;">Ready?</h4>
                <p style="color: white;">5 minutes!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("📝 Create Plan!", use_container_width=True, type="primary", key="btn_criar_plano"):
                st.session_state.plano_estudos['status'] = 'criando'
        
        # Statistics
        st.markdown("### 📊 Your Current Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Portuguese", f"{aluno_data['acertos_port']}/18")
        with col2:
            st.metric("🧮 Mathematics", f"{aluno_data['acertos_mat']}/18")
        with col3:
            st.metric("📝 Errors", aluno_data['erros_port'] + aluno_data['erros_mat'])
        with col4:
            # Count unique content from errors
            conteudos_totais = len(aluno_data['erros_port_df']['Conteúdo'].unique()) + len(aluno_data['erros_mat_df']['Conteúdo'].unique()) if not aluno_data['erros_port_df'].empty or not aluno_data['erros_mat_df'].empty else 0
            st.metric("🎯 Contents", conteudos_totais)
    
    elif status == 'criando':
        coletar_respostas_questionario(aluno_data['nome'])
    
    elif status == 'criado':
        exibir_plano_estudos_gerado(aluno_data)


# =============================================================================
# MAIN INTERFACE
# =============================================================================

# Main header
col_header1, col_header2, col_header3 = st.columns([1, 2, 1])
with col_header2:
    st.markdown('''
    <div class="welcome-header">
        <h1 style="color: white; margin: 0;">🎓 Learning Platform</h1>
        <p style="color: white; font-size: 1.2em; margin: 0;">3rd Grade - High School</p>
    </div>
    ''', unsafe_allow_html=True)

# OpenAI Configuration
with st.expander("⚙️ OpenAI Configuration (Required for AI Professor)"):
    st.info("Configure to activate AI Professor and analyses with commented answers")
    
    col_config1, col_config2 = st.columns([3, 1])
    
    with col_config1:
        api_key = st.text_input("OpenAI API Key:", type="password", 
                               placeholder="Paste your API key here...",
                               key="openai_api_key_input")
    
    with col_config2:
        if st.button("💾 Save Key", use_container_width=True, key="btn_salvar_api"):
            if api_key:
                st.session_state.openai_api_key = api_key
                st.success("🔑 Key saved!")
            else:
                st.warning("Enter a valid API key")
        
        if st.button("🗑️ Clear", use_container_width=True, key="btn_limpar_api"):
            if 'openai_api_key' in st.session_state:
                del st.session_state.openai_api_key
            st.info("Key removed")
    
    if 'openai_api_key' in st.session_state:
        st.success(f"✅ Key configured: {st.session_state.openai_api_key[:10]}...")

# OpenAI Status
if OPENAI_AVAILABLE:
    st.success(f"🤖 OpenAI: {OPENAI_STATUS} - AI Professor Active!")
else:
    st.warning(f"🔒 OpenAI: {OPENAI_STATUS} - Configure to activate AI Professor")

# Student ID input
st.markdown('''
<div class="ra-input-container">
    <h3>🔍 Student Identification</h3>
    <p>Enter your student ID below to access your personalized platform</p>
</div>
''', unsafe_allow_html=True)

ra_input = st.text_input("**Student ID:**", placeholder="Ex: 123456789", key="ra_input", label_visibility="collapsed")

# Process ID
if ra_input:
    try:
        df = load_data(pd, st)
        if df.empty:
            st.error("❌ Data file not found or empty")
        else:
            ra_input = int(ra_input)
            aluno_data = df[df['RA'] == ra_input]
            
            if not aluno_data.empty:
                aluno_nome = aluno_data['Nome'].iloc[0]
                
                # Student data
                port_data = aluno_data[aluno_data['Disciplina'] == 'PORT']
                mat_data = aluno_data[aluno_data['Disciplina'] == 'MAT']
                
                # Calculate metrics
                acertos_port = port_data['acerto'].sum() if not port_data.empty else 0
                acertos_mat = mat_data['acerto'].sum() if not mat_data.empty else 0
                erros_port = port_data['erro'].sum() if not port_data.empty else 0
                erros_mat = mat_data['erro'].sum() if not mat_data.empty else 0
                
                # Error DataFrames
                erros_port_df = port_data[port_data['erro'] == 1] if not port_data.empty else pd.DataFrame()
                erros_mat_df = mat_data[mat_data['erro'] == 1] if not mat_data.empty else pd.DataFrame()
                
                # Student context for LU
                contexto_aluno = {
                    'port_erros': erros_port_df['questao_numero'].tolist() if not erros_port_df.empty else [],
                    'mat_erros': erros_mat_df['questao_numero'].tolist() if not erros_mat_df.empty else [],
                    'conteudos_port': erros_port_df['Conteúdo'].unique().tolist() if not erros_port_df.empty else [],
                    'conteudos_mat': erros_mat_df['Conteúdo'].unique().tolist() if not erros_mat_df.empty else [],
                    'acertos_port': acertos_port,
                    'acertos_mat': acertos_mat,
                    'erros_port': erros_port,
                    'erros_mat': erros_mat,
                    'nome': aluno_nome
                }
                
                # Store data in session
                st.session_state.aluno_data = {
                    'nome': aluno_nome,
                    'acertos_port': acertos_port,
                    'acertos_mat': acertos_mat,
                    'erros_port': erros_port,
                    'erros_mat': erros_mat,
                    'erros_port_df': erros_port_df,
                    'erros_mat_df': erros_mat_df,
                    'contexto_aluno': contexto_aluno
                }
                
                # Initialize gamification
                inicializar_sistema_gamificacao(st)
                verificar_conquistas(st.session_state.aluno_data, st)
                
                # 🎮 Daily access bonus
                hoje = datetime.now().strftime("%Y-%m-%d")
                if st.session_state.gamificacao.get('ultimo_acesso') != hoje:
                    atualizar_pontuacao('acesso_diario', st=st)
                    st.session_state.gamificacao['ultimo_acesso'] = hoje
                
                # Personalized welcome message
                st.markdown(f'''
                <div class="main-card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-align: center;">
                    <h2 style="color: white;">👋 Hello, {aluno_nome}!</h2>
                    <p style="color: white; font-size: 1.1em;">Good to see you here!</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p style="color: white;">📊 <strong>Your current performance:</strong></p>
                    <p style="color: white; font-size: 1.2em;">📚 Portuguese: {acertos_port}/18 | 🧮 Mathematics: {acertos_mat}/18</p>
                    <p style="color: white; margin-top: 15px;">✨ Explore the tabs below to learn with AI Professor and chat with Tutor LU!</p>
                </div>
                ''', unsafe_allow_html=True)
                
            else:
                st.error("❌ Student ID not found. Check the number and try again.")
                if 'aluno_data' in st.session_state:
                    del st.session_state.aluno_data
                
    except ValueError:
        st.error("❌ Please enter a valid student ID (numbers only).")
        if 'aluno_data' in st.session_state:
            del st.session_state.aluno_data
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        if 'aluno_data' in st.session_state:
            del st.session_state.aluno_data

# Main tabs
if 'aluno_data' in st.session_state:
    aluno_data = st.session_state.aluno_data
    
# Main tabs
if 'aluno_data' in st.session_state:
    aluno_data = st.session_state.aluno_data
    
    # Initialize tab state if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "📚 Questions + Professor FABI", 
        "💬 LU - Learning Unit",
        "🚀 Study Plan"
    ])
    
    # Update tab state when changing (detects which is active)
    tabs_list = [tab1, tab2, tab3, tab4]
    
    with tab1:
        st.markdown('''
        <div class="main-card">
            <h2>📊 Performance Dashboard</h2>
            <p>Overview of your performance in subjects</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # ===== GAMIFICATION WIDGET =====
        st.markdown("### 🎮 Your Progression")
        exibir_widget_gamificacao(st)
        
        st.divider()
        
        # Main metrics
        st.markdown("### 📈 Academic Performance")
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        
        with col_met1:
            st.markdown(f'''
            <div class="metric-card">
                <h4>📚 Portuguese</h4>
                <h2>{aluno_data['acertos_port']}/18</h2>
                <p>{aluno_data['acertos_port'] - 9} vs average</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_met2:
            st.markdown(f'''
            <div class="metric-card">
                <h4>🧮 Mathematics</h4>
                <h2>{aluno_data['acertos_mat']}/18</h2>
                <p>{aluno_data['acertos_mat'] - 11} vs average</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_met3:
            st.markdown(f'''
            <div class="metric-card">
                <h4>📝 PORT Errors</h4>
                <h2>{aluno_data['erros_port']}</h2>
                <p>To review</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_met4:
            st.markdown(f'''
            <div class="metric-card">
                <h4>📝 MAT Errors</h4>
                <h2>{aluno_data['erros_mat']}</h2>
                <p>To review</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # GAUGE CHARTS
        st.markdown('''
        <div class="main-card">
            <h3>🎯 Performance by Subject</h3>
            <p>Your progress visualized in interactive gauges</p>
        </div>
        ''', unsafe_allow_html=True)
        
        col_vel1, col_vel2 = st.columns(2)
        
        with col_vel1:
            fig_vel_port = criar_grafico_velocimetro(
                aluno_data['acertos_port'], 
                "Portuguese", 
                "#10b981", 
                go
            )
            st.plotly_chart(fig_vel_port, use_container_width=True)
        
        with col_vel2:
            fig_vel_mat = criar_grafico_velocimetro(
                aluno_data['acertos_mat'], 
                "Mathematics", 
                "#3b82f6",
                go
            )
            st.plotly_chart(fig_vel_mat, use_container_width=True)
        
        # Priority contents chart
        fig_conteudos = criar_grafico_conteudos_prioritarios(
            aluno_data['erros_port_df'], 
            aluno_data['erros_mat_df'],
            px,
            pd
        )
        
        if fig_conteudos:
            st.markdown('''
            <div class="main-card">
                <h3>📊 Contents that Need More Attention</h3>
            </div>
            ''', unsafe_allow_html=True)
            st.plotly_chart(fig_conteudos, use_container_width=True)
    
    with tab2:
        # JavaScript to keep tab selected after rerun
        st.markdown('''
        <script>
        // Store which tab is active
        const observer = new MutationObserver(() => {
            const tabs = document.querySelectorAll('[data-testid="stTabs"] button');
            const activeTab = Array.from(tabs).findIndex(tab => tab.getAttribute('aria-selected') === 'true');
            if (activeTab > 0) {
                sessionStorage.setItem('activeTab', activeTab);
            }
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Restore tab on load
        window.addEventListener('load', () => {
            const savedTab = sessionStorage.getItem('activeTab');
            if (savedTab) {
                const tabs = document.querySelectorAll('[data-testid="stTabs"] button');
                if (tabs[savedTab]) {
                    setTimeout(() => tabs[savedTab].click(), 100);
                }
            }
        });
        </script>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="main-card">
            <h2>📚 Questions + Professor FABI</h2>
            <p>Review the questions you got wrong and chat with AI Professor about each one</p>
        </div>
        ''', unsafe_allow_html=True)
        
        if not OPENAI_AVAILABLE:
            st.warning("""
            ⚠️ **AI Professor not available**
            
            To use AI Professor that analyzes official commented answers:
            1. Click on "⚙️ OpenAI Configuration" at the top of the page
            2. Insert your OpenAI API key
            3. Reload the page
            
            AI Professor can read the official PDFs of questions and explain step by step!
            """)
        
        sub_tab1, sub_tab2 = st.tabs(["📚 Portuguese", "🧮 Mathematics"])
        
        with sub_tab1:
            st.markdown('''
            <div class="subject-card portuguese-card">
                <h3>📚 Questions to Review - Portuguese</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            if not aluno_data['erros_port_df'].empty:
                for idx, row in aluno_data['erros_port_df'].iterrows():
                    numero_questao = int(row['questao_numero'])
                    conteudo = row['Conteúdo']
                    url_pdf = row['Questão']
                    
                    with st.expander(f"❌ Question {numero_questao} - {conteudo}", expanded=False):
                        st.markdown(f'''
                        <div class="main-card">
                            <h4>Question {numero_questao} - {conteudo}</h4>
                            <p><strong>📝 Descriptor:</strong> {row['Descritor']}</p>
                            <p><strong>📖 Recommended Lesson:</strong> <a href="{row['Aula']}" target="_blank">Click here</a></p>
                            <p><strong>🎯 Question Link:</strong> <a href="{row['Questão']}" target="_blank">Click here</a></p>
                        </div>
                        ''', unsafe_allow_html=True)
                                                
                        # AI Professor section for this question
                        exibir_interface_professor_ia(
                            numero_questao=numero_questao,
                            disciplina="Portuguese",
                            url_pdf=url_pdf,
                            conteudo=conteudo,
                            unique_id=f"port_{idx}"
                        )
            else:
                st.success("🎉 Congratulations! You got all Portuguese questions correct!")
        
        with sub_tab2:
            st.markdown('''
            <div class="subject-card math-card">
                <h3>🧮 Questions to Review - Mathematics</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            if not aluno_data['erros_mat_df'].empty:
                for idx, row in aluno_data['erros_mat_df'].iterrows():
                    numero_questao = int(row['questao_numero'])
                    conteudo = row['Conteúdo']
                    url_pdf = row['Questão']
                    
                    with st.expander(f"❌ Question {numero_questao} - {conteudo}", expanded=False):
                        st.markdown(f'''
                        <div class="main-card">
                            <h4>Question {numero_questao} - {conteudo}</h4>
                            <p><strong>📝 Descriptor:</strong> {row['Descritor']}</p>
                            <p><strong>📖 Recommended Lesson:</strong> <a href="{row['Aula']}" target="_blank">Click here</a></p>
                            <p><strong>🎯 Question Link:</strong> <a href="{row['Questão']}" target="_blank">Click here</a></p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # AI Professor section for this question
                        exibir_interface_professor_ia(
                            numero_questao=numero_questao,
                            disciplina="Mathematics",
                            url_pdf=url_pdf,
                            conteudo=conteudo,
                            unique_id=f"mat_{idx}"
                        )
            else:
                st.success("🎉 Congratulations! You got all Mathematics questions correct!")
    
    with tab3:
        # LU - Learning Unit
        st.markdown('''
        <div class="main-card">
            <h2>💬 LU - Learning Unit</h2>
            <p>Chat about study strategies, motivation and general doubts</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Fixed LU avatar (positioned as sidebar in tab)
        st.markdown('''
        <div class="lu-avatar-fixed">
            <div class="lu-avatar-fixed-inner">LU</div>
            <div class="lu-avatar-label">Tutor LU</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if OPENAI_AVAILABLE:
            st.success("✨ LU is online! I'm your intelligent tutor. How can I help you today?")
        else:
            st.info("📚 LU is in basic mode. Configure OpenAI for more intelligent conversations!")
        
        # Initialize chat history
        if "lu_messages" not in st.session_state:
            st.session_state.lu_messages = [
                {
                    "role": "assistant", 
                    "content": f"Hello {aluno_data['nome'].split()[0]}! 👋 I'm LU, your intelligent tutor. \n\nI see you're working hard - you got {aluno_data['acertos_port']} Portuguese questions and {aluno_data['acertos_mat']} Mathematics questions correct.\n\n💡 **Tip:** Use **Professor FABI** (Questions tab) for specific doubts about questions. I can help you with:\n• Study strategies\n• Motivation and organization\n• General conceptual doubts\n• Study planning\n\nWhat would you like to chat about today? 💫"
                }
            ]
        
        # Chat container
        chat_container = st.container()
        with chat_container:
            # Show chat history
            for idx, message in enumerate(st.session_state.lu_messages):
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('''
                    <div class="lu-message">
                        <div class="lu-avatar">
                            <div class="lu-avatar-img">LU</div>
                            <span class="lu-name">LU - Intelligent Tutor</span>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.markdown(message["content"])
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Type your message to LU...", key="lu_chat_input"):
            # Add user message
            st.session_state.lu_messages.append({"role": "user", "content": prompt})
            
            # Show thinking image while thinking
            st.markdown('''
            <div style="text-align: center; padding: 20px;">
                <p style="color: #666; font-size: 0.9em;">LU is thinking about your question...</p>
            </div>
            ''', unsafe_allow_html=True)
            st.image('/Users/mac/IronHacks/W9/Final Project 4/app/static/lu_duvida.png', width=200)
            
            # Simple response (could be expanded with AI)
            if OPENAI_AVAILABLE:
                try:
                    from openai import OpenAI
                    
                    # Get API key
                    api_key = None
                    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
                        api_key = st.session_state.openai_api_key
                    elif 'OPENAI_API_KEY' in st.secrets:
                        api_key = st.secrets['OPENAI_API_KEY']
                    else:
                        api_key = os.getenv('OPENAI_API_KEY')
                    
                    if not api_key:
                        raise Exception("API key not available")
                    
                    client = OpenAI(api_key=api_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"""You are LU, an intelligent and empathetic tutor. The student {aluno_data['nome']} has {aluno_data['acertos_port']} correct in Portuguese and {aluno_data['acertos_mat']} in Mathematics. 

CHARACTERISTICS:
- Be helpful, encouraging and motivating
- Respect the student's level
- Use clear and accessible language
- Line breaks for better readability

MATHEMATICS ANSWER FORMATTING:
If the question involves mathematics:
- Use UNICODE SYMBOLS: × ÷ ² ³ √ π ° ≈ ± ≤ ≥ α β γ θ
- Never use [ ... ] for formulas
- Examples: "Area = πr²", "Volume = (4/3)πr³", "x = 5 ± 2"
- Use **bold** to highlight main formulas
- Structure with:
  * **Formula:** (use Unicode symbols)
  * **Meaning:** (what each letter means)
  * **Example:** (with real numbers)
  * **Tip:** (to memorize or avoid mistakes)

Be brief but complete in your answers."""},
                            *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.lu_messages[-6:]],
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8,
                        max_tokens=400
                    )
                    
                    resposta = response.choices[0].message.content.strip()
                except:
                    resposta = f"Hello {aluno_data['nome'].split()[0]}! I understand your question about '{prompt[:30]}...'. As tutor LU, I recommend focusing on contents where you have more difficulty and using AI Professor for specific questions. Can I help you with something else?"
            else:
                resposta = f"Hello {aluno_data['nome'].split()[0]}! I'm currently in basic mode. For more intelligent conversations, configure OpenAI. Meanwhile, remember to review the questions you got wrong and use the available study resources!"
            
            # Add answer to history
            st.session_state.lu_messages.append({"role": "assistant", "content": resposta})
            
            # 🎮 Update gamification score for LU interaction
            atualizar_pontuacao('interacao_lu', st=st)
            
            # Show idea image after getting answer
            st.markdown('''
            <div style="text-align: center; padding: 20px;">
                <p style="color: #666; font-size: 0.9em;">LU had an idea! ✨</p>
            </div>
            ''', unsafe_allow_html=True)
            st.image('/Users/mac/IronHacks/W9/Final Project 4/app/static/lu_ideia.png', width=200)
            
            # Show answer IMMEDIATELY (without depending on rerun)
            st.markdown("---")
            st.markdown("### 💬 LU's Answer")
            st.markdown(resposta)
            
            # Script to scroll to end of chat
            st.markdown('''
            <script>
            setTimeout(() => {
                window.scrollTo(0, document.body.scrollHeight);
            }, 100);
            </script>
            ''', unsafe_allow_html=True)
    
    with tab4:
        exibir_aba_plano_estudos(aluno_data)

else:
    # Initial page when no student ID has been entered
    st.markdown('''
    <div class="main-card" style="text-align: center;">
        <h2>Welcome to Learning Platform</h2>
        <p>Enter your student ID above to access your personalized dashboard</p>
    </div>
    
    <div class="main-card">
        <h3>✨ New: AI Professor!</h3>
        <p>Now you can chat with a specialized AI Professor that:</p>
        <ul>
            <li>✅ Reads the official PDF of the question you got wrong</li>
            <li>✅ Accesses the official commented answer</li>
            <li>✅ Explains step by step how to solve</li>
            <li>✅ Gives specific tips to not repeat the error</li>
            <li>✅ Answers your questions about each question</li>
        </ul>
        <p><strong>How to use:</strong></p>
        <ol>
            <li>Enter your student ID</li>
            <li>Go to "Questions + Professor FABI" tab</li>
            <li>Choose a question you got wrong</li>
            <li>Ask specific questions about it</li>
            <li>Receive personalized explanations!</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; color: #666;">
    <p>📱 <strong>AI Learning Platform</strong> | 🎓 <strong>EE Alberto Torres - 3rd Grade</strong> | 📚 <strong>Integrated AI Professor</strong></p>
</div>
''', unsafe_allow_html=True)