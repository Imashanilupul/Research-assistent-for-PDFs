from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    
    
settings = Settings()


