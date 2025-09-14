import json
import logging
import re
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

def handle_errors(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'Error in {func.__name__}: {str(e)}')
            logger.error(traceback.format_exc())
            return None
    return wrapper

def validate_messages(messages: List[Dict[str, Any]]) -> bool:
    if not messages:
        return False
    required_fields = ['timestamp', 'sender', 'message']
    for msg in messages:
        if not all((field in msg for field in required_fields)):
            return False
        if not isinstance(msg['message'], str) or not msg['message'].strip():
            return False
    return True

def safe_json_serialize(obj: Any) -> str:
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f'JSON serialization error: {e}')
        return json.dumps({'error': 'Serialization failed'})

def format_duration(days: int) -> str:
    if days < 1:
        return 'Less than a day'
    elif days < 7:
        return f'{days} day{('s' if days > 1 else '')}'
    elif days < 30:
        weeks = days // 7
        return f'{weeks} week{('s' if weeks > 1 else '')}'
    elif days < 365:
        months = days // 30
        return f'{months} month{('s' if months > 1 else '')}'
    else:
        years = days // 365
        return f'{years} year{('s' if years > 1 else '')}'

def get_color_for_sender(sender: str, color_palette: List[str]) -> str:
    hash_value = hash(sender) % len(color_palette)
    return color_palette[hash_value]

def truncate_text(text: str, max_length: int=100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'

def calculate_percentage(value: float, total: float) -> float:
    if total == 0:
        return 0.0
    return round(value / total * 100, 1)

def format_time_duration(seconds: float) -> str:
    if seconds < 60:
        return f'{seconds:.0f}s'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{minutes:.1f}m'
    else:
        hours = seconds / 3600
        return f'{hours:.1f}h'

def clean_filename(filename: str) -> str:
    import re
    filename = re.sub('[<>:"/\\\\|?*]', '_', filename)
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    return filename

class AnalyticsCache:

    def __init__(self, max_size: int=100):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        if len(self.cache) >= self.max_size:
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[lru_key]
            del self.access_times[lru_key]
        self.cache[key] = value
        self.access_times[key] = datetime.now()

    def clear(self) -> None:
        self.cache.clear()
        self.access_times.clear()
analytics_cache = AnalyticsCache()