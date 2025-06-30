from flask import Flask, render_template, request
import requests
from newspaper import Article
from textblob import TextBlob
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ─── Load environment variables from .env ─────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    summary = ""
    keywords = []
    sentiment = ""
    advanced_summary = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        action = request.form.get("action", "basic")

        try:
            # ─── Fetch article HTML with headers ──────────────────────
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"❌ Failed to fetch article. Status code: {response.status_code}")

            # ─── Parse with newspaper3k ───────────────────────────────
            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            article.nlp()

            summary = article.summary
            keywords = article.keywords

            # ─── Sentiment Analysis using TextBlob ────────────────────
            polarity = TextBlob(article.text).sentiment.polarity
            sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

            # ─── Advanced Summary via Gemini ──────────────────────────
            if action == "advanced":
                try:
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    response = model.generate_content(f"Summarize this article in bullet points:\n\n{article.text}")
                    advanced_summary = response.text.strip()
                except Exception as e:
                    advanced_summary = f"Gemini Error: {e}"


        except Exception as e:
            summary = f"Error: {e}"

    return render_template(
        "index.html",
        url=url,
        summary=summary,
        keywords=keywords,
        sentiment=sentiment,
        advanced_summary=advanced_summary
    )

if __name__ == "__main__":
    app.run(debug=True)
