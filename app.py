# ---------------- IMPORT ----------------
import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
crypto = pd.read_csv("crypto_prices.csv")
oil = pd.read_csv("oil_prices.csv")
stock = pd.read_csv("stock_prices.csv")

# ---------------- DATE CONVERSION ----------------
crypto["date"] = pd.to_datetime(crypto["date"])
oil["date"] = pd.to_datetime(oil["date"])
stock["date"] = pd.to_datetime(stock["date"])

# lowercase stock columns (important)
stock.columns = stock.columns.str.lower()

# ---------------- MERGE DATA ----------------
df = crypto.merge(oil, on="date", how="inner")
df = df.merge(stock, on="date", how="inner")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 📌 Navigation")
    page = st.radio("", [
        "📊 Market Overview",
        "📋 SQL Analysis",
        "🏆 Top 5 Crypto"
    ])

# ================= PAGE 1 =================
if page == "📊 Market Overview":

    st.markdown("# 📊 Cross-Market Overview")
    st.caption("Crypto • Oil • Stock Market | SQL-powered analytics")

    # -------- DATE FILTER --------
    col1, col2 = st.columns(2)
    start = col1.date_input("Start Date", df["date"].min())
    end = col2.date_input("End Date", df["date"].max())

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # -------- FILTER DATA --------
    filtered = df[
        (df["date"] >= start) &
        (df["date"] <= end) &
        (df["coin_id"] == "bitcoin")
    ]

    # -------- KPI CALCULATION --------
    btc = filtered["price_inr_x"].mean()
    oil_avg = filtered["price_inr_y"].mean()
    sp500 = filtered[filtered["ticker"] == "^GSPC"]["close"].mean()
    nifty = filtered[filtered["ticker"] == "^NSEI"]["close"].mean()

    # -------- ROUND VALUES --------
    btc_value = round(btc, 2) if pd.notna(btc) else 0
    oil_value = round(oil_avg, 2) if pd.notna(oil_avg) else 0
    sp500_value = round(sp500, 2) if pd.notna(sp500) else 0
    nifty_value = round(nifty, 2) if pd.notna(nifty) else 0

    # -------- KPI DISPLAY --------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("₿ Bitcoin Avg", f"{btc_value:.2f}")
    c2.metric("🛢 Oil Avg", f"{oil_value:.2f}")
    c3.metric("📉 S&P 500 Avg", f"{sp500_value:.2f}")
    c4.metric("📊 NIFTY Avg", f"{nifty_value:.2f}")

    st.markdown("---")

    # -------- TABLE --------
    st.markdown("### 📋 Daily Market Snapshot")

    # Prepare stock data
    sp500_df = stock[stock["ticker"] == "^GSPC"][["date", "close"]].rename(columns={"close": "sp500"})
    nifty_df = stock[stock["ticker"] == "^NSEI"][["date", "close"]].rename(columns={"close": "nifty"})

    # Merge
    table = crypto.merge(oil, on="date")
    table = table.merge(sp500_df, on="date", how="left")
    table = table.merge(nifty_df, on="date", how="left")

    # Filter
    table = table[
        (table["date"] >= start) &
        (table["date"] <= end) &
        (table["coin_id"] == "bitcoin")
    ]

    # Rename
    table = table.rename(columns={
        "price_inr_x": "bitcoin",
        "price_inr_y": "oil"
    })

    # Final columns
    table = table[["date", "bitcoin", "oil", "sp500", "nifty"]]

    # Display
    st.dataframe(table.sort_values("date", ascending=False).head(10), use_container_width=True)

