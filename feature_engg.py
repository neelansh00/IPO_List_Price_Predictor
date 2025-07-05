# make_processed_df.py

import pandas as pd
import numpy as np
import joblib
from market_fetcher import get_market_data_before_date  # assumes this is in a separate file
from datetime import datetime

def make_processed_df(user_input: dict, scaler_path="models/scaler.pkl",feature_order_path="models/feature_order.pkl", start_date="2020-09-21"):
    """
    Creates a processed and scaled DataFrame from raw user input.

    Args:
        user_input (dict): Contains IPO listing date, issue price, GMP, and subscription info.
        scaler_path (str): Path to scaler.pkl
        start_date (str): Start date of your dataset to compute days_since_start

    Returns:
        pd.DataFrame: Processed and scaled dataframe
    """

    # Load scaler
    scaler = joblib.load(scaler_path)
    feature_order=joblib.load(feature_order_path)
    # Parse listing date
    listing_date = pd.to_datetime(user_input["Listing_date"])
    start_date = pd.to_datetime(start_date)
    days_since_start = (listing_date - start_date).days

    # Fetch market data of the day before listing
    market_data = get_market_data_before_date(user_input["Listing_date"])
    if market_data is None:
        raise ValueError("Market data could not be fetched.")

    # Date-based features
    month = listing_date.month
    day = listing_date.day
    dow = listing_date.dayofweek
    quarter = listing_date.quarter

    # Prepare processed dict
    processed_data = {
        "IPO_size": user_input["IPO_size"],
        "Estimated_Price": user_input["Issue_price"] + user_input["GMP"],
        #"Estimated_Price": user_input["Estimated_Price"],
        "QIB": user_input["QIB_subscription"],
        "NII": user_input["NII_subscription"],
        "RII": user_input["RII_subscription"],
        "Total": user_input["Total_subscription"],
        "Prev_Vix_Close": user_input["Prev_Vix_Close"],
        "Prev_Vix_change(%)": user_input["Prev_Vix_change(%)"],
        "days_since_start": days_since_start,
        "month_cos": np.cos(2 * np.pi * month / 12),
        "month_sin": np.sin(2 * np.pi * month / 12),
        "day_sin": np.sin(2 * np.pi * day / 31),
        "day_cos": np.cos(2 * np.pi * day / 31),
        "day_of_week_sin": np.sin(2 * np.pi * dow / 7),
        "day_of_week_cos": np.cos(2 * np.pi * dow / 7),
        "quarter_2": 1 if quarter == 2 else 0,
        "quarter_3": 1 if quarter == 3 else 0,
        "quarter_4": 1 if quarter == 4 else 0,
    }

    # Add market data
    processed_data.update(market_data)

    # Create DataFrame
    df = pd.DataFrame([processed_data])

    # Apply scaler only to columns scaler was trained on
    scaled_df = df.copy()
    scaled_df[scaler.feature_names_in_] = scaler.transform(df[scaler.feature_names_in_])

    processed_df = scaled_df[feature_order]
    return processed_df

'''if __name__ == "__main__":
    # Example user input
    test_input = {
        "Listing_date": "2024-06-28",
        "IPO_size": 860,
        "Issue_price": 245,
        "GMP": 27.5,
        "QIB_subscription": 0.16,
        "NII_subscription": 6.61,
        "RII_subscription": 2.86,
        "Total_subscription": 2.89,
        "Prev_Vix_Close" : 13.34,
        "Prev_Vix_change(%)" : 0.54
    }

    try:
        df = make_processed_df(test_input)
        print("\n✅ Processed DataFrame:")
        print(df.head())
        print(f"\n🧾 Shape: {df.shape}")
        print(f"🧩 Columns: {list(df.columns)}")

    except Exception as e:
        print("❌ Test failed with error:")
        print(e) '''
