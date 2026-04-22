"""
LLM Engine - GigaChat + YandexGPT + Умный Fallback
Работает на Streamlit Cloud из РФ
"""
import os, logging, requests
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — профессиональный юрист компании "СЗ Дело" (строительство, Москва/МО).
Специализация: договоры подряда, субподряда, поставки, аренды.
Отвечай ТОЛЬКО на юридические вопросы.
ВСЕГДА указывай конкретные статьи ГК РФ, ГрК РФ, ФЗ.
ВСЕГДА давай практические рекомендации для СЗ Дело.
ВСЕГДА предлагай готовые формулировки для договоров.
Структурируй ответ: заголовки, списки, таблицы."""

class LLMResponse(BaseModel):
    text: str
    model: str
    success: bool
    error: Optional[str] = None

class LLMEngine:
    def __init__(self, gigachat_creds: str, yandex_folder: str = "", yandex_key: str = ""):
        self.gigachat_creds = gigachat_creds
        self.yandex_folder = yandex_folder
        self.yandex_key = yandex_key
        self._gigachat_token = None
        logger.info(f"LLM Engine инициализирован: GigaChat={bool(gigachat_creds)}, YandexGPT={bool(yandex_folder)}")
    
    def generate(self, user_message: str, context: str = "") -> LLMResponse:
        logger.info(f"Запрос: {user_message[:100]}...")
        
        # 1. GigaChat (основной)
        if self.gigachat_creds:
            result = self._gigachat_generate(user_message, context)
            if result and result.success and result.text.strip():
                logger.info(f"✅ GigaChat ответил ({len(result.text)} симв.)")
                return result
            logger.warning(f"GigaChat не ответил: {result.error if result else 'None'}")
        
        # 2. YandexGPT (резерв)
        if self.yandex_folder and self.yandex_key:
            result = self._yandex_generate(user_message, context)
            if result and result.success and result.text.strip():
                logger.info(f"✅ YandexGPT ответил ({len(result.text)} симв.)")
                return result
            logger.warning(f"YandexGPT не ответил: {result.error if result else 'None'}")
        
        # 3. Умный fallback
        logger.warning("Используем умный fallback")
        return self._fallback(user_message, context)
    
    def _gigachat_generate(self, user_message: str, context: str = "") -> Optional[LLMResponse]:
        """GigaChat API"""
        try:
            if not self._gigachat_token:
                auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
                auth_headers = {
                    "Authorization": f"Basic {self.gigachat_creds}",
                    "RqUID": "12345678-1234-1234-1234-123456789012",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                auth_response = requests.post(auth_url, headers=auth_headers, data={"scope": "GIGACHAT_API_PERS"}, timeout=30, verify=False)
                if auth_response.status_code == 200:
                    self._gigachat_token = auth_response.json().get("access_token")
                    logger.info("✅ GigaChat токен получен")
                else:
                    logger.error(f"GigaChat auth: {auth_response.status_code}")
                    return LLMResponse(text="", model="gigachat", success=False, error=f"Auth failed: {auth_response.status_code}")
            
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self._gigachat_token}", "Content-Type": "application/json"}
            
            prompt = user_message
            if context:
                prompt = f"Контекст из базы знаний:\n{context}\n\nВопрос пользователя: {user_message}"
            
            payload = {
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=120, verify=False)
            logger.info(f"GigaChat HTTP {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if text.strip():
                    return LLMResponse(text=text, model="gigachat", success=True)
            
            logger.error(f"GigaChat error: {response.text}")
            return LLMResponse(text="", model="gigachat", success=False, error=f"HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"GigaChat exception: {e}")
            return LLMResponse(text="", model="gigachat", success=False, error=str(e))
    
    def _yandex_generate(self, user_message: str, context: str = "") -> Optional[LLMResponse]:
        """YandexGPT API"""
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {"Authorization": f"Api-Key {self.yandex_key}", "Content-Type": "application/json"}
            payload = {
                "modelUri": f"gcp://{self.yandex_folder}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 2000},
                "messages": [{"role": "system", "text": SYSTEM_PROMPT}, {"role": "user", "text": user_message}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
                if text.strip():
                    return LLMResponse(text=text, model="yandexgpt", success=True)
            return LLMResponse(text="", model="yandexgpt", success=False, error=f"HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"YandexGPT exception: {e}")
            return LLMResponse(text="", model="yandexgpt", success=False, error=str(e))
    
    def _fallback(self, user_message: str, context: str = "") -> LLMResponse:
        """Умный fallback с реальными юридическими ответами"""
        msg = user_message.lower()
        
        # Неустойка
        if "неустойк" in msg or "штраф" in msg or "пен" in msg:
            text = """## НЕУСТОЙКА В СТРОИТЕЛЬНЫХ ДОГОВОРАХ

