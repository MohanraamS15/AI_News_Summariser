import os
import re
import json
from flask import Flask, render_template, request
import requests
from newspaper import Article
from textblob import TextBlob
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    summary = ""
    keywords = []
    sentiment = ""
    advanced_summary = ""
    advanced_title = ""
    advanced_tone = ""
    advanced_main_points = []
    advanced_keywords = []
    pub_date = ""
    image_url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        action = request.form.get("action", "basic")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"❌ Failed to fetch article. Status code: {response.status_code}")

            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            article.nlp()

            summary = article.summary
            keywords = article.keywords
            pub_date = article.publish_date.strftime("%B %d, %Y") if article.publish_date else "Not available"
            image_url = article.top_image or ""

            polarity = TextBlob(article.text).sentiment.polarity
            sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

            if action == "advanced":
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                prompt = f"""
Respond only with valid JSON. No explanations or extra text.

The JSON should have these keys:
- "title" (string)
- "summary" (string, 4-5 sentences)
- "tone" (string)
- "main_points" (array of strings, bullet points)
- "keywords" (array of strings, 5-6 important ones)

Article:
{article.text}
"""
                response = model.generate_content(prompt)
                advanced_data = extract_json_from_text(response.text.strip())
                if not advanced_data:
                    advanced_summary = "Error: Could not parse advanced summary response."
                else:
                    advanced_title = advanced_data.get("title", "")
                    advanced_summary = advanced_data.get("summary", "")
                    advanced_tone = advanced_data.get("tone", "")
                    advanced_main_points = advanced_data.get("main_points", [])
                    advanced_keywords = advanced_data.get("keywords", [])

        except Exception as e:
            if action == "advanced":
                advanced_summary = f"Error: {e}"
            else:
                summary = f"Error: {e}"

    return render_template(
        "index.html",
        url=url,
        summary=summary,
        keywords=keywords,
        sentiment=sentiment,
        pub_date=pub_date,
        advanced_summary=advanced_summary,
        advanced_title=advanced_title,
        advanced_tone=advanced_tone,
        advanced_main_points=advanced_main_points,
        advanced_keywords=advanced_keywords,
        image_url=image_url
    )

if __name__ == "__main__":
    app.run(debug=True)
import os
import re
import json
from flask import Flask, render_template, request
import requests
from newspaper import Article
from textblob import TextBlob
import google.generativeai as genai
from dotenv import load_dotenv
import nltk

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Load environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    summary = ""
    keywords = []
    sentiment = ""
    advanced_summary = ""
    advanced_title = ""
    advanced_tone = ""
    advanced_main_points = []
    advanced_keywords = []
    pub_date = ""
    image_url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        action = request.form.get("action", "basic")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                raise Exception(f"❌ Failed to fetch article. Status code: {response.status_code}")

            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            
            # Handle potential issues with NLP processing
            try:
                article.nlp()
            except:
                # If NLP fails, we'll still have the basic summary
                pass

            summary = article.summary if article.summary else "Summary not available"
            keywords = article.keywords if article.keywords else []
            pub_date = article.publish_date.strftime("%B %d, %Y") if article.publish_date else "Not available"
            image_url = article.top_image or ""

            # Sentiment analysis with error handling
            try:
                polarity = TextBlob(article.text).sentiment.polarity
                sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            except:
                sentiment = "Neutral"

            if action == "advanced":
                try:
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    prompt = f"""
Respond only with valid JSON. No explanations or extra text.

The JSON should have these keys:
- "title" (string)
- "summary" (string, 4-5 sentences)
- "tone" (string)
- "main_points" (array of strings, bullet points)
- "keywords" (array of strings, 5-6 important ones)

Article:
{article.text[:5000]}  # Limit text to avoid token limits
"""
                    response = model.generate_content(prompt)
                    advanced_data = extract_json_from_text(response.text.strip())
                    if not advanced_data:
                        advanced_summary = "Error: Could not parse advanced summary response."
                    else:
                        advanced_title = advanced_data.get("title", "")
                        advanced_summary = advanced_data.get("summary", "")
                        advanced_tone = advanced_data.get("tone", "")
                        advanced_main_points = advanced_data.get("main_points", [])
                        advanced_keywords = advanced_data.get("keywords", [])
                except Exception as e:
                    advanced_summary = f"Error: Advanced AI analysis failed - {str(e)}"

        except requests.exceptions.Timeout:
            error_msg = "Error: Request timed out. Please try again."
            if action == "advanced":
                advanced_summary = error_msg
            else:
                summary = error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Error: Network error - {str(e)}"
            if action == "advanced":
                advanced_summary = error_msg
            else:
                summary = error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if action == "advanced":
                advanced_summary = error_msg
            else:
                summary = error_msg

    return render_template(
        "index.html",
        url=url,
        summary=summary,
        keywords=keywords,
        sentiment=sentiment,
        pub_date=pub_date,
        advanced_summary=advanced_summary,
        advanced_title=advanced_title,
        advanced_tone=advanced_tone,
        advanced_main_points=advanced_main_points,
        advanced_keywords=advanced_keywords,
        image_url=image_url
    )

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)