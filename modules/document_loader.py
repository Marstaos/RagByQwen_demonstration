import os
import pypdf
import docx2txt
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
    
    def load_document(self, file_path):
        """加载文档并返回文本内容"""
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == '.pdf':
            return self._load_pdf(file_path)
        elif ext.lower() == '.txt':
            return self._load_text(file_path)
        elif ext.lower() in ['.docx', '.doc']:
            return self._load_word(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
    
    def _load_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _load_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _load_word(self, file_path):
        return docx2txt.process(file_path)
    
    def split_text(self, text):
        """将文本分割成小块"""
        return self.text_splitter.split_text(text)