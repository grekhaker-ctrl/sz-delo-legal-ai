"""
Risk Analyzer - РЕАЛЬНЫЙ АНАЛИЗ ТЕКСТА ДОГОВОРА
Анализирует конкретный текст, а не шаблоны
"""
import logging
import re
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ContractRisk:
    title: str
    description: str
    legal_basis: str
    recommendation: str
    proposed_text: str
    risk_level: RiskLevel
    clause_text: str = ""
    clause_number: str = ""

class RiskAnalyzer:
    def __init__(self):
        pass
    
    def analyze_contract(self, contract_text: str) -> List[ContractRisk]:
        """РЕАЛЬНЫЙ анализ конкретного текста договора"""
        risks = []
        
        logger.info(f"Анализ договора ({len(contract_text)} симв.)")
        
        # 1. Анализируем предмет договора
        risk = self._analyze_subject(contract_text)
        if risk:
            risks.append(risk)
        
        # 2. Анализируем неустойку
        risk = self._analyze_penalty(contract_text)
        if risk:
            risks.append(risk)
        
        # 3. Анализируем ответственность
        risk = self._analyze_liability(contract_text)
        if risk:
            risks.append(risk)
        
        # 4. Анализируем приёмку работ
        risk = self._analyze_acceptance(contract_text)
        if risk:
            risks.append(risk)
        
        # 5. Анализируем гарантийный срок
        risk = self._analyze_warranty(contract_text)
        if risk:
            risks.append(risk)
        
        # 6. Анализируем расторжение
        risk = self._analyze_termination(contract_text)
        if risk:
            risks.append(risk)
        
        # 7. Анализируем цену и оплату
        risk = self._analyze_payment(contract_text)
        if risk:
            risks.append(risk)
        
        # 8. Анализируем форс-мажор
        risk = self._analyze_force_majeure(contract_text)
        if risk:
            risks.append(risk)
        
        # 9. Анализируем претензионный порядок
        risk = self._analyze_claims(contract_text)
        if risk:
            risks.append(risk)
        
        # 10. Анализируем качество работ
        risk = self._analyze_quality(contract_text)
        if risk:
            risks.append(risk)
        
        # Сортировка по уровню риска
        risks.sort(key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.risk_level.value), reverse=True)
        
        logger.info(f"Найдено рисков: {len(risks)}")
        return risks
    
    def _find_clause(self, text: str, keywords: List[str]) -> tuple:
        """Найти конкретный пункт договора с цитатой"""
        # Ищем пункты по номерам (1., 1.1., 2.3. и т.д.)
        pattern = r'(\d+(?:\.\d+)*)\.\s*([^\n]+(?:\n[^\n]+){0,5}?)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for num, clause_text in matches:
            for keyword in keywords:
                if keyword.lower() in clause_text.lower():
                    return num, clause_text.strip()[:500]
        
        return None, None
    
    def _analyze_subject(self, text: str) -> Optional[ContractRisk]:
        """Анализ предмета договора"""
        # Ищем раздел "Предмет"
        has_subject = 'предмет' in text.lower()
        has_object = any(word in text.lower() for word in ['объект', 'адрес', 'строительств', 'работ'])
        has_address = any(word in text.lower() for word in ['г.', 'город', 'ул.', 'улица', 'дом', 'адрес'])
        
        if not has_subject:
            num, clause = self._find_clause(text, ['предмет'])
            return ContractRisk(
                title="🔴 Неопределённый предмет договора",
                description="Раздел 'Предмет договора' отсутствует или не содержит существенных условий. Без предмета договор может быть признан незаключённым (ст. 432 ГК РФ).",
                legal_basis="Статья 432 ГК РФ — существенные условия договора",
                recommendation="Добавить чёткий предмет с адресом объекта и видами работ",
                proposed_text="Предмет договора: Подрядчик обязуется выполнить строительные работы по объекту: [полный адрес с кадастровым номером], а Заказчик принять и оплатить. Виды работ: согласно Смете (Приложение №1).",
                risk_level=RiskLevel.CRITICAL,
                clause_text=clause or "Раздел не найден в тексте",
                clause_number=num or "N/A"
            )
        
        if not has_address:
            return ContractRisk(
                title="⚠️ Не указан адрес объекта",
                description="В предмете договора не указан конкретный адрес объекта строительства.",
                legal_basis="Статья 702 ГК РФ — договор подряда",
                recommendation="Указать полный адрес с кадастровым номером",
                proposed_text="Объект: [полный адрес: город, улица, дом, кадастровый номер]",
                risk_level=RiskLevel.HIGH,
                clause_text="Адрес не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_penalty(self, text: str) -> Optional[ContractRisk]:
        """Анализ неустойки"""
        text_lower = text.lower()
        
        # Ищем проценты неустойки
        penalty_match = re.search(r'неустойк[аеи].*?(\d+[,.]?\d*)\s*%', text_lower)
        
        if penalty_match:
            try:
                rate = float(penalty_match.group(1).replace(',', '.'))
                num, clause = self._find_clause(text, ['неустойк', 'штраф', 'пен'])
                
                if rate > 0.5:
                    return ContractRisk(
                        title="🔴 Чрезмерная неустойка",
                        description=f"Найдена неустойка {rate}% в день. Это превышает рекомендуемые 0.1% и может быть уменьшено судом по ст. 333 ГК РФ.",
                        legal_basis="Статья 333 ГК РФ — уменьшение неустойки",
                        recommendation="Снизить до 0.1% в день, максимум 5% от цены",
                        proposed_text="Неустойка составляет 0.1% от стоимости невыполненных работ за каждый день просрочки, но не более 5% от общей стоимости договора.",
                        risk_level=RiskLevel.HIGH,
                        clause_text=clause or f"Найдено: {rate}%",
                        clause_number=num or "N/A"
                    )
                elif rate > 0.1:
                    return ContractRisk(
                        title="🟡 Повышенная неустойка",
                        description=f"Неустойка {rate}% в день выше рекомендуемых 0.1%.",
                        legal_basis="Статья 330 ГК РФ",
                        recommendation="Снизить до 0.1% в день",
                        proposed_text="Неустойка составляет 0.1% за каждый день просрочки.",
                        risk_level=RiskLevel.MEDIUM,
                        clause_text=clause or f"Найдено: {rate}%",
                        clause_number=num or "N/A"
                    )
            except:
                pass
        
        # Если неустойка не указана
        if 'неустойк' not in text_lower and 'штраф' not in text_lower and 'пен' not in text_lower:
            return ContractRisk(
                title="ℹ️ Неустойка не предусмотрена",
                description="В договоре отсутствуют условия о неустойке за просрочку выполнения работ.",
                legal_basis="Статья 330 ГК РФ",
                recommendation="Добавить условие о неустойке 0.1% в день",
                proposed_text="За просрочку выполнения работ Подрядчик уплачивает неустойку в размере 0.1% от стоимости работ за каждый день просрочки, но не более 5%.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Пункт о неустойке не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_liability(self, text: str) -> Optional[ContractRisk]:
        """Анализ ответственности"""
        text_lower = text.lower()
        
        # Ищем неограниченную ответственность
        if 'полная ответственность' in text_lower or 'неограниченн' in text_lower:
            num, clause = self._find_clause(text, ['ответствен', 'полная'])
            return ContractRisk(
                title="🔴 Неограниченная ответственность",
                description="Подрядчик несёт полную/неограниченную ответственность. Это создаёт финансовые риски.",
                legal_basis="Статья 401 ГК РФ",
                recommendation="Ограничить ответственность 50% от цены договора",
                proposed_text="Общая ответственность Подрядчика ограничивается суммой не более 50% от цены Договора.",
                risk_level=RiskLevel.HIGH,
                clause_text=clause or "Найдено условие о полной ответственности",
                clause_number=num or "N/A"
            )
        
        # Ищем упущенную выгоду
        if 'упущенн' in text_lower and 'выгод' in text_lower:
            num, clause = self._find_clause(text, ['упущенн', 'выгод'])
            if 'несёт' in text_lower or 'отвечает' in text_lower:
                return ContractRisk(
                    title="🔴 Ответственность за упущенную выгоду",
                    description="Подрядчик отвечает за упущенную выгоду Заказчика — это рискованно.",
                    legal_basis="Статья 15 ГК РФ",
                    recommendation="Исключить ответственность за упущенную выгоду",
                    proposed_text="Подрядчик не несёт ответственности за упущенную выгоду Заказчика.",
                    risk_level=RiskLevel.HIGH,
                    clause_text=clause or "Найдено условие об упущенной выгоде",
                    clause_number=num or "N/A"
                )
        
        # Если ответственность не ограничена
        if 'огранич' not in text_lower and 'лимит' not in text_lower:
            return ContractRisk(
                title="🟡 Ответственность не ограничена",
                description="В договоре нет ограничения общей ответственности Подрядчика.",
                legal_basis="Статья 401 ГК РФ",
                recommendation="Добавить лимит ответственности 50% от цены",
                proposed_text="Общая ответственность Подрядчика ограничена 50% от цены Договора.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Ограничение ответственности не найдено",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_acceptance(self, text: str) -> Optional[ContractRisk]:
        """Анализ приёмки работ"""
        text_lower = text.lower()
        
        # Ищем КС-2, КС-11, акт
        has_ks2 = 'кс-2' in text_lower or 'акт' in text_lower
        has_ks11 = 'кс-11' in text_lower
        
        if not has_ks2:
            return ContractRisk(
                title="🟡 Нет порядка приёмки",
                description="Не указан порядок приёмки работ (формы КС-2, КС-11).",
                legal_basis="Статья 720 ГК РФ",
                recommendation="Добавить порядок приёмки по КС-2 в течение 5 дней",
                proposed_text="Приёмка работ осуществляется по актам формы КС-2 и справке КС-11 в течение 5 рабочих дней.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Порядок приёмки не найден",
                clause_number="N/A"
            )
        
        # Проверяем срок приёмки
        acceptance_match = re.search(r'приёмк.*?(\d+)\s*(дн|день|рабоч)', text_lower)
        if acceptance_match:
            days = int(acceptance_match.group(1))
            if days < 3:
                num, clause = self._find_clause(text, ['приёмк', 'акт'])
                return ContractRisk(
                    title="ℹ️ Короткий срок приёмки",
                    description=f"Срок приёмки {days} дн. — недостаточно для проверки качества.",
                    legal_basis="Статья 720 ГК РФ",
                    recommendation="Увеличить до 5-10 рабочих дней",
                    proposed_text="Приёмка работ осуществляется в течение 5 (пяти) рабочих дней.",
                    risk_level=RiskLevel.LOW,
                    clause_text=clause or f"Срок: {days} дней",
                    clause_number=num or "N/A"
                )
        
        return None
    
    def _analyze_warranty(self, text: str) -> Optional[ContractRisk]:
        """Анализ гарантийного срока"""
        text_lower = text.lower()
        
        # Ищем гарантийный срок
        warranty_match = re.search(r'гарантийн.*?срок.*?(\d+)\s*(лет|год|года)', text_lower)
        
        if warranty_match:
            years = int(warranty_match.group(1))
            num, clause = self._find_clause(text, ['гаранти'])
            
            if years < 3:
                return ContractRisk(
                    title="🟡 Короткий гарантийный срок",
                    description=f"Гарантийный срок {years} г. — меньше рекомендуемых 5 лет для строительства.",
                    legal_basis="Статья 756 ГК РФ",
                    recommendation="Установить 5 лет для строительных работ",
                    proposed_text="Гарантийный срок на выполненные работы составляет 5 (пять) лет.",
                    risk_level=RiskLevel.MEDIUM,
                    clause_text=clause or f"Гарантия: {years} лет",
                    clause_number=num or "N/A"
                )
        elif 'гаранти' not in text_lower:
            return ContractRisk(
                title="🔴 Нет гарантийного срока",
                description="Гарантийный срок не указан — это существенное условие для строительства.",
                legal_basis="Статья 756 ГК РФ",
                recommendation="Добавить гарантийный срок 5 лет",
                proposed_text="Гарантийный срок на выполненные работы составляет 5 (пять) лет с даты подписания итогового акта.",
                risk_level=RiskLevel.HIGH,
                clause_text="Гарантийный срок не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_termination(self, text: str) -> Optional[ContractRisk]:
        """Анализ расторжения"""
        text_lower = text.lower()
        
        # Ищем одностороннее расторжение
        if 'односторонн' in text_lower and 'расторж' in text_lower:
            if 'заказчик вправе расторгнуть' in text_lower and 'подрядчик вправе' not in text_lower:
                num, clause = self._find_clause(text, ['расторж', 'односторонн'])
                return ContractRisk(
                    title="🔴 Одностороннее расторжение",
                    description="Только Заказчик может расторгнуть договор — неравные условия.",
                    legal_basis="Статья 717 ГК РФ",
                    recommendation="Добавить взаимное право на расторжение",
                    proposed_text="Любая Сторона вправе расторгнуть Договор при существенном нарушении с уведомлением за 30 дней.",
                    risk_level=RiskLevel.HIGH,
                    clause_text=clause or "Найдено одностороннее право",
                    clause_number=num or "N/A"
                )
        
        if 'расторж' not in text_lower:
            return ContractRisk(
                title="ℹ️ Нет порядка расторжения",
                description="Не указан порядок расторжения договора.",
                legal_basis="Статья 717 ГК РФ",
                recommendation="Добавить условие о расторжении",
                proposed_text="Любая Сторона вправе расторгнуть Договор с уведомлением за 30 дней.",
                risk_level=RiskLevel.LOW,
                clause_text="Порядок расторжения не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_payment(self, text: str) -> Optional[ContractRisk]:
        """Анализ оплаты"""
        text_lower = text.lower()
        
        # Ищем аванс
        advance_match = re.search(r'аванс.*?(\d+)\s*%', text_lower)
        if advance_match:
            percent = int(advance_match.group(1))
            if percent > 50:
                num, clause = self._find_clause(text, ['аванс', 'предоплат'])
                return ContractRisk(
                    title="🟡 Высокий аванс",
                    description=f"Аванс {percent}% — высокий риск для Заказчика.",
                    legal_basis="Статья 711 ГК РФ",
                    recommendation="Снизить до 30% или требовать банковскую гарантию",
                    proposed_text="Аванс выплачивается при условии предоставления банковской гарантии на сумму аванса.",
                    risk_level=RiskLevel.MEDIUM,
                    clause_text=clause or f"Аванс: {percent}%",
                    clause_number=num or "N/A"
                )
        
        # Ищем порядок оплаты
        if 'оплат' not in text_lower and 'цена' not in text_lower:
            return ContractRisk(
                title="🔴 Нет порядка оплаты",
                description="Не указан порядок оплаты работ.",
                legal_basis="Статья 711 ГК РФ",
                recommendation="Добавить порядок оплаты по КС-2 в течение 10 дней",
                proposed_text="Оплата производится в течение 10 дней после подписания КС-2.",
                risk_level=RiskLevel.HIGH,
                clause_text="Порядок оплаты не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_force_majeure(self, text: str) -> Optional[ContractRisk]:
        """Анализ форс-мажора"""
        text_lower = text.lower()
        
        if 'форс-мажор' not in text_lower and 'непреодолим' not in text_lower:
            return ContractRisk(
                title="ℹ️ Нет форс-мажора",
                description="Отсутствует раздел о форс-мажорных обстоятельствах.",
                legal_basis="Статья 401 ГК РФ",
                recommendation="Добавить раздел о форс-мажоре",
                proposed_text="Стороны освобождаются от ответственности при наступлении обстоятельств непреодолимой силы.",
                risk_level=RiskLevel.LOW,
                clause_text="Форс-мажор не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_claims(self, text: str) -> Optional[ContractRisk]:
        """Анализ претензионного порядка"""
        text_lower = text.lower()
        
        if 'претензи' not in text_lower and 'досудебн' not in text_lower:
            return ContractRisk(
                title="ℹ️ Нет претензионного порядка",
                description="Не указан обязательный досудебный порядок урегулирования споров.",
                legal_basis="Статья 4 АПК РФ",
                recommendation="Добавить претензионный порядок 30 дней",
                proposed_text="Все споры урегулируются в досудебном порядке. Претензия рассматривается в течение 30 дней.",
                risk_level=RiskLevel.LOW,
                clause_text="Претензионный порядок не найден",
                clause_number="N/A"
            )
        
        return None
    
    def _analyze_quality(self, text: str) -> Optional[ContractRisk]:
        """Анализ качества работ"""
        text_lower = text.lower()
        
        has_gost = 'гост' in text_lower
        has_snip = 'снип' in text_lower or 'сп ' in text_lower
        has_quality = 'качеств' in text_lower
        
        if not has_quality and not has_gost and not has_snip:
            return ContractRisk(
                title="🟡 Нет условий о качестве",
                description="Не указаны требования к качеству работ (ГОСТ, СНиП).",
                legal_basis="Статья 721 ГК РФ",
                recommendation="Добавить ссылки на ГОСТ и СНиП",
                proposed_text="Работы выполняются в соответствии с ГОСТ, СНиП и проектной документацией.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Требования к качеству не найдены",
                clause_number="N/A"
            )
        
        return None
    
    def calculate_risk_score(self, risks: List[ContractRisk]) -> int:
        """Расчёт уровня риска (0-10)"""
        if not risks:
            return 0
        
        scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        total = sum(scores[r.risk_level] for r in risks)
        score = min(10, max(1, total // 2))
        
        return score
    
    def get_conclusion(self, risks: List[ContractRisk]) -> str:
        """Заключение по договору"""
        if not risks:
            return "✅ Можно подписывать"
        
        score = self.calculate_risk_score(risks)
        critical = sum(1 for r in risks if r.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for r in risks if r.risk_level == RiskLevel.HIGH)
        
        if critical > 0:
            return "❌ Не рекомендуется подписывать"
        elif high > 2 or score > 7:
            return "⚠️ Можно подписывать, но с правками"
        elif score > 4:
            return "⚠️ Можно подписывать, но с правками"
        else:
            return "✅ Можно подписывать"


def create_risk_analyzer() -> RiskAnalyzer:
    return RiskAnalyzer()
