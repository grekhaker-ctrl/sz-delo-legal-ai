"""
СЗ Дело | Юридический ИИ-агент
Premium Legal AI Platform
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="СЗ Дело | Legal AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PREMIUM DESIGN SYSTEM
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Premium Color Palette */
    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --accent-500: #8b5cf6;
        --accent-600: #7c3aed;
        --success-500: #10b981;
        --success-600: #059669;
        --warning-500: #f59e0b;
        --danger-500: #ef4444;
        --danger-600: #dc2626;
        --slate-50: #f8fafc;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-300: #cbd5e1;
        --slate-600: #475569;
        --slate-700: #334155;
        --slate-800: #1e293b;
        --slate-900: #0f172a;
    }
    
    /* App Background */
    .stApp {
        background: linear-gradient(135deg, #fafbfc 0%, #f0f2f5 50%, #e8ebef 100%);
        background-attachment: fixed;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.08),
            0 2px 8px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        padding: 28px;
        margin: 20px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 20px 48px rgba(0, 0, 0, 0.12),
            0 4px 12px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
        border-radius: 24px;
        padding: 48px;
        margin: 24px 0 32px 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(30, 41, 59, 0.4);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 12px 0;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.25em;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        border: 2px solid transparent;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .nav-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .nav-card:hover::before {
        transform: scaleX(1);
    }
    
    .nav-card:hover {
        transform: translateX(8px);
        border-color: #3b82f6;
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.15);
    }
    
    .nav-card.selected {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }
    
    /* Risk Cards */
    .risk-card {
        padding: 24px;
        border-radius: 16px;
        margin: 16px 0;
        border-left: 5px solid;
        background: white;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .risk-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .risk-critical {
        border-left-color: #dc2626;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    
    .risk-high {
        border-left-color: #ea580c;
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
    }
    
    .risk-medium {
        border-left-color: #d97706;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    }
    
    .risk-low {
        border-left-color: #059669;
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    }
    
    /* Buttons - Premium Style */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 36px;
        font-weight: 600;
        font-size: 1em;
        letter-spacing: 0.3px;
        box-shadow: 
            0 4px 16px rgba(59, 130, 246, 0.4),
            0 2px 8px rgba(59, 130, 246, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 12px 28px rgba(59, 130, 246, 0.5),
            0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 6px 8px 6px 0;
        backdrop-filter: blur(8px);
    }
    
    .status-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
    }
    
    .status-error {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
    }
    
    /* Sidebar Premium */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    /* Chat Messages */
    .chat-user {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 12px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
    }
    
    .chat-assistant {
        background: white;
        color: #1e293b;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 12px 0;
        max-width: 80%;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* File Upload */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 16px;
        padding: 32px;
        border: 2px dashed #cbd5e1;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 32px 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .glass-card, .risk-card, .nav-card {
        animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# STATE
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analyzed_contract' not in st.session_state:
    st.session_state.analyzed_contract = None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 32px 20px;">
        <div style="
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            box-shadow: 0 12px 24px rgba(59, 130, 246, 0.4);
            font-size: 2.5em;
        ">⚖️</div>
        <h1 style="
            font-size: 1.8em;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        ">СЗ ДЕЛО</h1>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95em;">Legal AI Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🧭 Меню", style={"color": "#94a3b8", "font-size": "0.9em", "font-weight": "600", "text-transform": "uppercase", "letter-spacing": "1px"})
    
    menu = st.radio(
        "Разделы",
        [
            "💬 Чат с юристом",
            "📄 Анализ договора",
            "⚖️ Заключение",
            "🔄 Сравнение версий",
        ],
        label_visibility="collapsed",
        index=0
    )
    
    st.divider()
    
    st.markdown("### 🔧 Статус")
    try:
        from backend.llm_engine import create_llm_engine
        llm = create_llm_engine()
        status = llm.get_status()
        for name, ok in status.items():
            if ok:
                st.markdown(f'<span class="status-badge status-success">● {name}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-badge status-error">● {name}</span>', unsafe_allow_html=True)
    except:
        pass
    
    st.divider()
    
    st.markdown("""
    <div style="color: #64748b; font-size: 0.85em; line-height: 1.8; padding: 0 8px;">
        <p style="margin: 4px 0;"><strong>🏢</strong> СЗ Дело</p>
        <p style="margin: 4px 0;"><strong>🏗️</strong> Строительство</p>
        <p style="margin: 4px 0;"><strong>🤖</strong> Polza AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🗑️ Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# FUNCTIONS
# ============================================================================

