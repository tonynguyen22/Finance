import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)
def fetch_api(url):
    import requests
    return requests.get(url).json()

def extract_sentiment(insights):
    if isinstance(insights, list) and len(insights) > 0:
        return insights[0].get("sentiment", "N/A").capitalize()
    return "N/A"

st.title("Sentiment Monitor")

symbol = st.text_input("Enter Ticker").upper()
run_analysis = st.button("Go")

if run_analysis and symbol:
    POLYGON_API_KEY = st.secrets["POLYGON_API_KEY"]
    url = f"https://api.polygon.io/v2/reference/news?ticker={symbol}&limit=20&sort=published_utc&apiKey={POLYGON_API_KEY}"
    data = fetch_api(url)

    if "results" not in data or not data["results"]:
        st.warning("No news found.")
        st.stop()

    articles = data["results"]
    df = pd.DataFrame(articles)

    df["published_utc"] = pd.to_datetime(df["published_utc"]).dt.date
    df["label"] = df["insights"].apply(extract_sentiment)

    df = df[["published_utc", "title", "label"]]
    df = df.sort_values("published_utc", ascending=False)

    st.subheader(f"News for {symbol}")
    st.dataframe(df, use_container_width=True)

    st.subheader("Sentiment Summary")
    st.bar_chart(df["label"].value_counts())
