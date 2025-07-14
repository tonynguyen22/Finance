import finnhub as finnhub
import streamlit as st
FINN_API_KEY = st.secrets["FINHUB_API_KEY"]
finnhub_client = finnhub.Client(api_key=FINN_API_KEY)

print(finnhub_client.company_basic_financials('AAPL', 'all'))