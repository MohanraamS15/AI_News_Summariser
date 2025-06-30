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
    # Try to find JSON object inside text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            return json.loads(json_str)
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
                response_text = response.text.strip()

                advanced_data = extract_json_from_text(response_text)
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
        advanced_keywords=advanced_keywords
    )

if __name__ == "__main__":
    app.run(debug=True)
