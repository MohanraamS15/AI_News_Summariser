#🚀 AI Article Summarizer

A modern web application that transforms any article into intelligent insights using advanced AI analysis and natural language processing.

## ✨ Features

- **Dual Analysis Modes**
  - Basic NLP summarization with sentiment analysis
  - Advanced AI analysis powered by Google Gemini API
- **Smart Content Extraction**
  - Article text, images, and metadata extraction
  - Keyword identification and sentiment detection
- **Modern UI/UX**
  - Responsive design with beautiful animations
  - Interactive image modal viewer
  - Real-time loading indicators
- **Comprehensive Analysis**
  - Article summaries and key points
  - Tone and sentiment analysis
  - Publication date and featured images

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **AI/ML:** Google Gemini API, TextBlob, NLTK
- **Frontend:** HTML5, CSS3, JavaScript
- **Libraries:** newspaper3k, requests
- **Deployment:** Render
- **Environment:** Python 3.11

## 🚀 Live Demo

[View Live Application](https://ai-article-summarizer-vet1.onrender.com/)

## 📋 Prerequisites

- Python 3.11+
- Google Gemini API key
- pip package manager

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MohanraamS15/ai-article-summarizer.git
   cd ai-article-summarizer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   ```

5. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## 🏃‍♂️ Running the Application

### Development
```bash
python app.py
```
Visit `http://localhost:5000`

### Production (using Gunicorn)
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## 🎯 Usage

1. **Enter Article URL:** Paste any article URL in the input field
2. **Basic Analysis:** Click "Summarize" for NLP-based summary with sentiment analysis
3. **Advanced Analysis:** Click "Advanced AI" for comprehensive AI-powered insights
4. **View Results:** Get summaries, keywords, sentiment, and key points
5. **Interactive Features:** Click on images to view in full-screen modal


## 🌐 Deployment

### Render Deployment

1. **Connect GitHub repository** to Render
2. **Set Environment Variables:**
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `PYTHON_VERSION`: 3.11.0
3. **Deploy** using the provided `render.yaml` configuration

### Manual Deployment
```bash
# Build command
pip install -r requirements.txt && python -m textblob.download_corpora

# Start command
gunicorn app:app --bind 0.0.0.0:$PORT
```

## 📁 Project Structure

```
ai-article-summarizer/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── render.yaml           # Render deployment configuration
├── .env                  # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
│
├── templates/
│   └── index.html       # Main HTML template
│
└── static/              # Static files (if any)
```

## 🔧 API Endpoints

- `GET /` - Main application interface
- `POST /` - Process article analysis
- `GET /health` - Health check endpoint

## 🤖 AI Features

### Basic NLP Analysis
- Text summarization using newspaper3k
- Sentiment analysis with TextBlob
- Automatic keyword extraction
- Publication date detection

### Advanced AI Analysis
- Comprehensive summarization via Gemini API
- Tone and style analysis
- Structured key points extraction
- Enhanced keyword identification

## 🎨 UI Features

- **Animated Gradient Background** with smooth transitions
- **Glassmorphism Design** with backdrop blur effects
- **Interactive Elements** with hover animations
- **Responsive Layout** for all device sizes
- **Loading Indicators** for better UX
- **Error Handling** with user-friendly messages

## 🛡️ Error Handling

- Network timeout handling
- Invalid URL detection
- API rate limit management
- Graceful degradation for failed requests
- User-friendly error messages

## 📝 Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000  # Optional, defaults to 5000
```

## 🔒 Security Features

- Input validation for URLs
- Environment variable protection
- Request timeout limits
- Error message sanitization

## 🧪 Testing

```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test with a sample article
curl -X POST http://localhost:5000 -d "url=https://example-article.com&action=basic"
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for advanced AI analysis
- newspaper3k library for article extraction
- TextBlob for sentiment analysis
- Flask framework for web application
- Render for hosting and deployment

## 📞 Contact

Mohanraam S - [mohanraams2004@gmail.com](mailto:mohanraams2004@gmail.com)

Project Link: [https://github.com/MohanraamS15/ai-article-summarizer](https://github.com/MohanraamS15/AI_News_Summariser)

---
