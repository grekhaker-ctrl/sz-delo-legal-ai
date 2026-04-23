"""
СЗ Дело | Юридический ИИ-агент
Legal AI Platform
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
# DESIGN SYSTEM - СЗ ДЕЛО STYLE
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Цветовая палитра СЗ Дело */
    :root {
        --delo-blue: #1a56db;
        --delo-dark: #0f172a;
        --delo-gray: #64748b;
        --delo-light: #f8fafc;
        --accent: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* App Background */
    .stApp {
        background: #ffffff;
    }
    
    /* Hero Section - СЗ Дело Style */
    .hero-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 0;
        padding: 48px;
        margin: 0 0 32px 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.2);
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 30% 50%, rgba(26, 86, 219, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 70% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 2.8em;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.2em;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Clean Cards */
    .clean-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .clean-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* Risk Cards */
    .risk-card {
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
        border-left: 4px solid;
        background: #ffffff;
    }
    
    .risk-critical { border-left-color: #dc2626; background: #fef2f2; }
    .risk-high { border-left-color: #ea580c; background: #fff7ed; }
    .risk-medium { border-left-color: #d97706; background: #fef3c7; }
    .risk-low { border-left-color: #059669; background: #f0fdf4; }
    
    /* Buttons - СЗ Дело Style */
    .stButton > button {
        background: #1a56db;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(26, 86, 219, 0.3);
    }
    
    .stButton > button:hover {
        background: #1e40af;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(26, 86, 219, 0.4);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 6px 6px 6px 0;
    }
    
    .status-success { 
        background: #d1fae5; 
        color: #065f46; 
    }
    
    .status-error { 
        background: #fee2e2; 
        color: #991b1b; 
    }
    
    /* Sidebar - Clean */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] * {
        color: #0f172a !important;
    }
    
    /* Chat Messages */
    .chat-user {
        background: #1a56db;
        color: white;
        padding: 14px 18px;
        border-radius: 12px 12px 4px 12px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-assistant {
        background: #f8fafc;
        color: #0f172a;
        padding: 14px 18px;
        border-radius: 12px 12px 12px 4px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid #e2e8f0;
    }
    
    /* File Upload */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 8px;
        padding: 24px;
        border: 2px dashed #cbd5e1;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #1a56db;
        background: #eff6ff;
    }
    
    /* Divider */
    hr {
        border-color: #e2e8f0;
        margin: 24px 0;
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
    # Логотип
    st.markdown("""
    <div style="text-align: center; padding: 32px 20px 24px;">
        <div style="
            width: 70px;
            height: 70px;
            background: #1a56db;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px;
            font-size: 2em;
        ">⚖️</div>
        <h1 style="
            font-size: 1.6em;
            font-weight: 800;
            margin: 0;
            color: #0f172a;
            letter-spacing: -0.5px;
        ">СЗ ДЕЛО</h1>
        <p style="color: #64748b; margin: 8px 0 0 0; font-size: 0.9em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Меню
    st.markdown("**Меню**")
    
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
    
    # Статус
    st.markdown("**Статус системы**")
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
    
    # Инфо
    st.markdown("""
    <div style="color: #64748b; font-size: 0.85em; line-height: 1.8;">
        <p style="margin: 4px 0;"><strong>🏢</strong> СЗ Дело</p>
        <p style="margin: 4px 0;"><strong>🏗️</strong> Девелопмент</p>
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
        <div class="clean-card">
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
Исправь договор для строительной компании СЗ Дело.

Оригинальный текст:
{contract_text[:10000]}

Твоя задача:
1. Найти все рискованные пункты
2. Предложить ИСПРАВЛЕННЫЙ текст
3. Указать конкретные статьи ГК РФ

ВАЖНО - ФОРМАТ ОТВЕТА:
Дай ответ СТРОГО в этой структуре:

### 📊 Анализ договора
[Тип договора, стороны, предмет, цена, сроки]

### ⚠️ Найденные проблемы
1. [Конкретный пункт] - [Проблема] - [Статья ГК РФ]
2. ...

### ✅ Исправленный текст договора
[ПОЛНЫЙ текст договора с ВСЕМИ исправлениями]
[Текст должен быть ЧЁТКО структурирован по разделам]

### 📝 Таблица изменений
| № | Пункт | Было | Стало | Обоснование (статья ГК) |
|---|-------|------|-------|------------------------|
| 1 | ... | ... | ... | ... |
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        # PDF
                        try:
                            from fpdf import FPDF
                            
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            font_path = "/tmp/DejaVuSans.ttf"
                            try:
                                import urllib.request
                                urllib.request.urlretrieve(
                                    "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
                                    font_path
                                )
                            except:
                                pass
                            
                            if os.path.exists(font_path):
                                pdf.add_font("DejaVu", "", font_path, uni=True)
                                pdf.set_font("DejaVu", "", 10)
                            else:
                                pdf.set_font("Arial", "", 10)
                            
                            pdf.set_font_size(14)
                            pdf.cell(0, 10, "ИСПРАВЛЕННЫЙ ДОГОВОР", ln=True, align="C")
                            pdf.set_font_size(10)
                            pdf.cell(0, 10, f"Оригинал: {uploaded_file.name}", ln=True, align="C")
                            pdf.ln(10)
                            
                            pdf.set_font_size(10)
                            for line in response.text.split("\n"):
                                clean_line = line.replace("#", "").replace("*", "").replace("-", "").strip()
                                if clean_line:
                                    pdf.multi_cell(0, 8, clean_line)
                            
                            pdf_path = f"fixed_{uploaded_file.name}.pdf"
                            pdf.output(pdf_path)
                            
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📥 Скачать PDF",
                                    data=f.read(),
                                    file_name=f"fixed_{uploaded_file.name}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                                
                        except Exception as pdf_error:
                            st.download_button(
                                label="📥 Скачать TXT",
                                data=response.text,
                                file_name=f"fixed_{uploaded_file.name}.txt",
                                mime="text/plain",
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
<div style="text-align: center; color: #64748b; font-size: 0.85em; padding: 24px;">
    <p style="margin: 0;">© 2025 СЗ Дело | Legal AI Platform</p>
    <p style="margin: 8px 0 0 0;">Powered by Polza AI</p>
</div>
""", unsafe_allow_html=True)
