# Load from repo CSV (auto-updated weekly — no scrape in app!)
@st.cache_data(ttl=86400)
def load_data():
    try:
        # GitHub raw URL to your CSV (replace YOURUSERNAME)
        csv_url = "https://raw.githubusercontent.com/AweOlanrewaju/best-player-leaderboard/main/data/big5_2024_25.csv"
        df = pd.read_csv(csv_url)
        st.success(f"Loaded {len(df)} players from auto-updated CSV! (Last: Dec 2025)")
        return df
    except:
        st.warning("CSV load failed — using sample")
        return get_sample_data()  # Fallback

df = load_data()
