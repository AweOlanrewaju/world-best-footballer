import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Create data folder if needed
os.makedirs('data', exist_ok=True)

url = "https://fbref.com/en/comps/Big5/2024-2025/stats/players/2024-2025-Big-5-European-Leagues-Stats"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find("table", {"id": "stats_standard"})
df = pd.read_html(str(table))[0]

# Flatten columns
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [' '.join(col).strip() for col in df.columns.values]

df = df[df['Player'] != 'Player'].dropna(subset=['Player'])

# Numeric cols
num_cols = ['Playing Time Min', 'Performance Gls', 'Performance Ast', 'Expected xG', 'Expected xAG']
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Save to CSV
df.to_csv('data/big5_2024_25.csv', index=False)
print(f"Saved {len(df)} players to data/big5_2024_25.csv")
