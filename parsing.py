import re
import json
from datetime import datetime
from typing import List, Dict, Any


class ChatParser:
    def __init__(self):
        self.android_message_re = re.compile(
            r'^(?P<ts>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4},?\s+\d{1,2}:\d{2}(?:\s*[ap]\.?m\.?)?)\s*-\s*(?P<sender>[^:]+):\s*(?P<msg>.*)$',
            re.IGNORECASE
        )
        self.ios_message_re = re.compile(
            r'^\[(?P<ts>[^,\]]+,\s*\d{1,2}:\d{2}(?:[:\d\sAPMapm\.]*)?)\]\s*(?P<sender>[^:]+):\s*(?P<msg>.*)$',
            re.IGNORECASE
        )
        self.android_system_re = re.compile(
            r'^(?P<ts>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4},?\s+\d{1,2}:\d{2}(?:\s*[ap]\.?m\.?)?)\s*-\s*(?P<msg>.+)$',
            re.IGNORECASE
        )
        self.ios_system_re = re.compile(
            r'^\[(?P<ts>[^,\]]+,\s*\d{1,2}:\d{2}(?:[:\d\sAPMapm\.]*)?)\]\s*(?P<msg>.+)$',
            re.IGNORECASE
        )
        self.ig_text_re = re.compile(
            r'^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?)\s*-\s*(?P<sender>[^:]+):\s*(?P<msg>.*)$'
        )
        self.media_placeholders = {
            '<Media omitted>', '[Media omitted]', '[Image]', '[Video]',
            '[Audio]', '[Sticker]', '[Document]', '<attached>', '<Attachment>'
        }

    def parse_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        if filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._parse_instagram_json(json.load(f))
        with open(file_path, 'r', encoding='utf-8') as f:
            return self._parse_text_lines(f.readlines())

    def _parse_text_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        messages, buffer, current = [], [], None
        for line in lines:
            line = line.strip('\n\r')
            if not line:
                continue
            match_android = self.android_message_re.match(line)
            match_ios = self.ios_message_re.match(line)
            match_android_sys = self.android_system_re.match(line)
            match_ios_sys = self.ios_system_re.match(line)
            match_ig_text = self.ig_text_re.match(line)

            if match_android:
                if buffer and current:
                    current['message'] += '\n'.join(buffer)
                    messages.append(current)
                buffer = []
                ts = self._parse_timestamp(match_android.group('ts'))
                current = {
                    'timestamp': ts,
                    'sender': match_android.group('sender').strip(),
                    'message': match_android.group('msg').strip(),
                    'is_system': False
                }
            elif match_ios:
                if buffer and current:
                    current['message'] += '\n'.join(buffer)
                    messages.append(current)
                buffer = []
                ts = self._parse_timestamp(match_ios.group('ts'))
                current = {
                    'timestamp': ts,
                    'sender': match_ios.group('sender').strip(),
                    'message': match_ios.group('msg').strip(),
                    'is_system': False
                }
            elif match_android_sys:
                if buffer and current:
                    current['message'] += '\n'.join(buffer)
                    messages.append(current)
                buffer = []
                ts = self._parse_timestamp(match_android_sys.group('ts'))
                current = {
                    'timestamp': ts,
                    'sender': None,
                    'message': match_android_sys.group('msg').strip(),
                    'is_system': True
                }
            elif match_ios_sys:
                if buffer and current:
                    current['message'] += '\n'.join(buffer)
                    messages.append(current)
                buffer = []
                ts = self._parse_timestamp(match_ios_sys.group('ts'))
                current = {
                    'timestamp': ts,
                    'sender': None,
                    'message': match_ios_sys.group('msg').strip(),
                    'is_system': True
                }
            elif match_ig_text:
                if buffer and current:
                    current['message'] += '\n'.join(buffer)
                    messages.append(current)
                buffer = []
                ts = self._parse_timestamp(match_ig_text.group('ts'))
                current = {
                    'timestamp': ts,
                    'sender': match_ig_text.group('sender').strip(),
                    'message': match_ig_text.group('msg').strip(),
                    'is_system': False
                }
            else:
                if current:
                    buffer.append(line)
        if current:
            if buffer:
                current['message'] += '\n'.join(buffer)
            if current['message'] not in self.media_placeholders:
                messages.append(current)
        return messages

    def _parse_instagram_json(self, data: Any) -> List[Dict[str, Any]]:
        messages = []
        if isinstance(data, dict) and 'messages' in data:
            items = data['messages']
        elif isinstance(data, list):
            items = data
        else:
            return []
        for msg in items:
            ts = None
            if 'timestamp_ms' in msg:
                ts = datetime.fromtimestamp(msg['timestamp_ms'] / 1000)
            elif 'created_at' in msg:
                try:
                    ts = self._parse_timestamp(msg['created_at'])
                except Exception:
                    ts = None
            messages.append({
                'timestamp': ts,
                'sender': msg.get('sender_name') or msg.get('sender') or None,
                'message': msg.get('content') or msg.get('text') or '',
                'is_system': False
            })
        return messages

    def _parse_timestamp(self, ts: str) -> datetime:
        fmts = [
            "%d/%m/%Y, %I:%M %p", "%d/%m/%y, %I:%M %p", "%d/%m/%Y, %H:%M",
            "%d/%m/%y, %H:%M", "%d/%m/%y, %I:%M:%S %p", "%d/%m/%Y, %I:%M:%S %p",
            "%m/%d/%y, %I:%M %p", "%m/%d/%Y, %I:%M %p", "%d/%m/%y, %I:%M:%S %p",
            "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S%z"
        ]
        for fmt in fmts:
            try:
                return datetime.strptime(ts.strip(), fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(ts.strip())
        except Exception:
            return datetime.now()
