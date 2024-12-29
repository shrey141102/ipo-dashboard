import math
import numpy as np
import pandas as pd
import re
from datetime import datetime

def parse_ipo_data(raw_text):
    lines = raw_text.strip().split('\n')
    parsed_data = []

    for line in lines:
        try:
            if line.startswith('Current Mainboard') or not line.strip():
                continue

            # Extract company name
            company_name_match = re.match(r'([A-Za-z\s&-]+) IPO', line)
            if not company_name_match:
                continue
            company_name = company_name_match.group(1).strip()

            # Extract status
            status_match = re.search(r'(Upcoming|Allotted|Listed|Close)', line)
            status = status_match.group(1) if status_match else 'Close'

            # Extract subscription percentage
            subscription_match = re.search(r'Sub:([\d.]+)x', line)
            subscription = float(subscription_match.group(1)) if subscription_match else None

            def calculate_price_gmp_listing(num_str, percentage):
                num_len = len(num_str)
                max_split = round(num_len / 3)
                max_split = min(max_split, 3)

                price = int(num_str[:max_split])

                # Refine the price assumption if it is unreasonably large
                if price > 4000:
                    price = int(num_str[:max_split - 1])

                gmp = round(price * (percentage / 100), 2)
                # listing_price = round(price + gmp, 2)

                return price, gmp

            match = re.search(r"(\d+(?:--\d+)?)\s+\(([\d.]+)%\)", line)
            # re.search(r"(\d+)\s+\(([\d.]+)%\)", line)
            if match:
                num_str = match.group(1).replace("--", "00")
                percentage = float(match.group(2))
                price, gmp = calculate_price_gmp_listing(num_str, percentage)

            ipo_price = price if price else None

            ipo_gmp = gmp if gmp else None

            # Extract issue size
            size_match = re.search(r'₹([\d,.]+)\s*Cr', line)
            ipo_size = float(size_match.group(1).replace(',', '')) if size_match else None

            # Extract lot size
            lot_size_match = math.floor(15000/price)
            lot_size = lot_size_match if lot_size_match else None

            # Extract dates
            dates = re.findall(r'(\d{1,2}-[A-Za-z]{3})', line)
            open_date = dates[0] if len(dates) > 0 else None
            close_date = dates[1] if len(dates) > 1 else None
            gmp_updated_date = dates[-1] if len(dates) > 2 else None

            data = {
                'ipo_name': company_name,
                'status': status,
                'subscription_percent': subscription,
                'ipo_price': ipo_price,
                'ipo_gmp': ipo_gmp,
                'ipo_size': ipo_size,
                'lot_size': lot_size,
                'open_date': open_date,
                'close_date': close_date,
                'gmp_updated_date': gmp_updated_date
            }
            parsed_data.append(data)

        except Exception as e:
            print(f"Error parsing line: {line}\n{str(e)}")
            continue

    df = pd.DataFrame(parsed_data)

    # Convert dates
    date_columns = ['open_date', 'close_date', 'gmp_updated_date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format='%d-%b', errors='coerce')
        current_year = datetime.now().year
        next_year = current_year + 1
        df[col] = df[col].apply(lambda x:
                                x.replace(year=next_year) if x is not pd.NaT and x.month < 6 else
                                x.replace(year=current_year) if x is not pd.NaT else x)

    return df

# Function to fill missing values
def fill_missing_values(df):
    for idx, row in df.iterrows():
        if pd.isna(row['ipo_gmp']) and row['subscription_percent']:
            if row['ipo_price']:
                df.at[idx, 'ipo_gmp'] = round(row['ipo_price'] * (row['subscription_percent'] / 100), 2)
        if pd.isna(row['ipo_price']) and row['ipo_gmp']:
            if row['subscription_percent']:
                df.at[idx, 'ipo_price'] = round(row['ipo_gmp'] / (row['subscription_percent'] / 100), 2)
    return df

# Function to save the DataFrame
def save_to_csv(df, filename='../ipo_data.csv'):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Main Execution
raw_data = ""
with open('../ipo_gmp.text') as f:
    raw_data = f.read()

df = parse_ipo_data(raw_data)
df = fill_missing_values(df)
save_to_csv(df)
print("\nParsed Data with Missing Values Filled:")
print(df)
