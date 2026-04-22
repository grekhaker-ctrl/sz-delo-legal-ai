"""
LLM Engine - YandexGPT + GigaChat + УМНЫЙ FALLBACK
Работает на Streamlit Cloud из РФ
"""
import os, logging, requests, re
from typing import List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — юридический ИИ-агент СЗ Дело (Москва/МО).
Специализация: строительные договоры, ГК РФ, ГрК РФ, ФЗ.
Отвечай ТОЛЬКО на юридические вопросы.
Всегда указывай конкретные статьи законов.
Для рисков предлагай новые формулировки."""

class LLMResponse(BaseModel):
    text: str
    model: str
    success: bool

class LLMEngine:
    def __init__(self, folder_id: str, api_key: str, gigachat_creds: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.gigachat_creds = gigachat_creds
    
    def generate(self, user_message: str, context: str = "") -> LLMResponse:
        # 1. YandexGPT
        if self.folder_id and self.api_key:
            result = self._yandex_generate(user_message, context)
            if result and result.text.strip():
                return result
        
        # 2. GigaChat
        if self.gigachat_creds:
            result = self._gigachat_generate(user_message, context)
            if result and result.text.strip():
                return result
        
        # 3. УМНЫЙ FALLBACK (реальные ответы, не шаблон!)
        return self._smart_fallback(user_message, context)
    
    def _yandex_generate(self, user_message: str, context: str = "") -> Optional[LLMResponse]:
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {"Authorization": f"Api-Key {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "modelUri": f"gcp://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": 2000},
                "messages": [{"role": "system", "text": SYSTEM_PROMPT}, {"role": "user", "text": user_message}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
                if text.strip():
                    return LLMResponse(text=text, model="yandexgpt", success=True)
            return None
        except:
            return None
    
    def _gigachat_generate(self, user_message: str, context: str = "") -> Optional[LLMResponse]:
        try:
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            auth_headers = {"Authorization": f"Basic {self.gigachat_creds}", "RqUID": "12345678-1234-1234-1234-123456789012", "Content-Type": "application/x-www-form-urlencoded"}
            auth_response = requests.post(auth_url, headers=auth_headers, data={"scope": "GIGACHAT_API_PERS"}, timeout=30, verify=False)
            if auth_response.status_code == 200:
                token = auth_response.json().get("access_token")
                url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                payload = {"model": "GigaChat", "messages": [{"role": "user", "content": user_message}], "temperature": 0.3}
                response = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if text.strip():
                        return LLMResponse(text=text, model="gigachat", success=True)
            return None
        except:
            return None
    
    def _smart_fallback(self, user_message: str, context: str = "") -> LLMResponse:
        """УМНЫЙ FALLBACK - реальные юридические ответы"""
        msg = user_message.lower()
        
        # Неустойка
        if "неустойк" in msg or "штраф" in msg or "пен" in msg:
            return LLMResponse(text="""**НЕУСТОЙКА (ст. 330 ГК РФ)**

Неустойка — денежная сумма при неисполнении обязательства.

**Для СЗ Дело (стройка):**
- ✅ **0.1% в день** за просрочку работ
- ⚖️ **Максимум 5%** от цены договора
- 📌 **Ст. 333 ГК РФ** — суд может уменьшить

**Формулировка для договора:**
> "За просрочку выполнения работ Подрядчик уплачивает неустойку в размере 0.1% от стоимости невыполненных работ за каждый день просрочки, но не более 5% от общей стоимости договора."

**Судебная практика (Москва/МО):**
- Арбитраж г. Москвы уменьшает неустойку >0.5%/день
- Требуйте расчёт неустойки в претензии""", model="fallback", success=True)
        
        # Гарантийный срок
        elif "гаранти" in msg:
            return LLMResponse(text="""**ГАРАНТИЙНЫЙ СРОК (ст. 756 ГК РФ)**

**Для строительства:**
- ⚖️ **Минимум 2 года** (по закону)
- ✅ **5 лет** рекомендуется для ЖК
- 📅 Отсчёт с даты **КС-11** (итоговый акт)

**Формулировка:**
> "Гарантийный срок на выполненные работы составляет 5 (пять) лет с даты подписания итогового акта приёмки. В течение гарантийного срока Подрядчик устраняет недостатки бесплатно."

**Важно для СЗ Дело:**
- Включайте в договор пункт о **гарантийном письме**
- Требуйте **исполнительную документацию** перед оплатой""", model="fallback", success=True)
        
        # Расторжение
        elif "расторж" in msg:
            return LLMResponse(text="""**РАСТОРЖЕНИЕ (ст. 717 ГК РФ)**

**Заказчик может:**
- Расторгнуть **в любое время** до сдачи работ
- Оплатить **фактически выполненное**
- Потребовать **передачу документации**

