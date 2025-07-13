import streamlit as st
import pandas as pd
import numpy as np

st.header("Valuation Dashboard & DCF")

symbol = st.text_input("Ticker", value="AAPL")
revenue_growth = st.slider("Revenue Growth Rate (%)", 0, 30, 10) / 100
net_margin = st.slider("Net Margin (%)", 0, 50, 20) / 100
terminal_growth = st.slider("Terminal Growth Rate (%)", 0, 5, 2) / 100
discount_rate = st.slider("Discount Rate (WACC %)", 5, 20, 10) / 100

revenue_now = st.number_input("Current Revenue ($B)", value=400.0)
shares_outstanding = st.number_input("Shares Outstanding (B)", value=16.0)

years = 5
revenue_forecast = [revenue_now * (1 + revenue_growth) ** i for i in range(1, years + 1)]
fcf_forecast = [rev * net_margin for rev in revenue_forecast]
terminal_value = fcf_forecast[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)

discount_factors = [(1 + discount_rate) ** i for i in range(1, years + 1)]
pv_fcf = [fcf / df for fcf, df in zip(fcf_forecast, discount_factors)]
pv_terminal = terminal_value / discount_factors[-1]
dcf_value = sum(pv_fcf) + pv_terminal
intrinsic_value = dcf_value * 1e9 / (shares_outstanding * 1e9)

st.subheader("DCF Output")
dcf_df = pd.DataFrame({
    "Year": [f"Year {i}" for i in range(1, years + 1)],
    "Revenue ($B)": revenue_forecast,
    "FCF ($B)": fcf_forecast,
    "Discount Factor": discount_factors,
    "PV FCF ($B)": pv_fcf,
})
st.dataframe(dcf_df.round(1))

st.metric("Terminal Value ($B)", round(terminal_value, 1))
st.metric("Enterprise Value ($B)", round(dcf_value, 1))
st.metric("Intrinsic Value / Share ($)", round(intrinsic_value, 1))
