import csv
import json 
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_transaction_data(start_date, end_date, num_records=10):
    # Example transaction names
    transaction_names = ['Gas', 'Deposit', 'Grocery', 'Salary', 'Transfer', 'ATM', 'Refund', 'Subscription']

    # Start from July 1, 2025
    # start_date = datetime.strptime('2025-07-01', '%Y-%m-%d')
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    delta_days = (end_date - start_date).days

    results = []
    for i in range(num_records):
        # Random day in July 2025
        # day_offset = random.randint(0, 30)
        # date_str = (start_date + timedelta(days=day_offset)).strftime('%B %-d %Y')  # e.g., 'July 1 2025'
        random_days = random.randint(0, delta_days)
        transaction_date = start_date + timedelta(days=random_days)
        date_str = transaction_date.strftime('%B %-d %Y')  # e.g., 'July 1 2025'

        # Random transaction name
        name = random.choice(transaction_names)

        # Random value: Deposits can be positive, others negative
        if name in ['Deposit', 'Salary', 'Refund']:
            value = round(random.uniform(20, 2000), 2)
        else:
            value = round(random.uniform(-250, -1), 2)

        results.append({
            'date': date_str,
            'transaction name': name,
            'value': value
        })
    return results


def advanced_generator():
    # Configuration
    num_days = 120
    start_date = datetime.now()
    end_date = start_date + timedelta(days=num_days - 1)
    descriptions = [
        "Grocery Store", "Restaurant", "Gas Station", "Online Shopping",
        "Coffee Shop", "Pharmacy", "Gym", "Travel Booking", "Electronics",
        "Bookstore", "Streaming Service", "Taxi", "Clothing Store", "Utility Bill"
    ]

    # Generate dates for 120 days (one per day)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]

    # Pick (typically) 3-8 transactions per week, spaced across 120 days
    num_transactions = random.randint(num_days, num_days + 50)
    print(f"{num_transactions} {num_transactions - 4} {len(dates)}")
    # transaction_dates = sorted(random.sample(dates, k=num_transactions - 4))

    # Add one regular payment near the end of each month
    payment_days = []
    num_regular = num_transactions - 4
    transaction_dates = random.choices(dates, k=num_regular)
    transaction_dates += payment_days
    transaction_dates = sorted(transaction_dates)
    # loop
    for month in set([d.month for d in dates]):
        # Last day of each month or close
        last_day = max(date for date in dates if date.month == month)
        day_before = last_day - timedelta(days=random.randint(0, 2))
        payment_days.append(day_before)
    transaction_dates += payment_days
    transaction_dates = sorted(transaction_dates)

    # Prepare list for DataFrame
    records = []
    balance = 0

    for date in transaction_dates:
        if date in payment_days:
            description = "Monthly Payment"
            value = -random.randint(800, 2500)   # Credit (negative value decreases balance)
        else:
            description = random.choice(descriptions)
            value = random.randint(10, 400)      # Debit (positive value increases balance)
            # Occasionally generate a refund/credit
            if random.random() < 0.05:
                value = -random.randint(5, 200)
                description = f"Refund - {description}"
        balance += value
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "transaction description": description,
            "value": value,
            "balance": balance
        })

    df = pd.DataFrame(records)
    return df

def generate_cc_transactions(
    start_date='2025-03-02',
    days=120,
    min_txn_per_week=5,
    max_txn_per_week=12,
    payment_interval=30,
    payment_percent=0.8
):
    categories = [
        'RESTAURANT', 'GROCERY STORE', 'ONLINE PURCHASE', 'COFFEE SHOP', 
        'GAS STATION', 'PHARMACY', 'ENTERTAINMENT', 'UTILITY BILL'
    ]
    # Value ranges for each category
    value_ranges = {
        'RESTAURANT': (20, 60),
        'GROCERY STORE': (40, 120),
        'ONLINE PURCHASE': (10, 80),
        'COFFEE SHOP': (3, 15),
        'GAS STATION': (30, 70),
        'PHARMACY': (10, 40),
        'ENTERTAINMENT': (20, 90),
        'UTILITY BILL': (100, 150),
    }

    transactions = []
    balance = 0.0
    dt = datetime.strptime(start_date, '%Y-%m-%d')
    
    dates = [dt + timedelta(days=i) for i in range(days)]
    week_indices = [i for i in range(0, days, 7)]

    # Allocate random # transactions to each week
    txns_per_week = []
    for _ in week_indices:
        txns_per_week.append(random.randint(min_txn_per_week, max_txn_per_week))
    # Map each day to whether to place a transaction on it
    # txn_dates = set()
    # for widx, wstart in enumerate(week_indices):
    #     possible = range(wstart, min(wstart+7, days))
    #     txn_days = random.sample(list(possible), txns_per_week[widx])
    #     txn_dates.update(txn_days)
    txn_dates = []
    for widx, wstart in enumerate(week_indices):
        possible = list(range(wstart, min(wstart+7, days)))
        num_txns = txns_per_week[widx]
        # Randomly assign transactions to days allowing multiple txns on the same day:
        chosen_days = random.choices(possible, k=num_txns)
        txn_dates.extend(chosen_days)    

    for i, cur_date in enumerate(dates):
        # Do purchases:
        if i in txn_dates:
            desc = random.choice(categories)
            val = round(random.uniform(*value_ranges[desc]), 2)
            val = -val  # Purchases are negative
            balance += val
            transactions.append({
                'date': cur_date.strftime('%Y-%m-%d'),
                'description': desc,
                'value': val,
                'balance': round(balance, 2),
            })
        # Payment every payment_interval days
        if (i + 1) % payment_interval == 0:
            if balance < 0:
                payment = round(-balance * payment_percent, 2)
                balance += payment
                transactions.append({
                    'date': cur_date.strftime('%Y-%m-%d'),
                    'description': 'PAYMENT',
                    'value': payment,
                    'balance': round(balance, 2),
                })
    return transactions


if __name__ == "__main__":
    results = generate_transaction_data('2025-05-01','2025-06-01',100)
    df = pd.DataFrame(results)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    # write it out
    df.to_parquet('./100.df.parquet',engine='pyarrow',compression='snappy',index=False)
    # get second set
    df = advanced_generator()
    df.to_parquet('./120.df.parquet',engine='pyarrow',compression='snappy',index=False)
    # get from the generator
    txn = generate_cc_transactions()
    df = pd.DataFrame(txn)
    df.to_parquet('./120.other.df.parquet',engine='pyarrow',compression='snappy',index=False)

