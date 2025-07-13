import streamlit as st
import pandas as pd
import yfinance as yf
import json
import matplotlib.pyplot as plt
from utils import highlight_gains

with open("data/trades.json") as f:
    trades_data = json.load(f)

rows = []
for trade in trades_data:
    rows.append({
        "Ticker": trade["ticker"],
        "Company": trade["company"],
        "Date": trade["date"],
        "Shares": float(trade["shares"]),
        "Cost/Share": float(trade["cost_share"])
    })
df_trades = pd.DataFrame(rows)

aggregated = df_trades.groupby("Ticker").agg({
    "Shares": "sum",
    "Cost/Share": "mean"
}).reset_index()

tickers = list(aggregated["Ticker"])
data = yf.download(tickers, progress=False, group_by='ticker')

latest_prices = []
earnings_dates = []

for ticker in tickers:
    price = data[ticker]['Close'][-1]
    latest_prices.append(price)

    t = yf.Ticker(ticker)
    try:
        cal = t.calendar
        if isinstance(cal, dict):
            ed = cal.get("Earnings Date", ["N/A"])
            earnings_date = ed[0] if isinstance(ed, list) else ed
        elif isinstance(cal, pd.DataFrame):
            earnings_date = cal.loc["Earnings Date"].values[0]
        else:
            earnings_date = "N/A"
    except:
        earnings_date = "N/A"

    earnings_dates.append(str(earnings_date))

aggregated["Market Price"] = latest_prices
aggregated["Total Value"] = aggregated["Shares"] * aggregated["Market Price"]
aggregated["Total Cost"] = aggregated["Shares"] * aggregated["Cost/Share"]
aggregated["Gain $"] = aggregated["Total Value"] - aggregated["Total Cost"]
aggregated["Gain %"] = (aggregated["Gain $"] / aggregated["Total Cost"]) * 100
aggregated["Earnings Date"] = earnings_dates

st.title("Portfolio Tracker")
st.subheader("Portfolio Overview")
styled = aggregated.round(1).style.applymap(highlight_gains, subset=["Gain $", "Gain %"])
st.dataframe(styled.format({
    "Shares": "{:.2f}",
    "Cost/Share": "{:.2f}",
    "Market Price": "{:.2f}",
    "Total Value": "{:.2f}",
    "Total Cost": "{:.2f}",
    "Gain $": "{:.1f}$",
    "Gain %": "{:.1f}%"
}))

sector_map = {
    "NU": "Fintech",
    "GOOG": "Tech",
    "SOXX": "Semis",
    "TSM": "Semis",
    "CVS": "Healthcare",
    "GXO": "Logistics"
}
aggregated["Sector"] = aggregated["Ticker"].map(sector_map)
sector_alloc = aggregated.groupby("Sector")["Total Value"].sum()
fig, ax = plt.subplots()
ax.pie(sector_alloc, labels=sector_alloc.index, autopct="%1.1f%%")
ax.set_title("Sector Diversification")
st.subheader("Sector Diversification")
st.pyplot(fig)

st.subheader("Trade History")
st.dataframe(df_trades.sort_values("Date", ascending=False).round(1))
