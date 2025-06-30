from flask import Flask, render_template, request
from newspaper import Article
from textblob import TextBlob

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    keywords = []
    sentiment = ""
    url = ""

    if request.method == "POST":
        url = request.form["url"]

        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            summary = article.summary
            keywords = article.keywords

            blob = TextBlob(article.text)
            polarity = blob.sentiment.polarity
            if polarity > 0:
                sentiment = "Positive"
            elif polarity < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        except Exception as e:
            summary = f"Error: {str(e)}"

    return render_template("index.html", summary=summary, keywords=keywords, sentiment=sentiment, url=url)

if __name__ == "__main__":
    app.run(debug=True)