# ================= PAGE 2 =================
elif page == "📋 SQL Analysis":

    st.markdown("# 📋 SQL Analysis Dashboard")
    st.caption("30 analytical queries across Crypto, Time Series, and Cross-Market")

    category = st.selectbox("Select Category", [
        "📊 Crypto Analysis",
        "📈 Time Series Analysis",
        "🔗 Cross-Market Analysis"
    ])

    # ================= CRYPTO =================
    if category == "📊 Crypto Analysis":

        option = st.selectbox("Choose Query", [
            "Top 3 Coins",
            "Top 5 Coins",
            "Lowest Price Coins",
            "Highest Volatility",
            "Lowest Volatility",
            "Average Price per Coin",
            "Max Price per Coin",
            "Min Price per Coin",
            "Coins Above Avg Price",
            "Coins Below Avg Price"
        ])

        grp = df.groupby("coin_id")["price_inr_x"]

        if option == "Top 3 Coins":
            res = grp.mean().sort_values(ascending=False).head(3)

        elif option == "Top 5 Coins":
            res = grp.mean().sort_values(ascending=False).head(5)

        elif option == "Lowest Price Coins":
            res = grp.mean().sort_values().head(5)

        elif option == "Highest Volatility":
            res = grp.std().sort_values(ascending=False).head(5)

        elif option == "Lowest Volatility":
            res = grp.std().sort_values().head(5)

        elif option == "Average Price per Coin":
            res = grp.mean().head(10)

        elif option == "Max Price per Coin":
            res = grp.max().head(10)

        elif option == "Min Price per Coin":
            res = grp.min().head(10)

        elif option == "Coins Above Avg Price":
            avg = df["price_inr_x"].mean()
            res = df[df["price_inr_x"] > avg].groupby("coin_id").size()

        elif option == "Coins Below Avg Price":
            avg = df["price_inr_x"].mean()
            res = df[df["price_inr_x"] < avg].groupby("coin_id").size()

        st.dataframe(res.reset_index())

    # ================= TIME SERIES =================
    elif category == "📈 Time Series Analysis":

        option = st.selectbox("Choose Query", [
            "Bitcoin Monthly Trend",
            "Ethereum Monthly Trend",
            "Bitcoin Yearly Avg",
            "Ethereum Yearly Avg",
            "Daily Price Change BTC",
            "Daily Price Change ETH",
            "Max BTC Price Day",
            "Min BTC Price Day",
            "Rolling Avg BTC",
            "Rolling Avg ETH"
        ])

        if option == "Bitcoin Monthly Trend":
            temp = df[df["coin_id"] == "bitcoin"].copy()
            temp["month"] = temp["date"].dt.to_period("M")
            res = temp.groupby("month")["price_inr_x"].mean()
            st.line_chart(res)

        elif option == "Ethereum Monthly Trend":
            temp = df[df["coin_id"] == "ethereum"].copy()
            temp["month"] = temp["date"].dt.to_period("M")
            res = temp.groupby("month")["price_inr_x"].mean()
            st.line_chart(res)

        elif option == "Bitcoin Yearly Avg":
            temp = df[df["coin_id"] == "bitcoin"].copy()
            temp["year"] = temp["date"].dt.year
            res = temp.groupby("year")["price_inr_x"].mean()
            st.bar_chart(res)

        elif option == "Ethereum Yearly Avg":
            temp = df[df["coin_id"] == "ethereum"].copy()
            temp["year"] = temp["date"].dt.year
            res = temp.groupby("year")["price_inr_x"].mean()
            st.bar_chart(res)

        elif option == "Daily Price Change BTC":
            temp = df[df["coin_id"] == "bitcoin"].copy()
            temp["change"] = temp["price_inr_x"].diff()
            st.line_chart(temp.set_index("date")["change"])

        elif option == "Daily Price Change ETH":
            temp = df[df["coin_id"] == "ethereum"].copy()
            temp["change"] = temp["price_inr_x"].diff()
            st.line_chart(temp.set_index("date")["change"])

        elif option == "Max BTC Price Day":
            res = df[df["coin_id"] == "bitcoin"].nlargest(1, "price_inr_x")

        elif option == "Min BTC Price Day":
            res = df[df["coin_id"] == "bitcoin"].nsmallest(1, "price_inr_x")

        elif option == "Rolling Avg BTC":
            temp = df[df["coin_id"] == "bitcoin"].copy()
            temp["rolling"] = temp["price_inr_x"].rolling(7).mean()
            st.line_chart(temp.set_index("date")["rolling"])

        elif option == "Rolling Avg ETH":
            temp = df[df["coin_id"] == "ethereum"].copy()
            temp["rolling"] = temp["price_inr_x"].rolling(7).mean()
            st.line_chart(temp.set_index("date")["rolling"])

        if 'res' in locals():
            st.dataframe(res)

    # ================= CROSS MARKET =================
    elif category == "🔗 Cross-Market Analysis":

        option = st.selectbox("Choose Query", [
            "BTC vs Oil Avg",
            "BTC vs SP500 Avg",
            "BTC vs NIFTY Avg",
            "Oil vs SP500 Avg",
            "BTC Correlation Oil",
            "BTC Correlation SP500",
            "BTC Correlation NIFTY",
            "ETH vs NASDAQ Trend",
            "BTC vs Oil Trend",
            "SP500 vs Oil Trend"
        ])

        if option == "BTC vs Oil Avg":
            res = pd.DataFrame({
                "Asset": ["Bitcoin", "Oil"],
                "Avg": [
                    df[df["coin_id"]=="bitcoin"]["price_inr_x"].mean(),
                    df["price_inr_y"].mean()
                ]
            })

        elif option == "BTC vs SP500 Avg":
            res = pd.DataFrame({
                "Asset": ["Bitcoin", "SP500"],
                "Avg": [
                    df[df["coin_id"]=="bitcoin"]["price_inr_x"].mean(),
                    df[df["ticker"]=="^GSPC"]["close"].mean()
                ]
            })

        elif option == "BTC vs NIFTY Avg":
            res = pd.DataFrame({
                "Asset": ["Bitcoin", "NIFTY"],
                "Avg": [
                    df[df["coin_id"]=="bitcoin"]["price_inr_x"].mean(),
                    df[df["ticker"]=="^NSEI"]["close"].mean()
                ]
            })

        elif option == "Oil vs SP500 Avg":
            res = pd.DataFrame({
                "Asset": ["Oil", "SP500"],
                "Avg": [
                    df["price_inr_y"].mean(),
                    df[df["ticker"]=="^GSPC"]["close"].mean()
                ]
            })

        elif option == "BTC Correlation Oil":
            res = df[["price_inr_x","price_inr_y"]].corr()

        elif option == "BTC Correlation SP500":
            temp = df[df["ticker"]=="^GSPC"]
            res = temp[["price_inr_x","close"]].corr()

        elif option == "BTC Correlation NIFTY":
            temp = df[df["ticker"]=="^NSEI"]
            res = temp[["price_inr_x","close"]].corr()

        elif option == "ETH vs NASDAQ Trend":
            temp = df[(df["coin_id"]=="ethereum") & (df["ticker"]=="^IXIC")]
            st.line_chart(temp.set_index("date")[["price_inr_x","close"]])

        elif option == "BTC vs Oil Trend":
            temp = df[df["coin_id"]=="bitcoin"]
            st.line_chart(temp.set_index("date")[["price_inr_x","price_inr_y"]])

        elif option == "SP500 vs Oil Trend":
            temp = df[df["ticker"]=="^GSPC"]
            st.line_chart(temp.set_index("date")[["close","price_inr_y"]])

        if 'res' in locals():
            st.dataframe(res)
