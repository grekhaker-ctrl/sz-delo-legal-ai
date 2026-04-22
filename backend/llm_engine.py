"""
LLM Engine - YandexGPT + GigaChat
"""
import os
import logging
from typing import List, Dict, Optional
import requests
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты - юридический консультант компании СЗ Дело.
Ты специализируешься на всех отраслях права РФ: ГК РФ, ТК РФ, АПК РФ, КоАП и др.
Ты даёшь РАЗВЁРНУТЫЕ ответы минимум 500 слов.
Ты всегда указываешь статьи законов с ссылками на КонсультантПлюс.
Ты думаешь как опытный юрист - анализируешь риски, последствия, альтернативы."""

class Message(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    text: str
    model: str
    success: bool
    error: Optional[str] = None

class YandexGPT:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.endpoint = "https://llm.cloud.yandex.net/text-generator/v1/generate"
    
    def is_available(self) -> bool:
        return bool(self.folder_id and self.api_key)
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            full_messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nКонтекст:\n{context}"}]
            for m in messages:
                full_messages.append({"role": m.role, "content": m.content})
            headers = {"Authorization": f"Api-Key {self.api_key}", "Content-Type": "application/json"}
            payload = {"modelUri": f"gcp://{self.folder_id}/yandexgpt-lite", "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 4096}, "messages": full_messages}
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            return LLMResponse(text=r.json().get("result", {}).get("text", ""), model="yandexgpt", success=True)
        except Exception as e:
            logger.error(f"YandexGPT: {e}")
            return LLMResponse(text="", model="yandexgpt", success=False, error=str(e))

class FallbackLLM:
    def is_available(self) -> bool: return True
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        return LLMResponse(text="ИИ временно недоступен. Попробуйте позже.", model="fallback", success=True)

class LLMEngine:
    def __init__(self, config: Dict):
        self.llms = []
        if config.get("yandex_folder_id") and config.get("yandex_api_key"):
            self.llms.append(YandexGPT(folder_id=config["yandex_folder_id"], api_key=config["yandex_api_key"]))
        self.llms.append(FallbackLLM())
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None) -> LLMResponse:
        messages = list(history) if history else []
        messages.append(Message(role="user", content=user_message))
        for llm in self.llms:
            if not llm.is_available(): continue
            r = llm.generate(messages, context)
            if r.success and r.text: return r
        return FallbackLLM().generate(messages, context)
    
    def get_status(self) -> Dict:
        return {llm.__class__.__name__: llm.is_available() for llm in self.llms}

def create_llm_engine() -> LLMEngine:
    try:
        import streamlit as st
        config = {"yandex_folder_id": st.secrets.get("YANDEX_FOLDER_ID"), "yandex_api_key": st.secrets.get("YANDEX_API_KEY")}
    except:
        config = {"yandex_folder_id": os.getenv("YANDEX_FOLDER_ID"), "yandex_api_key": os.getenv("YANDEX_API_KEY")}
    return LLMEngine(config)
