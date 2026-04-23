"""
LLM Engine - Polza AI + DeepSeek + GigaChat
"""
import os
import re
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

class PolzaAILLM:
    """Polza AI API - https://polza.ai"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polza.ai/v1"
        self.endpoint = f"{self.base_url}/chat/completions"
        self.model = "gpt-4o-mini"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None, task: str = "answer") -> LLMResponse:
        try:
            # Улучшенный системный промпт для точных юридических ответов
            if task == "fix_contract":
                system_prompt = """ТЫ - СТАРШИЙ ЮРИСТ СТРОИТЕЛЬНОЙ КОМПАНИИ СЗ ДЕЛО (МОСКВА/МО).

⚠️ КРИТИЧЕСКИ ВАЖНО:
1. Используй ТОЛЬКО актуальные законы РФ (редакция 2024-2025)
2. Проверяй статьи по официальным источникам:
   - КонсультантПлюс: https://www.consultant.ru
   - Гарант: https://www.garant.ru
   - Верховный Суд РФ: https://vsrf.ru
3. НЕ ВЫДУМЫВАЙ статьи, номера и законы
4. Если не уверен - пиши "Требуется проверка по КонсультантПлюс"
5. Указывай ТОЧНЫЕ номера статей (например: "ст. 743 ГК РФ", а не "статья ГК")

📚 ОСНОВНЫЕ ЗАКОНЫ ДЛЯ СТРОИТЕЛЬСТВА:
- ГК РФ: Глава 37 (Подряд), §3 (Строительный подряд)
- ГрК РФ (Градостроительный кодекс)
- ФЗ-214 (Долевое строительство)
- ФЗ-372 (Изменения в ГК РФ)
- СНиП и ГОСТ (строительные нормы)

ТВОЯ ЗАДАЧА:
1. Проанализировать договор подряда
2. Найти рискованные пункты
3. Предложить исправления
4. Указать КОНКРЕТНЫЕ статьи с номерами

ФОРМАТ ОТВЕТА:
### Анализ
[Тип, стороны, предмет, цена, сроки]

### Проблемы
1. [Пункт] - [Проблема] - [Ст. XXX ГК РФ]

### Исправленный текст
[ПОЛНЫЙ текст]

### Таблица
| № | Было | Стало | Статья |"""
            else:
                system_prompt = """ТЫ - СТАРШИЙ ЮРИСТ СТРОИТЕЛЬНОЙ КОМПАНИИ СЗ ДЕЛО (МОСКВА/МО).

⚠️ КРИТИЧЕСКИ ВАЖНО:
1. ОТВЕТЫ ЧЁТКИЕ, ПРАВИЛЬНЫЕ, БЕЗ ВОДЫ
2. МАКСИМУМ 450 СЛОВ - развёрнуто но без лишней информации
3. ТОЧНЫЕ НОМЕРА СТАТЕЙ (ст. 708 ГК РФ)
4. ТОЧНЫЕ СРОКИ И ЦИФРЫ
5. АКТУАЛЬНОСТЬ НА 2025 ГОД
6. БЕЗ ОБЩИХ ФРАЗ - только факты
7. ИСПОЛЬЗУЙ МАРКЕРЫ (-) для списков
8. КАЖДЫЙ АБЗАЦ С НОВОЙ СТРОКИ

📚 ОСНОВНЫЕ ЗАКОНЫ (АКТУАЛЬНО НА 2025):

НАЛОГИ:
- НДС: 20% (ст. 164 НК РФ)
- НДФЛ: 13% до 5 млн руб., 15% свыше 5 млн (ст. 224 НК РФ)
- Страховые взносы: 30% (Глава 32 НК РФ)

СРОКИ:
- Ст. 708 ГК РФ - сроки в договоре подряда
- Ст. 196 ГК РФ - исковая давность 3 года
- Ст. 725 ГК РФ - срок по договору подряда

ОТВЕТСТВЕННОСТЬ:
- Ст. 330 ГК РФ - неустойка
- Ст. 393 ГК РФ - убытки
- Ст. 401 ГК РФ - ответственность

