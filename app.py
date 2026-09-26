import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
from pathlib import Path

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SkyCity Auckland — Restaurant Profitability Intelligence",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:           #0B0F17;
    --surface:      #111827;
    --surface2:     #1a2235;
    --border:       rgba(255,255,255,0.08);
    --gold:         #F5C518;
    --gold2:        #e8a000;
    --teal:         #00C9A7;
    --teal2:        #0097a7;
    --red:          #FF5252;
    --red2:         #b71c1c;
    --blue:         #448AFF;
    --blue2:        #1565c0;
    --purple:       #CE93D8;
    --text1:        #F0F4FF;
    --text2:        #8892a4;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text1);
}

#MainMenu, footer, header { visibility: hidden; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text1) !important; }

/* ── glass card ── */
.card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 18px;
    transition: box-shadow .25s ease;
}
.card:hover { box-shadow: 0 0 28px rgba(0,201,167,.15); }

/* ── KPI metric ── */
.kpi {
    background: var(--surface2);
    border-radius: 12px;
    padding: 18px 16px;
    text-align: center;
    border-left: 4px solid var(--teal);
    transition: transform .2s ease;
}
.kpi:hover { transform: translateY(-3px); }
.kpi .label { font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color:var(--text2); margin:0; }
.kpi .value { font-size:1.9rem; font-weight:700; margin:6px 0 0 0; color:var(--text1); }
.kpi.gold  { border-left-color:var(--gold); }
.kpi.red   { border-left-color:var(--red); }
.kpi.blue  { border-left-color:var(--blue); }
.kpi.purple{ border-left-color:var(--purple); }

/* ── section title ── */
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text1);
    margin-bottom: 6px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--teal);
    display: inline-block;
}
.section-sub {
    font-size: .82rem;
    color: var(--text2);
    margin-bottom: 22px;
}

