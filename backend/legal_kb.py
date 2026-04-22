"""
База знаний - реальные источники КонсультантПлюс
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

LEGAL_SOURCES = {
    "гк рф": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/", "name": "ГК РФ", "source": "КонсультантПлюс"},
    "ст 702": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article702/", "name": "Ст. 702 ГК РФ - Договор подряда", "source": "КонсультантПлюс"},
    "ст 709": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article709/", "name": "Ст. 709 ГК РФ - Цена", "source": "КонсультантПлюс"},
    "ст 715": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article715/", "name": "Ст. 715 ГК РФ - Права заказчика", "source": "КонсультантПлюс"},
    "ст 717": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article717/", "name": "Ст. 717 ГК РФ - Отказ", "source": "КонсультантПлюс"},
    "ст 719": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article719/", "name": "Ст. 719 ГК РФ", "source": "КонсультантПлюс"},
    "ст 720": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article720/", "name": "Ст. 720 ГК РФ - Приёмка", "source": "КонсультантПлюс"},
    "ст 721": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article721/", "name": "Ст. 721 ГК РФ - Качество", "source": "КонсультантПлюс"},
    "ст 722": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article722/", "name": "Ст. 722 ГК РФ - Гарантии", "source": "КонсультантПлюс"},
    "ст 723": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article723/", "name": "Ст. 723 ГК РФ - Ответственность", "source": "КонсультантПлюс"},
    "ст 724": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article724/", "name": "Ст. 724 ГК РФ - Сроки", "source": "КонсультантПлюс"},
    "ст 725": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article725/", "name": "Ст. 725 ГК РФ - Давность", "source": "КонсультантПлюс"},
    "ст 330": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article330/", "name": "Ст. 330 ГК РФ - Неустойка", "source": "КонсультантПлюс"},
    "ст 333": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article333/", "name": "Ст. 333 ГК РФ - Уменьшение", "source": "КонсультантПлюс"},
    "ст 401": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article401/", "name": "Ст. 401 ГК РФ - Ответственность", "source": "КонсультантПлюс"},
    "ст 450": {"url": "https://www.consultant.ru/document/cons_doc_LAW_64629/Article450/", "name": "Ст. 450 ГК РФ - Расторжение", "source": "КонсультантПлюс"},
    "214 фз": {"url": "https://www.consultant.ru/document/cons_doc_LAW_168569/", "name": "214-ФЗ Долевое участие", "source": "КонсультантПлюс"},
    "44 фз": {"url": "https://www.consultant.ru/document/cons_doc_LAW_107961/", "name": "44-ФЗ Контракты", "source": "КонсультантПлюс"},
    "гск": {"url": "https://www.consultant.ru/document/cons_doc_LAW_51057/", "name": "Градостроительный кодекс", "source": "КонсультантПлюс"},
    "пленум вас 22": {"url": "https://www.consultant.ru/document/cons_doc_LAW_114400/", "name": "ПП ВАС №22 - Неустойка", "source": "КонсультантПлюс"},
    "пленум вас 54": {"url": "https://www.consultant.ru/document/cons_doc_LAW_132417/", "name": "ПП ВАС №54 - Подряд", "source": "КонсультантПлюс"},
    "апк": {"url": "https://www.consultant.ru/document/cons_doc_LAW_37875/", "name": "АПК РФ", "source": "КонсультантПлюс"},
}

class LegalKnowledgeBase:
    def __init__(self, data_dir: str = "data/sz_delo_base"):
        self.data_dir = data_dir
        self.documents = []
    
    def search(self, query: str) -> str:
        context = ["## РЕЛЕВАНТНЫЕ ИСТОЧНИКИ:"]
        q = query.lower()
        for kw, src in LEGAL_SOURCES.items():
            if kw in q:
                context.append(f"- [{src['name']}]({src['url']})")
        if len(context) == 1:
            context.append("- [ГК РФ](https://www.consultant.ru/document/cons_doc_LAW_64629/)")
            context.append("- [Ст. 702 ГК РФ](https://www.consultant.ru/document/cons_doc_LAW_64629/Article702/)")
        return "\n".join(context)
    
    def find_sources(self, query: str) -> List[Dict]:
        q = query.lower()
        sources = []
        for kw, src in LEGAL_SOURCES.items():
            if kw in q:
                sources.append(src)
        if not sources:
            sources = [LEGAL_SOURCES.get("гк рф"), LEGAL_SOURCES.get("ст 702"), LEGAL_SOURCES.get("ст 723")]
        return [s for s in sources if s]

def create_legal_kb(data_dir: str = "data/sz_delo_base") -> LegalKnowledgeBase:
    return LegalKnowledgeBase(data_dir)
