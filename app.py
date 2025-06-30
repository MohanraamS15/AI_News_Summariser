import os
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

@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    summary = ""
    keywords = []
    sentiment = ""
    advanced_summary = ""
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
                try:
                    model = genai.GenerativeModel("models/gemini-1.5-flash")
                    prompt = f"""
Summarize the following news article with these points:
- Title
- Published Date - find it it might be somewhere in the article (it is just a example for you -Jun 30, 2025 08:54 PM IST ,dont print the same),so after finding it, format it like this: June 30, 2025
- Summary (4-5 sentences)
- Tone of the article
- Main points in bullets
-keywords(most important 5 to 6 keywords)

Article:
{article.text}
"""
                    response = model.generate_content(prompt)
                    advanced_summary = response.text.strip()
                except Exception as e:
                    advanced_summary = f"Gemini Error: {e}"

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
        advanced_summary=advanced_summary,
        pub_date=pub_date
    )

if __name__ == "__main__":
    app.run(debug=True)
