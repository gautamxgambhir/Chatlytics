import os
import io
import json
import traceback
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image, ImageOps
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

class PDFExporter:

    def __init__(self, output_dir: str='uploads'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('CustomTitle', parent=self.styles['Title'], fontSize=24, spaceAfter=30, alignment=TA_CENTER, textColor=colors.HexColor('#1f2937'))
        self.heading_style = ParagraphStyle('CustomHeading', parent=self.styles['Heading2'], fontSize=16, spaceAfter=12, spaceBefore=20, textColor=colors.HexColor('#374151'))
        self.normal_style = ParagraphStyle('CustomNormal', parent=self.styles['Normal'], fontSize=10, spaceAfter=6, textColor=colors.HexColor('#4b5563'))
        self.small_style = ParagraphStyle('CustomSmall', parent=self.styles['Normal'], fontSize=9, spaceAfter=4, textColor=colors.HexColor('#6b7280'))
        self._tmp_images: List[str] = []

    def create_full_pdf(self, analytics: Dict[str, Any], ai_insights: Dict[str, Any], filename: str, session_id: str) -> Optional[str]:
        pdf_filename = os.path.join(self.output_dir, f'chatlytics_report_{session_id}.pdf')
        print('debug print (filname) :', pdf_filename)
        self._tmp_images = []
        try:
            doc = SimpleDocTemplate(pdf_filename, pagesize=A4, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
            story = []
            self._add_cover_page(story, filename, analytics)
            story.append(PageBreak())
            self._add_basic_stats_section(story, analytics)
            story.append(PageBreak())
            self._add_message_distribution_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_activity_patterns_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_response_sentiment_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_emoji_fun_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_love_compatibility_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_word_analysis_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_who_thinks_first_section(story, analytics, session_id)
            story.append(PageBreak())
            self._add_ai_insights_section(story, ai_insights)
            story.append(Spacer(1, 20))
            story.append(Paragraph('<i>Generated with Chatlytics - Your Personal Chat Analytics</i>', self.small_style))
            doc.build(story)
            if not os.path.exists(pdf_filename):
                raise Exception('PDF file was not created')
            file_size = os.path.getsize(pdf_filename)
            if file_size == 0:
                raise Exception('PDF file is empty')
            return os.path.abspath(pdf_filename)
        except Exception as e:
            print(f'PDF generation failed: {e}')
            traceback.print_exc()
            try:
                return self._create_fallback_pdf(pdf_filename, filename, str(e))
            except Exception as fallback_error:
                print(f'Fallback PDF creation also failed: {fallback_error}')
                return None
        finally:
            self._cleanup_temp_images()

    def _add_cover_page(self, story: List, filename: str, analytics: Dict[str, Any]):
        story.append(Paragraph('💬 Chatlytics', self.title_style))
        story.append(Paragraph('Personal Chat Analytics Report', ParagraphStyle('Subtitle', parent=self.styles['Normal'], fontSize=16, spaceAfter=30, alignment=TA_CENTER, textColor=colors.HexColor('#6b7280'))))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f'<b>Source File:</b> {filename}', self.normal_style))
        basic_stats = analytics.get('basic_stats', {})
        if basic_stats:
            story.append(Paragraph(f'<b>Participants:</b> {', '.join(basic_stats.get('senders', []))}', self.normal_style))
            story.append(Paragraph(f'<b>Total Messages:</b> {basic_stats.get('total_messages', 'N/A'):,}', self.normal_style))
            date_range = basic_stats.get('date_range', {})
            if date_range:
                story.append(Paragraph(f'<b>Date Range:</b> {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}', self.normal_style))
                story.append(Paragraph(f'<b>Duration:</b> {date_range.get('duration_days', 'N/A')} days', self.normal_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f'<i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>', self.small_style))

    def _add_basic_stats_section(self, story: List, analytics: Dict[str, Any]):
        story.append(Paragraph('📊 Basic Statistics', self.heading_style))
        basic_stats = analytics.get('basic_stats', {})
        if not basic_stats:
            story.append(Paragraph('No basic statistics available.', self.normal_style))
            return
        stats_data = [['Metric', 'Value'], ['Total Messages', f'{basic_stats.get('total_messages', 'N/A'):,}'], ['Participants', ', '.join(basic_stats.get('senders', []))], ['Date Range', f'{basic_stats.get('date_range', {}).get('start', 'N/A')} to {basic_stats.get('date_range', {}).get('end', 'N/A')}'], ['Duration', f'{basic_stats.get('date_range', {}).get('duration_days', 'N/A')} days']]
        message_counts = basic_stats.get('message_counts', {})
        if message_counts:
            for sender, count in message_counts.items():
                stats_data.append([f'Messages from {sender}', f'{count:,}'])
        word_counts = basic_stats.get('word_counts', {})
        if word_counts:
            for sender, count in word_counts.items():
                stats_data.append([f'Words from {sender}', f'{count:,}'])
        table = Table(stats_data, colWidths=[200, 300])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')), ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))]))
        story.append(table)

    def _add_message_distribution_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('📈 Message Distribution', self.heading_style))
        chart_path = self._create_message_distribution_chart(analytics, session_id)
        if chart_path:
            story.append(self._create_image_flowable(chart_path, 'Message distribution by participant'))
        basic_stats = analytics.get('basic_stats', {})
        message_counts = basic_stats.get('message_counts', {})
        word_counts = basic_stats.get('word_counts', {})
        if message_counts and word_counts:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Detailed Breakdown:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            total_messages = sum(message_counts.values())
            total_words = sum(word_counts.values())
            breakdown_data = [['Participant', 'Messages', 'Percentage', 'Words', 'Avg Words/Message']]
            for sender in message_counts.keys():
                msg_count = message_counts[sender]
                word_count = word_counts[sender]
                msg_percentage = msg_count / total_messages * 100 if total_messages > 0 else 0
                avg_words = word_count / msg_count if msg_count > 0 else 0
                breakdown_data.append([sender, f'{msg_count:,}', f'{msg_percentage:.1f}%', f'{word_count:,}', f'{avg_words:.1f}'])
            breakdown_table = Table(breakdown_data, colWidths=[100, 80, 80, 80, 100])
            breakdown_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, 0), 8), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')), ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))]))
            story.append(breakdown_table)

    def _add_activity_patterns_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('⏰ Activity Patterns', self.heading_style))
        timeline_chart = self._create_activity_timeline_chart(analytics, session_id)
        if timeline_chart:
            story.append(self._create_image_flowable(timeline_chart, 'Daily message activity over time'))
        heatmap_chart = self._create_hourly_heatmap_chart(analytics, session_id)
        if heatmap_chart:
            story.append(self._create_image_flowable(heatmap_chart, 'Hourly activity heatmap'))
        daily_chart = self._create_daily_activity_chart(analytics, session_id)
        if daily_chart:
            story.append(self._create_image_flowable(daily_chart, 'Activity by day of week'))

    def _add_response_sentiment_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('💬 Response Times & Sentiment', self.heading_style))
        response_chart = self._create_response_time_chart(analytics, session_id)
        if response_chart:
            story.append(self._create_image_flowable(response_chart, 'Response time distribution'))
        sentiment_data = analytics.get('sentiment_analysis', analytics.get('emotional_tone', {}))
        if sentiment_data:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Sentiment Analysis:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            if 'sentiment_percentages' in sentiment_data:
                sentiment_table_data = [['Participant', 'Positive', 'Negative', 'Neutral']]
                for sender, percentages in sentiment_data['sentiment_percentages'].items():
                    sentiment_table_data.append([sender, f'{percentages.get('positive', 0):.1f}%', f'{percentages.get('negative', 0):.1f}%', f'{percentages.get('neutral', 0):.1f}%'])
                sentiment_table = Table(sentiment_table_data, colWidths=[100, 80, 80, 80])
                sentiment_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, 0), 8), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')), ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))]))
                story.append(sentiment_table)

    def _add_emoji_fun_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('😊 Emojis & Fun Metrics', self.heading_style))
        emoji_chart = self._create_emoji_usage_chart(analytics, session_id)
        if emoji_chart:
            story.append(self._create_image_flowable(emoji_chart, 'Top emojis used in conversation'))
        fun_metrics = analytics.get('fun_metrics', {})
        if fun_metrics:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Fun Insights:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            insights = []
            if 'message_leader' in fun_metrics:
                insights.append(f'💬 {fun_metrics['message_leader']} is the message leader')
            if 'word_leader' in fun_metrics:
                insights.append(f'📝 {fun_metrics['word_leader']} uses the most words')
            if 'emoji_leader' in fun_metrics:
                insights.append(f'😊 {fun_metrics['emoji_leader']} is the emoji king/queen')
            if 'initiator_leader' in fun_metrics:
                insights.append(f'🚀 {fun_metrics['initiator_leader']} starts most conversations')
            if 'night_owl' in fun_metrics:
                insights.append(f'🦉 {fun_metrics['night_owl']} is the night owl')
            for insight in insights:
                story.append(Paragraph(insight, self.normal_style))

    def _add_love_compatibility_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('❤️ Love & Compatibility', self.heading_style))
        affection_chart = self._create_affection_score_gauge(analytics, session_id)
        if affection_chart:
            story.append(self._create_image_flowable(affection_chart, 'Affection/Love Score'))
        compatibility_chart = self._create_compatibility_gauge(analytics, session_id)
        if compatibility_chart:
            story.append(self._create_image_flowable(compatibility_chart, 'Compatibility Index'))
        affection_scores = analytics.get('affection_score', {})
        if isinstance(affection_scores, dict) and 'affection_scores' in affection_scores:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Affection Scores:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            for sender, score in affection_scores['affection_scores'].items():
                story.append(Paragraph(f'{sender}: {score:.1f}/100', self.normal_style))

    def _add_word_analysis_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('📝 Word Analysis', self.heading_style))
        wordcloud_path = self._create_wordcloud_image(analytics, session_id)
        if wordcloud_path:
            story.append(self._create_image_flowable(wordcloud_path, 'Word Cloud - Most used words'))
        word_analysis = analytics.get('word_analysis', analytics.get('keyword_tracker', {}))
        if word_analysis:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Top Words:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            top_words = {}
            if 'overall_common_words' in word_analysis:
                top_words = word_analysis['overall_common_words']
            elif 'common_words' in word_analysis:
                top_words = word_analysis['common_words']
            if top_words:
                word_data = [['Word', 'Count']]
                for word, count in list(top_words.items())[:20]:
                    word_data.append([word, str(count)])
                word_table = Table(word_data, colWidths=[200, 80])
                word_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, 0), 8), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')), ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))]))
                story.append(word_table)

    def _add_who_thinks_first_section(self, story: List, analytics: Dict[str, Any], session_id: str):
        story.append(Paragraph('🧠 Who Thinks First', self.heading_style))
        calendar_chart = self._create_who_thinks_first_calendar(analytics, session_id)
        if calendar_chart:
            story.append(self._create_image_flowable(calendar_chart, 'Who sends the first message each day'))
        bar_chart = self._create_who_thinks_first_bar(analytics, session_id)
        if bar_chart:
            story.append(self._create_image_flowable(bar_chart, 'Daily initiation counts'))
        who_thinks_first = analytics.get('who_thinks_first', {})
        if who_thinks_first and 'sender_percentages' in who_thinks_first:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Initiator Statistics:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            for sender, percentage in who_thinks_first['sender_percentages'].items():
                story.append(Paragraph(f'{sender}: {percentage:.1f}% of days', self.normal_style))

    def _add_ai_insights_section(self, story: List, ai_insights: Dict[str, Any]):
        story.append(Paragraph('🤖 AI-Powered Insights', self.heading_style))
        if not ai_insights:
            story.append(Paragraph('No AI insights available.', self.normal_style))
            return
        for key, value in ai_insights.items():
            if isinstance(value, str) and value.strip():
                title = key.replace('_', ' ').title()
                story.append(Paragraph(f'<b>{title}:</b>', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=6, textColor=colors.HexColor('#374151'))))
                story.append(Paragraph(value, self.normal_style))
                story.append(Spacer(1, 8))

    def _create_message_distribution_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            basic_stats = analytics.get('basic_stats', {})
            message_counts = basic_stats.get('message_counts', {})
            if not message_counts:
                return None
            fig = go.Figure(data=[go.Pie(labels=list(message_counts.keys()), values=list(message_counts.values()), hole=0.4, textinfo='label+percent', textfont_size=12)])
            fig.update_layout(title='Message Distribution by Participant', showlegend=True, height=400, font=dict(size=12))
            return self._save_plotly_fig(fig, f'msg_dist_{session_id}')
        except Exception as e:
            print(f'Error creating message distribution chart: {e}')
            return None

    def _create_activity_timeline_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            daily_activity = analytics.get('activity_patterns', {}).get('daily_activity', {})
            if not daily_activity:
                basic_stats = analytics.get('basic_stats', {})
                if 'date_range' in basic_stats:
                    return None
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(daily_activity.keys()), y=list(daily_activity.values()), mode='lines+markers', name='Daily Messages'))
            fig.update_layout(title='Daily Message Activity', xaxis_title='Date', yaxis_title='Messages', height=400)
            return self._save_plotly_fig(fig, f'timeline_{session_id}')
        except Exception as e:
            print(f'Error creating timeline chart: {e}')
            return None

    def _create_hourly_heatmap_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            time_analysis = analytics.get('time_analysis', {})
            sender_hourly = time_analysis.get('sender_hourly', {})
            if not sender_hourly:
                return None
            senders = list(sender_hourly.keys())
            hours = list(range(24))
            z_data = []
            for sender in senders:
                hourly_data = sender_hourly[sender]
                row = [hourly_data.get(str(hour), 0) for hour in hours]
                z_data.append(row)
            fig = go.Figure(data=go.Heatmap(z=z_data, x=hours, y=senders, colorscale='Blues'))
            fig.update_layout(title='Hourly Activity Heatmap', xaxis_title='Hour of Day', yaxis_title='Participant', height=400)
            return self._save_plotly_fig(fig, f'heatmap_{session_id}')
        except Exception as e:
            print(f'Error creating heatmap chart: {e}')
            return None

    def _create_daily_activity_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            time_analysis = analytics.get('time_analysis', {})
            daily_distribution = time_analysis.get('daily_distribution', {})
            if not daily_distribution:
                return None
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            values = [daily_distribution.get(day, 0) for day in days]
            fig = go.Figure(data=[go.Bar(x=days, y=values, marker_color='lightblue')])
            fig.update_layout(title='Activity by Day of Week', xaxis_title='Day', yaxis_title='Messages', height=400)
            return self._save_plotly_fig(fig, f'daily_{session_id}')
        except Exception as e:
            print(f'Error creating daily activity chart: {e}')
            return None

    def _create_response_time_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            response_analysis = analytics.get('response_time_analysis', {})
            avg_times = response_analysis.get('average_response_times', {})
            if not avg_times:
                return None
            fig = go.Figure(data=[go.Bar(x=list(avg_times.keys()), y=list(avg_times.values()), marker_color='lightcoral')])
            fig.update_layout(title='Average Response Times', xaxis_title='Participant', yaxis_title='Minutes', height=400)
            return self._save_plotly_fig(fig, f'response_{session_id}')
        except Exception as e:
            print(f'Error creating response time chart: {e}')
            return None

    def _create_emoji_usage_chart(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            emoji_stats = analytics.get('emoji_personality', analytics.get('emoji_stats', {}))
            top_emojis = emoji_stats.get('top_emojis', {})
            if not top_emojis:
                return None
            sorted_emojis = sorted(top_emojis.items(), key=lambda x: x[1], reverse=True)[:10]
            if not sorted_emojis:
                return None
            emojis, counts = zip(*sorted_emojis)
            fig = go.Figure(data=[go.Bar(x=list(emojis), y=list(counts), marker_color='lightgreen')])
            fig.update_layout(title='Top Emojis Used', xaxis_title='Emoji', yaxis_title='Count', height=400)
            return self._save_plotly_fig(fig, f'emoji_{session_id}')
        except Exception as e:
            print(f'Error creating emoji chart: {e}')
            return None

    def _create_affection_score_gauge(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            affection_score = analytics.get('affection_score', {})
            if isinstance(affection_score, dict):
                scores = affection_score.get('affection_scores', {})
                if scores:
                    avg_score = sum(scores.values()) / len(scores) if scores else 0
                else:
                    avg_score = 0
            else:
                avg_score = float(affection_score) if affection_score else 0
            fig = go.Figure(go.Indicator(mode='gauge+number', value=avg_score, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': 'Affection Score'}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': 'darkblue'}, 'steps': [{'range': [0, 25], 'color': 'lightgray'}, {'range': [25, 50], 'color': 'yellow'}, {'range': [50, 75], 'color': 'orange'}, {'range': [75, 100], 'color': 'red'}], 'threshold': {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 90}}))
            fig.update_layout(height=400)
            return self._save_plotly_fig(fig, f'affection_{session_id}')
        except Exception as e:
            print(f'Error creating affection gauge: {e}')
            return None

    def _create_compatibility_gauge(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            compatibility = analytics.get('compatibility_index', {})
            score = compatibility.get('score', 50) if isinstance(compatibility, dict) else 50
            fig = go.Figure(go.Indicator(mode='gauge+number', value=score, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': 'Compatibility Index'}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': 'darkgreen'}, 'steps': [{'range': [0, 25], 'color': 'lightgray'}, {'range': [25, 50], 'color': 'yellow'}, {'range': [50, 75], 'color': 'lightgreen'}, {'range': [75, 100], 'color': 'green'}], 'threshold': {'line': {'color': 'green', 'width': 4}, 'thickness': 0.75, 'value': 85}}))
            fig.update_layout(height=400)
            return self._save_plotly_fig(fig, f'compatibility_{session_id}')
        except Exception as e:
            print(f'Error creating compatibility gauge: {e}')
            return None

    def _create_wordcloud_image(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            if not WORDCLOUD_AVAILABLE:
                return None
            word_analysis = analytics.get('word_analysis', analytics.get('keyword_tracker', {}))
            top_words = word_analysis.get('overall_common_words', {})
            if not top_words:
                return None
            text = ' '.join([word for word, count in top_words.items() for _ in range(min(count, 10))])
            if not text.strip():
                return None
            wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100, colormap='viridis').generate(text)
            temp_path = os.path.join(tempfile.gettempdir(), f'wordcloud_{session_id}.png')
            wordcloud.to_file(temp_path)
            self._tmp_images.append(temp_path)
            return temp_path
        except Exception as e:
            print(f'Error creating wordcloud: {e}')
            return None

    def _create_who_thinks_first_calendar(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            who_thinks_first = analytics.get('who_thinks_first', {})
            calendar_data = who_thinks_first.get('calendar_data', [])
            if not calendar_data:
                return None
            dates = [item['date'] for item in calendar_data]
            senders = [item['sender'] for item in calendar_data]
            fig = go.Figure(data=[go.Scatter(x=dates, y=senders, mode='markers', marker=dict(size=8, color='blue'))])
            fig.update_layout(title='Who Thinks First - Calendar View', xaxis_title='Date', yaxis_title='Participant', height=400)
            return self._save_plotly_fig(fig, f'who_first_cal_{session_id}')
        except Exception as e:
            print(f'Error creating who thinks first calendar: {e}')
            return None

    def _create_who_thinks_first_bar(self, analytics: Dict[str, Any], session_id: str) -> Optional[str]:
        try:
            who_thinks_first = analytics.get('who_thinks_first', {})
            sender_counts = who_thinks_first.get('sender_first_counts', {})
            if not sender_counts:
                return None
            fig = go.Figure(data=[go.Bar(x=list(sender_counts.keys()), y=list(sender_counts.values()), marker_color='lightblue')])
            fig.update_layout(title='Who Thinks First - Daily Counts', xaxis_title='Participant', yaxis_title='Days', height=400)
            return self._save_plotly_fig(fig, f'who_first_bar_{session_id}')
        except Exception as e:
            print(f'Error creating who thinks first bar chart: {e}')
            return None

    def _save_plotly_fig(self, fig: go.Figure, basename: str) -> Optional[str]:
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f'{basename}.png')
            try:
                fig.write_image(temp_path, format='png', engine='kaleido', scale=2)
            except Exception:
                fig.write_image(temp_path, format='png', scale=2)
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self._tmp_images.append(temp_path)
                return temp_path
            return None
        except Exception as e:
            print(f'Error saving plotly figure: {e}')
            return None

    def _create_image_flowable(self, img_path: str, caption: str=None) -> KeepTogether:
        try:
            with Image.open(img_path) as img:
                max_width = 6 * inch
                max_height = 4 * inch
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                resized_path = img_path.replace('.png', '_resized.png')
                img.save(resized_path)
                self._tmp_images.append(resized_path)
                rl_img = RLImage(resized_path, width=img.width * 0.75, height=img.height * 0.75)
                parts = [rl_img]
                if caption:
                    parts.append(Paragraph(f'<i>{caption}</i>', self.small_style))
                parts.append(Spacer(1, 8))
                return KeepTogether(parts)
        except Exception as e:
            print(f'Error creating image flowable: {e}')
            return Paragraph('Image could not be loaded', self.normal_style)

    def _create_fallback_pdf(self, pdf_path: str, filename: str, error_msg: str) -> Optional[str]:
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            story.append(Paragraph('Chatlytics Report', self.title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f'Source: {filename}', self.normal_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph('The detailed report could not be generated due to an error.', self.normal_style))
            story.append(Paragraph(f'Error: {error_msg}', self.small_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph('Please try again or contact support if the issue persists.', self.normal_style))
            doc.build(story)
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                return os.path.abspath(pdf_path)
            return None
        except Exception as e:
            print(f'Fallback PDF creation failed: {e}')
            return None

    def _cleanup_temp_images(self):
        for img_path in self._tmp_images:
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass
        self._tmp_images = []