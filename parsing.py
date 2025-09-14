import re
import json
from datetime import datetime
from typing import List, Dict, Any

class ChatParser:

    def __init__(self):
        self.whatsapp_patterns = {
            'message': re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?:\s+[ap]m)?)\s*-\s*([^:]+):\s*(.*)$', re.MULTILINE | re.IGNORECASE),
            'system_message': re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?:\s+[ap]m)?)\s*-\s*(.*)$', re.MULTILINE | re.IGNORECASE)
        }
        self.instagram_patterns = {
            'message': re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*?)\s*-\s*([^:]+):\s*(.*)$', re.MULTILINE)
        }

    def parse_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        file_extension = filename.lower().split('.')[-1]
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        if file_extension == 'txt':
            return self._parse_whatsapp(content)
        elif file_extension == 'json':
            return self._parse_instagram(content)
        else:
            raise ValueError(f'Unsupported file format: {file_extension}')

    def _parse_whatsapp(self, content: str) -> List[Dict[str, Any]]:
        messages = []
        lines = content.split('\n')
        current_message = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = self.whatsapp_patterns['message'].match(line)
            if match:
                if current_message:
                    messages.append(current_message)
                timestamp_str, sender, message_text = match.groups()
                timestamp = self._parse_whatsapp_timestamp(timestamp_str)
                current_message = {'timestamp': timestamp, 'sender': sender.strip(), 'message': message_text.strip(), 'is_system': False}
            else:
                sys_match = self.whatsapp_patterns['system_message'].match(line)
                if sys_match:
                    if current_message:
                        messages.append(current_message)
                    timestamp_str, message_text = sys_match.groups()
                    timestamp = self._parse_whatsapp_timestamp(timestamp_str)
                    current_message = {'timestamp': timestamp, 'sender': 'System', 'message': message_text.strip(), 'is_system': True}
                elif current_message and (not current_message['is_system']):
                    current_message['message'] += ' ' + line
        if current_message:
            messages.append(current_message)
        return self._clean_messages(messages)

    def _parse_instagram(self, content: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
            messages = []
            if 'messages' in data:
                message_list = data['messages']
            elif isinstance(data, list):
                message_list = data
            else:
                message_list = []
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict):
                        if 'sender_name' in value[0] or 'from' in value[0]:
                            message_list = value
                            break
            for msg in message_list:
                if not isinstance(msg, dict):
                    continue
                timestamp = self._parse_instagram_timestamp(msg.get('timestamp_ms', msg.get('timestamp', '')))
                sender = msg.get('sender_name', msg.get('from', 'Unknown'))
                message_text = msg.get('content', msg.get('text', ''))
                if message_text and sender != 'Unknown':
                    messages.append({'timestamp': timestamp, 'sender': sender, 'message': message_text, 'is_system': False})
            return self._clean_messages(messages)
        except json.JSONDecodeError:
            return self._parse_instagram_text(content)

    def _parse_instagram_text(self, content: str) -> List[Dict[str, Any]]:
        messages = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = self.instagram_patterns['message'].match(line)
            if match:
                timestamp_str, sender, message_text = match.groups()
                timestamp = self._parse_instagram_timestamp(timestamp_str)
                messages.append({'timestamp': timestamp, 'sender': sender.strip(), 'message': message_text.strip(), 'is_system': False})
        return self._clean_messages(messages)

    def _parse_whatsapp_timestamp(self, timestamp_str: str) -> datetime:
        formats = ['%d/%m/%Y, %I:%M %p', '%d/%m/%y, %I:%M %p', '%d/%m/%Y, %H:%M', '%d/%m/%y, %H:%M', '%m/%d/%y, %I:%M %p', '%m/%d/%Y, %I:%M %p', '%m/%d/%y, %H:%M', '%m/%d/%Y, %H:%M']
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    def _parse_instagram_timestamp(self, timestamp_str: str) -> datetime:
        if isinstance(timestamp_str, (int, float)):
            return datetime.fromtimestamp(timestamp_str / 1000)
        formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    def _clean_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for msg in messages:
            if msg['is_system']:
                continue
            message_text = msg['message']
            media_placeholders = ['<Media omitted>', '<Media omitted>', '[Media]', '[Sticker]', '[Image]', '[Video]', '[Audio]', '[File]', '[GIF]', '[Voice Message]', '[Document]']
            if any((placeholder in message_text for placeholder in media_placeholders)):
                continue
            if not message_text.strip():
                continue
            sender = msg['sender'].strip()
            if not sender or sender == 'Unknown':
                continue
            cleaned.append({'timestamp': msg['timestamp'], 'sender': sender, 'message': message_text.strip(), 'is_system': False})
        return cleaned