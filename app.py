import requests
import pandas as pd
import streamlit as st
from millify import millify  # pip install millify

# Load API keys securely from Streamlit secrets
FMP_API_KEY = st.secrets["FMP_API_KEY"]
ALPHA_API_KEY = st.secrets["ALPHA_API_KEY"]

# Base API URL
base_url = 'https://financialmodelingprep.com/api/v3/'

# Streamlit UI
st.header('Financial Modeling Prep Stock Screener')
symbol = st.sidebar.text_input('Ticker:', value='MSFT')

# Mapping of user-friendly labels to API values
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

# Sidebar options
millify_option = st.sidebar.checkbox('Millify large numbers', value=True)
highlight_negatives = st.sidebar.checkbox('Highlight negatives in red', value=True)

# API request
url = f"{base_url}{financial_data}/{symbol}?apikey={FMP_API_KEY}"
response = requests.get(url)
data = response.json()

# Convert to DataFrame
if isinstance(data, list):
    df = pd.DataFrame(data)
else:
    df = pd.DataFrame([data])

# Apply millify if enabled
if millify_option:
    def apply_millify(val):
        try:
            if isinstance(val, (int, float)):
                return millify(val, precision=2)
        except:
            return val
        return val
    df = df.applymap(apply_millify)

# Apply styling if enabled
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
    st.dataframe(df.T, use_container_width=True)
