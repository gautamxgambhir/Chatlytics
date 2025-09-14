import re
import string
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, Optional

class ChatAnalyzer:

    def __init__(self) -> None:
        # Common English stopwords (no NLTK dependency)
        self.stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'}
        self.affectionate_words = {'love', 'loved', 'loving', 'heart', 'hearts', 'romantic', 'romance', 'passion', 'passionate', 'intimate', 'intimacy', 'hugs', 'hug', 'kiss', 'kisses', 'kissing', 'tender', 'tenderness', 'gentle', 'gentleness', 'warm', 'warmth', 'comfort', 'comforting', 'sweet', 'sweeter', 'sweetest', 'cute', 'cuter', 'cutest', 'beautiful', 'gorgeous', 'darling', 'dear', 'honey', 'baby', 'babe', 'sweetheart', 'beloved', 'treasure', 'angel', 'prince', 'princess', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect', 'incredible', 'unbelievable', 'extraordinary', 'remarkable', 'precious', 'special', 'unique', 'irreplaceable', 'valuable', 'miss', 'missing', 'care', 'caring', 'adore', 'adoring', 'cherish', 'cherishing', 'fond', 'fondness', 'affection', 'affectionate', 'secure', 'security', 'trust', 'trusting', 'faithful', 'faithfulness', 'loyal', 'loyalty', 'devoted', 'devotion', 'commitment', 'together', 'forever', 'always', 'promise', 'promises', 'dream', 'dreams', 'hope', 'hopes', 'wish', 'wishes', 'blessed', 'blessing', 'grateful', 'gratitude', 'thankful', 'appreciate', 'appreciation', 'jaan', 'bro', 'bestie', 'dude', 'buddy', 'friend', 'mate', 'pal'}
        self.conversation_starters = ['hey', 'hi', 'hello', 'hii', 'hiii', 'hiiii', 'hiiiii', 'yo', 'yoo', 'yooo', 'sup', 'whats up', "what's up", 'wassup', 'howdy', 'greetings', 'good morning', 'good afternoon', 'good evening', 'gm', 'gn', 'good night', 'goodnight']
        self.emoji_pattern = re.compile('[😀-🙏🌀-🗿🚀-\U0001f6ff\U0001f1e0-🇿✂-➰Ⓜ-🉑]+', flags=re.UNICODE)

    def analyze_chat(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {}
        total_messages = len(messages)
        senders = list(set((msg['sender'] for msg in messages)))
        message_counts = Counter((msg['sender'] for msg in messages))
        word_counts = self._calculate_word_counts(messages)
        emoji_stats = self._analyze_emoji_personality(messages)
        timing_stats = self._analyze_time_patterns(messages)
        conversation_starters = self._analyze_conversation_starters_detailed(messages)
        return {'basic_stats': {'total_messages': total_messages, 'senders': senders, 'message_counts': dict(message_counts), 'word_counts': word_counts, 'date_range': self._get_date_range(messages)}, 'balance_of_effort': self._analyze_balance_of_effort(messages, message_counts, word_counts), 'conversation_starters': conversation_starters, 'response_time_analysis': self._analyze_response_times_detailed(messages), 'time_analysis': timing_stats, 'emotional_tone': self._analyze_emotional_tone(messages), 'sentiment_analysis': self._analyze_emotional_tone(messages), 'emoji_personality': emoji_stats, 'emoji_stats': emoji_stats, 'message_length_stats': self._analyze_message_lengths(messages), 'conversation_flow': self._analyze_conversation_flow(messages), 'activity_patterns': self._analyze_activity_patterns(messages), 'keyword_tracker': self._analyze_keywords(messages), 'milestones': self._find_milestones(messages), 'affection_score': self._calculate_affection_score(messages), 'mood_timeline': self._analyze_mood_timeline(messages), 'topic_detector': self._detect_topics(messages), 'streaks_gaps': self._analyze_streaks_gaps(messages), 'compatibility_index': self._calculate_compatibility_index(messages, message_counts, word_counts), 'personality_insights': self._generate_personality_insights(messages, message_counts, word_counts), 'who_thinks_first': self._analyze_who_thinks_first(messages), 'fun_metrics': self._calculate_fun_metrics(messages, word_counts, emoji_stats, timing_stats, conversation_starters.get('conversation_starts', {})), 'affinity_scores': self._calculate_affinity_scores(messages)}

    def _calculate_word_counts(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        word_counts = defaultdict(int)
        for msg in messages:
            sender = msg['sender']
            words = self._extract_words(msg['message'])
            word_counts[sender] += len(words)
        return dict(word_counts)

    def _extract_words(self, text: str) -> List[str]:
        text = re.sub('[^\\w\\s]', ' ', text)
        words = text.lower().split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        return words

    def _analyze_emojis(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        emoji_counts = defaultdict(int)
        sender_emoji_counts = defaultdict(lambda: defaultdict(int))
        total_emojis = 0
        for msg in messages:
            sender = msg['sender']
            message = msg['message']
            emojis = self.emoji_pattern.findall(message)
            for emoji in emojis:
                emoji_counts[emoji] += 1
                sender_emoji_counts[sender][emoji] += 1
                total_emojis += 1
        top_emojis = dict(Counter(emoji_counts).most_common(20))
        sender_emoji_totals = {sender: sum(counts.values()) for sender, counts in sender_emoji_counts.items()}
        return {'total_emojis': total_emojis, 'unique_emojis': len(emoji_counts), 'top_emojis': top_emojis, 'sender_emoji_counts': dict(sender_emoji_totals), 'sender_emoji_details': {sender: dict(counts) for sender, counts in sender_emoji_counts.items()}}

    def _analyze_timing(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        sender_hourly = defaultdict(lambda: defaultdict(int))
        sender_daily = defaultdict(lambda: defaultdict(int))
        for msg in messages:
            sender = msg['sender']
            timestamp = msg['timestamp']
            hour = timestamp.hour
            day = timestamp.strftime('%A')
            hourly_counts[hour] += 1
            daily_counts[day] += 1
            sender_hourly[sender][hour] += 1
            sender_daily[sender][day] += 1
        most_active_hour = max(hourly_counts.items(), key=lambda x: x[1])[0]
        most_active_day = max(daily_counts.items(), key=lambda x: x[1])[0]
        late_night_messages = sum((hourly_counts.get(hour, 0) for hour in range(0, 4)))
        return {'hourly_distribution': dict(hourly_counts), 'daily_distribution': dict(daily_counts), 'most_active_hour': most_active_hour, 'most_active_day': most_active_day, 'late_night_messages': late_night_messages, 'sender_hourly': {sender: dict(hours) for sender, hours in sender_hourly.items()}, 'sender_daily': {sender: dict(days) for sender, days in sender_daily.items()}}

    def _analyze_response_times(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        response_times = defaultdict(list)
        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]
            if prev_msg['sender'] != curr_msg['sender']:
                time_diff = (curr_msg['timestamp'] - prev_msg['timestamp']).total_seconds() / 60
                if 0 < time_diff < 1440:
                    response_times[curr_msg['sender']].append(time_diff)
        avg_response_times = {}
        for sender, times in response_times.items():
            if times:
                avg_response_times[sender] = sum(times) / len(times)
        return {'average_response_times': avg_response_times, 'response_time_details': dict(response_times)}

    def _analyze_common_words(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_words = []
        sender_words = defaultdict(list)
        for msg in messages:
            sender = msg['sender']
            words = self._extract_words(msg['message'])
            all_words.extend(words)
            sender_words[sender].extend(words)
        word_freq = Counter(all_words)
        common_words = dict(word_freq.most_common(50))
        sender_common_words = {}
        for sender, words in sender_words.items():
            word_freq = Counter(words)
            sender_common_words[sender] = dict(word_freq.most_common(20))
        return {'overall_common_words': common_words, 'sender_common_words': sender_common_words}

    def _analyze_conversation_starters(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        conversation_starts = defaultdict(int)
        time_gap_threshold = 30
        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]
            time_gap = (curr_msg['timestamp'] - prev_msg['timestamp']).total_seconds() / 60
            if time_gap > time_gap_threshold:
                conversation_starts[curr_msg['sender']] += 1
        if messages:
            conversation_starts[messages[0]['sender']] += 1
        return dict(conversation_starts)

    def _calculate_fun_metrics(self, messages: List[Dict[str, Any]], word_counts: Dict[str, int], emoji_stats: Dict[str, Any], timing_stats: Dict[str, Any], conversation_starters: Dict[str, Any]) -> Dict[str, Any]:
        senders = list(set((msg['sender'] for msg in messages)))
        message_counts = Counter((msg['sender'] for msg in messages))
        message_leader = max(message_counts.items(), key=lambda x: x[1])[0]
        word_leader = max(word_counts.items(), key=lambda x: x[1])[0] if word_counts else senders[0]
        emoji_leader = max(emoji_stats['sender_emoji_counts'].items(), key=lambda x: x[1])[0] if emoji_stats['sender_emoji_counts'] else senders[0]
        initiator_leader = max(conversation_starters.items(), key=lambda x: x[1])[0] if conversation_starters else senders[0]
        night_owl_scores = {}
        for sender in senders:
            late_night_count = sum((timing_stats['sender_hourly'].get(sender, {}).get(hour, 0) for hour in range(0, 6)))
            night_owl_scores[sender] = late_night_count
        night_owl = max(night_owl_scores.items(), key=lambda x: x[1])[0] if night_owl_scores else senders[0]
        return {'message_leader': message_leader, 'word_leader': word_leader, 'emoji_leader': emoji_leader, 'initiator_leader': initiator_leader, 'night_owl': night_owl, 'night_owl_scores': night_owl_scores}

    def _calculate_affinity_scores(self, messages: List[Dict[str, Any]]) -> Dict[str, float]:
        sender_scores = defaultdict(float)
        for msg in messages:
            sender = msg['sender']
            message = msg['message'].lower()
            words = self._extract_words(message)
            affectionate_count = sum((1 for word in words if word in self.affectionate_words))
            affectionate_emojis = ['❤️', '💕', '💖', '💗', '💘', '💝', '💞', '💟', '💌', '💋', '😍', '🥰', '😘', '🤗', '🤩', '😊', '😌', '🥺', '😇', '💯', '✨', '🌟', '💫', '🌈', '🦄', '🌸', '🌺', '🌻', '🌷', '🌹', '🌼', '💐', '🎀', '🎁', '💎', '🏆', '🥇', '👑', '💍', '💐', '🌹', '🌺', '🌸', '🌻', '🌷', '🌼', '💐', '🎀', '🎁', '💎', '🏆', '🥇', '👑', '💍']
            emoji_count = sum((1 for emoji in self.emoji_pattern.findall(message) if emoji in affectionate_emojis))
            message_length = len(words) if words else 1
            score = (affectionate_count + emoji_count) / message_length
            sender_scores[sender] += score
        total_messages = Counter((msg['sender'] for msg in messages))
        normalized_scores = {}
        for sender, score in sender_scores.items():
            message_count = total_messages[sender]
            normalized_scores[sender] = score / message_count * 100 if message_count > 0 else 0
        return normalized_scores

    def _get_date_range(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        if not messages:
            return {}
        timestamps = [msg['timestamp'] for msg in messages]
        start_date = min(timestamps)
        end_date = max(timestamps)
        return {'start': start_date.strftime('%Y-%m-%d'), 'end': end_date.strftime('%Y-%m-%d'), 'duration_days': (end_date - start_date).days}

    def _analyze_message_lengths(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        sender_lengths = defaultdict(list)
        for msg in messages:
            sender = msg['sender']
            length = len(msg['message'].split())
            sender_lengths[sender].append(length)
        stats = {}
        for sender, lengths in sender_lengths.items():
            if lengths:
                stats[sender] = {'avg_length': sum(lengths) / len(lengths), 'min_length': min(lengths), 'max_length': max(lengths), 'median_length': sorted(lengths)[len(lengths) // 2]}
        return stats

    def _analyze_conversation_flow(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(messages) < 2:
            return {}
        turns = []
        current_sender = messages[0]['sender']
        turn_length = 1
        for i in range(1, len(messages)):
            if messages[i]['sender'] == current_sender:
                turn_length += 1
            else:
                turns.append({'sender': current_sender, 'length': turn_length})
                current_sender = messages[i]['sender']
                turn_length = 1
        turns.append({'sender': current_sender, 'length': turn_length})
        sender_turns = defaultdict(list)
        for turn in turns:
            sender_turns[turn['sender']].append(turn['length'])
        turn_stats = {}
        for sender, turn_lengths in sender_turns.items():
            if turn_lengths:
                turn_stats[sender] = {'avg_turn_length': sum(turn_lengths) / len(turn_lengths), 'max_turn_length': max(turn_lengths), 'total_turns': len(turn_lengths)}
        return {'turn_stats': turn_stats, 'total_turns': len(turns)}

    def _analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        positive_emojis = ['😊', '😄', '😃', '😁', '😆', '😂', '🤣', '😍', '🥰', '😘', '❤️', '💕', '💖', '💗', '💝', '✨', '🌟', '💫', '🌈', '🎉', '🎊', '👍', '👏', '🙌', '🔥', '💯']
        negative_emojis = ['😢', '😭', '😔', '😞', '😟', '😕', '🙁', '☹️', '😠', '😡', '😤', '😒', '😑', '😐', '😶', '💔', '😰', '😨', '😱', '😖', '😣', '😫', '😩']
        positive_words = ['love', 'amazing', 'wonderful', 'great', 'awesome', 'fantastic', 'perfect', 'beautiful', 'sweet', 'cute', 'happy', 'excited', 'joy', 'smile', 'laugh', 'fun', 'good', 'best', 'excellent', 'brilliant']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'worried', 'scared', 'hurt', 'pain', 'cry', 'sick', 'tired', 'bored', 'stupid', 'dumb']
        sender_sentiments = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        for msg in messages:
            sender = msg['sender']
            message = msg['message'].lower()
            emojis = self.emoji_pattern.findall(msg['message'])
            positive_emoji_count = sum((1 for emoji in emojis if emoji in positive_emojis))
            negative_emoji_count = sum((1 for emoji in emojis if emoji in negative_emojis))
            words = self._extract_words(msg['message'])
            positive_word_count = sum((1 for word in words if word in positive_words))
            negative_word_count = sum((1 for word in words if word in negative_words))
            positive_score = positive_emoji_count + positive_word_count
            negative_score = negative_emoji_count + negative_word_count
            if positive_score > negative_score:
                sender_sentiments[sender]['positive'] += 1
            elif negative_score > positive_score:
                sender_sentiments[sender]['negative'] += 1
            else:
                sender_sentiments[sender]['neutral'] += 1
        sentiment_percentages = {}
        for sender, sentiments in sender_sentiments.items():
            total = sum(sentiments.values())
            if total > 0:
                sentiment_percentages[sender] = {'positive': sentiments['positive'] / total * 100, 'negative': sentiments['negative'] / total * 100, 'neutral': sentiments['neutral'] / total * 100}
        return sentiment_percentages

    def _analyze_activity_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        weekly_activity = defaultdict(int)
        monthly_activity = defaultdict(int)
        for msg in messages:
            timestamp = msg['timestamp']
            week_key = timestamp.strftime('%Y-W%U')
            month_key = timestamp.strftime('%Y-%m')
            weekly_activity[week_key] += 1
            monthly_activity[month_key] += 1
        most_active_week = max(weekly_activity.items(), key=lambda x: x[1]) if weekly_activity else ('', 0)
        most_active_month = max(monthly_activity.items(), key=lambda x: x[1]) if monthly_activity else ('', 0)
        return {'weekly_activity': dict(weekly_activity), 'monthly_activity': dict(monthly_activity), 'most_active_week': most_active_week[0], 'most_active_month': most_active_month[0], 'avg_messages_per_week': sum(weekly_activity.values()) / len(weekly_activity) if weekly_activity else 0, 'avg_messages_per_month': sum(monthly_activity.values()) / len(monthly_activity) if monthly_activity else 0}

    def _analyze_balance_of_effort(self, messages: List[Dict[str, Any]], message_counts: Counter, word_counts: Dict[str, int]) -> Dict[str, Any]:
        total_messages = sum(message_counts.values())
        total_words = sum(word_counts.values())
        balance_data = {}
        for sender in message_counts.keys():
            msg_percentage = message_counts[sender] / total_messages * 100 if total_messages > 0 else 0
            avg_word_length = word_counts[sender] / message_counts[sender] if message_counts[sender] > 0 else 0
            balance_data[sender] = {'message_percentage': round(msg_percentage, 1), 'avg_word_length': round(avg_word_length, 1), 'total_messages': message_counts[sender], 'total_words': word_counts[sender]}
        message_leader = max(message_counts.items(), key=lambda x: x[1])[0]
        word_leader = max(word_counts.items(), key=lambda x: x[1])[0] if word_counts else list(message_counts.keys())[0]
        return {'balance_data': balance_data, 'message_leader': message_leader, 'word_leader': word_leader, 'insight': self._generate_balance_insight(balance_data, message_leader, word_leader)}

    def _generate_balance_insight(self, balance_data: Dict, message_leader: str, word_leader: str) -> str:
        if len(balance_data) < 2:
            return 'Single person conversation'
        senders = list(balance_data.keys())
        sender1, sender2 = (senders[0], senders[1])
        msg_diff = abs(balance_data[sender1]['message_percentage'] - balance_data[sender2]['message_percentage'])
        word_diff = abs(balance_data[sender1]['avg_word_length'] - balance_data[sender2]['avg_word_length'])
        if msg_diff > 20:
            if balance_data[sender1]['message_percentage'] > balance_data[sender2]['message_percentage']:
                return f'{sender1} sends more frequent messages, while {sender2} is more selective'
            else:
                return f'{sender2} sends more frequent messages, while {sender1} is more selective'
        elif word_diff > 5:
            if balance_data[sender1]['avg_word_length'] > balance_data[sender2]['avg_word_length']:
                return f'{sender1} writes longer messages, while {sender2} prefers shorter ones'
            else:
                return f'{sender2} writes longer messages, while {sender1} prefers shorter ones'
        else:
            return 'You both have a balanced conversation style'

    def _analyze_conversation_starters_detailed(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        conversation_starts = defaultdict(int)
        starter_words = defaultdict(int)
        time_gap_threshold = 30
        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]
            time_gap = (curr_msg['timestamp'] - prev_msg['timestamp']).total_seconds() / 60
            if time_gap > time_gap_threshold:
                conversation_starts[curr_msg['sender']] += 1
                first_words = curr_msg['message'].lower().split()[:3]
                for word in first_words:
                    if word in self.conversation_starters:
                        starter_words[word] += 1
        if messages:
            conversation_starts[messages[0]['sender']] += 1
            first_words = messages[0]['message'].lower().split()[:3]
            for word in first_words:
                if word in self.conversation_starters:
                    starter_words[word] += 1
        initiator_leader = max(conversation_starts.items(), key=lambda x: x[1])[0] if conversation_starts else 'Unknown'
        top_starter = max(starter_words.items(), key=lambda x: x[1])[0] if starter_words else 'Hey'
        return {'conversation_starts': dict(conversation_starts), 'starter_words': dict(starter_words), 'initiator_leader': initiator_leader, 'top_starter_word': top_starter, 'title': f'{initiator_leader} - The Icebreaker'}

    def _analyze_response_times_detailed(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        response_times = defaultdict(list)
        response_distribution = defaultdict(int)
        delivered_status = defaultdict(int)
        median_response_times = {}
        percentile_response_times = {}
        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]
            if prev_msg['sender'] != curr_msg['sender']:
                time_diff = (curr_msg['timestamp'] - prev_msg['timestamp']).total_seconds() / 60
                if 0 < time_diff < 10080:
                    response_times[curr_msg['sender']].append(time_diff)
                    if time_diff < 1:
                        response_distribution[f'{curr_msg['sender']}_instant'] += 1
                    elif time_diff < 5:
                        response_distribution[f'{curr_msg['sender']}_very_fast'] += 1
                    elif time_diff < 15:
                        response_distribution[f'{curr_msg['sender']}_fast'] += 1
                    elif time_diff < 60:
                        response_distribution[f'{curr_msg['sender']}_medium'] += 1
                    elif time_diff < 180:
                        response_distribution[f'{curr_msg['sender']}_slow'] += 1
                    elif time_diff < 1440:
                        response_distribution[f'{curr_msg['sender']}_very_slow'] += 1
                        delivered_status[curr_msg['sender']] += 1
                    else:
                        response_distribution[f'{curr_msg['sender']}_delivered'] += 1
                        delivered_status[curr_msg['sender']] += 1
        avg_response_times = {}
        for sender, times in response_times.items():
            if times:
                sorted_times = sorted(times)
                avg_response_times[sender] = round(sum(times) / len(times), 1)
                median_response_times[sender] = round(sorted_times[len(sorted_times) // 2], 1)
                percentile_response_times[sender] = {'p25': round(sorted_times[len(sorted_times) // 4], 1), 'p75': round(sorted_times[int(len(sorted_times) * 0.75)], 1), 'p90': round(sorted_times[int(len(sorted_times) * 0.9)], 1), 'min': round(min(times), 1), 'max': round(max(times), 1)}
        fastest_responder = min(avg_response_times.items(), key=lambda x: x[1])[0] if avg_response_times else None
        slowest_responder = max(avg_response_times.items(), key=lambda x: x[1])[0] if avg_response_times else None
        most_delivered = max(delivered_status.items(), key=lambda x: x[1])[0] if delivered_status else None
        response_speed_analysis = self._analyze_response_speed_patterns(response_times)
        return {'average_response_times': avg_response_times, 'median_response_times': median_response_times, 'percentile_response_times': percentile_response_times, 'response_distribution': dict(response_distribution), 'delivered_status': dict(delivered_status), 'fastest_responder': fastest_responder, 'slowest_responder': slowest_responder, 'most_delivered': most_delivered, 'speed_patterns': response_speed_analysis, 'insight': self._generate_enhanced_response_insight(avg_response_times, fastest_responder, slowest_responder, delivered_status)}

    def _analyze_response_speed_patterns(self, response_times: Dict) -> Dict[str, Any]:
        speed_patterns = {}
        for sender, times in response_times.items():
            if not times:
                continue
            instant_responses = sum((1 for t in times if t < 1))
            fast_responses = sum((1 for t in times if 1 <= t < 15))
            delayed_responses = sum((1 for t in times if t >= 60))
            total_responses = len(times)
            speed_patterns[sender] = {'instant_percent': round(instant_responses / total_responses * 100, 1), 'fast_percent': round(fast_responses / total_responses * 100, 1), 'delayed_percent': round(delayed_responses / total_responses * 100, 1), 'consistency_score': round(100 - (max(times) - min(times)) / 60, 1) if times else 0}
        return speed_patterns

    def _generate_enhanced_response_insight(self, avg_times: Dict, fastest: str, slowest: str, delivered_status: Dict) -> str:
        if len(avg_times) < 1:
            return 'No response time data available'
        if len(avg_times) < 2:
            return 'Single person conversation'
        if not fastest:
            return 'No response time analysis available'
        insights = []
        if fastest and slowest and (fastest != slowest):
            fast_time = avg_times[fastest]
            slow_time = avg_times[slowest]
            if fast_time < 5:
                insights.append(f'{fastest} is lightning fast (avg {fast_time:.1f} min)')
            elif fast_time < 15:
                insights.append(f'{fastest} responds quickly (avg {fast_time:.1f} min)')
            else:
                insights.append(f'{fastest} takes {fast_time:.1f} min on average')
            if slow_time > 60:
                insights.append(f'{slowest} takes their time (avg {slow_time:.1f} min)')
            else:
                insights.append(f'{slowest} responds in {slow_time:.1f} min')
        if delivered_status:
            most_delivered = max(delivered_status.items(), key=lambda x: x[1])[0]
            delivered_count = delivered_status[most_delivered]
            if delivered_count > 5:
                insights.append(f"{most_delivered} leaves {delivered_count} messages on 'delivered' status")
        return '. '.join(insights) if insights else 'Similar response patterns'

    def _analyze_time_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        hourly_counts = defaultdict(int)
        sender_hourly = defaultdict(lambda: defaultdict(int))
        day_night_counts = defaultdict(int)
        for msg in messages:
            sender = msg['sender']
            hour = msg['timestamp'].hour
            hourly_counts[hour] += 1
            sender_hourly[sender][hour] += 1
            if 6 <= hour < 18:
                day_night_counts[f'{sender}_day'] += 1
            else:
                day_night_counts[f'{sender}_night'] += 1
        night_owls = {}
        early_birds = {}
        for sender in sender_hourly.keys():
            night_count = sum((sender_hourly[sender].get(hour, 0) for hour in range(22, 24))) + sum((sender_hourly[sender].get(hour, 0) for hour in range(0, 6)))
            day_count = sum((sender_hourly[sender].get(hour, 0) for hour in range(6, 22)))
            night_owls[sender] = night_count
            early_birds[sender] = day_count
        night_owl = max(night_owls.items(), key=lambda x: x[1])[0] if night_owls else 'Unknown'
        early_bird = max(early_birds.items(), key=lambda x: x[1])[0] if early_birds else 'Unknown'
        most_active_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 12
        daily_counts = defaultdict(int)
        for msg in messages:
            day = msg['timestamp'].strftime('%A')
            daily_counts[day] += 1
        most_active_day = max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else 'Monday'
        late_night_messages = sum((hourly_counts.get(hour, 0) for hour in range(0, 4)))
        return {'hourly_distribution': dict(hourly_counts), 'daily_distribution': dict(daily_counts), 'most_active_hour': most_active_hour, 'most_active_day': most_active_day, 'late_night_messages': late_night_messages, 'sender_hourly': {sender: dict(hours) for sender, hours in sender_hourly.items()}, 'day_night_counts': dict(day_night_counts), 'night_owl': night_owl, 'early_bird': early_bird, 'insight': 'Most deep conversations happen after 11pm' if hourly_counts and max(hourly_counts.values()) > sum(hourly_counts.values()) * 0.3 else 'Balanced day and night conversations'}

    def _analyze_emotional_tone(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        positive_emojis = ['😊', '😄', '😃', '😁', '😆', '😂', '🤣', '😍', '🥰', '😘', '❤️', '💕', '💖', '💗', '💝', '✨', '🌟', '💫', '🌈', '🎉', '🎊', '👍', '👏', '🙌', '🔥', '💯', '😇', '🥺', '😌']
        negative_emojis = ['😢', '😭', '😔', '😞', '😟', '😕', '🙁', '☹️', '😠', '😡', '😤', '😒', '😑', '😐', '😶', '💔', '😰', '😨', '😱', '😖', '😣', '😫', '😩']
        positive_words = ['love', 'amazing', 'wonderful', 'great', 'awesome', 'fantastic', 'perfect', 'beautiful', 'sweet', 'cute', 'happy', 'excited', 'joy', 'smile', 'laugh', 'fun', 'good', 'best', 'excellent', 'brilliant', 'yay', 'yes', 'yeah', 'cool', 'nice']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'worried', 'scared', 'hurt', 'pain', 'cry', 'sick', 'tired', 'bored', 'stupid', 'dumb', 'no', 'nope', 'ugh', 'ughh']
        sender_sentiments = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        for msg in messages:
            sender = msg['sender']
            message = msg['message']
            emojis = self.emoji_pattern.findall(message)
            positive_emoji_count = sum((1 for emoji in emojis if emoji in positive_emojis))
            negative_emoji_count = sum((1 for emoji in emojis if emoji in negative_emojis))
            words = self._extract_words(message)
            positive_word_count = sum((1 for word in words if word in positive_words))
            negative_word_count = sum((1 for word in words if word in negative_words))
            positive_score = positive_emoji_count + positive_word_count
            negative_score = negative_emoji_count + negative_word_count
            if positive_score > negative_score:
                sender_sentiments[sender]['positive'] += 1
            elif negative_score > positive_score:
                sender_sentiments[sender]['negative'] += 1
            else:
                sender_sentiments[sender]['neutral'] += 1
        sentiment_percentages = {}
        for sender, sentiments in sender_sentiments.items():
            total = sum(sentiments.values())
            if total > 0:
                sentiment_percentages[sender] = {'positive': round(sentiments['positive'] / total * 100, 1), 'negative': round(sentiments['negative'] / total * 100, 1), 'neutral': round(sentiments['neutral'] / total * 100, 1)}
        return {'sentiment_percentages': sentiment_percentages, 'overall_mood': self._calculate_overall_mood(sentiment_percentages), **sentiment_percentages}

    def _calculate_overall_mood(self, sentiment_percentages: Dict) -> str:
        if not sentiment_percentages:
            return 'Neutral'
        total_positive = sum((data['positive'] for data in sentiment_percentages.values()))
        total_negative = sum((data['negative'] for data in sentiment_percentages.values()))
        if total_positive > total_negative * 1.5:
            return 'Very Positive'
        elif total_positive > total_negative:
            return 'Positive'
        elif total_negative > total_positive * 1.5:
            return 'Negative'
        else:
            return 'Neutral'

    def _analyze_emoji_personality(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        emoji_counts = defaultdict(int)
        sender_emojis = defaultdict(lambda: defaultdict(int))
        total_emojis = 0
        for msg in messages:
            sender = msg['sender']
            emojis = self.emoji_pattern.findall(msg['message'])
            for emoji in emojis:
                emoji_counts[emoji] += 1
                sender_emojis[sender][emoji] += 1
                total_emojis += 1
        top_emojis = dict(Counter(emoji_counts).most_common(20))
        sender_emoji_totals = {sender: sum(counts.values()) for sender, counts in sender_emojis.items()}
        emoji_leaders = {}
        for sender, emojis in sender_emojis.items():
            if emojis:
                top_emoji = max(emojis.items(), key=lambda x: x[1])[0]
                emoji_leaders[sender] = {'top_emoji': top_emoji, 'count': emojis[top_emoji], 'total_emojis': sum(emojis.values())}
        emoji_king = max(sender_emoji_totals.items(), key=lambda x: x[1])[0] if sender_emoji_totals else 'Unknown'
        return {'top_emojis': top_emojis, 'sender_emoji_totals': sender_emoji_totals, 'sender_emoji_counts': sender_emoji_totals, 'sender_emoji_details': {sender: dict(emojis) for sender, emojis in sender_emojis.items()}, 'emoji_leaders': emoji_leaders, 'emoji_king': emoji_king, 'title': f'{emoji_king} - Emoji King/Queen'}

    def _analyze_keywords(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_words = []
        sender_words = defaultdict(list)
        shared_words = set()
        for msg in messages:
            sender = msg['sender']
            words = self._extract_words(msg['message'])
            all_words.extend(words)
            sender_words[sender].extend(words)
        word_freq = Counter(all_words)
        common_words = dict(word_freq.most_common(50))
        sender_common_words = {}
        for sender, words in sender_words.items():
            word_freq = Counter(words)
            sender_common_words[sender] = dict(word_freq.most_common(20))
        if len(sender_words) == 2:
            senders = list(sender_words.keys())
            words1 = set(sender_words[senders[0]])
            words2 = set(sender_words[senders[1]])
            shared_words = words1.intersection(words2)
        return {'overall_common_words': common_words, 'sender_common_words': sender_common_words, 'shared_words': list(shared_words)[:20], 'unique_words_per_sender': {sender: len(set(words)) for sender, words in sender_words.items()}}

    def _find_milestones(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {}
        first_message = messages[0]
        last_message = messages[-1]
        daily_counts = defaultdict(int)
        for msg in messages:
            date_key = msg['timestamp'].strftime('%Y-%m-%d')
            daily_counts[date_key] += 1
        most_active_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else ('', 0)
        streaks = self._calculate_streaks(messages)
        longest_streak = max(streaks, key=lambda x: x['length']) if streaks else {'length': 0, 'start': '', 'end': ''}
        return {'first_message': {'sender': first_message['sender'], 'message': first_message['message'][:100] + '...' if len(first_message['message']) > 100 else first_message['message'], 'timestamp': first_message['timestamp'].strftime('%Y-%m-%d %H:%M')}, 'most_active_day': {'date': most_active_day[0], 'message_count': most_active_day[1]}, 'longest_conversation_streak': longest_streak, 'total_days': len(daily_counts)}

    def _calculate_streaks(self, messages: List[Dict[str, Any]]) -> List[Dict]:
        streaks = []
        current_streak = 1
        current_date = messages[0]['timestamp'].date()
        streak_start = current_date
        for i in range(1, len(messages)):
            msg_date = messages[i]['timestamp'].date()
            if msg_date == current_date:
                current_streak += 1
            else:
                if current_streak > 1:
                    streaks.append({'length': current_streak, 'start': streak_start.strftime('%Y-%m-%d'), 'end': current_date.strftime('%Y-%m-%d')})
                current_streak = 1
                current_date = msg_date
                streak_start = msg_date
        if current_streak > 1:
            streaks.append({'length': current_streak, 'start': streak_start.strftime('%Y-%m-%d'), 'end': current_date.strftime('%Y-%m-%d')})
        return streaks

    def _calculate_affection_score(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        sender_scores = defaultdict(float)
        sender_messages = defaultdict(int)
        for msg in messages:
            sender = msg['sender']
            message = msg['message'].lower()
            sender_messages[sender] += 1
            words = self._extract_words(message)
            affectionate_count = sum((1 for word in words if word in self.affectionate_words))
            affectionate_emojis = ['❤️', '💕', '💖', '💗', '💘', '💝', '💞', '💟', '💌', '💋', '😍', '🥰', '😘', '🤗', '🤩', '😊', '😌', '🥺', '😇', '💯', '✨', '🌟', '💫', '🌈', '🦄', '🌸', '🌺', '🌻', '🌷', '🌹', '🌼', '💐', '🎀', '🎁', '💎', '🏆', '🥇', '👑', '💍']
            emoji_count = sum((1 for emoji in self.emoji_pattern.findall(msg['message']) if emoji in affectionate_emojis))
            message_length = len(words) if words else 1
            score = (affectionate_count + emoji_count) / message_length
            sender_scores[sender] += score
        affection_scores = {}
        for sender, score in sender_scores.items():
            message_count = sender_messages[sender]
            affection_scores[sender] = round(score / message_count * 100, 1) if message_count > 0 else 0
        most_affectionate = max(affection_scores.items(), key=lambda x: x[1])[0] if affection_scores else 'Unknown'
        return {'affection_scores': affection_scores, 'most_affectionate': most_affectionate, 'compatibility_gauge': self._calculate_compatibility_gauge(affection_scores)}

    def _calculate_compatibility_gauge(self, affection_scores: Dict) -> int:
        if len(affection_scores) < 2:
            return 50
        scores = list(affection_scores.values())
        avg_score = sum(scores) / len(scores)
        score_diff = abs(scores[0] - scores[1]) if len(scores) == 2 else 0
        if avg_score > 10 and score_diff < 5:
            return min(100, int(avg_score * 2))
        elif avg_score > 5:
            return min(80, int(avg_score * 3))
        else:
            return max(20, int(avg_score * 5))

    def _analyze_mood_timeline(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        daily_moods = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        positive_words = ['love', 'amazing', 'wonderful', 'great', 'awesome', 'fantastic', 'perfect', 'beautiful', 'sweet', 'cute', 'happy', 'excited', 'joy', 'smile', 'laugh', 'fun', 'good', 'best', 'excellent', 'brilliant']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'worried', 'scared', 'hurt', 'pain', 'cry', 'sick', 'tired', 'bored', 'stupid', 'dumb']
        for msg in messages:
            date_key = msg['timestamp'].strftime('%Y-%m-%d')
            words = self._extract_words(msg['message'])
            positive_count = sum((1 for word in words if word in positive_words))
            negative_count = sum((1 for word in words if word in negative_words))
            if positive_count > negative_count:
                daily_moods[date_key]['positive'] += 1
            elif negative_count > positive_count:
                daily_moods[date_key]['negative'] += 1
            else:
                daily_moods[date_key]['neutral'] += 1
        timeline_data = []
        for date, moods in sorted(daily_moods.items()):
            total = sum(moods.values())
            if total > 0:
                timeline_data.append({'date': date, 'positive_ratio': round(moods['positive'] / total, 2), 'negative_ratio': round(moods['negative'] / total, 2), 'neutral_ratio': round(moods['neutral'] / total, 2)})
        return {'timeline_data': timeline_data, 'overall_trend': self._calculate_mood_trend(timeline_data)}

    def _calculate_mood_trend(self, timeline_data: List[Dict]) -> str:
        if len(timeline_data) < 2:
            return 'Insufficient data'
        recent_positive = sum((day['positive_ratio'] for day in timeline_data[-7:])) / min(7, len(timeline_data))
        early_positive = sum((day['positive_ratio'] for day in timeline_data[:7])) / min(7, len(timeline_data))
        if recent_positive > early_positive + 0.1:
            return 'Mood is improving over time'
        elif recent_positive < early_positive - 0.1:
            return 'Mood is declining over time'
        else:
            return 'Mood is stable over time'

    def _detect_topics(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        topic_keywords = {'work': ['work', 'job', 'office', 'meeting', 'project', 'boss', 'colleague', 'deadline', 'presentation'], 'food': ['food', 'eat', 'eating', 'hungry', 'restaurant', 'cooking', 'recipe', 'delicious', 'tasty', 'meal', 'dinner', 'lunch', 'breakfast'], 'travel': ['travel', 'trip', 'vacation', 'flight', 'hotel', 'beach', 'mountain', 'city', 'country', 'visit', 'explore'], 'entertainment': ['movie', 'film', 'show', 'series', 'music', 'song', 'book', 'game', 'fun', 'entertainment', 'watch', 'listen'], 'family': ['family', 'mom', 'dad', 'mother', 'father', 'sister', 'brother', 'parent', 'relative', 'home'], 'health': ['health', 'sick', 'ill', 'doctor', 'medicine', 'exercise', 'gym', 'fitness', 'pain', 'better', 'well'], 'shopping': ['buy', 'shopping', 'store', 'price', 'expensive', 'cheap', 'money', 'pay', 'card', 'cash'], 'technology': ['phone', 'computer', 'internet', 'app', 'software', 'tech', 'device', 'online', 'digital']}
        topic_counts = defaultdict(int)
        sender_topics = defaultdict(lambda: defaultdict(int))
        for msg in messages:
            sender = msg['sender']
            words = self._extract_words(msg['message'])
            for topic, keywords in topic_keywords.items():
                topic_score = sum((1 for word in words if word in keywords))
                if topic_score > 0:
                    topic_counts[topic] += topic_score
                    sender_topics[sender][topic] += topic_score
        top_topics = dict(Counter(topic_counts).most_common(5))
        return {'top_topics': top_topics, 'sender_topics': {sender: dict(topics) for sender, topics in sender_topics.items()}, 'summary': self._generate_topic_summary(top_topics)}

    def _generate_topic_summary(self, top_topics: Dict) -> str:
        if not top_topics:
            return 'No specific topics detected'
        topics = list(top_topics.keys())[:3]
        return f'You mostly talk about {', '.join(topics)}'

    def _analyze_streaks_gaps(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {}
        daily_activity = defaultdict(int)
        for msg in messages:
            date_key = msg['timestamp'].strftime('%Y-%m-%d')
            daily_activity[date_key] += 1
        dates = sorted(daily_activity.keys())
        if len(dates) < 2:
            return {'longest_streak': 0, 'longest_gap': 0}
        streaks = []
        gaps = []
        current_streak = 1
        current_gap = 0
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i - 1], '%Y-%m-%d').date()
            curr_date = datetime.strptime(dates[i], '%Y-%m-%d').date()
            day_diff = (curr_date - prev_date).days
            if day_diff == 1:
                current_streak += 1
                if current_gap > 0:
                    gaps.append(current_gap)
                    current_gap = 0
            else:
                if current_streak > 1:
                    streaks.append(current_streak)
                current_streak = 1
                if day_diff > 1:
                    current_gap = day_diff - 1
        if current_streak > 1:
            streaks.append(current_streak)
        if current_gap > 0:
            gaps.append(current_gap)
        longest_streak = max(streaks) if streaks else 0
        longest_gap = max(gaps) if gaps else 0
        return {'longest_streak': longest_streak, 'longest_gap': longest_gap, 'total_streaks': len(streaks), 'total_gaps': len(gaps), 'insight': f"You once didn't talk for {longest_gap} days straight" if longest_gap > 0 else 'No significant gaps found'}

    def _calculate_compatibility_index(self, messages: List[Dict[str, Any]], message_counts: Counter, word_counts: Dict[str, int]) -> Dict[str, Any]:
        if len(message_counts) < 2:
            return {'score': 50, 'description': 'Single person conversation'}
        senders = list(message_counts.keys())
        msg_balance = 1 - abs(message_counts[senders[0]] - message_counts[senders[1]]) / max(message_counts.values())
        word_balance = 1 - abs(word_counts[senders[0]] - word_counts[senders[1]]) / max(word_counts.values())
        affection_scores = self._calculate_affection_score(messages)['affection_scores']
        affection_balance = 1 - abs(affection_scores[senders[0]] - affection_scores[senders[1]]) / max(affection_scores.values()) if max(affection_scores.values()) > 0 else 0.5
        response_times = self._analyze_response_times_detailed(messages)['average_response_times']
        if len(response_times) >= 2:
            time_balance = 1 - abs(response_times[senders[0]] - response_times[senders[1]]) / max(response_times.values())
        else:
            time_balance = 0.5
        compatibility_score = int((msg_balance + word_balance + affection_balance + time_balance) * 25)
        if compatibility_score >= 80:
            description = f'{compatibility_score}/100: A perfect match! You complement each other beautifully'
        elif compatibility_score >= 60:
            description = f'{compatibility_score}/100: A great duo with balanced communication'
        elif compatibility_score >= 40:
            description = f'{compatibility_score}/100: A balanced pair with room to grow'
        else:
            description = f"{compatibility_score}/100: Different communication styles, but that's okay!"
        return {'score': compatibility_score, 'description': description, 'factors': {'message_balance': round(msg_balance * 100, 1), 'word_balance': round(word_balance * 100, 1), 'affection_balance': round(affection_balance * 100, 1), 'response_balance': round(time_balance * 100, 1)}}

    def _generate_personality_insights(self, messages: List[Dict[str, Any]], message_counts: Counter, word_counts: Dict[str, int]) -> Dict[str, Any]:
        """Generate personality insights without AI dependency"""
        senders = list(message_counts.keys())
        if len(senders) < 2:
            return {
                'summary': 'This appears to be a single-person conversation or group chat.',
                'top_3_things': ['Individual messaging patterns', 'Personal communication style', 'Message frequency patterns'],
                'fun_title': 'Solo Chatter',
                'personality_insights': ['Single person conversation']
            }
        
        sender1, sender2 = senders[0], senders[1]
        msg1, msg2 = message_counts[sender1], message_counts[sender2]
        words1, words2 = word_counts[sender1], word_counts[sender2]
        
        # Determine roles
        chatterbox = sender1 if msg1 > msg2 * 1.5 else (sender2 if msg2 > msg1 * 1.5 else None)
        listener = sender2 if chatterbox == sender1 else (sender1 if chatterbox == sender2 else None)
        verbose = sender1 if words1 > words2 * 1.2 else (sender2 if words2 > words1 * 1.2 else None)
        concise = sender2 if verbose == sender1 else (sender1 if verbose == sender2 else None)
        
        personality_insights = []
        if chatterbox and listener:
            personality_insights.append(f'{chatterbox} is the chatterbox 😂 while {listener} is the patient listener 🤗')
        if verbose and concise:
            personality_insights.append(f'{verbose} writes detailed messages while {concise} keeps it brief')
        
        emoji_stats = self._analyze_emoji_personality(messages)
        emoji_king = emoji_stats.get('emoji_king', senders[0])
        personality_insights.append(f'{emoji_king} is the emoji king/queen 👑')
        
        top_3_things = []
        if abs(msg1 - msg2) < max(msg1, msg2) * 0.2:
            top_3_things.append('Perfectly balanced communication - you both contribute equally')
        else:
            top_3_things.append('Complementary communication styles - different but harmonious')
        
        affection_scores = self._calculate_affection_score(messages)['affection_scores']
        avg_affection = sum(affection_scores.values()) / len(affection_scores)
        if avg_affection > 5:
            top_3_things.append('High affection levels - lots of love and care in your messages')
        else:
            top_3_things.append('Steady friendship - consistent and reliable communication')
        
        time_analysis = self._analyze_time_patterns(messages)
        night_owl = time_analysis.get('night_owl', senders[0])
        if night_owl:
            top_3_things.append(f'Late night conversations - {night_owl} keeps the chat alive after hours')
        
        fun_title = f'{chatterbox} & {listener} - The Dynamic Duo' if chatterbox and listener else f'{senders[0]} & {senders[1]} - The Perfect Pair'
        
        summary_parts = []
        summary_parts.append(f'You two are {('best friends' if avg_affection > 3 else 'great friends')} with {sum(message_counts.values()):,} messages between you.')
        if personality_insights:
            summary_parts.append(' '.join(personality_insights[:2]))
        summary_parts.append('Your conversation shows a strong bond with meaningful interactions and shared moments.')
        
        return {
            'summary': ' '.join(summary_parts),
            'top_3_things': top_3_things,
            'fun_title': fun_title,
            'personality_insights': personality_insights
        }

    def _analyze_who_thinks_first(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {}
        try:
            daily_messages = defaultdict(list)
            for msg in messages:
                date_key = msg['timestamp'].strftime('%Y-%m-%d')
                daily_messages[date_key].append(msg)
            first_messages = {}
            daily_first_times = defaultdict(list)
            for date, day_messages in daily_messages.items():
                day_messages.sort(key=lambda x: x['timestamp'])
                first_msg = day_messages[0]
                first_messages[date] = {'sender': first_msg['sender'], 'time': first_msg['timestamp'].time().strftime('%H:%M:%S'), 'message': first_msg['message'][:50] + '...' if len(first_msg['message']) > 50 else first_msg['message']}
                daily_first_times[first_msg['sender']].append(first_msg['timestamp'].time())
            sender_first_counts = defaultdict(int)
            for date_data in first_messages.values():
                sender_first_counts[date_data['sender']] += 1
            total_days = len(first_messages)
            sender_percentages = {}
            for sender, count in sender_first_counts.items():
                sender_percentages[sender] = round(count / total_days * 100, 1) if total_days > 0 else 0
            avg_first_times = {}
            for sender, times in daily_first_times.items():
                if times:
                    minutes = [t.hour * 60 + t.minute for t in times]
                    avg_minutes = sum(minutes) / len(minutes)
                    avg_hour = int(avg_minutes // 60)
                    avg_minute = int(avg_minutes % 60)
                    avg_first_times[sender] = f'{avg_hour:02d}:{avg_minute:02d}'
            most_frequent_first = max(sender_first_counts.items(), key=lambda x: x[1])[0] if sender_first_counts else None
            insights = self._generate_who_thinks_first_insights(sender_percentages, avg_first_times, most_frequent_first)
            calendar_data = []
            for date, data in sorted(first_messages.items()):
                calendar_data.append({'date': date, 'sender': data['sender'], 'time': data['time'][:5], 'message_preview': data['message']})
            return {'daily_first_messages': dict(first_messages), 'sender_first_counts': dict(sender_first_counts), 'sender_percentages': sender_percentages, 'avg_first_times': avg_first_times, 'most_frequent_first': most_frequent_first, 'total_days_analyzed': total_days, 'calendar_data': calendar_data, 'insights': insights}
        except Exception as e:
            print(f'Error in _analyze_who_thinks_first: {e}')
            import traceback
            traceback.print_exc()
            return {}

    def _generate_who_thinks_first_insights(self, sender_percentages: Dict, avg_first_times: Dict, most_frequent: str) -> str:
        if not sender_percentages or not most_frequent:
            return 'Insufficient data to analyze thinking patterns.'
        senders = list(sender_percentages.keys())
        if len(senders) < 2:
            return f'{most_frequent} is the only participant, so they naturally start all conversations.'
        percentages = list(sender_percentages.values())
        max_percentage = max(percentages)
        min_percentage = min(percentages)
        other_sender = [s for s in senders if s != most_frequent][0]
        time_insights = []
        if most_frequent in avg_first_times and other_sender in avg_first_times:
            most_time = avg_first_times[most_frequent]
            other_time = avg_first_times[other_sender]
            most_hour = int(most_time.split(':')[0])
            other_hour = int(other_time.split(':')[0])
            if most_hour < other_hour - 2:
                time_insights.append(f'{most_frequent} typically starts conversations {most_time} while {other_sender} starts around {other_time} - {most_frequent} is clearly the early bird!')
            elif other_hour < most_hour - 2:
                time_insights.append(f'{other_sender} is the early riser, starting around {other_time} while {most_frequent} starts at {most_time}')
            else:
                time_insights.append(f'Both start around similar times - {most_frequent} at {most_time} and {other_sender} at {other_time}')
        if max_percentage > 70:
            insight = f'{most_frequent} starts {max_percentage:.0f}% of the days, showing they think about {other_sender} first most of the time.'
        elif max_percentage > 60:
            insight = f"{most_frequent} initiates conversations {max_percentage:.0f}% of the time, indicating they're usually the one thinking first."
        elif max_percentage > 55:
            insight = f'Pretty balanced! {most_frequent} starts {max_percentage:.0f}% of days while {other_sender} starts {100 - max_percentage:.0f}% - you both think about each other equally.'
        else:
            insight = f'Very balanced conversation starters - {most_frequent} and {other_sender} both initiate conversations regularly.'
        all_insights = [insight]
        if time_insights:
            all_insights.extend(time_insights)
        return ' '.join(all_insights)