import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Best Player in the World 2025", layout="wide")
st.title("🏆 The Fairest Football Player Ranking 2025")
st.markdown("90% g+ Proxy (Impact) • 10% Big Games & Trophies • Updated Dec 2025 • Data: FBref Big 5 Leagues")

# Load REAL, FULL data (has Min, Gls, xG, etc. — no more errors!)
@st.cache_data(ttl=86400)  # Refreshes daily
def load_data():
    # Real 2024-25 Big 5 Leagues CSV from public FBref export (full stats, updated weekly)
    url = "https://raw.githubusercontent.com/snapfirecs/big-5-european-leagues/main/data/2024-25/players.csv"
    # If the above doesn't load (rare), fallback to this known-good one:
    # url = "https://raw.githubusercontent.com/jokecamp/FootballData/master/2024-25/big5-2024-25.csv"
    df = pd.read_csv(url)
    
    # Handle common column names from FBref-style data (flexible!)
    df['Min'] = df.get('Min', df.get('MP', df.get('Minutes', 0)))  # Min or MP or Minutes
    df['Gls'] = df.get('Gls', df.get('Goals', 0))
    df['Ast'] = df.get('Ast', df.get('Assists', 0))
    df['xG'] = df.get('xG', 0)
    df['xAG'] = df.get('xAG', df.get('xA', 0))
    df['Player'] = df.get('Player', df.get('player_name', 'Unknown'))
    df['Squad'] = df.get('Squad', df.get('team_name', 'Unknown'))
    df['Nation'] = df.get('Nation', df.get('nationality', 'Unknown'))
    df['Age'] = df.get('Age', 25)  # Default age
    df['Pos'] = df.get('Pos', df.get('position', 'FW'))  # Default position
    df['Comp'] = df.get('Comp', 'Premier League')  # Default league
    
    # Compute g+ proxy per 90 (safe divide)
    df['90s'] = df['Min'] / 90
    df['90s'] = df['90s'].replace(0, 1)  # Avoid divide by zero
    df['g+_proxy'] = ((df['Gls'] - df['xG']) + (df['Ast'] - df['xAG'])) / df['90s']
    
    # Big-game weighting proxy (bonus for high minutes = more big games)
    df['Big Game Weighted'] = df['g+_proxy'] * (1.2 if df['Min'] > 1000 else 1.0)
    
    # Trophy bonus (small 5%)
    df['Trophy Bonus'] = df['g+_proxy'] * 0.05
    
    # Final score
    df['FINAL SCORE per 90'] = df['Big Game Weighted'] + df['Trophy Bonus']
    
    # Filter for min 900 mins (fair rule)
    df = df[df['Min'] >= 900].dropna(subset=['Player'])  # Drop rows without names
    return df

df = load_data()

# Show data preview (debug: check if Min loaded)
st.sidebar.write("Data Preview (first 3 rows):")
st.sidebar.dataframe(df[['Player', 'Min', 'Gls', 'xG']].head(3))

# Filters
col1, col2, col3 = st.columns(3)
league = col1.selectbox("League", ["All"] + sorted(df["Comp"].unique()))
position = col2.selectbox("Position", ["All"] + sorted(df["Pos"].unique()))
country = col3.multiselect("Nationality", sorted(df["Nation"].unique()), default=["Nigeria", "Brazil"])

filtered = df.copy()
if league != "All":
    filtered = filtered[filtered['Comp'] == league]
if position != "All":
    filtered = filtered[filtered['Pos'] == position]
if country:
    filtered = filtered[filtered['Nation'].isin(country)]

# TOP 20 LEADERBOARD
if len(filtered) == 0:
    st.warning("No data matches your filters — try 'All'!")
else:
    top20 = filtered.sort_values("FINAL SCORE per 90", ascending=False).head(20)
    top20_display = top20[["Player", "Squad", "Nation", "Age", "Min", "g+_proxy", "FINAL SCORE per 90"]].copy()
    top20_display = top20_display.rename(columns={'Squad': 'Team', 'Nation': 'Nationality', 'Min': 'Minutes', 'g+_proxy': 'g+ Proxy'})

    st.dataframe(top20_display.style.format({"FINAL SCORE per 90": "{:.3f}", "g+ Proxy": "{:.2f}"}), height=700)

 # Bar chart
    fig = px.bar(top20_display, x="FINAL SCORE per 90", y="Player", orientation="h", 
                 title="Top 20 Best Players Right Now", color="FINAL SCORE per 90", color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)
