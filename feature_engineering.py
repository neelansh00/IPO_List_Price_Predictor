import pandas as pd
import numpy as np
import joblib
from market_data_scraper import market_data_scraper 
from datetime import datetime
from input_data_scraper import scrape_ipo_subscription_data_from_url

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
    #listing_date = pd.to_datetime(user_input["IPO Listing Date"], "%Y-%m-%d")
    listing_date = datetime.strptime(user_input["IPO Listing Date"], "%Y-%m-%d")
    start_date = pd.to_datetime(start_date)
    days_since_start = (listing_date - start_date).days
    ## Fetch market data of the day before listing
    #market_data = get_market_data_before_date(user_input["Listing_date"])
    #if market_data is None:
    #    raise ValueError("Market data could not be fetched.")

    # Date-based features
    month = listing_date.month
    day = listing_date.day
    dow = listing_date.weekday()
    #quarter = listing_date.
    quarter=(month - 1) // 3 + 1

    ## prepping the data types
    ipo_issue_size=float(user_input["IPO Issue Size"].replace("₹","").replace(" Cr",""))
    qib=float(user_input["QIB Subscription"].replace("x",""))
    nii=float(user_input["NII Subscription"].replace("x",""))
    rii=float(user_input["RII Subscription"].replace("x",""))
    total=float(user_input["Total Subscription"].replace("x",""))
    gmp=float(user_input["GMP on Allotment Date"].replace("₹",""))
    issue_price=float(user_input["IPO Price on Allotment Date"])

    # Prepare processed dict
    processed_data = {
        "IPO_size": ipo_issue_size,
        "Estimated_Price": issue_price+gmp,
        #"Estimated_Price": user_input["Estimated_Price"],
        "QIB": qib,
        "NII": nii,
        "RII": rii,
        "Total": total,
        "Prev_Vix_Close": user_input["VIX_CLOSE"],
        "Prev_Vix_change(%)": user_input["VIX_PERC_CHG"],
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
        "Prev_Nifty_Open" : user_input['NIFTY_OPEN'],
        "Prev_Nifty_High" : user_input['NIFTY_HIGH'],
        "Prev_Nifty_Low" : user_input['NIFTY_LOW'],
        "Prev_Nifty_Close" : user_input['NIFTY_CLOSE'],
        "Prev_Nifty_volume" : user_input['NIFTY_VOLUME'],
    }

    df = pd.DataFrame([processed_data])

    # Apply scaler only to columns scaler was trained on
    scaled_df = df.copy()
    scaled_df[scaler.feature_names_in_] = scaler.transform(df[scaler.feature_names_in_])

    processed_df = scaled_df[feature_order]
    return processed_df


'''
if __name__ == "__main__":
    url = "https://www.investorgain.com/ipo/hdb-financial/1276/"
    input_ipo_details_dict = scrape_ipo_subscription_data_from_url(url)
    output_dict = market_data_scraper(input_ipo_details_dict)
    processed_df=make_processed_df(output_dict)
    pd.set_option("display.max_columns",None)
    print(processed_df)
'''