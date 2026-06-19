import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
from datetime import datetime

st.set_page_config(
    page_title="ETF Ki Dukan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 0.9rem; }
.gain  { color: #00c853; font-weight: 600; }
.loss  { color: #ff1744; font-weight: 600; }
.flat  { color: #90a4ae; }
.section-title { font-size: 1.1rem; font-weight: 700; color: #e0e0e0;
                 border-left: 4px solid #00c853; padding-left: 8px; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Sector Map ─────────────────────────────────────────────────────────────────
SECTOR_MAP = {
    "NIFTYBEES":"Broad Market","BANKBEES":"Broad Market","SBINEQWETF":"Broad Market",
    "NIFTY100EW":"Broad Market","MULTICAP":"Broad Market","MONIFTY500":"Broad Market",
    "BSE500IETF":"Broad Market","AONETOTAL":"Broad Market","GROWWN200":"Broad Market",
    "ELM250":"Broad Market","TOP10ADD":"Broad Market","TOP15IETF":"Broad Market",
    "HDFCSENSEX":"Broad Market","MSCIINDIA":"Broad Market",
    "MIDCAPETF":"Midcap/Smallcap","HDFCSML250":"Midcap/Smallcap","SML100CASE":"Midcap/Smallcap",
    "MOM100":"Midcap/Smallcap","MIDCAP":"Midcap/Smallcap","MIDSMALL":"Midcap/Smallcap",
    "MIDSELIETF":"Midcap/Smallcap","MOMIDMTM":"Midcap/Smallcap","NEXT50IETF":"Midcap/Smallcap",
    "SMALLCAP":"Midcap/Smallcap",
    "ITBEES":"Sectoral","METALIETF":"Sectoral","PHARMABEES":"Sectoral",
    "PVTBANIETF":"Sectoral","PSUBNKBEES":"Sectoral","FMCGIETF":"Sectoral",
    "OILIETF":"Sectoral","AUTOIETF":"Sectoral","INFRAIETF":"Sectoral",
    "ENERGY":"Sectoral","BFSI":"Sectoral","FINIETF":"Sectoral",
    "HEALTHY":"Sectoral","CHEMICAL":"Sectoral","CONSUMER":"Sectoral","CONSUMBEES":"Sectoral",
    "ALPHA":"Factor/Smart Beta","QUAL30IETF":"Factor/Smart Beta","ALPL30IETF":"Factor/Smart Beta",
    "MOM30IETF":"Factor/Smart Beta","MOMENTUM50":"Factor/Smart Beta","MOMENTUM30":"Factor/Smart Beta",
    "LOWVOLIETF":"Factor/Smart Beta","VAL30IETF":"Factor/Smart Beta","ALPHAETF":"Factor/Smart Beta",
    "AXISVALUE":"Factor/Smart Beta","MOVALUE":"Factor/Smart Beta","NV20IETF":"Factor/Smart Beta",
    "TOP100CASE":"Factor/Smart Beta","FLEXIADD":"Factor/Smart Beta","AONETMMQ50":"Factor/Smart Beta",
    "MODEFENCE":"Thematic","DEFENCE":"Thematic","GROWWPOWER":"Thematic","GROWWRAIL":"Thematic",
    "GROWWEV":"Thematic","GROWWNET":"Thematic","MOREALTY":"Thematic","MOCAPITAL":"Thematic",
    "MAKEINDIA":"Thematic","TNIDETF":"Thematic","GROWWHOSPI":"Thematic",
    "ABSLPSE":"Thematic","CPSEETF":"Thematic","ICICIB22":"Thematic",
    "MON100":"International","MAFANG":"International","MAHKTECH":"International",
    "HNGSNGBEES":"International","MASPTOP50":"International","MONQ50":"International",
}

SECTOR_COLORS = {
    "Broad Market":     "#1565C0",
    "Midcap/Smallcap":  "#6A1B9A",
    "Sectoral":         "#00695C",
    "Factor/Smart Beta":"#E65100",
    "Thematic":         "#AD1457",
    "International":    "#00838F",
}

# ── Data Loading ───────────────────────────────────────────────────────────────
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "16hW9bFEhE8-yWZ98ja3XEtC8B4BZZKKI/export?format=csv&gid=947511781"
)

@st.cache_data(ttl=300, show_spinner=False)
def load_from_gsheet():
    resp = requests.get(SHEET_CSV_URL, allow_redirects=True, timeout=15)
    resp.raise_for_status()
    return resp.text

def build_df(raw_csv: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(raw_csv))
    df.columns = ["SYMBOL","UNDERLYING","OPEN","HIGH","LOW","LTP","VOLUME"]
    for col in ["OPEN","HIGH","LOW","LTP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["VOLUME"] = (df["VOLUME"].astype(str).str.replace(",","")
                    .astype(float).astype(int))
    df["CHG_PCT"]   = ((df["LTP"] - df["OPEN"]) / df["OPEN"] * 100).round(2)
    df["RANGE_PCT"] = ((df["HIGH"] - df["LOW"])  / df["LOW"]  * 100).round(2)
    df["SECTOR"]    = df["SYMBOL"].map(SECTOR_MAP).fillna("Other")
    df["SIGNAL"]    = df["CHG_PCT"].apply(
        lambda x: "▲" if x > 0 else ("▼" if x < 0 else "—"))
    return df

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 ETF Ki Dukan")
    st.caption("NSE/BSE ETF Market Dashboard")
    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()

    st.subheader("Filters")
    all_sectors = ["All"] + sorted(set(SECTOR_MAP.values()))
    sector_filter = st.selectbox("Sector / Theme", all_sectors)
    search_sym    = st.text_input("Search Symbol", placeholder="e.g. ITBEES")
    min_vol       = st.number_input("Min Volume (units)", value=0, step=100000,
                                    format="%d")
    chg_range     = st.slider("Change% Range", -10.0, 10.0, (-10.0, 10.0), 0.1)
    st.divider()
    st.caption("Data: Google Sheet snapshot — 05-Apr-2026")
    st.caption("Refresh every 5 min (cached)")

# ── Load Data ──────────────────────────────────────────────────────────────────
try:
    raw = load_from_gsheet()
    df  = build_df(raw)
    data_ok = True
except Exception as e:
    st.error(f"Could not fetch Google Sheet: {e}")
    data_ok = False
    st.stop()

# ── Apply Filters ──────────────────────────────────────────────────────────────
fdf = df.copy()
if sector_filter != "All":
    fdf = fdf[fdf["SECTOR"] == sector_filter]
if search_sym:
    fdf = fdf[fdf["SYMBOL"].str.contains(search_sym.upper(), na=False)]
fdf = fdf[fdf["VOLUME"] >= min_vol]
fdf = fdf[(fdf["CHG_PCT"] >= chg_range[0]) & (fdf["CHG_PCT"] <= chg_range[1])]

# ── Header KPIs ────────────────────────────────────────────────────────────────
st.markdown("## 📊 ETF Ki Dukan — Market Dashboard")
st.caption(f"Showing {len(fdf)} of {len(df)} ETFs  |  Last fetched: {datetime.now().strftime('%H:%M:%S')}")

pos   = int((df["CHG_PCT"] > 0).sum())
neg   = int((df["CHG_PCT"] < 0).sum())
flat  = int((df["CHG_PCT"] == 0).sum())
total_vol = df["VOLUME"].sum()
best_sym  = df.loc[df["CHG_PCT"].idxmax(), "SYMBOL"]
best_chg  = df["CHG_PCT"].max()
worst_sym = df.loc[df["CHG_PCT"].idxmin(), "SYMBOL"]
worst_chg = df["CHG_PCT"].min()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total ETFs",    len(df))
c2.metric("Advances ▲",    pos,  delta=f"{pos/len(df)*100:.0f}%",  delta_color="normal")
c3.metric("Declines ▼",    neg,  delta=f"-{neg/len(df)*100:.0f}%", delta_color="inverse")
c4.metric("Flat  —",       flat)
c5.metric("Best",  f"{best_sym}",  delta=f"+{best_chg:.2f}%", delta_color="normal")
c6.metric("Worst", f"{worst_sym}", delta=f"{worst_chg:.2f}%",  delta_color="inverse")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🏠 Overview", "📋 Watchlist", "📈 Gainers / Losers", "🗂 Sector View", "🔍 Screener"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 2])

    # Advance-Decline donut
    with col_left:
        st.markdown('<p class="section-title">Market Breadth</p>', unsafe_allow_html=True)
        fig_ad = go.Figure(go.Pie(
            labels=["Advances", "Declines", "Flat"],
            values=[pos, neg, flat],
            hole=0.55,
            marker_colors=["#00c853", "#ff1744", "#90a4ae"],
            textinfo="label+percent",
            textfont_size=12,
        ))
        fig_ad.update_layout(
            height=300, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            annotations=[dict(text=f"A/D<br>{pos}/{neg}", x=0.5, y=0.5,
                              font_size=14, showarrow=False, font_color="#e0e0e0")]
        )
        st.plotly_chart(fig_ad, use_container_width=True)

        # Volume summary
        st.markdown('<p class="section-title">Volume Leaders</p>', unsafe_allow_html=True)
        top5_vol = df.nlargest(5, "VOLUME")[["SYMBOL","VOLUME","CHG_PCT"]]
        for _, row in top5_vol.iterrows():
            clr = "gain" if row["CHG_PCT"] > 0 else ("loss" if row["CHG_PCT"] < 0 else "flat")
            st.markdown(
                f'**{row["SYMBOL"]}** &nbsp; {row["VOLUME"]:,} units &nbsp; '
                f'<span class="{clr}">{row["CHG_PCT"]:+.2f}%</span>',
                unsafe_allow_html=True
            )

    # Top movers bar chart
    with col_right:
        st.markdown('<p class="section-title">Top 10 Movers (Open → LTP)</p>', unsafe_allow_html=True)
        top5g  = df.nlargest(5,  "CHG_PCT")[["SYMBOL","CHG_PCT","SECTOR"]]
        top5l  = df.nsmallest(5, "CHG_PCT")[["SYMBOL","CHG_PCT","SECTOR"]]
        movers = pd.concat([top5g, top5l]).sort_values("CHG_PCT", ascending=True)
        movers["COLOR"] = movers["CHG_PCT"].apply(
            lambda x: "#00c853" if x > 0 else "#ff1744")

        fig_mv = go.Figure(go.Bar(
            x=movers["CHG_PCT"],
            y=movers["SYMBOL"],
            orientation="h",
            marker_color=movers["COLOR"],
            text=movers["CHG_PCT"].apply(lambda x: f"{x:+.2f}%"),
            textposition="outside",
        ))
        fig_mv.update_layout(
            height=380, margin=dict(t=10, b=10, l=10, r=60),
            xaxis_title="Change %",
            xaxis=dict(zeroline=True, zerolinecolor="#555"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            yaxis=dict(tickfont=dict(size=12)),
        )
        st.plotly_chart(fig_mv, use_container_width=True)

    # Intraday range (volatility) chart
    st.markdown('<p class="section-title">Intraday Range % — Top 15 Most Volatile</p>',
                unsafe_allow_html=True)
    top_range = df.nlargest(15, "RANGE_PCT").sort_values("RANGE_PCT", ascending=True)
    fig_rng = px.bar(
        top_range, x="RANGE_PCT", y="SYMBOL", orientation="h",
        color="SECTOR",
        color_discrete_map=SECTOR_COLORS,
        text="RANGE_PCT",
        labels={"RANGE_PCT": "High-Low Range %", "SYMBOL": ""},
    )
    fig_rng.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_rng.update_layout(
        height=420, margin=dict(t=10, b=10, l=10, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_rng, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">ETF Watchlist</p>', unsafe_allow_html=True)

    sort_col = st.selectbox("Sort by", ["VOLUME","CHG_PCT","RANGE_PCT","LTP","SYMBOL"],
                            key="sort_col")
    sort_asc = st.toggle("Ascending", value=False, key="sort_asc")

    display = fdf.sort_values(sort_col, ascending=sort_asc).copy()
    display["VOLUME_M"] = (display["VOLUME"] / 1_000_000).round(2)

    def color_chg(val):
        if val > 0:   return "color: #00c853; font-weight: 600"
        if val < 0:   return "color: #ff1744; font-weight: 600"
        return "color: #90a4ae"

    def color_bg(val):
        if val > 2:   return "background-color: rgba(0,200,83,0.15)"
        if val < -2:  return "background-color: rgba(255,23,68,0.15)"
        return ""

    show_cols = ["SYMBOL","UNDERLYING","OPEN","HIGH","LOW","LTP",
                 "CHG_PCT","SIGNAL","RANGE_PCT","VOLUME_M","SECTOR"]
    styled = (display[show_cols]
              .rename(columns={"CHG_PCT":"CHG%","RANGE_PCT":"RANGE%",
                               "VOLUME_M":"VOL(M)","SIGNAL":"↕"})
              .style
              .map(color_chg, subset=["CHG%"])
              .map(color_bg,  subset=["CHG%"])
              .format({"OPEN":"{:.2f}","HIGH":"{:.2f}","LOW":"{:.2f}",
                       "LTP":"{:.2f}","CHG%":"{:+.2f}%",
                       "RANGE%":"{:.2f}%","VOL(M)":"{:.2f}M"})
              )
    st.dataframe(styled, use_container_width=True, height=520)
    st.caption(f"{len(display)} ETFs shown after filters")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GAINERS / LOSERS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    n_top = st.slider("Show top N", 5, 20, 10, key="n_top")
    col_g, col_l = st.columns(2)

    with col_g:
        st.markdown('<p class="section-title">Top Gainers</p>', unsafe_allow_html=True)
        gainers = fdf.nlargest(n_top, "CHG_PCT").sort_values("CHG_PCT")
        fig_g = go.Figure(go.Bar(
            x=gainers["CHG_PCT"], y=gainers["SYMBOL"], orientation="h",
            marker_color="#00c853",
            text=gainers["CHG_PCT"].apply(lambda x: f"+{x:.2f}%"),
            textposition="outside",
        ))
        fig_g.update_layout(
            height=420, margin=dict(t=10, b=10, l=10, r=60),
            xaxis_title="Change %",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
        )
        st.plotly_chart(fig_g, use_container_width=True)

        # Detail table
        g_tbl = fdf.nlargest(n_top, "CHG_PCT")[
            ["SYMBOL","LTP","CHG_PCT","VOLUME","SECTOR"]].reset_index(drop=True)
        g_tbl.index += 1
        st.dataframe(g_tbl.style
                     .format({"LTP":"{:.2f}","CHG_PCT":"{:+.2f}%","VOLUME":"{:,}"})
                     .map(color_chg, subset=["CHG_PCT"]),
                     use_container_width=True)

    with col_l:
        st.markdown('<p class="section-title">Top Losers</p>', unsafe_allow_html=True)
        losers = fdf.nsmallest(n_top, "CHG_PCT").sort_values("CHG_PCT", ascending=False)
        fig_l = go.Figure(go.Bar(
            x=losers["CHG_PCT"], y=losers["SYMBOL"], orientation="h",
            marker_color="#ff1744",
            text=losers["CHG_PCT"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
        ))
        fig_l.update_layout(
            height=420, margin=dict(t=10, b=10, l=10, r=60),
            xaxis_title="Change %",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
        )
        st.plotly_chart(fig_l, use_container_width=True)

        l_tbl = fdf.nsmallest(n_top, "CHG_PCT")[
            ["SYMBOL","LTP","CHG_PCT","VOLUME","SECTOR"]].reset_index(drop=True)
        l_tbl.index += 1
        st.dataframe(l_tbl.style
                     .format({"LTP":"{:.2f}","CHG_PCT":"{:+.2f}%","VOLUME":"{:,}"})
                     .map(color_chg, subset=["CHG_PCT"]),
                     use_container_width=True)

    # Volume vs Change scatter
    st.markdown('<p class="section-title">Volume vs Change% (Bubble = Range%)</p>',
                unsafe_allow_html=True)
    fig_sc = px.scatter(
        fdf,
        x="CHG_PCT", y="VOLUME",
        size="RANGE_PCT", color="SECTOR",
        color_discrete_map=SECTOR_COLORS,
        hover_name="SYMBOL",
        hover_data={"CHG_PCT":":.2f","VOLUME":":,","RANGE_PCT":":.2f","SECTOR":True},
        labels={"CHG_PCT":"Change %","VOLUME":"Volume","RANGE_PCT":"Range %"},
        size_max=40,
    )
    fig_sc.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        xaxis=dict(zeroline=True, zerolinecolor="#555"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SECTOR VIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    sec_grp = (df.groupby("SECTOR")
               .agg(
                   COUNT=("SYMBOL","count"),
                   AVG_CHG=("CHG_PCT","mean"),
                   BEST=("CHG_PCT","max"),
                   WORST=("CHG_PCT","min"),
                   TOTAL_VOL=("VOLUME","sum"),
                   AVG_RANGE=("RANGE_PCT","mean"),
               ).reset_index()
               .sort_values("AVG_CHG", ascending=False))
    sec_grp["AVG_CHG"]   = sec_grp["AVG_CHG"].round(2)
    sec_grp["BEST"]      = sec_grp["BEST"].round(2)
    sec_grp["WORST"]     = sec_grp["WORST"].round(2)
    sec_grp["AVG_RANGE"] = sec_grp["AVG_RANGE"].round(2)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Average Change % by Sector</p>',
                    unsafe_allow_html=True)
        fig_sec = go.Figure(go.Bar(
            x=sec_grp["AVG_CHG"],
            y=sec_grp["SECTOR"],
            orientation="h",
            marker_color=[("#00c853" if v >= 0 else "#ff1744")
                          for v in sec_grp["AVG_CHG"]],
            text=sec_grp["AVG_CHG"].apply(lambda x: f"{x:+.2f}%"),
            textposition="outside",
        ))
        fig_sec.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=60),
            xaxis_title="Avg Change %",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            xaxis=dict(zeroline=True, zerolinecolor="#555"),
        )
        st.plotly_chart(fig_sec, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-title">Total Volume by Sector (Treemap)</p>',
                    unsafe_allow_html=True)
        fig_tree = px.treemap(
            sec_grp, path=["SECTOR"], values="TOTAL_VOL",
            color="AVG_CHG",
            color_continuous_scale=["#ff1744","#263238","#00c853"],
            color_continuous_midpoint=0,
            hover_data={"COUNT":True,"AVG_CHG":":.2f","TOTAL_VOL":":,"},
        )
        fig_tree.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0",
            coloraxis_colorbar=dict(title="Avg Chg%"),
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    # Sector summary table
    st.markdown('<p class="section-title">Sector Summary Table</p>', unsafe_allow_html=True)

    def color_sec_chg(val):
        if val > 0: return "color: #00c853; font-weight:600"
        if val < 0: return "color: #ff1744; font-weight:600"
        return ""

    st.dataframe(
        sec_grp.rename(columns={
            "SECTOR":"Sector","COUNT":"ETFs","AVG_CHG":"Avg Chg%",
            "BEST":"Best%","WORST":"Worst%",
            "TOTAL_VOL":"Total Volume","AVG_RANGE":"Avg Range%"
        }).style
        .map(color_sec_chg, subset=["Avg Chg%","Best%","Worst%"])
        .format({"Avg Chg%":"{:+.2f}%","Best%":"{:+.2f}%",
                 "Worst%":"{:+.2f}%","Total Volume":"{:,}",
                 "Avg Range%":"{:.2f}%"}),
        use_container_width=True,
    )

    # ETF breakdown within sector
    st.markdown('<p class="section-title">ETF Performance Within Each Sector</p>',
                unsafe_allow_html=True)
    selected_sector = st.selectbox("Select Sector", sorted(df["SECTOR"].unique()),
                                   key="sector_detail")
    sec_detail = df[df["SECTOR"] == selected_sector].sort_values("CHG_PCT", ascending=True)
    fig_sd = px.bar(
        sec_detail, x="CHG_PCT", y="SYMBOL", orientation="h",
        color="CHG_PCT",
        color_continuous_scale=["#ff1744","#37474f","#00c853"],
        color_continuous_midpoint=0,
        text="CHG_PCT",
        hover_data={"LTP":":.2f","VOLUME":":,","UNDERLYING":True},
    )
    fig_sd.update_traces(texttemplate="%{text:+.2f}%", textposition="outside")
    fig_sd.update_layout(
        height=max(300, len(sec_detail)*35),
        margin=dict(t=10, b=10, l=10, r=80),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        xaxis=dict(zeroline=True, zerolinecolor="#555"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_sd, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SCREENER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">ETF Screener</p>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sc_sector  = st.multiselect("Sectors", sorted(df["SECTOR"].unique()),
                                    default=sorted(df["SECTOR"].unique()))
        sc_signal  = st.multiselect("Signal", ["▲ Gainers","▼ Losers","— Flat"],
                                    default=["▲ Gainers","▼ Losers","— Flat"])
    with sc2:
        sc_chg_min = st.number_input("Min Change%", value=-10.0, step=0.5)
        sc_chg_max = st.number_input("Max Change%", value=10.0,  step=0.5)
    with sc3:
        sc_vol_min  = st.number_input("Min Volume",  value=0,        step=100000, format="%d")
        sc_range_min = st.number_input("Min Intraday Range%", value=0.0, step=0.5)

    sig_map = {"▲ Gainers":"▲","▼ Losers":"▼","— Flat":"—"}
    allowed_sigs = [sig_map[s] for s in sc_signal]

    result = df[
        (df["SECTOR"].isin(sc_sector)) &
        (df["SIGNAL"].isin(allowed_sigs)) &
        (df["CHG_PCT"] >= sc_chg_min) &
        (df["CHG_PCT"] <= sc_chg_max) &
        (df["VOLUME"]  >= sc_vol_min) &
        (df["RANGE_PCT"] >= sc_range_min)
    ].sort_values("CHG_PCT", ascending=False).reset_index(drop=True)
    result.index += 1

    st.markdown(f"**{len(result)} ETFs match your criteria**")

    show = result[["SYMBOL","UNDERLYING","LTP","CHG_PCT","SIGNAL",
                   "RANGE_PCT","VOLUME","SECTOR"]]
    st.dataframe(
        show.rename(columns={"CHG_PCT":"CHG%","RANGE_PCT":"RANGE%","SIGNAL":"↕"})
        .style
        .map(color_chg, subset=["CHG%"])
        .format({"LTP":"{:.2f}","CHG%":"{:+.2f}%",
                 "RANGE%":"{:.2f}%","VOLUME":"{:,}"}),
        use_container_width=True,
        height=450,
    )

    # ETF Detail card
    if not result.empty:
        st.divider()
        st.markdown('<p class="section-title">ETF Detail Card</p>', unsafe_allow_html=True)
        pick = st.selectbox("Select ETF for detail", result["SYMBOL"].tolist(), key="etf_pick")
        row  = df[df["SYMBOL"] == pick].iloc[0]

        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("LTP",   f"₹{row['LTP']:.2f}")
        d2.metric("Open",  f"₹{row['OPEN']:.2f}")
        d3.metric("High",  f"₹{row['HIGH']:.2f}")
        d4.metric("Low",   f"₹{row['LOW']:.2f}")
        d5.metric("Change", f"{row['CHG_PCT']:+.2f}%",
                  delta=f"{row['CHG_PCT']:+.2f}%",
                  delta_color="normal" if row["CHG_PCT"] >= 0 else "inverse")

        # Mini candlestick-style OHLC bar
        fig_ohlc = go.Figure()
        color = "#00c853" if row["CHG_PCT"] >= 0 else "#ff1744"
        fig_ohlc.add_trace(go.Bar(
            x=["Range"], y=[row["HIGH"] - row["LOW"]],
            base=[row["LOW"]],
            marker_color=color, opacity=0.5, name="Range",
        ))
        for price, label in [(row["OPEN"],"Open"),(row["LTP"],"LTP")]:
            fig_ohlc.add_hline(y=price, line_dash="dash",
                               annotation_text=label,
                               annotation_position="right",
                               line_color="#aaa", line_width=1)
        fig_ohlc.update_layout(
            height=250, margin=dict(t=20, b=20, l=40, r=80),
            title=f"{pick} — Intraday OHLC Range",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e0e0e0", showlegend=False,
            yaxis_title="Price (₹)",
        )
        st.plotly_chart(fig_ohlc, use_container_width=True)

        # Peers in same sector
        peers = df[(df["SECTOR"] == row["SECTOR"]) & (df["SYMBOL"] != pick)]
        st.markdown(f"**Peers in {row['SECTOR']}**")
        st.dataframe(
            peers[["SYMBOL","LTP","CHG_PCT","VOLUME"]].sort_values("CHG_PCT", ascending=False)
            .rename(columns={"CHG_PCT":"CHG%"})
            .style
            .map(color_chg, subset=["CHG%"])
            .format({"LTP":"{:.2f}","CHG%":"{:+.2f}%","VOLUME":"{:,}"}),
            use_container_width=True,
        )
