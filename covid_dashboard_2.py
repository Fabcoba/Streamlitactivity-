# ============================================================
# covid_dashboard.py — FABCO LABS Investigation Center
# COVID-19 Hospital & ICU Burden Analysis
# Purpose: Pandemic preparedness for future viral outbreaks
# Run: python3 -m streamlit run covid_dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import math
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="FABCO LABS — COVID-19 Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #080f1e !important;
    color: #c9d6e3;
}
.main .block-container { padding: 0 2rem 2rem 2rem; max-width: 100%; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #060d1a !important; border-right: 1px solid #0d1b35; }
section[data-testid="stSidebar"] * { color: #4a6080 !important; }
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 1px;
}

/* KPI cards */
.kpi-card {
    background: #0a1628;
    border: 1px solid #0d1b35;
    border-top: 2px solid #00d4ff;
    border-radius: 10px;
    padding: 20px 18px 16px;
}
.kpi-card.red    { border-top-color: #ff4757; }
.kpi-card.teal   { border-top-color: #2ed573; }
.kpi-card.purple { border-top-color: #a55eea; }
.kpi-label { font-size: 0.62rem; color: #2a4060; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
.kpi-value { font-size: 1.9rem; font-weight: 700; color: #e8f0fe; line-height: 1; font-family: 'Space Mono', monospace; }
.kpi-sub   { font-size: 0.68rem; color: #1a3050; margin-top: 5px; }

/* Chart title */
.chart-title {
    font-size: 0.78rem; font-weight: 600; color: #c9d6e3;
    margin: 0 0 4px 0; letter-spacing: 0.3px;
}
.chart-subtitle {
    font-size: 0.68rem; color: #2a4060; margin: 0 0 12px 0;
}

/* Section */
.section-title {
    font-size: 0.62rem; font-weight: 700; color: #00d4ff;
    text-transform: uppercase; letter-spacing: 2.5px;
    margin: 40px 0 6px 0; padding-bottom: 10px;
    border-bottom: 1px solid #0d1b35;
}
.section-story {
    font-size: 0.82rem; color: #4a6080; line-height: 1.75;
    margin-bottom: 20px; max-width: 900px;
}
.section-story b { color: #8aaac8; }
.section-story .hl { color: #00d4ff; font-weight: 600; }
.section-story .hl-r { color: #ff4757; font-weight: 600; }

/* Header */
.fabco-header {
    background: #060d1a;
    border: 1px solid #0d1b35;
    border-radius: 14px;
    padding: 32px 40px;
    margin-bottom: 32px;
    display: flex; align-items: center; gap: 28px;
}
.fabco-logo {
    width: 64px; height: 64px;
    background: radial-gradient(circle at 35% 35%, #8b0000, #3d0000);
    border-radius: 50%;
    animation: vpulse 3s ease-in-out infinite;
    box-shadow: 0 0 24px rgba(180,0,0,0.45);
    flex-shrink: 0; position: relative;
}
.fabco-logo::after {
    content:''; position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    width:80px; height:80px; border-radius:50%;
    border: 1px solid rgba(180,0,0,0.2);
    animation: vring 3s ease-in-out infinite;
}
@keyframes vpulse {
    0%,100% { transform:scale(1); box-shadow:0 0 24px rgba(180,0,0,0.45); }
    50%      { transform:scale(1.07); box-shadow:0 0 36px rgba(180,0,0,0.65); }
}
@keyframes vring {
    0%,100% { transform:translate(-50%,-50%) scale(1); opacity:0.35; }
    50%      { transform:translate(-50%,-50%) scale(1.2); opacity:0; }
}
.fabco-text h1 { color: #e8f0fe; font-size: 1.55rem; font-weight: 700; margin: 0 0 4px; letter-spacing: -0.4px; }
.fabco-text .org { color: #00d4ff; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }
.fabco-text .desc { color: #2a4060; font-size: 0.75rem; line-height: 1.5; max-width: 620px; }

/* Narrative block */
.story-block {
    background: #0a1628;
    border-left: 3px solid #00d4ff;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin-bottom: 24px;
    font-size: 0.82rem; color: #4a6080; line-height: 1.75;
}
.story-block b { color: #8aaac8; }
.story-block .hl { color: #00d4ff; font-weight: 600; }
.story-block .hl-r { color: #ff4757; font-weight: 600; }

#MainMenu, footer, .stDeployButton { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ── Colors — only 2 used in every chart ──────────────────────
CYAN      = "#00d4ff"   # relevant data
GRAY      = "#1a3050"   # everything else
RED       = "#ff4757"   # secondary accent (ICU / warnings only)
PLOT_BG   = "#080f1e"
GRID      = "#0d1b35"
TICK      = "#2a4060"

def dark_fig(fig, height=320, title=""):
    """Apply dark theme to all Plotly figures."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40 if title else 20, b=10),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(family="Space Grotesk", color=TICK, size=11),
        xaxis=dict(showgrid=False, color=TICK, tickfont=dict(size=10), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRID, color=TICK, tickfont=dict(size=10), zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=TICK)),
        title=dict(text=title, font=dict(size=12, color="#8aaac8"), x=0, pad=dict(t=4)) if title else {},
        showlegend=False,
    )
    return fig

# ── Load data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("WHO-COVID-19-global-hosp-icu-data.csv")
    df["Date_reported"] = pd.to_datetime(df["Date_reported"])
    df.columns = [c.strip() for c in df.columns]
    region_map = {
        "EUR":"Europe","AMR":"Americas","WPR":"Western Pacific",
        "SEAR":"South-East Asia","EMR":"Eastern Mediterranean",
        "AFR":"Africa","OTHER":"Other"
    }
    df["Region"] = df["WHO_region"].map(region_map).fillna(df["WHO_region"])
    df["Country"] = df["Country"].str.title()
    df["Year"]    = df["Date_reported"].dt.year
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    spikes = "".join([
        f'<div style="position:absolute;width:7px;height:7px;background:#cc0000;border-radius:50%;'
        f'box-shadow:0 0 4px rgba(200,0,0,0.6);'
        f'left:{60+52*math.cos(i*30*math.pi/180)-3.5:.0f}px;'
        f'top:{60+52*math.sin(i*30*math.pi/180)-3.5:.0f}px;"></div>'
        for i in range(12)
    ])
    st.markdown(f"""
    <div style="display:flex;justify-content:center;padding:20px 0 8px;">
      <div style="position:relative;width:120px;height:120px;display:flex;align-items:center;justify-content:center;">
        {spikes}
        <div class="fabco-logo"></div>
      </div>
    </div>
    <p style="text-align:center;font-size:0.6rem;color:#1a3050;letter-spacing:2.5px;text-transform:uppercase;margin-bottom:24px;">SARS-CoV-2</p>
    <p style="font-size:0.7rem;color:#00d4ff;letter-spacing:2px;text-transform:uppercase;margin:0 0 2px;">FABCO LABS</p>
    <p style="font-size:0.78rem;color:#2a4060;margin-bottom:24px;">Investigation Center</p>
    """, unsafe_allow_html=True)

    min_date = df["Date_reported"].min().date()
    max_date = df["Date_reported"].max().date()
    date_range = st.date_input("Date Range",
        [pd.to_datetime("2020-01-01").date(), max_date],
        min_value=min_date, max_value=max_date)
    all_regions = sorted(df["Region"].unique().tolist())
    sel_regions = st.multiselect("Regions", all_regions, default=all_regions)
    top_n = st.slider("Top N Countries", 5, 20, 10)
    st.markdown("---")
    st.markdown("<p style='font-size:0.6rem;color:#1a3050;'>Source: WHO COVID-19 Repository<br>240 countries · 2020–2026</p>", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────
s = pd.to_datetime(date_range[0])
e = pd.to_datetime(date_range[1])
dff = df[(df["Date_reported"]>=s)&(df["Date_reported"]<=e)&(df["Region"].isin(sel_regions))].copy()

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div class="fabco-header">
  <div class="fabco-logo"></div>
  <div class="fabco-text">
    <div class="org">FABCO LABS Investigation Center</div>
    <h1>COVID-19 Hospital & ICU Burden Analysis</h1>
    <div class="desc">
      Analyzing global hospitalization and ICU admission patterns from the 2020–2026 pandemic
      to build a preparedness framework for future viral outbreaks. Data source: WHO COVID-19 Repository.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── INTRO STORY ───────────────────────────────────────────────
st.markdown("""
<div class="story-block">
<b>Why this matters.</b> When COVID-19 emerged, healthcare systems worldwide were caught unprepared.
Hospitals ran out of ICU beds, ventilators, and staff. At <span class="hl">FABCO LABS</span>, our mission
is to ensure this never happens again. By dissecting the hospitalization and ICU data from the pandemic,
we can identify <b>when systems broke down, which regions were most vulnerable, and what signals
preceded collapse</b> — so the next outbreak finds us ready.
</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────
hosp_total = dff["Covid_new_hospitalizations_last_7days"].sum()
icu_total  = dff["Covid_new_icu_admissions_last_7days"].sum()
countries_rep = dff.dropna(subset=["Covid_new_hospitalizations_last_7days"])["Country"].nunique()
icu_df = dff.dropna(subset=["Covid_new_icu_admissions_last_7days","Covid_new_hospitalizations_last_7days"])
icu_df = icu_df[icu_df["Covid_new_hospitalizations_last_7days"]>0]
icu_ratio = (icu_df["Covid_new_icu_admissions_last_7days"].sum()/
             icu_df["Covid_new_hospitalizations_last_7days"].sum()*100) if len(icu_df)>0 else 0

k1,k2,k3,k4 = st.columns(4)
with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Hospitalizations</div><div class="kpi-value">{hosp_total/1e6:.1f}M</div><div class="kpi-sub">New admissions · 7-day rolling</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi-card red"><div class="kpi-label">ICU Admissions</div><div class="kpi-value">{icu_total/1e6:.2f}M</div><div class="kpi-sub">Critical care entries</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi-card teal"><div class="kpi-label">ICU / Hosp Ratio</div><div class="kpi-value">{icu_ratio:.1f}%</div><div class="kpi-sub">Global severity index</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi-card purple"><div class="kpi-label">Countries Reporting</div><div class="kpi-value">{countries_rep}</div><div class="kpi-sub">With hospitalization data</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CHART 1 — Global Wave
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">01 · The Pandemic in Waves</div>', unsafe_allow_html=True)
st.markdown("""<div class="section-story">
The pandemic did not arrive once — it arrived in <b>waves</b>. Each surge corresponded to a new variant:
Alpha, Delta, and then the massive <span class="hl">Omicron wave of early 2022</span>, which produced
the highest hospitalization counts ever recorded. Understanding these cycles is fundamental to
anticipating the rhythm of future outbreaks and pre-positioning resources before the next peak arrives.
</div>""", unsafe_allow_html=True)

gt = dff.groupby("Date_reported")["Covid_new_hospitalizations_last_7days"].sum().reset_index()
gt = gt[gt["Covid_new_hospitalizations_last_7days"]>0]
peak = gt.loc[gt["Covid_new_hospitalizations_last_7days"].idxmax()]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=gt["Date_reported"], y=gt["Covid_new_hospitalizations_last_7days"],
    mode="lines", fill="tozeroy",
    line=dict(color=CYAN, width=2.5),
    fillcolor="rgba(0,212,255,0.07)"
))
fig1.add_annotation(
    x=peak["Date_reported"], y=peak["Covid_new_hospitalizations_last_7days"],
    text=f"<b>PEAK — {peak['Covid_new_hospitalizations_last_7days']/1e6:.2f}M</b>",
    showarrow=True, arrowhead=2, arrowcolor=CYAN,
    font=dict(size=10, color=CYAN), bgcolor="#060d1a",
    bordercolor=CYAN, borderwidth=1, ax=60, ay=-40
)
dark_fig(fig1, 300, "Global New Hospitalizations (7-day rolling) · All Regions")
fig1.update_layout(
    xaxis_title="", yaxis_title="New Hospitalizations",
    yaxis=dict(tickformat=".2s", showgrid=True, gridcolor=GRID, color=TICK)
)
st.plotly_chart(fig1, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# CHART 2 — Regional comparison (bar)
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">02 · Where Did the Burden Fall?</div>', unsafe_allow_html=True)
st.markdown("""<div class="section-story">
The pandemic was not experienced equally. <span class="hl">Europe and the Americas</span> concentrated
the vast majority of reported hospitalizations, a result of both high disease burden and stronger
reporting infrastructure. Regions like Africa appear low — but this likely reflects
<b>data collection gaps</b> rather than true disease absence, a critical blind spot for
outbreak preparedness planning.
</div>""", unsafe_allow_html=True)

# Total hospitalizations by region — highlighted vs gray
reg_totals = (dff.groupby("Region")["Covid_new_hospitalizations_last_7days"]
              .sum().dropna().sort_values(ascending=True))
top_region = reg_totals.index[-1]
reg_colors = [CYAN if r == top_region else GRAY for r in reg_totals.index]

fig2 = go.Figure(go.Bar(
    x=reg_totals.values, y=reg_totals.index, orientation="h",
    marker_color=reg_colors,
    text=[f"{v/1e6:.1f}M" for v in reg_totals.values],
    textposition="outside", textfont=dict(size=10, color=TICK)
))
dark_fig(fig2, 300, "Total Hospitalizations by WHO Region (7-day) · Highlighted: Highest Burden")
fig2.update_layout(
    xaxis=dict(showgrid=True, gridcolor=GRID, tickformat=".2s"),
    margin=dict(r=60)
)
st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# CHART 3 — Top N countries
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">03 · Country-Level Concentration</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="section-story">
Drilling down to the country level, the concentration of burden becomes even more striking.
The <span class="hl-r">top country alone</span> often accounts for more hospitalizations than
the next several combined. For FABCO LABS, this signals where international response resources
should be pre-positioned — and which healthcare systems need the most capacity-building investment
before the next outbreak.
</div>""", unsafe_allow_html=True)

ct = (dff.groupby("Country")["Covid_new_hospitalizations_last_7days"]
      .sum().dropna().sort_values(ascending=True).tail(top_n))
ct_colors = [CYAN if i == len(ct)-1 else GRAY for i in range(len(ct))]

fig3 = go.Figure(go.Bar(
    x=ct.values, y=ct.index, orientation="h",
    marker_color=ct_colors,
    text=[f"{v/1e6:.2f}M" for v in ct.values],
    textposition="outside", textfont=dict(size=9.5, color=TICK)
))
dark_fig(fig3, max(300, top_n*32), f"Top {top_n} Countries by Total Hospitalizations (7-day) · Highlighted: #1")
fig3.update_layout(xaxis=dict(showgrid=True, gridcolor=GRID, tickformat=".2s"), margin=dict(r=70))
st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# CHART 4 — ICU vs Hosp scatter (Matplotlib)
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">04 · The ICU Overload Signal</div>', unsafe_allow_html=True)
st.markdown("""<div class="section-story">
Not all hospitalizations are equal. When ICU admissions grow <b>faster than general hospitalizations</b>,
it signals a more severe variant or an overwhelmed system pushing patients to critical care.
Countries above the trendline experienced <span class="hl">disproportionate ICU pressure</span> —
the clearest early warning sign of system collapse. Monitoring this ratio in real-time
is FABCO LABS' primary recommended preparedness metric.
</div>""", unsafe_allow_html=True)

sc = dff.groupby("Country").agg(
    H=("Covid_new_hospitalizations_last_7days","sum"),
    I=("Covid_new_icu_admissions_last_7days","sum")
).dropna().reset_index()
sc = sc[(sc["H"]>1000)&(sc["I"]>0)]
top3 = sc.nlargest(3,"H")["Country"].tolist()

fig4, ax = plt.subplots(figsize=(10, 4.5))
fig4.patch.set_facecolor(PLOT_BG); ax.set_facecolor(PLOT_BG)

# Gray dots — background
bg = sc[~sc["Country"].isin(top3)]
ax.scatter(bg["H"], bg["I"], c=GRAY, s=25, alpha=0.6, zorder=2)

# Cyan dots — highlighted
hi = sc[sc["Country"].isin(top3)]
ax.scatter(hi["H"], hi["I"], c=CYAN, s=100, alpha=1.0, zorder=4, edgecolors="#009bb5", linewidths=1)
for _, row in hi.iterrows():
    ax.annotate(row["Country"], (row["H"], row["I"]),
                fontsize=8.5, color=CYAN, fontweight="600",
                xytext=(7, 4), textcoords="offset points")

# Trend line
b, m = np.polynomial.polynomial.polyfit(sc["H"].values, sc["I"].values, 1)
xl = np.linspace(sc["H"].min(), sc["H"].max(), 100)
ax.plot(xl, b+m*xl, color="#2a4060", linewidth=1.5, linestyle="--", alpha=0.7)

ax.set_title("ICU Admissions vs. Hospitalizations by Country · Highlighted: Highest Volume",
             fontsize=10, color="#8aaac8", pad=10)
ax.set_xlabel("Total New Hospitalizations (7-day)", fontsize=9, color=TICK)
ax.set_ylabel("Total New ICU Admissions (7-day)", fontsize=9, color=TICK)
ax.tick_params(colors=TICK, labelsize=8.5)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M" if x>=1e6 else f"{x/1e3:.0f}K"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:.0f}K"))
for spine in ax.spines.values(): spine.set_edgecolor(GRID)
ax.grid(color=GRID, linewidth=0.6)
plt.tight_layout()
st.pyplot(fig4, use_container_width=True)
plt.close()

# ══════════════════════════════════════════════════════════════
# CHART 5 — Heatmap (Seaborn)
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">05 · Year-by-Year Intensity Map</div>', unsafe_allow_html=True)
st.markdown("""<div class="section-story">
Viewing the pandemic across years and regions simultaneously reveals a key preparedness insight:
<span class="hl">the burden was not static</span>. It shifted geographically and intensified
unpredictably. Any future outbreak response framework must account for this mobility —
a region that appeared safe in year one may become the epicenter in year two.
</div>""", unsafe_allow_html=True)

hm = (dff.groupby(["Region","Year"])["Covid_new_hospitalizations_last_7days"]
      .sum().unstack(fill_value=0))
hm = hm.loc[:, (hm>0).any(axis=0)]

from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("fabco", [PLOT_BG, "#0d2040", "#1a3a5c", CYAN])

fig5, ax = plt.subplots(figsize=(10, 3.8))
fig5.patch.set_facecolor(PLOT_BG); ax.set_facecolor(PLOT_BG)
sns.heatmap(hm/1e6, ax=ax, cmap=cmap, linewidths=0.8, linecolor=PLOT_BG,
            annot=True, fmt=".1f", annot_kws={"size":9,"color":"#c9d6e3"},
            cbar_kws={"shrink":0.6})
ax.set_title("New Hospitalizations (Millions) by Region and Year · Brighter = Higher Burden",
             fontsize=10, color="#8aaac8", pad=10)
ax.set_xlabel(""); ax.set_ylabel("")
ax.tick_params(colors=TICK, labelsize=9)
ax.figure.axes[-1].tick_params(colors=TICK, labelsize=8)
for spine in ax.spines.values(): spine.set_visible(False)
plt.tight_layout()
st.pyplot(fig5, use_container_width=True)
plt.close()

# ══════════════════════════════════════════════════════════════
# CHART 6 — Country deep dive
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">06 · Single Country Deep Dive</div>', unsafe_allow_html=True)
st.markdown("""<div class="section-story">
To build a preparedness plan, FABCO LABS must be able to zoom into any country's trajectory.
Select a country below to examine its hospitalization and ICU curve side by side —
identifying <span class="hl">when ICU pressure diverged from hospitalizations</span>,
which marks the most dangerous moments for any healthcare system.
</div>""", unsafe_allow_html=True)

available = sorted(dff.dropna(subset=["Covid_new_hospitalizations_last_7days"])["Country"].unique().tolist())
default_idx = available.index("United States Of America") if "United States Of America" in available else 0
sel = st.selectbox("Select a country to analyze", available, index=default_idx)

cd = dff[dff["Country"]==sel].sort_values("Date_reported")

fig6 = go.Figure()
# Hospitalizations — cyan (relevant)
fig6.add_trace(go.Scatter(
    x=cd["Date_reported"], y=cd["Covid_new_hospitalizations_last_7days"],
    name="Hospitalizations", mode="lines",
    line=dict(color=CYAN, width=2.5),
    fill="tozeroy", fillcolor="rgba(0,212,255,0.06)"
))
# ICU — red accent
fig6.add_trace(go.Scatter(
    x=cd["Date_reported"], y=cd["Covid_new_icu_admissions_last_7days"],
    name="ICU Admissions", mode="lines",
    line=dict(color=RED, width=2, dash="dot")
))
dark_fig(fig6, 300, f"{sel} — Hospitalization (solid) vs ICU Admissions (dotted)")
fig6.update_layout(
    showlegend=True,
    legend=dict(orientation="h", y=1.1, font=dict(size=10, color=TICK)),
    yaxis=dict(tickformat=".2s", showgrid=True, gridcolor=GRID, color=TICK)
)
st.plotly_chart(fig6, use_container_width=True)

# ── Conclusion ────────────────────────────────────────────────
st.markdown('<div class="section-title">Conclusions & Preparedness Recommendations</div>', unsafe_allow_html=True)
st.markdown("""
<div class="story-block">
<b>What this data tells us for the next outbreak.</b><br><br>
The COVID-19 pandemic revealed three structural vulnerabilities in global healthcare systems:
(1) <span class="hl">surge capacity is regional, not global</span> — burden concentrates in specific areas and cannot be easily redistributed;
(2) <span class="hl">ICU-to-hospitalization ratio is the most actionable early warning metric</span> — when it rises above historical baseline, system overload is imminent;
(3) <span class="hl-r">data blind spots are as dangerous as the virus itself</span> — regions without reliable reporting cannot be defended.<br><br>
<b>FABCO LABS recommends:</b> Establish regional ICU surge thresholds as trigger points for emergency resource deployment.
Invest in data reporting infrastructure in low-income countries before the next outbreak begins.
Run annual simulation exercises using the wave patterns identified in this dataset.
</div>
""", unsafe_allow_html=True)

st.markdown("<br><p style='font-size:0.6rem;color:#0d1b35;text-align:center;letter-spacing:2px;'>FABCO LABS INVESTIGATION CENTER · COVID-19 HOSPITAL BURDEN ANALYSIS · WHO DATA · 2020–2026</p>", unsafe_allow_html=True)
