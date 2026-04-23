"""
Document Parser - PDF, DOCX, TXT
"""
import logging
import re
from pathlib import Path
import pypdf
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self):
        self.supported = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}
    
    def parse_file(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf': return self._parse_pdf(file_path)
        elif ext in ['.docx', '.doc']: return self._parse_docx(file_path)
        elif ext == '.txt': return self._parse_txt(file_path)
        return self._try_generic(file_path)
    
    def _parse_pdf(self, path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: text += t + "\n\n"
        except Exception as e:
            logger.error(f"PDF: {e}")
            try:
                with open(path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t: text += t + "\n"
            except Exception as e2:
                logger.error(f"PDF fallback: {e2}")
        return self._clean(text)
    
    def _parse_docx(self, path: str) -> str:
        try:
            doc = Document(path)
            return self._clean("\n\n".join([p.text for p in doc.paragraphs if p.text.strip()]))
        except Exception as e:
            logger.error(f"DOCX: {e}")
            return ""
    
    def _parse_txt(self, path: str) -> str:
        for enc in ['utf-8', 'cp1251', 'koi8-r', 'latin-1']:
            try:
                with open(path, 'r', encoding=enc, errors='replace') as f:
                    return f.read()
            except:
                pass
        return ""
    
    def _try_generic(self, path: str) -> str:
        try:
            with open(path, 'rb') as f:
                content = f.read()
            for enc in ['utf-8', 'cp1251', 'latin-1']:
                try:
                    text = content.decode(enc, errors='ignore')
                    cleaned = ''.join(c if ord(c) > 31 or c in '\n\r\t' else ' ' for c in text)
                    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
                    if len(cleaned.strip()) > 100: return cleaned.strip()
                except: pass
        except: pass
        return ""
    
    def _clean(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        return text.strip()

def create_parser() -> DocumentParser:
    return DocumentParser()