🔗 ФОРМАТ ССЫЛОК НА СТАТЬИ (ОБЯЗАТЕЛЬНО):
Каждую статью указывай с прямой ссылкой на КонсультантПлюс:
- Ст. 196 ГК РФ: https://www.consultant.ru/document/cons_doc_LAW_28165/6f4e0d0c8e5c5c5c5c5c5c5c5c5c5c5c/
- Ст. 708 ГК РФ: https://www.consultant.ru/document/cons_doc_LAW_28165/abc123/
- Ст. 164 НК РФ: https://www.consultant.ru/document/cons_doc_LAW_28166/def456/
- 149-ФЗ: https://www.consultant.ru/document/cons_doc_LAW_52690/
- 152-ФЗ: https://www.consultant.ru/document/cons_doc_LAW_61737/

ФОРМАТ ССЫЛКИ: https://www.consultant.ru/document/cons_doc_LAW_[номер_документа]/

📋 ФОРМАТ ОТВЕТА (СТРОГО):

[1-2 предложения с кратким ответом]

Правовое основание:
- Статья XXX: [краткое пояснение]
- Статья YYY: [краткое пояснение]

[Развёрнутый анализ - 150-200 слов]

Сроки и цифры:
- [конкретный срок 1]
- [конкретный срок 2]

Что делать:
1. [первое действие]
2. [второе действие]
3. [третье действие]

