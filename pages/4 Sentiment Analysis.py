import streamlit as st
from utils import fetch_api
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

st.title("Polygon.io Sentiment Monitor")

symbol = st.text_input("Enter Ticker", value="AAPL")

POLYGON_API_KEY = st.secrets["POLYGON_API_KEY"]
url = f"https://api.polygon.io/v2/reference/news?ticker={symbol}&limit=20&sort=published_utc&apiKey={POLYGON_API_KEY}"

data = fetch_api(url)

if "results" not in data or not data["results"]:
    st.warning("No news found.")
    st.stop()

articles = data["results"]
df = pd.DataFrame(articles)

df["published_utc"] = pd.to_datetime(df["published_utc"])
df = df[["published_utc", "title", "description", "article_url", "publisher"]]
df = df.sort_values("published_utc", ascending=False)

nltk.download("vader_lexicon", quiet=True)
sid = SentimentIntensityAnalyzer()

df["text"] = df["title"] + ". " + df["description"].fillna("")
df["sentiment"] = df["text"].apply(lambda x: sid.polarity_scores(x)["compound"])
df["label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.2 else ("Negative" if x < -0.2 else "Neutral"))

st.subheader(f"News for {symbol}")
st.dataframe(df[["published_utc", "title", "publisher", "label"]])

st.subheader("Sentiment Summary")
st.bar_chart(df["label"].value_counts())
