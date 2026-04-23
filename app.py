"""
СЗ Дело | Юридический ИИ-агент
Профессиональная юридическая система
"""
import streamlit as st
import os

st.set_page_config(
    page_title="СЗ Дело | Юридический ИИ",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Принудительно держим sidebar открытым
st.markdown("""
<script>
    function keepSidebarOpen() {
        var sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
        }
    }
    setInterval(keepSidebarOpen, 500);
    keepSidebarOpen();
</script>
""", unsafe_allow_html=True)

# ============================================================================
# CSS - Меню всегда видно + чёткий дизайн
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Шрифт */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Фон приложения - нейтральный светлый */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Sidebar - классический тёмно-синий */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #1a283a 100%) !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Кнопку закрытия sidebar скрываем */
    button[title="Close sidebar"] {
        display: none !important;
    }
    
    /* Скрываем английские placeholder Streamlit */
    .stFileUploader > div > p,
    .stFileUploader > div > div > p,
    [data-testid="stFileUploader"] > div > p,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] p {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    
    /* Скрываем drag and drop текст */
    [data-testid="stFileUploader"] [data-testid="baseButton"] {
        display: none !important;
    }
    
    /* Hero секция - классический синий */
    .hero-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        border-radius: 12px;
        padding: 32px 40px;
        margin: 20px 24px 24px 24px;
        box-shadow: 0 4px 16px rgba(30, 58, 95, 0.2);
    }
    
    .hero-title {
        font-size: 2.2em;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        font-size: 1.05em;
        color: #e0e7ff;
        margin: 0;
    }
    
    /* Карточки - белый */
    .info-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Кнопки - синий */
    .stButton > button {
        background: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    /* Загрузчик файлов */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 10px;
        padding: 24px;
        border: 2px dashed #d1d5db;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background: #f0f9ff;
    }
    
    /* ЧАТ - чёткое разделение */
    .chat-user-message {
        background: #2563eb;
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 12px 4px 12px 12px;
        margin: 10px 0;
        max-width: 75%;
        margin-left: auto;
    }
    
    .chat-assistant-message {
        background: #ffffff;
        color: #1f2937;
        padding: 14px 18px;
        border-radius: 4px 12px 12px 12px;
        margin: 10px 0;
        max-width: 75%;
        border: 1px solid #e5e7eb;
    }
    
    /* Разделители */
    hr {
        border-color: #e5e7eb;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# КНОПКА ОТКРЫТИЯ SIDEBAR (если закрыт)
# ============================================================================

st.markdown("""
<style>
    .sidebar-open-btn {
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 9999;
    }
</style>
<div class="sidebar-open-btn">
    <button onclick="
        var sidebar = document.querySelector('[data-testid=\"stSidebar\"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            var btn = document.querySelector('[title=\"Open sidebar\"]');
            if (btn) btn.click();
        }
        return false;
    " style="
        background: #1a284a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 1.3em;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    ">☰ Меню</button>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Состояние
# ============================================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analyzed_contract' not in st.session_state:
    st.session_state.analyzed_contract = None

# ============================================================================
# SIDEBAR - ВСЕГДА ВИДИМ
# ============================================================================

with st.sidebar:
    # Логотип
    st.markdown("""
    <div style="text-align: center; padding: 28px 18px 22px;">
        <div style="
            width: 68px;
            height: 68px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 14px;
            font-size: 2.1em;
            box-shadow: 0 7px 18px rgba(59, 130, 246, 0.45);
        ">⚖️</div>
        <h2 style="
            margin: 0;
            color: #ffffff;
            font-size: 1.55em;
            font-weight: 800;
            letter-spacing: -0.4px;
        ">СЗ ДЕЛО</h2>
        <p style="color: #9fb8d0; margin: 7px 0 0 0; font-size: 0.88em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Меню
    st.markdown("**МЕНЮ**")
    menu = st.radio(
        "Разделы",
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
    
    # Ссылка на приложение
    st.divider()
    st.markdown("""
    <div style="color: #b8cce6; font-size: 0.8em; padding: 0 8px; line-height: 1.7;">
        <p><strong>🌐 Ссылка:</strong></p>
        <p style="color: #e8f0f8; word-break: break-all;">https://sz-delo-legal-ai.streamlit.app</p>
    </div>
    """, unsafe_allow_html=True)
    
# ============================================================================
# ФУНКЦИИ
# ============================================================================

def render_chat():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">💬 Чат с ИИ-юристом</h1>
        <p class="hero-subtitle">Профессиональные юридические консультации по праву РФ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Сообщения чата
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-user-message"><strong>Вы:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant-message"><strong>ИИ-юрист:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    
    # Ввод вопроса
    prompt = st.chat_input("Введите ваш юридический вопрос...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-user-message"><strong>Вы:</strong><br>{prompt}</div>', unsafe_allow_html=True)
        
        with st.spinner("🤖 Анализирую вопрос..."):
            try:
                from backend.llm_engine import create_llm_engine
                from backend.legal_kb import create_legal_kb
                
                llm = create_llm_engine()
                kb = create_legal_kb()
                context = kb.search(prompt)
                
                response = llm.generate(prompt, context=context, task="answer")
                st.markdown(f'<div class="chat-assistant-message"><strong>ИИ-юрист:</strong><br>{response.text}</div>', unsafe_allow_html=True)
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
    
    st.markdown("### 📁 Загрузите файл договора")
    st.markdown("*Форматы: PDF, DOCX, TXT*")
    
    uploaded_file = st.file_uploader("drag_and_drop_placeholder", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.markdown(f"""
        <div class="info-card">
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
            with st.spinner("🤖 Анализирую..."):
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
Ты - старший юрист СЗ Дело с 15+ лет опытом. СЕЙЧАС 2025 ГОД.

Текст договора:
{contract_text[:10000]}

ТРЕБОВАНИЯ:
1. ИСПОЛЬЗУЙ ТОЛЬКО АКТУАЛЬНЫЕ ЗАКОНЫ НА 2025 ГОД
2. ДАВАЙ КОНКРЕТНЫЕ ОТВЕТЫ - не воду
3. УКАЗЫВАЙ ТОЧНЫЕ НОМЕРА СТАТЕЙ ГК РФ
4. УКАЗЫВАЙ ТОЧНЫЕ СРОКИ И ПЕРИОДЫ
5. ПРОВЕРЬ АКТУАЛЬНОСТЬ - перед ответом убедись что закон действует в 2025
6. НЕ ВЫДУМЫВАЙ - проверяй по КонсультантПлюс, Гарант

ФОРМАТ ОТВЕТА СТРОГО:
### Тип договора
[Определение по ГК РФ]

### Найденные риски
1. [Конкретный пункт] - [Статья ГК РФ с номером] - [Уровень риска: Критичный/Высокий/Средний/Низкий] - [Актуально на 2025]
2. ...

### Сроки
- [Конкретные сроки: начало, окончание, последствия просрочки]

### Рекомендации
1. [Конкретное действие]
2. [Конкретное действие]

### Источник
- КонсультантПлюс / Гарант (актуальная редакция 2025)
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                        
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия")
                        fix_prompt = f"""
Ты - старший юрист СЗ Дело.

ТРЕБОВАНИЯ:
1. ТОЛЬКО актуальные законы РФ
2. Проверяй: КонсультантПлюс, Гарант
3. НЕ выдумывай статьи
4. Сохраняй структуру

Текст:
{contract_text[:10000]}

ФОРМАТ:
### Анализ
### Проблемы
### Исправленный текст
### Таблица
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        st.download_button(
                            label="📥 Скачать TXT",
                            data=response.text.encode('utf-8'),
                            file_name=f"fixed_{uploaded_file.name}.txt",
                            mime="text/plain; charset=utf-8",
                            use_container_width=True
                        )
                    
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
    
    st.markdown("### 📁 Загрузите файл")
    uploaded_file = st.file_uploader("drag_and_drop_placeholder", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("📝 Получить заключение", type="primary", use_container_width=True):
            with st.spinner("🤖 Готовлю..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    llm = create_llm_engine()
                    
                    prompt = f"""
Ты - старший юрист СЗ Дело с 15+ лет опытом. СЕЙЧАС 2025 ГОД.

Текст:
{contract_text[:10000]}

ТРЕБОВАНИЯ:
1. ИСПОЛЬЗУЙ ТОЛЬКО АКТУАЛЬНЫЕ ЗАКОНЫ НА 2025 ГОД
2. ДАВАЙ КОНКРЕТНЫЕ ОТВЕТЫ
3. УКАЗЫВАЙ ТОЧНЫЕ НОМЕРА СТАТЕЙ ГК РФ
4. УКАЗЫВАЙ ТОЧНЫЕ СРОКИ И ПЕРИОДЫ
5. ПРОВЕРЬ АКТУАЛЬНОСТЬ - перед ответом убедись что закон действует в 2025
6. НЕ ВЫДУМЫВАЙ - проверяй по КонсультантПлюс, Гарант

ФОРМАТ ОТВЕТА СТРОГО:
1. Тип договора
2. Вывод (✅/⚠️/❌) с обоснованием
3. Риски со статьями ГК РФ (актуально на 2025)
4. Конкретные рекомендации
5. Сроки и последствия
6. Источник (КонсультантПлюс/Гарант - актуальная редакция 2025)
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
        <p class="hero-subtitle">Найдите различия между версиями</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Версия 1**")
        file1 = st.file_uploader("drag_and_drop_placeholder", type=['pdf', 'docx', 'txt'], key="v1", label_visibility="collapsed")
    with col2:
        st.markdown("**Версия 2**")
        file2 = st.file_uploader("drag_and_drop_placeholder", type=['pdf', 'docx', 'txt'], key="v2", label_visibility="collapsed")
    
    if file1 and file2:
        temp1 = f"temp_v1_{file1.name}"
        temp2 = f"temp_v2_{file2.name}"
        
        with open(temp1, "wb") as f:
            f.write(file1.getvalue())
        with open(temp2, "wb") as f:
            f.write(file2.getvalue())
        
        if st.button("🔍 Сравнить", type="primary", use_container_width=True):
            with st.spinner("🤖 Сравниваю..."):
                try:
                    from backend.contract_comparator import create_comparator
                    comparator = create_comparator()
                    result = comparator.compare_and_explain(temp1, temp2)
                    
                    st.markdown(f"### 📊 Изменений: {result['total_changes']}")
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
st.markdown('<p style="text-align: center; color: #8fa5b8; font-size: 0.83em; padding: 18px;">© 2025 СЗ Дело | Юридический ИИ</p>', unsafe_allow_html=True)
