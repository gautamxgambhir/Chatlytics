# 💬 Chatlytics - Personal Chat Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Transform your WhatsApp and Instagram conversations into beautiful, insightful analytics! Chatlytics provides comprehensive analysis of your chat patterns, relationships, and communication style with stunning visualizations and detailed PDF reports.

## ✨ Features

### 📊 **Comprehensive Analytics**
- **Message Statistics**: Total messages, word counts, participation breakdown
- **Timeline Analysis**: Daily/weekly activity patterns and communication trends
- **Response Time Analysis**: How quickly people respond and communication flow
- **Sentiment Analysis**: Emotional tone detection (positive/negative/neutral)
- **Activity Patterns**: Most active hours, days, and communication habits

### 💕 **Relationship Insights**
- **Affection Score**: Measure warmth and care in conversations
- **Compatibility Index**: Relationship compatibility based on communication
- **Conversation Starters**: Who initiates conversations and when
- **Communication Balance**: Analysis of speaking vs listening patterns

### 🎨 **Beautiful Visualizations**
- **Interactive Charts**: Stunning charts and graphs using Plotly
- **Word Clouds**: Visual representation of most frequently used words
- **Activity Heatmaps**: Time-based activity visualization
- **Emoji Analysis**: Most used emojis and expression patterns

### 📄 **Professional Reports**
- **PDF Export**: Comprehensive reports with all analytics and charts
- **Print-Ready**: High-quality PDF format perfect for sharing
- **Complete Analysis**: All insights, charts, and statistics in one document

### 🤖 **AI-Powered Insights**
- **Personality Analysis**: AI insights about communication styles
- **Fun Facts**: Interesting discoveries about your conversations
- **Relationship Dynamics**: Understanding of communication patterns
- **Conversation Summary**: AI-generated overview of your chat

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed on your system
- **pip** (Python package installer)
- **Git** (optional, for cloning)

### Installation

1. **Download or Clone the Project**
```bash
# Option 1: Clone with Git
git clone https://github.com/yourusername/chatlytics.git
cd chatlytics

# Option 2: Download ZIP and extract
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Application**
```bash
python app.py
```

4. **Open Your Browser**
Navigate to `http://localhost:5001`

### First Time Setup
1. Upload your chat file (see supported formats below)
2. Wait for analysis to complete
3. Explore your dashboard with interactive charts
4. Download your PDF report

## 📱 Supported Chat Formats

### WhatsApp Chat Export
1. Open WhatsApp on your phone
2. Go to the chat you want to analyze
3. Tap the **three dots menu** → **More** → **Export chat**
4. Choose **"Without Media"** (text only)
5. Save the `.txt` file and upload it

### Instagram Messages Export
1. Go to Instagram **Settings** → **Privacy and Security**
2. Click **"Data Download"**
3. Request your data download
4. Extract the ZIP file
5. Find and upload the `messages.json` file

## 🎯 How It Works

1. **Upload**: Simply drag and drop your chat export file
2. **Analysis**: Advanced algorithms analyze your conversation patterns
3. **Visualization**: Beautiful charts and graphs are generated
4. **Insights**: AI provides personality and relationship insights
5. **Export**: Download a comprehensive PDF report

## 📊 What You'll Discover

### Communication Patterns
- Who sends more messages and when
- Response time patterns
- Most active conversation periods
- Communication consistency over time

### Relationship Insights
- Affection levels and emotional connection
- Communication balance and compatibility
- Who initiates conversations
- Conversation flow and dynamics

### Fun Statistics
- Most used words and phrases
- Emoji personalities and usage
- Longest conversation streaks
- Late-night conversation habits

### Personality Analysis
- Communication styles and preferences
- Relationship dynamics assessment
- Fun facts about your conversations
- AI-generated personality insights

## 🛠️ Advanced Configuration

### Environment Variables (Optional)
Create a `.env` file for advanced configuration:

```env
# Basic Settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
HOST=127.0.0.1
PORT=5001

# AI Insights (Optional)
OPENROUTER_API_KEY=your-api-key-here
AI_MODEL=deepseek/deepseek-chat-v3.1:free

# Analysis Settings
MIN_MESSAGES_FOR_ANALYSIS=10
MAX_MESSAGES_FOR_AI_ANALYSIS=1000

# Logging
LOG_LEVEL=INFO
```

