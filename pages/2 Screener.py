import streamlit as st
from utils import fetch_api
import pandas as pd
from millify import millify

FMP_API_KEY = st.secrets["FMP_API_KEY"]
base_url = 'https://financialmodelingprep.com/api/v3/'

st.header('Financial Modeling Prep Stock Screener')
symbol = st.sidebar.text_input('Ticker:')

if symbol:
    symbol = symbol.upper()
    data_options = {
        'Income Statement': 'income-statement',
        'Balance Sheet Statement': 'balance-sheet-statement',
        'Cash Flow Statement': 'cash-flow-statement',
        'Income Statement Growth': 'income-statement-growth',
        'Balance Sheet Growth': 'balance-sheet-statement-growth',
        'Cash Flow Growth': 'cash-flow-statement-growth',
        'Ratios TTM': 'ratios-ttm',
        'Ratios': 'ratios',
        'Financial Growth': 'financial-growth',
        'Quote': 'quote',
        'Rating': 'rating',
        'Enterprise Values': 'enterprise-values',
        'Key Metrics TTM': 'key-metrics-ttm',
        'Key Metrics': 'key-metrics',
        'Discounted Cash Flow': 'discounted-cash-flow',
    }

    selected_label = st.sidebar.selectbox('Financial Data Type', options=list(data_options.keys()))
    financial_data = data_options[selected_label]

    millify_option = st.sidebar.checkbox('Millify large numbers', value=True)
    highlight_negatives = st.sidebar.checkbox('Highlight negatives in red', value=True)

    url = f"{base_url}{financial_data}/{symbol}?apikey={FMP_API_KEY}"
    data = fetch_api(url)

    df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

    if millify_option:
        def apply_millify(val):
            try:
                if isinstance(val, (int, float)):
                    return millify(val, precision=1)
            except:
                return val
            return val
        df = df.applymap(apply_millify)

    def highlight_negative(val):
        try:
            val_str = str(val).replace(',', '').replace('−', '-')
            if float(val_str) < 0:
                return 'color: red'
        except:
            pass
        return ''

    if highlight_negatives:
        styled_df = df.T.style.applymap(highlight_negative)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df.T.round(1), use_container_width=True)
