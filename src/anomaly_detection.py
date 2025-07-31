import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

def detect_anomalous_transactions(df, column_names=['description_id','value'], contamination=0.05):
    # Prepare the data for modeling
    # X = df[[column_name]]
    X = df[column_names]
    # X = df[df[column_name] < 0][[column_name]]
    # Initialize the Isolation Forest model
    model = IsolationForest(contamination=contamination, random_state=42)
    # Fit the model and predict anomalies
    df['is_anomaly'] = model.fit_predict(X)

    # Map the predictions: 1 for normal, -1 for anomaly
    df['is_anomaly'] = df['is_anomaly'].map({1: False, -1: True})

    return df

def encode_description(df):
    #TODO encode the description field
    descriptions = df['description'].unique().tolist()
    # loop over the description list 
    for idx,row in df.iterrows():
        description = row['description']
        description_id = descriptions.index(description)
        df.at[idx,'description_id'] = description_id
    return df

def date_column(df):
    df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
    df['date_float'] = df['date'].astype('int64') / 1e9 #nanoseconds
    return df

def isolate_repayments(df):
    # extract all the positive values
    # use date and amount<->balance to determine anomaly or not
    positive_df = df[df['value'] > 0] # only positive values
    positive_df = positive_df[positive_df['description'] == 'PAYMENT'] # only payments
    # build the array
    X = positive_df[['date_float','value','balance']]
    # model
    model = IsolationForest(contamination=0.05, random_state=42)
    positive_df['is_anomaly'] = model.fit_predict(X)
    positive_df['is_anomaly'] = positive_df['is_anomaly'].map({1: False, -1: True})
    return positive_df

def linear_repayments(df,threshold=3):
    positive_df = df[df['value'] > 0] # only positive values
    positive_df = positive_df[positive_df['description'] == 'PAYMENT'] # only payments
    # build the array
    X = positive_df[['date_float','value']]
    y = positive_df[['balance']]

    model = LinearRegression()
    model.fit(X,y)
    # predict
    y_pred = model.predict(X)
    residuals = y - y_pred
    # anomalies
    std_res = np.std(residuals)
    positive_df['anomlay'] = residuals.abs() > threshold * std_res
    return positive_df


if __name__ == "__main__":
    # load up the data frame
    df = pd.read_parquet('../data/120.other.df.parquet')
    # encode
    df = encode_description(df)
    df = date_column(df)
    # execute
    df_negative = df[df['value'] < 0]
    df_negative = detect_anomalous_transactions(df_negative)
    pd.set_option('display.max_rows',None)
    # print
    print(df_negative)
    # do payments
    positive_df = isolate_repayments(df)
    print(positive_df)
    # use linear reg
    positive_df = linear_repayments(df)
    print(positive_df)
