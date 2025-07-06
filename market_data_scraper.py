from input_data_scraper import scrape_ipo_subscription_data_from_url
import requests
from datetime import datetime,timedelta
import re
import yfinance as yf


def normalize_date(date_str):
    if not date_str:
        return None
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    for fmt in ("%d %b %Y", "%d-%m-%Y", "%d %B %Y", "%d-%b-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return None

def market_data_scraper(ipo_dict):
    basis_date = ipo_dict.get("Basis of Allotment Date")
    if not basis_date:
        print("No basis of allotment date found in input dict.")
        return ipo_dict

    # Convert YYYY-MM-DD to DD-MM-YYYY for the API
    try:
        date_obj = datetime.strptime(basis_date, "%Y-%m-%d")
        api_date = date_obj.strftime("%d-%m-%Y")
    except Exception as e:
        print(f"Date format error: {e}")
        return ipo_dict

    nifty_url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType=NIFTY%2050&from={api_date}&to={api_date}"
    vix_url = f"https://www.nseindia.com/api/historicalOR/vixhistory?from={api_date}&to={api_date}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    # Fetch NIFTY data from yfinance

    # Ensure date is in YYYY-MM-DD
    try:
        allot_date = datetime.strptime(basis_date, "%Y-%m-%d")
    except Exception as e:
        print(f"Date format error: {e}")
        return ipo_dict

    # yfinance requires a range: start is the date, end is next day
    start_date =allot_date.strftime("%Y-%m-%d")
    end_date = (allot_date+ timedelta(days=1)).strftime("%Y-%m-%d")

    nifty_ticker = "^NSEI"
    nifty_data = yf.download(nifty_ticker, start=start_date, end=end_date, progress=False)

    if not nifty_data.empty and start_date in nifty_data.index.strftime("%Y-%m-%d"):
        row = nifty_data.loc[nifty_data.index.strftime("%Y-%m-%d") == start_date].iloc[0]
        ipo_dict["NIFTY_OPEN"] = float(row["Open"].iloc[0])
        ipo_dict["NIFTY_HIGH"] = float(row["High"].iloc[0]) 
        ipo_dict["NIFTY_LOW"] = float(row["Low"].iloc[0])
        ipo_dict["NIFTY_CLOSE"] = float(row["Close"].iloc[0])
        ipo_dict["NIFTY_VOLUME"] = float(row["Volume"].iloc[0]) 
    else:
        ipo_dict["NIFTY_OPEN"] = ipo_dict["NIFTY_HIGH"] = ipo_dict["NIFTY_LOW"] = ipo_dict["NIFTY_CLOSE"] = ipo_dict["NIFTY_VOLUME"] = "N/A"
    # Fetch VIX Data
    try:
        r_vix = requests.get(vix_url, headers=headers, timeout=10)
        r_vix.raise_for_status()
        vix_json = r_vix.json()
        vix_data = None
        for rec in vix_json.get('data', []):
            rec_date = rec.get('EOD_TIMESTAMP')
            if rec_date:
                try:
                    rec_date_obj = datetime.strptime(rec_date, "%d-%b-%Y")
                    rec_date_short = rec_date_obj.strftime("%Y-%m-%d")
                except:
                    rec_date_short = rec_date[:10]
                if rec_date_short == basis_date:
                    vix_data = rec
                    break
        if vix_data:
            ipo_dict["VIX_CLOSE"] = vix_data.get("EOD_CLOSE_INDEX_VAL")
            ipo_dict["VIX_PERC_CHG"] = vix_data.get("VIX_PERC_CHG")
        else:
            ipo_dict["VIX_CLOSE"] = ipo_dict["VIX_PERC_CHG"] = "N/A"
    except Exception as e:
        print(f"Error fetching VIX data: {e}")
        ipo_dict["VIX_CLOSE"] = ipo_dict["VIX_PERC_CHG"] = "N/A"

    return ipo_dict

'''if __name__ == "__main__":
    url = "https://www.investorgain.com/ipo/hdb-financial/1276/"
    input_ipo_details_dict = scrape_ipo_subscription_data_from_url(url)
    output_dict = market_data_scraper(input_ipo_details_dict)
    print(output_dict)'''