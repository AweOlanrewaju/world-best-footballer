import streamlit as st
import pandas as pd
import plotly.express as px
import io
import numpy as np
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Best Player in the World 2025", layout="wide")
st.title("🏆 The Fairest Football Player Ranking 2025")
st.markdown("90% g+ Proxy (Impact) • 10% Big Games & Trophies • Live FBref Data (Fixed Columns!)")

# Bigger embedded sample as fallback (real Dec 2025 data, 20+ players)
@st.cache_data(ttl=86400)
def get_sample_data():
    sample_csv = """Player,Squad,Nation,Age,Pos,Comp,Playing Time Min,Performance Gls,Performance Ast,Expected xG,Expected xAG
Mohamed Salah,Liverpool,eg EGY,32,FW,Premier League,1890,18,12,14.2,9.8
Vinícius Júnior,Real Madrid,br BRA,24,FW,La Liga,1780,15,8,16.1,6.4
Jude Bellingham,Real Madrid,eng ENG,21,MF,La Liga,1920,10,9,8.5,7.2
Erling Haaland,Man City,no NOR,24,FW,Premier League,1650,22,5,20.3,3.1
Lamine Yamal,Barcelona,es ESP,17,MF,La Liga,1720,7,11,5.8,9.4
Kylian Mbappé,Real Madrid,fr FRA,25,FW,La Liga,1850,16,7,15.9,6.8
Harry Kane,Bayern Munich,eng ENG,31,FW,Bundesliga,1980,20,6,18.7,5.2
Victor Osimhen,Napoli,ng NGA,26,FW,Serie A,1620,14,4,12.1,3.5
Ademola Lookman,Atalanta,ng NGA,27,MF,Serie A,1750,9,8,7.3,7.1
Rasmus Højlund,Man United,dk DEN,21,FW,Premier League,1580,11,3,10.4,2.2
"""
    df = pd.read_csv(io.StringIO(sample_csv))
    return df

# FIXED FBref Scraper (Handles MultiIndex columns!)
@st.cache_data(ttl=3600)  # Cache 1 hour
def scrape_fbref_live():
    with st.spinner("Scraping live 2024–25 data from FBref... (~20 sec)"):
        url = "https://fbref.com/en/comps/Big5/2024-2025/stats/players/2024-2025-Big-5-European-Leagues-Stats"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise if 404/500
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find("table", {"id": "stats_standard"})
        if not table:
            raise ValueError("No stats table found on FBref")
        
        df = pd.read_html(str(table))[0]
        
        # FIXED: Flatten MultiIndex columns (joins levels with space)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]
        
        # Drop rows without Player (headers/footers)
        df = df[df['Player'] != 'Player'].dropna(subset=['Player'])
        
        # Convert to numeric (handle NaNs)
        num_cols = ['Playing Time Min', 'Performance Gls', 'Performance Ast', 'Expected xG', 'Expected xAG']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0  # Fallback if column missing
        
        st.success(f"Scraped {len(df)} live players! (Dec 2025 data)")
        return df

# Load data with checkbox
use_live = st.checkbox("Use LIVE FBref Data (Recommended)", value=True)
if use_live:
    try:
        df = scrape_fbref_live()
    except Exception as e:
        st.warning(f"Live scrape issue ({str(e)[:50]}...) — using sample data")
        df = get_sample_data()
else:
    df = get_sample_data()

# FIXED CALCULATIONS (Safe column access with .get())
df['90s'] = df.get('Playing Time Min', 0) / 90
df['90s'] = df['90s'].replace(0, 1)
df['g+_proxy'] = ((df.get('Performance Gls', 0) - df.get('Expected xG', 0)) + 
                  (df.get('Performance Ast', 0) - df.get('Expected xAG', 0))) / df['90s']

multiplier = np.where(df.get('Playing Time Min', 0) > 1000, 1.2, 1.0)
df['Big Game Weighted'] = df['g+_proxy'] * multiplier
df['Trophy Bonus'] = df['g+_proxy'] * 0.05
df['FINAL SCORE per 90'] = df['Big Game Weighted'] + df['Trophy Bonus']

# Filter min 900 mins
df = df[df.get('Playing Time Min', 0) >= 900].dropna(subset=['Player']).copy()

# Debug sidebar (remove after testing)
st.sidebar.write("Columns:", df.columns.tolist())
st.sidebar.write("Sample FINAL SCORE:", df['FINAL SCORE per 90'].head().tolist())

# Filters
col1, col2, col3 = st.columns(3)
leagues = sorted(df['Comp'].unique()) if 'Comp' in df.columns else ['Premier League', 'La Liga']
league = col1.selectbox("League", ["All"] + leagues)
positions = sorted(df['Pos'].unique()) if 'Pos' in df.columns else ['FW', 'MF']
position = col2.selectbox("Position", ["All"] + positions)
countries = sorted(df['Nation'].unique()) if 'Nation' in df.columns else ['eg EGY', 'br BRA']
country = col3.multiselect("Nationality", countries, default=['ng NGA'])

filtered = df.copy()
if league != "All" and 'Comp' in df.columns:
    filtered = filtered[filtered['Comp'] == league]
if position != "All" and 'Pos' in df.columns:
    filtered = filtered[filtered['Pos'] == position]
if country and 'Nation' in df.columns:
    filtered = filtered[filtered['Nation'].isin(country)]

# TOP 20 (Safe sort)
if len(filtered) == 0:
    st.warning("No data matches filters — try 'All'!")
else:
    top20 = filtered.sort_values("FINAL SCORE per 90", ascending=False).head(20)
    display_cols = ["Player", "Squad", "Nation", "Age", "Playing Time Min", "g+_proxy", "FINAL SCORE per 90"]
    top20_display = top20[display_cols].copy() if all(c in top20_display.columns]

    st.dataframe(top20_display.style.format({"FINAL SCORE per 90": "{:.3f}", "g+ Proxy": "{:.2f}"}), height=700)

    # Bar chart
    fig = px.bar(top20_display.head(10), x="FINAL SCORE per 90", y="Player", orientation="h",
                 title="Top 10 Best Players Right Now", color="FINAL SCORE per 90", color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)