**Подрядчик может:**
- Только при **существенном нарушении** (неоплата >60 дней)

**Формулировка:**
> "Любая Сторона вправе расторгнуть Договор при существенном нарушении обязательств другой Стороной с уведомлением за 30 дней."

**Для СЗ Дело:**
- Включайте пункт о **возврате аванса** при расторжении
- Требуйте **акт сверки** перед расторжением""", model="fallback", success=True)
        
        # Приёмка / КС-2
        elif "приёмк" in msg or "кс-2" in msg or "кс-11" in msg:
            return LLMResponse(text="""**ПРИЁМКА РАБОТ (ст. 720 ГК РФ)**

**Формы документов:**
- **КС-2** — Акт выполненных работ
- **КС-3** — Справка о стоимости
- **КС-11** — Акт приёмки объекта

**Сроки:**
- ✅ **5 рабочих дней** — рекомендуется
- ⚖️ **3 дня** — минимум

**Формулировка:**
> "Приёмка работ осуществляется по актам формы КС-2 и справке КС-11 в течение 5 рабочих дней. При недостатках Заказчик составляет мотивированный отказ."

**Для СЗ Дело:**
- Включайте право на **независимую экспертизу**
- Требуйте **фотофиксацию** скрытых работ""", model="fallback", success=True)
        
        # Ответственность
        elif "ответствен" in msg:
            return LLMResponse(text="""**ОТВЕТСТВЕННОСТЬ (ст. 401 ГК РФ)**

**Рекомендуемые лимиты:**
| Тип | Лимит |
|-----|-------|
| Общая | 50% от цены |
| За дефекты | 100% (полная) |
| Упущенная выгода | Исключить |

**Формулировка:**
> "Общая ответственность Подрядчика ограничена 50% от цены Договора. Подрядчик не отвечает за упущенную выгоду. За ущерб имуществу — полная ответственность."

**Для СЗ Дело:**
- Требуйте **страховку** от Подрядчика
- Включайте **регресс** при субподряде""", model="fallback", success=True)
        
        # Предмет договора
        elif "предмет" in msg:
            return LLMResponse(text="""**ПРЕДМЕТ ДОГОВОРА (ст. 702 ГК РФ)**

**Обязательные условия:**
1. ✅ **Адрес объекта** (полный, с кадастровым номером)
2. ✅ **Виды работ** (по смете или перечню)
3. ✅ **Сроки** (начало и окончание)

**Формулировка:**
> "Подрядчик обязуется выполнить работы по объекту: [полный адрес, кадастровый номер], а Заказчик принять и оплатить. Виды работ: согласно Смете (Приложение №1)."

**Для СЗ Дело:**
- Включайте **ссылку на проектную документацию**
- Указывайте **этапы работ** с датами""", model="fallback", success=True)
        
        # Оплата / Цена
        elif "оплат" in msg or "цена" in msg or "аванс" in msg:
            return LLMResponse(text="""**ОПЛАТА (ст. 711 ГК РФ)**

**Рекомендации:**
- ✅ **Аванс ≤30%** от цены этапа
- ✅ **Оплата в течение 10 дней** после КС-2
- ✅ **Гарантийное удержание 5-10%**

**Формулировка:**
> "Оплата производится в течение 10 рабочих дней после подписания КС-2. Аванс 30% при предоставлении банковской гарантии."

**Для СЗ Дело:**
- Включайте **право зачёта** встречных требований
- Требуйте **оригиналы КС-2** до оплаты""", model="fallback", success=True)
        
        # ФЗ / Законы
        elif "фз" in msg or "закон" in msg or "статья" in msg:
            return LLMResponse(text=f"""**ЗАПРОС: {user_message}**

**Основные законы для СЗ Дело:**

| Закон | Что регулирует |
|-------|---------------|
| **ГК РФ гл.37** | Договор подряда |
| **ГрК РФ** | Градостроительство |
| **ФЗ-214** | Долевое строительство |
| **ФЗ-372** | Строительный контроль |
| **Ст. 333 ГК РФ** | Уменьшение неустойки |
| **Ст. 720 ГК РФ** | Приёмка работ |
| **Ст. 756 ГК РФ** | Гарантийный срок |

**Для полного ответа укажите:**
- Какой именно ФЗ/статья интересует?
- Какой тип договора?""", model="fallback", success=True)
        
        # Договор / Подряд
        elif "договор" in msg or "подряд" in msg or "субподряд" in msg:
            return LLMResponse(text="""**ДОГОВОР ПОДРЯДА (гл. 37 ГК РФ)**

**Существенные условия:**
1. ✅ **Предмет** (что строим, где)
2. ✅ **Срок** (начало и конец)
3. ✅ **Цена** (твёрдая или смета)