def render_chat():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">💬 Чат с ИИ-юристом</h1>
        <p class="hero-subtitle">Профессиональные юридические консультации 24/7</p>
    </div>
    """, unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Задайте юридический вопрос..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Анализирую..."):
                try:
                    from backend.llm_engine import create_llm_engine
                    from backend.legal_kb import create_legal_kb
                    
                    llm = create_llm_engine()
                    kb = create_legal_kb()
                    context = kb.search(prompt)
                    response = llm.generate(prompt, context=context, task="answer")
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")


def render_analyze():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">📄 Анализ договора</h1>
        <p class="hero-subtitle">ИИ найдёт риски и предложит исправления</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Загрузите договор", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        st.markdown(f"""
        <div class="glass-card">
            <strong>📎</strong> {uploaded_file.name} &nbsp;|&nbsp; 
            <strong>📊</strong> {uploaded_file.size / 1024:.1f} КБ
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            analyze_risks = st.checkbox("✅ Анализ рисков", value=True)
        with col2:
            fix_contract = st.checkbox("✅ Исправить текст", value=True)
        
        if st.button("🔍 Начать анализ", type="primary", use_container_width=True):
            with st.spinner("🤖 Анализирую..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(f"temp_{uploaded_file.name}")
                    st.session_state.analyzed_contract = contract_text
                    llm = create_llm_engine()
                    
                    if analyze_risks:
                        st.markdown("### 📊 Анализ рисков")
                        risk_prompt = f"""
Проанализируй договор для СЗ Дело (Москва/МО).

Текст:
{contract_text[:10000]}

Формат:
### 🔍 Тип договора
[Определение]

### ⚠️ Риски
1. [Риск] - [Статья ГК] - [Уровень]
2. ...

### 📋 Рекомендации
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия")
                        fix_prompt = f"""
Исправь договор для СЗ Дело.

Текст:
{contract_text[:10000]}

Формат:
### 📊 Анализ
### ⚠️ Проблемы
### ✅ Исправленный текст
### 📝 Таблица изменений
| № | Было | Стало | Почему |
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        st.download_button(
                            label="📥 Скачать исправленный",
                            data=response.text,
                            file_name=f"fixed_{uploaded_file.name}.txt",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    if os.path.exists(f"temp_{uploaded_file.name}"):
                        os.remove(f"temp_{uploaded_file.name}")


def render_conclusion():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">⚖️ Юридическое заключение</h1>
        <p class="hero-subtitle">Профессиональное заключение по договору</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Загрузите договор", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("📝 Получить заключение", type="primary", use_container_width=True):
            with st.spinner("Готовлю..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    llm = create_llm_engine()
                    
                    prompt = f"""
Юридическое заключение для СЗ Дело.

Текст:
{contract_text[:10000]}

Формат:
1. Тип договора
2. Заключение (✅/⚠️/❌)
3. Риски
4. Рекомендации
"""
                    response = llm.generate(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)


def render_compare():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🔄 Сравнение версий</h1>
        <p class="hero-subtitle">Найдите различия между версиями договора</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Версия 1", type=['pdf', 'docx', 'txt'], key="v1")
    with col2:
        file2 = st.file_uploader("Версия 2", type=['pdf', 'docx', 'txt'], key="v2")
    
    if file1 and file2:
        temp1 = f"temp_v1_{file1.name}"
        temp2 = f"temp_v2_{file2.name}"
        
        with open(temp1, "wb") as f:
            f.write(file1.getvalue())
        with open(temp2, "wb") as f:
            f.write(file2.getvalue())
        
        if st.button("🔍 Сравнить", type="primary", use_container_width=True):
            with st.spinner("Сравниваю..."):
                try:
                    from backend.contract_comparator import create_comparator
                    comparator = create_comparator()
                    result = comparator.compare_and_explain(temp1, temp2)
                    
                    st.markdown(f"### Изменений: {result['total_changes']}")
                    st.components.v1.html(result['diff_html'], height=400)
                    st.markdown(result['legal_analysis'])
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp1): os.remove(temp1)
                    if os.path.exists(temp2): os.remove(temp2)


# ============================================================================
# MAIN
# ============================================================================

if menu == "💬 Чат с юристом":
    render_chat()
elif menu == "📄 Анализ договора":
    render_analyze()
elif menu == "⚖️ Заключение":
    render_conclusion()
elif menu == "🔄 Сравнение версий":
    render_compare()

st.divider()
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85em; padding: 24px;">
    <p style="margin: 0;">© 2025 СЗ Дело | Legal AI Platform</p>
    <p style="margin: 8px 0 0 0;">Powered by Polza AI</p>
</div>
""", unsafe_allow_html=True)
