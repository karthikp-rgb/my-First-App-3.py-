import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# ---------------- Page Config ----------------
st.set_page_config(page_title="Stock Comparison Dashboard", layout="centered")
st.title("📊 5-Year Stock Performance Comparison")

st.write(
    "Compare two stocks across performance metrics like normalized returns, "
    "relative outperformance, CAGR, and maximum drawdown."
)

# ---------------- Ticker Selection ----------------
POPULAR_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "SBIN.NS", "LT.NS", "ITC.NS"
]

col1, col2 = st.columns(2)
ticker1 = col1.selectbox("Select Ticker 1", POPULAR_TICKERS, index=3)
ticker2 = col2.selectbox("Select Ticker 2", POPULAR_TICKERS, index=2)

# ---------------- Date Range ----------------
end_date = datetime.today()
start_date = end_date - timedelta(days=5 * 365)

# ---------------- Helper Functions ----------------
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


def calculate_cagr(s: pd.Series) -> float:
    years = (s.index[-1] - s.index[0]).days / 365
    return (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1


def max_drawdown(s: pd.Series) -> float:
    cumulative_max = s.cummax()
    drawdown = (s - cumulative_max) / cumulative_max
    return drawdown.min()

# ---------------- Action ----------------
if st.button("Compare Stocks"):
    with st.spinner("Fetching data and computing metrics..."):
        try:
            s1 = get_monthly_price(ticker1)
            s2 = get_monthly_price(ticker2)

            n1 = normalize_to_100(s1)
            n2 = normalize_to_100(s2)

            df = pd.concat([n1, n2], axis=1)

            # ---------------- Metrics ----------------
            cagr1 = calculate_cagr(s1)
            cagr2 = calculate_cagr(s2)

            dd1 = max_drawdown(s1)
            dd2 = max_drawdown(s2)

            # ---------------- Metrics Display ----------------
            # ---------------- Metrics Display ----------------
st.subheader("📌 Key Metrics")

m1, m2 = st.columns(2)

m1.metric(
    label=f"{ticker1} CAGR",
    value=f"{cagr1*100:.2f}%"
)
m1.caption(f"Max Drawdown: {dd1*100:.2f}%")

m2.metric(
    label=f"{ticker2} CAGR",
    value=f"{cagr2*100:.2f}%"
)
m2.caption(f"Max Drawdown: {dd2*100:.2f}%")

        

            # ---------------- Chart 1: Normalized Comparison ----------------
            st.subheader("📈 Normalized Price Comparison (Base = 100)")

            fig1, ax1 = plt.subplots()
            df.plot(ax=ax1)
            ax1.set_ylabel("Normalized Price")
            ax1.set_xlabel("Date")
            ax1.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig1)

            # ---------------- Chart 2: Relative Performance ----------------
            st.subheader("📊 Relative Performance (Outperformance)")

            diff = df[ticker1] - df[ticker2]

            fig2, ax2 = plt.subplots()
            ax2.plot(diff, label="Performance Difference", color="black")
            ax2.axhline(0, linestyle="--", linewidth=1)

            ax2.fill_between(
                diff.index, diff, 0,
                where=diff >= 0,
                interpolate=True,
                color="green",
                alpha=0.3,
                label=f"{ticker1} Outperformance"
            )
            ax2.fill_between(
                diff.index, diff, 0,
                where=diff < 0,
                interpolate=True,
                color="red",
                alpha=0.3,
                label=f"{ticker2} Outperformance"
            )

            ax2.set_ylabel("Normalized Difference")
            ax2.set_xlabel("Date")
            ax2.legend()
            ax2.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig2)

            # ---------------- CSV Download ----------------
            st.subheader("📥 Download Data")
            st.download_button(
                label="Download comparison data as CSV",
                data=df.to_csv().encode("utf-8"),
                file_name="stock_comparison.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(str(e))
