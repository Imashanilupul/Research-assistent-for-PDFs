from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata for uploaded document"""
    filename: str
    size: int
    upload_time: datetime
    pages: int


class SummarySections(BaseModel):
    """Summary with structured sections"""
    title: str
    authors: Optional[Union[str, list]] = None
    abstract: str
    problem_statement: str
    methodology: str
    key_results: str
    conclusion: str
    
    @field_validator('authors', mode='before')
    @classmethod
    def convert_authors_to_string(cls, v):
        """Convert authors list to comma-separated string if needed"""
        if isinstance(v, list):
            return ', '.join(str(author) for author in v)
        return v


class DocumentSummary(BaseModel):
    """Complete document summary response"""
    document_id: str
    metadata: DocumentMetadata
    summary: SummarySections
    full_text: Optional[str] = None


class UploadResponse(BaseModel):
    """Response after document upload"""
    success: bool
    document_id: str
    message: str
    summary: SummarySections
    metadata: DocumentMetadata
