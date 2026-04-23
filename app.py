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
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Фон приложения - светлый серый */
    .stApp {
        background: #f0f2f5;
    }
    
    /* Sidebar - тёмно-синий ЧЁТКИЙ */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 3px solid #1e40af !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    button[title="Close sidebar"] {
        display: none !important;
    }
    
    /* Скрываем английские placeholder */
    .stFileUploader > div > p,
    .stFileUploader > div > div > p,
    [data-testid="stFileUploader"] > div > p,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] p {
        display: none !important;
        opacity: 0 !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="baseButton"] {
        display: none !important;
    }
    
    /* Hero секция - ЯРКИЙ синий */
    .hero-section {
        background: #1e40af;
        border-radius: 8px;
        padding: 28px 36px;
        margin: 16px 20px 20px 20px;
        border: 2px solid #1e3a8a;
    }
    
    .hero-title {
        font-size: 2em;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        font-size: 1em;
        color: #bfdbfe;
        margin: 0;
    }
    
    /* Карточки - белый с ЧЁТКОЙ рамкой */
    .info-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 18px;
        margin: 14px 0;
        border: 2px solid #cbd5e1;
    }
    
    /* Кнопки - ЯРКИЙ синий */
    .stButton > button {
        background: #2563eb;
        color: #ffffff;
        border: 2px solid #1d4ed8;
        border-radius: 6px;
        padding: 10px 26px;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
    }
    
    /* Загрузчик файлов - ЧЁТКИЙ */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        border: 2px dashed #64748b;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background: #eff6ff;
    }
    
    /* ЧАТ - ЧЁТКОЕ РАЗДЕЛЕНИЕ БЕЗ РАМОК */
    .chat-user-message {
        background: #2563eb;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 10px 4px 10px 10px;
        margin: 8px 0;
        max-width: 75%;
        margin-left: auto;
    }
    
    .chat-assistant-message {
        background: #ffffff;
        color: #0f172a;
        padding: 14px 18px;
        border-radius: 4px 10px 10px 10px;
        margin: 8px 0;
        max-width: 75%;
        border-left: 4px solid #2563eb;
        border-right: none;
        border-top: none;
        border-bottom: none;
        line-height: 1.6;
    }
    
    .chat-assistant-message p {
        margin: 8px 0;
        text-align: left;
    }
    
    hr {
        border-color: #cbd5e1;
        margin: 16px 0;
    }
    
    strong {
        color: #0f172a !important;
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
        background: #0f172a;
        color: white;
        border: 2px solid #1e40af;
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 1.3em;
        cursor: pointer;
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
    <div style="color: #94a3b8; font-size: 0.8em; padding: 0 8px; line-height: 1.7;">
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
                
                # Улучшенный промпт для чата - чёткая структура с маркерами
                enhanced_prompt = f"""
Ты - старший юрист СЗ Дело. СЕЙЧАС 2025 ГОД.

Вопрос: {prompt}

ТРЕБОВАНИЯ:
1. ОТВЕТ ЧЁТКИЙ, ПРАВИЛЬНЫЙ, БЕЗ ВОДЫ
2. МАКСИМУМ 450 СЛОВ
3. ТОЧНЫЕ НОМЕРА СТАТЕЙ (ст. XXX ГК РФ)
4. АКТУАЛЬНОСТЬ НА 2025 ГОД
5. ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МАРКЕРЫ (-) ДЛЯ СПИСКОВ
6. КАЖДЫЙ БЛОК С НОВОЙ СТРОКИ

ФОРМАТ ОТВЕТА ОБЯЗАТЕЛЬНО:

[1-2 предложения с кратким ответом]

Правовое основание:
- Статья XXX: [краткое пояснение]
- Статья YYY: [краткое пояснение]

[Развёрнутый анализ - 150-200 слов]

Сроки и цифры:
- [конкретный срок 1]
- [конкретный срок 2]

Что делать:
1. [первое действие]
2. [второе действие]
3. [третье действие]

Источник: КонсультантПлюс 2025 (https://www.consultant.ru)

ПРИМЕР ХОРОШЕГО ОТВЕТА:

Срок исковой давности по договору подряда составляет 3 года (ст. 196 ГК РФ).

Правовое основание:
- Статья 196 ГК РФ: общий срок исковой давности 3 года (https://www.consultant.ru/document/cons_doc_LAW_28165/)
- Статья 200 ГК РФ: начало с момента нарушения (https://www.consultant.ru/document/cons_doc_LAW_28165/)
- Статья 725 ГК РФ: специальный срок по подряду (https://www.consultant.ru/document/cons_doc_LAW_28165/)

Согласно ст. 725 ГК РФ, срок исковой давности по требованиям о недостатках работы начинается с момента сдачи работы заказчику. Если недостатки обнаружены позднее, срок исчисляется с момента их обнаружения. Срок нельзя восстановить после истечения.

Сроки и цифры:
- Общий срок: 3 года
- Начало: день сдачи работы или обнаружения недостатков
- Последствия пропуска: отказ в иске (ст. 199 ГК РФ)

Что делать:
1. Фиксируйте дату сдачи работы актом
2. Проводите осмотр после сдачи
3. При недостатках пишите претензию
4. Подавайте иск в течение 3 лет
5. Храните документы 4 года

Источник: КонсультантПлюс 2025 (https://www.consultant.ru/document/cons_doc_LAW_28165/)
"""
                
                response = llm.generate(enhanced_prompt, context=context, task="answer")
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
Ты - юрист СЗ Дело. СЕЙЧАС 2025 ГОД.

Текст договора:
{contract_text[:10000]}

ТРЕБОВАНИЯ:
1. ЧЁТКО И ПРАВИЛЬНО - БЕЗ ВОДЫ
2. МАКСИМУМ 450 СЛОВ
3. ТОЧНЫЕ НОМЕРА СТАТЕЙ ГК РФ
4. АКТУАЛЬНОСТЬ НА 2025
5. ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МАРКЕРЫ (-) ДЛЯ СПИСКОВ

ФОРМАТ ОБЯЗАТЕЛЬНО:

[Тип договора - 1-2 предложения]

Риски:
- [Пункт 1] - [Ст. XXX ГК РФ] - [Уровень риска]
- [Пункт 2] - [Ст. YYY ГК РФ] - [Уровень риска]

Что исправить:
1. [первое действие]
2. [второе действие]
3. [третье действие]

Ссылки на статьи:
- Ст. XXX ГК РФ: https://www.consultant.ru/document/cons_doc_LAW_28165/
- Ст. YYY ГК РФ: https://www.consultant.ru/document/cons_doc_LAW_28165/

Источник: КонсультантПлюс 2025 (https://www.consultant.ru/document/cons_doc_LAW_28165/)
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
Ты - юрист СЗ Дело. СЕЙЧАС 2025 ГОД.

Текст:
{contract_text[:10000]}

ТРЕБОВАНИЯ:
1. ЧЁТКО И ПРАВИЛЬНО - БЕЗ ВОДЫ
2. МАКСИМУМ 450 СЛОВ
3. ТОЧНЫЕ НОМЕРА СТАТЕЙ ГК РФ
4. АКТУАЛЬНОСТЬ НА 2025
5. ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МАРКЕРЫ (-) ДЛЯ СПИСКОВ

ФОРМАТ ОБЯЗАТЕЛЬНО:

[Тип договора - 1-2 предложения]

Вывод: ✅/⚠️/❌ с кратким обоснованием

Риски:
- [Риск 1] - [Ст. XXX ГК РФ]
- [Риск 2] - [Ст. YYY ГК РФ]

Что делать:
1. [первое действие]
2. [второе действие]
3. [третье действие]

Ссылки на статьи:
- Ст. XXX ГК РФ: https://www.consultant.ru/document/cons_doc_LAW_28165/

Источник: КонсультантПлюс 2025 (https://www.consultant.ru/document/cons_doc_LAW_28165/)
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
st.markdown('<p style="text-align: center; color: #64748b; font-size: 0.83em; padding: 18px;">© 2025 СЗ Дело | Юридический ИИ</p>', unsafe_allow_html=True)