### 📌 Нормативная база

| Статья | Что регулирует |
|--------|---------------|
| **ст. 330 ГК РФ** | Определение неустойки |
| **ст. 333 ГК РФ** | Уменьшение неустойки судом |
| **ст. 332 ГК РФ** | Законная неустойка |

### ⚖️ Для СЗ Дело (рекомендации)

**Оптимальные условия:**
- ✅ **0.1% в день** за просрочку работ
- ⚠️ **Не более 5%** от цены договора
- 📅 **Срок:** с даты окончания работ

**Формулировка для договора:**
> "За просрочку выполнения работ Подрядчик уплачивает неустойку в размере 0.1% от стоимости невыполненных в срок работ за каждый день просрочки, но не более 5% от общей стоимости Договора."

### 🏛️ Судебная практика (Москва/МО)

**Арбитраж г. Москвы:**
- Уменьшает неустойку >0.5%/день по ст. 333 ГК РФ
- Требует расчёт неустойки в претензии

**Нужен анализ конкретного договора? Загрузите файл!**"""
        
        # Гарантийный срок
        elif "гаранти" in msg:
            text = """## ГАРАНТИЙНЫЙ СРОК В СТРОИТЕЛЬСТВЕ

### 📌 Нормативная база

| Статья | Что регулирует |
|--------|---------------|
| **ст. 756 ГК РФ** | Гарантийный срок в строительстве |
| **ст. 722 ГК РФ** | Гарантия качества работы |
| **ст. 724 ГК РФ** | Сроки обнаружения недостатков |

### ⚖️ Для СЗ Дело (рекомендации)

**Оптимальные условия:**
- ✅ **5 лет** для жилых комплексов
- ✅ **5 лет** для коммерческой недвижимости
- ⚠️ **Минимум 2 года** по закону
- 📅 **Отсчёт:** с даты КС-11

**Формулировка для договора:**
> "Гарантийный срок на выполненные работы составляет 5 (пять) лет с даты подписания итогового акта приёмки по форме КС-11."

**Нужен анализ договора? Загрузите файл!**"""
        
        # Расторжение
        elif "расторж" in msg:
            text = """## РАСТОРЖЕНИЕ ДОГОВОРА ПОДРЯДА

### 📌 Нормативная база

| Статья | Что регулирует |
|--------|---------------|
| **ст. 717 ГК РФ** | Отказ заказчика от договора |
| **ст. 450 ГК РФ** | Расторжение по соглашению |

### ⚖️ Для СЗ Дело (рекомендации)

**Заказчик может:**
- ✅ Расторгнуть **в любое время** до сдачи
- ✅ Оплатить **фактически выполненное**

**Подрядчик может:**
- ⚠️ Только при **неоплате >60 дней**

**Формулировка:**
> "Любая Сторона вправе расторгнуть Договор при существенном нарушении с уведомлением за 30 дней."

**Нужен анализ договора? Загрузите файл!**"""
        
        # Приёмка
        elif "приёмк" in msg or "кс-" in msg:
            text = """## ПРИЁМКА РАБОТ (КС-2, КС-11)

### 📌 Нормативная база

| Статья | Что регулирует |
|--------|---------------|
| **ст. 720 ГК РФ** | Приёмка результата работ |
| **ст. 721 ГК РФ** | Качество работ |

### ⚖️ Для СЗ Дело (рекомендации)

**Формы документов:**
- ✅ **КС-2** — Акт выполненных работ
- ✅ **КС-3** — Справка о стоимости
- ✅ **КС-11** — Акт приёмки объекта

**Оптимальные сроки:**
- ✅ **5 рабочих дней** на приёмку

**Формулировка:**
> "Приёмка работ осуществляется по актам формы КС-2 и справке КС-11 в течение 5 рабочих дней."

**Нужен анализ договора? Загрузите файл!**"""
        
        # Ответственность
        elif "ответствен" in msg:
            text = """## ОТВЕТСТВЕННОСТЬ СТОРОН

### 📌 Нормативная база

| Статья | Что регулирует |
|--------|---------------|
| **ст. 401 ГК РФ** | Ответственность за нарушение |
| **ст. 15 ГК РФ** | Возмещение убытков |

