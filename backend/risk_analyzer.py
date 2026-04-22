"""
Risk Analyzer для ИИ-юриста СЗ Дело
Анализ рисков строительных договоров
"""
import logging
from typing import List, Dict, Optional
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
    """Риск в договоре"""
    title: str
    description: str
    legal_basis: str
    recommendation: str
    proposed_text: str = ""
    risk_level: RiskLevel = RiskLevel.MEDIUM


class RiskAnalyzer:
    """Анализ рисков договоров"""
    
    def __init__(self):
        self.risk_patterns = self._init_risk_patterns()
    
    def _init_risk_patterns(self) -> List[Dict]:
        """Шаблоны рисков для строительных договоров"""
        return [
            {
                'name': 'Чрезмерная неустойка',
                'keywords': ['неустойка', 'штраф', 'пеня', '0.5%', '1%', '2%'],
                'pattern': r'(неустойка|штраф|пеня).*?(\d+[,.]?\d*)\s*%',
                'risk_level': RiskLevel.HIGH,
                'legal_basis': 'Статья 333 ГК РФ — уменьшение неустойки судом',
                'recommendation': 'Снизить неустойку до 0.1% в день',
                'proposed_text': 'Неустойка составляет 0.1% от стоимости невыполненных работ за каждый день просрочки, но не более 5% от общей стоимости договора.',
                'description': 'Чрезмерно высокая неустойка может быть уменьшена судом, но создаёт риски'
            },
            {
                'name': 'Неограниченная ответственность',
                'keywords': ['полная ответственность', 'неограниченная', 'все убытки', 'упущенная выгода'],
                'pattern': r'(полная|неограниченная)\s*ответственность',
                'risk_level': RiskLevel.HIGH,
                'legal_basis': 'Статья 401 ГК РФ — ответственность за нарушение обязательств',
                'recommendation': 'Ограничить ответственность 50% от цены договора',
                'proposed_text': 'Общая ответственность Подрядчика ограничивается суммой не более 50% от цены Договора. Подрядчик не несёт ответственности за упущенную выгоду.',
                'description': 'Неограниченная ответственность создаёт финансовые риски'
            },
            {
                'name': 'Отсутствие порядка приёмки',
                'keywords': ['приёмка', 'акт', 'кс-2', 'кс-11'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.MEDIUM,
                'legal_basis': 'Статья 720 ГК РФ — приёмка результата работ',
                'recommendation': 'Добавить раздел о порядке приёмки работ',
                'proposed_text': 'Приёмка работ осуществляется по актам формы КС-2 и справке КС-11 в течение 5 рабочих дней с даты подачи.',
                'description': 'Отсутствие порядка приёмки может привести к спорам'
            },
            {
                'name': 'Короткий гарантийный срок',
                'keywords': ['гарантийный срок', 'гарантия', '1 год', '2 года'],
                'pattern': r'гарантийный\s*срок.*?(\d+)\s*(год|лет|года)',
                'risk_level': RiskLevel.MEDIUM,
                'legal_basis': 'Статья 756 ГК РФ — гарантийный срок в строительстве',
                'recommendation': 'Установить гарантийный срок не менее 5 лет',
                'proposed_text': 'Гарантийный срок на выполненные работы составляет 5 (пять) лет с даты подписания итогового акта приёмки.',
                'description': 'Короткий гарантийный срок недостаточен для строительства'
            },
            {
                'name': 'Одностороннее расторжение',
                'keywords': ['расторжение', 'односторонний', 'без причин'],
                'pattern': r'расторгнуть.*?(односторонний|без\s*причин)',
                'risk_level': RiskLevel.HIGH,
                'legal_basis': 'Статья 717 ГК РФ — отказ заказчика от договора',
                'recommendation': 'Добавить взаимное право на расторжение',
                'proposed_text': 'Любая Сторона вправе расторгнуть Договор при существенном нарушении обязательств другой Стороной с уведомлением за 30 дней.',
                'description': 'Одностороннее право расторжения создаёт нестабильность'
            },
            {
                'name': 'Отсутствие форс-мажора',
                'keywords': ['форс-мажор', 'непреодолимая сила'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.LOW,
                'legal_basis': 'Статья 401 ГК РФ — обстоятельства непреодолимой силы',
                'recommendation': 'Добавить раздел о форс-мажоре',
                'proposed_text': 'Стороны освобождаются от ответственности при наступлении обстоятельств непреодолимой силы. Сторона должна уведомить другую сторону в течение 5 дней.',
                'description': 'Отсутствие форс-мажора создаёт риски при ЧП'
            },
            {
                'name': 'Неясные условия о качестве',
                'keywords': ['качество', 'гост', 'снип', 'норматив'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.MEDIUM,
                'legal_basis': 'Статья 721 ГК РФ — качество работ',
                'recommendation': 'Добавить ссылки на ГОСТ и СНиП',
                'proposed_text': 'Работы выполняются в соответствии с ГОСТ, СНиП и проектной документацией.',
                'description': 'Неясные условия о качестве могут привести к спорам'
            },
            {
                'name': 'Отсутствие графика работ',
                'keywords': ['график', 'календарный план', 'этапы'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.MEDIUM,
                'legal_basis': 'Статья 708 ГК РФ — сроки выполнения работ',
                'recommendation': 'Добавить календарный график работ',
                'proposed_text': 'Работы выполняются согласно календарному графику (Приложение №1).',
                'description': 'Отсутствие графика затрудняет контроль сроков'
            },
            {
                'name': 'Аванс без обеспечения',
                'keywords': ['аванс', 'предоплата', '30%', '50%'],
                'pattern': r'аванс.*?(\d+)\s*%',
                'risk_level': RiskLevel.MEDIUM,
                'legal_basis': 'Статья 711 ГК РФ — порядок оплаты работ',
                'recommendation': 'Требовать обеспечение аванса (банковская гарантия)',
                'proposed_text': 'Аванс выплачивается при условии предоставления банковской гарантии на сумму аванса.',
                'description': 'Аванс без обеспечения создаёт финансовые риски'
            },
            {
                'name': 'Нет претензионного порядка',
                'keywords': ['претензия', 'досудебный', 'споры'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.LOW,
                'legal_basis': 'Статья 4 АПК РФ — обязательный досудебный порядок',
                'recommendation': 'Добавить обязательный претензионный порядок',
                'proposed_text': 'Все споры урегулируются в досудебном порядке. Претензия рассматривается в течение 30 дней.',
                'description': 'Отсутствие претензионного порядка усложняет разрешение споров'
            },
            {
                'name': 'Неопределённый предмет договора',
                'keywords': ['предмет', 'объект', 'работы'],
                'pattern': None,
                'check_missing': True,
                'risk_level': RiskLevel.CRITICAL,
                'legal_basis': 'Статья 432 ГК РФ — существенные условия договора',
                'recommendation': 'Чётко определить предмет договора',
                'proposed_text': 'Предмет договора: выполнение работ по объекту [адрес], виды работ: [перечень].',
                'description': 'Неопределённый предмет делает договор незаключённым'
            }
        ]
    
    def analyze_contract(self, contract_text: str) -> List[ContractRisk]:
        """Анализ договора на риски"""
        import re
        
        risks = []
        text_lower = contract_text.lower()
        
        for pattern in self.risk_patterns:
            risk_found = False
            
            # Поиск по ключевым словам
            if pattern.get('keywords'):
                for keyword in pattern['keywords']:
                    if keyword.lower() in text_lower:
                        risk_found = True
                        break
            
            # Поиск по regex паттерну
            if pattern.get('pattern') and risk_found:
                match = re.search(pattern['pattern'], contract_text, re.IGNORECASE)
                if match:
                    risk_found = True
            
            # Проверка на отсутствие раздела
            if pattern.get('check_missing'):
                # Если раздел не найден — это риск
                if not any(kw in text_lower for kw in pattern['keywords'][:2]):
                    risk_found = True
            
            if risk_found:
                risks.append(ContractRisk(
                    title=pattern['name'],
                    description=pattern['description'],
                    legal_basis=pattern['legal_basis'],
                    recommendation=pattern['recommendation'],
                    proposed_text=pattern.get('proposed_text', ''),
                    risk_level=pattern['risk_level']
                ))
        
        # Сортировка по уровню риска
        risks.sort(key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.risk_level.value), reverse=True)
        
        return risks
    
    def calculate_risk_score(self, risks: List[ContractRisk]) -> int:
        """Расчёт общего уровня риска (0-10)"""
        if not risks:
            return 0
        
        scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 5,
            RiskLevel.CRITICAL: 8
        }
        
        total = sum(scores[r.risk_level] for r in risks)
        score = min(10, total // 2)
        
        return score
    
    def get_conclusion(self, risks: List[ContractRisk]) -> str:
        """Получение заключения по договору"""
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
    """Создание анализатора рисков"""
    return RiskAnalyzer()
