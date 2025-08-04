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

def calculate_monthly_interest(balance, apr=27.99):
    if balance <= 0:
        return 0.0
    monthly_rate = apr / 100 / 12  # Convert APR to decimal and monthly rate
    interest = balance * monthly_rate
    return round(interest, 2)

def accumulate_daily_balance(df):
    # Ensure 'date' is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])

    # Sum transactions per day
    daily_totals = df.groupby('date')['value'].sum().reset_index(name='daily_total')

    # Calculate cumulative balance
    daily_totals['cumulative_balance'] = daily_totals['daily_total'].cumsum()

    return daily_totals    

def add_interest_calculations(df,apr=27.99):
    # go through a dataframe and find repayments that have a remainding balance
    # look at the previous months records to get the daily balances
    # calculate the daily interest rate for that balance (apr/365)
    # multiply daily balance by the daily apr to get an output
    # sum and apply as a transaction for that date
    daily_apr = apr / 365
    for idx,row in df.iterrows():
        if row['category'] == 'Repayment':
            # it's a repayment check
            if row['balance'] > 0:
                # didn't pay all of it --> need to loop
                start_month = row['date'].month
                start_year = row['date'].year
                row_index = idx
                for row_index in range(idx - 1, -1, -1):
                    current_month = df.loc[row_index,'date']
                    if current_month.year != start_year or current_month.month != start_month:
                        # changed --> use this index to grab
                        break
                # start at the idx and loop backwards until getting to the change_index
                accumulative_balance = 0.0
                accumulative_interest = 0.0                
                backward_idx = idx
                for backward_idx in range(idx -1, -1,-1):
                    if backward_idx == row_index:
                        break
                    # get ADB
                    accumulative_balance += df.loc[backward_idx,'balance']
                    # get balance * by daily APR
                    print(f"revert balance {df.loc[backward_idx,'balance']} {daily_apr}")
                    accumulative_interest += (df.loc[backward_idx,'balance'] * daily_apr)
                # dump for now
                print(f"balance {row['balance']} {accumulative_interest}")
    return df


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

        for trans_date in week_transaction_dates:
            day_index = (trans_date - start_date).days
            if day_index >= total_days:
                break

            # For first 180 days, normal spending + monthly repayment
            if day_index < 180:
                # Monthly repayment approx every 30 days on start day offset, only in first 180 days
                if day_index > 0 and (trans_date.day == start_date.day or 
                   trans_date.day == (start_date + timedelta(days=29)).day or 
                   trans_date.day == (start_date + timedelta(days=59)).day or
                   trans_date.day == (start_date + timedelta(days=89)).day or
                   trans_date.day == (start_date + timedelta(days=119)).day or
                   trans_date.day == (start_date + timedelta(days=149)).day):
                    if balance > 0:
                        repay_value = -round(random.uniform(0.75, 1.0) * balance, 2)
                        transactions.append({
                            'date': trans_date.strftime("%Y-%m-%d"),
                            'value': repay_value,
                            'description': random.choice(descriptions['Repayment']),
                            'category': 'Repayment',
                            'balance': round(balance + repay_value, 2)
                        })
                        balance += repay_value
                        # check
                        if balance > 0:
                            # add the interest charges
                            interest_add = calculate_monthly_interest(balance)
                            transactions.append({
                                'date': trans_date.strftime("%Y-%m-%d"),
                                'value': interest_add,
                                'description': 'Interest Charges',
                                'category': 'Fees',
                                'balance': round(balance + interest_add, 2)
                            })                            


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

if __name__ == "__main__":
    # today_str = (datetime.now() - timedelta(days=270)).strftime('%Y-%m-%-d')
    # df = generate_cc_transactions(today_str)
    # generate_chart(df)
    # load the df
     df = pd.read_json('../data/generated.2025-08-04.json',orient='records')
     add_interest_calculations(df)
