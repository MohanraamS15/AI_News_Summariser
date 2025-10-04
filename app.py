import os
import re
import json
import requests
import nltk
from flask import Flask, render_template, request
from newspaper import Article, Config
from textblob import TextBlob
import google.generativeai as genai
from dotenv import load_dotenv

# ───────────── NLTK Setup for Render ─────────────
NLTK_DATA_DIR = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DATA_DIR)

# Download NLTK data with error handling
for pkg in ("punkt", "stopwords", "averaged_perceptron_tagger", "wordnet"):
    try:
        nltk.download(pkg, download_dir=NLTK_DATA_DIR, quiet=True)
    except Exception as e:
        print(f"Warning: Failed to download {pkg}: {e}")

# ───────────── Gemini API Setup ─────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")
genai.configure(api_key=GEMINI_API_KEY)

# ───────────── Flask App + Newspaper Config ─────────────
app = Flask(__name__)
cfg = Config()
cfg.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

def create_manual_summary(text, max_sentences=5):
    """Create a summary by taking the first few sentences if NLP fails"""
    if not text:
        return "No content available for summarization."
    
    # Split into sentences (simple approach)
    sentences = []
    current_sentence = ""
    
    for char in text:
        current_sentence += char
        if char in '.!?' and len(current_sentence.strip()) > 10:
            sentences.append(current_sentence.strip())
            current_sentence = ""
            if len(sentences) >= max_sentences:
                break
    
    # If we didn't get enough sentences, add the remaining text
    if current_sentence.strip() and len(sentences) < max_sentences:
        sentences.append(current_sentence.strip())
    
    summary = ' '.join(sentences[:max_sentences])
    
    # If summary is too short, take first 400 characters
    if len(summary) < 100:
        summary = text[:400] + ("..." if len(text) > 400 else "")
    
    return summary

def get_sentiment_safe(text):
    """Get sentiment with fallback if TextBlob fails"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        # Simple keyword-based fallback
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'failed']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "Positive"
        elif neg_count > pos_count:
            return "Negative"
        else:
            return "Neutral"

def extract_keywords_safe(text):
    """Extract keywords with fallback if NLTK fails"""
    try:
        blob = TextBlob(text)
        # Get noun phrases as keywords
        keywords = list(blob.noun_phrases)[:10]  # Limit to 10 keywords
        return keywords if keywords else []
    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        # Simple fallback - extract capitalized words and common nouns
        words = text.split()
        keywords = []
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if (len(clean_word) > 3 and 
                (clean_word[0].isupper() or clean_word.lower() in 
                 ['technology', 'business', 'health', 'science', 'politics', 'economy'])):
                if clean_word not in keywords and len(keywords) < 10:
                    keywords.append(clean_word)
        return keywords

def json_from(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    ctx = dict(
        url="",
        summary="",
        keywords=[],
        sentiment="",
        pub_date="",
        image_url="",
        advanced_title="",
        advanced_summary="",
        advanced_tone="",
        advanced_main_points=[],
        advanced_keywords=[]
    )

    if request.method == "POST":
        ctx["url"] = url = request.form.get("url", "").strip()
        action = request.form.get("action", "basic")

        try:
            headers = {"User-Agent": cfg.browser_user_agent}
            html_r = requests.get(url, headers=headers, timeout=30)
            html_r.raise_for_status()

            art = Article(url, config=cfg)
            art.download(input_html=html_r.text)
            art.parse()

            print(f"[DEBUG] Article text length: {len(art.text)}")
            print(f"[DEBUG] First 300 chars: {art.text[:300]}")

            # Try NLP processing with fallback
            try:
                art.nlp()
                print("[DEBUG] NLP processing successful")
                # Use article's summary if available and good quality
                if art.summary and len(art.summary) > 50:
                    ctx["summary"] = art.summary
                else:
                    ctx["summary"] = create_manual_summary(art.text)
                
                # Use article's keywords if available
                if art.keywords:
                    ctx["keywords"] = art.keywords[:10]  # Limit to 10
                else:
                    ctx["keywords"] = extract_keywords_safe(art.text)
                    
            except Exception as e:
                print(f"[WARNING] article.nlp() failed: {e}")
                # Fallback to manual processing
                ctx["summary"] = create_manual_summary(art.text)
                ctx["keywords"] = extract_keywords_safe(art.text)

            # Publication date
            ctx["pub_date"] = (
                art.publish_date.strftime("%B %d, %Y")
                if art.publish_date else "Not available"
            )
            
            # Image
            ctx["image_url"] = art.top_image or ""

            # Sentiment analysis with fallback
            ctx["sentiment"] = get_sentiment_safe(art.text)

            # Advanced AI analysis
            if action == "advanced":
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"""
Respond ONLY with JSON.

Keys:
- "title"
- "summary"
- "tone"
- "main_points"
- "keywords"

Article:
{art.text[:5000]}
"""
                    res = model.generate_content(prompt)
                    data = json_from(res.text.strip())

                    if data:
                        ctx["advanced_title"] = data.get("title", "")
                        ctx["advanced_summary"] = data.get("summary", "")
                        ctx["advanced_tone"] = data.get("tone", "")
                        ctx["advanced_main_points"] = data.get("main_points", [])
                        ctx["advanced_keywords"] = data.get("keywords", [])
                    else:
                        ctx["advanced_summary"] = "Gemini JSON parse error."
                except Exception as e:
                    ctx["advanced_summary"] = f"Gemini error: {str(e)}"

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if action == "advanced":
                ctx["advanced_summary"] = error_msg
            else:
                ctx["summary"] = error_msg

    return render_template("index.html", **ctx)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)