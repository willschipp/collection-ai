import pandas as pd
from datetime import datetime
import random

# Example data to randomly select from for names and locations
first_names = ['John', 'Jane', 'Alex', 'Emily', 'Chris', 'Katie', 'Michael', 'Laura', 'David', 'Sarah']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Martinez', 'Wilson']
streets = ['Main St', '2nd Ave', '3rd Blvd', 'Park Lane', 'Oak St', 'Pine St', 'Maple Ave', 'Cedar Rd', 'Elm St', 'Washington St']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']

def random_date_of_birth(start_year=1950, end_year=2000):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    # Rough days per month approximation to avoid invalid dates
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"

def random_phone_number():
    return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

def generate():
    # Generate data
    data = []
    for i in range(1000000): # goal is 232,000,000
        person_id = i + 1
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        dob = random_date_of_birth()
        address = f"{random.randint(100, 9999)} {random.choice(streets)}"
        # city = cities[i]
        city = random.choice(cities)
        # state = states[i]
        state = random.choice(states)
        zip_code = f"{random.randint(10000, 99999)}"
        phone = random_phone_number()
        fico = random.randint(300, 850)
        today = datetime.now().date().strftime('%Y-%m-%d')
        
        data.append({'Person_ID': person_id,
                    'First_Name': first_name,
                    'Last_Name': last_name,
                    'Date_of_Birth': dob,
                    'Address': address,
                    'City': city,
                    'State': state,
                    'Zip_Code': zip_code,
                    'Phone_Number': phone,
                    'FICO_Score': fico,
                    'Date': today})

    credit_bureau_df = pd.DataFrame(data)
    return credit_bureau_df

if __name__ == "__main__":
    print(f"before {datetime.now()}")
    df = generate()
    print(f"after {datetime.now()}")
    # print(df)
    # save to parquet
    df.to_parquet(path="../data/cb.parquet",engine="pyarrow",compression="snappy")
