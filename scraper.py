import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Create data folder
os.makedirs('data', exist_ok=True)

print("Starting FBref scrape...")

url = "https://fbref.com/en/comps/Big5/2024-2025/stats/players/2024-2025-Big-5-European-Leagues-Stats"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print(f"Fetching {url}...")
response = requests.get(url, headers=headers)
print(f"Status code: {response.status_code}")

if response.status_code != 200:
    raise Exception(f"Request failed: {response.status_code}")

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find("table", {"id": "stats_standard"})

if not table:
    raise Exception("No stats_standard table found!")

print("Parsing table...")
df = pd.read_html(str(table), header=1)[0]  # header=1 skips the first row (titles)

# FIXED: Flatten MultiIndex columns properly
df.columns = df.columns.droplevel(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
df.columns = [col.get_text(strip=True) if hasattr(col, 'get_text') else str(col) for col in df.columns]

# Drop invalid rows (headers, footers)
df = df[df['Player'] != 'Player'].dropna(subset=['Player'])

print(f"Raw rows after cleaning: {len(df)}")

# Convert to numeric (key columns for g+)
num_cols = ['Min', 'Gls', 'Ast', 'xG', 'xAG']  # FBref actual names
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    else:
        df[col] = 0
        print(f"Warning: Column '{col}' not found!")

# Save
csv_path = 'data/big5_2024_25.csv'
df.to_csv(csv_path, index=False)
print(f"SUCCESS: Saved {len(df)} players to {csv_path}")
