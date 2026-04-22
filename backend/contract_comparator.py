"""
Contract Comparator для ИИ-юриста СЗ Дело
Сравнение двух версий договора с подсветкой отличий
"""
import os
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from docx import Document
import difflib

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class ClauseChange:
    """Изменение в пункте договора"""
    clause_number: str
    change_type: ChangeType
    old_text: str = ""
    new_text: str = ""
    legal_impact: str = ""
    recommendation: str = ""
    risk_level: str = "medium"  # low, medium, high, critical


class ContractComparator:
    """Сравнение версий договоров"""
    
    def __init__(self):
        pass
    
    def compare_files(self, file1_path: str, file2_path: str) -> List[ClauseChange]:
        """
        Сравнение двух файлов договоров
        
        Args:
            file1_path: Путь к первой версии
            file2_path: Путь ко второй версии
            
        Returns:
            Список изменений
        """
        # Извлечение текста
        text1 = self._extract_text(file1_path)
        text2 = self._extract_text(file2_path)
        
        # Разбиение на пункты
        clauses1 = self._split_into_clauses(text1)
        clauses2 = self._split_into_clauses(text2)
        
        # Сравнение
        changes = self._compare_clauses(clauses1, clauses2)
        
        return changes
    
    def _extract_text(self, file_path: str) -> str:
        """Извлечение текста из файла"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.docx':
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == '.pdf':
            from backend.document_parser import create_parser
            parser = create_parser()
            return parser.parse_file(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.warning(f"Unsupported format: {ext}")
            return ""
    
    def _split_into_clauses(self, text: str) -> Dict[str, str]:
        """
        Разбиение текста на пункты
        
        Returns:
            dict: {номер_пункта: текст}
        """
        import re
        
        clauses = {}
        current_clause = None
        current_text = []
        
        # Поиск пунктов по номерам
        pattern = r'^(\d+(?:\.\d+)*)\.\s*(.*)$'
        
        for line in text.split('\n'):
            match = re.match(pattern, line.strip())
            
            if match:
                # Сохранение предыдущего пункта
                if current_clause:
                    clauses[current_clause] = "\n".join(current_text)
                
                # Новый пункт
                current_clause = match.group(1)
                current_text = [match.group(2)]
            else:
                # Продолжение текущего пункта
                if current_clause and line.strip():
                    current_text.append(line)
        
        # Сохранение последнего пункта
        if current_clause:
            clauses[current_clause] = "\n".join(current_text)
        
        return clauses
    
    def _compare_clauses(self, 
                        clauses1: Dict[str, str], 
                        clauses2: Dict[str, str]) -> List[ClauseChange]:
        """Сравнение пунктов двух договоров"""
        changes = []
        
        all_clause_numbers = set(clauses1.keys()) | set(clauses2.keys())
        
        for clause_num in sorted(all_clause_numbers, key=lambda x: [int(p) if p.isdigit() else p for p in x.split('.')]):
            text1 = clauses1.get(clause_num, "")
            text2 = clauses2.get(clause_num, "")
            
            if not text1 and text2:
                # Добавлен новый пункт
                changes.append(ClauseChange(
                    clause_number=clause_num,
                    change_type=ChangeType.ADDED,
                    new_text=text2,
                    legal_impact="Добавлен новый пункт, требует анализа на соответствие интересам СЗ Дело",
                    recommendation="Проверить新增条款是否可接受"
                ))
            
            elif text1 and not text2:
                # Удалён пункт
                changes.append(ClauseChange(
                    clause_number=clause_num,
                    change_type=ChangeType.REMOVED,
                    old_text=text1,
                    legal_impact="Удалён пункт из договора",
                    recommendation="Проверить, не было ли удалено важное условие"
                ))
            
            elif text1 != text2:
                # Изменён пункт
                changes.append(ClauseChange(
                    clause_number=clause_num,
                    change_type=ChangeType.MODIFIED,
                    old_text=text1,
                    new_text=text2,
                    legal_impact="Изменены условия пункта",
                    recommendation="Сравнить редакции и оценить риски"
                ))
        
        return changes
    
    def generate_diff_html(self, text1: str, text2: str) -> str:
        """
        Генерация HTML diff с подсветкой
        
        Args:
            text1: Текст первой версии
            text2: Текст второй версии
            
        Returns:
            HTML с подсветкой отличий
        """
        # Разбиение на строки
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # Создание diff
        diff = difflib.unified_diff(lines1, lines2, lineterm='')
        
        # Генерация HTML
        html = ['<div class="diff-container" style="font-family: monospace; font-size: 12px;">']
        
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('-'):
                html.append(f'<div style="background-color: #ffebee; color: #c62828; padding: 2px;">{line}</div>')
            elif line.startswith('+'):
                html.append(f'<div style="background-color: #e8f5e9; color: #2e7d32; padding: 2px;">{line}</div>')
            elif line.startswith('@@'):
                html.append(f'<div style="background-color: #e3f2fd; color: #1565c0; padding: 2px; font-weight: bold;">{line}</div>')
            else:
                html.append(f'<div style="padding: 2px;">{line}</div>')
        
        html.append('</div>')
        
        return "\n".join(html)
    
    def analyze_legal_impact(self, changes: List[ClauseChange]) -> str:
        """
        Анализ юридических последствий изменений
        
        Args:
            changes: Список изменений
            
        Returns:
            Текст анализа
        """
        if not changes:
            return "Изменений не обнаружено."
        
        analysis = []
        
        # Критические изменения
        critical = [c for c in changes if c.risk_level == 'critical']
        high = [c for c in changes if c.risk_level == 'high']
        
        if critical:
            analysis.append("## 🔴 КРИТИЧЕСКИЕ ИЗМЕНЕНИЯ")
            for change in critical:
                analysis.append(f"- Пункт {change.clause_number}: {change.legal_impact}")
        
        if high:
            analysis.append("\n## 🟠 ВЫСОКИЕ РИСКИ")
            for change in high:
                analysis.append(f"- Пункт {change.clause_number}: {change.legal_impact}")
        
        # Общие рекомендации
        analysis.append("\n## 📋 ОБЩИЕ РЕКОМЕНДАЦИИ")
        analysis.append("1. Проверить все изменённые пункты на соответствие интересам СЗ Дело")
        analysis.append("2. Убедиться, что не удалены важные гарантийные положения")
        analysis.append("3. Проверить изменённые условия оплаты и сроков")
        
        return "\n".join(analysis)
    
    def compare_and_explain(self, 
                           file1_path: str, 
                           file2_path: str,
                           llm_engine=None) -> Dict:
        """
        Полное сравнение с объяснением от LLM
        
        Args:
            file1_path: Первая версия
            file2_path: Вторая версия
            llm_engine: LLM движок для объяснений
            
        Returns:
            dict с результатами
        """
        # Сравнение
        changes = self.compare_files(file1_path, file2_path)
        
        # HTML diff
        text1 = self._extract_text(file1_path)
        text2 = self._extract_text(file2_path)
        diff_html = self.generate_diff_html(text1, text2)
        
        # Юридический анализ
        legal_analysis = self.analyze_legal_impact(changes)
        
        # LLM объяснение (если доступно)
        llm_explanation = ""
        if llm_engine:
            prompt = f"""
Проанализируй изменения в договоре и объясни юридические последствия:

{legal_analysis}

Список изменений:
{chr(10).join([f"- {c.clause_number}: {c.change_type.value}" for c in changes])}

Дай рекомендации для строительной компании СЗ Дело (Москва/МО):
"""
            from backend.llm_engine import Message
            response = llm_engine.generate(prompt)
            llm_explanation = response.text
        
        return {
            'changes': changes,
            'diff_html': diff_html,
            'legal_analysis': legal_analysis,
            'llm_explanation': llm_explanation,
            'total_changes': len(changes)
        }


# ============================================================================
# Фабрика
# ============================================================================

def create_comparator() -> ContractComparator:
    """Создание компаратора договоров"""
    return ContractComparator()
