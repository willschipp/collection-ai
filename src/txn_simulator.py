import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

def calculate_minimum_repayment(balance, apr=0.2799):
    # Monthly interest rate
    monthly_rate = apr / 12
    # Typical minimum payment rate (e.g., 2.1%)
    # min_payment_rate = 0.021
    min_payment_rate = monthly_rate
    
    # Calculate minimum payment as max of 2.1% of balance or $10
    min_payment = max(min_payment_rate * balance, 10)
    # Minimum payment can't be more than balance
    min_payment = min(min_payment, balance)
    
    return round(min_payment, 2)


#TODO add late fee element
def clean_up(df,starting_balance=0.0,apr=0.2799):
    # forward loop
    # add running daily balance for interest calcs
    # update eod balance based on previous day plus transactions
    daily_apr = apr / 365
    previous_balance = starting_balance
    accumulative_eod = 0
    is_repayment = False
    idx = 0
    days_since_repayment = 0
    while (idx + 1) < len(df.index):
    # for idx,row in df.iterrows():
        if is_repayment:
            # get if the previous value is 0
            if df.loc[idx-1,'balance'] > 0:
                # need to process interest
                # process
                charge = {
                    'date': df.loc[idx,'date'],
                    'value': round(accumulative_eod,2),
                    'description': 'Interest Charges',
                    'category': 'Fees',
                    'balance': round(df.loc[idx-1,'balance'] + accumulative_eod, 2),
                    'rolling_eod':0.0
                }            
                new_charge = pd.DataFrame([charge])
                upper_part = df.iloc[:idx, :]
                lower_part = df.iloc[idx:, :]
                df = pd.concat([upper_part, new_charge, lower_part], ignore_index=True)                
            # reset
            accumulative_eod = 0 # always reset
            is_repayment = False
            days_since_repayment = 0 # reset
        elif is_repayment == False and days_since_repayment >= 30:
            # add an interest charge          
            # need to process interest
            # process
            charge = {
                'date': df.loc[idx,'date'],
                'value': round(accumulative_eod,2),
                'description': 'Interest Charges',
                'category': 'Fees',
                'balance': round(df.loc[idx-1,'balance'] + accumulative_eod, 2),
                'rolling_eod':0.0
            }            
            new_charge = pd.DataFrame([charge])
            upper_part = df.iloc[:idx, :]
            lower_part = df.iloc[idx:, :]
            df = pd.concat([upper_part, new_charge, lower_part], ignore_index=True)                
            accumulative_eod = 0 # always reset
            is_repayment = False
            days_since_repayment = 0 # reset
        else:
            if df.loc[idx,'category'] == 'Repayment':
                is_repayment = True # so the next loop will calculate interest if needed
            # get balance
            df.at[idx,'balance'] = round(previous_balance + df.loc[idx,'value'], 2)
            previous_balance = df.loc[idx,'balance'] # set for the next loop
            df.at[idx,'eod_interest'] = round(previous_balance * daily_apr,2)
            df.at[idx,'rolling_eod'] = round(accumulative_eod + (round(previous_balance * daily_apr,2)),2)
            accumulative_eod += round(previous_balance * daily_apr,2)
            if idx - 1 > 0:
                if df.loc[idx-1,'date'] != df.loc[idx,'date']: # not the same date
                    days_since_repayment += 1
        #loop
        idx += 1
    return df

