"""
LLM Engine для ИИ-юриста СЗ Дело
YandexGPT + GigaChat + Fallback
"""
import os
import json
import logging
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — юридический ИИ-агент компании "СЗ Дело", строительной компании из Москвы/МО.
Специализация: строительные договоры (подряд, субподряд, поставка, аренда).
Отвечай ТОЛЬКО на юридические вопросы. Всегда структурируй ответ, указывай статьи ГК РФ.
Для каждого риска предлагай новую формулировку."""

LEGAL_KEYWORDS = [
    'договор', 'пункт', 'статья', 'закон', 'фз', 'кодекс', 'право', 'гк рф', 'ук рф',
    'суд', 'иск', 'ответственность', 'неустойка', 'штраф', 'пеня', 'подряд', 'субподряд',
    'аренд', 'поставк', 'заказчик', 'подрядчик', 'оплат', 'срок', 'качество', 'расторжени',
    'претензи', 'обязан', 'вправе', 'можно ли', 'нужно ли', 'что такое', 'как'
]

NON_LEGAL_RESPONSE = "Я юридический помощник. Отвечаю только на вопросы по праву и договорам."

class Message(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    text: str
    model: str
    success: bool
    error: Optional[str] = None

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        pass
    @abstractmethod
    def is_available(self) -> bool:
        pass

class YandexGPT(BaseLLM):
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        # ПРАВИЛЬНЫЙ ENDPOINT для YandexGPT Lite
        self.endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    def is_available(self) -> bool:
        return bool(self.folder_id and self.api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            # Формируем сообщение в формате YandexGPT
            prompt_text = ""
            for msg in messages:
                prompt_text += f"{msg.role}: {msg.content}\n"
            
            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json",
                "X-Data-Logging-Uuid": "sz-delo-legal-ai"
            }
            
            payload = {
                "modelUri": f"gcp://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.3,
                    "maxTokens": 2000
                },
                "messages": [
                    {"role": "system", "text": SYSTEM_PROMPT},
                    {"role": "user", "text": prompt_text}
                ]
            }
            
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Извлекаем текст ответа
            text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not text:
                text = result.get("result", {}).get("text", "")
            
            return LLMResponse(text=text, model="yandexgpt", success=True)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"YandexGPT network error: {e}")
            return LLMResponse(text="", model="yandexgpt", success=False, error=f"Network: {str(e)}")
        except Exception as e:
            logger.error(f"YandexGPT error: {e}")
            return LLMResponse(text="", model="yandexgpt", success=False, error=str(e))

class GigaChat(BaseLLM):
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
            headers = {
                "RqUID": "12345678-1234-1234-1234-123456789012",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {self.credentials}"
            }
            data = {"scope": "GIGACHAT_API_PERS"}
            
            response = requests.post(auth_url, headers=headers, data=data, timeout=30, verify=False)
            response.raise_for_status()
            token = response.json().get("access_token")
            self._token = token
            return token
        except Exception as e:
            logger.error(f"GigaChat token error: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        try:
            token = self._get_token()
            if not token:
                return LLMResponse(text="", model="gigachat", success=False, error="Token error")
            
            full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in messages:
                full_messages.append({"role": msg.role, "content": msg.content})
            
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "GigaChat",
                "messages": full_messages,
                "temperature": 0.3
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
            response.raise_for_status()
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return LLMResponse(text=text, model="gigachat", success=True)
        except Exception as e:
            logger.error(f"GigaChat error: {e}")
            return LLMResponse(text="", model="gigachat", success=False, error=str(e))

class FallbackLLM(BaseLLM):
    def is_available(self) -> bool:
        return True
    
    def generate(self, messages: List[Message], context: str = "") -> LLMResponse:
        last_message = messages[-1].content if messages else ""
        
        # Простые ответы на частые вопросы
        if "неустойк" in last_message.lower():
            text = "Неустойка (ст. 330 ГК РФ) — денежная сумма, которую должник уплачивает кредитору при неисполнении обязательства.\n\nДля строительных договоров рекомендуется:\n- 0.1% в день за просрочку\n- Максимум 5% от цены договора\n- Статья 333 ГК РФ позволяет уменьшить неустойку"
        elif "гарантий" in last_message.lower():
            text = "Гарантийный срок в строительстве (ст. 756 ГК РФ):\n\n- Минимум: 2 года\n- Рекомендуется: 5 лет\n- Отсчитывается с даты приёмки работ\n\nВ течение гарантийного срока подрядчик устраняет недостатки бесплатно."
        elif "расторжени" in last_message.lower():
            text = "Расторжение договора подряда (ст. 717 ГК РФ):\n\n- Заказчик может расторгнуть в любое время до сдачи работ\n- Подрядчик вправе требовать оплату за выполненную часть\n- Уведомление: 30 дней рекомендуется\n\nПри существенном нарушении — любая сторона может расторгнуть."
        elif "приёмк" in last_message.lower():
            text = "Приёмка работ (ст. 720 ГК РФ):\n\n- Форма: КС-2 (акт), КС-11 (справка)\n- Срок: 5 рабочих дней рекомендуется\n- При недостатках: мотивированный отказ\n\nЗаказчик обязан осмотреть работы и принять результат."
        elif "ответственност" in last_message.lower():
            text = "Ответственность в строительных договорах (ст. 401 ГК РФ):\n\n- Рекомендуется ограничить: 50% от цены договора\n- Исключить упущенную выгоду\n- За умысел или грубую неосторожность — полная ответственность"
        else:
            text = f"⚠️ ИИ временно недоступен.\n\nВаш вопрос: \"{last_message[:100]}\"\n\nПопробуйте позже или задайте вопрос про:\n- Неустойку\n- Гарантийный срок\n- Расторжение договора\n- Приёмку работ"
        
        return LLMResponse(text=text, model="fallback", success=True)

class LLMEngine:
    def __init__(self, config: Dict):
        self.llms: List[BaseLLM] = []
        if config.get("yandex_folder_id") and config.get("yandex_api_key"):
            self.llms.append(YandexGPT(config["yandex_folder_id"], config["yandex_api_key"]))
        if config.get("gigachat_credentials"):
            self.llms.append(GigaChat(config["gigachat_credentials"]))
        self.llms.append(FallbackLLM())
        logger.info(f"LLM Engine: {len(self.llms)} providers")
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None) -> LLMResponse:
        messages = history or []
        messages.append(Message(role="user", content=user_message))
        
        for llm in self.llms:
            if not llm.is_available():
                continue
            logger.info(f"Trying: {llm.__class__.__name__}")
            response = llm.generate(messages, context)
            if response.success and response.text.strip():
                logger.info(f"Success: {llm.__class__.__name__}")
                return response
        
        logger.warning("All LLMs failed, using fallback")
        return FallbackLLM().generate(messages, context)

def create_llm_engine() -> LLMEngine:
    """Создание LLM Engine (поддержка Streamlit Cloud)"""
    import os
    
    try:
        import streamlit as st
        config = {
            "yandex_folder_id": st.secrets.get("YANDEX_FOLDER_ID", ""),
            "yandex_api_key": st.secrets.get("YANDEX_API_KEY", ""),
            "gigachat_credentials": st.secrets.get("GIGACHAT_CREDENTIALS", "")
        }
        logger.info("Using st.secrets (Streamlit Cloud)")
    except:
        config = {
            "yandex_folder_id": os.getenv("YANDEX_FOLDER_ID", ""),
            "yandex_api_key": os.getenv("YANDEX_API_KEY", ""),
            "gigachat_credentials": os.getenv("GIGACHAT_CREDENTIALS", "")
        }
        logger.info("Using os.getenv (local)")
    
    return LLMEngine(config)