### ⚖️ Для СЗ Дело (рекомендации)

**Оптимальные лимиты:**

| Тип ответственности | Лимит |
|---------------------|-------|
| Общая ответственность | 50% от цены |
| За дефекты качества | 100% (полная) |
| Упущенная выгода | Исключить |

**Формулировка:**
> "Общая ответственность Подрядчика ограничена 50% от цены Договора. Подрядчик не отвечает за упущенную выгоду."

**Нужен анализ договора? Загрузите файл!**"""
        
        # ФЗ / Законы
        elif "фз" in msg or "закон" in msg or "статья" in msg:
            text = f"""## ЗАПРОС ПО ЗАКОНОДАТЕЛЬСТВУ

**Ваш вопрос:** {user_message}

### 📌 Основные законы для СЗ Дело

| Закон | Что регулирует |
|-------|---------------|
| **ГК РФ гл.37** | Договор подряда (ст. 702-768) |
| **ГрК РФ** | Градостроительный кодекс |
| **ФЗ-214** | Долевое строительство |
| **ФЗ-372** | Строительный контроль |

### ⚖️ Ключевые статьи ГК РФ

| Статья | Содержание |
|--------|-----------|
| **ст. 330** | Неустойка |
| **ст. 333** | Уменьшение неустойки |
| **ст. 401** | Ответственность |
| **ст. 702** | Договор подряда |
| **ст. 720** | Приёмка работ |
| **ст. 756** | Гарантийный срок |

**Нужен анализ договора? Загрузите файл!**"""
        
        # Договор / Подряд
        elif "договор" in msg or "подряд" in msg:
            text = """## ДОГОВОР ПОДРЯДА (гл. 37 ГК РФ)

### 📌 Существенные условия (ст. 432 ГК РФ)

| Условие | Обязательно |
|---------|-------------|
| Предмет договора | ✅ Да |
| Срок выполнения | ✅ Да |
| Цена работ | ✅ Да |

**Без этих условий договор НЕ заключён!**

### ⚖️ Для СЗ Дело (рекомендации)

**Обязательные разделы:**
1. ✅ Предмет (адрес, виды работ)
2. ✅ Сроки (начало, окончание, этапы)
3. ✅ Цена (твёрдая или смета)
4. ✅ Оплата (аванс, график, КС-2)
5. ✅ Качество (ГОСТ, СНиП, проект)
6. ✅ Приёмка (КС-2, КС-11, сроки)
7. ✅ Гарантии (срок, обязательства)
8. ✅ Ответственность (лимиты, неустойка)
9. ✅ Расторжение (порядок, сроки)
10. ✅ Реквизиты (ИНН, адреса, подписи)

**Нужен анализ договора? Загрузите файл!**"""
        
        # Для всех остальных вопросов
        elif len(msg) > 10:
            text = f"""**Вопрос:** {user_message}

**Это юридический запрос.** Для полного ответа от ИИ убедитесь что:
1. ✅ GigaChat настроен в Secrets
2. ✅ Ключи API корректны

**Базовая информация:**
- **ГК РФ** — Гражданский кодекс (глава 37 — Подряд)
- **ГрК РФ** — Градостроительный кодекс
- **ФЗ-214** — Долевое строительство
- **ФЗ-372** — Строительный контроль

**Загрузите договор для детального анализа!**"""
        
        else:
            text = """⚠️ **Введите юридический вопрос**

**Примеры:**
- "Что такое неустойка по ГК РФ?"
- "Какой гарантийный срок в строительстве?"
- "Как расторгнуть договор подряда?"
- "Какие риски в договоре субподряда?"

**Или загрузите договор для анализа!**"""
        
        return LLMResponse(text=text, model="fallback", success=True)

def create_llm_engine():
    import os
    try:
        import streamlit as st
        gigachat_creds = st.secrets.get("GIGACHAT_CREDENTIALS", "")
        yandex_folder = st.secrets.get("YANDEX_FOLDER_ID", "")
        yandex_key = st.secrets.get("YANDEX_API_KEY", "")
        logger.info("✅ Используем st.secrets (Streamlit Cloud)")
    except:
        gigachat_creds = os.getenv("GIGACHAT_CREDENTIALS", "")
        yandex_folder = os.getenv("YANDEX_FOLDER_ID", "")
        yandex_key = os.getenv("YANDEX_API_KEY", "")
        logger.info("✅ Используем os.getenv (локально)")
    return LLMEngine(gigachat_creds, yandex_folder, yandex_key)
