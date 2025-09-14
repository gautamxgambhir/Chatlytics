from enum import Enum
from typing import Dict, List, Set
SUPPORTED_EXTENSIONS: Set[str] = {'.txt', '.json'}
MAX_FILE_SIZE: int = 16 * 1024 * 1024
TEMP_FILE_PREFIX: str = 'chatlytics_temp_'
SESSION_FILE_SUFFIX: str = '_data.json'
MIN_MESSAGES_FOR_ANALYSIS: int = 10
MAX_MESSAGES_FOR_AI: int = 1000
RESPONSE_TIME_THRESHOLD_MINUTES: int = 30
CONVERSATION_GAP_THRESHOLD_MINUTES: int = 30
LATE_NIGHT_START_HOUR: int = 0
LATE_NIGHT_END_HOUR: int = 4
DEFAULT_CHART_HEIGHT: int = 400
CHART_MARGINS: Dict[str, int] = {'t': 50, 'b': 50, 'l': 50, 'r': 50}
BRAND_COLORS: List[str] = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
MAX_CHART_ITEMS: int = 10
EXTENDED_STOP_WORDS: Set[str] = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
MIN_WORD_LENGTH: int = 2
MAX_TEXT_DISPLAY_LENGTH: int = 100
EMOJI_PATTERN: str = '[\\U0001F600-\\U0001F64F\\U0001F300-\\U0001F5FF\\U0001F680-\\U0001F6FF\\U0001F1E0-\\U0001F1FF\\U00002702-\\U000027B0\\U000024C2-\\U0001F251]+'
URL_PATTERN: str = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\\\(\\\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
WHATSAPP_TIMESTAMP_PATTERNS: List[str] = ['\\d{1,2}/\\d{1,2}/\\d{2,4},?\\s+\\d{1,2}:\\d{2}(?::\\d{2})?\\s*(?:AM|PM)?', '\\d{1,2}-\\d{1,2}-\\d{2,4},?\\s+\\d{1,2}:\\d{2}(?::\\d{2})?\\s*(?:AM|PM)?', '\\d{2,4}-\\d{1,2}-\\d{1,2},?\\s+\\d{1,2}:\\d{2}(?::\\d{2})?']
AI_REQUEST_TIMEOUT: int = 30
AI_MAX_RETRIES: int = 3
AI_RATE_LIMIT_DELAY: float = 1.0
SESSION_TIMEOUT_HOURS: int = 24
CACHE_MAX_SIZE: int = 100
AFFECTIONATE_WORDS: Set[str] = {'love', 'loved', 'loving', 'heart', 'hearts', 'romantic', 'romance', 'passion', 'passionate', 'intimate', 'intimacy', 'hugs', 'hug', 'kiss', 'kisses', 'kissing', 'tender', 'tenderness', 'gentle', 'gentleness', 'warm', 'warmth', 'comfort', 'comforting', 'sweet', 'sweeter', 'sweetest', 'cute', 'cuter', 'cutest', 'beautiful', 'gorgeous', 'darling', 'dear', 'honey', 'baby', 'babe', 'sweetheart', 'beloved', 'treasure', 'angel', 'prince', 'princess', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect', 'incredible', 'unbelievable', 'extraordinary', 'remarkable', 'precious', 'special', 'unique', 'irreplaceable', 'valuable', 'miss', 'missing', 'care', 'caring', 'adore', 'adoring', 'cherish', 'cherishing', 'fond', 'fondness', 'affection', 'affectionate', 'secure', 'security', 'trust', 'trusting', 'faithful', 'faithfulness', 'loyal', 'loyalty', 'devoted', 'devotion', 'commitment', 'together', 'forever', 'always', 'promise', 'promises', 'dream', 'dreams', 'hope', 'hopes', 'wish', 'wishes', 'blessed', 'blessing', 'grateful', 'gratitude', 'thankful', 'appreciate', 'appreciation', 'jaan', 'bro', 'bestie', 'dude', 'buddy', 'friend', 'mate', 'pal'}
CONVERSATION_STARTERS: List[str] = ['hey', 'hi', 'hello', 'hii', 'hiii', 'hiiii', 'hiiiii', 'yo', 'yoo', 'yooo', 'sup', 'whats up', "what's up", 'wassup', 'howdy', 'greetings', 'good morning', 'good afternoon', 'good evening', 'gm', 'gn', 'good night', 'goodnight']

class MessageType(Enum):
    USER = 'user'
    SYSTEM = 'system'
    MEDIA = 'media'
    DELETED = 'deleted'

class Platform(Enum):
    WHATSAPP = 'whatsapp'
    INSTAGRAM = 'instagram'
    GENERIC = 'generic'

class AnalysisType(Enum):
    BASIC = 'basic'
    DETAILED = 'detailed'
    AI_ENHANCED = 'ai_enhanced'

class ChartType(Enum):
    BAR = 'bar'
    LINE = 'line'
    PIE = 'pie'
    SCATTER = 'scatter'
    HEATMAP = 'heatmap'

class ExportFormat(Enum):
    JSON = 'json'
    CSV = 'csv'
    PDF = 'pdf'
    HTML = 'html'
ERROR_MESSAGES: Dict[str, str] = {'FILE_TOO_LARGE': 'File size exceeds maximum limit of 16MB.', 'INVALID_FILE_TYPE': 'Invalid file type. Please upload .txt or .json files.', 'EMPTY_FILE': 'The uploaded file is empty or contains no valid messages.', 'PARSE_ERROR': 'Could not parse the chat file. Please check the format.', 'INSUFFICIENT_DATA': f'Need at least {MIN_MESSAGES_FOR_ANALYSIS} messages for analysis.', 'SESSION_NOT_FOUND': 'Session data not found. Please upload a new file.', 'AI_SERVICE_ERROR': 'AI service temporarily unavailable. Using fallback analysis.', 'EXPORT_ERROR': 'Failed to generate export. Please try again.', 'NETWORK_ERROR': 'Network error occurred. Please check your connection.', 'RATE_LIMIT_ERROR': 'Too many requests. Please wait before trying again.'}
SUCCESS_MESSAGES: Dict[str, str] = {'UPLOAD_SUCCESS': 'File uploaded and processed successfully.', 'ANALYSIS_COMPLETE': 'Analysis completed successfully.', 'EXPORT_READY': 'Export generated successfully.', 'SESSION_CREATED': 'New analysis session created.', 'DATA_PROCESSED': 'Chat data processed and ready for analysis.'}