import streamlit as st
import requests

API_KEY = "15485c15d5fa422bbf63f462c68df565"
BASE_URL = "https://public-api.birdeye.so"
HEADERS = {"X-API-KEY": API_KEY, "x-chain": "solana"}

st.set_page_config(page_title="SolRadar", page_icon="🔭", layout="wide")

# دالة جلب التوكنات الأكثر ترنداً
def get_trending(limit=20):
    url = f"{BASE_URL}/defi/token_trending"
    params = {"sort_by": "rank", "sort_type": "asc", "offset": 0, "limit": limit}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if r.status_code == 200 and r.text.strip():
            return r.json().get("data", {}).get("tokens", [])
    except Exception:
        pass
    return []

# دالة جلب أحدث التوكنات المطروحة
def get_new_listings(limit=20):
    url = f"{BASE_URL}/v2/tokens/new_listing"
    params = {"limit": limit, "meme_platform_enabled": "true"}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if r.status_code == 200 and r.text.strip():
            return r.json().get("data", {}).get("items", [])
    except Exception:
        pass
    return []

# دالة تحليل أمان التوكن
def get_security(address):
    url = f"{BASE_URL}/defi/token_security"
    try:
        r = requests.get(url, headers=HEADERS, params={"address": address}, timeout=10)
        if r.status_code == 200 and r.text.strip():
            return r.json().get("data", {})
    except Exception:
        pass
    return {}

# دالة جلب نظرة عامة على التوكن
def get_overview(address):
    url = f"{BASE_URL}/defi/token_overview"
    try:
        r = requests.get(url, headers=HEADERS, params={"address": address}, timeout=10)
        if r.status_code == 200 and r.text.strip():
            return r.json().get("data", {})
    except Exception:
        pass
    return {}

# تنسيق الأرقام الكبيرة
def fmt(num):
    if num is None:
        return "N/A"
    try:
        num = float(num)
        if num >= 1_000_000_000:
            return f"${num/1_000_000_000:.2f}B"
        if num >= 1_000_000:
            return f"${num/1_000_000:.2f}M"
        if num >= 1_000:
            return f"${num/1_000:.2f}K"
        return f"${num:.6f}"
    except Exception:
        return "N/A"

# تنسيق النسب المئوية مع إشارة اللون
def pct(num):
    if num is None:
        return "N/A"
    try:
        v = float(num)
        icon = "🟢" if v >= 0 else "🔴"
        return f"{icon} {v:.2f}%"
    except Exception:
        return "N/A"

st.title("🔭 SolRadar — Solana Meme Token Intelligence")
st.caption("Real-time trending & new token discovery powered by Birdeye Data API")

tab1, tab2, tab3 = st.tabs(["🔥 Trending Tokens", "🆕 New Listings", "🛡️ Security Scanner"])

with tab1:
    st.subheader("Top 20 Trending Tokens on Solana")
    with st.spinner("Fetching live data..."):
        tokens = get_trending(20)
    if tokens:
        rows = []
        for t in tokens:
            rows.append({
                "Rank": t.get("rank", "?"),
                "Name": t.get("name", "Unknown"),
                "Symbol": t.get("symbol", "?"),
                "Price": fmt(t.get("price")),
                "Market Cap": fmt(t.get("marketcap")),
                "24h Volume": fmt(t.get("volume24hUSD")),
                "24h Change": pct(t.get("volume24hChangePercent")),
                "Liquidity": fmt(t.get("liquidity")),
            })
        st.table(rows)
    else:
        st.error("Failed to fetch trending tokens.")

with tab2:
    st.subheader("Recently Listed Tokens")
    with st.spinner("Fetching new listings..."):
        listings = get_new_listings(20)
    if listings:
        rows2 = []
        for t in listings:
            rows2.append({
                "Name": t.get("name", "Unknown"),
                "Symbol": t.get("symbol", "?"),
                "Price": fmt(t.get("price")),
                "Liquidity": fmt(t.get("liquidity")),
                "Market Cap": fmt(t.get("marketcap")),
                "24h Change": pct(t.get("price24hChangePercent")),
            })
        st.table(rows2)
    else:
        st.warning("New listings not available on current API plan.")

with tab3:
    st.subheader("Token Security Scanner")
    st.write("Enter any Solana token address to check for red flags.")
    address_input = st.text_input("Token Address", placeholder="Paste token address here...")
    if st.button("Scan Token") and address_input:
        col1, col2 = st.columns(2)
        with st.spinner("Scanning..."):
            sec = get_security(address_input)
            over = get_overview(address_input)
        with col1:
            st.markdown("### Token Overview")
            if over:
                st.metric("Price", fmt(over.get("price")))
                st.metric("Market Cap", fmt(over.get("mc")))
                st.metric("24h Volume", fmt(over.get("v24hUSD")))
                st.metric("Holders", str(over.get("holder", "N/A")))
                st.metric("24h Change", pct(over.get("priceChange24hPercent")))
            else:
                st.warning("Could not fetch overview data.")
        with col2:
            st.markdown("### Security Analysis")
            if sec:
                creator_pct = float(sec.get("creatorPercentage") or 0)
                top10_pct = float(sec.get("top10HolderPercent") or 0)
                is_mintable = sec.get("mintAuthorityAddress", None)
                is_mutable = sec.get("metaplexUpdateAuthority", "")
                st.metric("Creator Holdings", f"{creator_pct*100:.1f}%")
                st.metric("Top 10 Holders", f"{top10_pct*100:.1f}%")
                st.metric("Mint Authority", "Active" if is_mintable else "Disabled")
                st.metric("Mutable Metadata", "Yes" if is_mutable else "No")
                risk = 0
                if creator_pct > 0.10:
                    risk += 2
                if top10_pct > 0.50:
                    risk += 2
                if is_mintable:
                    risk += 3
                if risk == 0:
                    st.success("LOW RISK — Looks relatively safe")
                elif risk <= 2:
                    st.warning("MEDIUM RISK — Proceed with caution")
                else:
                    st.error("HIGH RISK — Multiple red flags detected")
            else:
                st.warning("Could not fetch security data.")

st.divider()
st.caption("Built using Birdeye Data API | #BirdeyeAPI | @M_DataAnalyst")