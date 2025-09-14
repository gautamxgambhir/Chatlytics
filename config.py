import os
from typing import Dict, List, Set
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY: str = os.environ.get('SECRET_KEY')
    DEBUG: bool = os.environ.get('FLASK_ENV') == 'development'
    UPLOAD_FOLDER: str = 'uploads'
    ALLOWED_EXTENSIONS: Set[str] = {'txt', 'json'}
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024
    OPENROUTER_API_KEY: str = os.environ.get('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL: str = 'https://openrouter.ai/api/v1'
    MIN_MESSAGES_FOR_ANALYSIS: int = 10
    MAX_MESSAGES_FOR_AI_ANALYSIS: int = 1000
    RESPONSE_TIME_THRESHOLD_MINUTES: int = 30
    CONVERSATION_GAP_THRESHOLD_MINUTES: int = 30
    CHART_HEIGHT: int = 400
    CHART_MARGIN: Dict[str, int] = {'t': 50, 'b': 50, 'l': 50, 'r': 50}
    COLOR_PALETTE: List[str] = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
    AI_MODEL: str = os.environ.get('AI_MODEL', 'deepseek/deepseek-chat-v3.1:free')
    AI_MAX_TOKENS: int = int(os.environ.get('AI_MAX_TOKENS', '500'))
    AI_TEMPERATURE: float = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    AI_REQUEST_TIMEOUT: int = 30
    SESSION_TIMEOUT_HOURS: int = 24
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'