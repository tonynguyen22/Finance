import requests
import pandas as pd
import streamlit as st

FMP_API_KEY = st.secrets["FMP_API_KEY"] 
ALPHA_API_KEY = st.secrets["ALPHA_API_KEY"] 

base_url = 'https://financialmodelingprep.com/api/v3/'

st.header('Financial Modeling Prep Stock Screener')

symbol = st.sidebar.text_input('Ticker:', value='MSFT')

financial_data = st.sidebar.selectbox(
    'Financial Data Type',
    options=[
        'income-statement', 'balance-sheet-statement', 'cash-flow-statement',
        'income-statement-growth', 'balance-sheet-statement-growth',
        'cash-flow-statement-growth', 'ratios-ttm', 'ratios',
        'financial-growth', 'quote', 'rating', 'enterprise-values',
        'key-metrics-ttm', 'key-metrics', 'historical-rating',
        'discounted-cash-flow', 'historical-discounted-cash-flow-statement',
        'historical-price-full', 'Historical Price smaller intervals'
    ]
)

if financial_data == 'Historical Price smaller intervals':
    interval = st.sidebar.selectbox('Interval', options=['1min', '5min', '15min', '30min', '1hour', '4hour'])
    financial_data = 'historical-chart/' + interval

url = f"{base_url}{financial_data}/{symbol}?apikey={FMP_API_KEY}"

response = requests.get(url)
data = response.json()
df = pd.DataFrame(data).T

st.write(df)