### Custom Settings
- **MIN_MESSAGES_FOR_ANALYSIS**: Minimum messages needed for analysis (default: 10)
- **MAX_MESSAGES_FOR_AI_ANALYSIS**: Maximum messages for AI analysis (default: 1000)
- **AI_MODEL**: AI model for insights generation
- **LOG_LEVEL**: Logging detail level (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing the Application

Run the built-in test to verify everything works:

```bash
python test_pdf.py
```

This will:
- Create sample chat data
- Generate a full analysis
- Create a PDF report
- Verify all functionality works correctly

## 🔧 Troubleshooting

### Common Issues

**PDF Generation Problems**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)
- Verify write permissions in the application folder

**Chart Generation Issues**
- Install kaleido: `pip install kaleido`
- Try: `pip install plotly --upgrade`
- Restart the application

**File Upload Problems**
- Ensure file is in correct format (.txt for WhatsApp, .json for Instagram)
- Check file size (limit: 16MB)
- Verify file is not corrupted

**Memory Issues with Large Files**
- Reduce `MAX_MESSAGES_FOR_AI_ANALYSIS` in settings
- Close other applications to free memory
- Consider splitting large chat files

### Getting Help
1. Check the error messages in the terminal/console
2. Try the test script: `python test_pdf.py`
3. Ensure all dependencies are correctly installed
4. Check Python and pip versions

## 📁 Project Structure

```
chatlytics/
├── app.py              # Main Flask application
├── analysis.py         # Chat analysis algorithms
├── pdf_export.py       # PDF report generation
├── parsing.py          # Chat file parsing
├── config.py           # Configuration settings
├── ai_summary.py       # AI insights generation
├── visualization.py    # Chart and graph creation
├── requirements.txt    # Python dependencies
├── test_pdf.py        # Testing script
├── uploads/           # Temporary file storage
└── templates/         # Web interface templates
```

## 🔒 Privacy & Security

### Data Protection
- **Local Processing**: All analysis happens on your computer
- **No Cloud Storage**: Your chat data never leaves your device
- **Automatic Cleanup**: Temporary files are deleted after analysis
- **No Account Required**: Use completely offline after setup

### What We Don't Collect
- ❌ Your chat messages or content
- ❌ Personal information or metadata
- ❌ User accounts or profiles
- ❌ Usage analytics or tracking

### What Stays Local
- ✅ All uploaded chat files
- ✅ Generated analysis data
- ✅ PDF reports and visualizations
- ✅ All processing and computation

## 🎨 Customization

### Styling and Themes
The application uses a clean, modern interface that's easy to customize:
- Modify `templates/` for HTML layout changes
- Update color schemes in `config.py`
- Customize chart colors and styling

### Adding New Analysis Features
The modular architecture makes it easy to add new analysis features:
1. Add new analysis functions to `analysis.py`
2. Create visualizations in `visualization.py`
3. Add PDF sections in `pdf_export.py`

## 🚀 Deployment (Optional)

### Local Network Access
To access from other devices on your network:

```bash
# Set host to 0.0.0.0
python app.py
# Then access via http://YOUR_IP_ADDRESS:5001
```

## 📈 Performance Tips

### For Large Chat Files
- Use the latest Python version (3.11+ recommended)
- Ensure sufficient RAM (4GB+ for large files)
- Close unnecessary applications during analysis
- Consider analyzing smaller date ranges for very large chats

### Optimization Settings
```env
# Reduce memory usage
MAX_MESSAGES_FOR_AI_ANALYSIS=500

# Speed up processing
CHART_HEIGHT=300

# Minimize logging
LOG_LEVEL=ERROR
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Bug Reports
1. Use the test script to isolate the issue
2. Include error messages and system information
3. Describe steps to reproduce the problem

### Feature Requests
1. Check existing features first
2. Describe the use case and benefits
3. Consider implementation complexity

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License. You're free to:
- ✅ Use for personal and commercial purposes
- ✅ Modify and distribute
- ✅ Create derivative works
- ✅ Private use

## 🙏 Acknowledgments

Built with amazing open-source libraries:
- **Flask** - Web framework
- **Plotly** - Interactive visualizations
- **ReportLab** - PDF generation
- **NLTK** - Natural language processing
- **Pandas** - Data manipulation
- **PIL (Pillow)** - Image processing
- **WordCloud** - Word cloud generation

## 📞 Support & Updates

### Getting Support
- 🔍 Check the troubleshooting section
- 🧪 Run the test script for diagnostics
- 📚 Review the documentation

### Version Information
- **Current Version**: 2.0.0
- **Python Support**: 3.8+
- **Last Updated**: 2024

---

**Made with ❤️ for better understanding of our digital conversations**

*Discover the story your messages tell!*
