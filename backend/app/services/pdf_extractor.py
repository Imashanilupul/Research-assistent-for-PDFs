from pypdf import PdfReader
from io import BytesIO
from utils.logger import logger
from typing import Optional
import os


class PDFExtractor:
    """Service to extract text and metadata from PDF files"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    def validate_pdf(self, file_content: bytes, filename: str) -> bool:
        """Validate if the file is a valid PDF"""
        try:
            if len(file_content) > self.max_file_size:
                logger.error(f"File size exceeds limit: {filename}")
                return False
            
            if not filename.lower().endswith('.pdf'):
                logger.error(f"File is not a PDF: {filename}")
                return False
            
            # Try to read PDF
            pdf_reader = PdfReader(BytesIO(file_content))
            if len(pdf_reader.pages) == 0:
                logger.error(f"PDF has no pages: {filename}")
                return False
            
            logger.info(f"PDF validation successful: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"PDF validation failed for {filename}: {str(e)}", exc_info=True)
            return False
    
    def extract_text(self, file_content: bytes) -> Optional[str]:
        """Extract all text from PDF"""
        try:
            pdf_reader = PdfReader(BytesIO(file_content))
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            logger.info(f"Successfully extracted text from {len(pdf_reader.pages)} pages")
            return text
        
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}", exc_info=True)
            return None
    
    def extract_metadata(self, file_content: bytes, filename: str) -> dict:
        """Extract PDF metadata"""
        try:
            pdf_reader = PdfReader(BytesIO(file_content))
            metadata = {
                "filename": filename,
                "pages": len(pdf_reader.pages),
                "size": len(file_content),
            }
            
            # Try to extract document metadata
            if pdf_reader.metadata:
                if "/Title" in pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata["/Title"]
                if "/Author" in pdf_reader.metadata:
                    metadata["author"] = pdf_reader.metadata["/Author"]
                if "/Subject" in pdf_reader.metadata:
                    metadata["subject"] = pdf_reader.metadata["/Subject"]
            
            logger.info(f"Metadata extracted: {metadata['pages']} pages")
            return metadata
        
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}", exc_info=True)
            return {"filename": filename, "size": len(file_content)}
    
    def extract_first_pages(self, file_content: bytes, num_pages: int = 5) -> str:
        """Extract text from first N pages"""
        try:
            pdf_reader = PdfReader(BytesIO(file_content))
            text = ""
            
            for page_num in range(min(num_pages, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            return text
        
        except Exception as e:
            logger.error(f"Failed to extract first pages: {str(e)}", exc_info=True)
            return ""
