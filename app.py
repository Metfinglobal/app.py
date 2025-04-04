
import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from datetime import datetime, timedelta

st.set_page_config(page_title="Nifty 50 RSI + VWAP Algo", layout="wide")
st.title("Nifty 50 Algo Backtester: RSI + VWAP Reversion")

# Parameters
nifty50_tickers = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "LT.NS", 
    "SBIN.NS", "AXISBANK.NS", "ITC.NS", "HINDUNILVR.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", 
    "WIPRO.NS", "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS", "MARUTI.NS", "ASIANPAINT.NS", 
    "ULTRACEMCO.NS", "NESTLEIND.NS", "TECHM.NS", "POWERGRID.NS", "GRASIM.NS", "NTPC.NS",
    "COALINDIA.NS", "ONGC.NS", "ADANIPORTS.NS", "CIPLA.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS",
    "JSWSTEEL.NS", "DRREDDY.NS", "HINDALCO.NS", "TATASTEEL.NS", "BPCL.NS", "HEROMOTOCO.NS",
    "BAJAJFINSV.NS", "INDUSINDBK.NS", "DIVISLAB.NS", "SBILIFE.NS", "BRITANNIA.NS", "SHREECEM.NS",
    "HDFCLIFE.NS", "APOLLOHOSP.NS", "UPL.NS", "TATACONSUM.NS", "M&M.NS", "HDFCAMC.NS"
]

selected_stock = st.selectbox("Choose a Nifty 50 Stock", nifty50_tickers)
interval = st.selectbox("Timeframe", ["15m", "5m", "1h"])
start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
end_date = st.date_input("End Date", datetime.now())

if st.button("Run Backtest"):
    with st.spinner("Fetching data and running strategy..."):
        df = yf.download(selected_stock, start=start_date, end=end_date, interval=interval)
        df.dropna(inplace=True)

        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        df['Signal'] = None

        position = False
        buy_price = 0
        trades = []

        for i in range(1, len(df)):
            if not position:
                if df['RSI'].iloc[i] < 30 and df['Close'].iloc[i] < df['VWAP'].iloc[i] * 0.98:
                    df.at[df.index[i], 'Signal'] = 'Buy'
                    buy_price = df['Close'].iloc[i]
                    position = True
            elif position:
                if df['Close'].iloc[i] >= buy_price * 1.03 or df['Close'].iloc[i] <= buy_price * 0.985:
                    df.at[df.index[i], 'Signal'] = 'Sell'
                    sell_price = df['Close'].iloc[i]
                    trades.append({
                        'Buy Price': buy_price,
                        'Sell Price': sell_price,
                        'Result': 'Win' if sell_price >= buy_price * 1.03 else 'Loss'
                    })
                    position = False

        st.subheader("Signal Chart")
        st.line_chart(df[['Close', 'VWAP']])

        trade_df = pd.DataFrame(trades)
        if not trade_df.empty:
            st.subheader("Trade Log")
            st.dataframe(trade_df)
            wins = trade_df[trade_df['Result'] == 'Win'].shape[0]
            total = trade_df.shape[0]
            success_rate = wins / total * 100 if total else 0
            st.metric("Total Trades", total)
            st.metric("Win Rate", f"{success_rate:.2f}%")
        else:
            st.info("No trades generated for the selected stock and timeframe.")
