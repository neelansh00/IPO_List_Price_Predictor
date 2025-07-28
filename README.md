# IPO_List_Price_Predictor


####  User input: investor gain link of company ---> scrap the subscription closing date and then the subscription data of that date if not available yet output Subscription not completed yet ---> scrape the issue size , issue price , scrap the listing date and store in Listing_date will be used later to find sin cos transforms and days since start ---> scrape the GMP of the  allotment date ---> scrape nifty and vix data of allotment date itself from investing.com 


#### 1. User input link : https://www.investorgain.com/ipo/crizac-ipo/1308/
2. in this link from the <ipo name> IPO dates table scrape the basis of allotment date and the ipo listing date and IPO issue size
3. use ipo listing date to find sin cos transformations and days since start and the quarter 
4. in the same link scroll down and from IPO Bidding Live Updates from BSE, NSE table scrap qib nii rii and total 
5. go to https://www.investorgain.com/gmp/crizac-ipo/1308/ and scrap the ipo price and the gmp of the date stored in basis of allotment if the data of basis of allotment date not available fetch data of the date previous to it and 
6. use basis of allotment date to scrap nifty and vix data of that date from https://in.investing.com/indices/s-p-cnx-nifty-historical-data and for vix from https://in.investing.com/indices/india-vix-historical-data
7. store all this in data in dict and then the feature_engg.py does the sin cos tranfrom and the days since start and the quarter and the changes of datatypes and removing % signs and then scaling and then use to predict and then return prediction along with percentage increase or decrease from ipo issue price
8. Results achieved for all applied models :-
   Decision Tree 
    r2 score: 0.9685028271999611
    mae: 29.00333333333333
    mape: 0.12747883416135067
    rmse: 38.057506924828026
    ---------------------------------
    Random forest 
    r2 score: 0.9794702800690932
    mae: 24.98779333333336
    mape: 0.11079136084975467
    rmse: 30.72529496883637
    ---------------------------------
     XG Boost 
    r2 score: 0.9822383013444111
    mae: 18.219043477376303
    mape: 0.07536364984130016
    rmse: 28.578984790717133
