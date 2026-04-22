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
        
        # 1. Предмет договора
        risk = self._analyze_subject(contract_text)
        if risk: risks.append(risk)
        
        # 2. Неустойка
        risk = self._analyze_penalty(contract_text)
        if risk: risks.append(risk)
        
        # 3. Ответственность
        risk = self._analyze_liability(contract_text)
        if risk: risks.append(risk)
        
        # 4. Приёмка работ
        risk = self._analyze_acceptance(contract_text)
        if risk: risks.append(risk)
        
        # 5. Гарантийный срок
        risk = self._analyze_warranty(contract_text)
        if risk: risks.append(risk)
        
        # 6. Расторжение
        risk = self._analyze_termination(contract_text)
        if risk: risks.append(risk)
        
        # 7. Оплата
        risk = self._analyze_payment(contract_text)
        if risk: risks.append(risk)
        
        # 8. Форс-мажор
        risk = self._analyze_force_majeure(contract_text)
        if risk: risks.append(risk)
        
        # 9. Претензионный порядок
        risk = self._analyze_claims(contract_text)
        if risk: risks.append(risk)
        
        # 10. Качество работ
        risk = self._analyze_quality(contract_text)
        if risk: risks.append(risk)
        
        risks.sort(key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.risk_level.value), reverse=True)
        logger.info(f"Найдено рисков: {len(risks)}")
        return risks
    
    def _find_clause(self, text: str, keywords: List[str]) -> tuple:
        """Найти конкретный пункт договора с цитатой"""
        pattern = r'(\d+(?:\.\d+)*)\.\s*([^\n]+(?:\n[^\n]+){0,5}?)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for num, clause_text in matches:
            for keyword in keywords:
                if keyword.lower() in clause_text.lower():
                    return num, clause_text.strip()[:500]
        return None, None
    
    def _analyze_subject(self, text: str) -> Optional[ContractRisk]:
        has_subject = 'предмет' in text.lower()
        has_object = any(word in text.lower() for word in ['объект', 'адрес', 'строительств', 'работ'])
        has_address = any(word in text.lower() for word in ['г.', 'город', 'ул.', 'улица', 'дом', 'адрес'])
        
        if not has_subject:
            num, clause = self._find_clause(text, ['предмет'])
            return ContractRisk(
                title="🔴 Неопределённый предмет договора",
                description="Раздел 'Предмет договора' отсутствует. Без предмета договор может быть признан незаключённым (ст. 432 ГК РФ).",
                legal_basis="Статья 432 ГК РФ — существенные условия договора",
                recommendation="Добавить чёткий предмет с адресом объекта и видами работ",
                proposed_text="Предмет договора: Подрядчик обязуется выполнить строительные работы по объекту: [полный адрес с кадастровым номером], а Заказчик принять и оплатить.",
                risk_level=RiskLevel.CRITICAL,
                clause_text=clause or "Раздел не найден",
                clause_number=num or "N/A"
            )
        
        if not has_address:
            return ContractRisk(
                title="⚠️ Не указан адрес объекта",
                description="В предмете договора не указан конкретный адрес объекта.",
                legal_basis="Статья 702 ГК РФ — договор подряда",
                recommendation="Указать полный адрес с кадастровым номером",
                proposed_text="Объект: [полный адрес: город, улица, дом, кадастровый номер]",
                risk_level=RiskLevel.HIGH,
                clause_text="Адрес не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_penalty(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        penalty_match = re.search(r'неустойк[аеи].*?(\d+[,.]?\d*)\s*%', text_lower)
        
        if penalty_match:
            try:
                rate = float(penalty_match.group(1).replace(',', '.'))
                num, clause = self._find_clause(text, ['неустойк', 'штраф', 'пен'])
                
                if rate > 0.5:
                    return ContractRisk(
                        title="🔴 Чрезмерная неустойка",
                        description=f"Найдена неустойка {rate}% в день. Это превышает рекомендуемые 0.1%.",
                        legal_basis="Статья 333 ГК РФ — уменьшение неустойки",
                        recommendation="Снизить до 0.1% в день, максимум 5% от цены",
                        proposed_text="Неустойка составляет 0.1% за каждый день просрочки, но не более 5% от стоимости договора.",
                        risk_level=RiskLevel.HIGH,
                        clause_text=clause or f"Найдено: {rate}%",
                        clause_number=num or "N/A"
                    )
            except: pass
        
        if 'неустойк' not in text_lower and 'штраф' not in text_lower:
            return ContractRisk(
                title="ℹ️ Неустойка не предусмотрена",
                description="В договоре отсутствуют условия о неустойке.",
                legal_basis="Статья 330 ГК РФ",
                recommendation="Добавить условие о неустойке 0.1% в день",
                proposed_text="За просрочку Подрядчик уплачивает неустойку 0.1% от стоимости работ за каждый день, но не более 5%.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Пункт о неустойке не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_liability(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        
        if 'полная ответственность' in text_lower or 'неограниченн' in text_lower:
            num, clause = self._find_clause(text, ['ответствен', 'полная'])
            return ContractRisk(
                title="🔴 Неограниченная ответственность",
                description="Подрядчик несёт полную ответственность — это рискованно.",
                legal_basis="Статья 401 ГК РФ",
                recommendation="Ограничить ответственность 50% от цены договора",
                proposed_text="Общая ответственность Подрядчика ограничена 50% от цены Договора.",
                risk_level=RiskLevel.HIGH,
                clause_text=clause or "Найдено условие о полной ответственности",
                clause_number=num or "N/A"
            )
        
        if 'упущенн' in text_lower and 'выгод' in text_lower:
            return ContractRisk(
                title="🔴 Ответственность за упущенную выгоду",
                description="Подрядчик отвечает за упущенную выгоду — это рискованно.",
                legal_basis="Статья 15 ГК РФ",
                recommendation="Исключить ответственность за упущенную выгоду",
                proposed_text="Подрядчик не несёт ответственности за упущенную выгоду.",
                risk_level=RiskLevel.HIGH,
                clause_text="Найдено условие об упущенной выгоде",
                clause_number="N/A"
            )
        return None
    
    def _analyze_acceptance(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        has_ks2 = 'кс-2' in text_lower or 'акт' in text_lower
        
        if not has_ks2:
            return ContractRisk(
                title="🟡 Нет порядка приёмки",
                description="Не указан порядок приёмки работ (формы КС-2, КС-11).",
                legal_basis="Статья 720 ГК РФ",
                recommendation="Добавить порядок приёмки по КС-2 в течение 5 дней",
                proposed_text="Приёмка работ осуществляется по актам формы КС-2 в течение 5 рабочих дней.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Порядок приёмки не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_warranty(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        warranty_match = re.search(r'гарантийн.*?срок.*?(\d+)\s*(лет|год|года)', text_lower)
        
        if warranty_match:
            years = int(warranty_match.group(1))
            if years < 3:
                num, clause = self._find_clause(text, ['гаранти'])
                return ContractRisk(
                    title="🟡 Короткий гарантийный срок",
                    description=f"Гарантийный срок {years} г. — меньше рекомендуемых 5 лет.",
                    legal_basis="Статья 756 ГК РФ",
                    recommendation="Установить 5 лет для строительных работ",
                    proposed_text="Гарантийный срок составляет 5 (пять) лет.",
                    risk_level=RiskLevel.MEDIUM,
                    clause_text=clause or f"Гарантия: {years} лет",
                    clause_number=num or "N/A"
                )
        elif 'гаранти' not in text_lower:
            return ContractRisk(
                title="🔴 Нет гарантийного срока",
                description="Гарантийный срок не указан.",
                legal_basis="Статья 756 ГК РФ",
                recommendation="Добавить гарантийный срок 5 лет",
                proposed_text="Гарантийный срок на выполненные работы составляет 5 (пять) лет.",
                risk_level=RiskLevel.HIGH,
                clause_text="Гарантийный срок не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_termination(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        
        if 'односторонн' in text_lower and 'расторж' in text_lower:
            if 'заказчик вправе' in text_lower and 'подрядчик вправе' not in text_lower:
                return ContractRisk(
                    title="🔴 Одностороннее расторжение",
                    description="Только Заказчик может расторгнуть договор — неравные условия.",
                    legal_basis="Статья 717 ГК РФ",
                    recommendation="Добавить взаимное право на расторжение",
                    proposed_text="Любая Сторона вправе расторгнуть Договор при существенном нарушении с уведомлением за 30 дней.",
                    risk_level=RiskLevel.HIGH,
                    clause_text="Найдено одностороннее право",
                    clause_number="N/A"
                )
        return None
    
    def _analyze_payment(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        
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
        text_lower = text.lower()
        
        if 'форс-мажор' not in text_lower and 'непреодолим' not in text_lower:
            return ContractRisk(
                title="ℹ️ Нет форс-мажора",
                description="Отсутствует раздел о форс-мажоре.",
                legal_basis="Статья 401 ГК РФ",
                recommendation="Добавить раздел о форс-мажоре",
                proposed_text="Стороны освобождаются от ответственности при форс-мажоре.",
                risk_level=RiskLevel.LOW,
                clause_text="Форс-мажор не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_claims(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        
        if 'претензи' not in text_lower and 'досудебн' not in text_lower:
            return ContractRisk(
                title="ℹ️ Нет претензионного порядка",
                description="Не указан досудебный порядок.",
                legal_basis="Статья 4 АПК РФ",
                recommendation="Добавить претензионный порядок 30 дней",
                proposed_text="Споры урегулируются в досудебном порядке. Претензия рассматривается 30 дней.",
                risk_level=RiskLevel.LOW,
                clause_text="Претензионный порядок не найден",
                clause_number="N/A"
            )
        return None
    
    def _analyze_quality(self, text: str) -> Optional[ContractRisk]:
        text_lower = text.lower()
        
        if 'качеств' not in text_lower and 'гост' not in text_lower and 'снип' not in text_lower:
            return ContractRisk(
                title="🟡 Нет условий о качестве",
                description="Не указаны требования к качеству (ГОСТ, СНиП).",
                legal_basis="Статья 721 ГК РФ",
                recommendation="Добавить ссылки на ГОСТ и СНиП",
                proposed_text="Работы выполняются в соответствии с ГОСТ, СНиП и проектной документацией.",
                risk_level=RiskLevel.MEDIUM,
                clause_text="Требования к качеству не найдены",
                clause_number="N/A"
            )
        return None
    
    def calculate_risk_score(self, risks: List[ContractRisk]) -> int:
        if not risks: return 0
        scores = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        total = sum(scores[r.risk_level] for r in risks)
        return min(10, max(1, total // 2))
    
    def get_conclusion(self, risks: List[ContractRisk]) -> str:
        if not risks: return "✅ Можно подписывать"
        critical = sum(1 for r in risks if r.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for r in risks if r.risk_level == RiskLevel.HIGH)
        if critical > 0: return "❌ Не рекомендуется подписывать"
        elif high > 2: return "⚠️ Можно подписывать, но с правками"
        else: return "✅ Можно подписывать"

def create_risk_analyzer() -> RiskAnalyzer:
    return RiskAnalyzer()
