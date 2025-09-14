import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from config import Config
from parsing import ChatParser
from analysis import ChatAnalyzer
from ai_summary import AISummaryGenerator
from visualization import ChartGenerator
from pdf_export import PDFExporter
from supabase import create_client

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL), format=Config.LOG_FORMAT)

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_messages_from_session(session_id: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    session_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}_data.json')
    logger.info(f'Loading session data for session_id: {session_id}')
    try:
        with open(session_file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        messages_data = session_data['messages']
        messages = []
        for msg in messages_data:
            message = {'timestamp': datetime.fromisoformat(msg['timestamp']), 'sender': msg['sender'], 'message': msg['message'], 'is_system': msg['is_system']}
            messages.append(message)
        logger.info(f'Successfully loaded {len(messages)} messages for session {session_id}')
        return (messages, session_data)
    except FileNotFoundError:
        logger.error(f'Session data file not found for session_id: {session_id}')
        raise
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON in session data file for session_id: {session_id} - {e}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error loading session data: {e}')
        raise

@app.route('/')
def index():
    logger.info('Home page accessed')
    return render_template('index.html')


supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_bucket = os.getenv("SUPABASE_BUCKET", "chat-uploads")
supabase = create_client(supabase_url, supabase_key)

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info('File upload request received')
    if 'file' not in request.files:
        logger.warning('Upload request missing file')
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning('Upload request with empty filename')
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        session_id = str(uuid.uuid4())
        logger.info(f'Processing upload for session: {session_id}')
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}_{filename}')

        try:
            file.save(file_path)
            logger.info(f'File saved locally: {file_path}')

            supabase_path = f"{session_id}_{filename}"
            with open(file_path, "rb") as f:
                res = supabase.storage.from_(supabase_bucket).upload(
                    supabase_path,
                    f,
                    file_options={"cache-control": "3600", "upsert": "true"}
                )

            parser = ChatParser()
            messages = parser.parse_file(file_path, filename)
            if not messages:
                logger.error(f'Failed to parse file: {filename}')
                return jsonify({'error': 'Could not parse chat file. Please check the format.'}), 400

            logger.info(f'Successfully parsed {len(messages)} messages from {filename}')

            serializable_messages = []
            for msg in messages:
                serializable_msg = {
                    'timestamp': msg['timestamp'].isoformat(),
                    'sender': msg['sender'],
                    'message': msg['message'],
                    'is_system': msg['is_system']
                }
                serializable_messages.append(serializable_msg)

            session_data = {
                'session_id': session_id,
                'filename': filename,
                'messages': serializable_messages,
                'file_path': file_path,
                'created_at': datetime.now().isoformat(),
                'message_count': len(messages),
                'supabase_path': supabase_path
            }

            session_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}_data.json')
            with open(session_file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            logger.info(f'Session data saved for {session_id}')
            return jsonify({'success': True, 'session_id': session_id})

        except Exception as e:
            logger.error(f'Error processing file upload: {e}', exc_info=True)
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

    logger.warning(f'Invalid file type uploaded: {file.filename}')
    return jsonify({'error': 'Invalid file type. Please upload .txt or .json files.'}), 400


@app.route('/dashboard/<session_id>')
def dashboard(session_id: str):
    logger.info(f'Dashboard access requested for session: {session_id}')
    try:
        session_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{session_id}_data.json')
        with open(session_file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        logger.info(f'Dashboard loaded successfully for session: {session_id}')
        return render_template('dashboard.html', session_id=session_id, filename=session_data['filename'])
    except FileNotFoundError:
        logger.warning(f'Session data not found for session: {session_id}')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f'Error loading dashboard for session {session_id}: {e}')
        return redirect(url_for('index'))

@app.route('/api/analytics/<session_id>')
def get_analytics(session_id: str):
    logger.info(f'Analytics requested for session: {session_id}')
    try:
        messages, session_data = load_messages_from_session(session_id)
        analyzer = ChatAnalyzer()
        analytics = analyzer.analyze_chat(messages)
        logger.info(f'Analytics generated successfully for session: {session_id}')
        return jsonify(analytics)
    except FileNotFoundError:
        logger.error(f'Session not found for analytics: {session_id}')
        return (jsonify({'error': 'Session not found'}), 404)
    except Exception as e:
        logger.error(f'Error generating analytics for session {session_id}: {e}', exc_info=True)
        return (jsonify({'error': 'Failed to generate analytics'}), 500)

@app.route('/api/ai-insights/<session_id>')
def get_ai_insights(session_id: str):
    logger.info(f'AI insights requested for session: {session_id}')
    try:
        messages, session_data = load_messages_from_session(session_id)
        ai_generator = AISummaryGenerator()
        insights = ai_generator.generate_insights(messages)
        logger.info(f'AI insights generated successfully for session: {session_id}')
        return jsonify(insights)
    except FileNotFoundError:
        logger.error(f'Session not found for AI insights: {session_id}')
        return (jsonify({'error': 'Session not found'}), 404)
    except Exception as e:
        logger.error(f'Error generating AI insights for session {session_id}: {e}', exc_info=True)
        return (jsonify({'error': 'Failed to generate AI insights'}), 500)

@app.route('/api/charts/<session_id>')
def get_charts(session_id: str):
    logger.info(f'Charts requested for session: {session_id}')
    try:
        messages, session_data = load_messages_from_session(session_id)
        chart_generator = ChartGenerator()
        charts = chart_generator.generate_charts(messages)
        logger.info(f'Charts generated successfully for session: {session_id}')
        return jsonify(charts)
    except FileNotFoundError:
        logger.error(f'Session not found for charts: {session_id}')
        return (jsonify({'error': 'Session not found'}), 404)
    except Exception as e:
        logger.error(f'Error generating charts for session {session_id}: {e}', exc_info=True)
        return (jsonify({'error': 'Failed to generate charts'}), 500)

@app.route('/export/<session_id>')
def export_pdf(session_id: str):
    logger.info(f'PDF export requested for session: {session_id}')
    try:
        messages, session_data = load_messages_from_session(session_id)
        filename = session_data['filename']
        analyzer = ChatAnalyzer()
        analytics = analyzer.analyze_chat(messages)
        ai_generator = AISummaryGenerator()
        try:
            ai_insights = ai_generator.generate_insights(messages)
        except Exception as ai_error:
            logger.warning(f'AI insights failed: {ai_error}')
            ai_insights = {'personality_analysis': 'AI analysis temporarily unavailable.', 'relationship_dynamics': 'Relationship analysis temporarily unavailable.', 'conversation_style': 'Style analysis temporarily unavailable.', 'fun_facts': 'Fun facts temporarily unavailable.', 'overall_summary': 'AI summary temporarily unavailable.'}
        pdf_exporter = PDFExporter()
        pdf_path = pdf_exporter.create_full_pdf(analytics, ai_insights, filename, session_id)
        if not pdf_path or not os.path.exists(pdf_path):
            raise Exception('PDF file was not created')
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            logger.warning('Generated PDF is empty, creating fallback')
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            fallback_path = os.path.join(app.config['UPLOAD_FOLDER'], f'chatlytics_report_{session_id}_fallback.pdf')
            doc = SimpleDocTemplate(fallback_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = [Paragraph('Chatlytics Report', styles['Title']), Paragraph('⚠️ Analytics PDF generation failed.', styles['Normal']), Paragraph('Please try again later.', styles['Normal'])]
            doc.build(story)
            pdf_path = fallback_path
            file_size = os.path.getsize(pdf_path)
        abs_pdf_path = os.path.abspath(pdf_path)
        return send_file(abs_pdf_path, as_attachment=True, download_name=f'chatlytics_report_{session_id}.pdf', mimetype='application/pdf', conditional=False, max_age=0)
    except FileNotFoundError:
        return (jsonify({'error': 'Session not found'}), 404)
    except Exception as e:
        logger.error(f'Error exporting PDF for {session_id}: {e}', exc_info=True)
        return (jsonify({'error': f'Failed to export PDF: {str(e)}'}), 500)
if __name__ == '__main__':
    logger.info('Starting Chatlytics application')
    try:
        app.run(debug=Config.DEBUG, host='127.0.0.1', port=5001)
    except Exception as e:
        logger.error(f'Failed to start application: {e}', exc_info=True)
        raise