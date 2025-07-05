import streamlit as st
import pickle
import joblib
from feature_engg import make_processed_df
from market_fetcher import get_market_data_before_date

# Load model
model = joblib.load("models/model.pkl")

# Streamlit UI
st.title("IPO Listing Price Predictor")

st.markdown("Enter the IPO details below:")

# Inputs
listing_date = st.date_input("Listing Date")
ipo_size = st.number_input("IPO Size (in Cr)", value=500)
issue_price = st.number_input("Issue Price", value=100)
gmp = st.number_input("GMP", value=20.0)
#est_price = st.number_input("Estimated Price", value=20.0)
qib = st.number_input("QIB Subscription", value=1.0)
nii = st.number_input("NII Subscription", value=1.0)
rii = st.number_input("RII Subscription", value=1.0)
total = st.number_input("Total Subscription", value=1.0)
prev_vix_close = st.number_input("Previous Day VIX", value=1.0)
prev_vix_change = st.number_input("Previous Day VIX Change (%)", value=1.0)

# Predict Button
if st.button("Predict Listing Price"):
    user_input = {
        "Listing_date": listing_date.strftime("%Y-%m-%d"),
        "IPO_size": ipo_size,
        "Issue_price": issue_price,
        "GMP": gmp,
        #"Estimated_Price" : est_price,
        "QIB_subscription": qib,
        "NII_subscription": nii,
        "RII_subscription": rii,
        "Total_subscription": total,
        "Prev_Vix_Close" : prev_vix_close,
        "Prev_Vix_change(%)" : prev_vix_change
    }

   
    try:
        # Fetch market data for display
        market_data = get_market_data_before_date(user_input["Listing_date"])

        if market_data is not None:
            st.markdown("### 🧾 Market Data (1 day before listing):")
            st.json(market_data)

        # Process user input and predict
        processed_df = make_processed_df(user_input)

        prediction = model.predict(processed_df)[0]
        st.success(f"💰 **Estimated Listing Price: ₹{round(prediction, 2)}**")

    except Exception as e:
        st.error(f"❌ Error during prediction: {e}")