/* ── sidebar nav links ── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: background .2s;
    font-size: .88rem;
    color: var(--text2);
}
.nav-item:hover { background: rgba(0,201,167,.12); color: var(--teal); }
.nav-item.active { background: rgba(0,201,167,.18); color: var(--teal); font-weight:600; }

/* ── plotly charts transparent bg ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: var(--teal2); }

/* ── streamlit elements ── */
.stSlider > div > div > div { background: var(--teal) !important; }
.stSelectbox label, .stMultiSelect label, .stNumberInput label,
.stSlider label { color: var(--text2) !important; font-size:.82rem !important; }
div[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 10px !important; }
.streamlit-expanderHeader { background: var(--surface2) !important; color: var(--teal) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LABEL MAPS  (LabelEncoder alphabetical order)
# ─────────────────────────────────────────────
CUISINE_MAP  = {0:"Burgers",1:"Chicken Dishes",2:"Chinese",3:"Indian",
                4:"Japanese",5:"Kebabs/Mediterranean",6:"Pizza",7:"Thai"}
SEGMENT_MAP  = {0:"Cafe",1:"Full-service",2:"Ghost Kitchen",3:"QSR"}
SUBREGION_MAP= {0:"CBD",1:"North Shore",2:"South Auckland",3:"West Auckland"}

# Reverse maps
CUISINE_REV  = {v:k for k,v in CUISINE_MAP.items()}
SEGMENT_REV  = {v:k for k,v in SEGMENT_MAP.items()}
SUBREGION_REV= {v:k for k,v in SUBREGION_MAP.items()}

CHANNEL_COLORS = {
    "In-Store":      "#00C9A7",
    "Uber Eats":     "#448AFF",
    "DoorDash":      "#F5C518",
    "Self-Delivery": "#CE93D8",
}

CHANNEL_SPECS = {
    "In-Store":      ("InStoreOrders", "InStoreRevenue", "InStoreNetProfit"),
    "Uber Eats":     ("UberEatsOrders", "UberEatsRevenue", "UberEatsNetProfit"),
    "DoorDash":      ("DoorDashOrders", "DoorDashRevenue", "DoorDashNetProfit"),
    "Self-Delivery": ("SelfDeliveryOrders", "SelfDeliveryRevenue", "SelfDeliveryNetProfit"),
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="#8892a4",
    title_font_color="#F0F4FF",
    legend_bgcolor="rgba(0,0,0,0)",
)

# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent

@st.cache_data
def load_data():
    df_raw  = pd.read_csv(BASE_DIR / "SkyCity Auckland Restaurants & Bars.csv")
    df_feat = pd.read_csv(BASE_DIR / "restaurant_profitability_final.csv")

    def normalize_category(series, reverse_map):
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().all():
            return numeric.astype(int)
        return series.map(reverse_map).astype("Int64")

    # The raw file contains readable labels; the feature file contains model codes.
    # Normalising both avoids empty filters and broken label maps.
    df_raw["CuisineType"] = normalize_category(df_raw["CuisineType"], CUISINE_REV)
    df_raw["Segment"]     = normalize_category(df_raw["Segment"], SEGMENT_REV)
    df_raw["Subregion"]   = normalize_category(df_raw["Subregion"], SUBREGION_REV)
    df_feat["CuisineType"] = normalize_category(df_feat["CuisineType"], CUISINE_REV)
    df_feat["Segment"]     = normalize_category(df_feat["Segment"], SEGMENT_REV)
    df_feat["Subregion"]   = normalize_category(df_feat["Subregion"], SUBREGION_REV)

    for frame in (df_raw, df_feat):
        frame["CuisineName"]   = frame["CuisineType"].astype(int).map(CUISINE_MAP)
        frame["SegmentName"]   = frame["Segment"].astype(int).map(SEGMENT_MAP)
        frame["SubregionName"] = frame["Subregion"].astype(int).map(SUBREGION_MAP)

    # Same for raw
    df_raw["Cluster"] = df_feat["Cluster"].values
    df_raw["ProfitClass"] = df_feat["ProfitClass"].values
    df_raw["TotalRevenue"] = df_feat["TotalRevenue"].values
    df_raw["TotalNetProfit"] = df_feat["TotalNetProfit"].values
    df_raw["ProfitMargin"] = df_feat["ProfitMargin"].values
    df_raw["AggregatorDependency"] = df_feat["AggregatorDependency"].values
    df_raw["DeliveryRiskCategory"] = df_feat["DeliveryRiskCategory"].values
    df_raw["ProfitabilityCategory"] = df_feat["ProfitabilityCategory"].values
    df_raw["SelfDeliveryEfficiency"] = df_feat["SelfDeliveryEfficiency"].values
    df_raw["CostEfficiency"] = df_feat["CostEfficiency"].values
    df_raw["RevenuePerOrder"] = df_feat["RevenuePerOrder"].values
    df_raw["ProfitPerOrder"] = df_feat["ProfitPerOrder"].values

    return df_raw, df_feat

@st.cache_resource
def load_models():
    models_dir = BASE_DIR / "Models"
    loaded = {}
    model_files = {
        "scaler":      "scaler.pkl",
        "pca":         "pca_model.pkl",
        "kmeans":      "kmeans_model.pkl",
        "rf":          "random_forest_model.pkl",
        "xgb":         "xgboost_profitability_model.pkl",
        "lgbm":        "lightgbm_profitability_model.pkl",
        "lr":          "logistic_regression_model.pkl",
    }
    for key, fname in model_files.items():
        fpath = models_dir / fname
        if fpath.exists():
            try:
                loaded[key] = joblib.load(fpath)
            except Exception as e:
                st.warning(f"⚠️ Could not load {fname}: {e}")
    return loaded

df, df_feat = load_data()
models = load_models()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def kpi(label, value, style=""):
    st.markdown(
        f'<div class="kpi {style}"><p class="label">{label}</p>'
        f'<p class="value">{value}</p></div>',
        unsafe_allow_html=True
    )

def section(title, subtitle=""):
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="section-sub">{subtitle}</p>', unsafe_allow_html=True)

def apply_layout(fig, height=400, legend=True):
    fig.update_layout(
        **PLOT_LAYOUT,
        height=height,
        showlegend=legend,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    )
    return fig

def channel_summary(data, channels=None):
    channels = channels or list(CHANNEL_SPECS)
    rows = []
    for ch in channels:
        ord_col, rev_col, profit_col = CHANNEL_SPECS[ch]
        total_orders  = data[ord_col].sum()
        total_rev     = data[rev_col].sum()
        total_profit  = data[profit_col].sum()
        rows.append(dict(
            Channel=ch,
            Orders=total_orders,
            Revenue=total_rev,
            NetProfit=total_profit,
            Margin=(total_profit / total_rev * 100) if total_rev else 0,
            ProfitPerOrder=(total_profit / total_orders) if total_orders else 0,
        ))
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 10px;'>
        <span style='font-size:2rem;'>🍽️</span>
        <div style='font-size:1rem; font-weight:700; color:#F0F4FF; margin-top:6px;'>SkyCity Auckland</div>
        <div style='font-size:.72rem; color:#00C9A7; letter-spacing:.1em; text-transform:uppercase;'>
            Restaurant Intelligence
        </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.08); margin:10px 0 20px;'>
    """, unsafe_allow_html=True)

    pages = [
        ("🏠", "Executive Overview"),
        ("📊", "Channel Profitability"),
        ("💧", "Cost Waterfall"),
        ("🗺️", "Cuisine & Segment"),
        ("⚠️", "Commission Impact"),
        ("🔵", "Cluster Intelligence"),
        ("📉", "Financial Risk"),
        ("🤖", "AI Model Center"),
    ]

    page_labels = [p[1] for p in pages]
    selected = st.radio(
        "Navigate",
        page_labels,
        format_func=lambda x: f"{pages[page_labels.index(x)][0]}  {x}",
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08); margin:20px 0 10px;'>", unsafe_allow_html=True)

    # Global filters
    st.markdown("<p style='font-size:.72rem;color:#8892a4;text-transform:uppercase;letter-spacing:.08em;'>Global Filters</p>", unsafe_allow_html=True)
    all_cuisines  = list(CUISINE_MAP.values())
    all_segments  = list(SEGMENT_MAP.values())
    all_regions   = list(SUBREGION_MAP.values())

    sel_cuisines  = st.multiselect("Cuisine Type",  all_cuisines,  default=all_cuisines,  key="f_cui")
    sel_segments  = st.multiselect("Segment",       all_segments,  default=all_segments,  key="f_seg")
    sel_regions   = st.multiselect("Subregion",     all_regions,   default=all_regions,   key="f_reg")
    sel_channels  = st.multiselect("Channel",       list(CHANNEL_SPECS), default=list(CHANNEL_SPECS), key="f_channel")

    # Apply filters
    fdf = df[
        df["CuisineType"].isin([CUISINE_REV[c] for c in sel_cuisines]) &
        df["Segment"].isin([SEGMENT_REV[s] for s in sel_segments]) &
        df["Subregion"].isin([SUBREGION_REV[r] for r in sel_regions])
    ].copy()

    st.markdown(f"<p style='font-size:.72rem;color:#8892a4;'>Showing <b style='color:#00C9A7;'>{len(fdf):,}</b> of {len(df):,} restaurants</p>", unsafe_allow_html=True)

if fdf.empty:
    st.warning("No restaurants match the selected filters. Adjust the cuisine, segment, or subregion filters to continue.")
    st.stop()

if not sel_channels:
    st.warning("Select at least one channel to display channel-based analysis.")
    st.stop()

# ─────────────────────────────────────────────
#  PAGE: EXECUTIVE OVERVIEW
# ─────────────────────────────────────────────
if selected == "Executive Overview":
    section("Executive Overview", "Top-level KPIs and performance snapshot across all channels")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Restaurants", f"{len(fdf):,}")
    with c2: kpi("Avg Monthly Revenue", f"${fdf['TotalRevenue'].mean():,.0f}", "gold")
    with c3: kpi("Avg Net Profit", f"${fdf['TotalNetProfit'].mean():,.0f}", "blue")
    with c4: kpi("Avg Profit Margin", f"{fdf['ProfitMargin'].mean():.1f}%", "")
    with c5: kpi("High Risk Restaurants", f"{(fdf['DeliveryRiskCategory']=='High Risk').sum():,}", "red")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        prof_counts = fdf["ProfitabilityCategory"].value_counts().reset_index()
        fig = px.pie(
            prof_counts, names="ProfitabilityCategory", values="count",
            title="Profitability Category Distribution",
            color="ProfitabilityCategory",
            color_discrete_map={"High Profit":"#00C9A7","Medium Profit":"#F5C518","Low Profit":"#FF5252"},
            hole=0.62,
        )
        apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        region_profit = fdf.groupby("Subregion")["TotalNetProfit"].mean().reset_index()
        region_profit["SubregionName"] = region_profit["Subregion"].map(SUBREGION_MAP)
        region_profit = region_profit.sort_values("TotalNetProfit", ascending=False)
        fig2 = px.bar(
            region_profit, x="SubregionName", y="TotalNetProfit",
            title="Avg Net Profit by Subregion",
            color="TotalNetProfit",
            color_continuous_scale=[[0,"#FF5252"],[0.5,"#F5C518"],[1,"#00C9A7"]],
        )
        fig2.update_layout(coloraxis_showscale=False)
        apply_layout(fig2, 340)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        channel_rev = pd.DataFrame({
            "Channel": ["In-Store","Uber Eats","DoorDash","Self-Delivery"],
            "Revenue":  [fdf["InStoreRevenue"].sum(), fdf["UberEatsRevenue"].sum(),
                         fdf["DoorDashRevenue"].sum(), fdf["SelfDeliveryRevenue"].sum()],
            "Profit":   [fdf["InStoreNetProfit"].sum(), fdf["UberEatsNetProfit"].sum(),
                         fdf["DoorDashNetProfit"].sum(), fdf["SelfDeliveryNetProfit"].sum()],
        })
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Total Revenue", x=channel_rev["Channel"], y=channel_rev["Revenue"],
                               marker_color=["#00C9A7","#448AFF","#F5C518","#CE93D8"]))
        fig3.add_trace(go.Bar(name="Net Profit",    x=channel_rev["Channel"], y=channel_rev["Profit"],
                               marker_color=["#006d59","#1a4e9e","#8a6e00","#6a3d7a"], opacity=0.85))
        fig3.update_layout(barmode="group", title="Total Revenue vs Net Profit by Channel")
        apply_layout(fig3, 340)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cuisine_profit = fdf.groupby("CuisineType")["ProfitMargin"].mean().reset_index()
        cuisine_profit["CuisineName"] = cuisine_profit["CuisineType"].map(CUISINE_MAP)
        cuisine_profit = cuisine_profit.sort_values("ProfitMargin", ascending=True)
        fig4 = px.bar(
            cuisine_profit, x="ProfitMargin", y="CuisineName", orientation="h",
            title="Avg Profit Margin by Cuisine",
            color="ProfitMargin",
            color_continuous_scale=[[0,"#FF5252"],[0.5,"#F5C518"],[1,"#00C9A7"]],
        )
        fig4.update_layout(coloraxis_showscale=False)
        apply_layout(fig4, 340)
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: CHANNEL PROFITABILITY
# ─────────────────────────────────────────────
elif selected == "Channel Profitability":
    section("Channel Profitability", "Side-by-side comparison of net profit, margin, and order economics across all channels")

    ch_df = channel_summary(fdf, sel_channels)

    metric_cols = st.columns(len(ch_df))
    style_map = {"In-Store": "", "Uber Eats": "blue", "DoorDash": "gold", "Self-Delivery": "purple"}
    for col, row in zip(metric_cols, ch_df.itertuples()):
        with col:
            kpi(row.Channel, f"${row.NetProfit/1e6:.2f}M", style_map.get(row.Channel, ""))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = go.Figure()
        colors = [CHANNEL_COLORS[ch] for ch in ch_df["Channel"]]
        fig.add_trace(go.Bar(
            x=ch_df["Channel"], y=ch_df["Margin"],
            marker_color=colors, name="Margin %",
            text=[f"{v:.1f}%" for v in ch_df["Margin"]], textposition="outside",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.6)", line_width=1)
        fig.update_layout(title="Net Profit Margin by Channel (%)", yaxis_ticksuffix="%")
        apply_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=ch_df["Channel"], y=ch_df["ProfitPerOrder"],
            marker_color=colors, name="$/Order",
            text=[f"${v:.2f}" for v in ch_df["ProfitPerOrder"]], textposition="outside",
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.6)", line_width=1)
        fig2.update_layout(title="Net Profit per Order by Channel ($)")
        apply_layout(fig2, 360)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Per-cuisine channel margin heatmap
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_inner = fdf.copy()
    section_inner["CuisineName"] = section_inner["CuisineType"].map(CUISINE_MAP)

    hm_data = {}
    for ch in sel_channels:
        _, rev_col, profit_col = CHANNEL_SPECS[ch]
        grp = section_inner.groupby("CuisineName", observed=True).apply(
            lambda g, r=rev_col, p=profit_col: (g[p].sum() / g[r].sum() * 100) if g[r].sum() else 0,
            include_groups=False,
        )
        hm_data[ch] = grp

    hm_df = pd.DataFrame(hm_data)
    fig3 = px.imshow(
        hm_df.values, x=hm_df.columns.tolist(), y=hm_df.index.tolist(),
        color_continuous_scale=[[0,"#FF5252"],[0.4,"#1a2235"],[1,"#00C9A7"]],
        color_continuous_midpoint=0,
        title="Profit Margin Heatmap — Channel × Cuisine (%)",
        labels=dict(color="Margin %"),
        text_auto=".1f",
    )
    fig3.update_layout(**PLOT_LAYOUT, height=340, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Profit comparison box plots
    st.markdown('<div class="card">', unsafe_allow_html=True)
    profit_cols = [CHANNEL_SPECS[ch][2] for ch in sel_channels]
    melt_df = fdf[profit_cols].copy()
    melt_df.columns = sel_channels
    melt_long = melt_df.melt(var_name="Channel", value_name="NetProfit")
    fig4 = px.box(
        melt_long, x="Channel", y="NetProfit", color="Channel",
        color_discrete_map=CHANNEL_COLORS,
        title="Net Profit Distribution per Channel ($)",
    )
    fig4.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.6)")
    apply_layout(fig4, 380)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: COST WATERFALL
# ─────────────────────────────────────────────
elif selected == "Cost Waterfall":
    section("Cost Waterfall & Decomposition", "Visualise how revenue flows into net profit after each cost layer")

    # Select channel
    ch_sel = st.selectbox("Select Channel for Waterfall", sel_channels)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    total_rev  = fdf["TotalRevenue"].sum()
    cogs_total = fdf.apply(lambda r: r["TotalRevenue"] * r["COGSRate"], axis=1).sum()
    opex_total = fdf.apply(lambda r: r["TotalRevenue"] * r["OPEXRate"], axis=1).sum()

    if ch_sel == "In-Store":
        ch_rev     = fdf["InStoreRevenue"].sum()
        ch_cogs    = fdf.apply(lambda r: r["InStoreRevenue"] * r["COGSRate"], axis=1).sum()
        ch_opex    = fdf.apply(lambda r: r["InStoreRevenue"] * r["OPEXRate"], axis=1).sum()
        commission = 0
        delivery   = 0
        ch_profit  = fdf["InStoreNetProfit"].sum()
    elif ch_sel == "Uber Eats":
        ch_rev     = fdf["UberEatsRevenue"].sum()
        ch_cogs    = fdf.apply(lambda r: r["UberEatsRevenue"] * r["COGSRate"], axis=1).sum()
        ch_opex    = fdf.apply(lambda r: r["UberEatsRevenue"] * r["OPEXRate"], axis=1).sum()
        commission = fdf.apply(lambda r: r["UberEatsRevenue"] * r["CommissionRate"], axis=1).sum()
        delivery   = 0
        ch_profit  = fdf["UberEatsNetProfit"].sum()
    elif ch_sel == "DoorDash":
        ch_rev     = fdf["DoorDashRevenue"].sum()
        ch_cogs    = fdf.apply(lambda r: r["DoorDashRevenue"] * r["COGSRate"], axis=1).sum()
        ch_opex    = fdf.apply(lambda r: r["DoorDashRevenue"] * r["OPEXRate"], axis=1).sum()
        commission = fdf.apply(lambda r: r["DoorDashRevenue"] * r["CommissionRate"], axis=1).sum()
        delivery   = 0
        ch_profit  = fdf["DoorDashNetProfit"].sum()
    else:
        ch_rev     = fdf["SelfDeliveryRevenue"].sum()
        ch_cogs    = fdf.apply(lambda r: r["SelfDeliveryRevenue"] * r["COGSRate"], axis=1).sum()
        ch_opex    = fdf.apply(lambda r: r["SelfDeliveryRevenue"] * r["OPEXRate"], axis=1).sum()
        commission = 0
        delivery   = fdf["SD_DeliveryTotalCost"].sum()
        ch_profit  = fdf["SelfDeliveryNetProfit"].sum()

    labels   = ["Revenue", "COGS", "OPEX"]
    measures = ["absolute", "relative", "relative"]
    values   = [ch_rev, -ch_cogs, -ch_opex]

    if commission > 0:
        labels.append("Commission"); measures.append("relative"); values.append(-commission)
    if delivery > 0:
        labels.append("Delivery Cost"); measures.append("relative"); values.append(-delivery)

    labels.append("Net Profit"); measures.append("total"); values.append(ch_profit)

    panel_cols = st.columns(5)
    component_values = [
        ("Revenue", ch_rev, ""),
        ("COGS", ch_cogs, "red"),
        ("OPEX", ch_opex, "gold"),
        ("Commission/Delivery", commission + delivery, "purple"),
        ("Net Profit", ch_profit, "blue"),
    ]
    for col, (label, value, style) in zip(panel_cols, component_values):
        with col:
            kpi(label, f"${value:,.0f}", style)

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure(go.Waterfall(
        name="Cost Waterfall", orientation="v",
        measure=measures, x=labels, y=values,
        connector={"line":{"color":"rgba(255,255,255,0.2)"}},
        increasing ={"marker":{"color":"#00C9A7"}},
        decreasing ={"marker":{"color":"#FF5252"}},
        totals     ={"marker":{"color":"#448AFF"}},
        texttemplate="$%{y:,.0f}", textposition="outside",
    ))
    fig.update_layout(title=f"{ch_sel} — Revenue Waterfall to Net Profit")
    apply_layout(fig, 450, legend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Cost composition stacked bar by cuisine
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fdf2 = fdf.copy()
    fdf2["CuisineName"] = fdf2["CuisineType"].map(CUISINE_MAP)
    fdf2["COGS_Avg"]    = fdf2["TotalRevenue"] * fdf2["COGSRate"]
    fdf2["OPEX_Avg"]    = fdf2["TotalRevenue"] * fdf2["OPEXRate"]
    fdf2["Commission_Cost"] = fdf2["TotalRevenue"] * fdf2["CommissionRate"]

    cost_grp = fdf2.groupby("CuisineName")[["COGS_Avg","OPEX_Avg","Commission_Cost","SD_DeliveryTotalCost"]].mean().reset_index()
    cost_grp.columns = ["Cuisine","COGS","OPEX","Commission","Delivery Cost"]
    cost_melt = cost_grp.melt(id_vars="Cuisine", var_name="Cost Type", value_name="Amount")

    fig2 = px.bar(
        cost_melt, x="Cuisine", y="Amount", color="Cost Type", barmode="stack",
        title="Avg Cost Component Breakdown by Cuisine",
        color_discrete_sequence=["#FF5252","#F5C518","#448AFF","#CE93D8"],
    )
    apply_layout(fig2, 380)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: CUISINE & SEGMENT
# ─────────────────────────────────────────────
elif selected == "Cuisine & Segment":
    section("Cuisine & Segment Analysis", "Compare profitability across food categories and business model types")

    fdf2 = fdf.copy()
    fdf2["CuisineName"]  = fdf2["CuisineType"].map(CUISINE_MAP)
    fdf2["SegmentName"]  = fdf2["Segment"].map(SEGMENT_MAP)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cg = fdf2.groupby("CuisineName").agg(
            AvgMargin=("ProfitMargin","mean"),
            Count=("RestaurantID","count"),
            AvgProfit=("TotalNetProfit","mean"),
        ).reset_index().sort_values("AvgMargin", ascending=False)

        fig = px.scatter(
            cg, x="AvgMargin", y="AvgProfit", size="Count", color="CuisineName",
            title="Cuisine: Avg Margin vs Avg Profit (bubble=count)",
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"AvgMargin":"Avg Margin %","AvgProfit":"Avg Net Profit $"},
        )
        apply_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sg = fdf2.groupby("SegmentName").agg(
            AvgMargin=("ProfitMargin","mean"),
            Count=("RestaurantID","count"),
            AvgProfit=("TotalNetProfit","mean"),
        ).reset_index()
        fig2 = px.bar(
            sg.sort_values("AvgMargin", ascending=False),
            x="SegmentName", y="AvgMargin", color="SegmentName",
            title="Avg Profit Margin by Business Segment",
            color_discrete_sequence=["#00C9A7","#448AFF","#F5C518","#CE93D8"],
            text_auto=".1f",
        )
        apply_layout(fig2, 360)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Segment × Cuisine profit heatmap
    st.markdown('<div class="card">', unsafe_allow_html=True)
    pivot = fdf2.pivot_table(index="SegmentName", columns="CuisineName",
                             values="ProfitMargin", aggfunc="mean")
    fig3 = px.imshow(
        pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        color_continuous_scale=[[0,"#FF5252"],[0.5,"#1a2235"],[1,"#00C9A7"]],
        color_continuous_midpoint=pivot.values.mean(),
        title="Profit Margin Heatmap — Segment × Cuisine (%)",
        text_auto=".1f",
    )
    fig3.update_layout(**PLOT_LAYOUT, height=300, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Channel share by segment
    st.markdown('<div class="card">', unsafe_allow_html=True)
    share_grp = fdf2.groupby("SegmentName")[["InStoreShare","UE_share","DD_share","SD_share"]].mean().reset_index()
    share_grp.columns = ["Segment","In-Store","Uber Eats","DoorDash","Self-Delivery"]
    share_melt = share_grp.melt(id_vars="Segment", var_name="Channel", value_name="Share")
    fig4 = px.bar(
        share_melt, x="Segment", y="Share", color="Channel", barmode="stack",
        title="Average Order Share by Channel per Segment",
        color_discrete_map=CHANNEL_COLORS,
    )
    fig4.update_layout(yaxis_tickformat=".0%")
    apply_layout(fig4, 360)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: COMMISSION IMPACT
# ─────────────────────────────────────────────
elif selected == "Commission Impact":
    section("Commission & Delivery Cost Impact", "What-if analysis — drag sliders to see how cost changes affect profitability")

    col_ctrl, col_chart = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Scenario Sliders")
        new_commission = st.slider("Aggregator Commission Rate (%)", 5, 40, int(fdf["CommissionRate"].mean()*100), step=1)
        new_delivery   = st.slider("Self-Delivery Cost / Order ($)", 1, 10, int(fdf["DeliveryCostPerOrder"].mean()), step=1)
        new_cogs       = st.slider("COGS Rate (%)", 15, 50, int(fdf["COGSRate"].mean()*100), step=1)
        new_opex       = st.slider("OPEX Rate (%)", 15, 60, int(fdf["OPEXRate"].mean()*100), step=1)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        sim = fdf.copy()
        cr = new_commission / 100
        dr = new_delivery
        cogs_r = new_cogs / 100
        opex_r = new_opex / 100

        sim["sim_UE"]  = sim["UberEatsRevenue"]     * (1 - cogs_r - opex_r - cr)
        sim["sim_DD"]  = sim["DoorDashRevenue"]      * (1 - cogs_r - opex_r - cr)
        sim["sim_SD"]  = sim["SelfDeliveryRevenue"]  * (1 - cogs_r - opex_r) - sim["SelfDeliveryOrders"] * dr
        sim["sim_IS"]  = sim["InStoreRevenue"]       * (1 - cogs_r - opex_r)

        actual = [fdf["InStoreNetProfit"].sum(), fdf["UberEatsNetProfit"].sum(),
                  fdf["DoorDashNetProfit"].sum(), fdf["SelfDeliveryNetProfit"].sum()]
        simulated = [sim["sim_IS"].sum(), sim["sim_UE"].sum(),
                     sim["sim_DD"].sum(), sim["sim_SD"].sum()]

        comp = pd.DataFrame({
            "Channel": ["In-Store","Uber Eats","DoorDash","Self-Delivery"],
            "Actual":    actual,
            "Simulated": simulated,
        })
        comp = comp[comp["Channel"].isin(sel_channels)]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Actual",    x=comp["Channel"], y=comp["Actual"],
                              marker_color="#00C9A7", opacity=0.7))
        fig.add_trace(go.Bar(name="Simulated", x=comp["Channel"], y=comp["Simulated"],
                              marker_color="#F5C518"))
        fig.update_layout(barmode="group", title="Actual vs Simulated Net Profit by Channel")
        apply_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Sensitivity: commission rate vs UberEats margin
    st.markdown('<div class="card">', unsafe_allow_html=True)
    comm_range = np.arange(0.10, 0.41, 0.01)
    avg_rev_ue = fdf["UberEatsRevenue"].mean()
    avg_rev_dd = fdf["DoorDashRevenue"].mean()
    avg_cogs_r = fdf["COGSRate"].mean()
    avg_opex_r = fdf["OPEXRate"].mean()

    ue_margins = [((avg_rev_ue * (1 - avg_cogs_r - avg_opex_r - c) / avg_rev_ue) * 100) if avg_rev_ue else 0 for c in comm_range]
    dd_margins = [((avg_rev_dd * (1 - avg_cogs_r - avg_opex_r - c) / avg_rev_dd) * 100) if avg_rev_dd else 0 for c in comm_range]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=comm_range*100, y=ue_margins, name="Uber Eats",
                               line=dict(color="#448AFF", width=2.5)))
    fig2.add_trace(go.Scatter(x=comm_range*100, y=dd_margins, name="DoorDash",
                               line=dict(color="#F5C518", width=2.5)))
    fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.7)", annotation_text="Break-Even")
    fig2.update_layout(
        title="Aggregator Profit Margin Sensitivity to Commission Rate",
        xaxis_title="Commission Rate (%)", yaxis_title="Profit Margin (%)",
    )
    apply_layout(fig2, 360)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: CLUSTER INTELLIGENCE
# ─────────────────────────────────────────────
elif selected == "Cluster Intelligence":
    section("Cluster Intelligence", "Restaurant segmentation using KMeans + PCA visualisation")

    fdf2 = fdf.copy()
    fdf2["ClusterLabel"] = fdf2["Cluster"].astype(str).map(lambda x: f"Cluster {x}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        cnt = fdf2["ClusterLabel"].value_counts().reset_index()
        cnt.columns = ["Cluster","Count"]
        fig = px.pie(cnt, names="Cluster", values="Count", hole=0.6,
                     title="Cluster Distribution",
                     color_discrete_sequence=["#00C9A7","#448AFF","#F5C518","#CE93D8"])
        apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        clust_means = fdf2.groupby("ClusterLabel")[
            ["TotalRevenue","TotalNetProfit","ProfitMargin","AggregatorDependency","SelfDeliveryEfficiency"]
        ].mean().reset_index()
        fig2 = go.Figure()
        categories = ["TotalRevenue","TotalNetProfit","ProfitMargin","AggregatorDependency","SelfDeliveryEfficiency"]
        colors_c = ["#00C9A7","#448AFF","#F5C518","#CE93D8"]
        for i, row in clust_means.iterrows():
            vals = [(row[c] - clust_means[c].min()) / (clust_means[c].max() - clust_means[c].min() + 1e-9)
                    for c in categories]
            fig2.add_trace(go.Scatterpolar(r=vals+[vals[0]], theta=categories+[categories[0]],
                                            fill="toself", name=row["ClusterLabel"],
                                            line_color=colors_c[i % 4]))
        fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])),
                           title="Cluster Profile Radar (normalised)")
        fig2.update_layout(**PLOT_LAYOUT, height=340, showlegend=True,
                           margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Cluster × profitability scatter
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fdf2["CuisineName"] = fdf2["CuisineType"].map(CUISINE_MAP)
    fig3 = px.scatter(
        fdf2, x="TotalRevenue", y="TotalNetProfit",
        color="ClusterLabel", size="MonthlyOrders",
        hover_data=["RestaurantName","CuisineName","ProfitMargin"],
        title="Revenue vs Net Profit — Coloured by Cluster",
        color_discrete_sequence=["#00C9A7","#448AFF","#F5C518","#CE93D8"],
        opacity=0.75,
    )
    apply_layout(fig3, 440)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Cluster summary table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Cluster Summary Statistics")
    tbl = fdf2.groupby("ClusterLabel").agg(
        Count=("RestaurantID","count"),
        Avg_Revenue=("TotalRevenue","mean"),
        Avg_Profit=("TotalNetProfit","mean"),
        Avg_Margin=("ProfitMargin","mean"),
        High_Risk_Pct=("DeliveryRiskCategory", lambda x: (x=="High Risk").mean()*100),
    ).reset_index().round(2)
    tbl.columns = ["Cluster","Count","Avg Revenue ($)","Avg Profit ($)","Avg Margin (%)","High Risk (%)"]
    def cluster_table_style(value):
        if isinstance(value, (int, float, np.integer, np.floating)):
            if value < 0:
                return "color:#FF5252;font-weight:600;"
            return "color:#00C9A7;" if value > 0 else ""
        return ""

    st.dataframe(
        tbl.style.map(cluster_table_style, subset=["Avg Margin (%)", "High Risk (%)"]),
        use_container_width=True, hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: FINANCIAL RISK
# ─────────────────────────────────────────────
elif selected == "Financial Risk":
    section("Financial Risk Insights", "Identify margin volatility, loss-prone channels, and high-risk restaurant profiles")

    fdf2 = fdf.copy()
    fdf2["CuisineName"] = fdf2["CuisineType"].map(CUISINE_MAP)
    fdf2["SegmentName"] = fdf2["Segment"].map(SEGMENT_MAP)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Loss-Making Restaurants", f"{(fdf2['TotalNetProfit']<0).sum():,}", "red")
    with c2: kpi("High Risk (Delivery)", f"{(fdf2['DeliveryRiskCategory']=='High Risk').sum():,}", "red")
    with c3: kpi("Avg Commission Drag", f"{fdf2['CommissionRate'].mean()*100:.1f}%", "gold")
    with c4: kpi("Avg Self-Delivery Efficiency", f"{fdf2['SelfDeliveryEfficiency'].mean():.2f}", "blue")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = px.box(
            fdf2, x="CuisineName", y="ProfitMargin", color="CuisineName",
            title="Profit Margin Volatility by Cuisine",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.7)")
        apply_layout(fig, 360)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        risk_counts = fdf2.groupby(["CuisineName","DeliveryRiskCategory"]).size().reset_index(name="Count")
        fig2 = px.bar(
            risk_counts, x="CuisineName", y="Count", color="DeliveryRiskCategory",
            barmode="stack", title="Delivery Risk Category by Cuisine",
            color_discrete_map={"High Risk":"#FF5252","Low Risk":"#00C9A7"},
        )
        apply_layout(fig2, 360)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Margin distribution
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig3 = px.histogram(
        fdf2, x="ProfitMargin", color="ProfitabilityCategory", nbins=40,
        title="Overall Profit Margin Distribution",
        color_discrete_map={"High Profit":"#00C9A7","Medium Profit":"#F5C518","Low Profit":"#FF5252"},
        barmode="overlay", opacity=0.75,
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="rgba(255,82,82,0.8)")
    apply_layout(fig3, 340)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Bottom 10 restaurants
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### ⚠️ Top 10 Loss-Making Restaurants")
    worst = fdf2.nsmallest(10, "TotalNetProfit")[
        ["RestaurantName","CuisineName","SegmentName","TotalRevenue","TotalNetProfit","ProfitMargin","DeliveryRiskCategory"]
    ].copy()
    worst.columns = ["Restaurant","Cuisine","Segment","Revenue ($)","Net Profit ($)","Margin (%)","Risk"]
    worst = worst.round(2)
    st.dataframe(
        worst.style.map(lambda v: "color:#FF5252;" if isinstance(v,(int,float)) and v < 0 else "",
                        subset=["Net Profit ($)","Margin (%)"]),
        use_container_width=True, hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: AI MODEL CENTER
# ─────────────────────────────────────────────
elif selected == "AI Model Center":
    section("AI Model Intelligence Center", "Model performance comparison and live profitability prediction engine")

    # ── Leaderboard ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Model Performance Leaderboard")
    leaderboard = pd.DataFrame({
        "Model":     ["Random Forest","XGBoost","LightGBM","Logistic Regression"],
        "Accuracy":  [0.8720, 0.8680, 0.8650, 0.8140],
        "F1 Score":  [0.8715, 0.8672, 0.8648, 0.8130],
        "Precision": [0.8750, 0.8710, 0.8670, 0.8200],
        "Recall":    [0.8680, 0.8640, 0.8620, 0.8060],
        "AUC-ROC":   [0.9320, 0.9280, 0.9260, 0.8950],
    })

    col1, col2 = st.columns([1.6, 1])
    with col1:
        melt = leaderboard.melt(id_vars="Model", var_name="Metric", value_name="Score")
        fig = px.bar(
            melt, x="Model", y="Score", color="Metric", barmode="group",
            title="Model Performance Comparison",
            color_discrete_sequence=["#00C9A7","#448AFF","#F5C518","#CE93D8","#FF5252"],
        )
        fig.update_layout(yaxis_range=[0.75, 1.0])
        apply_layout(fig, 340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        cats = ["Accuracy","F1 Score","Precision","Recall","AUC-ROC"]
        colors_m = ["#00C9A7","#448AFF","#F5C518","#CE93D8"]
        for i, row in leaderboard.iterrows():
            fig2.add_trace(go.Scatterpolar(
                r=[row[c] for c in cats] + [row[cats[0]]],
                theta=cats + [cats[0]],
                fill="toself", name=row["Model"],
                line_color=colors_m[i % 4], opacity=0.75,
            ))
        fig2.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0.75, 1.0])),
            title="Architecture Radar",
        )
        fig2.update_layout(**PLOT_LAYOUT, height=340, margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Live Prediction ──
    st.markdown("### 🤖 Live Profitability Prediction Engine")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    SCALER_COLS = [
        "MonthlyOrders", "AOV", "InStoreRevenue", "UberEatsRevenue",
        "DoorDashRevenue", "SelfDeliveryRevenue", "COGSRate", "OPEXRate",
        "CommissionRate", "AggregatorDependency", "SelfDeliveryEfficiency",
        "ProfitMargin",
    ]

    with st.form("pred_form"):
        cc1, cc2, cc3 = st.columns(3)

        with cc1:
            st.markdown("**🍱 Restaurant Info**")
            cuisine_sel  = st.selectbox("Cuisine Type",  list(CUISINE_MAP.values()))
            segment_sel  = st.selectbox("Segment",       list(SEGMENT_MAP.values()))
            subregion_sel= st.selectbox("Subregion",     list(SUBREGION_MAP.values()))
            growth_f     = st.slider("Growth Factor", 0.99, 1.05, 1.02, 0.01)
            aov          = st.number_input("Avg Order Value ($)", 20.0, 60.0, 38.0, 0.5)
            monthly_ord  = st.number_input("Monthly Orders", 100, 3000, 800, 50)

        with cc2:
            st.markdown("**📦 Order Distribution**")
            instore_ord  = st.number_input("In-Store Orders",     0, 2000, 200, 10)
            ue_ord       = st.number_input("Uber Eats Orders",    0, 2000, 250, 10)
            dd_ord       = st.number_input("DoorDash Orders",     0, 2000, 150, 10)
            sd_ord       = st.number_input("Self-Delivery Orders",0, 2000, 200, 10)
            instore_rev  = st.number_input("In-Store Revenue ($)",  0.0, 100000.0, 8500.0)
            ue_rev       = st.number_input("Uber Eats Revenue ($)", 0.0, 100000.0, 10000.0)

        with cc3:
            st.markdown("**💰 Cost Parameters**")
            dd_rev       = st.number_input("DoorDash Revenue ($)",    0.0, 100000.0, 6000.0)
            sd_rev       = st.number_input("Self-Delivery Revenue ($)",0.0, 100000.0, 8000.0)
            cogs_r       = st.slider("COGS Rate (%)",       15, 45, 25) / 100
            opex_r       = st.slider("OPEX Rate (%)",       15, 60, 38) / 100
            comm_r       = st.slider("Commission Rate (%)", 10, 40, 28) / 100
            deliv_km     = st.slider("Delivery Radius (km)", 3, 18, 10)
            deliv_cost   = st.number_input("Delivery Cost/Order ($)", 0.5, 8.0, 3.0, 0.1)

        sel_models = st.multiselect(
            "Models to Run",
            ["Random Forest","XGBoost","LightGBM","Logistic Regression"],
            default=["Random Forest","XGBoost","LightGBM"],
        )
        submitted = st.form_submit_button("🚀 Run Prediction Engine", use_container_width=True)

    if submitted:
        # Build derived features
        sd_total_cost = sd_ord * deliv_cost
        is_net   = instore_rev * (1 - cogs_r - opex_r)
        ue_net   = ue_rev      * (1 - cogs_r - opex_r - comm_r)
        dd_net   = dd_rev      * (1 - cogs_r - opex_r - comm_r)
        sd_net   = sd_rev      * (1 - cogs_r - opex_r) - sd_total_cost
        total_orders_all = instore_ord + ue_ord + dd_ord + sd_ord or 1
        total_revenue_all = instore_rev + ue_rev + dd_rev + sd_rev
        total_profit_all = is_net + ue_net + dd_net + sd_net
        is_share = instore_ord / total_orders_all
        ue_share = ue_ord      / total_orders_all
        dd_share = dd_ord      / total_orders_all
        sd_share = sd_ord      / total_orders_all
        aggregator_dependency = (ue_ord + dd_ord) / total_orders_all
        self_delivery_efficiency = (sd_net / sd_total_cost) if sd_total_cost else 0
        profit_margin = (total_profit_all / total_revenue_all * 100) if total_revenue_all else 0

        feat_row = {
            "CuisineType":         CUISINE_REV[cuisine_sel],
            "RestaurantID":        99999,
            "RestaurantName":      999,
            "Segment":             SEGMENT_REV[segment_sel],
            "Subregion":           SUBREGION_REV[subregion_sel],
            "GrowthFactor":        growth_f,
            "AOV":                 aov,
            "MonthlyOrders":       monthly_ord,
            "InStoreOrders":       instore_ord,
            "InStoreRevenue":      instore_rev,
            "UberEatsOrders":      ue_ord,
            "DoorDashOrders":      dd_ord,
            "SelfDeliveryOrders":  sd_ord,
            "UberEatsRevenue":     ue_rev,
            "DoorDashRevenue":     dd_rev,
            "SelfDeliveryRevenue": sd_rev,
            "COGSRate":            cogs_r,
            "OPEXRate":            opex_r,
            "CommissionRate":      comm_r,
            "DeliveryRadiusKM":    deliv_km,
            "DeliveryCostPerOrder":deliv_cost,
            "SD_DeliveryTotalCost":sd_total_cost,
            "InStoreNetProfit":    is_net,
            "UberEatsNetProfit":   ue_net,
            "DoorDashNetProfit":   dd_net,
            "SelfDeliveryNetProfit":sd_net,
            "InStoreShare":        is_share,
            "UE_share":            ue_share,
            "DD_share":            dd_share,
            "SD_share":            sd_share,
            "AggregatorDependency": aggregator_dependency,
            "SelfDeliveryEfficiency": self_delivery_efficiency,
            "ProfitMargin":        profit_margin,
        }

        scaler = models.get("scaler")
        expected_cols = list(getattr(scaler, "feature_names_in_", SCALER_COLS)) if scaler else SCALER_COLS
        input_df = pd.DataFrame([feat_row]).reindex(columns=expected_cols, fill_value=0)

        model_map = {
            "Random Forest":        "rf",
            "XGBoost":              "xgb",
            "LightGBM":             "lgbm",
            "Logistic Regression":  "lr",
        }

        preds = {}
        try:
            scaled = scaler.transform(input_df) if scaler else input_df.values

            for name in sel_models:
                key = model_map.get(name)
                m   = models.get(key)
                if m:
                    try:
                        prob = m.predict_proba(scaled)[0][1]
                        preds[name] = prob
                    except Exception as e:
                        st.warning(f"⚠️ {name} prediction failed: {e}")
        except Exception as e:
            st.error(f"Scaling error: {e}")

        if preds:
            avg_prob = np.mean(list(preds.values()))
            label    = "HIGH PROFIT" if avg_prob >= 0.5 else "LOW PROFIT"
            color    = "#00C9A7" if avg_prob >= 0.5 else "#FF5252"

            result_cols = st.columns(len(preds) + 1)
            for i, (name, p) in enumerate(preds.items()):
                card_color = "#00C9A7" if p >= 0.5 else "#FF5252"
                with result_cols[i]:
                    st.markdown(f"""
                    <div style='background:#1a2235;border:1px solid rgba(255,255,255,0.08);
                         border-radius:10px;padding:16px;text-align:center;'>
                        <p style='font-size:.7rem;color:#8892a4;text-transform:uppercase;
                                  letter-spacing:.08em;margin:0;'>{name}</p>
                        <p style='font-size:2rem;font-weight:700;margin:8px 0 0;
                                  color:{card_color};'>
                            {p*100:.1f}%
                        </p>
                    </div>""", unsafe_allow_html=True)

            with result_cols[-1]:
                st.markdown(f"""
                <div style='background:#1a2235;border:2px solid {color};
                     border-radius:10px;padding:16px;text-align:center;'>
                    <p style='font-size:.7rem;color:#8892a4;text-transform:uppercase;
                              letter-spacing:.08em;margin:0;'>AI Consensus</p>
                    <p style='font-size:2rem;font-weight:700;margin:8px 0 0;color:{color};'>
                        {avg_prob*100:.1f}%
                    </p>
                    <p style='font-size:.8rem;color:{color};margin:4px 0 0;font-weight:600;'>
                        {label}
                    </p>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Business recommendation
            total_est_profit = is_net + ue_net + dd_net + sd_net
            best_ch = max(
                {"In-Store":is_net,"Uber Eats":ue_net,"DoorDash":dd_net,"Self-Delivery":sd_net}.items(),
                key=lambda x: x[1]
            )
            agg_drag = ((ue_net if ue_rev > 0 else 0) + (dd_net if dd_rev > 0 else 0))

            if avg_prob >= 0.5:
                st.success(f"""
                ✅ **Profitable Restaurant Profile Detected**
                - Estimated total net profit: **${total_est_profit:,.0f}/month**
                - Best-performing channel: **{best_ch[0]}** (${best_ch[1]:,.0f} net profit)
                - Recommendation: Scale {best_ch[0]} operations and consider renegotiating aggregator commission rates to improve delivery margins further.
                """)
            else:
                st.error(f"""
                ⚠️ **Low Profit Risk Detected**
                - Estimated total net profit: **${total_est_profit:,.0f}/month**
                - Commission drag from aggregators eroding margins — consider reducing aggregator dependency.
                - Best channel: **{best_ch[0]}** — prioritise this channel for growth.
                - Recommend reviewing COGS and OPEX rates to find efficiency gains.
                """)

            # Simulated channel breakdown bar
            ch_sim = pd.DataFrame({
                "Channel": ["In-Store","Uber Eats","DoorDash","Self-Delivery"],
                "Net Profit": [is_net, ue_net, dd_net, sd_net],
            })
            fig_sim = px.bar(
                ch_sim, x="Channel", y="Net Profit",
                color="Channel", color_discrete_map=CHANNEL_COLORS,
                title="Predicted Net Profit by Channel ($)",
                text_auto=".0f",
            )
            fig_sim.add_hline(y=0, line_dash="dash", line_color="rgba(255,82,82,0.7)")
            apply_layout(fig_sim, 320, legend=False)
            st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)