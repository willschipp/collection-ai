import pandas as pd

#Summarize total spending ('value') per category from a DataFrame.
def summarize_category_spends(df):
    # summary = df.groupby('category')['value'].sum().reset_index()
    # summary = summary.sort_values(by='value', ascending=False).reset_index(drop=True)
    # return summary
    # Ensure 'date' is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract year-month string for grouping
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    
    summary = df.groupby(['year_month', 'category'])['value'].sum().reset_index()
    summary = summary.rename(columns={'value': 'total_spend'})
    summary = summary.sort_values(['year_month', 'total_spend'], ascending=[True, False]).reset_index(drop=True)
    return summary    

def summarize_category_spends_by_month(df, category=None):
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    if category is not None:
        df = df[df['category'] == category]

    summary = df.groupby(['year_month', 'category'])['value'].sum().reset_index()
    summary = summary.rename(columns={'value': 'total_spend'})
    summary = summary.sort_values(['year_month', 'total_spend'], ascending=[True, False]).reset_index(drop=True)
    return summary

if __name__ == "__main__":
    # load the data frame and dump it out
    df = pd.read_json('./data/generated.2025-08-06.complete.json',orient='records')
    # summarize
    summary = summarize_category_spends(df)
    print(summary)
    summary_repayments = summarize_category_spends_by_month(df,'Repayment')
    print(summary_repayments)
    summary_fee = summarize_category_spends_by_month(df,'Fees')
    print(summary_fee)    