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
# CSS - Меню всегда видно + дизайн
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Скрываем стандартные элементы */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Блокируем закрытие sidebar */
    [data-testid="stSidebarCloseButton"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    
    [data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        overflow: hidden !important;
    }
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Фон */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        margin-left: 300px !important;
    }
    
    /* Hero секция */
    .hero-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
        border-radius: 16px;
        padding: 40px 48px;
        margin: 24px 24px 32px 24px;
        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
    }
    
    .hero-title {
        font-size: 2.5em;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        font-size: 1.1em;
        color: #bfdbfe;
        margin: 0;
    }
    
    /* Карточки */
    .info-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
    
    /* Загрузчик файлов */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 2px dashed #94a3b8;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    /* Чат - чёткое разделение */
    .chat-user {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 16px 4px 16px 16px;
        margin: 12px 0;
        max-width: 75%;
        margin-left: auto;
    }
    
    .chat-assistant {
        background: #ffffff;
        color: #1e293b;
        padding: 16px 20px;
        border-radius: 4px 16px 16px 16px;
        margin: 12px 0;
        max-width: 75%;
        border: 1px solid #e2e8f0;
    }
    
    /* Разделители */
    hr {
        border-color: #e2e8f0;
        margin: 24px 0;
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
# SIDEBAR - ВСЕГДА ВИДЕН
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 32px 20px 24px;">
        <div style="
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            font-size: 2.2em;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        ">⚖️</div>
        <h2 style="
            margin: 0;
            color: #ffffff;
            font-size: 1.6em;
            font-weight: 800;
        ">СЗ ДЕЛО</h2>
        <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 0.9em;">Юридический ИИ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
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
    
    if st.button("🗑️ Очистить чат", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

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
    
    # Сообщения
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-user"><strong>Вы:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant"><strong>ИИ-юрист:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    
    # Ввод
    prompt = st.chat_input("Введите ваш юридический вопрос...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-user"><strong>Вы:</strong><br>{prompt}</div>', unsafe_allow_html=True)
        
        with st.spinner("🤖 Анализирую вопрос..."):
            try:
                from backend.llm_engine import create_llm_engine
                from backend.legal_kb import create_legal_kb
                
                llm = create_llm_engine()
                kb = create_legal_kb()
                context = kb.search(prompt)
                
                response = llm.generate(prompt, context=context, task="answer")
                st.markdown(f'<div class="chat-assistant"><strong>ИИ-юрист:</strong><br>{response.text}</div>', unsafe_allow_html=True)
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

ТРЕБОВАНИЯ К ОТВЕТУ:
1. Используй ТОЛЬКО актуальные законы РФ (2024-2025)
2. Проверяй статьи по официальным источникам:
   - КонсультантПлюс: consultant.ru
   - Гарант: garant.ru  
   - Верховный Суд РФ: vsrf.ru
3. НЕ выдумывай статьи и законы
4. Указывай точные номера статей
5. Если не уверен - пиши "Требуется проверка"

Текст договора:
{contract_text[:10000]}

ФОРМАТ ОТВЕТА:
### Тип договора
[Определение по ГК РФ]

### Найденные риски
1. [Конкретный пункт] - [Статья ГК РФ с номером] - [Уровень]
2. ...

### Рекомендации
[Конкретные действия]
"""
                        response = llm.generate(risk_prompt, task="answer")
                        st.markdown(response.text)
                    
                    if fix_contract:
                        st.markdown("### ✨ Исправленная версия")
                        fix_prompt = f"""
Ты - старший юрист СЗ Дело с 15-летним опытом.

ТРЕБОВАНИЯ:
1. ТОЛЬКО актуальные законы РФ (2024-2025)
2. Проверяй по: КонсультантПлюс, Гарант, vsrf.ru
3. НЕ выдумывай статьи
4. Указывай точные номера статей ГК РФ
5. Сохраняй структуру договора

Текст:
{contract_text[:10000]}

ФОРМАТ СТРОГО:
### Анализ
[Тип, стороны, предмет, цена, сроки]

### Проблемы
1. [Пункт] - [Проблема] - [Статья ГК РФ]

### Исправленный текст
[ПОЛНЫЙ текст договора]

### Таблица
| № | Было | Стало | Статья ГК |
"""
                        response = llm.generate(fix_prompt, task="fix_contract")
                        st.markdown(response.text)
                        
                        # TXT
                        st.download_button(
                            label="📥 Скачать TXT",
                            data=response.text.encode('utf-8'),
                            file_name=f"fixed_{uploaded_file.name}.txt",
                            mime="text/plain; charset=utf-8",
                            use_container_width=True
                        )
                        
                        # PDF
                        try:
                            from fpdf import FPDF
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_auto_page_break(auto=True, margin=15)
                            
                            font_path = "/tmp/DejaVuSans.ttf"
                            if not os.path.exists(font_path):
                                try:
                                    import urllib.request
                                    urllib.request.urlretrieve(
                                        "https://cdn.jsdelivr.net/gh/dejavu-fonts/dejavu-fonts@master/ttf/DejaVuSans.ttf",
                                        font_path
                                    )
                                except:
                                    pass
                            
                            if os.path.exists(font_path):
                                pdf.add_font("DejaVu", "", font_path, uni=True)
                                pdf.set_font("DejaVu", "", 10)
                            else:
                                pdf.set_font("Arial", "", 10)
                            
                            pdf.set_font_size(14)
                            pdf.cell(0, 10, "ИСПРАВЛЕННЫЙ ДОГОВОР", ln=True, align="C")
                            pdf.set_font_size(10)
                            pdf.cell(0, 10, f"Файл: {uploaded_file.name}", ln=True, align="C")
                            pdf.ln(10)
                            
                            pdf.set_font_size(10)
                            for line in response.text.split("\n"):
                                clean = line.replace("#", "").replace("*", "").strip()
                                if clean:
                                    try:
                                        pdf.multi_cell(0, 8, clean)
                                    except:
                                        pdf.multi_cell(0, 8, clean.encode('latin-1', errors='ignore').decode('latin-1'))
                            
                            pdf_path = f"fixed_{uploaded_file.name}.pdf"
                            pdf.output(pdf_path)
                            
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="📥 Скачать PDF",
                                    data=f.read(),
                                    file_name=f"fixed_{uploaded_file.name}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                        except Exception as pdf_error:
                            st.warning(f"⚠️ PDF: {str(pdf_error)[:200]}")
                    
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
Ты - старший юрист СЗ Дело.

ТРЕБОВАНИЯ:
1. ТОЛЬКО актуальные законы РФ (2024-2025)
2. Проверяй: КонсультантПлюс, Гарант, vsrf.ru
3. НЕ выдумывай статьи
4. Указывай точные номера

Текст:
{contract_text[:10000]}

ФОРМАТ:
1. Тип договора
2. Вывод (✅/⚠️/❌)
3. Риски со статьями ГК РФ
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
st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 0.85em;">© 2025 СЗ Дело</p>', unsafe_allow_html=True)
