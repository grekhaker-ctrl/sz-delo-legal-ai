"""
СЗ Дело | Юридический ИИ-агент v4.1
Полный функционал с авторизацией
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
    .user-msg { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 15px 20px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 4px solid #1e3a5f; }
    .ai-msg { background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%); padding: 15px 20px; border-radius: 15px 15px 0 15px; margin: 10px 0; border-left: 4px solid #2e7d32; }
</style>
""", unsafe_allow_html=True)

USERS = {
    "admin": {"password_hash": "23ea41613125b253051dc8e008c78e3375fb5c71bee06a24c79eb34ef1e1b58b", "name": "Администратор", "role": "admin"},
    "jurist1": {"password_hash": "5dab6d039e2c79ed1477b61a1bbd7f8f7d2e1a6e692fe6bbd5709f1360c2a835", "name": "Юрист 1", "role": "jurist"},
    "jurist2": {"password_hash": "5dab6d039e2c79ed1477b61a1bbd7f8f7d2e1a6e692fe6bbd5709f1360c2a835", "name": "Юрист 2", "role": "jurist"},
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

for key, default in [('logged_in', False), ('messages', []), ('session_id', secrets.token_hex(16)), ('contract_text', None)]:
    if key not in st.session_state:
        st.session_state[key] = default

SUPPORTED_FORMATS = ['pdf', 'docx', 'doc', 'txt', 'rtf']

def save_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower().lstrip('.')
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{suffix}') as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name

def cleanup(path: str):
    try:
        if path and os.path.exists(path): os.remove(path)
    except: pass

@st.cache_resource
def get_llm_engine():
    try:
        from backend.llm_engine import create_llm_engine as _create
        return _create()
    except Exception as e:
        st.warning(f"Ошибка LLM: {e}")
        return None

@st.cache_resource  
def get_kb_engine():
    try:
        from backend.legal_kb import create_legal_kb as _create
        return _create()
    except: return None

@st.cache_resource
def get_doc_parser():
    try:
        from backend.document_parser import create_parser as _create
        return _create()
    except: return None

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="auth-container"><div style="text-align: center; margin-bottom: 30px;"><h1 style="color: #1e3a5f; font-size: 2em;">⚖️ СЗ Дело</h1><p style="color: #666;">Юридический ИИ-агент</p></div>""", unsafe_allow_html=True)
        st.markdown("### 🔐 Вход в систему")
        username = st.text_input("👤 Логин", key="login_username")
        password = st.text_input("🔑 Пароль", type="password", key="login_password")
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
        st.markdown("<div style='margin-top:30px;text-align:center;color:#888;'>© 2025 СЗ Дело</div></div>", unsafe_allow_html=True)

def render_main_app():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2275/2275970.png", width=80)
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.divider()
        menu = st.radio("📋", ["💬 Чат с ИИ", "📄 Анализ", "⚖️ Заключение", "📝 Шаблоны", "🔄 Сравнение", "📚 Справочник"], label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Выйти", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    if menu == "💬 Чат с ИИ": render_chat()
    elif menu == "📄 Анализ": render_analyze()
    elif menu == "⚖️ Заключение": render_conclusion()
    elif menu == "📝 Шаблоны": render_template()
    elif menu == "🔄 Сравнение": render_compare()
    elif menu == "📚 Справочник": render_kb()

def render_chat():
    st.markdown("<p class='main-title'>💬 Чат с ИИ-юристом</p><p class='main-subtitle'>Задавайте юридические вопросы</p>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        st.markdown(f"<div class='{'user-msg' if msg['role']=='user' else 'ai-msg'}'><b>{'Вы' if msg['role']=='user' else '🤖'}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    if prompt := st.chat_input("Введите вопрос..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("🤖"):
            llm = get_llm_engine()
            if llm:
                response = llm.generate(prompt)
                if response.success:
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()

def render_analyze():
    st.markdown("<p class='main-title'>📄 Анализ документов</p>", unsafe_allow_html=True)
    file = st.file_uploader("📎 Загрузите", type=['pdf', 'docx', 'txt'])
    if file and st.button("🔍 Анализировать", type="primary"):
        path = save_file(file)
        parser = get_doc_parser()
        llm = get_llm_engine()
        if parser and llm:
            text = parser.parse_file(path)
            if text:
                response = llm.generate(f"Анализ: {text[:15000]}")
                if response.success:
                    st.markdown(response.text)
        cleanup(path)

def render_conclusion():
    st.markdown("<p class='main-title'>⚖️ Заключение</p>", unsafe_allow_html=True)
    file = st.file_uploader("📎 Загрузите", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
    if file and st.button("📝 Заключение", type="primary"):
        paths = [save_file(f) for f in file]
        parser = get_doc_parser()
        llm = get_llm_engine()
        if parser and llm:
            texts = [parser.parse_file(p) for p in paths]
            combined = "\n\n".join([t for t in texts if t])
            response = llm.generate(f"Заключение: {combined[:15000]}")
            if response.success:
                st.markdown(response.text)
        for p in paths: cleanup(p)

def render_template():
    st.markdown("<p class='main-title'>📝 Шаблоны</p>", unsafe_allow_html=True)
    doc_type = st.selectbox("Тип", ["", "Договор подряда", "Претензия"])
    if doc_type:
        customer = st.text_input("Сторона 1")
        contractor = st.text_input("Сторона 2")
        price = st.text_input("Сумма")
        if st.button("📄 Создать", type="primary"):
            llm = get_llm_engine()
            if llm:
                response = llm.generate(f"Создай {doc_type}. {customer} - {contractor}. {price}")
                if response.success:
                    st.markdown(response.text)
                    st.download_button("📥 Скачать", data=response.text, file_name=f"{doc_type}.txt", mime="text/plain")

def render_compare():
    st.markdown("<p class='main-title'>🔄 Сравнение</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: file1 = st.file_uploader("Версия 1", type=['pdf', 'docx', 'txt'])
    with col2: file2 = st.file_uploader("Версия 2", type=['pdf', 'docx', 'txt'])
    if file1 and file2 and st.button("🔍 Сравнить", type="primary"):
        path1, path2 = save_file(file1), save_file(file2)
        parser = get_doc_parser()
        llm = get_llm_engine()
        if parser and llm:
            t1, t2 = parser.parse_file(path1), parser.parse_file(path2)
            if t1 and t2:
                response = llm.generate(f"Сравни:\n1: {t1[:5000]}\n2: {t2[:5000]}")
                if response.success:
                    st.markdown(response.text)
        cleanup(path1); cleanup(path2)

def render_kb():
    st.markdown("<p class='main-title'>📚 Справочник</p>", unsafe_allow_html=True)
    query = st.text_input("🔍 Поиск")
    if query and st.button("Найти", type="primary"):
        kb = get_kb_engine()
        llm = get_llm_engine()
        if kb and llm:
            response = llm.generate(f"Ответь: {query}", context=kb.search(query))
            if response.success:
                st.markdown(response.text)

if not st.session_state.get("logged_in"):
    render_login()
else:
    render_main_app()
