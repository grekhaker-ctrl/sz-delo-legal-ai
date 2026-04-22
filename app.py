import streamlit as st
import os
from datetime import datetime
import hashlib

st.set_page_config(page_title="СЗ Дело | Юридический ИИ-агент", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 2.5em; font-weight: 700; color: #1e3a5f; margin-bottom: 10px; }
.subheader { font-size: 1.2em; color: #666; margin-bottom: 30px; }
.risk-card { padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid; }
.risk-critical { background-color: #ffebee; border-color: #c62828; }
.risk-high { background-color: #fff3e0; border-color: #f57c00; }
.risk-medium { background-color: #fff8e1; border-color: #fbc02d; }
.risk-low { background-color: #e8f5e9; border-color: #2e7d32; }
</style>
""", unsafe_allow_html=True)

if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_contract' not in st.session_state:
    st.session_state.current_contract = None

with st.sidebar:
    st.title("⚖️ СЗ Дело")
    st.markdown("**Юридический ИИ-агент**")
    st.divider()
    menu = st.radio("Разделы", ["💬 Чат", "📄 Анализ рисков", "⚖️ Заключение", "📝 Шаблон", "🔄 Сравнение", "📚 База знаний"], label_visibility="collapsed")
    st.divider()
    st.markdown("### ℹ️ О системе")
    st.markdown("- **LLM:** YandexGPT + GigaChat\n- **Работа:** Без VPN, РФ")
    if st.button("🗑️ Очистить историю", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

def render_chat():
    st.markdown('<p class="main-header">💬 Чат с ИИ-юристом</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Задавайте вопросы по ФЗ, ГК РФ, договорам</p>', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Введите ваш вопрос (например: 159 ФЗ, что такое неустойка)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Отвечаю..."):
                try:
                    from backend.llm_engine import create_llm_engine
                    from backend.legal_kb import create_legal_kb
                    
                    llm = create_llm_engine()
                    kb = create_legal_kb()
                    context = kb.search(prompt, sources=['local'])
                    response = llm.generate(prompt, context=context)
                    
                    st.markdown(response.text if response.text else "⚠️ Не удалось получить ответ")
                    st.session_state.messages.append({"role": "assistant", "content": response.text if response.text else "Ошибка"})
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Ошибка: {str(e)}"})

def render_analyze():
    st.markdown('<p class="main-header">📄 Анализ рисков договора</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Загрузите договор (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("🔍 Начать анализ", type="primary", use_container_width=True):
            with st.spinner("Анализирую..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.risk_analyzer import create_risk_analyzer
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    analyzer = create_risk_analyzer()
                    risks = analyzer.analyze_contract(contract_text)
                    conclusion = analyzer.get_conclusion(risks)
                    score = analyzer.calculate_risk_score(risks)
                    
                    st.markdown(f"### {conclusion}")
                    st.metric("Уровень риска", f"{score}/10")
                    
                    for i, risk in enumerate(risks, 1):
                        risk_class = f"risk-{risk.risk_level.value}"
                        st.markdown(f"""<div class="risk-card {risk_class}"><strong>{i}. {risk.title}</strong><br><small>{risk.risk_level.value.upper()}</small></div>""", unsafe_allow_html=True)
                        with st.expander(f"Подробнее {i}"):
                            st.markdown(f"**Описание:** {risk.description}\n\n**Рекомендация:** {risk.recommendation}")
                            if risk.proposed_text:
                                st.info(f"**Новая формулировка:**\n{risk.proposed_text}")
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

def render_conclusion():
    st.markdown('<p class="main-header">⚖️ Юридическое заключение</p>', unsafe_allow_html=True)
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
                    prompt = f"Дай юридическое заключение по договору для СЗ Дело (Москва/МО):\n\n{contract_text[:10000]}"
                    response = llm.generate(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

def render_fill():
    st.markdown('<p class="main-header">📝 Заполнить шаблон</p>', unsafe_allow_html=True)
    st.info("Шаблоны в data/templates/. Создайте .docx файлы с переменными {{name}}")
    
    col1, col2 = st.columns(2)
    with col1:
        contract_number = st.text_input("Номер договора")
        customer_name = st.text_input("Заказчик")
        customer_inn = st.text_input("ИНН Заказчика")
    with col2:
        contract_date = st.date_input("Дата", value=datetime.now())
        contractor_name = st.text_input("Подрядчик")
        contractor_inn = st.text_input("ИНН Подрядчика")
    
    if st.button("📄 Заполнить", type="primary", use_container_width=True):
        st.success("✅ Шаблон готов! (нужно добавить шаблоны в data/templates/)")

def render_compare():
    st.markdown('<p class="main-header">🔄 Сравнить версии</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Версия 1", type=['pdf', 'docx', 'txt'], key="v1")
    with col2:
        file2 = st.file_uploader("Версия 2", type=['pdf', 'docx', 'txt'], key="v2")
    
    if file1 and file2:
        if st.button("🔍 Сравнить", type="primary", use_container_width=True):
            st.success("✅ Сравнение готово! (требуется настройка contract_comparator.py)")

def render_kb():
    st.markdown('<p class="main-header">📚 База знаний</p>', unsafe_allow_html=True)
    query = st.text_input("Поиск", placeholder="неустойка, гарантийный срок...")
    if st.button("🔍 Поиск", type="primary", use_container_width=True):
        if query:
            with st.spinner("Ищу..."):
                try:
                    from backend.legal_kb import create_legal_kb
                    kb = create_legal_kb()
                    context = kb.search(query)
                    st.markdown(context)
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")

if menu == "💬 Чат":
    render_chat()
elif menu == "📄 Анализ рисков":
    render_analyze()
elif menu == "⚖️ Заключение":
    render_conclusion()
elif menu == "📝 Шаблон":
    render_fill()
elif menu == "🔄 Сравнение":
    render_compare()
elif menu == "📚 База знаний":
    render_kb()

st.divider()
st.markdown("<div style='text-align: center; color: #666;'>© 2025 СЗ Дело | Юридический ИИ-агент</div>", unsafe_allow_html=True)
