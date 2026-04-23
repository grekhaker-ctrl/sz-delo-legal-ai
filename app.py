"""
СЗ Дело | Юридический ИИ-агент
"""
import streamlit as st
import os

st.set_page_config(
    page_title="СЗ Дело | Legal AI",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLES
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Main background */
    .stApp {
        background: #f5f5f7;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 32px 0;
        margin: -20px -20px 24px -20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .app-title {
        color: #ffffff;
        font-size: 2.2em;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        color: #94a3b8;
        font-size: 1.1em;
        margin: 8px 0 0 0;
        font-weight: 400;
    }
    
    /* Cards */
    .info-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e5e5e5;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.4em;
        font-weight: 600;
        color: #1a1a2e;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
    }
    
    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Status */
    .status-ok {
        display: inline-block;
        padding: 4px 12px;
        background: #d1fae5;
        color: #065f46;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    
    .status-err {
        display: inline-block;
        padding: 4px 12px;
        background: #fee2e2;
        color: #991b1b;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e5e5;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Chat */
    .chat-message {
        padding: 16px 20px;
        border-radius: 12px;
        margin: 12px 0;
        max-width: 85%;
    }
    
    .chat-user {
        background: #3b82f6;
        color: white;
        margin-left: auto;
        border-radius: 12px 12px 4px 12px;
    }
    
    .chat-bot {
        background: #ffffff;
        color: #1a1a2e;
        border: 1px solid #e5e5e5;
        border-radius: 12px 12px 12px 4px;
    }
    
    /* Risk cards */
    .risk-box {
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid;
        background: #ffffff;
    }
    
    .risk-critical { border-left-color: #dc2626; background: #fef2f2; }
    .risk-high { border-left-color: #ea580c; background: #fff7ed; }
    .risk-medium { border-left-color: #d97706; background: #fef3c7; }
    .risk-low { border-left-color: #10b981; background: #f0fdf4; }
    
    /* Divider */
    hr {
        border-color: #e5e5e5;
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
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="
            width: 64px;
            height: 64px;
            background: #3b82f6;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            margin-bottom: 12px;
        ">⚖️</div>
        <h2 style="margin: 0; color: #1a1a2e; font-size: 1.5em;">СЗ ДЕЛО</h2>
        <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 0.9em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("**Навигация**")
    menu = st.radio(
        "Разделы",
        [
            "💬 Чат",
            "📄 Анализ договора",
            "⚖️ Заключение",
            "🔄 Сравнение",
        ],
        label_visibility="collapsed",
        index=0
    )
    
    st.divider()
    
    st.markdown("**Статус**")
    try:
        from backend.llm_engine import create_llm_engine
        llm = create_llm_engine()
        status = llm.get_status()
        for name, ok in status.items():
            if ok:
                st.markdown(f'<span class="status-ok">✓ {name}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-err">✗ {name}</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="status-err">Нет подключения</span>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="color: #6b7280; font-size: 0.85em; line-height: 1.6;">
        <p><strong>🏢</strong> СЗ Дело</p>
        <p><strong>🏗️</strong> Девелопмент</p>
        <p><strong>🤖</strong> Polza AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🗑️ Очистить", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="app-header">
    <h1 class="app-title">⚖️ СЗ ДЕЛО</h1>
    <p class="app-subtitle">Юридический ИИ-агент</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCTIONS
# ============================================================================

def render_chat():
    st.markdown('<p class="section-title">💬 Чат с юристом</p>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ваш вопрос..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
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
    st.markdown('<p class="section-title">📄 Анализ договора</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Загрузите договор (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        st.markdown(f"""
        <div class="info-card">
            <strong>📎 Файл:</strong> {uploaded_file.name}<br>
            <strong>📊 Размер:</strong> {uploaded_file.size / 1024:.1f} КБ
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            analyze_risks = st.checkbox("Анализ рисков", value=True)
        with col2:
            fix_contract = st.checkbox("Исправить текст", value=True)
        
        if st.button("🔍 Начать анализ", type="primary", use_container_width=True):
            with st.spinner("Анализирую..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(f"temp_{uploaded_file.name}")
                    st.session_state.analyzed_contract = contract_text
                    llm = create_llm_engine()
                    
                    if analyze_risks:
                        st.markdown("### 📊 Риски")
                        risk_prompt = f"""
Проанализируй договор для СЗ Дело.

Текст:
{contract_text[:10000]}

Найди:
1. Риски со статьями ГК РФ
2. Рекомендации

Формат:
### Риски
1. [Риск] - [Статья ГК] - [Уровень]

### Рекомендации
[Советы]
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    if fix_contract:
                        st.markdown("### ✨ Исправления")
                        fix_prompt = f"""
Исправь договор для СЗ Дело.

Текст:
{contract_text[:10000]}

Формат СТРОГО:
### Анализ
[Кратко]

### Проблемы
1. [Пункт] - [Проблема] - [Статья ГК]

### Исправленный текст
[ПОЛНЫЙ текст]

### Таблица
| № | Было | Стало | Причина |
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
                            pdf.cell(0, 10, f"Файл: {uploaded_file.name}", ln=True, align="C")
                            pdf.ln(10)
                            
                            pdf.set_font_size(10)
                            for line in response.text.split("\n"):
                                clean = line.replace("#", "").replace("*", "").replace("-", "").strip()
                                if clean:
                                    pdf.multi_cell(0, 8, clean)
                            
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
                        except:
                            st.download_button(
                                label="📥 Скачать TXT",
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
    st.markdown('<p class="section-title">⚖️ Юридическое заключение</p>', unsafe_allow_html=True)
    
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
2. Вывод (✅/⚠️/❌)
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
    st.markdown('<p class="section-title">🔄 Сравнение версий</p>', unsafe_allow_html=True)
    
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
                    
                    st.markdown(f"### Найдено изменений: {result['total_changes']}")
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

if menu == "💬 Чат":
    render_chat()
elif menu == "📄 Анализ договора":
    render_analyze()
elif menu == "⚖️ Заключение":
    render_conclusion()
elif menu == "🔄 Сравнение":
    render_compare()

# Footer
st.divider()
st.markdown('<p style="text-align: center; color: #9ca3af; font-size: 0.85em;">© 2025 СЗ Дело | Legal AI</p>', unsafe_allow_html=True)