# ================= PAGE 3 =================
elif page == "🏆 Top 5 Crypto":

    st.markdown("# 🏆 Top 5 Crypto Analysis")
    st.caption("Interactive analysis of top performing cryptocurrencies")

    # -------- DATE FILTER --------
    col1, col2 = st.columns(2)

    start = col1.date_input("Start Date", df["date"].min(), key="p3_start")
    end = col2.date_input("End Date", df["date"].max(), key="p3_end")

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # -------- FILTER DATA --------
    filtered = df[
        (df["date"] >= start) &
        (df["date"] <= end)
    ]

    # -------- TOP 5 COINS --------
    top5 = filtered.groupby("coin_id")["price_inr_x"] \
                   .mean() \
                   .sort_values(ascending=False) \
                   .head(5) \
                   .reset_index()

    top5.columns = ["Coin", "Average Price"]

    st.markdown("### 📊 Top 5 Coins (Avg Price)")
    st.dataframe(top5, use_container_width=True)

    # -------- COIN SELECTION --------
    coin = st.selectbox("Select Coin for Trend", top5["Coin"])

    # -------- CHART DATA --------
    chart_df = filtered[filtered["coin_id"] == coin]

    if chart_df.empty:
        st.warning("No data available for selected range")
    else:
        chart_df = chart_df.sort_values("date")

        st.markdown("### 📈 Price Trend")
        st.line_chart(chart_df.set_index("date")["price_inr_x"])