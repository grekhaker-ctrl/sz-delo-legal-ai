"""
СЗ Дело | Юридический ИИ-агент
Веб-приложение для юридического отдела строительной компании
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

# Кастомные стили
st.markdown("""
<style>
    /* Фирменные цвета */
    :root {
        --primary-color: #1e3a5f;  /* Тёмно-синий */
        --success-color: #2e7d32;  /* Зелёный */
        --warning-color: #f57c00;  /* Оранжевый */
        --danger-color: #c62828;   /* Красный */
    }
    
    /* Заголовки */
    .main-header {
        font-size: 2.5em;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 10px;
    }
    
    .subheader {
        font-size: 1.2em;
        color: #666;
        margin-bottom: 30px;
    }
    
    /* Карточки рисков */
    .risk-card {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    
    .risk-critical {
        background-color: #ffebee;
        border-color: #c62828;
    }
    
    .risk-high {
        background-color: #fff3e0;
        border-color: #f57c00;
    }
    
    .risk-medium {
        background-color: #fff8e1;
        border-color: #fbc02d;
    }
    
    .risk-low {
        background-color: #e8f5e9;
        border-color: #2e7d32;
    }
    
    /* Кнопки */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        padding: 10px 24px;
    }
    
    /* Diff */
    .diff-added {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .diff-removed {
        background-color: #ffebee;
        color: #c62828;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация сессии
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_contract' not in st.session_state:
    st.session_state.current_contract = None

if 'current_contract_name' not in st.session_state:
    st.session_state.current_contract_name = None


# ============================================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2275/2275970.png", width=80)
    st.title("СЗ Дело")
    st.markdown("**Юридический ИИ-агент**")
    
    st.divider()
    
    # Навигация
    menu = st.radio(
        "Разделы",
        [
            "💬 Чат с ИИ-юристом",
            "📄 Анализ рисков договора",
            "⚖️ Юридическое заключение",
            "📝 Заполнить шаблон",
            "🔄 Сравнить версии",
            "📚 База знаний",
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Информация
    st.markdown("### ℹ️ О системе")
    st.markdown("""
    - **Компания:** СЗ Дело
    - **Специализация:** Строительство ЖК в Москве и МО
    - **LLM:** YandexGPT + GigaChat
    - **Работа:** Без VPN, РФ
    """)
    
    # Кнопка очистки
    if st.button("🗑️ Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================================================
# ГЛАВНЫЙ ЭКРАН
# ============================================================================

def render_chat():
    """Чат с ИИ-юристом"""
    st.markdown('<p class="main-header">💬 Чат с ИИ-юристом</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Задавайте юридические вопросы по договорам и строительному праву</p>', unsafe_allow_html=True)
    
    # Отображение истории сообщений
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Ввод пользователя
    if prompt := st.chat_input("Введите ваш юридический вопрос..."):
        # Добавление сообщения пользователя
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Генерация ответа
        with st.chat_message("assistant"):
            with st.spinner("Анализирую вопрос..."):
                try:
                    from backend.llm_engine import create_llm_engine
                    from backend.legal_kb import create_legal_kb
                    
                    llm = create_llm_engine()
                    kb = create_legal_kb()
                    
                    # Поиск контекста в базе знаний
                    context = kb.search(prompt, sources=['local'])
                    
                    # Генерация ответа
                    response = llm.generate(prompt, context=context)
                    
                    st.markdown(response.text)
                    
                    # Добавление ответа в историю
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.text
                    })
                    
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")


def render_conclusion():
    """Юридическое заключение"""
    st.markdown('<p class="main-header">⚖️ Юридическое заключение</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Получите профессиональное заключение по договору</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Загрузите договор",
        type=['pdf', 'docx', 'txt']
    )
    
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
Проанализируй договор и дай юридическое заключение для строительной компании СЗ Дело (Москва/МО).

Текст договора:
{contract_text[:10000]}  # Ограничение по длине

Формат ответа:
1. Тип договора
2. Заключение (✅ Можно подписывать / ⚠️ С правками / ❌ Не рекомендуется)
3. Ключевые риски
4. Рекомендации по изменениям
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
    st.markdown('<p class="main-header">📝 Заполнить шаблон договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Автоматическое заполнение шаблона по реквизитам</p>', unsafe_allow_html=True)
    
    from backend.contract_filler import create_filler
    
    filler = create_filler()
    templates = filler.get_available_templates()
    
    if not templates:
        st.info("Шаблоны не найдены. Разместите файлы .docx в папке data/templates/")
        return
    
    # Выбор шаблона
    template_options = {t['name']: t for t in templates}
    selected_name = st.selectbox("Выберите шаблон", list(template_options.keys()))
    selected_template = template_options[selected_name]
    
    st.markdown(f"**Файл:** `{selected_template['filename']}`")
    
    # Форма для реквизитов
    st.markdown("### Реквизиты")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contract_number = st.text_input("Номер договора")
        customer_name = st.text_input("Заказчик (название)")
        customer_inn = st.text_input("ИНН Заказчика")
    
    with col2:
        contract_date = st.date_input("Дата договора", value=datetime.now())
        contractor_name = st.text_input("Подрядчик (название)")
        contractor_inn = st.text_input("ИНН Подрядчика")
    
    object_address = st.text_input("Адрес объекта строительства")
    contract_price = st.text_input("Цена договора (рублей)")
    work_description = st.text_area("Описание работ")
    
    if st.button("📄 Заполнить шаблон", type="primary", use_container_width=True):
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
            
            # Скачивание
            with open(output_path, "rb") as f:
                st.download_button(
                    "📥 Скачать договор",
                    data=f.read(),
                    file_name=f"contract_{contract_number}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")


def render_compare():
    """Сравнение версий"""
    st.markdown('<p class="main-header">🔄 Сравнить версии договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Сравните две версии договора и узнайте о юридических последствиях изменений</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        file1 = st.file_uploader("Версия 1", type=['pdf', 'docx', 'txt'], key="v1")
    
    with col2:
        file2 = st.file_uploader("Версия 2", type=['pdf', 'docx', 'txt'], key="v2")
    
    if file1 and file2:
        # Сохранение файлов
        temp1 = f"temp_v1_{file1.name}"
        temp2 = f"temp_v2_{file2.name}"
        
        with open(temp1, "wb") as f:
            f.write(file1.getvalue())
        with open(temp2, "wb") as f:
            f.write(file2.getvalue())
        
        if st.button("🔍 Сравнить версии", type="primary", use_container_width=True):
            with st.spinner("Сравниваю версии..."):
                try:
                    from backend.contract_comparator import create_comparator
                    from backend.llm_engine import create_llm_engine
                    
                    comparator = create_comparator()
                    
                    # Сравнение
                    result = comparator.compare_and_explain(temp1, temp2)
                    
                    # Результаты
                    st.markdown(f"### Найдено изменений: {result['total_changes']}")
                    
                    # HTML diff
                    st.markdown("### 📊 Визуальное сравнение")
                    st.components.v1.html(result['diff_html'], height=400, scrolling=True)
                    
                    # Юридический анализ
                    st.markdown("### ⚖️ Юридические последствия")
                    st.markdown(result['legal_analysis'])
                    
                    if result['llm_explanation']:
                        st.markdown("### 🤖 Объяснение ИИ")
                        st.markdown(result['llm_explanation'])
                    
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp1):
                        os.remove(temp1)
                    if os.path.exists(temp2):
                        os.remove(temp2)


def render_kb():
    """База знаний"""
    st.markdown('<p class="main-header">📚 База знаний</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Поиск по Гарант, КонсультантПлюс и внутренней базе СЗ Дело</p>', unsafe_allow_html=True)
    
    query = st.text_input("Поисковый запрос", placeholder="Например: неустойка по договору подряда")
    
    if st.button("🔍 Поиск", type="primary", use_container_width=True):
        if not query:
            st.warning("Введите поисковый запрос")
        else:
            with st.spinner("Ищу в базах знаний..."):
                try:
                    from backend.legal_kb import create_legal_kb
                    
                    kb = create_legal_kb()
                    context = kb.search(query)
                    
                    st.markdown("### Результаты поиска")
                    st.markdown(context)
                    
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")


# ============================================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================================

if menu == "💬 Чат с ИИ-юристом":
    render_chat()

elif menu == "📄 Анализ рисков договора":
    render_analyze()

elif menu == "⚖️ Юридическое заключение":
    render_conclusion()

elif menu == "📝 Заполнить шаблон":
    render_fill()

elif menu == "🔄 Сравнить версии":
    render_compare()

elif menu == "📚 База знаний":
    render_kb()


# ============================================================================
# ПОДВАЛ
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>© 2025 СЗ Дело | Юридический ИИ-агент</p>
    <p>Система работает на базе YandexGPT и GigaChat (РФ, без VPN)</p>
</div>
""", unsafe_allow_html=True)
