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

# Calculate total portfolio value
total_portfolio_value = aggregated["Total Value"].sum()
total_portfolio_cost = aggregated["Total Cost"].sum()
total_portfolio_gain_loss = total_portfolio_value - total_portfolio_cost

st.write(f"**Total Portfolio Value:** ${total_portfolio_value:,.2f}")

# Display total portfolio gain/loss with color based on value
if total_portfolio_gain_loss >= 0:
    st.markdown(f"**Total Portfolio Gain/Loss:** <span style='color:green;'>${total_portfolio_gain_loss:,.2f}</span>", unsafe_allow_html=True)
else:
    st.markdown(f"**Total Portfolio Gain/Loss:** <span style='color:red;'>${total_portfolio_gain_loss:,.2f}</span>", unsafe_allow_html=True)

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
    "NU": "Financials",  # Fintech thường thuộc về Financials hoặc Technology, nhưng Financials rộng hơn và phù hợp với mục đích diversify.
    "GOOG": "Communication Services", # Google (Alphabet) được phân loại vào Communication Services vì các dịch vụ internet và quảng cáo.
    "SOXX": "Technology", # Semiconductors thuộc về Information Technology.
    "TSM": "Technology", # Semiconductors thuộc về Information Technology.
    "CVS": "Healthcare", # Healthcare vẫn là Healthcare.
    "GXO": "Industrials", # Logistics thường thuộc về Industrials.
    "QGEN": "Healthcare", # Healthcare vẫn là Healthcare.
    "WMT": "Consumer Staples", # Walmart là một công ty bán lẻ lớn, thuộc về Consumer Staples.
    "KO": "Consumer Staples", # Coca-Cola là một công ty đồ uống lớn, thuộc về Consumer Staples.
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

## Future Portfolio Plan
st.subheader("Future Portfolio Plan")
st.write("This proposed portfolio allocation for US investments focuses on growth with some defensive elements. This plan will be adjusted based on market conditions and personal goals.")

# Technology
with st.expander("1. Technology (20%) - AI & Cloud Dominance"):
    st.markdown("""
    **Objective:** Focus on companies leading in Artificial Intelligence (AI) and cloud computing, key drivers of market growth.
    - **AI Infrastructure:** :green[**TSM** (Taiwan Semiconductor Manufacturing)], :green[**SOXX** (iShares Semiconductor ETF)]
    """)

# Industrials
with st.expander("2. Industrials (15%) - Logistics & Automation"):
    st.markdown("""
    **Objective:** Benefit from industrial automation trends, infrastructure investment, and the development of digital supply chains.
    - **Logistics & Automation:** :green[**GXO** (GXO Logistics)]
    """)

# Financials
with st.expander("3. Financials (15%) - Payments & Diversified Services"):
    st.markdown("""
    **Objective:** Bet on the growth of electronic transactions and the stability of large financial institutions.
    - **Payments:** :green[**V** (Visa)]
    - **Diversified Financials:** :green[**JPM** (JPMorgan Chase)]
    """)

# Communication Services
with st.expander("4. Communication Services (10%) - Digital Content & Connectivity"):
    st.markdown("""
    **Objective:** Capture value from the explosion of digital content, online advertising, and user connectivity platforms.
    - **Digital Content & Advertising:** :green[**GOOG** (Alphabet - Google)]
    """)

# Healthcare
with st.expander("5. Healthcare (10%) - Innovation & Stability"):
    st.markdown("""
    **Objective:** A defensive sector with growth potential driven by biotech innovation and medical devices.
    - **Biotech & Pharma:** :green[**CVS** (CVS Health)], :green[**QGEN** (Qiagen NV)]
    """)

# Utilities & Renewable Energy
with st.expander("6. Utilities & Renewable Energy (10%) - Powering the Future"):
    st.markdown("""
    **Objective:** Benefit from increasing energy demand (especially from AI data centers) and the global shift towards clean energy.
    - **Utilities:** **DUK** (Duke Energy)
    - **Renewable Energy (Pure Play):** **FSLR** (First Solar), **ENPH** (Enphase Energy), :orange[**ICLN** (iShares Global Clean Energy ETF)]
    """)

# Consumer Staples
with st.expander("7. Consumer Staples (10%) - Stability & Essential Goods"):
    st.markdown("""
    **Objective:** Provide portfolio stability, consistent income, and defensiveness by investing in companies producing essential goods consumed regardless of economic conditions.
    - **Retail & Essentials:** :green[**WMT** (Walmart)]
    - **Food & Beverage:** :green[**KO** (Coca-Cola)]
    """)

# Consumer Discretionary
with st.expander("8. Consumer Discretionary (10%) - E-commerce & Lifestyle"):
    st.markdown("""
    **Objective:** Invest in companies benefiting from consumer spending on non-essential products and services, particularly e-commerce and travel.
    - **E-commerce & Brands:** :green[**AMZN** (Amazon.com)]
    - **Travel & Leisure:** :green[**MAR** (Marriott International)]
    - **Experiential Retail:** :green[**SBUX** (Starbucks)]
    """)
