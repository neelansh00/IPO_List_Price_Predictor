import yfinance as yf
import pandas as pd

def get_market_data_before_date(listing_date_str: str):
    """
    Fetches Nifty 50 OHLCV and India VIX close/change data for the last trading day
    BEFORE the user-provided listing date (format: YYYY-MM-DD).

    Args:
        listing_date_str (str): IPO listing date in YYYY-MM-DD format

    Returns:
        dict or None: Dictionary of market data or None if not found
    """
    try:
        listing_date = pd.to_datetime(listing_date_str)
        
        # Fetch a buffer of 10 days before the listing date to handle weekends/holidays
        start_date = (listing_date - pd.Timedelta(days=10)).strftime('%Y-%m-%d')
        end_date = (listing_date - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

        # Fetch historical data
        nifty = yf.Ticker("^NSEI")
        #vix = yf.Ticker("^INDIAVIX")

        nifty_hist = nifty.history(start=start_date, end=listing_date)
        #vix_hist = vix.history(start=start_date, end=listing_date)

        if nifty_hist.empty :           # or vix_hist.empty or len(vix_hist) < 2
            print("❌ Could not find sufficient historical market data.")
            return None

        # Get the last available trading day before listing
        latest_nifty = nifty_hist.iloc[-1]
        #latest_vix = vix_hist.iloc[-1]
        #previous_vix_close = vix_hist.iloc[-2]['Close']

        #vix_change_pct = ((latest_vix['Close'] - previous_vix_close) / previous_vix_close) * 100

        market_data = {
            "Prev_Nifty_Open": latest_nifty['Open'],
            "Prev_Nifty_High": latest_nifty['High'],
            "Prev_Nifty_Low": latest_nifty['Low'],
            "Prev_Nifty_Close": latest_nifty['Close'],
            "Prev_Nifty_volume": int(latest_nifty['Volume']),
            #"Prev_Vix_Close": latest_vix['Close'],
            #"Prev_Vix_change(%)": vix_change_pct
        }

        return market_data

    except Exception as e:
        print(f"⚠️ Error fetching data: {e}")
        return None
    
'''if __name__ == "__main__":
    test_date = "2025-07-03"  # You can change this to any IPO date
    result = get_market_data_before_date(test_date)
    if result:
        print("\n✅ Market data fetched for use in processed_df:")
        print(pd.Series(result))
    else:
        print("❌ Market data fetch failed.")'''

## might have to change as vol. loaded by yf is coming as 0.00 sometimes
