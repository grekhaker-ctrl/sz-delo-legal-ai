"""
СЗ Дело | Юридический ИИ-агент v4.0
Полный функционал с авторизацией и расширенными юридическими консультациями
"""
import streamlit as st
import os
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime
import secrets

st.set_page_config(
    page_title="СЗ Дело | Юридический ИИ",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    :root { --primary: #1e3a5f; --success: #2e7d32; --warning: #f57c00; --danger: #c62828; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
    .main-title { font-size: 2.5em; font-weight: 800; color: #1e3a5f; text-align: center; margin-bottom: 10px; }
    .main-subtitle { font-size: 1.3em; color: #666; text-align: center; margin-bottom: 40px; }
    .auth-container { max-width: 400px; margin: 50px auto; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); }
    .feature-card { background: white; border-radius: 16px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 15px 0; }
    .risk-critical { background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-left: 5px solid #c62828; padding: 18px; border-radius: 10px; margin: 12px 0; }
    .risk-high { background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left: 5px solid #f57c00; padding: 18px; border-radius: 10px; margin: 12px 0; }
    .risk-medium { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 5px solid #fbc02d; padding: 18px; border-radius: 10px; margin: 12px 0; }
    .risk-low { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-left: 5px solid #2e7d32; padding: 18px; border-radius: 10px; margin: 12px 0; }
    .user-msg { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 15px 20px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 4px solid #1e3a5f; }
    .ai-msg { background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%); padding: 15px 20px; border-radius: 15px 15px 0 15px; margin: 10px 0; border-left: 4px solid #2e7d32; }
</style>
""", unsafe_allow_html=True)

USERS = {
    "admin": {"password_hash": "3d3f9d4e1c2b8a7f6e9d3c2b1a0f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1", "name": "Администратор", "role": "admin"},
    "jurist1": {"password_hash": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890", "name": "Юрист 1", "role": "jurist"},
    "jurist2": {"password_hash": "b2c3d4e5f6789012345678901234567890123456789012345678901234567890123", "name": "Юрист 2", "role": "jurist"},
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

for key, default in [('logged_in', False), ('messages', []), ('session_id', secrets.token_hex(16)), ('contract_text', None), ('contract_name', None)]:
    if key not in st.session_state:
        st.session_state[key] = default

SUPPORTED_FORMATS = ['pdf', 'docx', 'doc', 'txt', 'rtf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']

def save_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower().lstrip('.')
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{suffix}') as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name

def cleanup(path: str):
    try:
        if path and os.path.exists(path): os.remove(path)
    except: pass

def get_llm():
    try:
        from backend.llm_engine import create_llm_engine
        return create_llm_engine()
    except Exception as e:
        st.error(f"Ошибка LLM: {e}")
        return None

def get_kb():
    try:
        from backend.legal_kb import create_legal_kb
        return create_legal_kb()
    except Exception as e:
        st.error(f"Ошибка KB: {e}")
        return None

def get_parser():
    try:
        from backend.document_parser import create_parser
        return create_parser()
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="auth-container"><div style="text-align: center; margin-bottom: 30px;"><h1 style="color: #1e3a5f; font-size: 2em;">⚖️ СЗ Дело</h1><p style="color: #666;">Юридический ИИ-агент</p></div>""", unsafe_allow_html=True)
        st.markdown("### 🔐 Вход в систему")
        username = st.text_input("👤 Логин", placeholder="Введите логин", key="login_username")
        password = st.text_input("🔑 Пароль", type="password", placeholder="Введите пароль", key="login_password")
        if st.button("🚀 Войти", type="primary", use_container_width=True):
            if username in USERS and verify_password(password, USERS[username]["password_hash"]):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_name = USERS[username]["name"]
                st.session_state.user_role = USERS[username]["role"]
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("❌ Неверный логин или пароль")
        st.markdown("<div style='margin-top: 30px; text-align: center; color: #888;'><p>Доступ только для сотрудников СЗ Дело</p></div></div>", unsafe_allow_html=True)

def render_main_app():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2275/2275970.png", width=80)
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"**Роль:** {st.session_state.user_role}")
        st.divider()
        menu = st.radio("📋 Меню", ["💬 Чат с ИИ", "📄 Анализ документов", "⚖️ Юридическое заключение", "📝 Генерация документов", "🔄 Сравнение версий", "📚 Справочник"], label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Выйти", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    if menu == "💬 Чат с ИИ": render_chat()
    elif menu == "📄 Анализ документов": render_analyze()
    elif menu == "⚖️ Юридическое заключение": render_conclusion()
    elif menu == "📝 Генерация документов": render_template()
    elif menu == "🔄 Сравнение версий": render_compare()
    elif menu == "📚 Справочник": render_kb()

def render_chat():
    st.markdown("<p class='main-title'>💬 Чат с ИИ-юристом</p><p class='main-subtitle'>Универсальный юридический помощник</p>", unsafe_allow_html=True)
    with st.expander("📎 Прикрепить документ"):
        file = st.file_uploader("Загрузите документ", type=SUPPORTED_FORMATS, key="chat_file")
        file_text = ""
        if file:
            path = save_file(file)
            parser = get_parser()
            if parser:
                file_text = parser.parse_file(path)
                if file_text: st.success(f"✅ Прочитан ({len(file_text)} символов)")
            cleanup(path)
    for msg in st.session_state.messages:
        st.markdown(f"<div class='{'user-msg' if msg['role']=='user' else 'ai-msg'}'><b>{'Вы' if msg['role']=='user' else '🤖 ИИ'}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        if msg.get("sources"): st.markdown("**📚 Источники:** " + " ".join(msg["sources"]))
    prompt = st.chat_input("Введите юридический вопрос...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("🤖 Анализирую..."):
            llm = get_llm()
            kb = get_kb()
            if not llm: return
            context = kb.search(prompt) if kb else ""
            full_prompt = prompt
            if file_text:
                full_prompt = f"""Пользователь задаёт вопрос и прикрепил документ.
ВОПРОС: {prompt}
ДОКУМЕНТ: {file_text[:15000]}
ТРЕБОВАНИЯ: 1) Развёрнутый ответ 500+ слов 2) Цитаты из документа 3) Все статьи законов с ссылками 4) Пошаговые рекомендации 5) Риски 6) Примеры из практики
"""
            else:
                full_prompt = f"""Дай развёрнутый юридический ответ на вопрос: {prompt}
ТРЕБОВАНИЯ: 1) 500+ слов 2) Все нормы права 3) Ссылки на КонсультантПлюс 4) Примеры из практики 5) Пошаговые действия 6) Риски 7) Альтернативы
"""
            response = llm.generate(full_prompt, context=context)
            if response.success and response.text:
                sources = []
                if kb:
                    for s in kb.find_sources(prompt)[:15]:
                        sources.append(f"📖 [{s['name']}]({s['url']})")
                st.session_state.messages.append({"role": "assistant", "content": response.text, "sources": sources})
                st.rerun()

def render_analyze():
    st.markdown("<p class='main-title'>📄 Анализ документов</p><p class='main-subtitle'>ИИ найдёт все риски и даст рекомендации</p>", unsafe_allow_html=True)
    file = st.file_uploader("📎 Загрузите документ", type=['pdf', 'docx', 'doc', 'txt', 'rtf'], key="analyze_file")
    if file:
        path = save_file(file)
        if st.button("🔍 Начать анализ", type="primary", use_container_width=True):
            with st.spinner("📖 Читаю..."):
                parser = get_parser()
                if not parser: cleanup(path); return
                text = parser.parse_file(path)
                if not text: st.error("Ошибка чтения"); cleanup(path); return
                st.success(f"✅ ({len(text)} символов)")
                llm = get_llm()
                kb = get_kb()
                if not llm: cleanup(path); return
                prompt = f"""Проведи полный анализ документа.
ДОКУМЕНТ: {text[:15000]}
ТРЕБОВАНИЯ: 1) Найди ВСЕ риски с цитатами 2) Уровень: 🔴🟠🟡🟢 3) Статьи законов 4) Ссылки 5) Рекомендации по исправлению 6) Итоговое заключение
"""
                response = llm.generate(prompt, context=kb.search("анализ рисков") if kb else "")
                if response.success and response.text:
                    st.markdown("---")
                    st.markdown("## 📊 Результаты анализа")
                    st.markdown(response.text)
                cleanup(path)

def render_conclusion():
    st.markdown("<p class='main-title'>⚖️ Юридическое заключение</p><p class='main-subtitle'>ИИ подготовит экспертное заключение</p>", unsafe_allow_html=True)
    file = st.file_uploader("📎 Загрузите документы", type=['pdf', 'docx', 'doc', 'txt', 'rtf'], accept_multiple_files=True, key="conc_file")
    if file and st.button("📝 Подготовить заключение", type="primary"):
        paths = [save_file(f) for f in file]
        with st.spinner("📖 Читаю..."):
            parser = get_parser()
            texts = [parser.parse_file(p) for p in paths]
            combined = "\n\n".join([f"===DOC {i+1}===\n{t}" for i, t in enumerate(texts) if t])
            llm = get_llm()
            if llm:
                response = llm.generate(f"""Подготовь юридическое заключение.
ДОКУМЕНТЫ: {combined[:15000]}
ТРЕБОВАНИЯ: 1) Оценка соответствия законодательству 2) Риски 3) Рекомендации 4) Экспертное мнение 5) Источники
""")
                if response.success and response.text:
                    st.markdown("---")
                    st.markdown("## 📋 Заключение")
                    st.markdown(response.text)
            for p in paths: cleanup(p)

def render_template():
    st.markdown("<p class='main-title'>📝 Генерация документов</p><p class='main-subtitle'>ИИ создаст документ</p>", unsafe_allow_html=True)
    doc_types = [("dogovor_podryada", "Договор подряда"), ("dogovor_subpodryada", "Договор субподряда"), ("pretenziya", "Претензия"), ("soglashenie", "Соглашение")]
    selected = st.selectbox("Тип", [x[1] for x in doc_types])
    if selected:
        col1, col2 = st.columns(2)
        with col1: customer = st.text_input("Сторона 1"); inn1 = st.text_input("ИНН")
        with col2: contractor = st.text_input("Сторона 2"); inn2 = st.text_input("ИНН")
        price = st.text_input("Сумма")
        subject = st.text_area("Предмет")
        if st.button("📄 Сгенерировать", type="primary"):
            llm = get_llm()
            if llm:
                response = llm.generate(f"""Создай документ: {selected}
Сторона 1: {customer}, ИНН: {inn1}
Сторона 2: {contractor}, ИНН: {inn2}
Сумма: {price}
Предмет: {subject}
ТРЕБОВАНИЯ: Полный текст, готов к подписанию, все разделы ГК РФ
""")
                if response.success and response.text:
                    st.markdown("---")
                    st.markdown("## 📄 Документ")
                    st.markdown(response.text)

def render_compare():
    st.markdown("<p class='main-title'>🔄 Сравнение версий</p><p class='main-subtitle'>ИИ сравнит документы</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: file1 = st.file_uploader("Версия 1", type=['pdf', 'docx', 'txt'], key="v1")
    with col2: file2 = st.file_uploader("Версия 2", type=['pdf', 'docx', 'txt'], key="v2")
    if file1 and file2 and st.button("🔍 Сравнить", type="primary"):
        path1, path2 = save_file(file1), save_file(file2)
        parser = get_parser()
        if parser:
            t1, t2 = parser.parse_file(path1), parser.parse_file(path2)
            llm = get_llm()
            if llm and t1 and t2:
                response = llm.generate(f"""Сравни два договора.
ВЕРСИЯ 1: {t1[:6000]}
ВЕРСИЯ 2: {t2[:6000]}
ТРЕБОВАНИЯ: Все изменения, влияние, риски, рекомендации
""")
                if response.success and response.text:
                    st.markdown("---")
                    st.markdown(response.text)
        cleanup(path1); cleanup(path2)

def render_kb():
    st.markdown("<p class='main-title'>📚 Справочник</p><p class='main-subtitle'>База знаний</p>", unsafe_allow_html=True)
    query = st.text_input("🔍 Поиск")
    if query and st.button("Найти", type="primary"):
        kb = get_kb()
        llm = get_llm()
        if kb and llm:
            response = llm.generate(f"""Ответь на вопрос: {query}
ТРЕБОВАНИЯ: Развёрнуто, ссылки на КонсультантПлюс, примеры практики
""", context=kb.search(query))
            if response.success and response.text:
                st.markdown(response.text)

if not st.session_state.get("logged_in"):
    render_login()
else:
    render_main_app()
