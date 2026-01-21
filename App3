import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.title("5-Year Normed Price Comparison")

# --- Inputs ---
col1, col2 = st.columns(2)
ticker1 = col1.text_input("Ticker 1 (e.g., RELIANCE.NS)", "")
ticker2 = col2.text_input("Ticker 2 (e.g., TCS.NS)", "")

# Last 5 years monthly
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)

def get_monthly_adj_close(ticker: str) -> pd.Series:
    """
    Download last 5 years monthly adjusted close for a ticker.
    Returns a Series with Date index and Adj Close values.
    Raises ValueError if ticker is invalid or no data.
    """
    data = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1mo",
        auto_adjust=False,     # ensure 'Adj Close' column exists [web:9][web:13]
        progress=False,
        group_by="ticker"
    )

    # yfinance returns a DataFrame; for single ticker, use columns directly [web:22]
    if data.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    if "Adj Close" not in data.columns:
        raise ValueError(f\"'Adj Close' not available for '{ticker}' (check ticker or yfinance version)\")

    s = data["Adj Close"].dropna()
    if s.empty:
        raise ValueError(f"No adjusted close data for '{ticker}'")

    s.name = ticker
    return s

def normalize_series_to_100(s: pd.Series) -> pd.Series:
    """
    Normalize price series so first value = 100 for comparison. [web:15][web:18]
    """
    return (s / s.iloc[0]) * 100.0

# --- Action ---
if st.button("Compare"):
    error_msgs = []

    series_dict = {}
    for t in [ticker1, ticker2]:
        if not t:
            error_msgs.append("Both tickers must be provided.")
            continue
        try:
            s = get_monthly_adj_close(t)
            series_dict[t] = normalize_series_to_100(s)
        except Exception as e:
            error_msgs.append(str(e))

    if error_msgs:
        st.error("\n".join(error_msgs))
    else:
        # Align on common dates
        df_norm = pd.concat(series_dict.values(), axis=1).dropna()

        if df_norm.empty:
            st.error("No overlapping monthly data for the selected tickers.")
        else:
            st.subheader("Normed Adjusted Close (Start = 100)")
            fig, ax = plt.subplots(figsize=(10, 6))
            for col in df_norm.columns:
                ax.plot(df_norm.index, df_norm[col], label=col)

            ax.set_title("5-Year Monthly Normed Adjusted Close")
            ax.set_xlabel("Date")
            ax.set_ylabel("Index (Start = 100)")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)

            st.pyplot(fig)

            st.subheader("Underlying Normed Data")
            st.dataframe(df_norm.round(2))