# randomly generate the transactions
def generate_cc_transactions(start_date_str,starting_balance=0.0,reduction=0.15):
    np.random.seed(42)
    random.seed(42)

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    total_days = 300  # 180 + 120 days

    categories = ['Groceries', 'Entertainment', 'Dining', 'Travel', 'Utilities', 'Repayment', 'Shopping', 'Others']
    descriptions = {
        'Groceries': ['Supermarket', 'Farmers Market', 'Grocery Store'],
        'Entertainment': ['Movie Theater', 'Concert', 'Streaming Service'],
        'Dining': ['Restaurant', 'Cafe', 'Fast Food'],
        'Travel': ['Taxi', 'Airline', 'Hotel'],
        'Utilities': ['Electric Bill', 'Water Bill', 'Internet Bill'],
        'Repayment': ['Credit Card Payment'],
        'Shopping': ['Mall', 'Online Store', 'Clothing'],
        'Others': ['Miscellaneous']
    }

    balance = starting_balance
    transactions = []

    total_expense_90_to_180 = 0
    expense_count_90_to_180 = 0

    def generate_dates_for_week(week_start):
        num_transactions = random.randint(5, 8)
        dates = []
        for _ in range(num_transactions):
            day_offset = random.randint(0, 6)
            trans_date = week_start + timedelta(days=day_offset)
            dates.append(trans_date)
        dates.sort()
        return dates

    for week in range(total_days // 7 + 1):
        week_start = start_date + timedelta(days=week*7)
        week_transaction_dates = generate_dates_for_week(week_start)
        
        current_month = week_start.month
        current_month_paid = False

        for trans_date in week_transaction_dates:            
            day_index = (trans_date - start_date).days
            if day_index >= total_days:
                break

            # get the month
            trans_month = trans_date.month

            # For first 180 days, normal spending + monthly repayment
            if day_index < 180:
                # Monthly repayment approx every 30 days on start day offset, only in first 180 days
                if day_index > 0 and (trans_date.day == start_date.day or 
                   trans_date.day == (start_date + timedelta(days=29)).day or 
                   trans_date.day == (start_date + timedelta(days=59)).day or
                   trans_date.day == (start_date + timedelta(days=89)).day or
                   trans_date.day == (start_date + timedelta(days=119)).day or
                   trans_date.day == (start_date + timedelta(days=149)).day):
                    if balance > 0 and current_month_paid == False and current_month == trans_month: # can pay
                        repay_value = -round(random.uniform(0.75, 1.0) * balance, 2)
                        transactions.append({
                            'date': trans_date.strftime("%Y-%m-%d"),
                            'value': repay_value,
                            'description': random.choice(descriptions['Repayment']),
                            'category': 'Repayment',
                            'balance': round(balance + repay_value, 2)
                        })
                        balance += repay_value
                        current_month_paid = True # paid this month

                # Avoid duplicate repayment on same day
                if not any(t['date'] == trans_date.strftime("%Y-%m-%d") and t['category'] == 'Repayment' for t in transactions):
                    category = random.choice([c for c in categories if c != 'Repayment'])
                    description = random.choice(descriptions[category])
                    value = round(random.uniform(5, 150), 2)
                    balance += value

                    # Accumulate spending for days 90-179 for later scaling
                    if 90 <= day_index < 180:
                        total_expense_90_to_180 += value
                        expense_count_90_to_180 += 1

                    transactions.append({
                        'date': trans_date.strftime("%Y-%m-%d"),
                        'value': value,
                        'description': description,
                        'category': category,
                        'balance': round(balance, 2)
                    })

            else:
                # Days 180-299: reduced spending at ~15% of avg daily spend in days 90-179, no repayments
                if expense_count_90_to_180 > 0:
                    avg_expense_90_179 = total_expense_90_to_180 / expense_count_90_to_180
                else:
                    avg_expense_90_179 = 50  # fallback

                scaled_avg = avg_expense_90_179 * reduction # reduction rate
                min_val = max(5, scaled_avg * 0.5)
                max_val = max(15, scaled_avg * 1.5)

                category = random.choice([c for c in categories if c != 'Repayment'])
                description = random.choice(descriptions[category])
                value = round(random.uniform(min_val, max_val), 2)
                balance += value

                transactions.append({
                    'date': trans_date.strftime("%Y-%m-%d"),
                    'value': value,
                    'description': description,
                    'category': category,
                    'balance': round(balance, 2)
                })

    df = pd.DataFrame(transactions)
    df = df.sort_values('date').reset_index(drop=True)
    return df

# create a simple line chart for quick visual check
def generate_chart(df,filename='./chart/generated.jpg'):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    plt.figure(figsize=(12,6))
    plt.plot(df['date'], df['balance'], marker='o', linestyle='-')
    plt.title('Credit Card Balance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Balance')
    plt.grid(True)
    plt.tight_layout()
    
    plt.savefig(filename, format='jpeg')
    plt.close()    

def generate():
    file_date_str = datetime.now().strftime('%Y-%m-%d')
    json_path = f'./data/generated.{file_date_str}.complete.json'
    today_str = (datetime.now() - timedelta(days=270)).strftime('%Y-%m-%-d')
    df = generate_cc_transactions(today_str)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date').reset_index(drop=True)
    df = clean_up(df)
    df.to_json(json_path,orient='records')
    generate_chart(df,f'./chart/{file_date_str}.generated.jpg')
    df.to_csv(f'./data/generated.{file_date_str}.complete.csv')
    # return the dataframe
    return df, json_path

if __name__ == "__main__":
    generate()
    
