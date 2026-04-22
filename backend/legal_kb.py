"""
Legal Knowledge Base для ИИ-юриста СЗ Дело
Поиск по Гарант, КонсультантПлюс и внутренней базе
"""
import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LegalKB:
    """База знаний: Гарант, Консультант, внутренняя БЗ"""
    
    def __init__(self, local_kb_path: str = "data/sz_delo_base"):
        self.local_kb_path = Path(local_kb_path)
        self._ensure_kb_dir()
    
    def _ensure_kb_dir(self):
        """Создание директории базы знаний"""
        self.local_kb_path.mkdir(parents=True, exist_ok=True)
    
    def search(self, query: str, sources: List[str] = None) -> str:
        """
        Поиск по базе знаний
        
        Args:
            query: Поисковый запрос
            sources: Источники ['garant', 'consultant', 'local']
            
        Returns:
            Текстовый контекст
        """
        if sources is None:
            sources = ['local']  # По умолчанию только локальная БЗ
        
        results = []
        
        if 'local' in sources:
            local_results = self._search_local(query)
            results.append(local_results)
        
        if 'garant' in sources:
            garant_results = self._search_garant(query)
            results.append(garant_results)
        
        if 'consultant' in sources:
            consultant_results = self._search_consultant(query)
            results.append(consultant_results)
        
        return "\n\n".join(results) if results else "Контекст не найден."
    
    def _search_local(self, query: str) -> str:
        """Поиск в локальной базе"""
        if not self.local_kb_path.exists():
            return "Локальная база знаний пуста."
        
        results = []
        query_lower = query.lower()
        
        for file in self.local_kb_path.glob("*.txt"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query_lower in content.lower():
                        results.append(f"📄 {file.name}:\n{content[:500]}...")
            except Exception as e:
                logger.error(f"Error reading {file}: {e}")
        
        if results:
            return "📚 Найдено во внутренней базе СЗ Дело:\n\n" + "\n\n".join(results)
        else:
            return "Во внутренней базе не найдено."
    
    def _search_garant(self, query: str) -> str:
        """Поиск на Гарант (парсинг)"""
        try:
            # Поиск по сайту Гарант
            url = f"https://www.garant.ru/search/?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлечение результатов (структура может меняться)
            results = []
            search_results = soup.find_all(['h3', 'h4', 'a'], limit=5)
            
            for result in search_results:
                text = result.get_text(strip=True)
                if text and len(text) > 10:
                    results.append(f"- {text}")
            
            if results:
                return "🔍 Гарант (первые результаты):\n" + "\n".join(results[:5])
            else:
                return "Гарант: результаты не найдены."
        
        except Exception as e:
            logger.error(f"Garant search error: {e}")
            return "Гарант: ошибка поиска (возможно недоступен)."
    
    def _search_consultant(self, query: str) -> str:
        """Поиск на КонсультантПлюс (парсинг)"""
        try:
            # Поиск по сайту Консультант
            url = f"http://www.consultant.ru/search/?s={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлечение результатов
            results = []
            search_results = soup.find_all(['h3', 'h4', 'a'], limit=5)
            
            for result in search_results:
                text = result.get_text(strip=True)
                if text and len(text) > 10:
                    results.append(f"- {text}")
            
            if results:
                return "🔍 КонсультантПлюс (первые результаты):\n" + "\n".join(results[:5])
            else:
                return "КонсультантПлюс: результаты не найдены."
        
        except Exception as e:
            logger.error(f"Consultant search error: {e}")
            return "КонсультантПлюс: ошибка поиска (возможно недоступен)."
    
    def add_document(self, filename: str, content: str):
        """Добавление документа в локальную базу"""
        filepath = self.local_kb_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Document added: {filepath}")
    
    def get_all_documents(self) -> List[str]:
        """Получение списка всех документов"""
        if not self.local_kb_path.exists():
            return []
        
        return [f.name for f in self.local_kb_path.glob("*.txt")]


# ============================================================================
# Фабрика
# ============================================================================

def create_legal_kb() -> LegalKB:
    """Создание базы знаний"""
    return LegalKB()
