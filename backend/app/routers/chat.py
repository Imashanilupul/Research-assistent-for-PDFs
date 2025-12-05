from fastapi import APIRouter, HTTPException, status
from models.chat_schema import ChatRequest, ChatResponse
from services.llm_service import LLMService
from db.vector_store import vector_store
from utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

llm_service = LLMService()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question about an uploaded PDF document
    
    - **document_id**: ID of the document to ask about
    - **question**: The question to ask
    - **conversation_history**: Optional previous messages for context
    
    Returns:
    - Answer to the question
    - Source references
    - Conversation ID
    """
    try:
        logger.info(f"Processing question for document: {request.document_id}")
        
        # Get document from vector store
        document = vector_store.get_document(request.document_id)
        if not document:
            logger.error(f"Document not found: {request.document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get document text for context
        document_text = document.get("text", "")
        
        # Prepare conversation history
        conversation_history = request.conversation_history or []
        
        # Get answer from LLM
        answer = await llm_service.answer_question(
            question=request.question,
            document_text=document_text,
            conversation_history=[msg.dict() for msg in conversation_history]
        )
        
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate answer"
            )
        
        # Store conversation in vector store
        vector_store.add_conversation_message(
            request.document_id,
            "user",
            request.question
        )
        vector_store.add_conversation_message(
            request.document_id,
            "assistant",
            answer
        )
        
        logger.info("Question answered successfully")
        
        return ChatResponse(
            success=True,
            question=request.question,
            answer=answer,
            sources=[request.document_id],
            conversation_id=request.document_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question answering failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.get("/conversation/{document_id}")
async def get_conversation(document_id: str):
    """
    Get conversation history for a document
    
    - **document_id**: ID of the document
    
    Returns:
    - List of all messages in the conversation
    """
    try:
        # Check if document exists
        document = vector_store.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get conversation history
        conversation = vector_store.get_conversation_history(document_id)
        logger.info(f"Retrieved conversation for document: {document_id}")
        
        return {
            "success": True,
            "document_id": document_id,
            "conversation": conversation,
            "message_count": len(conversation)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.delete("/conversation/{document_id}")
async def clear_conversation(document_id: str):
    """
    Clear conversation history for a document
    
    - **document_id**: ID of the document
    
    Returns:
    - Success status
    """
    try:
        # Check if document exists
        document = vector_store.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Clear conversation
        vector_store.conversations[document_id] = []
        logger.info(f"Conversation cleared for document: {document_id}")
        
        return {
            "success": True,
            "message": "Conversation cleared successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation"
        )


@router.get("/summary/{document_id}")
async def get_summary(document_id: str):
    """
    Get the generated summary for a document
    
    - **document_id**: ID of the document
    
    Returns:
    - Structured summary with all sections
    """
    try:
        summary = vector_store.get_document_summary(document_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summary not found for this document"
            )
        
        logger.info(f"Retrieved summary for document: {document_id}")
        
        return {
            "success": True,
            "document_id": document_id,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summary"
        )
