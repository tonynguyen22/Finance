import streamlit as st
from utils import fetch_api
import pandas as pd

FMP_API_KEY = st.secrets["FMP_API_KEY"]
BASE_URL1 = "https://financialmodelingprep.com/stable"
BASE_URL2 = "https://financialmodelingprep.com/api/v3"

st.title("📊 Comparable Analysis")

ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL):", value="AAPL").upper()
run_analysis = st.button("Go")

if run_analysis and ticker:
    peer_url = f"{BASE_URL1}/stock-peers?symbol={ticker}&apikey={FMP_API_KEY}"
    peers_data = fetch_api(peer_url)

    if not peers_data or not isinstance(peers_data, list):
        st.error("No peer data returned.")
        st.stop()

    all_symbols = [ticker] + [item["symbol"] for item in peers_data if item["symbol"] != ticker][:5]
    st.write(f"✅ Peers found: {', '.join(all_symbols)}")

    ratios = []
    for sym in all_symbols:
        url = f"{BASE_URL2}/key-metrics-ttm/{sym}?apikey={FMP_API_KEY}"
        data = fetch_api(url)
        if isinstance(data, list) and len(data) > 0:
            record = data[0]
            ratios.append({
                "Symbol": sym,
                "P/E (TTM)": record.get("peRatioTTM"),
                "P/B (TTM)": record.get("pbRatioTTM"),
                "EV/EBITDA (TTM)": record.get("enterpriseValueOverEBITDATTM")
            })

    if not ratios:
        st.error("No ratio data found.")
        st.stop()

    selected = pd.DataFrame(ratios)
    st.subheader("Peer Valuation Comparison")
    st.dataframe(selected.round(1).set_index("Symbol"))

    pe_history_url = f"{BASE_URL2}/ratios/{ticker}?limit=20&apikey={FMP_API_KEY}"
    pe_history_data = fetch_api(pe_history_url)

    try:
        pe_values = [x["priceEarningsRatio"] for x in pe_history_data if x["priceEarningsRatio"] is not None][:5]
        pe_avg = round(sum(pe_values) / len(pe_values), 1)

        pe_current = next((r["P/E (TTM)"] for r in ratios if r["Symbol"] == ticker), None)

        st.subheader(f"{ticker} Valuation vs Historical")
        st.metric("Current P/E", round(pe_current, 1) if pe_current is not None else "N/A")
        st.metric("5Y Avg P/E", pe_avg, delta=round(pe_current - pe_avg, 1) if pe_current is not None else "N/A")
    except:
        st.warning("Could not fetch historical P/E data.")
