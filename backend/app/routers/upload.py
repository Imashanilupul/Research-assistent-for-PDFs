from fastapi import APIRouter, UploadFile, File, HTTPException, status
from services.pdf_extractor import PDFExtractor
from services.llm_service import LLMService
from db.vector_store import vector_store
from models.upload_schema import UploadResponse, DocumentMetadata
from utils.logger import logger
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/upload", tags=["Upload"])

pdf_extractor = PDFExtractor()
llm_service = LLMService()


@router.post("/", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and generate a structured summary
    
    - **file**: PDF file to upload
    
    Returns:
    - Document ID
    - Generated summary with structured sections
    - File metadata
    """
    try:
        logger.info(f"Starting PDF upload: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Validate PDF
        if not pdf_extractor.validate_pdf(content, file.filename):
            logger.error(f"PDF validation failed: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file or file size exceeds limit"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Extract text from PDF
        extracted_text = pdf_extractor.extract_text(content)
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract text from PDF"
            )
        
        # Extract metadata
        metadata = pdf_extractor.extract_metadata(content, file.filename)
        
        logger.info(f"Generating summary for document: {document_id}")
        
        # Generate summary using LLM
        summary = await llm_service.generate_summary(extracted_text)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate summary"
            )
        
        # Create document metadata
        doc_metadata = DocumentMetadata(
            filename=file.filename,
            size=len(content),
            upload_time=datetime.now(),
            pages=metadata.get("pages", 0)
        )
        
        # Store in vector store
        vector_store.store_document(
            document_id=document_id,
            text=extracted_text,
            summary=summary.dict(),
            metadata=metadata
        )
        
        logger.info(f"Document successfully stored: {document_id}")
        
        return UploadResponse(
            success=True,
            document_id=document_id,
            message="PDF uploaded and summary generated successfully",
            summary=summary,
            metadata=doc_metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/documents")
async def list_documents():
    """
    Get list of all uploaded documents
    
    Returns:
    - List of documents with metadata
    """
    try:
        documents = vector_store.list_documents()
        logger.info(f"Listed {len(documents)} documents")
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.get("/document/{document_id}")
async def get_document(document_id: str):
    """
    Get a specific document with its summary
    
    - **document_id**: ID of the document to retrieve
    
    Returns:
    - Document text, summary, and metadata
    """
    try:
        document = vector_store.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {
            "success": True,
            "document": document
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the vector store
    
    - **document_id**: ID of the document to delete
    
    Returns:
    - Success status
    """
    try:
        success = vector_store.delete_document(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        logger.info(f"Document deleted: {document_id}")
        
        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
