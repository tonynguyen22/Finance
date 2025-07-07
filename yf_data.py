import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=60*60*24*30)
def get_analyst_ratings(symbol: str) -> pd.DataFrame:
    """
    Returns a one-row DataFrame (latest period) with columns:
      strongBuy, buy, hold, sell, strongSell
    """
    ticker = yf.Ticker(symbol)
    df = ticker.recommendations

    if df is None or df.empty:
        # empty frame with the right columns
        return pd.DataFrame(columns=["strongBuy","buy","hold","sell","strongSell"])

    # take the very first row and drop 'period'
    first = df.iloc[[0]].drop(columns=["period"], errors="ignore")
    return first


@st.cache_data(ttl=60*60*24*30)
def get_target_prices(symbol: str) -> dict:
    """
    Returns a dict with mean, low and high analyst target prices.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "target_mean": info.get("targetMeanPrice"),
        "target_low":  info.get("targetLowPrice"),
        "target_high": info.get("targetHighPrice")
    }

