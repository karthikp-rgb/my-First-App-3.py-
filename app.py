import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ---------------- UI ----------------
st.set_page_config(page_title="Stock Comparison", layout="centered")
st.title("5-Year Normed Price Comparison")

st.write(
    "Compare the 5-year performance of two stocks using normalized prices "
    "(base value = 100)."
)

# ---------------- Inputs ----------------
col1, col2 = st.columns(2)
ticker1 = col1.text_input("Ticker 1 (e.g., RELIANCE.NS)", "")
ticker2 = col2.text_input("Ticker 2 (e.g., TCS.NS)", "")

# ---------------- Date Range ----------------
end_date = datetime.today()
start_date = end_date - timedelta(days=5 * 365)

# ---------------- Data Functions ----------------
def get_monthly_price(ticker: str) -> pd.Series:
    data = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval="1mo",
        progress=False
    )

    if data.empty:
        raise ValueError(f"No data returned for {ticker}")

    price_col = "Adj Close" if "Adj Close" in data.columns else "Close"
    s = data[price_col].dropna()

    if s.empty:
        raise ValueError(f"No usable price data for {ticker}")

    s.name = ticker
    return s


def normalize_to_100(s: pd.Series) -> pd.Series:
    return (s / s.iloc[0]) * 100

# ---------------- Action ----------------
if st.button("Compare"):
    errors = []
    series_dict = {}

    with st.spinner("Fetching data and generating charts..."):
        for t in [ticker1, ticker2]:
            if not t:
                errors.append("Both tickers must be provided.")
                continue
            try:
                s = get_monthly_price(t)
                series_dict[t] = normalize_to_100(s)
            except Exception as e:
                errors.append(str(e))

    if errors:
        for err in errors:
            st.error(err)
    else:
        df = pd.concat(series_dict.values(), axis=1)

        # -------- Chart 1: Normalized Price Comparison --------
        st.subheader("📈 Normalized Price Comparison (Base = 100)")

        fig1, ax1 = plt.subplots()
        df.plot(ax=ax1)
        ax1.set_ylabel("Normalized Price")
        ax1.set_xlabel("Date")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()
        st.pyplot(fig1)

        # -------- Chart 2: Relative Performance Difference --------
        st.subheader("📊 Relative Performance (Difference)")

        diff = df.iloc[:, 0] - df.iloc[:, 1]

        fig2, ax2 = plt.subplots()
        diff.plot(ax=ax2, color="orange", label=f"{df.columns[0]} − {df.columns[1]}")
        ax2.axhline(0, linestyle="--", linewidth=1)
        ax2.set_ylabel("Performance Difference")
        ax2.set_xlabel("Date")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend()
        st.pyplot(fig2)
