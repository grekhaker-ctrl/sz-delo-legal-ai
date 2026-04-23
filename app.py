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
# СОВРЕМЕННЫЙ ДИЗАЙН
# ============================================================================

st.markdown("""
<style>
    /* Цветовая палитра */
    :root {
        --primary: #3b82f6;
        --primary-dark: #1d4ed8;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-gray: #f8fafc;
    }
    
    /* Фон приложения */
    .stApp {
        background: #f8fafc;
    }
    
    /* Заголовки */
    .main-header {
        font-size: 2.2em;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .subheader {
        font-size: 1.1em;
        color: #64748b;
        margin-bottom: 24px;
    }
    
    /* Карточки */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Карточки рисков */
    .risk-card {
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid;
        background: white;
    }
    
    .risk-critical { border-left-color: #dc2626; background: #fef2f2; }
    .risk-high { border-left-color: #ea580c; background: #fff7ed; }
    .risk-medium { border-left-color: #ca8a04; background: #fefce8; }
    .risk-low { border-left-color: #16a34a; background: #f0fdf4; }
    
    /* Кнопки */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        background: #3b82f6;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    /* Статус бейджи */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    .status-success { background: #dcfce7; color: #16a34a; }
    .status-error { background: #fee2e2; color: #dc2626; }
    
    /* Чат */
    .chat-message {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    /* Divider */
    hr {
        border-color: #e2e8f0;
        margin: 24px 0;
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
    # Логотип
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 3em; margin-bottom: 8px;">⚖️</div>
        <h1 style="color: white; margin: 0; font-size: 1.6em;">СЗ ДЕЛО</h1>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.9em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🧭 Навигация")
    menu = st.radio(
        "Разделы",
        [
            "💬 Чат с ИИ-юристом",
            "📄 Анализ и исправление договора",
            "⚖️ Юридическое заключение",
            "🔄 Сравнить версии",
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
    st.divider()
    st.markdown("### ℹ️ О системе")
    st.markdown("""
    <div style="color: #94a3b8; font-size: 0.9em; line-height: 1.8;">
        <p><strong>🏢 Компания:</strong> СЗ Дело</p>
        <p><strong>🏗️ Строительство:</strong> Москва и МО</p>
        <p><strong>🤖 ИИ:</strong> Polza AI</p>
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
    st.markdown('<p class="main-header">📄 Анализ договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Загрузите договор — ИИ найдёт риски и исправит текст</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Загрузите договор",
        type=['pdf', 'docx', 'txt'],
        help="Максимум 10 МБ"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="card">
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
                    contract_text = parser.parse_file(f"temp_{uploaded_file.name}")
                    st.session_state.analyzed_contract = contract_text
                    llm = create_llm_engine()
                    
                    # Анализ рисков
                    if analyze_risks:
                        st.markdown("### 📊 Результаты анализа")
                        risk_prompt = f"""
Проанализируй договор строительного подряда для СЗ Дело (Москва/МО).

Текст:
{contract_text[:10000]}

Формат:
### 🔍 Тип договора
[Определение]

### ⚠️ Риски
1. [Риск] - [Статья ГК] - [Уровень]
2. ...

### 📋 Рекомендации
[Советы]
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    # Исправление
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия")
                        fix_prompt = f"""
Исправь договор для СЗ Дело.

Текст:
{contract_text[:10000]}

Формат:
### 📊 Анализ
[Кратко]

### ⚠️ Проблемы
1. [Пункт] - [Проблема] - [Статья ГК]

### ✅ Исправленный текст
[ПОЛНЫЙ текст с исправлениями]

### 📝 Изменения
| № | Было | Стало | Почему |
|---|------|-------|--------|
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        st.download_button(
                            label="📥 Скачать исправленный",
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


# ============================================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================================

if menu == "💬 Чат с ИИ-юристом":
    render_chat()
elif menu == "📄 Анализ и исправление договора":
    render_analyze()
elif menu == "⚖️ Юридическое заключение":
    render_conclusion()
elif menu == "🔄 Сравнить версии":
    render_compare()

# Подвал
st.divider()
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.9em; padding: 20px 0;">
    <p style="margin: 0;">© 2025 СЗ Дело | Юридический ИИ-агент</p>
    <p style="margin: 8px 0 0 0;">Polza AI • GigaChat • YandexGPT</p>
</div>
""", unsafe_allow_html=True)
