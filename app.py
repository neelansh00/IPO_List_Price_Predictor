import streamlit as st
import pickle
import joblib
from input_data_scraper import scrape_ipo_subscription_data_from_url
from market_data_scraper import market_data_scraper
from feature_engineering import make_processed_df

# Load model
model = joblib.load("models/model.pkl")

# Streamlit UI
st.title("IPO Listing Price Predictor")

st.markdown("Enter the IPO URL from Investor Gain below:")

# Inputs
url = st.text_input("Enter IPO URL", type="default")
# Predict Button
if st.button("Predict Listing Price"):
    input_ipo_details_dict = scrape_ipo_subscription_data_from_url(url)
    if input_ipo_details_dict is None:
        st.error("Failed to scrape IPO details. Please check the URL or try again later.")
        st.stop()
    output_dict = market_data_scraper(input_ipo_details_dict)
    if output_dict is None:
        st.error("Failed to scrape market details. Please check the URL or try again later.")
        st.stop()


    st.success(f"💰 Output Dict {output_dict}**")

    processed_df=make_processed_df(output_dict)

   
    try:
        ## Fetch market data for display
        #market_data = get_market_data_before_date(user_input["Listing_date"])
#
        #if market_data is not None:
        #    st.markdown("### 🧾 Market Data (1 day before listing):")
        #    st.json(market_data)
#
        # Process user input and predict

        prediction = model.predict(processed_df)[0]
        st.success(f"💰 **Estimated Listing Price: ₹{round(prediction, 2)}**")

    except Exception as e:
        st.error(f"❌ Error during prediction: {e}")
