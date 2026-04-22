"""
Document Parser для ИИ-юриста СЗ Дело
Поддержка PDF, DOCX, TXT
"""
import os
import logging
from typing import Optional, List
from pathlib import Path

import pypdf
import pdfplumber
from docx import Document
from PIL import Image

logger = logging.getLogger(__name__)


class DocumentParser:
    """Парсинг документов различных форматов"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}
    
    def parse_file(self, file_path: str) -> str:
        """Парсинг файла в текст"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._parse_docx(file_path)
        elif ext == '.txt':
            return self._parse_txt(file_path)
        else:
            logger.warning(f"Unsupported format: {ext}")
            return self._parse_txt(file_path)
    
    def _parse_pdf(self, file_path: str) -> str:
        """Парсинг PDF файла"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    tables = page.extract_tables()
                    text += page_text + "\n\n"
                    for table in tables:
                        table_text = "\n".join([" | ".join(row) for row in table if row])
                        text += table_text + "\n\n"
            if not text.strip():
                with open(file_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            return f"Ошибка чтения PDF: {str(e)}"
    
    def _parse_docx(self, file_path: str) -> str:
        """Парсинг DOCX файла"""
        try:
            doc = Document(file_path)
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text for cell in row.cells]
                    text.append(" | ".join(row_text))
            return self._clean_text("\n\n".join(text))
        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            return f"Ошибка чтения DOCX: {str(e)}"
    
    def _parse_txt(self, file_path: str) -> str:
        """Парсинг TXT файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1251') as f:
                return f.read()
        except Exception as e:
            logger.error(f"TXT parsing error: {e}")
            return f"Ошибка чтения файла: {str(e)}"
    
    def _ocr_file(self, file_path: str) -> str:
        """OCR отключён на Streamlit Cloud"""
        logger.warning("OCR недоступен на Streamlit Cloud")
        return "OCR недоступен. Используйте текстовые PDF/DOCX."
    
    def _clean_text(self, text: str) -> str:
        """Очистка текста"""
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        return text.strip()
    
    def split_into_paragraphs(self, text: str, max_length: int = 2000) -> List[str]:
        """Разбиение текста на абзацы"""
        paragraphs = []
        current_para = ""
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if current_para:
                    paragraphs.append(current_para)
                    current_para = ""
                continue
            if len(current_para) + len(line) < max_length:
                current_para += line + "\n"
            else:
                if current_para:
                    paragraphs.append(current_para)
                current_para = line + "\n"
        if current_para:
            paragraphs.append(current_para)
        return paragraphs
    
    def extract_clauses(self, text: str) -> List[dict]:
        """Извлечение пунктов договора"""
        import re
        clauses = []
        pattern = r'(\d+\.?\d*\.?\d*\.)\s+(.*?)(?=\d+\.?\d*\.?\d*\.|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        for num, content in matches:
            clauses.append({'number': num.strip(), 'text': content.strip()})
        return clauses


def create_parser() -> DocumentParser:
    """Создание парсера документов"""
    return DocumentParser()
