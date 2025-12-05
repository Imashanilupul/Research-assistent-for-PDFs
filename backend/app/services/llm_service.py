import google.generativeai as genai
from config import settings
from utils.logger import logger
from models.upload_schema import SummarySections
from typing import Optional
import json
import re


class LLMService:
    """Service for LLM interactions using Google Gemini"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_sessions = {}  # Store chat sessions by document_id
    
    async def generate_summary(self, text: str) -> Optional[SummarySections]:
        """Generate structured summary from document text"""
        try:
            prompt = f"""
            Analyze the following research paper text and generate a structured summary with these exact sections:
            
            TEXT:
            {text[:4000]}  # Limit to first 4000 chars for API limits
            
            Please provide the summary in JSON format with these fields:
            - title: The title of the paper (string)
            - authors: The authors of the paper as a SINGLE STRING with comma-separated names, e.g., "John Doe, Jane Smith" (NOT a list)
            - abstract: A brief abstract (2-3 sentences, string)
            - problem_statement: The main problem being addressed (2-3 sentences, string)
            - methodology: The research methodology (3-4 sentences, string)
            - key_results: The key findings/results (3-4 sentences, string)
            - conclusion: The conclusion and implications (2-3 sentences, string)
            
            IMPORTANT: 
            - authors MUST be a single STRING with comma-separated values, NOT a JSON array
            - All values must be strings
            - Return ONLY valid JSON without any markdown formatting or extra text.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Clean the response
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            # Parse JSON response
            summary_data = json.loads(response_text.strip())
            
            # Ensure all fields are strings
            summary_data = self._normalize_summary_data(summary_data)
            
            summary = SummarySections(
                title=summary_data.get("title", "Unknown Title"),
                authors=summary_data.get("authors", "Unknown Authors"),
                abstract=summary_data.get("abstract", ""),
                problem_statement=summary_data.get("problem_statement", ""),
                methodology=summary_data.get("methodology", ""),
                key_results=summary_data.get("key_results", ""),
                conclusion=summary_data.get("conclusion", "")
            )
            
            logger.info("Summary generated successfully")
            return summary
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            return self._generate_fallback_summary(text)
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
            return self._generate_fallback_summary(text)
    
    def _normalize_summary_data(self, data: dict) -> dict:
        """Normalize summary data to ensure all values are strings"""
        normalized = {}
        for key, value in data.items():
            if isinstance(value, list):
                # Convert list to comma-separated string
                normalized[key] = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                # Convert dict to string representation
                normalized[key] = str(value)
            else:
                # Keep as is if already string or None
                normalized[key] = value if isinstance(value, str) else str(value) if value else ""
        return normalized
    
    async def answer_question(self, question: str, document_text: str, 
                             conversation_history: Optional[list] = None) -> Optional[str]:
        """Answer a question about the document using RAG"""
        try:
            # Build context with conversation history
            context = f"Document Content:\n{document_text[:3000]}\n\n"
            
            if conversation_history:
                context += "Previous conversation:\n"
                for msg in conversation_history[-3:]:  # Include last 3 messages
                    context += f"{msg['role']}: {msg['content']}\n"
            
            prompt = f"""
            You are an expert research assistant. Based on the provided document and conversation history,
            answer the following question accurately and concisely.
            
            {context}
            
            Question: {question}
            
            Provide a clear, accurate answer based on the document content. If the answer is not in the document,
            say "This information is not available in the provided document."
            """
            
            response = self.model.generate_content(prompt)
            answer = response.text
            
            logger.info("Question answered successfully")
            return answer
        
        except Exception as e:
            logger.error(f"Question answering failed: {str(e)}", exc_info=True)
            return None
    
    def _generate_fallback_summary(self, text: str) -> SummarySections:
        """Generate a basic fallback summary when LLM parsing fails"""
        lines = text.split('\n')
        title = lines[0] if lines else "Research Paper"
        
        return SummarySections(
            title=title,
            authors="Authors not extracted",
            abstract="Unable to generate abstract automatically. Please review the document.",
            problem_statement="Unable to extract problem statement. Please review the document.",
            methodology="Unable to extract methodology. Please review the document.",
            key_results="Unable to extract key results. Please review the document.",
            conclusion="Unable to extract conclusion. Please review the document."
        )
