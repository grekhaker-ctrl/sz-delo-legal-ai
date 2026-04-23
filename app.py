"""
СЗ Дело | Юридический ИИ-агент
"""
import streamlit as st
import os

st.set_page_config(
    page_title="СЗ Дело | Юридический ИИ",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS - Улучшенный дизайн
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Скрываем лишнее */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Фон приложения */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        background-attachment: fixed;
    }
    
    /* Карточки */
    .glass-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    /* Hero секция */
    .hero-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
        border-radius: 16px;
        padding: 40px;
        margin: 0 0 24px 0;
        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
    }
    
    .hero-title {
        font-size: 2.5em;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 1.1em;
        color: #bfdbfe;
        margin: 0;
        font-weight: 400;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
    
    /* Заголовки разделов */
    .section-title {
        font-size: 1.5em;
        font-weight: 700;
        color: #1e293b;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Sidebar - фиксированный */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden !important;
        position: fixed !important;
        height: 100vh !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] .stVerticalBlock {
        overflow: hidden !important;
    }
    
    /* Кнопка открытия sidebar */
    .sidebar-toggle-btn {
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 10000;
        background: #1e3a5f;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 1.3em;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s;
    }
    .sidebar-toggle-btn:hover {
        background: #2d5a87;
        transform: scale(1.05);
    }
    
    /* Загрузчик файлов */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 2px dashed #94a3b8;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    /* Чат */
    .chat-user {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-assistant {
        background: #ffffff;
        color: #1e293b;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 4px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid #e2e8f0;
    }
    
    /* Риски */
    .risk-box {
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid;
        background: #ffffff;
    }
    
    .risk-critical { border-left-color: #dc2626; background: #fef2f2; }
    .risk-high { border-left-color: #ea580c; background: #fff7ed; }
    .risk-medium { border-left-color: #d97706; background: #fef3c7; }
    .risk-low { border-left-color: #10b981; background: #f0fdf4; }
    
    /* Разделитель */
    hr {
        border-color: #e2e8f0;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Состояние
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analyzed_contract' not in st.session_state:
    st.session_state.analyzed_contract = None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    # Логотип и название
    st.markdown("""
    <div style="text-align: center; padding: 32px 20px 24px;">
        <div style="
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            font-size: 2.2em;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        ">⚖️</div>
        <h2 style="
            margin: 0;
            color: #ffffff;
            font-size: 1.6em;
            font-weight: 800;
            letter-spacing: -0.5px;
        ">СЗ ДЕЛО</h2>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.9em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Меню
    st.markdown("**🧭 Меню**")
    menu = st.radio(
        "Выберите раздел",
        [
            "💬 Чат с юристом",
            "📄 Анализ договора",
            "⚖️ Юридическое заключение",
            "🔄 Сравнение версий",
        ],
        label_visibility="collapsed",
        index=0
    )
    
    st.divider()
    
    # Кнопка очистки
    if st.button("🗑️ Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Кнопка для открытия sidebar (видна всегда)
st.markdown("""
<div class="sidebar-toggle-btn" onclick="
    var sidebar = document.querySelector('[data-testid=\"stSidebar\"]');
    if (sidebar) {
        sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'block';
        sidebar.style.width = '300px';
    }
    return false;
">☰ Меню</div>
""", unsafe_allow_html=True)

# ============================================================================
# ФУНКЦИИ
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
    
    if prompt := st.chat_input("Задайте ваш юридический вопрос..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Анализирую вопрос..."):
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
                    st.error(f"❌ Ошибка: {str(e)}")


def render_analyze():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">📄 Анализ договора</h1>
        <p class="hero-subtitle">Загрузите договор — ИИ найдёт риски и исправит текст</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите файл договора",
        type=['pdf', 'docx', 'txt'],
        help="Поддерживаемые форматы: PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.markdown(f"""
        <div class="glass-card">
            <strong>📎 Файл:</strong> {uploaded_file.name}<br>
            <strong>📊 Размер:</strong> {uploaded_file.size / 1024:.1f} КБ
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            analyze_risks = st.checkbox("✅ Анализ рисков", value=True)
        with col2:
            fix_contract = st.checkbox("✅ Исправить текст", value=True)
        
        if st.button("🔍 Начать анализ", type="primary", use_container_width=True):
            with st.spinner("🤖 Анализирую договор..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    st.session_state.analyzed_contract = contract_text
                    llm = create_llm_engine()
                    
                    if analyze_risks:
                        st.markdown("### 📊 Анализ рисков")
                        risk_prompt = f"""
Проанализируй договор для СЗ Дело (Москва/МО).

Текст:
{contract_text[:10000]}

Формат ответа:
### Тип договора
[Определение]

### Риски
1. [Риск] - [Статья ГК РФ] - [Уровень]
2. ...

### Рекомендации
[Советы]
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия")
                        fix_prompt = f"""
Исправь договор для строительной компании СЗ Дело (Москва/МО).

Оригинальный текст:
{contract_text[:10000]}

Твоя задача:
1. Найти все рискованные пункты
2. Предложить исправленный текст
3. Указать конкретные статьи ГК РФ

Формат ответа СТРОГО:
### Анализ
[Кратко: тип договора, стороны, предмет]

### Проблемы
1. [Пункт] - [Проблема] - [Статья ГК РФ]

### Исправленный текст
[ПОЛНЫЙ текст договора с исправлениями]

### Таблица изменений
| № | Было | Стало | Причина |
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        # Скачать TXT
                        st.download_button(
                            label="📥 Скачать исправленный (TXT)",
                            data=response.text.encode('utf-8'),
                            file_name=f"fixed_{uploaded_file.name}.txt",
                            mime="text/plain; charset=utf-8",
                            use_container_width=True
                        )
                        
                        # PDF
                        try:
                            from fpdf import FPDF
                            
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            font_path = "/tmp/DejaVuSans.ttf"
                            if not os.path.exists(font_path):
                                try:
                                    import urllib.request
                                    urllib.request.urlretrieve(
                                        "https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@master/ttf/DejaVuSans.ttf",
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
                                clean = line.replace("#", "").replace("*", "").strip()
                                if clean:
                                    try:
                                        pdf.multi_cell(0, 8, clean)
                                    except:
                                        pdf.multi_cell(0, 8, clean.encode('latin-1', errors='ignore').decode('latin-1'))
                            
                            pdf_path = f"fixed_{uploaded_file.name}.pdf"
                            pdf.output(pdf_path)
                            
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📥 Скачать исправленный (PDF)",
                                    data=f.read(),
                                    file_name=f"fixed_{uploaded_file.name}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                                
                        except Exception as pdf_error:
                            st.warning(f"⚠️ PDF не создан: {str(pdf_error)[:200]}")
                    
                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)


def render_conclusion():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">⚖️ Юридическое заключение</h1>
        <p class="hero-subtitle">Профессиональное заключение по договору</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите файл договора",
        type=['pdf', 'docx', 'txt'],
        help="Поддерживаемые форматы: PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("📝 Получить заключение", type="primary", use_container_width=True):
            with st.spinner("🤖 Готовлю заключение..."):
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

Формат ответа:
1. Тип договора
2. Вывод (✅/⚠️/❌)
3. Риски
4. Рекомендации
"""
                    response = llm.generate(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")
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
        file1 = st.file_uploader(
            "Версия 1",
            type=['pdf', 'docx', 'txt'],
            key="v1",
            help="Загрузите первую версию"
        )
    with col2:
        file2 = st.file_uploader(
            "Версия 2",
            type=['pdf', 'docx', 'txt'],
            key="v2",
            help="Загрузите вторую версию"
        )
    
    if file1 and file2:
        temp1 = f"temp_v1_{file1.name}"
        temp2 = f"temp_v2_{file2.name}"
        
        with open(temp1, "wb") as f:
            f.write(file1.getvalue())
        with open(temp2, "wb") as f:
            f.write(file2.getvalue())
        
        if st.button("🔍 Сравнить версии", type="primary", use_container_width=True):
            with st.spinner("🤖 Сравниваю версии..."):
                try:
                    from backend.contract_comparator import create_comparator
                    comparator = create_comparator()
                    result = comparator.compare_and_explain(temp1, temp2)
                    
                    st.markdown(f"### 📊 Найдено изменений: {result['total_changes']}")
                    st.components.v1.html(result['diff_html'], height=400)
                    st.markdown(result['legal_analysis'])
                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp1): os.remove(temp1)
                    if os.path.exists(temp2): os.remove(temp2)


# ============================================================================
# ОСНОВНАЯ ЧАСТЬ
# ============================================================================

if menu == "💬 Чат с юристом":
    render_chat()
elif menu == "📄 Анализ договора":
    render_analyze()
elif menu == "⚖️ Юридическое заключение":
    render_conclusion()
elif menu == "🔄 Сравнение версий":
    render_compare()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85em; padding: 24px;">
    <p style="margin: 0;">© 2025 СЗ Дело | Юридический ИИ</p>
    <p style="margin: 8px 0 0 0;">Работает на Polza AI</p>
</div>
""", unsafe_allow_html=True)
