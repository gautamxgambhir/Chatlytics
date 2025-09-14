import os
import secrets
from typing import Dict, List, Set
from dotenv import load_dotenv

load_dotenv()

class Config:    
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    DEBUG: bool = os.environ.get('FLASK_ENV', 'production').lower() == 'development'
    ENV: str = os.environ.get('FLASK_ENV', 'production')
    
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS: Set[str] = {'txt', 'json'}
    MAX_CONTENT_LENGTH: int = int(os.environ.get('MAX_CONTENT_LENGTH', str(16 * 1024 * 1024)))  # 16MB
    
    
    # AI functionality removed for Vercel optimization
    
    MIN_MESSAGES_FOR_ANALYSIS: int = int(os.environ.get('MIN_MESSAGES_FOR_ANALYSIS', '10'))
    RESPONSE_TIME_THRESHOLD_MINUTES: int = int(os.environ.get('RESPONSE_TIME_THRESHOLD_MINUTES', '30'))
    CONVERSATION_GAP_THRESHOLD_MINUTES: int = int(os.environ.get('CONVERSATION_GAP_THRESHOLD_MINUTES', '30'))
    
    CHART_HEIGHT: int = int(os.environ.get('CHART_HEIGHT', '400'))
    CHART_MARGIN: Dict[str, int] = {'t': 50, 'b': 50, 'l': 50, 'r': 50}
    COLOR_PALETTE: List[str] = [
        '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
        '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
    ]
    
    SESSION_TIMEOUT_HOURS: int = int(os.environ.get('SESSION_TIMEOUT_HOURS', '24'))
    
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    PORT: int = int(os.environ.get('PORT', '5001'))
    HOST: str = os.environ.get('HOST', '0.0.0.0' if ENV == 'production' else '127.0.0.1')
    
    @staticmethod
    def validate_config() -> List[str]:
        errors = []
        
        if not Config.SECRET_KEY:
            errors.append('SECRET_KEY is required')
            
        return errors
        
    @classmethod
    def is_production(cls) -> bool:
        return cls.ENV.lower() == 'production'
