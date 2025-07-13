import streamlit as st

@st.cache_data(ttl=3600)
def fetch_api(url):
    import requests
    return requests.get(url).json()

def highlight_gains(val):
    try:
        val = float(str(val).replace(',', '').replace('%', ''))
        if val > 0:
            return 'color: green'
        elif val < 0:
            return 'color: red'
    except:
        return ''
    return ''
