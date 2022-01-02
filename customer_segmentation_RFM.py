##Customer Segmentation RFM
#libraries and settings
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 20)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

##Task1 analysing and processing dataset
#1 read excel btw 2010-2011 and copy
df_ = pd.read_excel("datasets/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df  = df_.copy()

#2 Review of descriptive statistics
df.info()
df.head()
df.describe()
df.shape

#3 check NA
df.isnull().any()
df.isnull().sum()
df.isnull().any().sum()

#4 Drop NAs
df.dropna(inplace=True)

#5 Number of total unique goods
df["StockCode"].nunique()

#6 Amount of each unique good
df["StockCode"].value_counts()
##df.groupby("StockCode")["Description"].value_counts()

#7 Sort by amount of order
df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(20)

#8 Exclusion of cancelled("C") transactions
df = df[~df["Invoice"].str.contains("C", na=False)]


#9 Revenue per transaction
df["TotalRevenue"] = df["Quantity"]*df["Price"]

#Task2: Calculation of RFM metrics

# Recency: How recently a customer has made a purchase
# Frequency: How often a customer makes a purchase
# Monetary Value: How much money a customer spends on purchases
# Source: Investopedia

today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days, #recency
                                     "Invoice": lambda num: num.nunique(), #frequency
                                     "TotalRevenue": lambda TotalRevenue: TotalRevenue.sum()}) #monetary

##edit column names
rfm.columns = ["recency", "frequency", "monetary"]
rfm.head()
rfm = rfm[rfm["monetary"] > 0]

#task3 Calculating RFM scores

#recency score
rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels = [5,4,3,2,1])

#frequency score
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels = [1,2,3,4,5])
###rank(method="first") -> first: ranks assigned in order they appear in the array

#monetary score
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels = [1,2,3,4,5])

#creating RFM scores
rfm['RFM_SCORE'] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str))

# Segmentation of RFM scores

seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm.head()

#Task5 Interpretation of results and policy recommendations

# Grouping segments by means of RFM scores
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#Best Customers
rfm[rfm["segment"].str.contains("champions")].head()

#These customers in this segment spend relatively higher than other customers.
#Their transactions are relatively new and they purchased recently.
#Recommendations: Increase communications and analyze individual preferences.

#High-spending New Customers
rfm[rfm["segment"].str.contains("potential_loyalists")].head()
#They purchased recently and spent relatively high.
#recommendations: There should be specific incentives to keep them
#interacted with the business.

#Low-Spending Active Loyal Customers
rfm[rfm["segment"].str.contains("need_attention")].head()
#They purchased frequently but spent lower than other prior segments.
#Recommendation: Special discounts could make them spend higher.

#Reference: https://www.optimove.com/resources/learning-center/rfm-segmentation

# write loyal_customers to excel
new_df = pd.DataFrame()
rfm[rfm["segment"].str.contains("loyal_customers")]
new_df["loyal_customer_id"] = rfm["segment"].str.contains("loyal_customers").index
new_df.head()

new_df.to_excel("loyal_customers.xls", index=False)








##########################################################################################
rfm.groupby("segment")["frequency"].mean().sort_values(ascending=False)

agg_rfm = rfm[["recency", "frequency",
               "monetary", "RFM_SCORE",
               "segment"]].groupby("segment")["recency", "frequency", "monetary"].mean()

agg_rfm = agg_rfm.reset_index()
agg_rfm.sort_values(by="recency", ascending=False)

agg_rfm.sort_values(by=["recency", "frequency", "monetary"],
                    ascending=[False, False, True])

agg_rfm.sort_values(by=["recency", "frequency", "monetary"],
                    ascending = [True, False, False])
