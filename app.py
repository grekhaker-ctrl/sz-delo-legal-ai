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

# ============================================================================
# CSS - Меню всегда видно + чёткий дизайн
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Скрываем стандартные элементы Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar - ВСЕГДА ВИДИМ, нельзя скрыть */
    [data-testid="stSidebarCloseButton"] {
        display: none !important;
    }
    
    [data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        height: 100vh !important;
        overflow: hidden !important;
        background: linear-gradient(180deg, #1e3a5f 0%, #2d5a87 100%) !important;
        border-right: 2px solid #3d7ab5 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Главный контейнер - сдвиг вправо */
    .stApp {
        margin-left: 280px !important;
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        min-height: 100vh;
    }
    
    /* Шрифт */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hero секция */
    .hero-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
        border-radius: 12px;
        padding: 32px 40px;
        margin: 20px 24px 24px 24px;
        box-shadow: 0 8px 24px rgba(30, 58, 95, 0.3);
    }
    
    .hero-title {
        font-size: 2.2em;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        font-size: 1.05em;
        color: #bfdbfe;
        margin: 0;
    }
    
    /* Карточки */
    .info-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 18px;
        margin: 16px 0;
        border: 1px solid #bcccdc;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 11px 26px;
        font-weight: 600;
        font-size: 0.93em;
        transition: all 0.25s ease;
        box-shadow: 0 3px 10px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 18px rgba(37, 99, 235, 0.4);
    }
    
    /* Загрузчик файлов */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 10px;
        padding: 22px;
        border: 2px dashed #7a8fa3;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background: #e8f1f8;
    }
    
    /* ЧАТ - ЧЁТКОЕ РАЗДЕЛЕНИЕ */
    .chat-user-message {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 15px 19px;
        border-radius: 14px 3px 14px 14px;
        margin: 11px 0;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 0 3px 11px rgba(37, 99, 235, 0.28);
        line-height: 1.5;
    }
    
    .chat-assistant-message {
        background: #ffffff;
        color: #1e293b;
        padding: 15px 19px;
        border-radius: 3px 14px 14px 14px;
        margin: 11px 0;
        max-width: 75%;
        border: 1px solid #bcccdc;
        box-shadow: 0 3px 11px rgba(0, 0, 0, 0.09);
        line-height: 1.5;
    }
    
    /* Разделители */
    hr {
        border-color: #bcccdc;
        margin: 22px 0;
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
    <div style="color: #9fb8d0; font-size: 0.8em; padding: 0 8px; line-height: 1.7;">
        <p><strong>🌐 Ссылка:</strong></p>
        <p style="color: #bfdbfe; word-break: break-all;">https://sz-delo-legal-ai.streamlit.app</p>
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
    
    uploaded_file = st.file_uploader("", type=['pdf', 'docx', 'txt'])
    
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
Ты - опытный юрист строительной компании СЗ Дело (Москва/МО).

ТРЕБОВАНИЯ:
1. ТОЛЬКО актуальные законы РФ (2024-2025)
2. Проверяй: КонсультантПлюс, Гарант, vsrf.ru
3. НЕ выдумывай статьи
4. Указывай точные номера статей

Текст:
{contract_text[:10000]}

ФОРМАТ:
### Тип договора
[Определение]

### Риски
1. [Пункт] - [Статья ГК РФ] - [Уровень]

### Рекомендации
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
    uploaded_file = st.file_uploader("", type=['pdf', 'docx', 'txt'])
    
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
Ты - юрист СЗ Дело.

ТРЕБОВАНИЯ:
1. ТОЛЬКО актуальные законы РФ
2. Проверяй: КонсультантПлюс, Гарант
3. НЕ выдумывай статьи

Текст:
{contract_text[:10000]}

ФОРМАТ:
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
        <p class="hero-subtitle">Найдите различия между версиями</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Версия 1**")
        file1 = st.file_uploader("", type=['pdf', 'docx', 'txt'], key="v1")
    with col2:
        st.markdown("**Версия 2**")
        file2 = st.file_uploader("", type=['pdf', 'docx', 'txt'], key="v2")
    
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
st.markdown('<p style="text-align: center; color: #7a8fa3; font-size: 0.83em; padding: 18px;">© 2025 СЗ Дело | Юридический ИИ</p>', unsafe_allow_html=True)
