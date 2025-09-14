import os
import io
import json
import traceback
import tempfile
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
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

logger = logging.getLogger(__name__)

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
        logger.info(f'Creating PDF report: {pdf_filename}')
        self._tmp_images = []
        
        if not analytics or not isinstance(analytics, dict):
            logger.error('Invalid analytics data provided')
            return self._create_fallback_pdf(pdf_filename, filename, 'Invalid analytics data')
        
        try:
            doc = SimpleDocTemplate(
                pdf_filename, 
                pagesize=A4, 
                leftMargin=0.75 * inch, 
                rightMargin=0.75 * inch, 
                topMargin=0.75 * inch, 
                bottomMargin=0.75 * inch
            )
            story = []
            
            logger.info('Adding cover page...')
            self._add_cover_page(story, filename, analytics)
            story.append(PageBreak())
            
            story.append(Paragraph('Chat Analysis Report', ParagraphStyle('ReportTitle', parent=self.styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.HexColor('#1f2937'))))
            story.append(Spacer(1, 12))
            
            sections = [
                ('Basic Statistics', self._add_basic_stats_section),
                ('Message Distribution', self._add_message_distribution_section),
                ('Activity Patterns', self._add_activity_patterns_section),
                ('Response Times & Sentiment', self._add_response_sentiment_section),
                ('Emojis & Fun Metrics', self._add_emoji_fun_section),
                ('Love & Compatibility', self._add_love_compatibility_section),
                ('Word Analysis', self._add_word_analysis_section),
                ('Who Thinks First', self._add_who_thinks_first_section),
                ('AI Insights', self._add_ai_insights_section)
            ]
            
            sections_added = 0
            for section_name, section_method in sections:
                try:
                    logger.info(f'Adding {section_name} section...')
                    section_start_length = len(story)
                    
                    if section_name == 'AI Insights':
                        section_method(story, ai_insights or {})
                    elif section_name == 'Basic Statistics':
                        section_method(story, analytics)
                    else:
                        section_method(story, analytics, session_id)
                    
                    if len(story) > section_start_length:
                        sections_added += 1
                        story.append(PageBreak())
                    else:
                        story.append(Paragraph(f'{section_name}', self.heading_style))
                        story.append(Paragraph('This section contains the analysis results.', self.normal_style))
                        story.append(PageBreak())
                        sections_added += 1
                        
                except Exception as e:
                    logger.error(f'Error adding {section_name} section: {e}')
                    story.append(Paragraph(f'{section_name}', self.heading_style))
                    story.append(Paragraph(f'{section_name} section could not be generated due to an error.', self.normal_style))
                    story.append(Spacer(1, 10))
                    story.append(PageBreak())
                    sections_added += 1
            
            if sections_added == 0:
                story.append(Paragraph('Analytics Report', self.heading_style))
                story.append(Paragraph('Your chat analysis is being processed. Some sections may not be available at this time.', self.normal_style))
                story.append(Spacer(1, 20))
            
            story.append(Spacer(1, 20))
            story.append(Paragraph('<i>Generated with Chatlytics - Your Personal Chat Analytics</i>', self.small_style))
            
            logger.info('Building PDF document...')
            doc.build(story)
            
            if not os.path.exists(pdf_filename):
                raise Exception('PDF file was not created')
            
            file_size = os.path.getsize(pdf_filename)
            if file_size == 0:
                raise Exception('PDF file is empty')
                
            logger.info(f'PDF created successfully: {pdf_filename} ({file_size} bytes)')
            return os.path.abspath(pdf_filename)
            
        except Exception as e:
            logger.error(f'PDF generation failed: {e}')
            logger.error(traceback.format_exc())
            try:
                return self._create_fallback_pdf(pdf_filename, filename, str(e))
            except Exception as fallback_error:
                logger.error(f'Fallback PDF creation also failed: {fallback_error}')
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
        
        stats_data = [['Metric', 'Value']]
        
        total_messages = basic_stats.get('total_messages', 0)
        stats_data.append(['Total Messages', f'{total_messages:,}' if total_messages > 0 else 'No data'])
        
        senders = basic_stats.get('senders', [])
        if senders:
            stats_data.append(['Participants', ', '.join(senders)])
        else:
            stats_data.append(['Participants', 'Not available'])
            
        date_range = basic_stats.get('date_range', {})
        if date_range and date_range.get('start') and date_range.get('end'):
            stats_data.append(['Date Range', f"{date_range.get('start')} to {date_range.get('end')}"])
            duration = date_range.get('duration_days', 0)
            stats_data.append(['Duration', f'{duration} days' if duration > 0 else 'Less than 1 day'])
        else:
            stats_data.append(['Date Range', 'Not available'])
            
        message_counts = basic_stats.get('message_counts', {})
        if message_counts and isinstance(message_counts, dict):
            for sender, count in message_counts.items():
                if isinstance(sender, str) and isinstance(count, (int, float)):
                    stats_data.append([f'Messages from {sender}', f'{int(count):,}'])
        
        word_counts = basic_stats.get('word_counts', {})
        if word_counts and isinstance(word_counts, dict):
            for sender, count in word_counts.items():
                if isinstance(sender, str) and isinstance(count, (int, float)):
                    stats_data.append([f'Words from {sender}', f'{int(count):,}'])
        
        if len(stats_data) <= 1: 
            stats_data.append(['Status', 'Analysis in progress'])
            stats_data.append(['Data', 'Please check back later'])
        
        try:
            table = Table(stats_data, colWidths=[200, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
            story.append(table)
        except Exception as e:
            logger.error(f'Error creating basic stats table: {e}')
            for row in stats_data[1:]: 
                story.append(Paragraph(f'<b>{row[0]}:</b> {row[1]}', self.normal_style))

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
        
        try:
            wordcloud_path = self._create_wordcloud_image(analytics, session_id)
            if wordcloud_path:
                story.append(self._create_image_flowable(wordcloud_path, 'Word Cloud - Most used words'))
            else:
                story.append(Paragraph('Word cloud could not be generated.', self.normal_style))
        except Exception as e:
            logger.error(f'Error creating word cloud: {e}')
            story.append(Paragraph('Word cloud could not be generated.', self.normal_style))
        
        word_analysis = analytics.get('word_analysis', analytics.get('keyword_tracker', {}))
        
        if word_analysis:
            story.append(Spacer(1, 10))
            story.append(Paragraph('Top Words:', ParagraphStyle('SubHeading', parent=self.styles['Normal'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#374151'))))
            
            top_words = {}
            if isinstance(word_analysis, dict):
                if 'overall_common_words' in word_analysis:
                    top_words = word_analysis['overall_common_words']
                elif 'common_words' in word_analysis:
                    top_words = word_analysis['common_words']
                elif 'sender_common_words' in word_analysis:
                    all_words = {}
                    for sender_words in word_analysis['sender_common_words'].values():
                        if isinstance(sender_words, dict):
                            for word, count in sender_words.items():
                                all_words[word] = all_words.get(word, 0) + count
                    top_words = dict(sorted(all_words.items(), key=lambda x: x[1], reverse=True)[:30])
            
            if top_words and isinstance(top_words, dict):
                try:
                    word_data = [['Word', 'Count']]
                    valid_words = [(word, count) for word, count in top_words.items() 
                                   if isinstance(word, str) and isinstance(count, (int, float)) and word.strip()]
                    
                    for word, count in valid_words[:20]:
                        word_data.append([str(word).strip(), str(int(count))])
                    
                    if len(word_data) > 1:
                        word_table = Table(word_data, colWidths=[200, 80])
                        word_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
                        ]))
                        story.append(word_table)
                    else:
                        story.append(Paragraph('No valid word data available.', self.normal_style))
                except Exception as e:
                    logger.error(f'Error creating word table: {e}')
                    story.append(Paragraph('Word analysis table could not be generated.', self.normal_style))
            else:
                story.append(Paragraph('No word frequency data available.', self.normal_style))
        else:
            story.append(Paragraph('Word analysis data not available.', self.normal_style))

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
            
            if not message_counts or not isinstance(message_counts, dict):
                logger.warning('No message counts data available for pie chart')
                return None
                
            labels = list(message_counts.keys())
            values = list(message_counts.values())
            
            if not labels or not values or sum(values) == 0:
                logger.warning('Invalid or empty message counts data')
                return None
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.3,
                textinfo='label+percent',
                textfont_size=12,
                marker=dict(
                    colors=['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
                )
            )])
            
            fig.update_layout(
                title={
                    'text': 'Message Distribution by Participant',
                    'x': 0.5,
                    'xanchor': 'center'
                },
                showlegend=True, 
                height=400, 
                width=600,
                font=dict(size=12),
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            return self._save_plotly_fig(fig, f'msg_dist_{session_id}')
        except Exception as e:
            logger.error(f'Error creating message distribution chart: {e}')
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
                logger.warning('WordCloud library not available')
                return None
                
            word_analysis = analytics.get('word_analysis', analytics.get('keyword_tracker', {}))
            top_words = {}
            
            if isinstance(word_analysis, dict):
                if 'overall_common_words' in word_analysis:
                    top_words = word_analysis['overall_common_words']
                elif 'common_words' in word_analysis:
                    top_words = word_analysis['common_words']
                elif 'sender_common_words' in word_analysis:
                    all_words = {}
                    for sender_words in word_analysis['sender_common_words'].values():
                        if isinstance(sender_words, dict):
                            for word, count in sender_words.items():
                                if isinstance(word, str) and isinstance(count, (int, float)):
                                    all_words[word] = all_words.get(word, 0) + count
                    top_words = all_words
            
            if not top_words or not isinstance(top_words, dict):
                logger.warning('No valid word data found for wordcloud')
                return None
            
            text_parts = []
            for word, count in top_words.items():
                if isinstance(word, str) and isinstance(count, (int, float)) and word.strip():
                    repeat_count = min(int(count), 10, 50 // len(word) + 1)  # Adjust based on word length
                    text_parts.extend([word.strip()] * max(1, repeat_count))
            
            text = ' '.join(text_parts)
            
            if not text.strip() or len(text.split()) < 3:
                logger.warning('Insufficient text for wordcloud generation')
                return None
            
            logger.info(f'Creating wordcloud with {len(text.split())} words')
            
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                max_words=100, 
                colormap='viridis',
                relative_scaling=0.5,
                min_font_size=10
            ).generate(text)
            
            temp_path = os.path.join(tempfile.gettempdir(), f'wordcloud_{session_id}_{os.getpid()}.png')
            wordcloud.to_file(temp_path)
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                self._tmp_images.append(temp_path)
                logger.info(f'Wordcloud created successfully: {temp_path}')
                return temp_path
            else:
                logger.error('Wordcloud file was not created or is empty')
                return None
                
        except Exception as e:
            logger.error(f'Error creating wordcloud: {e}')
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
        if not fig:
            logger.error('No figure provided to save')
            return None
            
        try:
            temp_path = os.path.join(tempfile.gettempdir(), f'{basename}_{os.getpid()}.png')
            logger.info(f'Attempting to save chart: {temp_path}')
            
            fig.update_layout(
                width=800,
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            export_attempts = [
                {'engine': 'kaleido', 'scale': 2, 'format': 'png'},
                {'engine': 'kaleido', 'scale': 1, 'format': 'png'},
                {'scale': 2, 'format': 'png'},
                {'format': 'png'}
            ]
            
            for i, params in enumerate(export_attempts):
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                    fig.write_image(temp_path, **params)
                    
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                        logger.info(f'Chart saved successfully using method {i+1}: {os.path.getsize(temp_path)} bytes')
                        self._tmp_images.append(temp_path)
                        return temp_path
                    else:
                        logger.warning(f'Method {i+1} created empty or invalid file')
                        
                except Exception as method_error:
                    logger.warning(f'Export method {i+1} failed: {method_error}')
                    continue
            
            logger.warning('All plotly export methods failed, creating fallback chart')
            return self._create_fallback_chart(basename, temp_path)
                
        except Exception as e:
            logger.error(f'Error saving plotly figure {basename}: {e}')
            return None
            
    def _create_fallback_chart(self, basename: str, temp_path: str) -> Optional[str]:
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (800, 400), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype('arial.ttf', 16)
                title_font = ImageFont.truetype('arial.ttf', 24)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            draw.text((400, 30), f'Chart: {basename}', fill='black', font=title_font, anchor='mm')
            draw.text((400, 200), 'Chart generation temporarily unavailable', fill='gray', font=font, anchor='mm')
            draw.text((400, 230), 'Please check your plotly/kaleido installation', fill='gray', font=font, anchor='mm')
            
            draw.rectangle([10, 10, 790, 390], outline='gray', width=2)
            
            img.save(temp_path, 'PNG')
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                logger.info(f'Fallback chart created: {temp_path}')
                self._tmp_images.append(temp_path)
                return temp_path
                
        except Exception as e:
            logger.error(f'Failed to create fallback chart: {e}')
            
        return None

    def _create_image_flowable(self, img_path: str, caption: str = None):
        try:
            if not img_path or not os.path.exists(img_path):
                logger.warning(f'Image file not found: {img_path}')
                return Paragraph('Chart could not be generated.', self.normal_style)
            
            if os.path.getsize(img_path) == 0:
                logger.warning(f'Image file is empty: {img_path}')
                return Paragraph('Chart could not be generated.', self.normal_style)
            
            with Image.open(img_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  
                    else:
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                max_width = 6 * inch
                max_height = 4 * inch
                
                img_width, img_height = img.size
                width_ratio = max_width / img_width
                height_ratio = max_height / img_height
                scale_ratio = min(width_ratio, height_ratio)
                
                new_width = img_width * scale_ratio
                new_height = img_height * scale_ratio
                
                img = img.resize((int(img_width * scale_ratio), int(img_height * scale_ratio)), Image.Resampling.LANCZOS)
                
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                resized_path = os.path.join(tempfile.gettempdir(), f'{base_name}_resized_{os.getpid()}.png')
                img.save(resized_path, 'PNG')
                self._tmp_images.append(resized_path)
                
                rl_img = RLImage(resized_path, width=new_width * 0.75, height=new_height * 0.75)
                
                parts = [rl_img]
                if caption:
                    parts.append(Spacer(1, 4))
                    parts.append(Paragraph(f'<i>{caption}</i>', self.small_style))
                parts.append(Spacer(1, 8))
                
                return KeepTogether(parts)
                
        except Exception as e:
            logger.error(f'Error creating image flowable for {img_path}: {e}')
            return Paragraph('Chart could not be loaded.', self.normal_style)

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