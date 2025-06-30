from flask import Flask, render_template, request
import requests
from newspaper import Article
from textblob import TextBlob
import google.generativeai as genai
import os

app = Flask(__name__)

# ─── Gemini API Setup ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "PASTE_YOUR_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

# ─── Route for Home Page ─────────────────────────────────────────────
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
            # ─── Fetch HTML using requests with custom headers ─────
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"❌ Failed to fetch the article. Status: {response.status_code}")

            # ─── Use newspaper3k with fetched HTML ────────────────
            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            article.nlp()

            summary = article.summary
            keywords = article.keywords

            # ─── Sentiment Analysis ───────────────────────────────
            polarity = TextBlob(article.text).sentiment.polarity
            sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

            # ─── Gemini Advanced Summary ──────────────────────────
            if action == "advanced":
                model = genai.GenerativeModel("gemini-pro")
                chat = model.start_chat()
                prompt = f"Summarize this news article in bullet points:\n\n{article.text}"
                response = chat.send_message(prompt)
                advanced_summary = response.text.strip()

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
