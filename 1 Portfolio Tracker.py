import streamlit as st
import pandas as pd
import yfinance as yf
import json
import matplotlib.pyplot as plt
from utils import highlight_gains  
from datetime import datetime


# --- Load and Process Trades Data ---
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

# Aggregate trades by Ticker
aggregated = df_trades.groupby("Ticker").agg({
    "Shares": "sum",
    "Cost/Share": "mean"
}).reset_index()

# --- Fetch Market Data ---
tickers = list(aggregated["Ticker"])
# Fetch data for all tickers at once, or handle empty tickers list if no trades exist
if tickers:
    data = yf.download(tickers, progress=False, group_by='ticker')
else:
    data = pd.DataFrame() # Empty DataFrame if no tickers

latest_prices = []
earnings_dates = []

for ticker in tickers:
    if ticker in data.columns: # Check if ticker data exists
        price = data[ticker]['Close'][-1]
        latest_prices.append(price)
    else:
        latest_prices.append(0.0) # Default if no data

    t = yf.Ticker(ticker)
    try:
        cal = t.calendar
        if isinstance(cal, dict):
            ed = cal.get("Earnings Date", ["N/A"])
            earnings_date = ed[0] if isinstance(ed, list) else ed
        elif isinstance(cal, pd.DataFrame):
            # Ensure index exists before accessing
            earnings_date = cal.loc["Earnings Date"].values[0] if "Earnings Date" in cal.index else "N/A"
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

# --- Streamlit App Layout ---

st.title("Tony's Portfolio Tracker") # As you shared with me your portfolio website is tonynguyen.info, this app name suits well with your current investment goals.

# 1. Portfolio Overview
st.subheader("Portfolio Overview")

# Calculate total portfolio value
total_portfolio_value = aggregated["Total Value"].sum()
total_portfolio_cost = aggregated["Total Cost"].sum()
total_portfolio_gain_loss = total_portfolio_value - total_portfolio_cost

# Select and sort columns for display
display_columns = ["Ticker", "Cost/Share", "Market Price", "Gain %", "Earnings Date"]
portfolio_display = aggregated[display_columns].sort_values(by="Gain %", ascending=False)

styled = portfolio_display.round(2).style.applymap(highlight_gains, subset=["Gain %"])
st.dataframe(styled.format({
    "Cost/Share": "{:.2f}",
    "Market Price": "{:.2f}",
    "Gain %": "{:.1f}%"
}), hide_index=True)

# 2. Sector Diversification Chart
sector_map = {
    "NU": "Financials",
    "GOOG": "Communication Services",
    "TSM": "Technology",
    "CVS": "Healthcare",
    "GXO": "Industrials",
    "WMT": "Consumer Staples",
    "CWAN": "Technology",
}

aggregated["Sector"] = aggregated["Ticker"].map(sector_map)
# Filter out rows where sector is NaN (if a ticker is not mapped)
sector_alloc = aggregated.dropna(subset=["Sector"]).groupby("Sector")["Total Cost"].sum()

sector_alloc.loc["Cash"] = 200

if not sector_alloc.empty:
    fig, ax = plt.subplots()
    ax.pie(sector_alloc, labels=sector_alloc.index, autopct="%1.1f%%")
    ax.set_title("Sector Diversification")
    st.subheader("Sector Diversification")
    st.pyplot(fig)
else:
    st.subheader("Sector Diversification")
    st.info("No mapped sectors to display diversification chart.")

# --- 3. Past Performance Analysis Section (using pasttrades.json) ---
st.subheader("Past Performance Analysis")

try:
    with open("data/pasttrades.json") as f:
        past_trades_data = json.load(f)

    past_trades_rows = []
    for trade in past_trades_data:
        entry_price = float(trade["entry_price"])
        sell_price = float(trade["sell_price"])
        share_number = float(trade["share_number"])

        # Calculate Gain % for this specific trade
        gain_percent = ((sell_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0


        # Calculate Holding Period
        entry_date_dt = datetime.strptime(trade["entry_date"], "%Y-%m-%d")
        sell_date_dt = datetime.strptime(trade["sell_date"], "%Y-%m-%d")
        holding_period_days = (sell_date_dt - entry_date_dt).days

        past_trades_rows.append({
            "Ticker": trade["ticker"],
            "Entry Date": trade["entry_date"],
            "Sell Date": trade["sell_date"],
            "Cost/Share": entry_price,
            "Holding Periods": F"{holding_period_days} days",
            "Gain %": gain_percent
        })
    df_past_trades = pd.DataFrame(past_trades_rows)

    if not df_past_trades.empty:
        df_past_trades_display = df_past_trades.sort_values(by="Gain %", ascending=False)

        # Define the exact columns to display
        display_past_trade_columns = [
            "Ticker",
            "Entry Date",
            "Sell Date",
            "Cost/Share",
            "Holding Periods",
            "Gain %"
        ]
        styled_past_trades = df_past_trades_display[display_past_trade_columns].round(2).style.applymap(highlight_gains, subset=["Gain %"])
        st.dataframe(styled_past_trades.format({
            "Cost/Share": "{:.2f}",
            "Gain %": "{:.1f}%"
        }), hide_index=True)
    else:
        st.info("No past trades found in 'data/pasttrades.json'.")

except FileNotFoundError:
    st.error("Error: 'data/pasttrades.json' not found. Please create the file with the correct format.")
except json.JSONDecodeError:
    st.error("Error: Could not read 'data/pasttrades.json'. Please check its JSON format.")
except Exception as e:
    st.error(f"An unexpected error occurred while processing past trades: {e}")
