import streamlit as st
import requests

st.title("🔍 Тест API ключей")

st.header("1. Проверка Secrets")

try:
    YANDEX_FOLDER_ID = st.secrets.get("YANDEX_FOLDER_ID", "НЕ НАЙДЕНО")
    YANDEX_API_KEY = st.secrets.get("YANDEX_API_KEY", "НЕ НАЙДЕНО")
    GIGACHAT_CREDENTIALS = st.secrets.get("GIGACHAT_CREDENTIALS", "НЕ НАЙДЕНО")
    
    st.success("✅ Secrets читаются")
    st.code(f"YANDEX_FOLDER_ID: {YANDEX_FOLDER_ID[:10]}...")
    st.code(f"YANDEX_API_KEY: {YANDEX_API_KEY[:10]}...")
    st.code(f"GIGACHAT: {GIGACHAT_CREDENTIALS[:20]}...")
except Exception as e:
    st.error(f"❌ Ошибка чтения Secrets: {e}")

st.header("2. Тест YandexGPT API")

if st.button("🔌 Проверить YandexGPT"):
    if "НЕ НАЙДЕНО" in YANDEX_FOLDER_ID or "НЕ НАЙДЕНО" in YANDEX_API_KEY:
        st.error("❌ Ключи не найдены в Secrets!")
    else:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "modelUri": f"gcp://{YANDEX_FOLDER_ID}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 100},
                "messages": [{"role": "user", "text": "Тест"}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                st.success(f"✅ YandexGPT работает! Status: {response.status_code}")
                st.json(response.json())
            else:
                st.error(f"❌ YandexGPT ошибка: {response.status_code}")
                st.code(response.text)
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

st.header("3. Тест GigaChat API")

if st.button("🔌 Проверить GigaChat"):
    if "НЕ НАЙДЕНО" in GIGACHAT_CREDENTIALS:
        st.error("❌ Ключи не найдены в Secrets!")
    else:
        try:
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            auth_headers = {
                "Authorization": f"Basic {GIGACHAT_CREDENTIALS}",
                "RqUID": "12345678-1234-1234-1234-123456789012",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            auth_response = requests.post(auth_url, headers=auth_headers, data={"scope": "GIGACHAT_API_PERS"}, timeout=30, verify=False)
            
            if auth_response.status_code == 200:
                token = auth_response.json().get("access_token")
                st.success(f"✅ GigaChat токен получен!")
                st.code(f"Token: {token[:50]}...")
            else:
                st.error(f"❌ GigaChat ошибка: {auth_response.status_code}")
                st.code(auth_response.text)
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

st.header("4. Логи")
st.info("Откройте вкладку 'Logs' в Streamlit Cloud для просмотра ошибок приложения")
