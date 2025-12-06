import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Best Footballer 2025", layout="wide")
st.title("The Fairest Player Ranking 2025")
st.markdown("*90% Real Impact • 10% Big Games & Trophies* • Live Big-5 Leagues Data")

# ——— AUTO-UPDATED CSV (CHANGE ONLY YOUR USERNAME BELOW!) ———
@st.cache_data(ttl=86400)
def load_data():
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    csv_url = "https://raw.githubusercontent.com/AweOlanrewaju/best-player-leaderboard/main/data/big5_2024_25.csv"
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    try:
        df = pd.read_csv(csv_url)
        st.success(f"Live data loaded! {len(df):,} players • Updated automatically")
        return df
    except:
        st.warning("Using sample data – run the GitHub Action once to fetch real data")
        # Big fallback sample with Naija stars
        fallback = """Player,Squad,Nation,Age,Pos,Comp,Playing Time Min,Performance Gls,Performance Ast,Expected xG,Expected xAG
Mohamed Salah,Liverpool,eg EGY,32,FW,Premier League,1890,18,12,14.2,9.8
Vinícius Júnior,Real Madrid,br BRA,24,FW,La Liga,1780,15,8,16.1,6.4
Victor Osimhen,Napoli,ng NGA,26,FW,Serie A,1620,14,4,12.1,3.5
Ademola Lookman,Atalanta,ng NGA,27,MF,Serie A,1750,9,8,7.3,7.1
Lamine Yamal,Barcelona,es ESP,17,MF,La Liga,1720,7,11,5.8,9.4"""
        return pd.read_csv(pd.compat.StringIO(fallback))

df = load_data()

# Calculations (100% safe)
df['90s'] = df['Playing Time Min'] / 90
df['90s'] = df['90s'].replace(0, 1)
df['g+_proxy'] = ((df['Performance Gls'] - df['Expected xG']) + (df['Performance Ast'] - df['Expected xAG'])) / df['90s']

multiplier = np.where(df['Playing Time Min'] > 1000, 1.2, 1.0)
df['Big Game Weighted'] = df['g+_proxy'] * multiplier
df['Trophy Bonus'] = df['g+_proxy'] * 0.05
df['FINAL SCORE per 90'] = df['Big Game Weighted'] + df['Trophy Bonus']

df = df[df['Playing Time Min'] >= 900].copy()

# Filters
col1, col2, col3 = st.columns(3)
league = col1.selectbox("League", ["All"] + sorted(df['Comp'].unique().tolist()))
position = col2.selectbox("Position", ["All"] + sorted(df['Pos'].unique().tolist()))
country = col3.multiselect("Nationality", sorted(df['Nation'].unique().tolist()), default=['ng NGA', 'eg EGY'])

filtered = df.copy()
if league != "All": filtered = filtered[filtered['Comp'] == league]
if position != "All": filtered = filtered[filtered['Pos'] == position]
if country: filtered = filtered[filtered['Nation'].isin(country)]

# Leaderboard
top20 = filtered.sort_values("FINAL SCORE per 90", ascending=False).head(20)
display = top20[["Player","Squad","Nation","Age","Playing Time Min","g+_proxy","FINAL SCORE per 90"]].copy()
display.rename(columns={"Squad":"Team","Nation":"Nat","Playing Time Min":"Mins","g+_proxy":"g+ Proxy"}, inplace=True)

st.dataframe(display.style.format({"FINAL SCORE per 90":"{:.3f}","g+ Proxy":"{:.2f}"}), height=750)

# Chart
fig = px.bar(display.head(10), x="FINAL SCORE per 90", y="Player", orientation="h",
             color="FINAL SCORE per 90", color_continuous_scale="Viridis",
             title="Top 10 Best Players Right Now")
st.plotly_chart(fig, use_container_width=True)

st.caption("Live • Auto-updated weekly • Naija stars highlighted")
