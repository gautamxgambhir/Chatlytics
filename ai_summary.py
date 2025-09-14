import requests
import json
import re
import os
from typing import List, Dict, Any
from config import Config

class AISummaryGenerator:

    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.AI_MODEL
        if not self.api_key:
            print('Warning: OPENROUTER_API_KEY not found in environment variables. AI features will use fallback content.')

    def test_api_connection(self) -> bool:
        if not self.api_key:
            print('API test failed: No API key configured')
            return False
        try:
            test_response = self._call_openrouter_api("Hello, just testing the connection. Please respond with 'API working'.", max_tokens=50)
            print(f'API Test Response: {test_response}')
            return True
        except Exception as e:
            print(f'API test failed: {e}')
            return False

    def generate_insights(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {'error': 'No messages to analyze'}
        try:
            chat_summary = self._prepare_chat_summary(messages)
            api_working = self.test_api_connection()
            if not api_working:
                print('API connection failed, using fallback content immediately.')
                raise Exception('API connection test failed')
            try:
                print('API connection successful! Generating all AI insights in one call...')
                all_insights = self._generate_all_insights_at_once(chat_summary)
                print('✓ All AI insights generated successfully!')
                return all_insights
            except Exception as ai_error:
                print(f'AI generation failed, using fallback content: {ai_error}')
                print('Note: This might be due to API limits or network issues. Using static fallback content.')
                personality_analysis = self._generate_fallback_personality_analysis(chat_summary)
                relationship_dynamics = self._generate_fallback_relationship_dynamics(chat_summary)
                conversation_style = self._generate_fallback_conversation_style(chat_summary)
                fun_facts = self._generate_fallback_fun_facts(chat_summary)
                overall_summary = self._generate_fallback_overall_summary(chat_summary)
                return {'personality_analysis': personality_analysis, 'relationship_dynamics': relationship_dynamics, 'conversation_style': conversation_style, 'fun_facts': fun_facts, 'overall_summary': overall_summary}
        except Exception as e:
            return {'error': f'Failed to generate AI insights: {str(e)}'}

    def _prepare_chat_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        senders = list(set((msg['sender'] for msg in messages)))
        sample_messages = messages[::max(1, len(messages) // 50)]
        message_lengths = [len(msg['message'].split()) for msg in messages]
        avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        hours = [msg['timestamp'].hour for msg in messages]
        most_active_hour = max(set(hours), key=hours.count) if hours else 12
        sender_counts = {}
        for sender in senders:
            sender_counts[sender] = sum((1 for msg in messages if msg['sender'] == sender))
        start_date = min((msg['timestamp'] for msg in messages))
        end_date = max((msg['timestamp'] for msg in messages))
        duration_days = (end_date - start_date).days + 1
        return {'senders': senders, 'total_messages': len(messages), 'sample_messages': sample_messages[:20], 'avg_message_length': avg_message_length, 'most_active_hour': most_active_hour, 'sender_counts': sender_counts, 'date_range': {'start': start_date.strftime('%Y-%m-%d'), 'end': end_date.strftime('%Y-%m-%d'), 'duration_days': duration_days}}

    def _call_openrouter_api(self, prompt: str, max_tokens: int=500) -> str:
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json', 'HTTP-Referer': 'http://localhost:5000', 'X-Title': 'Chatlytics'}
        data = {'model': self.model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': max_tokens, 'temperature': Config.AI_TEMPERATURE}
        try:
            response = requests.post(f'{self.base_url}/chat/completions', headers=headers, json=data, timeout=Config.AI_REQUEST_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._clean_ai_text(content)
            else:
                print(f'API Error: {response.status_code} - {response.text}')
                raise Exception(f'API call failed: {response.status_code} - {response.text}')
        except requests.exceptions.RequestException as e:
            print(f'Request error: {str(e)}')
            raise Exception(f'Network error: {str(e)}')
        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            raise

    def _clean_ai_text(self, text: str) -> str:
        if not text:
            return ''
        text = re.sub('#{1,6}\\s*', '', text)
        text = re.sub('\\*\\*(.*?)\\*\\*', '\\1', text)
        text = re.sub('\\*(.*?)\\*', '\\1', text)
        text = re.sub('\\[([^\\]]+)\\]\\([^)]+\\)', '\\1', text)
        text = re.sub('\\n\\s*\\n', '\n\n', text)
        text = text.strip()
        return text

    def _generate_all_insights_at_once(self, chat_summary: Dict[str, Any]) -> Dict[str, str]:
        senders = chat_summary['senders']
        sample_messages = chat_summary['sample_messages']
        total_messages = chat_summary['total_messages']
        sender_counts = chat_summary['sender_counts']
        date_range = chat_summary['date_range']
        avg_message_length = chat_summary['avg_message_length']
        most_active_hour = chat_summary['most_active_hour']
        prompt = f'Analyze this chat data and provide 5 concise, fun insights. Keep each response under 50 words and be playful!\n\nCHAT DATA:\nParticipants: {', '.join(senders)}\nMessages: {', '.join([f'{sender}: {count}' for sender, count in sender_counts.items()])}\nPeriod: {date_range['start']} to {date_range['end']} ({date_range['duration_days']} days)\nStats: {avg_message_length:.1f} words/msg, most active at {most_active_hour}:00, {total_messages:,} total messages\n\nSample messages:\n{chr(10).join([f'{msg['sender']}: {msg['message'][:100]}...' for msg in sample_messages[:8]])}\n\nPlease respond in this EXACT format:\n\nPERSONALITY: [Fun 1-2 sentence personality analysis for each person]\nRELATIONSHIP: [Warm 1-2 sentence relationship dynamic]\nSTYLE: [Playful 1-2 sentence conversation style]\nFACTS: [3-4 bullet point fun facts]\nSUMMARY: [Heartfelt 1-2 sentence overall summary]\n\nBe concise, fun, and positive!'
        try:
            response = self._call_openrouter_api(prompt, 400)
            return self._parse_ai_response(response)
        except Exception as e:
            print(f'Single API call failed: {e}')
            raise e

    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        sections = {'personality_analysis': 'Personality analysis temporarily unavailable.', 'relationship_dynamics': 'Relationship dynamics temporarily unavailable.', 'conversation_style': 'Conversation style temporarily unavailable.', 'fun_facts': 'Fun facts temporarily unavailable.', 'overall_summary': 'Overall summary temporarily unavailable.'}
        try:
            parts = response.split('\n')
            current_section = None
            current_content = []
            for line in parts:
                line = line.strip()
                if line.startswith('PERSONALITY:'):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'personality_analysis'
                    current_content = [line.replace('PERSONALITY:', '').strip()]
                elif line.startswith('RELATIONSHIP:'):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'relationship_dynamics'
                    current_content = [line.replace('RELATIONSHIP:', '').strip()]
                elif line.startswith('STYLE:'):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'conversation_style'
                    current_content = [line.replace('STYLE:', '').strip()]
                elif line.startswith('FACTS:'):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'fun_facts'
                    current_content = [line.replace('FACTS:', '').strip()]
                elif line.startswith('SUMMARY:'):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'overall_summary'
                    current_content = [line.replace('SUMMARY:', '').strip()]
                elif current_section and line:
                    current_content.append(line)
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            for key, value in sections.items():
                if not value or value == f'{key.replace('_', ' ').title()} temporarily unavailable.':
                    sections[key] = f'{key.replace('_', ' ').title()} temporarily unavailable.'
            return sections
        except Exception as e:
            print(f'Error parsing AI response: {e}')
            return sections

    def _generate_personality_analysis(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        sample_messages = chat_summary['sample_messages']
        prompt = f'Fun personality analysis for each person in 1-2 sentences. Be playful!\n\nParticipants: {', '.join(senders)}\nSample: {chr(10).join([f'{msg['sender']}: {msg['message'][:80]}...' for msg in sample_messages[:6]])}\n\nFocus on communication style and what makes them unique!'
        return self._call_openrouter_api(prompt, 120)

    def _generate_relationship_dynamics(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        total_messages = chat_summary['total_messages']
        sender_counts = chat_summary['sender_counts']
        date_range = chat_summary['date_range']
        prompt = f'Relationship dynamic in 1-2 warm sentences.\n\n{', '.join(senders)}: {', '.join([f'{sender}({count})' for sender, count in sender_counts.items()])}\n{date_range['start']} to {date_range['end']}\n\nWhat kind of connection? Keep it positive!'
        return self._call_openrouter_api(prompt, 80)

    def _generate_conversation_style(self, chat_summary: Dict[str, Any]) -> str:
        avg_message_length = chat_summary['avg_message_length']
        most_active_hour = chat_summary['most_active_hour']
        total_messages = chat_summary['total_messages']
        prompt = f"Conversation style in 1-2 fun sentences.\n\n{avg_message_length:.1f} words/msg, active at {most_active_hour}:00, {total_messages:,} messages\n\nChatty or brief? Night owls? What's special?"
        return self._call_openrouter_api(prompt, 80)

    def _generate_fun_facts(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        total_messages = chat_summary['total_messages']
        date_range = chat_summary['date_range']
        duration_days = date_range.get('duration_days', 1)
        prompt = f'3-4 fun facts about this chat! Use bullets.\n\n{', '.join(senders)}: {total_messages:,} messages in {duration_days} days ({date_range['start']} to {date_range['end']})\n\nMake them entertaining! Think milestones or cool patterns.'
        return self._call_openrouter_api(prompt, 120)

    def _generate_overall_summary(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        total_messages = chat_summary['total_messages']
        date_range = chat_summary['date_range']
        prompt = f'Warm 1-2 sentence summary celebrating their connection.\n\n{', '.join(senders)}: {total_messages:,} messages from {date_range['start']} to {date_range['end']}\n\nWhat story does this tell? Make it heartfelt!'
        return self._call_openrouter_api(prompt, 80)

    def _generate_fallback_personality_analysis(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        sender_counts = chat_summary['sender_counts']
        sample_messages = chat_summary['sample_messages']
        analysis = []
        for sender in senders:
            sender_messages = [msg for msg in sample_messages if msg['sender'] == sender]
            message_count = sender_counts[sender]
            avg_length = sum((len(msg['message'].split()) for msg in sender_messages)) / len(sender_messages) if sender_messages else 0
            if avg_length > 10:
                style = 'detailed writer'
            elif avg_length > 5:
                style = 'moderate communicator'
            else:
                style = 'concise texter'
            emoji_count = sum((len([c for c in msg['message'] if ord(c) > 127]) for msg in sender_messages))
            emoji_style = ' 😊' if emoji_count > len(sender_messages) * 0.5 else ''
            if message_count > sum(sender_counts.values()) * 0.6:
                engagement = 'conversation leader'
            elif message_count > sum(sender_counts.values()) * 0.4:
                engagement = 'active participant'
            else:
                engagement = 'thoughtful listener'
            analysis.append(f'**{sender}**: A {style} and {engagement} with {message_count:,} messages{emoji_style}!')
        return '\n\n'.join(analysis)

    def _generate_fallback_relationship_dynamics(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        sender_counts = chat_summary['sender_counts']
        total_messages = chat_summary['total_messages']
        if len(senders) == 2:
            sender1, sender2 = senders
            count1, count2 = (sender_counts[sender1], sender_counts[sender2])
            if abs(count1 - count2) < total_messages * 0.1:
                balance = 'perfectly balanced'
            elif abs(count1 - count2) < total_messages * 0.3:
                balance = 'well-balanced'
            else:
                balance = 'complementary'
            insight = 'a strong connection' if total_messages > 5000 else 'meaningful communication'
            return f'{sender1} and {sender2} have {insight} with a {balance} dynamic ({count1:,} vs {count2:,} messages). They bring different but complementary styles to their relationship! 💕'
        else:
            return f'This group chat has {len(senders)} participants with diverse communication styles. Everyone brings their unique voice to the conversation! 👥'

    def _generate_fallback_conversation_style(self, chat_summary: Dict[str, Any]) -> str:
        avg_message_length = chat_summary['avg_message_length']
        most_active_hour = chat_summary['most_active_hour']
        total_messages = chat_summary['total_messages']
        if avg_message_length > 15:
            length_style = 'detailed & thoughtful'
        elif avg_message_length > 8:
            length_style = 'moderately detailed'
        else:
            length_style = 'concise & direct'
        if most_active_hour < 6 or most_active_hour > 22:
            time_style = 'night owls' if most_active_hour < 6 else 'late night chatters'
        elif 9 <= most_active_hour <= 17:
            time_style = 'daytime communicators'
        else:
            time_style = 'evening conversationalists'
        return f"Communication style: {length_style} with {total_messages:,} messages. They're {time_style}! 🌙☀️"

    def _generate_fallback_fun_facts(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        total_messages = chat_summary['total_messages']
        date_range = chat_summary['date_range']
        duration_days = chat_summary['date_range'].get('duration_days', 1)
        facts = []
        if total_messages > 10000:
            facts.append(f'• Massive chat: {total_messages:,} messages! 🚀')
        elif total_messages > 1000:
            facts.append(f'• Big conversation: {total_messages:,} messages! 💬')
        else:
            facts.append(f'• Shared {total_messages:,} messages together')
        if duration_days > 365:
            facts.append(f'• Over a year of chatting ({duration_days} days) 📅')
        elif duration_days > 30:
            facts.append(f'• {duration_days} days of conversation')
        else:
            facts.append(f'• {duration_days}-day chat streak')
        if len(senders) == 2:
            facts.append(f'• One-on-one between {senders[0]} & {senders[1]} 💕')
        else:
            facts.append(f'• Group chat with {len(senders)} people 👥')
        avg_daily = total_messages / max(duration_days, 1)
        if avg_daily > 50:
            facts.append(f'• {avg_daily:.1f} messages/day - super active! ⚡')
        elif avg_daily > 10:
            facts.append(f'• {avg_daily:.1f} messages/day')
        else:
            facts.append(f'• {avg_daily:.1f} messages/day - quality over quantity! ✨')
        return '\n'.join(facts)

    def _generate_fallback_overall_summary(self, chat_summary: Dict[str, Any]) -> str:
        senders = chat_summary['senders']
        total_messages = chat_summary['total_messages']
        date_range = chat_summary['date_range']
        duration_days = chat_summary['date_range'].get('duration_days', 1)
        if len(senders) == 2:
            relationship_type = 'friendship' if total_messages < 5000 else 'close bond'
            connection = 'deep connection' if total_messages > 10000 else 'meaningful communication'
            activity = 'very active' if total_messages > 10000 else 'moderately active'
            bond = 'strong bond' if total_messages > 5000 else 'growing relationship'
            return f"{senders[0]} & {senders[1]}'s {relationship_type}: {duration_days} days, {total_messages:,} messages. Shows {connection} with {activity} communication - a {bond}! 💕"
        else:
            activity = 'highly active' if total_messages > 10000 else 'active'
            return f'Group chat with {len(senders)} people: {total_messages:,} messages over {duration_days} days. {activity.title()} group dynamics with meaningful interactions! 👥✨'