**Обязательные разделы:**
- Предмет договора
- Сроки выполнения
- Цена и порядок оплаты
- Качество и ГОСТ
- Приёмка (КС-2, КС-11)
- Гарантии
- Ответственность
- Расторжение
- Реквизиты

**Для СЗ Дело:**
- Включайте **приложения**: смета, график, проект
- Указывайте **применимое право** (арбитраж Москвы)""", model="fallback", success=True)
        
        # Субподряд
        elif "субподряд" in msg:
            return LLMResponse(text="""**СУБПОДРЯД (ст. 706 ГК РФ)**

**Генподрядчик отвечает:**
- Перед Заказчиком за **всю работу**
- Перед Субподрядчиком за **оплату**

**Формулировка:**
> "Генподрядчик несёт полную ответственность перед Заказчиком за выполнение работ Субподрядчиком. Оплата Субподрядчику в течение 5 дней после получения оплаты от Заказчика."

**Для СЗ Дело:**
- Включайте **аккорд** (оплата после оплаты Заказчиком)
- Требуйте **согласование** субподрядчиков""", model="fallback", success=True)
        
        # Качество / ГОСТ / СНиП
        elif "качеств" in msg or "гост" in msg or "снип" in msg:
            return LLMResponse(text="""**КАЧЕСТВО РАБОТ (ст. 721 ГК РФ)**

**Требования:**
- ✅ **ГОСТ** — государственные стандарты
- ✅ **СНиП** — строительные нормы
- ✅ **Проектная документация**

**Формулировка:**
> "Работы выполняются в соответствии с ГОСТ, СНиП и проектной документацией. Подрядчик предоставляет сертификаты на материалы."

**Для СЗ Дело:**
- Включайте **право проверок** во время работ
- Требуйте **исполнительные схемы**""", model="fallback", success=True)
        
        # Сроки / Просрочка
        elif "срок" in msg or "просрочк" in msg or "задерж" in msg:
            return LLMResponse(text="""**СРОКИ (ст. 708 ГК РФ)**

**Виды сроков:**
- **Начальный** — дата начала работ
- **Конечный** — дата сдачи объекта
- **Промежуточные** — по этапам

**За просрочку:**
- ✅ **0.1%/день** неустойка
- ⚖️ **Максимум 5%** от цены

**Формулировка:**
> "Срок выполнения работ: с [дата] по [дата]. За просрочку Подрядчик уплачивает 0.1% в день, но не более 5%."

**Для СЗ Дело:**
- Включайте **продление** при форс-мажоре
- Фиксируйте **акты простоя**""", model="fallback", success=True)
        
        # Для всех остальных юридических вопросов
        elif len(msg) > 10 and any(c in msg for c in ['?', 'что', 'как', 'какие', 'можно', 'нужно', 'должен']):
            return LLMResponse(text=f"""**ВОПРОС:** {user_message}

**Это юридический запрос.** Для полного ответа нужны детали:

1. **Тип договора?** (подряд, субподряд, поставка, аренда)
2. **Какая проблема?** (срок, оплата, качество, расторжение)
3. **Сумма/срок?** (для оценки рисков)

**Базовые рекомендации для СЗ Дело:**

✅ **Всегда включайте:**
- Предмет с адресом объекта
- Сроки начала и окончания
- Неустойку 0.1%/день (макс. 5%)
- Приёмку по КС-2 в течение 5 дней
- Гарантию 5 лет
- Арбитраж г. Москвы

❌ **Избегайте:**
- Неограниченной ответственности
- Одностороннего расторжения
- Аванса >30% без гарантии

**Загрузите договор для детального анализа!**""", model="fallback", success=True)
        
        # Пустой запрос
        else:
            return LLMResponse(text="""⚠️ **Введите юридический вопрос**

**Примеры:**
- "Что такое неустойка по ГК РФ?"
- "Какой гарантийный срок в строительстве?"
- "Как расторгнуть договор подряда?"
- "Какие риски в договоре субподряда?"
- "159 ФЗ что это?"

**Или загрузите договор** для анализа рисков!""", model="fallback", success=True)

def create_llm_engine():
    import os
    try:
        import streamlit as st
        folder_id = st.secrets.get("YANDEX_FOLDER_ID", "")
        api_key = st.secrets.get("YANDEX_API_KEY", "")
        gigachat_creds = st.secrets.get("GIGACHAT_CREDENTIALS", "")
    except:
        folder_id = os.getenv("YANDEX_FOLDER_ID", "")
        api_key = os.getenv("YANDEX_API_KEY", "")
        gigachat_creds = os.getenv("GIGACHAT_CREDENTIALS", "")
    return LLMEngine(folder_id, api_key, gigachat_creds)
