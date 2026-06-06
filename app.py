import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64
from pathlib import Path

st.set_page_config(
    page_title="Nestlé Energy Monitor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Load images
logo_b64 = img_to_b64("Nestlelogo.png")
icons = {
    "Overview":     img_to_b64("Overview.png"),
    "Factories":    img_to_b64("Factories.png"),
    "Anomalies":    img_to_b64("Anomalies.png"),
    "Savings":      img_to_b64("Savings.png"),
    "CO₂ Tracking": img_to_b64("CO2.png"),
}
pages = ["Overview", "Factories", "Anomalies", "Savings", "CO₂ Tracking"]

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="collapsedControl"] { display: none !important; }
    button[kind="header"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #e8f5f0 !important; }
    [data-testid="stSidebar"] * { color: #111111 !important; }

    /* Dropdowns */
    [data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1.5px solid #9FE1CB !important;
        border-radius: 8px !important;
    }

    /* Nav buttons */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 14px;
        border-radius: 10px;
        cursor: pointer;
        margin-bottom: 4px;
        font-size: 0.88rem;
        font-weight: 500;
        color: #333333;
        background: transparent;
        border: none;
        width: 100%;
        text-align: left;
        transition: background 0.15s;
    }
    .nav-btn:hover { background: #d0ece3; }
    .nav-btn.active {
        background: #ffffff;
        color: #0F6E56;
        font-weight: 700;
        border: 1.5px solid #9FE1CB;
    }
    .nav-btn img { width: 20px; height: 20px; object-fit: contain; }

    /* KPI cards */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #d4ece3;
        border-radius: 14px;
        padding: 16px 18px 12px 18px;
        text-align: center;
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-label { font-size:0.65rem; font-weight:700; color:#555; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:5px; }
    .kpi-value { font-size:2rem; font-weight:800; color:#111; line-height:1.0; }
    .kpi-unit  { font-size:0.95rem; font-weight:600; color:#333; }
    .kpi-delta-good    { font-size:0.75rem; color:#0F6E56; margin-top:4px; font-weight:600; }
    .kpi-delta-bad     { font-size:0.75rem; color:#c0392b; margin-top:4px; font-weight:600; }
    .kpi-delta-warn    { font-size:0.75rem; color:#b8680a; margin-top:4px; font-weight:600; }
    .kpi-delta-neutral { font-size:0.75rem; color:#555;    margin-top:4px; font-weight:600; }

    /* Section cards */
    .section-card { background:#fff; border:1px solid #d4ece3; border-radius:14px; padding:16px 20px; margin-bottom:14px; }
    .section-card-title { font-size:0.92rem; font-weight:700; color:#111; margin-bottom:12px; }

    /* Badges */
    .badge-danger  { background:#fdecea; color:#c0392b; padding:3px 10px; border-radius:20px; font-size:0.70rem; font-weight:700; }
    .badge-warning { background:#fef3e2; color:#b8680a; padding:3px 10px; border-radius:20px; font-size:0.70rem; font-weight:700; }
    .badge-success { background:#e8f5e9; color:#0F6E56; padding:3px 10px; border-radius:20px; font-size:0.70rem; font-weight:700; }
    .badge-open    { background:#f0f0f0; color:#444;    padding:3px 10px; border-radius:20px; font-size:0.70rem; font-weight:700; }

    /* Factory cards */
    .factory-card { background:#fff; border:1px solid #d4ece3; border-radius:14px; padding:16px 18px; margin-bottom:12px; }

    /* Anomaly rows */
    .anom-row { background:#fff; border:1px solid #e8e8e8; border-radius:10px; padding:13px 16px; margin-bottom:8px; }

    /* Banners */
    .info-banner    { background:#fef9ec; border:1px solid #f5d97a; border-radius:10px; padding:12px 16px; font-size:0.82rem; color:#444; margin-top:10px; }
    .success-banner { background:#edf7f2; border:1px solid #9FE1CB; border-radius:10px; padding:12px 16px; font-size:0.82rem; color:#0F6E56; margin-top:10px; }

    /* Page titles */
    .page-title { font-size:1.5rem; font-weight:800; color:#111; margin-bottom:2px; }
    .page-sub   { font-size:0.80rem; color:#666; margin-bottom:18px; }

    /* HTML table */
    .html-table { width:100%; border-collapse:collapse; font-size:0.83rem; }
    .html-table th { text-align:left; padding:8px 12px; color:#555; font-weight:600; font-size:0.72rem; text-transform:uppercase; border-bottom:2px solid #e8e8e8; }
    .html-table td { padding:10px 12px; border-bottom:1px solid #f0f0f0; color:#111; }
    .html-table tr:last-child td { border-bottom:none; }
    .dot-green  { display:inline-block; width:9px; height:9px; border-radius:50%; background:#1D9E75; margin-right:5px; vertical-align:middle; }
    .dot-orange { display:inline-block; width:9px; height:9px; border-radius:50%; background:#EF9F27; margin-right:5px; vertical-align:middle; }
    .dot-red    { display:inline-block; width:9px; height:9px; border-radius:50%; background:#E24B4A; margin-right:5px; vertical-align:middle; }

    /* Force sidebar always visible */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"] { transform: none !important; min-width: 220px !important; }

    /* ENG button */
    .eng-btn {
        position: fixed; top: 14px; right: 20px; z-index: 999;
        background: white; border: 1.5px solid #d4ece3;
        border-radius: 8px; padding: 5px 14px;
        font-size: 0.82rem; font-weight: 700; color: #111;
    }
</style>
""", unsafe_allow_html=True)

# ENG button
st.markdown('<div class="eng-btn">ENG ▾</div>', unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SITES = {
    "Avenches":         {"product":"Café",                "brand":"Nespresso, Starbucks", "canton":"VD", "baseline":480},
    "Bâle":             {"product":"Produits culinaires", "brand":"Thomy",                "canton":"BS", "baseline":320},
    "Broc":             {"product":"Chocolat",            "brand":"Cailler",              "canton":"FR", "baseline":560},
    "Henniez":          {"product":"Eau & Boissons",      "brand":"Henniez, Nestea",      "canton":"VD", "baseline":290},
    "Konolfingen":      {"product":"Nutrition infantile", "brand":"BEBA Bio, Alfamino",   "canton":"BE", "baseline":410},
    "Manno":            {"product":"Huiles spécialisées", "brand":"Sofinol",              "canton":"TI", "baseline":180},
    "Orbe":             {"product":"Café",                "brand":"Nescafé, Nespresso",   "canton":"VD", "baseline":620},
    "Romont":           {"product":"Café",                "brand":"Nespresso, Starbucks", "canton":"FR", "baseline":390},
    "Wangen bei Olten": {"product":"Pâtes fraîches",      "brand":"Leisi",                "canton":"SO", "baseline":240},
}
G="#1D9E75"; GD="#0F6E56"; WARN="#EF9F27"; RED="#E24B4A"; BLUE="#378ADD"; FC="#111111"
EMISSION_FACTOR=0.023; ENERGY_PRICE=0.18
np.random.seed(42)

@st.cache_data
def generate_monthly():
    rows=[]
    months=pd.date_range("2025-01-01",periods=6,freq="MS")
    for site,info in SITES.items():
        base=info["baseline"]
        for i,month in enumerate(months):
            f=1+(-0.012*i)+np.sin(i/2)*0.08+np.random.normal(0,0.07)
            mwh=round(base*f,1)
            rows.append({"site":site,"month":month,"mwh":mwh,"baseline":base,
                "product":info["product"],"brand":info["brand"],"canton":info["canton"],
                "co2e":round(mwh*EMISSION_FACTOR,1),
                "savings_chf":round(max(0,(base-mwh)*ENERGY_PRICE*1000),0)})
    return pd.DataFrame(rows)

df_m=generate_monthly()
df=df_m[df_m["month"]==df_m["month"].max()].copy()
df["pct"]=((df["mwh"]-df["baseline"])/df["baseline"]*100).round(1)
df["status"]=df["pct"].apply(lambda x:"Anomaly" if x>8 else("Review" if x>2 else "Normal"))

def kpi(label,val,delta,cls="kpi-delta-good"):
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <div class="{cls}">{delta}</div>
    </div>""",unsafe_allow_html=True)

def dot_badge(status):
    if status=="Anomaly": return '<span class="dot-red"></span><span class="badge-danger">Anomaly</span>'
    if status=="Review":  return '<span class="dot-orange"></span><span class="badge-warning">Review</span>'
    return '<span class="dot-green"></span><span class="badge-success">Normal</span>'

def prog(pct):
    w=min(int(abs(pct)*5),95)
    c=RED if pct>8 else(WARN if pct>2 else G)
    return f'<div style="background:#e0e0e0;border-radius:4px;height:6px;width:100%;margin:6px 0;"><div style="width:{w}%;background:{c};height:6px;border-radius:4px;"></div></div>'

# ── Session state for page ────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown(f"""
    <div style="text-align:center; padding: 12px 0 8px 0;">
        <img src="data:image/png;base64,{logo_b64}" style="width:85%; max-width:160px;">
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Clean radio navigation with green active style
    st.markdown("""
    <style>
        div[data-testid="stSidebar"] .stRadio > div {
            gap: 2px;
        }
        div[data-testid="stSidebar"] .stRadio label {
            padding: 9px 14px !important;
            border-radius: 10px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            color: #333333 !important;
            cursor: pointer;
            width: 100%;
            display: block;
        }
        div[data-testid="stSidebar"] .stRadio label:hover {
            background: #d0ece3 !important;
        }
        div[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
        div[data-testid="stSidebar"] .stRadio input:checked + div label {
            background: #ffffff !important;
            border: 1.5px solid #9FE1CB !important;
            color: #0F6E56 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {
            background: #ffffff !important;
        }
        /* Hide radio circles */
        div[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] { display: none; }
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
    </style>""", unsafe_allow_html=True)

    selected = st.radio("", pages,
                        index=pages.index(st.session_state.page),
                        label_visibility="collapsed",
                        key="nav_radio")
    st.session_state.page = selected

    st.divider()
    if st.session_state.page == "Factories":
        st.markdown("<div style='font-size:0.80rem;font-weight:700;color:#111;'>Filters</div>",unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.75rem;color:#333;margin-bottom:2px;'>Site</div>",unsafe_allow_html=True)
        sel_site=st.selectbox("Site",["All factories"]+list(SITES.keys()),label_visibility="collapsed")
        st.markdown("<div style='font-size:0.75rem;color:#333;margin-bottom:2px;margin-top:6px;'>Period</div>",unsafe_allow_html=True)
        sel_period=st.selectbox("Period",["Last 30 days","Last 3 months","YTD"],label_visibility="collapsed")
        st.markdown("---")
    else:
        sel_site="All factories"
        sel_period="Last 30 days"
    st.caption("Last updated: today, 08:42")
    st.caption("© Nestlé Switzerland · 2025")

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page=="Overview":
    st.markdown('<div class="page-title">Energy overview — all sites</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Last updated: today, 08:42</div>',unsafe_allow_html=True)

    total_mwh=df["mwh"].sum(); total_co2=df["co2e"].sum()
    total_save=df["savings_chf"].sum(); n_anom=(df["pct"]>2).sum()

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Total Consumption",f"{total_mwh:,.0f} <span class='kpi-unit'>MWh</span>","↓ 6% vs baseline")
    with c2: kpi("CO₂ Equivalent",f"{total_co2:,.0f} <span class='kpi-unit'>tCO₂e</span>","↓ 4% vs last month")
    with c3: kpi("Potential Savings",f"CHF {total_save/1000:.0f}<span class='kpi-unit'>k</span>",f"{n_anom} opportunities","kpi-delta-warn")
    with c4: kpi("Sites Monitored","9<span class='kpi-unit'>/9</span>","3 pending integration","kpi-delta-neutral")

    st.markdown("<br>",unsafe_allow_html=True)
    col1,col2,col3=st.columns([5,3,2])

    with col1:
        agg=df_m.groupby("month")[["mwh","baseline"]].sum().reset_index()
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=agg["month"],y=agg["mwh"],name="Actual",
            line=dict(color=G,width=2.5),fill="tozeroy",fillcolor="rgba(29,158,117,0.10)",
            mode="lines+markers",marker=dict(size=7,color=G)))
        fig.add_trace(go.Scatter(x=agg["month"],y=agg["baseline"],name="Baseline",
            line=dict(color="#aaa",width=1.5,dash="dash"),mode="lines"))
        ym=agg["mwh"].min()*0.93; yM=agg["mwh"].max()*1.07
        fig.update_layout(height=230,margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="white",paper_bgcolor="white",font=dict(color=FC),
            legend=dict(orientation="h",y=1.12,x=0,font=dict(color=FC)),
            xaxis=dict(showgrid=False,tickfont=dict(color=FC),tickformat="%b %Y"),
            yaxis=dict(gridcolor="#eee",tickfont=dict(color=FC),range=[ym,yM]),
            title=dict(text="Consumption vs baseline",font=dict(color=FC,size=13),x=0))
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        fig2=go.Figure(go.Pie(labels=["Electricity","Gas","Steam"],values=[58,29,13],hole=0.62,
            marker_colors=[G,BLUE,WARN]))
        fig2.update_layout(height=230,margin=dict(l=0,r=0,t=30,b=0),
            paper_bgcolor="white",font=dict(color=FC),
            legend=dict(font=dict(color=FC)),
            title=dict(text="By energy type",font=dict(color=FC,size=13),x=0))
        st.plotly_chart(fig2,use_container_width=True)

    with col3:
        anom_sites=df[df["pct"]>2]["site"].tolist()
        anom_html="".join([f'<div style="margin:5px 0;"><span class="badge-danger">⚠ {s}</span></div>' for s in anom_sites[:3]])
        st.markdown(f"""<div class="section-card" style="height:230px;overflow:hidden;">
            <div class="section-card-title">Anomalies detected</div>
            {anom_html or '<div style="color:#0F6E56;font-size:0.85rem;">✓ All normal</div>'}
        </div>""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    rows_html=""
    for _,row in df.iterrows():
        pct=row["pct"]; arrow="↑" if pct>0 else "↓"
        a_col=RED if pct>0 else GD
        rows_html+=f"""<tr>
            <td><b>{row['site']}</b></td>
            <td>{row['mwh']:.0f}</td>
            <td style="color:{a_col};font-weight:600;">{arrow} {abs(pct):.1f}%</td>
            <td>{dot_badge(row['status'])}</td>
        </tr>"""
    st.markdown(f"""<div class="section-card">
        <div class="section-card-title">Factory breakdown</div>
        <table class="html-table">
            <thead><tr><th>Site</th><th>MWh</th><th>vs baseline</th><th>Status</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FACTORIES
# ══════════════════════════════════════════════════════════════════════════════
elif page=="Factories":
    st.markdown('<div class="page-title">Factory breakdown — all sites</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">9 sites monitored · Last update: today, 08:42</div>',unsafe_allow_html=True)

    fdf=df if sel_site=="All factories" else df[df["site"]==sel_site]
    sites_list=fdf.to_dict("records")

    for i in range(0,len(sites_list),2):
        cols=st.columns(2)
        for j,col in enumerate(cols):
            if i+j>=len(sites_list): break
            row=sites_list[i+j]; pct=row["pct"]
            arrow="↑" if pct>0 else "↓"
            a_col=RED if pct>0 else GD
            db=dot_badge(row["status"])
            pb=prog(pct)
            msg="⚠️ Unusual peak detected" if pct>8 else("🕐 Slight overrun — monitoring" if pct>2 else "✅ On track — target met")
            with col:
                st.markdown(f"""<div class="factory-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <div>
                            <div style="font-size:0.98rem;font-weight:700;color:#111;">🏭 {row['site']}</div>
                            <div style="font-size:0.76rem;color:#555;">Switzerland · {row['canton']}</div>
                        </div>
                        <div>{db}</div>
                    </div>
                    <div style="display:flex;gap:16px;font-size:0.70rem;color:#888;margin-bottom:2px;">
                        <span>Consumption vs baseline</span><span>CO₂e</span><span>Savings</span>
                    </div>
                    <div style="font-size:0.92rem;font-weight:700;color:#111;margin-bottom:4px;">
                        {row['mwh']:.0f} MWh
                        &nbsp;<span style="color:{a_col};">{arrow} {abs(pct):.0f}%</span>
                        &nbsp;{row['co2e']:.0f} t
                        &nbsp;<span style="color:{GD};">CHF {row['savings_chf']/1000:.0f}k</span>
                    </div>
                    {pb}
                    <div style="font-size:0.78rem;color:#555;margin-top:4px;">{msg}</div>
                </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANOMALIES
# ══════════════════════════════════════════════════════════════════════════════
elif page=="Anomalies":
    st.markdown('<div class="page-title">Anomalies detected</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Auto-detected via baseline deviation · Last scan: today, 08:42</div>',unsafe_allow_html=True)

    anoms=df[df["pct"]>2].sort_values("pct",ascending=False)
    critical=anoms[anoms["pct"]>8]
    elost=anoms.apply(lambda r:max(0,r["mwh"]-r["baseline"]),axis=1).sum()

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Total Anomalies",str(len(anoms)),"this month","kpi-delta-neutral")
    with c2: kpi("Critical",str(len(critical)),"action required","kpi-delta-bad")
    with c3: kpi("Energy Lost",f"{elost:.0f} <span class='kpi-unit'>MWh</span>",f"≈ CHF {elost*ENERGY_PRICE*1000/1000:.0f}k","kpi-delta-warn")
    with c4: kpi("Resolved","3","this month","kpi-delta-good")

    st.markdown("<br>",unsafe_allow_html=True)

    entries=[
        ("HVAC peak","Avenches","+38% above baseline · 14 Jun, 03:20 AM · Electricity","Critical","Open","#E24B4A"),
        ("Compressor overload","Broc","+29% above baseline · 11 Jun, 11:45 PM · Gas","Critical","Open","#E24B4A"),
        ("Lighting off-hours","Orbe","+11% above baseline · 09 Jun, 10:00 PM · Electricity","Warning","Resolved","#EF9F27"),
        ("Steam indicator","Henniez","+8% above baseline · 07 Jun, 06:15 AM · Steam","Warning","Resolved","#EF9F27"),
    ]
    for title,site,sub,sev,stat,dot_col in entries:
        sev_cls ="badge-danger" if sev=="Critical" else "badge-warning"
        stat_cls="badge-open"   if stat=="Open"    else "badge-success"
        st.markdown(f"""<div class="anom-row" style="display:flex;align-items:center;gap:12px;">
            <div style="width:10px;height:10px;border-radius:50%;background:{dot_col};flex-shrink:0;"></div>
            <div style="flex:1;">
                <div style="font-weight:700;color:#111;font-size:0.90rem;">{title} — {site}</div>
                <div style="font-size:0.76rem;color:#666;margin-top:2px;">{sub}</div>
            </div>
            <span class="{sev_cls}">{sev}</span>
            <span class="{stat_cls}">{stat}</span>
            <span style="font-size:0.78rem;color:{BLUE};cursor:pointer;">View →</span>
        </div>""",unsafe_allow_html=True)

    st.markdown(f"""<div class="info-banner">
        💡 <b>Detection method:</b> Z-score baseline model — flags consumption deviating
        more than 2σ from 30-day rolling average per site.
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAVINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page=="Savings":
    st.markdown('<div class="page-title">Savings & opportunities</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Identified via anomaly detection & baseline analysis</div>',unsafe_allow_html=True)

    total_pot=df["savings_chf"].sum(); realized=total_pot*0.37
    mwh_av=df.apply(lambda r:max(0,r["mwh"]-r["baseline"]),axis=1).sum()
    open_opp=(df["pct"]>2).sum()

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Total Potential",f"CHF {total_pot/1000:.0f}<span class='kpi-unit'>k</span>","across all sites")
    with c2: kpi("Already Realized",f"CHF {realized/1000:.0f}<span class='kpi-unit'>k</span>","↑ 6% vs last month")
    with c3: kpi("MWh Avoidable",f"{mwh_av:.0f} <span class='kpi-unit'>MWh</span>","if all actions taken","kpi-delta-warn")
    with c4: kpi("Open Opportunities",str(open_opp),"awaiting action","kpi-delta-warn")

    st.markdown("<br>",unsafe_allow_html=True)

    opps=[
        ("HVAC scheduling optimisation — Avenches","Reduce off-hours HVAC runtime by 40% · Electricity","High",75,"CHF 14k","52 MWh saved"),
        ("Compressor maintenance — Broc","Fix compressor efficiency loss · Gas","Medium",40,"CHF 10k","38 MWh saved"),
        ("LED lighting upgrade — Bâle","Replace legacy lighting system · Electricity","Low",20,"CHF 6k","28 MWh saved"),
        ("Steam line insulation — Henniez","Reduce steam heat loss · Steam","Low",10,"CHF 8k","24 MWh saved"),
    ]

    st.markdown('<div class="section-card"><div class="section-card-title">⚡ Top opportunities <span style="font-size:0.75rem;color:#888;font-weight:400;float:right;">Sorted by impact</span></div>',unsafe_allow_html=True)
    for title,desc,prio,p,chf,mwh in opps:
        p_cls="badge-danger" if prio=="High" else("badge-warning" if prio=="Medium" else "badge-open")
        st.markdown(f"""<div style="padding:12px 0;border-bottom:1px solid #f0f0f0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-weight:700;color:#111;font-size:0.90rem;">{title}</span>
                    &nbsp;<span class="{p_cls}">{prio}</span><br>
                    <span style="font-size:0.76rem;color:#666;">{desc}</span>
                </div>
                <div style="text-align:right;min-width:100px;">
                    <div style="font-size:1rem;font-weight:800;color:{GD};">{chf}</div>
                    <div style="font-size:0.76rem;color:#666;">{mwh}</div>
                </div>
            </div>
            <div style="background:#e0e0e0;border-radius:4px;height:6px;margin-top:8px;">
                <div style="width:{p}%;background:{G};height:6px;border-radius:4px;"></div>
            </div>
            <div style="font-size:0.70rem;color:#888;margin-top:3px;">{p}% action progress</div>
        </div>""",unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown(f"""<div class="success-banner">
        ↗ Implementing all open opportunities would avoid <b>142 MWh</b> and save <b>CHF 24k</b> over the next 3 months.
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CO2 TRACKING
# ══════════════════════════════════════════════════════════════════════════════
elif page=="CO₂ Tracking":
    st.markdown('<div class="page-title">CO₂ tracking — all sites</div>',unsafe_allow_html=True)
    st.markdown('<div class="page-sub">GHG emissions · Scope 1, 2 & 3 · Net Zero target 2050</div>',unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Total CO₂e","1'120 <span class='kpi-unit'>t</span>","↓ 4% vs last month")
    with c2: kpi("Per Employee","19 <span class='kpi-unit'>t/emp</span>","59 employees total","kpi-delta-neutral")
    with c3: kpi("vs 2030 Target","−18%","target: −50% by 2030","kpi-delta-warn")
    with c4: kpi("Annual Reduction","6%","achieved in 2025 ✓")

    st.markdown("<br>",unsafe_allow_html=True)

    scopes=[
        ("Scope 1",RED, "#fdecea","Direct emissions — gas combustion, company vehicles","314 tCO₂e","↓ 5% vs baseline",28,GD),
        ("Scope 2",WARN,"#fef3e2","Indirect emissions — purchased electricity & steam",  "538 tCO₂e","↓ 3% vs baseline",48,GD),
        ("Scope 3",BLUE,"#e8f0fb","Value chain — suppliers, logistics, waste",           "268 tCO₂e","↑ 2% vs baseline",24,RED),
    ]
    st.markdown('<div class="section-card"><div class="section-card-title">🗂 Emissions by scope</div>',unsafe_allow_html=True)
    for label,color,bg,desc,val,delta,pct,d_color in scopes:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid #f0f0f0;">
            <div style="min-width:70px;">
                <span style="background:{bg};color:{color};padding:4px 12px;border-radius:20px;font-size:0.70rem;font-weight:700;">{label}</span>
            </div>
            <div style="flex:1;">
                <div style="font-size:0.83rem;color:#111;font-weight:500;margin-bottom:6px;">{desc}</div>
                <div style="background:#e0e0e0;border-radius:4px;height:6px;">
                    <div style="width:{pct}%;background:{color};height:6px;border-radius:4px;"></div>
                </div>
            </div>
            <div style="text-align:right;min-width:120px;">
                <div style="font-weight:700;color:#111;font-size:0.88rem;">{val}</div>
                <div style="font-size:0.73rem;color:{d_color};font-weight:600;">{delta}</div>
            </div>
        </div>""",unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    rows_html=""
    for _,row in df.iterrows():
        pct=row["pct"]; arrow="↑" if pct>0 else "↓"
        a_col=RED if pct>0 else GD
        status=row["status"]
        if status=="Anomaly":  s_html='<span class="dot-red"></span><span class="badge-danger">Off track</span>'
        elif status=="Review": s_html='<span class="dot-orange"></span><span class="badge-warning">Review</span>'
        else:                  s_html='<span class="dot-green"></span><span class="badge-success">On track</span>'
        intensity=round(row["co2e"]/row["mwh"],3)
        rows_html+=f"""<tr>
            <td><b>{row['site']}</b></td>
            <td>{row['co2e']:.1f}</td>
            <td>{intensity}</td>
            <td style="color:{a_col};font-weight:600;">{arrow} {abs(pct):.1f}%</td>
            <td>{s_html}</td>
            <td>{row['canton']}</td>
        </tr>"""

    st.markdown(f"""<div class="section-card">
        <div class="section-card-title">🏭 CO₂e by site</div>
        <table class="html-table">
            <thead><tr><th>Site</th><th>tCO₂e</th><th>t/MWh</th><th>vs target</th><th>Status</th><th>Canton</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""",unsafe_allow_html=True)

    st.markdown(f"""<div class="info-banner">
        🌍 <b>Nestlé Net Zero roadmap:</b> −50% emissions by 2030 · Net Zero by 2050.
        Current Swiss trajectory: on track at group level.
    </div>""",unsafe_allow_html=True)
