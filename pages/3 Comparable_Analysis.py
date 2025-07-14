import streamlit as st
import pandas as pd
import finnhub
import datetime
import time
import numpy as np

# Cache client initialization to prevent re-creation
@st.cache_resource
def get_finnhub_client(api_key):
    return finnhub.Client(api_key=api_key)

FINN_API_KEY = st.secrets["FINHUB_API_KEY"]
finnhub_client = get_finnhub_client(FINN_API_KEY)

st.title("📊 Comparable Analysis")

ticker = st.text_input("Enter Ticker Symbol:").upper()
run_analysis = st.button("Go")

# Cached function to fetch company peers
@st.cache_data(ttl=3600) # Cache for 1 hour (3600 seconds)
def fetch_company_peers(symbol):
    try:
        return finnhub_client.company_peers(symbol)
    except Exception as e:
        st.error(f"Error fetching peer data from Finnhub: {e}")
        return []

# Cached function to fetch basic financial metrics
@st.cache_data(ttl=3600) # Cache for 1 hour
def fetch_basic_financials(symbol):
    try:
        return finnhub_client.company_basic_financials(symbol, 'all')
    except finnhub.FinnhubAPIException as e:
        if e.status_code == 403:
            st.error(f"Access Denied (403) for {symbol}. {symbol} will not be included.")
            return None
        else:
            st.warning(f"Could not fetch financial data for {symbol} from Finnhub: {e}")
            return None
    except Exception as e:
        st.warning(f"An unexpected error occurred fetching data for {symbol}: {e}")
        return None

if run_analysis and ticker:
    # 1. Fetch peer data from Finnhub
    peers_data = fetch_company_peers(ticker)

    if not peers_data:
        st.warning("No peer data returned from Finnhub. Analyzing only the entered ticker for historical data.")
        all_symbols = [ticker]
    else:
        unique_peers = [sym for sym in peers_data if sym != ticker]
        # Ensure the main ticker is always the first in all_symbols for structured display later
        all_symbols = [ticker] + unique_peers[:10] # Limit to 10 peers + main ticker for max 11 symbols

    st.write(f"✅ Symbols for analysis: {', '.join(all_symbols)}")

    peer_ratios = []
    # Collect data for all symbols including the main ticker for the overall table
    for sym in all_symbols:
        data = fetch_basic_financials(sym)
        if data and 'metric' in data:
            record = data['metric']
            peer_ratios.append({
                "Symbol": sym,
                "P/E (TTM)": record.get("peTTM"),
                "P/B (TTM)": record.get("pbQuarterly"),
                "ROE (TTM)": record.get("roeTTM"),
                "ROA (TTM)": record.get("roaTTM"),
            })
        else:
            if data is not None:
                st.warning(f"No metric data found for {sym}.")

    if not peer_ratios:
        st.error("No comparable ratio data found for any symbol.")
    else:
        selected_peers_df = pd.DataFrame(peer_ratios)
        st.subheader("Peer Valuation Comparison (Current TTM Ratios)")
        st.dataframe(selected_peers_df.set_index("Symbol").round(1))

        # Filter out the main ticker for mean and median calculations
        peers_only_df = selected_peers_df[selected_peers_df["Symbol"] != ticker]

        if not peers_only_df.empty:
            peer_means = peers_only_df.mean(numeric_only=True).to_dict()
            peer_medians = peers_only_df.median(numeric_only=True).to_dict()

            st.subheader(f"Mean and Median Ratios for Peers (excluding {ticker})")
            st.write("### Mean Ratios")
            mean_df = pd.DataFrame([peer_means])
            mean_df.index = ["Mean"] # Set index for display
            st.dataframe(mean_df.round(1))

            st.write("### Median Ratios")
            median_df = pd.DataFrame([peer_medians])
            median_df.index = ["Median"] # Set index for display
            st.dataframe(median_df.round(1))
        else:
            st.warning("No peer data available to calculate mean and median ratios (after excluding the main ticker).")

    # 2. Find historical P/E for the input stock
    st.subheader(f"Historical P/E Analysis for {ticker}")
    historical_data = fetch_basic_financials(ticker) # Use the cached function

    if historical_data and 'series' in historical_data and 'quarterly' in historical_data['series'] and 'peTTM' in historical_data['series']['quarterly']:
        pe_history_raw = historical_data['series']['quarterly']['peTTM']

        # Extract 'v' values and take the first 20 elements
        pe_values = [item['v'] for item in pe_history_raw if 'v' in item]

        if len(pe_values) >= 20:
            pe_values_for_average = pe_values[0:20]
            average_pe = np.mean(pe_values_for_average)

            st.metric(label=f"Current P/E (TTM) for {ticker}", value=f"{historical_data['metric']['peTTM']:.1f}")
            st.metric(label=f"Average P/E (most recent 20 periods) for {ticker}", value=f"{average_pe:.1f}", delta=f"{historical_data['metric']['peTTM'] - average_pe:.1f}")

            # Display the periods and values used for the average
            df_display = pd.DataFrame(pe_history_raw[0:20])
            st.write("Historical P/E (TTM) Values used for average:")
            st.dataframe(df_display.rename(columns={'period': 'Period', 'v': 'P/E (TTM)'}))
        else:
            st.warning(f"Not enough P/E history (less than 20 periods) to calculate the average for {ticker}.")
    else:
        st.warning(f"No historical P/E data found for {ticker}.")