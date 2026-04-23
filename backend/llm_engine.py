"""
LLM Engine - YandexGPT + GigaChat
"""
import os
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class LLMResponse:
    def __init__(self, text: str = "", model: str = "", success: bool = False, error: Optional[str] = None):
        self.text = text
        self.model = model
        self.success = success
        self.error = error

class YandexGPT:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.endpoint = "https://llm.cloud.yandex.net/text-generator/v1/generate"
        logger.info(f"YandexGPT инициализирован (folder: {folder_id[:10]}...)")
    
    def is_available(self) -> bool:
        available = bool(self.folder_id and self.api_key)
        logger.info(f"YandexGPT available: {available}")
        return available
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            logger.info(f"Отправка запроса к YandexGPT...")
            
            system_prompt = """Ты - юридический консультант компании СЗ Дело.
Ты специализируешься на всех отраслях права РФ: ГК РФ, ТК РФ, АПК РФ, КоАП и др.
Ты даёшь РАЗВЁРНУТЫЕ ответы минимум 500 слов.
Ты всегда указываешь статьи законов с ссылками на КонсультантПлюс."""
            
            full_messages = [{"role": "system", "content": f"{system_prompt}\n\nКонтекст:\n{context}"}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            
            headers = {"Authorization": f"Api-Key {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "modelUri": f"gcp://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 4096},
                "messages": full_messages
            }
            
            logger.info(f"Запрос: {payload}")
            
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            logger.info(f"Статус ответа: {r.status_code}")
            r.raise_for_status()
            
            result = r.json()
            logger.info(f"Ответ API: {result}")
            
            text = result.get("result", {}).get("text", "")
            
            if not text:
                return LLMResponse(text="", model="yandexgpt", success=False, error="Пустой ответ от API")
            
            return LLMResponse(text=text, model="yandexgpt", success=True)
            
        except requests.exceptions.Timeout:
            logger.error("YandexGPT: Timeout")
            return LLMResponse(text="", model="yandexgpt", success=False, error="Превышено время ожидания")
        except Exception as e:
            logger.error(f"YandexGPT ошибка: {e}")
            return LLMResponse(text="", model="yandexgpt", success=False, error=str(e))

class GigaChat:
    def __init__(self, credentials: str):
        self.credentials = credentials
        self._token = None
    
    def is_available(self) -> bool:
        return bool(self.credentials)
    
    def _get_token(self) -> Optional[str]:
        if self._token:
            return self._token
        try:
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            headers = {"RqUID": "12345678-1234-1234-1234-123456789012", "Content-Type": "application/x-www-form-urlencoded"}
            data = {"scope": "GIGACHAT_API_PERS", "grant_type": "client_credentials"}
            r = requests.post(auth_url, headers=headers, data=data, verify=False)
            r.raise_for_status()
            self._token = r.json().get("access_token")
            return self._token
        except Exception as e:
            logger.error(f"GigaChat token error: {e}")
            return None
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            token = self._get_token()
            if not token:
                return LLMResponse(text="", model="gigachat", success=False, error="Token error")
            
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "RqUID": "12345678-1234-1234-1234-123456789012"}
            
            system_prompt = "Ты - юридический консультант СЗ Дело. Отвечай развёрнуто."
            full_messages = [{"role": "system", "content": system_prompt}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            
            payload = {"model": "GigaChat", "messages": full_messages, "temperature": 0.3, "max_tokens": 4096}
            
            r = requests.post(url, headers=headers, json=payload, timeout=90, verify=False)
            r.raise_for_status()
            
            text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(text=text, model="gigachat", success=True)
            
        except Exception as e:
            logger.error(f"GigaChat error: {e}")
            return LLMResponse(text="", model="gigachat", success=False, error=str(e))

class LLMEngine:
    def __init__(self, config: Dict):
        self.llms = []
        logger.info(f"LLMEngine конфиг: {config}")
        
        folder_id = config.get("yandex_folder_id")
        api_key = config.get("yandex_api_key")
        
        if folder_id and api_key:
            self.llms.append(YandexGPT(folder_id=folder_id, api_key=api_key))
            logger.info(f"✅ YandexGPT добавлен")
        else:
            logger.warning(f"❌ YandexGPT: folder_id={folder_id}, api_key={'есть' if api_key else 'нет'}")
        
        gigachat_creds = config.get("gigachat_credentials")
        if gigachat_creds:
            self.llms.append(GigaChat(credentials=gigachat_creds))
            logger.info(f"✅ GigaChat добавлен")
        else:
            logger.warning(f"❌ GigaChat: credentials нет")
        
        logger.info(f"Всего LLM: {len(self.llms)}")
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None) -> LLMResponse:
        messages = list(history) if history else []
        messages.append(Message(role="user", content=user_message))
        
        logger.info(f"Генерация ответа для: {user_message[:50]}...")
        
        for llm in self.llms:
            if not llm.is_available():
                logger.warning(f"{llm.__class__.__name__} недоступен")
                continue
            
            logger.info(f"Пробую {llm.__class__.__name__}...")
            response = llm.generate(messages, context)
            
            if response.success and response.text:
                logger.info(f"✅ Успех от {llm.__class__.__name__}")
                return response
            
            logger.warning(f"❌ {llm.__class__.__name__} вернул ошибку: {response.error}")
        
        # Fallback с полезным ответом
        return LLMResponse(
            text=f"""⚠️ **ИИ-движок не ответил**

**Возможные причины:**
1. Не настроены API ключи в Secrets
2. Превышен лимит запросов
3. Проблемы с соединением

**Что делать:**
- Проверьте Secrets в настройках Streamlit Cloud
- Убедитесь что добавлены YANDEX_FOLDER_ID и YANDEX_API_KEY
- Попробуйте позже

**Ваш вопрос:** {user_message[:200]}

Попробуйте переформулировать вопрос или обратитесь к юристу.""",
            model="fallback",
            success=True
        )
    
    def get_status(self) -> Dict:
        return {llm.__class__.__name__: llm.is_available() for llm in self.llms}

def create_llm_engine() -> LLMEngine:
    """Создание LLM Engine"""
    config = {"yandex_folder_id": None, "yandex_api_key": None, "gigachat_credentials": None}
    
    # Streamlit Secrets
    try:
        import streamlit as st
        config["yandex_folder_id"] = st.secrets.get("YANDEX_FOLDER_ID")
        config["yandex_api_key"] = st.secrets.get("YANDEX_API_KEY")
        config["gigachat_credentials"] = st.secrets.get("GIGACHAT_CREDENTIALS")
        logger.info(f"Secrets загружены: folder_id={'есть' if config['yandex_folder_id'] else 'нет'}")
    except Exception as e:
        logger.warning(f"Secrets не загружены: {e}")
    
    # Fallback на .env
    if not config["yandex_folder_id"]:
        config["yandex_folder_id"] = os.getenv("YANDEX_FOLDER_ID")
        config["yandex_api_key"] = os.getenv("YANDEX_API_KEY")
        config["gigachat_credentials"] = os.getenv("GIGACHAT_CREDENTIALS")
        logger.info(f"Попытка загрузки из .env")
    
    return LLMEngine(config)
