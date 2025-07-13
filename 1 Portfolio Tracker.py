import streamlit as st
import pandas as pd
import yfinance as yf
import json
import matplotlib.pyplot as plt
from utils import highlight_gains # Đảm bảo file utils.py có hàm highlight_gains

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

st.title("Tony's Portfolio Tracker")

# 1. Portfolio Overview
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

# 2. Sector Diversification Chart
sector_map = {
    "NU": "Fintech",
    "GOOG": "Tech",
    "SOXX": "Semis",
    "TSM": "Semis",
    "CVS": "Healthcare",
    "GXO": "Logistics",
    # Add more mappings for your current portfolio tickers if needed
}

aggregated["Sector"] = aggregated["Ticker"].map(sector_map)
# Filter out rows where sector is NaN (if a ticker is not mapped)
sector_alloc = aggregated.dropna(subset=["Sector"]).groupby("Sector")["Total Value"].sum()

if not sector_alloc.empty:
    fig, ax = plt.subplots()
    ax.pie(sector_alloc, labels=sector_alloc.index, autopct="%1.1f%%")
    ax.set_title("Sector Diversification")
    st.subheader("Sector Diversification")
    st.pyplot(fig)
else:
    st.subheader("Sector Diversification")
    st.info("No mapped sectors to display diversification chart.")


# 3. Trade History
st.subheader("Trade History")
st.dataframe(df_trades.sort_values("Date", ascending=False).round(1))

## Plan for Future Portfolio ✨
st.subheader("Future Portfolio Plan")

# Technology
with st.expander("1. Technology (30%) - AI & Cloud Dominance"):
    st.markdown("""
    **Objective:** Focus on companies leading in Artificial Intelligence (AI) and cloud computing, key drivers of market growth.
    - **AI Infrastructure:** **NVDA** (NVIDIA), **SMCI** (Super Micro Computer), **ANET** (Arista Networks)
    - **Cloud & Software:** **MSFT** (Microsoft), **GOOGL** (Alphabet - Google), **CRWD** (CrowdStrike)
    """)

# Industrials
with st.expander("2. Industrials (15%) - Logistics & Automation"):
    st.markdown("""
    **Objective:** Benefit from industrial automation trends, infrastructure investment, and the development of digital supply chains.
    - **Logistics & Automation:** **GXO** (GXO Logistics), **HON** (Honeywell), **TDG** (TransDigm Group)
    - **Infrastructure:** **CAT** (Caterpillar), **DE** (Deere & Company)
    """)

# Financials
with st.expander("3. Financials (15%) - Payments & Diversified Services"):
    st.markdown("""
    **Objective:** Bet on the growth of electronic transactions and the stability of large financial institutions.
    - **Payments:** **V** (Visa), **MA** (Mastercard)
    - **Diversified Financials:** **BRK.B** (Berkshire Hathaway), **JPM** (JPMorgan Chase)
    """)

# Communication Services
with st.expander("4. Communication Services (10%) - Digital Content & Connectivity"):
    st.markdown("""
    **Objective:** Capture value from the explosion of digital content, online advertising, and user connectivity platforms.
    - **Digital Content & Ads:** **GOOGL** (Alphabet - Google), **META** (Meta Platforms), **NFLX** (Netflix)
    - **Networking:** **CMCSA** (Comcast)
    """)

# Healthcare
with st.expander("5. Healthcare (10%) - Innovation & Stability"):
    st.markdown("""
    **Objective:** A defensive sector with growth potential driven by biotech innovation and medical devices.
    - **Biotech & Pharma:** **LLY** (Eli Lilly), **JNJ** (Johnson & Johnson)
    - **Medical Devices:** **ISRG** (Intuitive Surgical), **ABT** (Abbott Laboratories)
    """)

# Utilities & Renewable Energy
with st.expander("6. Utilities & Renewable Energy (10%) - Powering the Future"):
    st.markdown("""
    **Objective:** Benefit from increasing energy demand (especially from AI data centers) and the global shift towards clean energy.
    - **Utilities:** **NEE** (NextEra Energy), **DUK** (Duke Energy)
    - **Renewable Energy:** **FSLR** (First Solar), **ENPH** (Enphase Energy)
    """)

# Consumer Discretionary
with st.expander("7. Consumer Discretionary (10%) - E-commerce & Lifestyle"):
    st.markdown("""
    **Objective:** Invest in companies benefiting from consumer spending on non-essential products and services, particularly e-commerce and travel.
    - **E-commerce & Brands:** **AMZN** (Amazon.com), **LULU** (Lululemon Athletica)
    - **Travel & Leisure:** **BKNG** (Booking Holdings), **MAR** (Marriott International)
    """)