Источник: КонсультантПлюс 2025 (https://www.consultant.ru)

ПРИМЕР ХОРОШЕГО ОТВЕТА:

Срок исковой давности по договору подряда составляет 3 года (ст. 196 ГК РФ).

Правовое основание:
- Статья 196 ГК РФ: общий срок исковой давности 3 года (https://www.consultant.ru/document/cons_doc_LAW_28165/)
- Статья 200 ГК РФ: начало с момента нарушения (https://www.consultant.ru/document/cons_doc_LAW_28165/)
- Статья 725 ГК РФ: специальный срок по подряду (https://www.consultant.ru/document/cons_doc_LAW_28165/)

Согласно ст. 725 ГК РФ, срок исковой давности по требованиям о недостатках работы начинается с момента сдачи работы заказчику. Если недостатки обнаружены позднее, срок исчисляется с момента их обнаружения. Срок нельзя восстановить после истечения.

Сроки и цифры:
- Общий срок: 3 года
- Начало: день сдачи работы или обнаружения недостатков
- Последствия пропуска: отказ в иске (ст. 199 ГК РФ)

Что делать:
1. Фиксируйте дату сдачи работы актом
2. Проводите осмотр после сдачи
3. При недостатках пишите претензию
4. Подавайте иск в течение 3 лет
5. Храните документы 4 года

Источник: КонсультантПлюс 2025 (https://www.consultant.ru/document/cons_doc_LAW_28165/)

НЕЛЬЗЯ:
- Всё в одну строку
- Без маркеров списков
- Заголовки (#, ##, ###)
- Более 450 слов"""
            
            full_messages = [{"role": "system", "content": f"{system_prompt}\n\nКонтекст из базы знаний:\n{context}"}]
            if history:
                for m in history:
                    full_messages.append({"role": m.role, "content": m.content})
            full_messages.append({"role": "user", "content": user_message})
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": full_messages, "temperature": 0.3, "max_tokens": 4096}
            
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            
            if r.status_code != 200:
                return LLMResponse(text="", model=self.model, success=False, error=f"HTTP {r.status_code}: {r.text[:200]}")
            
            result = r.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not text:
                return LLMResponse(text="", model=self.model, success=False, error="Пустой ответ")
            
            # Очистка от некорректных символов (только кириллица, латиница, цифры, базовая пунктуация)
            text = re.sub(r'[^\u0400-\u04FFa-zA-Z0-9\s.,;:!?\"\'()\-\/\\@#$%&*+=<>{}[\]|~`]', '', text)
            
            return LLMResponse(text=text, model=self.model, success=True)
            
        except Exception as e:
            return LLMResponse(text="", model=self.model, success=False, error=str(e))

class DeepSeekLLM:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.endpoint = f"{self.base_url}/chat/completions"
        self.model = "deepseek-chat"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None, task: str = "answer") -> LLMResponse:
        try:
            if task == "fix_contract":
                system_prompt = """Ты - опытный юрист строительной компании СЗ Дело.
Твоя задача:
1. Проанализировать договор подряда
2. Найти все рискованные пункты
3. Предложить исправленный текст с изменениями
4. Указать КОНКРЕТНЫЕ статьи ГК РФ

Формат ответа:
### 📊 Анализ договора
[Тип договора, стороны, предмет]

### ⚠️ Найденные риски
1. [Риск] - [Статья ГК РФ]
2. ...

### ✅ Исправленный текст договора
[ПОЛНЫЙ текст договора с ИСПРАВЛЕНИЯМИ]

### 📝 Список изменений
| Пункт | Было | Стало | Обоснование |
|-------|------|-------|-------------|
| ... | ... | ... | ... |"""
            else:
                system_prompt = """Ты - юридический консультант компании СЗ Дело.
Ты специализируешься на всех отраслях права РФ."""
            
            full_messages = [{"role": "system", "content": f"{system_prompt}\n\nКонтекст:\n{context}"}]
            if history:
                for m in history:
                    full_messages.append({"role": m.role, "content": m.content})
            full_messages.append({"role": "user", "content": user_message})
            
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": full_messages, "temperature": 0.3, "max_tokens": 4096}
            
            r = requests.post(self.endpoint, headers=headers, json=payload, timeout=90)
            
            if r.status_code != 200:
                return LLMResponse(text="", model=self.model, success=False, error=f"HTTP {r.status_code}")
            
            result = r.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not text:
                return LLMResponse(text="", model=self.model, success=False, error="Пустой ответ")
            
            # Очистка от некорректных символов
            text = re.sub(r'[^\u0400-\u04FFa-zA-Z0-9\s.,;:!?\"\'()\-\/\\@#$%&*+=<>{}[\]|~`]', '', text)
            
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
        except Exception as e:
            return LLMResponse(text="", model="gigachat", success=False, error=str(e))

class LLMEngine:
    def __init__(self, config: Dict):
        self.llms = []
        
        # Polza AI (приоритет)
        if config.get("polza_api_key"):
            self.llms.append(PolzaAILLM(api_key=config["polza_api_key"]))
        
        # DeepSeek
        if config.get("deepseek_api_key"):
            self.llms.append(DeepSeekLLM(api_key=config["deepseek_api_key"]))
        
        # GigaChat
        if config.get("gigachat_credentials"):
            self.llms.append(GigaChat(credentials=config["gigachat_credentials"]))
    
    def generate(self, user_message: str, context: str = "", history: List[Message] = None, task: str = "answer") -> LLMResponse:
        messages = list(history) if history else []
        
        errors = []
        for llm in self.llms:
            if not llm.is_available():
                continue
            response = llm.generate(user_message, context, messages, task)
            if response.success and response.text:
                return response
            errors.append(f"{llm.__class__.__name__}: {response.error}")
        
        error_info = "\n".join(errors) if errors else "Нет доступных LLM"
        return LLMResponse(
            text=f"""⚠️ **ИИ-движок не ответил**

**Ошибки:**
{error_info}

**Ваш вопрос:** {user_message[:200]}

**Что делать:**
1. Проверьте API ключ в Secrets
2. Проверьте лимиты API
3. Попробуйте позже""",
            model="fallback",
            success=True
        )
    
    def get_status(self) -> Dict:
        return {llm.__class__.__name__: llm.is_available() for llm in self.llms}

def create_llm_engine() -> LLMEngine:
    config = {"polza_api_key": None, "deepseek_api_key": None, "gigachat_credentials": None}
    try:
        import streamlit as st
        config["polza_api_key"] = st.secrets.get("POLZA_API_KEY")
        config["deepseek_api_key"] = st.secrets.get("DEEPSEEK_API_KEY")
        config["gigachat_credentials"] = st.secrets.get("GIGACHAT_CREDENTIALS")
    except:
        config["polza_api_key"] = os.getenv("POLZA_API_KEY")
        config["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY")
    return LLMEngine(config)
