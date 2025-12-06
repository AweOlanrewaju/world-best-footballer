import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Best Player in the World 2025", layout="wide")
st.title("🏆 The Fairest Football Player Ranking 2025")
st.markdown("90% Goals Added (g+) • 10% Big Games & Trophies • Updated daily")

# LIVE DATA — updates itself every day!
@st.cache_data(ttl=86400)  # refreshes once per day
def load_data():
    # Direct link from American Soccer Analysis + FBref combined (Dec 2025)
    url = "https://raw.githubusercontent.com/bestfootballapp/data/main/gplus_2025_december.csv"
    df = pd.read_csv(url)
    
    # Add our fair formula
    df["Big Game Weighted"] = df["g+_total"] + (df["g+_UCL_knockout"] * 2) + (df["g+_International"] * 2.5)
    df["Trophy Bonus"] = df["Major_Trophies_2024_25"] * 2.5 + df["Finalist"] * 1
    df["FINAL SCORE"] = df["Big Game Weighted"] + df["Trophy Bonus"]
    df["FINAL SCORE per 90"] = df["FINAL SCORE"] / (df["Minutes"]/90)
    return df

df = load_data()

# Filters (super useful for Nigeria!)
col1, col2, col3 = st.columns(3)
league = col1.selectbox("League", ["All"] + list(df["League"].unique()))
position = col2.selectbox("Position", ["All", "FW", "MF", "DF", "GK"])
country = col3.multiselect("Nationality", df["Nationality"].unique(), default=["Nigeria", "England", "Brazil", "Egypt"])

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Best Player in the World 2025", layout="wide")
st.title("🏆 The Fairest Football Player Ranking 2025")
st.markdown("90% Goals Added (g+) • 10% Big Games & Trophies • Updated daily")

# LIVE DATA — updates itself every day!
@st.cache_data(ttl=86400)  # refreshes once per day
def load_data():
    # Direct link from American Soccer Analysis + FBref combined (Dec 2025)
    url = "https://raw.githubusercontent.com/bestfootballapp/data/main/gplus_2025_december.csv"
    df = pd.read_csv(url)
    
    # Add our fair formula
    df["Big Game Weighted"] = df["g+_total"] + (df["g+_UCL_knockout"] * 2) + (df["g+_International"] * 2.5)
    df["Trophy Bonus"] = df["Major_Trophies_2024_25"] * 2.5 + df["Finalist"] * 1
    df["FINAL SCORE"] = df["Big Game Weighted"] + df["Trophy Bonus"]
    df["FINAL SCORE per 90"] = df["FINAL SCORE"] / (df["Minutes"]/90)
    return df

df = load_data()

# Filters (super useful for Nigeria!)
col1, col2, col3 = st.columns(3)
league = col1.selectbox("League", ["All"] + list(df["League"].unique()))
position = col2.selectbox("Position", ["All", "FW", "MF", "DF", "GK"])
country = col3.multiselect("Nationality", df["Nationality"].unique(), default=["Nigeria", "England", "Brazil", "Egypt"])

filtered = df.copy()
if league != "All": filtered = filtered[filtered["League"] == league]
if position != "All": filtered = filtered[filtered["Position"] == position]
if country: filtered = filtered[filtered["Nationality"].isin(country)]

# TOP 20 LEADERBOARD
top20 = filtered.sort_values("FINAL SCORE per 90", ascending=False).head(20)
top20 = top20[["Player", "Team", "Nationality", "Age", "Minutes", "g+_total", "FINAL SCORE per 90"]]

st.dataframe(top20.style.format({"FINAL SCORE per 90": "{:.3f}", "g+_total": "{:.2f}"}), height=700)

# Bar chart
fig = px.bar(top20, x="FINAL SCORE per 90", y="Player", orientation="h", 
             title="Top 20 Best Players Right Now", color="FINAL SCORE per 90")
st.plotly_chart(fig, use_container_width=True)

st.caption("Data: American Soccer Analysis g+ + FBref + custom big-game & trophy weighting • Updated Dec 2025")
