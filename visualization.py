import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
from collections import Counter, defaultdict
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class ChartGenerator:

    def __init__(self):
        self.color_palette = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

    def _apply_base_layout(self, fig: 'go.Figure', title: str=None, xaxis_title: str=None, yaxis_title: str=None, height: int=400):
        fig.update_layout(template='plotly_white', title={'text': title, 'x': 0.5, 'font': {'size': 16}} if title else None, height=height, font=dict(family='Inter, system-ui, sans-serif', size=12, color='#111827'), margin=dict(l=40, r=20, t=60, b=40), hoverlabel=dict(bgcolor='white', font_size=12, font_family='Inter, system-ui, sans-serif'), legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5), xaxis=dict(title=xaxis_title, gridcolor='#e5e7eb', zerolinecolor='#e5e7eb'), yaxis=dict(title=yaxis_title, gridcolor='#e5e7eb', zerolinecolor='#e5e7eb'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    def generate_charts(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return {}
        charts = {}
        try:
            charts['message_distribution'] = self._create_message_distribution_chart(messages)
            charts['word_count'] = self._create_word_count_chart(messages)
            charts['activity_timeline'] = self._create_activity_timeline_chart(messages)
            charts['hourly_heatmap'] = self._create_hourly_heatmap_chart(messages)
            charts['daily_activity'] = self._create_daily_activity_chart(messages)
            charts['emoji_usage'] = self._create_emoji_usage_chart(messages)
            charts['response_times'] = self._create_response_time_chart(messages)
            charts['message_length'] = self._create_message_length_chart(messages)
            charts['mood_timeline'] = self._create_mood_timeline_chart(messages)
            charts['affection_score_gauge'] = self._create_affection_score_gauge(messages)
            charts['compatibility_meter'] = self._create_compatibility_meter(messages)
            charts['wordcloud_data'] = self._create_wordcloud_data(messages)
            charts['streaks_gaps_timeline'] = self._create_streaks_gaps_timeline(messages)
            charts['who_thinks_first_calendar'] = self._create_who_thinks_first_calendar(messages)
            charts['who_thinks_first_bar'] = self._create_who_thinks_first_bar_chart(messages)
        except Exception as e:
            print(f'Chart generation error: {e}')
        return charts

    def _create_message_distribution_chart(self, messages: List[Dict[str, Any]]) -> str:
        sender_counts = Counter((msg['sender'] for msg in messages))
        total = sum(sender_counts.values())
        percentages = {sender: count / total * 100 for sender, count in sender_counts.items()}
        labels = [f'{sender}<br>{count:,} messages ({percentages[sender]:.1f}%)' for sender, count in sender_counts.items()]
        fig = go.Figure(data=[go.Pie(labels=labels, values=list(sender_counts.values()), hole=0.4, marker_colors=self.color_palette[:len(sender_counts)], textinfo='label', textfont_size=12, hovertemplate='<b>%{label}</b><br>Messages: %{value}<extra></extra>')])
        self._apply_base_layout(fig, title='Who Sends More Messages?', height=400)
        fig.update_layout(showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5))
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_word_count_chart(self, messages: List[Dict[str, Any]]) -> str:
        sender_word_counts = {}
        sender_msg_counts = Counter((msg['sender'] for msg in messages))
        for msg in messages:
            sender = msg['sender']
            word_count = len(msg['message'].split())
            sender_word_counts[sender] = sender_word_counts.get(sender, 0) + word_count
        avg_words_per_msg = {sender: word_count / sender_msg_counts[sender] for sender, word_count in sender_word_counts.items()}
        hover_text = [f'{sender}<br>Total Words: {sender_word_counts[sender]:,}<br>Average per Message: {avg_words_per_msg[sender]:.1f} words' for sender in sender_word_counts.keys()]
        fig = go.Figure(data=[go.Bar(x=list(sender_word_counts.keys()), y=list(sender_word_counts.values()), marker_color=self.color_palette[:len(sender_word_counts)], text=[f'{count:,} words' for count in sender_word_counts.values()], textposition='auto', hovertemplate='%{customdata}<extra></extra>', customdata=hover_text)])
        self._apply_base_layout(fig, title='Who Uses More Words?', xaxis_title='Participant', yaxis_title='Total Words', height=400)
        fig.update_xaxes(categoryorder='total descending')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_activity_timeline_chart(self, messages: List[Dict[str, Any]]) -> str:
        daily_counts = {}
        for msg in messages:
            date = msg['timestamp'].date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        sorted_dates = sorted(daily_counts.keys())
        counts = [daily_counts[date] for date in sorted_dates]
        max_count = max(counts) if counts else 0
        max_date = sorted_dates[counts.index(max_count)] if counts else None
        fig = go.Figure(data=[go.Scatter(x=sorted_dates, y=counts, mode='lines+markers', line=dict(color=self.color_palette[0], width=3), marker=dict(size=6, color=self.color_palette[0]), fill='tozeroy', fillcolor='rgba(59,130,246,0.15)', hovertemplate='<b>%{x}</b><br>Messages: %{y}<br><extra></extra>', name='Daily Messages')])
        if max_date:
            fig.add_annotation(x=max_date, y=max_count, text=f'Peak Day!<br>{max_count} messages', showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor=self.color_palette[1], font=dict(size=12, color=self.color_palette[1]))
        self._apply_base_layout(fig, title='Conversation Timeline', xaxis_title='Date', yaxis_title='Messages per Day', height=400)
        fig.update_layout(hovermode='x unified')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_hourly_heatmap_chart(self, messages: List[Dict[str, Any]]) -> str:
        hourly_data = defaultdict(lambda: [0] * 24)
        senders = list(set((msg['sender'] for msg in messages)))
        for msg in messages:
            sender = msg['sender']
            hour = msg['timestamp'].hour
            hourly_data[sender][hour] += 1
        fig = go.Figure(data=go.Heatmap(z=[hourly_data[sender] for sender in senders], x=list(range(24)), y=senders, colorscale='Blues', colorbar=dict(title='Messages')))
        self._apply_base_layout(fig, title='Hourly Activity Heatmap', xaxis_title='Hour of Day', yaxis_title='Participant', height=400)
        fig.update_yaxes(autorange='reversed')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_daily_activity_chart(self, messages: List[Dict[str, Any]]) -> str:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_counts = {day: 0 for day in days}
        for msg in messages:
            day = msg['timestamp'].strftime('%A')
            daily_counts[day] += 1
        fig = go.Figure(data=[go.Bar(x=days, y=[daily_counts[day] for day in days], marker_color=self.color_palette[1], hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>')])
        self._apply_base_layout(fig, title='Activity by Day', xaxis_title='Day of Week', yaxis_title='Messages', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_emoji_usage_chart(self, messages: List[Dict[str, Any]]) -> str:
        import re
        emoji_pattern = re.compile('[\\U0001F600-\\U0001F64F\\U0001F300-\\U0001F5FF\\U0001F680-\\U0001F6FF\\U0001F1E0-\\U0001F1FF\\U00002702-\\U000027B0\\U000024C2-\\U0001F251]+')
        emoji_counts = Counter()
        total_emojis = 0
        for msg in messages:
            emojis = emoji_pattern.findall(msg['message'])
            emoji_counts.update(emojis)
            total_emojis += len(emojis)
        top_emojis = emoji_counts.most_common(10)
        if not top_emojis:
            fig = go.Figure()
            fig.add_annotation(text='No emoji usage detected in this conversation.', xref='paper', yref='paper', x=0.5, y=0.5, xanchor='center', yanchor='middle', font=dict(size=16, color='gray'), showarrow=False)
            self._apply_base_layout(fig, title='Top Emojis', height=400)
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            return json.dumps(fig, cls=PlotlyJSONEncoder)
        percentages = [count / total_emojis * 100 for emoji, count in top_emojis]
        fig = go.Figure(data=[go.Bar(x=[emoji for emoji, count in top_emojis], y=[count for emoji, count in top_emojis], marker_color=self.color_palette[:len(top_emojis)], text=[f'{count}<br>({pct:.1f}%)' for (emoji, count), pct in zip(top_emojis, percentages)], textposition='auto', hovertemplate='<b>%{x}</b><br>Used %{y} times<br>%{customdata:.1f}% of all emojis<extra></extra>', customdata=percentages)])
        self._apply_base_layout(fig, title='Top Emojis', xaxis_title='Emoji', yaxis_title='Times Used', height=400)
        fig.update_xaxes(tickfont=dict(size=20))
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_response_time_chart(self, messages: List[Dict[str, Any]]) -> str:
        response_times = defaultdict(list)
        response_distribution = defaultdict(lambda: {'instant': 0, 'fast': 0, 'medium': 0, 'slow': 0, 'delivered': 0})
        for i in range(1, len(messages)):
            prev_msg = messages[i - 1]
            curr_msg = messages[i]
            if prev_msg['sender'] != curr_msg['sender']:
                time_diff = (curr_msg['timestamp'] - prev_msg['timestamp']).total_seconds() / 60
                if 0 < time_diff < 10080:
                    response_times[curr_msg['sender']].append(time_diff)
                    if time_diff < 1:
                        response_distribution[curr_msg['sender']]['instant'] += 1
                    elif time_diff < 15:
                        response_distribution[curr_msg['sender']]['fast'] += 1
                    elif time_diff < 60:
                        response_distribution[curr_msg['sender']]['medium'] += 1
                    elif time_diff < 1440:
                        response_distribution[curr_msg['sender']]['slow'] += 1
                    else:
                        response_distribution[curr_msg['sender']]['delivered'] += 1
        if not response_times:
            fig = go.Figure()
            fig.add_annotation(text='No response time data available.', xref='paper', yref='paper', x=0.5, y=0.5, xanchor='center', yanchor='middle', font=dict(size=16, color='gray'), showarrow=False)
            self._apply_base_layout(fig, title='Response Time Analysis', height=400)
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            return json.dumps(fig, cls=PlotlyJSONEncoder)
        senders = list(response_times.keys())
        categories = ['Instant (<1min)', 'Fast (1-15min)', 'Medium (15-60min)', 'Slow (1-24hr)', 'Delivered (>24hr)']
        colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
        fig = go.Figure()
        for i, sender in enumerate(senders):
            dist = response_distribution[sender]
            total = sum(dist.values())
            if total > 0:
                values = [dist['instant'] / total * 100, dist['fast'] / total * 100, dist['medium'] / total * 100, dist['slow'] / total * 100, dist['delivered'] / total * 100]
                fig.add_trace(go.Bar(name=sender, x=categories, y=values, marker_color=colors, text=[f'{v:.1f}%' for v in values], textposition='auto', hovertemplate=f'<b>{sender}</b><br>%{{x}}: %{{y:.1f}}%<br>Count: %{{customdata}}<extra></extra>', customdata=[dist['instant'], dist['fast'], dist['medium'], dist['slow'], dist['delivered']], offsetgroup=i))
        avg_times = {sender: round(sum(times) / len(times), 1) for sender, times in response_times.items() if times}
        subtitle = ' | '.join([f'{sender}: {time}min avg' for sender, time in avg_times.items()])
        self._apply_base_layout(fig, title=f"Response Time Distribution<br><span style='font-size: 12px;'>{subtitle}</span>", xaxis_title='Response Speed Category', yaxis_title='Percentage', height=400)
        fig.update_layout(barmode='group')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_message_length_chart(self, messages: List[Dict[str, Any]]) -> str:
        sender_lengths = defaultdict(list)
        for msg in messages:
            length = len(msg['message'].split())
            sender_lengths[msg['sender']].append(length)
        fig = go.Figure()
        for i, (sender, lengths) in enumerate(sender_lengths.items()):
            fig.add_trace(go.Box(y=lengths, name=sender, marker_color=self.color_palette[i % len(self.color_palette)]))
        self._apply_base_layout(fig, title='Message Length Distribution', xaxis_title=None, yaxis_title='Words', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_mood_timeline_chart(self, messages: List[Dict[str, Any]]) -> str:
        daily_mood = defaultdict(lambda: {'positive': 0, 'negative': 0})
        positive_words = ['love', 'great', 'awesome', 'happy', 'good', 'amazing', 'wonderful']
        negative_words = ['hate', 'bad', 'sad', 'angry', 'terrible', 'awful', 'upset']
        for msg in messages:
            date = msg['timestamp'].date()
            words = msg['message'].lower().split()
            pos_count = sum((1 for word in words if word in positive_words))
            neg_count = sum((1 for word in words if word in negative_words))
            daily_mood[date]['positive'] += pos_count
            daily_mood[date]['negative'] += neg_count
        dates = sorted(daily_mood.keys())
        pos_scores = [daily_mood[date]['positive'] for date in dates]
        neg_scores = [daily_mood[date]['negative'] for date in dates]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=pos_scores, mode='lines', name='Positive', line_color='green'))
        fig.add_trace(go.Scatter(x=dates, y=neg_scores, mode='lines', name='Negative', line_color='red'))
        self._apply_base_layout(fig, title='Mood Timeline', xaxis_title='Date', yaxis_title='Score', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_affection_score_gauge(self, messages: List[Dict[str, Any]]) -> str:
        affection_words = {'love', 'heart', 'kiss', 'hug', 'miss', 'care', 'sweet', 'cute', 'dear', 'honey', 'baby', 'darling', 'sweetheart', 'beautiful', 'handsome', 'adorable'}
        total_score = 0
        emoji_affection = 0
        for msg in messages:
            words = msg['message'].lower().split()
            total_score += sum((1 for word in words if word in affection_words))
            emoji_affection += msg['message'].count('❤️') + msg['message'].count('💕') + msg['message'].count('😘') + msg['message'].count('💗')
        word_score = total_score / len(messages) * 50 if messages else 0
        emoji_score = emoji_affection / len(messages) * 50 if messages else 0
        final_score = min(100, word_score + emoji_score)
        fig = go.Figure(go.Indicator(mode='gauge+number+delta', value=final_score, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': 'Love/Affection Score', 'font': {'size': 20, 'color': '#1f2937'}}, number={'font': {'size': 48, 'color': '#1f2937'}}, delta={'reference': 50}, gauge={'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#374151'}, 'bar': {'color': '#ec4899', 'thickness': 0.8}, 'bgcolor': 'white', 'borderwidth': 2, 'bordercolor': '#e5e7eb', 'steps': [{'range': [0, 25], 'color': '#fee2e2'}, {'range': [25, 50], 'color': '#fecaca'}, {'range': [50, 75], 'color': '#fca5a5'}, {'range': [75, 100], 'color': '#f87171'}], 'threshold': {'line': {'color': '#dc2626', 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        fig.update_layout(template='plotly_white', height=400, margin=dict(l=20, r=20, t=80, b=20), font=dict(family='Inter, system-ui, sans-serif', color='#1f2937'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_compatibility_meter(self, messages: List[Dict[str, Any]]) -> str:
        senders = list(set((msg['sender'] for msg in messages)))
        if len(senders) < 2:
            score = 75
        else:
            msg_counts = Counter((msg['sender'] for msg in messages))
            balance = 1 - abs(msg_counts[senders[0]] - msg_counts[senders[1]]) / max(msg_counts.values())
            balance_score = balance * 30
            response_times = []
            for i in range(1, len(messages)):
                if messages[i - 1]['sender'] != messages[i]['sender']:
                    time_diff = (messages[i]['timestamp'] - messages[i - 1]['timestamp']).total_seconds() / 60
                    if 0 < time_diff < 1440:
                        response_times.append(time_diff)
            response_score = min(25, len(response_times) / len(messages) * 50) if messages else 10
            emoji_score = 15
            activity_score = 20
            score = min(100, balance_score + response_score + emoji_score + activity_score)
        fig = go.Figure(go.Indicator(mode='gauge+number+delta', value=score, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': 'Compatibility Index', 'font': {'size': 20, 'color': '#1f2937'}}, number={'font': {'size': 48, 'color': '#1f2937'}}, delta={'reference': 50}, gauge={'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#374151'}, 'bar': {'color': '#3b82f6', 'thickness': 0.8}, 'bgcolor': 'white', 'borderwidth': 2, 'bordercolor': '#e5e7eb', 'steps': [{'range': [0, 25], 'color': '#dbeafe'}, {'range': [25, 50], 'color': '#bfdbfe'}, {'range': [50, 75], 'color': '#93c5fd'}, {'range': [75, 100], 'color': '#60a5fa'}], 'threshold': {'line': {'color': '#1d4ed8', 'width': 4}, 'thickness': 0.75, 'value': 85}}))
        fig.update_layout(template='plotly_white', height=400, margin=dict(l=20, r=20, t=80, b=20), font=dict(family='Inter, system-ui, sans-serif', color='#1f2937'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_wordcloud_data(self, messages: List[Dict[str, Any]]) -> str:
        from collections import Counter
        import re
        all_words = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        for msg in messages:
            words = re.findall('\\b[a-zA-Z]{3,}\\b', msg['message'].lower())
            all_words.extend([word for word in words if word not in stop_words])
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(50)
        if not top_words:
            top_words = [('No words found', 1)]
        words, counts = zip(*top_words)
        max_count = max(counts) if counts else 1
        return json.dumps({'words': list(words), 'counts': list(counts), 'max_count': max_count})

    def _create_streaks_gaps_timeline(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return json.dumps(go.Figure().add_annotation(text='No data available'), cls=PlotlyJSONEncoder)
        daily_activity = {}
        for msg in messages:
            date = msg['timestamp'].date()
            daily_activity[date] = daily_activity.get(date, 0) + 1
        dates = sorted(daily_activity.keys())
        activities = [daily_activity[date] for date in dates]
        fig = go.Figure(data=go.Scatter(x=dates, y=activities, mode='lines+markers', fill='tozeroy', line=dict(color=self.color_palette[2], width=2), hovertemplate='<b>%{x}</b><br>Messages: %{y}<extra></extra>'))
        self._apply_base_layout(fig, title='Communication Streaks & Gaps', xaxis_title='Date', yaxis_title='Messages', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_who_thinks_first_calendar(self, messages: List[Dict[str, Any]]) -> str:
        daily_first = {}
        current_date = None
        for msg in messages:
            date = msg['timestamp'].date()
            if date != current_date:
                daily_first[date] = msg['sender']
                current_date = date
        if not daily_first:
            return json.dumps(go.Figure().add_annotation(text='No data available'), cls=PlotlyJSONEncoder)
        dates = list(daily_first.keys())
        senders = list(daily_first.values())
        fig = go.Figure(data=go.Scatter(x=dates, y=senders, mode='markers', marker=dict(size=10, color=self.color_palette[0])))
        self._apply_base_layout(fig, title='Who Thinks First - Calendar View', xaxis_title='Date', yaxis_title='Participant', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _create_who_thinks_first_bar_chart(self, messages: List[Dict[str, Any]]) -> str:
        daily_first = {}
        sender_counts = defaultdict(int)
        current_date = None
        for msg in messages:
            date = msg['timestamp'].date()
            if date != current_date:
                daily_first[date] = msg['sender']
                sender_counts[msg['sender']] += 1
                current_date = date
        if not sender_counts:
            sender_counts = {'No data': 0}
        fig = go.Figure(data=[go.Bar(x=list(sender_counts.keys()), y=list(sender_counts.values()), marker_color=self.color_palette, hovertemplate='<b>%{x}</b><br>Days first: %{y}<extra></extra>')])
        self._apply_base_layout(fig, title='Who Thinks First - Daily Counts', xaxis_title='Participant', yaxis_title='Days', height=400)
        return json.dumps(fig, cls=PlotlyJSONEncoder)