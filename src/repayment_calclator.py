import logging
import pandas as pd

logger = logging.getLogger(__name__)

# simple repayment calculator
def monthly_repayment(balance, months, monthly_spend=0,annual_rate=27.99):
    adjusted_balance = balance + (monthly_spend * int(months)) # include increment spend
    if annual_rate == 0:
        return balance / months

    monthly_rate = (annual_rate / 100) / 12
    payment = (adjusted_balance * monthly_rate) / (1 - (1 + monthly_rate) ** -int(months))
    return payment

def average_monthly_spend(df):
    # iterate over the data frame to analyze average monthly spend for last 90d/3m
    # use that average increment + balance + fees to calculate repayment plan
    
    idx = len(df.index) - 1
    # go in reverse to find last possible repayment
    while True:
        if df.loc[idx,'category'] == 'Repayment':
            # found it - stop
            break        
        idx -= 1 # decrement
    #idx is the last repayment, now go forward and build an average until each 'Fees' is paid
    monthly_totals = []
    monthly_total = 0
    idx += 1 # move past the repayment
    while (idx < len(df.index)):
        if df.loc[idx,'category'] == 'Fees':
            # end of the month
            monthly_totals.append(monthly_total) # add
            monthly_total = 0 # reset
        else:   
            monthly_total += df.loc[idx,'value']
        idx += 1 # increment
    # now have an array of monthly totals
    average = 0
    for monthly in monthly_totals:
        average += monthly
    return round(average / len(monthly_totals),2)
    # return average_monthly

# load and calculate payment
def get_repayment_plan_json(file_location,months,include_monthly=True):
    # load the up the file
    df = pd.read_json(file_location,orient='records')
    # get the last balance
    last_balance = df.tail(1)['balance'].values[0]
    # get the overhead
    monthly_overhead = 0.0
    if include_monthly:
        monthly_overhead = average_monthly_spend(df)
    # calculate
    return monthly_repayment(last_balance,months,monthly_spend=monthly_overhead)


if __name__ == "__main__":
    # lets try a starter
    # open up the dataframe
    df = pd.read_json('./data/generated.2025-08-06.complete.json',orient='records')
    # get the last balance
    last_balance = df.tail(1)['balance']
    # get average spend
    monthly_overhead = average_monthly_spend(df)
    # calculate repayment
    print(f"3 months {monthly_repayment(df.tail(1)['balance'],27.99,3,monthly_overhead)}")
    print(f"6 months {monthly_repayment(df.tail(1)['balance'],27.99,6,monthly_overhead)}")
    print(f"12 months {monthly_repayment(df.tail(1)['balance'],27.99,12,monthly_overhead)}")
    print(f"24 months {monthly_repayment(df.tail(1)['balance'],27.99,24,monthly_overhead)}")
