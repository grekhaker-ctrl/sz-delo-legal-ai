import streamlit as st
import os
from datetime import datetime
import hashlib

st.set_page_config(page_title="СЗ Дело | ИИ-юрист", page_icon="⚖️", layout="wide")

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

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_contract' not in st.session_state:
    st.session_state.current_contract = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()

with st.sidebar:
    st.title("⚖️ СЗ Дело")
    st.markdown("**ИИ-юрист**")
    st.divider()
    menu = st.radio("Разделы", ["💬 Чат", "📄 Анализ рисков", "⚖️ Заключение", "📝 Шаблон", "🔄 Сравнение", "📚 База знаний"], label_visibility="collapsed")
    st.divider()
    st.markdown("### ℹ️ О системе")
    st.markdown("- **ИИ:** GigaChat + YandexGPT\n- **Специализация:** Строительство\n- **Регион:** Москва/МО")
    if st.button("🗑️ Очистить историю", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

def render_chat():
    st.markdown('<p class="main-header">💬 Чат с ИИ-юристом</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Задавайте вопросы по ФЗ, ГК РФ, договорам</p>', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Введите вопрос (например: 159 ФЗ, неустойка, гарантийный срок)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("ИИ анализирует..."):
                try:
                    from backend.llm_engine import create_llm_engine
                    from backend.legal_kb import create_legal_kb
                    
                    llm = create_llm_engine()
                    kb = create_legal_kb()
                    context = kb.search(prompt, sources=['local'])
                    response = llm.generate(prompt, context=context)
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("⚠️ Не удалось получить ответ")
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")

def render_analyze():
    st.markdown('<p class="main-header">📄 Анализ рисков договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Загрузите договор для анализа рисков и ИИ-заключения</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Загрузите договор (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'], help="Максимальный размер: 50MB")
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.success(f"✅ Файл загружен: {uploaded_file.name} ({round(uploaded_file.size/1024/1024, 2)} MB)")
        
        if st.button("🔍 Анализировать договор", type="primary", use_container_width=True):
            with st.spinner("🤖 ИИ анализирует договор..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.risk_analyzer import create_risk_analyzer
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    
                    if not contract_text or len(contract_text) < 100:
                        st.error("⚠️ Не удалось извлечь текст из файла. Проверьте формат.")
                        return
                    
                    st.markdown(f"### 📄 Информация о документе")
                    st.info(f"**Размер текста:** {len(contract_text)} символов\n\n**Первые 500 символов:**\n\n{contract_text[:500]}...")
                    
                    analyzer = create_risk_analyzer()
                    risks = analyzer.analyze_contract(contract_text)
                    score = analyzer.calculate_risk_score(risks)
                    conclusion = analyzer.get_conclusion(risks)
                    
                    st.markdown(f"### {conclusion}")
                    st.metric("📊 Уровень риска", f"{score}/10", delta_color="inverse")
                    
                    st.markdown("### 🤖 ИИ-заключение по договору")
                    with st.spinner("ИИ готовит развёрнутое заключение..."):
                        llm = create_llm_engine()
                        llm_prompt = f"""Ты — юрист СЗ Дело (Москва/МО). Дай профессиональное заключение по договору.

ТЕКСТ ДОГОВОРА:
{contract_text[:6000]}

НАЙДЕННЫЕ РИСКИ:
{chr(10).join([f'- {r.title}: {r.description}' for r in risks])}

ДАЙ РАЗВЁРНУТЫЙ ОТВЕТ:
1. Тип договора (подряд, субподряд, поставка)
2. Существенные условия (предмет, срок, цена) — указаны ли?
3. Ключевые риски для СЗ Дело (минимум 3)
4. Рекомендации по изменениям (конкретные формулировки)
5. Статьи ГК РФ которые нарушены
6. Вердикт: можно подписывать / с правками / нельзя

Отвечай структурированно, с заголовками и списками."""
                        
                        llm_response = llm.generate(llm_prompt)
                        
                        if llm_response and llm_response.text:
                            st.markdown(llm_response.text)
                        else:
                            st.warning("⚠️ ИИ не ответил. Показываем базовый анализ.")
                    
                    if risks:
                        st.markdown("### 📋 Детальный разбор рисков")
                        for i, risk in enumerate(risks, 1):
                            risk_class = f"risk-{risk.risk_level.value}"
                            emoji = "🔴" if risk.risk_level.value == "critical" else "🟠" if risk.risk_level.value == "high" else "🟡" if risk.risk_level.value == "medium" else "🟢"
                            
                            st.markdown(f"""<div class="risk-card {risk_class}">
                                <strong>{emoji} {i}. {risk.title}</strong><br>
                                <small>Пункт: {risk.clause_number} | Уровень: {risk.risk_level.value.upper()}</small>
                            </div>""", unsafe_allow_html=True)
                            
                            with st.expander(f"📖 Подробнее о риске {i}"):
                                if risk.clause_text and risk.clause_text != "Не найдено" and risk.clause_text != "Пункт не найден":
                                    st.markdown("**📌 Цитата из договора:**")
                                    st.info(risk.clause_text[:500])
                                st.markdown(f"**Описание проблемы:** {risk.description}")
                                st.markdown(f"**Правовое основание:** {risk.legal_basis}")
                                st.markdown(f"**💡 Рекомендация:** {risk.recommendation}")
                                if risk.proposed_text:
                                    st.success(f"**✅ Новая формулировка:**\n\n```\n{risk.proposed_text}\n```")
                    
                    report_text = f"""ОТЧЁТ ПО АНАЛИЗУ ДОГОВОРА
=====================================
Файл: {uploaded_file.name}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Заключение: {conclusion}
Уровень риска: {score}/10

НАЙДЕННЫЕ РИСКИ:
"""
                    for i, risk in enumerate(risks, 1):
                        report_text += f"\n{i}. {risk.title}\n   - {risk.description}\n   - {risk.legal_basis}\n   - Рекомендация: {risk.recommendation}\n"
                    
                    st.download_button(
                        "📥 Скачать отчёт (TXT)",
                        data=report_text,
                        file_name=f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"⚠️ Ошибка анализа: {str(e)}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

def render_conclusion():
    st.markdown('<p class="main-header">⚖️ Юридическое заключение</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Получите профессиональное заключение по договору</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Загрузите договор", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if st.button("📝 Получить заключение ИИ", type="primary", use_container_width=True):
            with st.spinner("ИИ готовит заключение..."):
                try:
                    from backend.document_parser import create_parser
                    from backend.llm_engine import create_llm_engine
                    
                    parser = create_parser()
                    contract_text = parser.parse_file(temp_path)
                    
                    llm = create_llm_engine()
                    prompt = f"""Дай профессиональное юридическое заключение по договору для строительной компании СЗ Дело (Москва/МО).

Проанализируй:
1. Тип договора (подряд, субподряд, поставка)
2. Существенные условия (предмет, срок, цена)
3. Риски для СЗ Дело
4. Рекомендации по изменениям

Текст договора:
{contract_text[:8000]}

Формат ответа:
- Заключение (✅ Можно / ⚠️ С правками / ❌ Не рекомендуется)
- Ключевые риски
- Рекомендации по изменениям
- Статьи ГК РФ"""
                    
                    response = llm.generate(prompt)
                    st.markdown("### 📋 Заключение ИИ-юриста")
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
    
    object_address = st.text_input("Адрес объекта")
    contract_price = st.text_input("Цена договора (рублей)")
    work_description = st.text_area("Описание работ")
    
    if st.button("📄 Сформировать договор", type="primary", use_container_width=True):
        st.success("✅ Шаблон готов! (добавьте файлы в data/templates/)")
        st.info("Для автозаполнения создайте .docx шаблоны с переменными {{contract_number}}, {{customer_name}} и т.д.")

def render_compare():
    st.markdown('<p class="main-header">🔄 Сравнить версии договора</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Сравните две версии и узнайте о юридических последствиях</p>', unsafe_allow_html=True)
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
        
        if st.button("🔍 Сравнить версии", type="primary", use_container_width=True):
            with st.spinner("ИИ сравнивает..."):
                try:
                    from backend.contract_comparator import create_comparator
                    from backend.llm_engine import create_llm_engine
                    
                    comparator = create_comparator()
                    text1 = comparator._extract_text(temp1)
                    text2 = comparator._extract_text(temp2)
                    changes = comparator.compare_files(temp1, temp2)
                    diff_html = comparator.generate_diff_html(text1, text2)
                    
                    st.markdown(f"### Найдено изменений: {len(changes)}")
                    st.markdown("### 📊 Визуальное сравнение")
                    st.components.v1.html(diff_html, height=400, scrolling=True)
                    
                    if changes:
                        st.markdown("### ⚖️ Изменения")
                        for change in changes:
                            emoji = "🟢" if change.change_type.value == "added" else "🔴" if change.change_type.value == "removed" else "🟡"
                            st.markdown(f"{emoji} **Пункт {change.clause_number}:** {change.legal_impact}")
                            st.info(f"Рекомендация: {change.recommendation}")
                    
                    st.markdown("### 🤖 ИИ-анализ изменений")
                    with st.spinner("ИИ анализирует..."):
                        llm = create_llm_engine()
                        llm_prompt = f"Проанализируй изменения в договоре. Версия 1: {text1[:2000]}. Версия 2: {text2[:2000]}. Изменения: {[f'{c.clause_number}: {c.change_type.value}' for c in changes]}. Дай рекомендации для СЗ Дело."
                        llm_response = llm.generate(llm_prompt)
                        st.markdown(llm_response.text)
                    
                except Exception as e:
                    st.error(f"⚠️ Ошибка: {str(e)}")
                finally:
                    if os.path.exists(temp1):
                        os.remove(temp1)
                    if os.path.exists(temp2):
                        os.remove(temp2)

def render_kb():
    st.markdown('<p class="main-header">📚 База знаний</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Поиск по внутренней базе СЗ Дело</p>', unsafe_allow_html=True)
    
    query = st.text_input("Поисковый запрос", placeholder="неустойка, гарантийный срок, расторжение...")
    
    if st.button("🔍 Поиск", type="primary", use_container_width=True):
        if not query:
            st.warning("Введите поисковый запрос")
        else:
            with st.spinner("Ищем в базе..."):
                try:
                    from backend.legal_kb import create_legal_kb
                    
                    kb = create_legal_kb()
                    context = kb.search(query, sources=['local'])
                    
                    st.markdown("### Результаты поиска")
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
st.markdown("<div style='text-align: center; color: #666; font-size: 0.9em;'>© 2025 СЗ Дело | ИИ-юрист | GigaChat + YandexGPT</div>", unsafe_allow_html=True)
