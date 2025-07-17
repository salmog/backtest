# 01_download_data.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Tickers
tickers = ["QQQ", "SPY", "IWM", "IBIT"]

# Date ranges
end = datetime.today()
start_daily_weekly = end - timedelta(days=7*365)
start_hourly = end - timedelta(days=729)  # yfinance limit is 730 days MAX

# Download wrapper
def fetch_data(tickers, interval, start, end):
    df = yf.download(
        tickers=tickers,
        start=start.strftime('%Y-%m-%d'),
        end=end.strftime('%Y-%m-%d'),
        interval=interval,
        group_by='ticker',
        auto_adjust=False,
        threads=True
    )
    return df

# Ensure MultiIndex columns for vectorbt
def ensure_multiindex(df, tickers):
    if not isinstance(df.columns, pd.MultiIndex):
        df.columns = pd.MultiIndex.from_product([tickers, df.columns])
    return df

# Fetch data and fix column format
print("Downloading daily data...")
daily_df = ensure_multiindex(fetch_data(tickers, "1d", start_daily_weekly, end), tickers)

print("Downloading hourly data...")
hourly_df = ensure_multiindex(fetch_data(tickers, "1h", start_hourly, end), tickers)

print("Downloading weekly data...")
weekly_df = ensure_multiindex(fetch_data(tickers, "1wk", start_daily_weekly, end), tickers)

# Save as CSV
daily_df.to_csv("data_daily.csv")
hourly_df.to_csv("data_hourly.csv")
weekly_df.to_csv("data_weekly.csv")

print("✅ Done. CSVs saved.")
