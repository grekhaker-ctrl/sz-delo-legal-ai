"""
LLM Engine - DeepSeek + GigaChat + YandexGPT
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

class DeepSeekLLM:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.endpoint = f"{self.base_url}/chat/completions"
        self.model = "deepseek-chat"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            system_prompt = """Ты - юридический консультант компании СЗ Дело.
Ты специализируешься на всех отраслях права РФ: ГК РФ, ТК РФ, АПК РФ, КоАП и др.
Ты даёшь РАЗВЁРНУТЫЕ ответы минимум 500 слов.
Ты всегда указываешь статьи законов с ссылками на КонсультантПлюс."""
            
            full_messages = [{"role": "system", "content": f"{system_prompt}\n\nКонтекст:\n{context}"}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": full_messages, "temperature": 0.3, "max_tokens": 4096}
            
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            
            if r.status_code != 200:
                return LLMResponse(text="", model=self.model, success=False, error=f"HTTP {r.status_code}")
            
            result = r.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not text:
                return LLMResponse(text="", model=self.model, success=False, error="Пустой ответ")
            
            return LLMResponse(text=text, model=self.model, success=True)
            
        except Exception as e:
            return LLMResponse(text="", model=self.model, success=False, error=str(e))

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
        except:
            return None
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            token = self._get_token()
            if not token:
                return LLMResponse(text="", model="gigachat", success=False, error="Token error")
            
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "RqUID": "12345678-1234-1234-1234-123456789012"}
            system_prompt = "Ты - юридический консультант СЗ Дело."
            full_messages = [{"role": "system", "content": system_prompt}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            
            payload = {"model": "GigaChat", "messages": full_messages, "temperature": 0.3, "max_tokens": 4096}
            r = requests.post(url, headers=headers, json=payload, timeout=90, verify=False)
            r.raise_for_status()
            
            text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(text=text, model="gigachat", success=True)
        except:
            return LLMResponse(text="", model="gigachat", success=False, error="Error")

class YandexGPT:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.endpoint = "https://llm.cloud.yandex.net/text-generator/v1/generate"
    
    def is_available(self) -> bool:
        return bool(self.folder_id and self.api_key)
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            system_prompt = "Ты - юридический консультант СЗ Дело."
            full_messages = [{"role": "system", "content": f"{system_prompt}\n\nКонтекст:\n{context}"}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            
            headers = {"Authorization": f"Api-Key {self.api_key}", "Content-Type": "application/json"}
            payload = {"modelUri": f"gcp://{self.folder_id}/yandexgpt-lite", "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 4096}, "messages": full_messages}
            
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            r.raise_for_status()
            
            text = r.json().get("result", {}).get("text", "")
            return LLMResponse(text=text, model="yandexgpt", success=True) if text else LLMResponse(text="", model="yandexgpt", success=False, error="Пустой ответ")
        except Exception as e:
            return LLMResponse(text="", model="yandexgpt", success=False, error=str(e))

class LLMEngine:
    def __init__(self, config: Dict):
        self.llms = []
        if config.get("deepseek_api_key"):
            self.llms.append(DeepSeekLLM(api_key=config["deepseek_api_key"]))
        if config.get("gigachat_credentials"):
            self.llms.append(GigaChat(credentials=config["gigachat_credentials"]))
        if config.get("yandex_folder_id") and config.get("yandex_api_key"):
            self.llms.append(YandexGPT(folder_id=config["yandex_folder_id"], api_key=config["yandex_api_key"]))
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None) -> LLMResponse:
        messages = list(history) if history else []
        messages.append(Message(role="user", content=user_message))
        
        for llm in self.llms:
            if not llm.is_available():
                continue
            response = llm.generate(messages, context)
            if response.success and response.text:
                return response
        
        return LLMResponse(text="⚠️ ИИ недоступен. Добавьте DEEPSEEK_API_KEY в Secrets.", model="fallback", success=True)
    
    def get_status(self) -> Dict:
        return {llm.__class__.__name__: llm.is_available() for llm in self.llms}

def create_llm_engine() -> LLMEngine:
    config = {"deepseek_api_key": None, "gigachat_credentials": None, "yandex_folder_id": None, "yandex_api_key": None}
    try:
        import streamlit as st
        config["deepseek_api_key"] = st.secrets.get("DEEPSEEK_API_KEY")
        config["gigachat_credentials"] = st.secrets.get("GIGACHAT_CREDENTIALS")
        config["yandex_folder_id"] = st.secrets.get("YANDEX_FOLDER_ID")
        config["yandex_api_key"] = st.secrets.get("YANDEX_API_KEY")
    except:
        config["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY")
    return LLMEngine(config)
