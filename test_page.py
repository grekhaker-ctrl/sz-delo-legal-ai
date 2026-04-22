import streamlit as st
import requests

st.set_page_config(page_title="Тест API", page_icon="🔍")
st.title("🔍 Тест API ключей YandexGPT")

# Получаем секреты
try:
    import streamlit as st
    folder_id = st.secrets.get("YANDEX_FOLDER_ID", "")
    api_key = st.secrets.get("YANDEX_API_KEY", "")
except:
    folder_id = ""
    api_key = ""

st.header("📋 Проверка ключей")
st.write(f"Folder ID: {'✅' if folder_id else '❌'}")
st.write(f"API Key: {'✅' if api_key else '❌'}")

if st.button("🚀 Протестировать YandexGPT"):
    if not folder_id or not api_key:
        st.error("❌ Ключи не найдены!")
    else:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "modelUri": f"gcp://{folder_id}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 500},
                "messages": [
                    {"role": "system", "text": "Ты юрист. Отвечай кратко."},
                    {"role": "user", "text": "Что такое неустойка по ГК РФ?"}
                ]
            }
            
            with st.spinner("Запрос к YandexGPT..."):
                response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                st.success("✅ API работает!")
                result = response.json()
                answer = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Нет ответа")
                st.markdown("### Ответ ИИ:")
                st.write(answer)
            else:
                st.error(f"❌ Ошибка: {response.status_code}")
                st.code(response.text)
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
            st.code(str(e))
