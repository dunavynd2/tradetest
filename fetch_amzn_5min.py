# fetch_amzn_5min.py
import os
import yfinance as yf
import pandas as pd

def fetch_and_save_amzn_5min():
    """Fetches recent 5-minute intraday data for AMZN and saves to CSV."""
    print("Fetching 5-minute intraday data for AMZN...")
    
    # Fetch 5-minute data (limited lookback, typically ~60 days)
    # Using `period` is simpler than start/end for intraday
    data = yf.download(
        tickers="AMZN",
        interval="5m",
        period="60d",  # Max lookback for 5m data
        progress=False,
        ignore_tz=False  # Keep timezone info
    )
    
    if data.empty:
        print("No data retrieved.")
        return

    # Prepare DataFrame
    df = data.copy()
    df = df.reset_index()
    
    # Rename columns to lowercase
    df = df.rename(columns={
        'Datetime': 'timestamp',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Ensure timestamp is timezone-aware UTC
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # Select and order columns
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_file = 'data/amzn_5min.csv'
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} rows to {output_file}")

if __name__ == "__main__":
    fetch_and_save_amzn_5min()
