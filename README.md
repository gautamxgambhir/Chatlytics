# Chatlytics 💬📊

**Advanced Chat Analytics Dashboard with AI-Powered Insights**

Transform your chat conversations into beautiful visualizations and meaningful insights. Chatlytics analyzes your text messages and provides comprehensive analytics, sentiment analysis, and AI-generated relationship insights.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 📊 Analytics
- **Message Statistics**: Total messages, participants, conversation duration
- **Balance Analysis**: Communication patterns and effort distribution
- **Response Time Analysis**: Average response times and communication speed
- **Activity Patterns**: Most active hours, days, and time-based insights
- **Fun Metrics**: Message leaders, emoji champions, conversation starters

### 🎯 Advanced Insights
- **Sentiment Analysis**: Positive, neutral, and negative message classification
- **Emoji Personality**: Top emojis, usage patterns, and emoji leaders
- **Word Analysis**: Common words, unique vocabulary, shared expressions
- **Conversation Flow**: Turn-taking patterns and conversation dynamics
- **Who Thinks First**: Daily conversation initiators and timing patterns

### 🤖 AI-Powered Features
- **Personality Analysis**: AI assessment of communication styles
- **Relationship Dynamics**: Insights into relationship patterns
- **Conversation Style**: Analysis of interaction preferences
- **Fun Facts**: AI-generated interesting observations
- **Personalized Reports**: Custom AI insights about your bond

### 📈 Visualizations
- Interactive charts and graphs using Plotly
- Message distribution charts
- Activity timeline visualizations
- Sentiment trend analysis
- Emoji usage statistics
- Response time distributions

### 📄 Export Options
- PDF report generation with all insights
- Comprehensive analytics summary
- Shareable insights and statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatlytics
   ```

2. **Install dependencies**
   ```bash
   pip install flask plotly requests nltk python-dotenv reportlab
   ```

3. **Download NLTK data** (automatic on first run)
   ```bash
   python -c "import nltk; nltk.download('stopwords')"
   ```

4. **Launch the application**
   ```bash
   python launch_dashboard.py
   ```

5. **Access the dashboard**
   Open your browser and navigate to `http://localhost:5000`

## 📱 Supported Chat Formats

Chatlytics supports various chat export formats:

### WhatsApp
- Export chat from WhatsApp (Settings → Chats → Export Chat)
- Upload the .txt file to analyze

### Text Formats
- Plain text with timestamp patterns
- JSON formatted chat exports
- Custom delimited formats

### Example Format
```
[12/1/23, 10:30:45 AM] John: Hey, how are you?
[12/1/23, 10:31:02 AM] Jane: I'm doing great! How about you?
```

## 🎨 Dashboard Sections

### Overview Tab
- Key statistics and metrics
- Fun achievements and crowns
- Message distribution charts
- Activity timeline

### Messages Tab
- Word count comparisons
- Message length analysis
- Common words exploration

### Emojis Tab
- Top emoji usage charts
- Emoji personality insights
- Participant emoji preferences

### Timing Tab
- Activity heatmaps by hour
- Daily activity patterns
- Response time analysis
- Timing insights

### Sentiment Tab
- Sentiment distribution
- Message length vs sentiment
- Conversation flow analysis
- Activity pattern insights

### AI Insights Tab
- Overall relationship summary
- Personality analysis
- Relationship dynamics
- Conversation style insights

### Who Thinks First Tab
- Daily conversation initiator analysis
- Calendar heatmap visualization
- First message statistics
- Morning person insights

### Advanced Tab
- Love/affection scores
- Compatibility index
- Mood timeline
- Communication streaks and gaps
- Word cloud visualization
- Personalized AI reports

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

### API Configuration
- **OpenRouter AI**: For generating AI insights
- **Model**: deepseek/deepseek-chat-v3.1:free (configurable)
- **Max Tokens**: 500 (configurable)
- **Temperature**: 0.7 (configurable)

### File Upload Limits
- Maximum file size: 16MB
- Supported formats: .txt, .json
- Minimum messages for analysis: 10

## 🛠️ Architecture

### Backend Components
- **Flask**: Web framework and API endpoints
- **Analysis Engine**: Core analytics and statistics
- **AI Integration**: OpenRouter API for insights
- **Visualization**: Plotly chart generation
- **PDF Export**: ReportLab for report generation

### Frontend Components
- **Responsive UI**: Modern dashboard interface
- **Interactive Charts**: Plotly.js visualizations
- **Real-time Loading**: Progress indicators and animations
- **Tab Navigation**: Organized content sections

### File Structure
```
chatlytics/
├── app.py              # Main Flask application
├── analysis.py         # Core analytics engine
├── ai_summary.py       # AI insight generation
├── visualization.py    # Chart and graph generation
├── pdf_export.py       # PDF report creation
├── parsing.py          # Chat file parsing
├── config.py           # Configuration settings
├── utils.py            # Utility functions
├── templates/          # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   └── index.html
├── uploads/            # Uploaded chat files
└── static/             # Static assets
```

## 🎯 API Endpoints

### Core Endpoints
- `GET /` - Main upload interface
- `POST /upload` - File upload handler
- `GET /dashboard/<session_id>` - Dashboard interface

### API Endpoints
- `GET /api/analytics/<session_id>` - Analytics data
- `GET /api/ai-insights/<session_id>` - AI-generated insights
- `GET /api/charts/<session_id>` - Chart data
- `GET /export/<session_id>` - PDF export

## 🔧 Development

### Running in Development Mode
```bash
python app.py
```

### Testing
```bash
python test_complete_dashboard.py
```

### Code Structure
- Clean, modular Python code
- Type hints for better maintainability
- Error handling and fallbacks
- Responsive frontend design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter**: AI API services
- **Plotly**: Interactive visualizations
- **NLTK**: Natural language processing
- **Flask**: Web framework
- **Tailwind CSS**: Styling framework

## 📞 Support

For support, questions, or feature requests:
- Create an issue on GitHub
- Check the documentation
- Review the configuration guide

---

**Made with ❤️ for understanding relationships through data**
