"""
СЗ Дело | Юридический ИИ-агент
Профессиональное приложение для юридического отдела
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import hashlib

# Настройка страницы
st.set_page_config(
    page_title="СЗ Дело | Юридический ИИ-агент",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ПРОФЕССИОНАЛЬНЫЙ ДИЗАЙН
# ============================================================================

st.markdown("""
<style>
    /* Цветовая палитра */
    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --secondary: #64748b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-light: #f8fafc;
        --bg-dark: #1e293b;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --border: #e2e8f0;
    }
    
    /* Основной фон */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Заголовки */
    .main-header {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .subheader {
        font-size: 1.2em;
        color: #64748b;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #f1f5f9;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }
    
    /* Карточки */
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    
    /* Карточки рисков */
    .risk-card {
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        border-left: 5px solid;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .risk-critical {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-color: #dc2626;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border-color: #ea580c;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
        border-color: #ca8a04;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-color: #16a34a;
    }
    
    /* Кнопки */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 12px 32px;
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        border: none;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
    }
    
    /* Чат */
    .chat-message {
        padding: 16px 20px;
        border-radius: 16px;
        margin: 12px 0;
        max-width: 85%;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        margin-left: auto;
    }
    
    .chat-assistant {
        background: white;
        border: 1px solid #e2e8f0;
        color: #0f172a;
    }
    
    /* Статус бары */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: 600;
        margin: 4px 8px 4px 0;
    }
    
    .status-success {
        background: #dcfce7;
        color: #16a34a;
    }
    
    .status-error {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #d97706;
    }
    
    /* Таблицы */
    .changes-table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .changes-table th {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        padding: 14px 16px;
        text-align: left;
        font-weight: 600;
    }
    
    .changes-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .changes-table tr:hover {
        background: #f8fafc;
    }
    
    /* Code blocks */
    .contract-text {
        background: #1e293b;
        color: #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
        line-height: 1.6;
        overflow-x: auto;
        margin: 16px 0;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 32px 0;
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.95em;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()

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
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3.5em; margin-bottom: 10px;">⚖️</div>
        <h1 style="color: #f1f5f9; margin: 0; font-size: 1.8em;">СЗ ДЕЛО</h1>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.95em;">Юридический ИИ-агент</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Навигация
    st.markdown("### 🧭 Навигация")
    menu = st.radio(
        "Разделы",
        [
            "💬 Чат с ИИ-юристом",
            "📄 Анализ и исправление договора",
            "⚖️ Юридическое заключение",
            "📝 Заполнить шаблон",
            "🔄 Сравнить версии",
            "📚 База знаний",
        ],
        label_visibility="collapsed",
        index=0
    )
    
    st.divider()
    
    # Статус ИИ
    st.markdown("### 🔧 Статус системы")
    try:
        from backend.llm_engine import create_llm_engine
        llm = create_llm_engine()
        status = llm.get_status()
        for name, ok in status.items():
            if ok:
                st.markdown(f'<span class="status-badge status-success">✅ {name}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="status-badge status-error">❌ {name}</span>', unsafe_allow_html=True)
        
        if not any(status.values()):
            st.markdown("""
            <div style="background: #fef2f2; padding: 16px; border-radius: 10px; margin: 16px 0;">
                <p style="color: #dc2626; margin: 0; font-weight: 600;">⚠️ Нет активных LLM</p>
                <p style="color: #dc2626; margin: 8px 0 0 0; font-size: 0.9em;">Добавьте POLZA_API_KEY в Secrets</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")
    
    st.divider()
    
    # Информация
    st.markdown("### ℹ️ О системе")
    st.markdown("""
    <div style="color: #94a3b8; font-size: 0.9em; line-height: 1.8;">
        <p><strong>🏢 Компания:</strong> СЗ Дело</p>
        <p><strong>🏗️ Специализация:</strong> Строительство ЖК в Москве и МО</p>
        <p><strong>🤖 LLM:</strong> Polza AI (GPT-4)</p>
        <p><strong>🌍 Работа:</strong> Без VPN, РФ</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопка очистки
    st.divider()
    if st.button("🗑️ Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================================
# ФУНКЦИИ
# ============================================================================

def render_chat():
    """Чат с ИИ-юристом"""
    st.markdown('<p class="main-header">💬 Чат с ИИ-юристом</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Задавайте юридические вопросы по договорам и строительному праву</p>', unsafe_allow_html=True)
    
    # История чата
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Ввод
    if prompt := st.chat_input("Введите ваш юридический вопрос..."):
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
                    st.error(f"Ошибка: {str(e)}")


def render_analyze():
    """Анализ и исправление договора"""
    st.markdown('<p class="main-header">📄 Анализ и исправление договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Загрузите договор для анализа рисков и получения исправленной версии</p>', unsafe_allow_html=True)
    
    # Загрузка файла
    uploaded_file = st.file_uploader(
        "Загрузите договор (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Максимальный размер файла: 10 МБ"
    )
    
    if uploaded_file:
        # Отображение информации о файле
        st.markdown(f"""
        <div class="card">
            <strong>📎 Файл:</strong> {uploaded_file.name}<br>
            <strong>📊 Размер:</strong> {uploaded_file.size / 1024:.1f} КБ
        </div>
        """, unsafe_allow_html=True)
        
        # Опции анализа
        st.markdown("### ⚙️ Параметры анализа")
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
                    contract_text = parser.parse_file(f"temp_{uploaded_file.name}")
                    
                    # Сохраняем текст в сессию
                    st.session_state.analyzed_contract = contract_text
                    
                    llm = create_llm_engine()
                    
                    # Анализ рисков
                    if analyze_risks:
                        st.markdown("### 📊 Результаты анализа")
                        
                        risk_prompt = f"""
Проанализируй договор строительного подряда для компании СЗ Дело (Москва/МО).

Текст договора:
{contract_text[:10000]}

Формат ответа:
### 🔍 Тип договора
[Определение]

### ⚠️ Найденные риски
1. [Риск] - [Статья ГК РФ] - [Уровень: Критический/Высокий/Средний/Низкий]
2. ...

### 📋 Рекомендации
[Конкретные рекомендации по устранению рисков]
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    # Исправление договора
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия договора")
                        
                        fix_prompt = f"""
Проанализируй и исправь договор для строительной компании СЗ Дело.

Оригинальный текст:
{contract_text[:10000]}

Твоя задача:
1. Найти все рискованные пункты
2. Предложить исправленный текст
3. Указать статьи ГК РФ

Формат ответа:
### 📊 Анализ
[Краткий анализ]

### ⚠️ Проблемные пункты
1. [Пункт] - [Проблема] - [Статья ГК]
2. ...

### ✅ Исправленный текст договора
[ПОЛНЫЙ текст с исправлениями]

### 📝 Таблица изменений
| № | Было | Стало | Обоснование |
|---|------|-------|-------------|
| ... | ... | ... | ... |
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        # Кнопка скачивания
                        st.download_button(
                            label="📥 Скачать исправленный договор",
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
    """Юридическое заключение"""
    st.markdown('<p class="main-header">⚖️ Юридическое заключение</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Получите профессиональное заключение по договору</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Загрузите договор", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("📝 Получить заключение", type="primary", use_container_width=True):
            with st.spinner("Готовлю заключение..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    llm = create_llm_engine()
                    
                    prompt = f"""
Проанализируй договор и дай юридическое заключение для СЗ Дело (Москва/МО).

Текст договора:
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


def render_fill():
    """Заполнение шаблонов"""
    st.markdown('<p class="main-header">📝 Заполнить шаблон</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Автоматическое заполнение шаблона по реквизитам</p>', unsafe_allow_html=True)
    
    from backend.contract_filler import create_filler
    
    filler = create_filler()
    templates = filler.get_available_templates()
    
    if not templates:
        st.info("Шаблоны не найдены. Разместите файлы .docx в папке data/templates/")
        return
    
    template_options = {t['name']: t for t in templates}
    selected_name = st.selectbox("Выберите шаблон", list(template_options.keys()))
    selected_template = template_options[selected_name]
    
    st.markdown(f"**Файл:** `{selected_template['filename']}`")
    
    col1, col2 = st.columns(2)
    with col1:
        contract_number = st.text_input("Номер договора")
        customer_name = st.text_input("Заказчик")
        customer_inn = st.text_input("ИНН Заказчика")
    
    with col2:
        contract_date = st.date_input("Дата", value=datetime.now())
        contractor_name = st.text_input("Подрядчик")
        contractor_inn = st.text_input("ИНН Подрядчика")
    
    object_address = st.text_input("Адрес объекта")
    contract_price = st.text_input("Цена договора")
    work_description = st.text_area("Описание работ")
    
    if st.button("📄 Заполнить", type="primary", use_container_width=True):
        try:
            data = {
                'contract_number': contract_number or "№ ___",
                'contract_date': contract_date.strftime('%d.%m.%Y'),
                'customer_name': customer_name or "________",
                'customer_inn': customer_inn or "________",
                'contractor_name': contractor_name or "________",
                'contractor_inn': contractor_inn or "________",
                'object_address': object_address or "________",
                'contract_price': contract_price or "________",
                'work_description': work_description or "________",
            }
            
            output_path = filler.fill_template(selected_template['path'], data)
            st.success("✅ Шаблон заполнен!")
            
            with open(output_path, "rb") as f:
                st.download_button(
                    "📥 Скачать",
                    data=f.read(),
                    file_name=f"contract_{contract_number}.docx",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")


def render_compare():
    """Сравнение версий"""
    st.markdown('<p class="main-header">🔄 Сравнить версии</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Сравните две версии договора</p>', unsafe_allow_html=True)
    
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
                    st.components.v1.html(result['diff_html'], height=400, scrolling=True)
                    st.markdown("### Юридические последствия")
                    st.markdown(result['legal_analysis'])
                    
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp1): os.remove(temp1)
                    if os.path.exists(temp2): os.remove(temp2)


def render_kb():
    """База знаний"""
    st.markdown('<p class="main-header">📚 База знаний</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Поиск по законодательству РФ</p>', unsafe_allow_html=True)
    
    query = st.text_input("Поисковый запрос", placeholder="Например: неустойка по договору подряда")
    
    if st.button("🔍 Поиск", type="primary", use_container_width=True):
        if not query:
            st.warning("Введите запрос")
        else:
            with st.spinner("Ищу..."):
                try:
                    from backend.legal_kb import create_legal_kb
                    kb = create_legal_kb()
                    context = kb.search(query)
                    st.markdown("### Результаты")
                    st.markdown(context)
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")


# ============================================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================================

if menu == "💬 Чат с ИИ-юристом":
    render_chat()
elif menu == "📄 Анализ и исправление договора":
    render_analyze()
elif menu == "⚖️ Юридическое заключение":
    render_conclusion()
elif menu == "📝 Заполнить шаблон":
    render_fill()
elif menu == "🔄 Сравнить версии":
    render_compare()
elif menu == "📚 База знаний":
    render_kb()

# Подвал
st.divider()
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.9em; padding: 20px 0;">
    <p style="margin: 0;">© 2025 СЗ Дело | Юридический ИИ-агент</p>
    <p style="margin: 8px 0 0 0;">Polza AI • GigaChat • YandexGPT</p>
</div>
""", unsafe_allow_html=True)
